# SUPERSEDED — DO NOT EXECUTE

This Qwen3-8B / Mistral-Nemo-12B Kaggle GPU reader plan was superseded on 2026-10-08 before execution. Current plan: [LABEL_V6_SOL_CHUNKED_EXECUTION.md](LABEL_V6_SOL_CHUNKED_EXECUTION.md).

---

# LABEL-V6 Full4349 A/B Execution Plan

Date: 2026-10-08

## Goal

Generate competition-aligned report-derived supervision for all **4,349 report-only studies × 12 targets = 52,188 target decisions** before final R3D training.

The separately delivered Pilot28 notebooks are superseded for user execution. Pilot validation is now integrated inside each Full4349 notebook.

## Reader A

- Experiment: `LABEL-V6A-FULL4349`
- Account tag: A
- Model: `unsloth/Qwen3-8B-bnb-4bit`
- Pinned revision: `1deaf68f694c40dbce295da300851729d759b21a`
- Notebook: `A_LABEL-V6A_Qwen3_8B_Full4349.ipynb`
- Notebook SHA256: `48efe94b8ce6a6bb6e91dc745ccfc9c0e2a9b781e889ffed349e952af6018436`
- Save Version: `A LABEL-V6A Qwen3 Full4349`
- Runtime: T4×2 / Internet ON / Save & Run All

## Reader B

- Experiment: `LABEL-V6B-FULL4349`
- Account tag: B
- Model: `unsloth/Mistral-Nemo-Instruct-2407-bnb-4bit`
- Pinned revision: `a8e82a934394c6858f5ee545fa55e1e8cc67065f`
- Notebook: `B_LABEL-V6B_MistralNemo12B_Full4349.ipynb`
- Notebook SHA256: `de281caf16dc4845db754e4a9592df4389f859b29c42626939c37d32605589e3`
- Save Version: `B LABEL-V6B MistralNemo Full4349`
- Runtime: T4×2 / Internet ON / Save & Run All

## Integrated gate inside each notebook

The user does not run a separate Pilot notebook. Each Full notebook performs, in order:

1. Exact `train.csv` SHA and 4,407 / Gold58 / report-only4349 scope audit.
2. No Gold/V4/pilot decisions exposed to the reader.
3. Synthetic policy unit tests, including English and Cyrillic cases, with fixed expected competition-policy states.
4. Existing 28 report-only studies used only as blind parser/evidence preflight (14 per GPU lane); no reference decisions are shown.
5. If those machine checks pass, the same worker continues automatically to the remaining report-only studies.
6. GPU0/GPU1 process disjoint deterministic lanes; Qwen preferred batch 4, Mistral preferred batch 2, with same-chunk recovery and permanent batch-1 fallback after CUDA OOM.
7. Per-record output is flushed to JSONL and progress JSON so partial artifacts survive worker failure for recovery analysis.
8. Final CPU audit requires exactly 4,349 unique UIDs / 52,188 decisions, re-checks each evidence quote and Unicode offset against the exact source report, and audits exact-duplicate report consistency.

## Reader outputs

Each reader independently produces:

- rich `reader_A.jsonl` or `reader_B.jsonl`
- `decisions_long.csv`
- `labels_wide_reader.csv`
- `target_distribution.csv`
- `study_supervision.csv`
- `script_target_state_distribution.csv`
- `exact_duplicate_consistency.csv`
- retry/invalid queue
- worker return codes, summaries and logs
- source/model contracts and SHA information
- result ZIP

A single reader output is **not** a canonical training label set.

## Next gate after both Full runs

After both result ZIPs are available:

1. Match by UID + target + source report SHA.
2. Automatic candidate only when A/B agree on supervised state/label and no blocking inference/flags are present.
3. Keep non-supervised agreement masked.
4. Send disagreement, inference-used, flagged, invalid and duplicate-inconsistent items to adjudication.
5. Audit target-wise five-state distribution, supervised coverage, positive prevalence, A/B agreement rate, adjudication rate, script subgroup behavior and duplicate consistency.
6. Freeze canonical release with SHA.
7. Only then calculate target-wise class weighting from canonical `N_pos/N_neg`, finalize masked per-target loss, and start R3D-13.

Gold58 and V4 remain descriptive references and are not used to tune the report-label policy or reader routing.
