# RMIL — High-Score Architecture Candidates & Next Experiments

Updated: **2026-10-10**. **Status: C1/C2/C3 NOT YET SELECTED; RMIL-01 COMPLETED; RMIL-02 NEXT (PLANNED).** This is the new forward-looking imaging-model plan. Existing numbering `EXP-01` is occupied; use **RMIL-01..06**. This does not rename or invalidate previous R2D, RDINO, R3D, SS, Exp57 histories.

## 2026-10-10 — RMIL-01 actual result (supersedes original execution instructions below)

**COMPLETED/AUDITED.** [RMIL-01 artifact audit and 12-target comparison](RMIL-01_COMPLETED_AUDIT_2026-10-10.md): MEAN Gold58 macro AUROC **0.5763704369**, macro AUPRC **0.4507296488**, best epoch4/7 total; shared 4-window ATTN AUROC **0.5442963023**, AUPRC **0.4158921311**, best epoch3/6 total. ATTN − MEAN **−0.0320741346 AUROC**, **−0.0348375177 AUPRC**, 4/12 targets up, 8/12 down. Received review ZIP CRC and all **38 declared internal SHA-256 entries verified**; ZIP SHA `0642f2363003031a9e88c5f5c3e759bb16e95a45eb278d740f0ed204cf26449f`. No binary checkpoints or raw Gold labels inside review ZIP. This is reused development Gold58, not Public LB.

**Decision:** preserve 4-window uniform MEAN as comparator; reject promotion of this *shared scalar* ATTN under current conditions, without claiming target-specific attention cannot work. **RMIL-02 is NEXT, not yet executed**; CPU-first high-coverage actual Slice cache experiment, keep number of candidate windows and selection policy as separate axes. **Important source constraint:** the canonical R2D_SHARED224_V1 cache stores only four selected 3-Slice windows per Series; it cannot produce new, native 16/24/32 windows. Use original raw DICOM or a separately verified full-native-Slice cache, with patient/Series IDs and physical ordering reconciled to frozen manifests. Audit 4-window reconstruction parity (crop, scaling and index/UID) before interpreting any wider-window gain. Do not invent an already-mounted full-Slice Kaggle Input. RMIL-03 still unexecuted. C1/C2/C3, 3-/5-Fold, Exp57 blend remain undecided/deferred. Exp57 best Public LB remains 0.918.

## 2026-10-10 — NEW APPROVED RMIL-02/03 experimental contract

**See the canonical [RMIL-02/03 native-Window controlled protocol](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md).** RMIL-01 remains CLOSED; original per-Series K4 shared-ATTN was inferior but *insufficient candidate coverage as the cause* is **unverified**. New RMIL-02 splits (A) K4/K16/K24/K32 **MEAN** effect from (B) **MEAN vs SHARED ATTN** at identical K/pixels/sampling/split; first perform CPU-only audit of existing full-Slice vs DICOM assets, native physical geometry and K4 pixel/preprocessing parity. **RMIL-02A (CPU metadata/geometry preflight) prepared, NOT executed. RMIL-02B image cache requires verified original preprocessing pipeline and parity gate and is not yet built.** R3D D24×96 caches and Exp16B Full-MRI features cannot reconstruct original native 224px images. No automatic K24/K32 training: choose based on CPU effective-K and cost. Source competition `train_series/` has real DICOMs, but Kaggle current mount still must be verified.

RMIL-03 sequentially evaluates selected K: shared-window attention → **per-target Window Attention** → **per-target Window + Series Attention** (plus matched Mean comparator). Keep Exp57 full-MRI hierarchical MIL, target Top24 selection, and SS05 historical ranks as architectural *ideas*, **not learned target selection labels** or proof of isolated improvements. Freeze same backbone/pixels/training budget between variants. Decisions C1/C2/C3, folds and Exp57 blend remain open/deferred.

## Absolute anchors and honesty

- Current project best **Public LB 0.918**, Exp57: fold-specific task-tuned DINOv2-Base 2.5D, full-series hierarchical MIL / direct prediction and attention-selected Top-24 raw windows with further fine-tuning; 3-Fold per branch, 70% Top24 / 30% Direct.
- SS08 pure 12-specialist Public LB **0.876**, despite pseudo-label Fixed Val target-best mean 0.9341. This is *not* evidence that 12 experts selected via pseudo validation generalize.
- R3D-13V4 full 4349 / R3D-14V4 single-model standalone Public LB **0.689** (user reported); Gold58 macro AUROC 0.68023. Different samples, no claim these are equivalent.
- Recent **11 controlled Train300/Gold58 pilots**: max 0.57637 Gold58 AUROC, see [completed audit](R2D_RDINO_R3D15_COMPLETED_AUDIT_2026-10-10.md). They use all Series but *only 4 windows per Series*, and their training set of 300 differs markedly from Exp57's full data. Never compare pilot Gold58 score numerically to Public LB 0.918 as the same evaluation population.
- Gold58 is a repeatedly consulted, small *development* validation set, not untouched independent test. V4 routing already used most official Gold for decisions. Target-wise winners are hypothesis-generating and highly selection-biased.
- LABEL-V6 report-only decisions are separately being processed. **Not canonical/released until complete audit and independent adjudication**. Do not call a candidate label an official ground truth, and do not treat `not_mentioned`, `insufficient`, `uncertain` as negative.
- Key hypothesis: losses from limited window coverage and uniform pooling may dominate raw Backbone size. This requires ablation; do not assume causation.

## Architecture choices — all tentative

| Candidate | Architecture | Checkpoint budget (initial) | Acceptance |
|---|---|---|---|
| **C1 (first priority)** | **Single 2.5D high-resolution CNN** over actual adjacent Slice windows → per-target Window and Series Attention/MIL → 12 outputs. Start MedicalNet-deflated R34 baseline; consider stronger native 2.5D medical CNN *only after fair comparison*. | 1 | Full-data validated improvement vs prior baselines |
| **C2 (conditional)** | **2D expert + 2.5D expert**; fuse target-specific probabilities (late fusion) first; feature-level gating only if reliable improvement. May share Backbone to reduce checkpoint count, but verify representation effectiveness. | 1–2 | Repeatable OOF complementarity in weak targets; inference cost justified |
| **C3 (only if warranted)** | **2D + 2.5D + 3D expert**; 3D specialized for verified complementary targets, not automatically all 12. | 2–3 | 3D independently improves sufficiently powered OOF and end-to-end runtime budget |

**Unselected:** do NOT precommit 3-/5-Fold per expert or blend Exp57 into the final system. That could lead to >10 checkpoints and high inference latency. Revisit only *after* a strong expert has been independently validated. Minimal viable final could be C1 only.

**Depth claims:** four evaluated Backbone families — R34, R50, DINO-S, DINO-B — yielded 2.5D macro AUROC > 2D in 3/4, but R50 favored 2D, with many small deltas. Post-hoc 11-model target wins: 2.5D 8, 2D 2, 3D 2, but two 3D wins (ACL 0.627, Contusion 0.501) are not reliable evidence of 3D superiority. Target-specific spatial dependence remains a hypothesis requiring stable OOF.

## Controlled experiment roadmap

| ID | Question | Precise design / contract | Promotion gate |
|---|---|---|---|
| **RMIL-01** | Does attention improve on uniform pooling? | Keep **R2D-SHARED-A MedicalNet-deflated R34 2.5D** EXACT Train300 V4 / Gold58 / 358-study cache / all Series x 4 windows / 224px 130mm / full fine-tune / optimizer / 10 epochs. GPU0 **MEAN** vs GPU1 **ATTN** shared scalar window softmax; initialize attention weights to zero (exact initial mean). *No target-specific logic yet.* | Confirm QA, paired per-target AUROC and AUPRC, attention actually learns, no overinterpretation of small Gold58 deltas |
| **RMIL-02** | Separately test Window K coverage and shared Window Attention | CPU-only asset/physical-geometry/K4 preprocessing parity gate → single-channel native-Slice cache if needed; K4/16/24/32 MEAN (K24/32 conditional on CPU survey); at **same K** compare MEAN vs shared ATTN on T4×2. Freeze training and selection policy. | Cache SHA/parity + effective K/cost; paired Gold58 12-target metrics, with limited-dev-set caveat |
| **RMIL-03** | Does target-aware Window and Series aggregation help? | At RMIL-02 selected K, compare fixed shared Window ATTN → 12-target Window ATTN → 12-target Window+Series ATTN, each with identical data/encoder budget and 12 logits; retain Mean control. Do not simultaneously change K, sampling or labels. | Evidence beyond reused Gold58 selection noise; inference efficiency |
| **RMIL-04** | Does winning architecture generalize with all report-only cases? | Train full **4,349** with frozen V4 and, if verified canonical, separately frozen V6 masked losses; Gold58 development checks and standalone Public LB; require preprocessing/inference parity. | Strong standalone expert with credible evidence |
| **RMIL-05** | Does 2D add complementarity to 2.5D? | Add **2D only** to strong 2.5D, analyze target OOF and prediction/error correlations, conservative late fusion before learned gating. | OOF gain reproducible and inference benefit sufficient |
| **RMIL-06** | Is 3D worth its cost? | Only run if unresolved targets and clean evidence; standalone 3D target-specific complementarity + inference budget. | Repeated net gain; else discard 3D |
 
**RMIL-01 IS COMPLETED** following actual Kaggle Save & Run All and received artifact ZIP audit on 2026-10-10. The original notebook is an executed artifact; only RMIL-02+ remain proposed.

## RMIL-01 executed Kaggle contract (historical reproduction information)

- Notebook: `RMIL-01_R34_25D_Mean_vs_WindowAttention_T4x2.ipynb` (delivered as user artifact, not necessarily Git committed).
- **A account**, accelerator **T4 x2**, Internet **OFF**, **Save & Run All**. GPU0 MEAN, GPU1 ATTN (both identical 2.5D).
- Estimated ~20–60 minutes after preflight (uncertain). Save Version: `RMIL-01 R34 25D Mean vs WindowAttn` (<60 characters).
- Input dataset **`rsna-knee-wide224-persistent-cache-v1`** → `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1` with `cache_contract.json`, `cache_index_sha256.csv`, `allseries4/`, `frozen_manifests/`.
- Pretrained dataset **`rsna-knee-r3d-medicalnet-pretrained-v1`**, owner **`yhlucas`** → exact file `/kaggle/input/datasets/yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1/resnet_34.pth`.
- SHA audit/prefight, strict pretrained weight contract; no global `/kaggle/input` recursive scan.
- Readouts: each arm `best.pt`, `training_history.csv`, `gold58_metrics_best.csv`, `gold58_predictions_best.csv`, `artifact_sha256.json`, `training_summary.json`, per-arm ZIP; paired `RMIL-01_comparison.csv`, `RMIL-01_target_delta.csv`, `RMIL-01_results_for_review.zip`.
- Validate in Kaggle: 2 GPUs actually used; independent smoke Forward/Backward; all 58 UID / 12 targets; no shared train-val UID; best checkpoint selection; artifact checks. User should send both worker logs or combined review ZIP and summary after run.

## Full-project constraints

- 12 target-wise ROC-AUC macro competition objective; **AUPRC** and class counts always secondary diagnostics.
- Official severity criteria and uncertainty policies apply; Gold58/target-best cherry-picking is unsafe; use non-leaky grouping and larger silver OOF if trustworthy.
- Exp57 and prior Specialists are benchmark/evidence, not mandatory final ensemble members.
- Resource priority: correct physical MRI geometry → sufficient native Slice coverage → target-specific MIL → label reliability → strong single-model standalone → only then complementary experts/folds.
- Public LB 0.918 is the **only evidenced best project Public LB** in the cited repo docs; scores 0.94/0.96 in public discussions are third-party reports, not our model results.

## New-chat handoff

1. Read **this document** for future architecture / RMIL next action.
2. Read [completed pilot evidence](R2D_RDINO_R3D15_COMPLETED_AUDIT_2026-10-10.md), [Experiment History](EXPERIMENT_HISTORY.md), [Agent Rules](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md), and the historical [Current Handoff](CURRENT_HANDOFF.md).
3. RMIL-01 has already completed. Read [RMIL-01 completed audit](RMIL-01_COMPLETED_AUDIT_2026-10-10.md); do NOT rerun it by default.
4. Proceed to RMIL-02 CPU-only candidate-cache design/preflight; do not assume dataset exists or training has run. Do not start 3/5-Fold or Exp57 ensemble by default.
