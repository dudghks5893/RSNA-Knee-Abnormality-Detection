#!/usr/bin/env python3
"""
Build fixed target-specific pseudo validation manifests for RSNA Knee Specialist experiments.

Contract fixed on 2026-09-30:
- Official Gold 58 studies remain in Train.
- Validation comes from V4 routed strict pseudo labels.
- Positive: target >= 0.5
- Negative: target < 0.5
- Per class, use confidence percentile [50%, 90%) as the default validation candidate band.
- Preserve the top 10% confidence samples for training whenever possible.
- Fixed random seed: 20260930.
- Target-specific validation sizes are predefined below.
"""

from pathlib import Path
import re
import numpy as np
import pandas as pd

SEED = 20260930

TARGETS = [
    "ACL",
    "MCL",
    "Medial Meniscus",
    "Lateral Meniscus",
    "Medial OA",
    "Lateral OA",
    "PF OA",
    "Effusion",
    "Synovitis",
    "Baker's",
    "Contusion",
    "Fracture",
]

VAL_PLAN = {
    "ACL": (40, 40),
    "MCL": (40, 40),
    "Medial Meniscus": (40, 40),
    "Lateral Meniscus": (40, 40),
    "Medial OA": (40, 40),
    "Lateral OA": (40, 40),
    "PF OA": (40, 40),
    "Effusion": (40, 40),
    "Synovitis": (25, 25),
    "Baker's": (40, 40),
    "Contusion": (40, 40),
    "Fracture": (30, 30),
}

DEFAULT_BAND_LOW = 0.50
DEFAULT_BAND_HIGH = 0.90

INPUT_ROOT = Path("/kaggle/input")
OUTPUT_DIR = Path("/kaggle/working/specialist_fixed_val_v1")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_one(pattern: str, required_substring: str | None = None) -> Path:
    files = list(INPUT_ROOT.rglob(pattern))
    if required_substring is not None:
        files = [p for p in files if required_substring.lower() in str(p).lower()]
    if not files:
        raise FileNotFoundError(f"Could not find {pattern!r} under {INPUT_ROOT}")
    return files[0]


def safe_name(target: str) -> str:
    s = target.lower().replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def choose_class_samples(
    class_df: pd.DataFrame,
    n_select: int,
    target: str,
    hard_label: int,
) -> pd.DataFrame:
    """
    Select validation samples while preserving the highest-confidence tail for Train.

    Default:
      confidence percentile >= 0.50 and < 0.90.

    Fallback:
      if the default band is too small, extend downward only:
      [0.40, 0.90), [0.30, 0.90), ... [0.00, 0.90).
      The top 10% remains protected from validation selection.
    """
    if len(class_df) < n_select:
        raise ValueError(
            f"{target} label={hard_label}: only {len(class_df)} strict samples, "
            f"but {n_select} validation samples were requested."
        )

    d = class_df.copy()
    d = d.sort_values(["confidence", "StudyInstanceUID"], ascending=[True, True]).reset_index(drop=True)

    # Rank within each target/class. Average ranks make ties deterministic.
    d["confidence_percentile"] = d["confidence"].rank(method="average", pct=True)

    lows = [0.50, 0.40, 0.30, 0.20, 0.10, 0.00]
    candidate = None
    used_low = None

    for low in lows:
        c = d[
            (d["confidence_percentile"] >= low)
            & (d["confidence_percentile"] < DEFAULT_BAND_HIGH)
        ].copy()
        if len(c) >= n_select:
            candidate = c
            used_low = low
            break

    if candidate is None:
        raise ValueError(
            f"{target} label={hard_label}: cannot select {n_select} samples "
            f"without entering the protected top-10% confidence region."
        )

    # Stable but random fixed selection.
    # Offset by target/class so each group gets an independent deterministic draw.
    target_offset = TARGETS.index(target) * 100 + hard_label
    selected = candidate.sample(
        n=n_select,
        random_state=SEED + target_offset,
        replace=False,
    ).copy()

    selected["candidate_band_low"] = used_low
    selected["candidate_band_high"] = DEFAULT_BAND_HIGH
    return selected


strict_path = find_one("rsna_knee_pseudolabels_v4_routed_strict.csv")
broad_path = find_one("rsna_knee_pseudolabels_v4_routed_broad.csv")
train_path = find_one(
    "train.csv",
    required_substring="rsna-knee-abnormality-detection",
)

print("Strict:", strict_path)
print("Broad :", broad_path)
print("Train :", train_path)
print("Output:", OUTPUT_DIR)

strict = pd.read_csv(strict_path)
broad = pd.read_csv(broad_path)
train = pd.read_csv(train_path)

required_cols = {"StudyInstanceUID"}
for target in TARGETS:
    required_cols.add(target)
    required_cols.add(f"{target}__conf")

missing = required_cols - set(strict.columns)
if missing:
    raise KeyError(f"Strict CSV missing columns: {sorted(missing)}")

if strict["StudyInstanceUID"].duplicated().any():
    raise ValueError("Strict CSV contains duplicate StudyInstanceUID values.")

# Official fully-labeled Gold studies. They should not exist in pseudo CSVs.
gold_mask = train[TARGETS].notna().all(axis=1)
gold_uids = set(train.loc[gold_mask, "StudyInstanceUID"].astype(str))
pseudo_uids = set(strict["StudyInstanceUID"].astype(str))
gold_overlap = gold_uids & pseudo_uids

if gold_overlap:
    raise ValueError(
        f"Gold/pseudo UID overlap detected: {len(gold_overlap)} studies. "
        "Validation creation stopped."
    )

all_selected = []
summary_rows = []

for target in TARGETS:
    val_pos, val_neg = VAL_PLAN[target]

    target_values = pd.to_numeric(strict[target], errors="coerce")
    conf_values = pd.to_numeric(strict[f"{target}__conf"], errors="coerce")

    base = pd.DataFrame({
        "StudyInstanceUID": strict["StudyInstanceUID"].astype(str),
        "target": target,
        "soft_label": target_values,
        "confidence": conf_values,
    })

    # Strict target/study pairs only.
    base = base[base["soft_label"].notna() & base["confidence"].notna()].copy()
    base["hard_label"] = (base["soft_label"] >= 0.5).astype(int)

    pos = base[base["hard_label"] == 1].copy()
    neg = base[base["hard_label"] == 0].copy()

    selected_pos = choose_class_samples(pos, val_pos, target, 1)
    selected_neg = choose_class_samples(neg, val_neg, target, 0)

    selected = pd.concat([selected_pos, selected_neg], ignore_index=True)
    selected["split"] = "val"
    selected["selection_seed"] = SEED

    if selected["StudyInstanceUID"].duplicated().any():
        raise AssertionError(f"{target}: duplicate UID inside validation split.")

    # Reproducible ordering.
    selected = selected.sort_values(
        ["hard_label", "StudyInstanceUID"],
        ascending=[False, True],
    ).reset_index(drop=True)

    out_cols = [
        "StudyInstanceUID",
        "target",
        "hard_label",
        "soft_label",
        "confidence",
        "confidence_percentile",
        "candidate_band_low",
        "candidate_band_high",
        "split",
        "selection_seed",
    ]
    selected = selected[out_cols]

    out_path = OUTPUT_DIR / f"{safe_name(target)}_fixed_val_v1.csv"
    selected.to_csv(out_path, index=False)

    all_selected.append(selected)

    strict_pos = len(pos)
    strict_neg = len(neg)
    remain_pos = strict_pos - val_pos
    remain_neg = strict_neg - val_neg

    summary_rows.append({
        "Target": target,
        "Strict_Total": len(base),
        "Strict_Pos": strict_pos,
        "Strict_Neg": strict_neg,
        "Val_Total": len(selected),
        "Val_Pos": int((selected["hard_label"] == 1).sum()),
        "Val_Neg": int((selected["hard_label"] == 0).sum()),
        "Train_Strict_Pos_Remaining": remain_pos,
        "Train_Strict_Neg_Remaining": remain_neg,
        "Val_Pos_Conf_Min": float(selected.loc[selected["hard_label"] == 1, "confidence"].min()),
        "Val_Pos_Conf_Mean": float(selected.loc[selected["hard_label"] == 1, "confidence"].mean()),
        "Val_Pos_Conf_Max": float(selected.loc[selected["hard_label"] == 1, "confidence"].max()),
        "Val_Neg_Conf_Min": float(selected.loc[selected["hard_label"] == 0, "confidence"].min()),
        "Val_Neg_Conf_Mean": float(selected.loc[selected["hard_label"] == 0, "confidence"].mean()),
        "Val_Neg_Conf_Max": float(selected.loc[selected["hard_label"] == 0, "confidence"].max()),
    })

combined = pd.concat(all_selected, ignore_index=True)
combined_path = OUTPUT_DIR / "specialist_fixed_val_manifest_v1.csv"
combined.to_csv(combined_path, index=False)

summary = pd.DataFrame(summary_rows)
summary_path = OUTPUT_DIR / "specialist_fixed_val_summary_v1.csv"
summary.to_csv(summary_path, index=False)

# Global checks.
expected_rows = sum(pos + neg for pos, neg in VAL_PLAN.values())
assert len(combined) == expected_rows, (len(combined), expected_rows)

for target, (vp, vn) in VAL_PLAN.items():
    t = combined[combined["target"] == target]
    assert len(t) == vp + vn
    assert int((t["hard_label"] == 1).sum()) == vp
    assert int((t["hard_label"] == 0).sum()) == vn
    assert not set(t["StudyInstanceUID"]) & gold_uids

print("\n=== Specialist Fixed Validation Summary ===")
print(summary.to_string(index=False))

print("\n=== Output Files ===")
for p in sorted(OUTPUT_DIR.glob("*.csv")):
    print(p.name, f"({p.stat().st_size:,} bytes)")

print("\nPASS")
print("Combined manifest:", combined_path)
print("Summary          :", summary_path)
