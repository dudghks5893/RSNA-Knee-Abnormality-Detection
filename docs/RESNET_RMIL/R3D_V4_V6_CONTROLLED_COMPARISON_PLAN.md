# R3D V4 → V6 Controlled Label Comparison Plan

Decision date: 2026-10-08
Status: PLAN ONLY — neither R3D-13V4 nor R3D-13V6 has been trained.

## Motivation and lineage

LABEL-V6 creation continues independently in GPT-6 chats. Do not block the R3D model-training lane on V6. First finish a single Main R3D with **existing V4 routed broad soft labels**; later retrain with released V6 canonical labels and compare.

Do not modify/resume historical search checkpoints. Best project Public LB is Exp57 0.918, not R3D.

## Frozen imaging architecture

- ALL usable Series per study.
- Physical 130 mm center crop, interpolated D24×96×96 from R3D-12CACHE.
- MedicalNet R34 full fine-tune, pure FP32, BN running stats frozen.
- One GLOB feature per series + series metadata embedding → Transformer 2 layers (512, 8 heads, FFN2048, dropout 0.10, Pre-LN, shared CLS) → 12 target logits.
- Backbone LR 1e-5; new layers LR 5e-5; WD 1e-4.
- MedicalNet R34 checkpoint SHA256: 977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658.
- Earlier input/backbone/series/dual-FOV experiments are closed without new evidence. Sag1 specialist remains hold.

## Data assets verified (local user ZIP audit, not Kaggle mount confirmation)

- Official train.csv 4,407 unique studies; Gold58 fully labeled, report-only 4,349 fully unlabeled; zero partial.
- V4 ZIP `rsna_knee_v4_consensus_dataset(3).zip` SHA256 `4ce490986e8d6f2f2f0ced70b1891122e05cc9fa9eb26f8523875dd66cd14047`.
- V4 `rsna_knee_pseudolabels_v4_routed_broad.csv`: 4,349 report-only UIDs, 12 soft labels & 12 confidence columns; all 52,188 soft target values non-null, range [.01,.99].
- V4 `rsna_knee_pseudolabels_v4_routed_strict.csv`: 4,349 UIDs, 39,792 non-null of 52,188 target slots.
- Both have 1:1 UID parity against report-only train.csv and no Gold UIDs.
- V4 broad recommended as principal first model; strict is reference/possible separately logged fine-tune, **not automatically included in controlled V4-vs-V6 primary comparison**.
- V4 is target-routed using previous Gold57. Gold58 is therefore not fully independent even when Gold images are held out from training.
- R3D-12CACHE full4407: 4,407 studies, 24,371 Series, 160 float16 shards, ~10.04GiB, local audit PASS.
- Full cache **upload to Kaggle Dataset and exact mounted path are NOT yet verified**. Audit ZIP cannot replace volume shards.

## Step 1 — R3D-12V4DATA / preflight (CPU, no model training)

1. Verify actual Kaggle-mounted complete R3D-12CACHE dataset path and `crop130_d24_96/series_index.csv` + every referenced shard. Fail fast on absent/incomplete mount; never regenerate cache on GPU.
2. Verify Official train.csv and V4 Kaggle Input (suggested historical Dataset display name `rsna-knee-v4-consensus-dataset`, filename `rsna_knee_pseudolabels_v4_routed_broad.csv`) on **exact** mount paths. Do not assume root or version.
3. Assert Gold58 x 12 fully official, pseudo study UIDs exactly report-only 4349 and no overlap; all volume series coverage; target ordering and confidence values [0,1]; source SHA.
4. Produce train/val UID manifests, target-wise pseudo soft-score histograms, confidence distributions, counts & report-only pseudo-positive proxy (score >0.5; not clinical prevalence).
5. Loss unit checks: soft-target BCE with logits, per-target confidence weighting, no Gold in train. Divide by supervised-count, not sum of weights if intending absolute attenuation; batch/inference GPU smoke test profiles speed and VRAM.
6. Estimate an executable full-data epoch budget from observed throughput. The historical 192-draw search epoch is **not** a full pass.

## Step 2 — R3D-13V4 / first full-data single model

- Training: exactly 4,349 report-only studies, V4 routed broad soft labels & confidence. Gold58 excluded from training.
- New initial MedicalNet R34, not search best.pt.
- Fix seed, UID ordering, model hyperparameters, optimizer/scheduler, augmentations, number of complete full-data passes, batch/accumulation, step budget and checkpoint rule. Record all in machine-readable config for V6 replay.
- 12-target masked soft BCE per target; confidence weights used with explicitly tested scaling; do not normalize a single uniform weight away. Pseudo score is not a binary truth.
- Gold58 validation at end of every complete epoch; checkpoint selection primary 12-target Macro ROC-AUC, Macro AUPRC tie-break. Gold is reused model-selection reference, not independent test.
- Save weights, last & best, epoch logs, target metrics, Gold predictions, train/val manifests, config, SHA, preprocessing contract, runtime, actual GPU utilization. Preserve recoverable checkpoints if session runtime limit is reached.
- Use Kaggle clean Save & Run All. If multi-session training is needed, document explicit resume inputs and exact continuation state without violating notebook rules.
- Do not assert both T4 GPUs are used unless explicit 2-GPU execution is implemented and logged.

## Step 3 — R3D-14V4 / standalone submission

- Use R3D-13V4 best single checkpoint only.
- Implement hidden-test all-series preprocessing with frozen imaging geometry; output correct 12-target submission shape/UID order/range/NaNs and checksum.
- Submit to public LB only as a standalone R3D score first. Reference Exp57=0.918.
- Record Gold-vs-LB gap and target metrics; avoid repeated Public LB micro-tuning.

## Step 4 — V6 arrival / controlled replay

- Wait until V6 candidate adjudication, complete 4,349×12 contract, canonical release SHA.
- Audit target-wise masks, positive and negative counts, class imbalance, missingness. V6 positive/negative hard targets and masked others; compute loss and class weights only after release.
- Train `R3D-13V6` from the SAME MedicalNet R34, same architecture/crop, identical seed and compute/epoch budget as V4 run. Freeze all non-label dimensions as much as possible. Label encoding/defined mask and associated loss differ by necessity.
- Evaluate on **same Gold58**, identical selection rule and standalone LB protocol: `R3D-14V6`.
- Compare V4 vs V6 target-wise ROC-AUC/AUPRC, macro metrics, confidence intervals if feasible, label supervision coverage, failure patterns, runtime and hidden-test Public LB. Note V4 Gold57 routing contamination favors V4 in reused Gold comparison; public LB is not an independent unlimited tuning signal either.
- Consider V4→V6 continued fine-tune only as a separately labelled experiment, not the controlled initial comparison.

## Step 5 — Ensemble and closeout

- Only after standalone scores and error correlation review, test complementary blend with Exp57 (3fold B3A/Direct, 70:30 internal).
- Avoid public-LB-driven blend weight micro-search; document any predeclared ratio.
- Optional 3/5fold expansion **only** if standalone single model merits compute. The same released label manifest is usable for single/3/5fold; preserve fold-aware routing requirements if using Gold-derived legacy V4 fold models.
- Maintain `EXPERIMENT_HISTORY.md` only for **actual run results**; keep pending plans separate.
