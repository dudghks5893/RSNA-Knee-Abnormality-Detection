# R3D-15 — Local Feature / Target Attention 300-Study Screening Handoff

Date: 2026-10-09 (KST)
Status: **EXPERIMENT PLAN — NOT EXECUTED**
User decision: start new chat and deliver reproducible Kaggle notebooks for quick single-model train300 / Gold58-validation, then consider full4349 and Kaggle submission only if screening is promising.

## 0. New chat starting point / source priority
1. **THIS DOCUMENT** — current user-approved R3D-15 controlled screen scope and actual mounted input paths.
2. [R3D_13V4_NOTEBOOK_DELIVERY.md](R3D_13V4_NOTEBOOK_DELIVERY.md) — Kaggle CPU preflight actual PASS; exact mounted path and file hashes.
3. [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md) — R3D-05A, R3D-06D, R3D-13V4 Gold58, R3D-14V4 LB.
4. [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md) — **MANDATORY** Save & Run All, explicit inputs, bounded paths, two-GPU semantics, naming.
5. [R3D_14V4_STANDALONE_SUBMISSION_DELIVERY.md](R3D_14V4_STANDALONE_SUBMISSION_DELIVERY.md) — prior actual E7 checkpoint and inference topology/preprocessing.
6. [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md) — older project background; ignore stale pending claims for already-completed R3D-13/14.

Historical `3D_RESNET_EXPERIMENT_PLAN.md` reserves "R3D-15" for an unexecuted Exp57+R3D blend. The **new user-approved R3D-15A/B/C** is the active designation; do not confuse it with that old unexecuted blend plan.

## 1. Confirmed state and decision
- Previous full-data baseline `R3D-13V4-DDP`: ONE MedicalNet 3D ResNet34 + GLOB Series vectors + Series metadata + shared CLS Transformer512/2 layers/8 heads/FFN2048, 12 sigmoid logits. Full fine-tune, FP32, BN running statistics frozen, MASK_OFF. ALL usable Series; crop130mm; trilinear interpolated D24×96×96; cache float16 -> model FP32.
- Previously trained on **4,349 report-only studies** / V4 routed broad soft target + confidence; **58 Gold studies validation only**. Ten complete full epochs, two-GPU synchronized DDP, best E7 Gold58 Macro AUROC `0.6802269985`, AUPRC `0.5521237806`. User-reported R3D-14V4 Public LB **0.689**. Best project LB remains DINOv2 Exp57 **0.918**.
- Hypotheses: (A) GAP over final ResNet features discards fine-grained location and local lesion details; (B) a shared CLS vector is insufficient for 12 disease-specific localization tasks. Neither is proven. **3D backbone is fully pretrained/fine-tuned already; intermediate features were computed but not separately fed to classifier.**
- Past negative tests: R3D-05A final-layer spatial tokens SPT27/SPT48 hurt primary AUROC; R3D-06D simple target-query substitution hurt primary AUROC. **Do not repeat those architectures.**
- User-approved screen: **300 report-only pseudo-labeled train studies, all Gold58 validation**, ONE model/checkpoint per variant, no 3-/5-fold, no ensemble; **existing full R3D-12CACHE**, no DICOM reconstruction. This 300 vs 58 split is ~83.8/16.2, not exactly 80/20; the 58 Gold are a fixed official validation cohort, not random held-out pseudo-labels.

## 2. KAGGLE ADD INPUTS — VERIFIED ACTUAL PATHS

Four required sources from previously PASSed Kaggle R3D-12V4DATA preflight / R3D-13 actual training:

| Source | Add Input lookup / path | Status |
|---|---|---|
| Full R3D-12CACHE | Dataset `rsna-knee-wide224-persistent-cache-v1`; **`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d12cache_full`** | **actual Kaggle mounted root verified**; complete 4407 Studies, 24371 Series, 160 shards |
| V4 Broad labels | Dataset `rsna-knee-v4-consensus-dataset` (sidebar has also displayed `rsna_knee_v4_consensus_dataset`); **`/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_broad.csv`** | **actual verified path** |
| MedicalNet pretrained R34 | Dataset `rsna-knee-r3d-medicalnet-pretrained-v1` (sidebar may display `rsna-knee-r3d-medicalnet-pretrain`); **`/kaggle/input/datasets/yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1/resnet_34.pth`** | **actual verified path** |
| Competition | Kaggle competition **RSNA Knee Abnormality Detection**, original `train.csv` with official Gold58 labels | train.csv SHA verified; **exact resolved mount path to be printed/asserted by notebook**, candidate `/kaggle/input/competitions/rsna-knee-abnormality-detection/train.csv` OR competition-root alternative `/kaggle/input/rsna-knee-abnormality-detection/train.csv`; do not assert either without exists check |

Optional **diagnostics only**, not initial training weights:
- R3D-13V4 E7 private model Dataset `rsna-knee-r3d13v4-ddp-best-e7`, **actual previously verified path** `/kaggle/input/datasets/yhlucas/rsna-knee-r3d13v4-ddp-best-e7/R3D-13V4-DDP/best.pt`; checkpoint training-config SHA `78a258125c3fd20fddee55253cd1d3c8be065e48bb4f5071a5020dd6f8b896f5`.
- Saved original results path `/kaggle/working/R3D-13V4-DDP/`: `training_history.csv`, `gold58_metrics_best.csv`, `gold58_predictions_best.csv`, `best.pt`, `last.pt`. New Kaggle sessions do NOT inherit old `/kaggle/working`; attach published output or user-provided results separately if diagnostics need them.

**Full cache expected relative contents**: `r3d12cache_full/crop130_d24_96/series_index.csv` and its indexed volume shards, plus shard manifest and study roles. Confirm the real on-disk structure with **one bounded root listing**, not guesses. Entire R3D-12CACHE must be mounted: audit ZIP alone has metadata and NOT 160 volume shards.

Previously verified fingerprints:
- Official train.csv SHA256 `8ca2203c0e9d61c080c7a314c7cdb51c1b03a1d9eb4770819f7f34af53ef4e33`
- V4 Broad CSV SHA256 `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`
- MedicalNet R34 SHA256 `977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`
- Full cache index SHA256 `e72c9238c97e0957bb7fccee91489d23847519dd1aaf01e40620411875abe217`
- Full cache shard manifest SHA256 `bf4a008de5fbf9a239066524b38d0b0632891b83ff2781bde07538ff75bd44a0`.

Path resolution policy: exact root + `Path.exists()` first; fallback ONLY within named dataset roots; **NEVER** `Path('/kaggle/input').rglob(...)` or other whole-input recursive scan. Fail immediately on a missing source, mismatch, shard/UID mismatch; never create 3D cache during training.

## 3. Train300 selection — MUST RUN A CPU PREFLIGHT AND FREEZE MANIFEST
- Candidate pool: exact **4,349 report-only UIDs** (no Gold58) in official train.csv matched 1:1 to V4 Broad and full cache.
- Select **300 unique studies deterministically** by predeclared seed/algorithm, iterative multi-label stratification / greedy multicoverage optimizing **all 12 targets**. DO NOT use official Gold58 labels, Gold predictions, Public LB, or target-specific Gold scores in sampling.
- Each V4 Soft score is available for all 12 targets, but non-null does **not** mean a valid true positive/negative. Define and print *proxy class* using a clear fixed rule (e.g. soft>0.5 vs soft<0.5, report ties separately), per-target confidence quantiles, strong-evidence counts, score ranges and selected-vs-full distribution. No fabricated ground-truth positive labels.
- Aim for >=10 high-confidence pseudo-positive and >=10 high-confidence pseudo-negative studies **per target if feasible**. Rare targets may make that impossible: report infeasibility honestly; do not forge labels, secretly adjust class thresholds, or overpromise all targets are accurately learned.
- Mandatory gate: 300 unique selected study UIDs, exactly 58 distinct Gold Val UIDs, zero intersection, exactly 12 finite V4 soft-score/confidence columns per train, valid [0,1], each target both proxy sides where feasible; target count table, cache Study/Series coverage and all shard references readable.
- Save `train300_manifest.csv`, `gold58_manifest.csv`, `train300_target_distribution.csv`, `train300_selection_audit.json` including seed, selection policy and SHA hashes. Freeze manifest across **all** B0/A/B/C. Do not reselect on results.

## 4. Single-model controlled architecture screening
**B0 reference (MUST retrain)**: canonical R3D-13V4 GLOB + metadata + shared CLS + 12 heads, but train on EXACT same frozen 300, same V4 loss. This is the fair comparison; 4349-trained Gold `0.68023` is NOT a valid matched baseline for train300.

**R3D-15A — Local-only add-on**:
- Keep entire original GLOB/shared CLS path and its direct logit contribution.
- Extract intermediate MedicalNet R34 feature maps (for example stage/layer2 or layer3 **after inspecting actual checkpoint/module topology**, not hardcoding shapes). Light multi-scale local projection/pooling -> a bounded number of local tokens per Series; preserve spatial position embeddings/masks. Add residual / gated correction to GLOB, without replacing GLOB.
- IMPORTANT: prior R3D-05A SPT27/SPT48 used only FINAL feature maps; new test must genuinely tap intermediate maps, not repeat that screen.
- Avoid over-large tokens and unbounded Series×Token Transformer memory; microbatch Series with consistent gradient averaging.

**R3D-15B — Disease-specific selection-only**:
- Retain current GLOB features and shared-CLS prediction path.
- Add 12 separate disease query/gated attention branches over Series features/metadata (not solely hard-replace shared CLS, unlike the failed R3D-06D TargetQuery).
- Disease-specific residual logit correction, gate initialized conservatively (e.g. zero correction at initialization) to protect base pathway. Do not claim this makes model identical to pretrained *full R3D* because models are initialized from **MedicalNet** weights, not the trained E7 R3D checkpoint.

**R3D-15C — Combined**:
- Intermediate local tokens + disease-specific query attention + gated residual to canonical GLOB.
- Run only if A and/or B shows credible improvement; keep diagnostic stage separate. No other input/label/model family modifications.

Common: R34 MedicalNet initial weights identical; no reuse of Gold-selected E7 checkpoint as initial supervised model; ALL Series; exact index ordering from original training and same preprocessing, same seed and frozen train300/Gold58, optimizer/LR/WD/FP32/BN freeze, data loader, augmentation, 10 full passes or equal *optimizer update budget*, same checkpoint selection (Gold58 macro AUROC, AUPRC tie-break), identical early-stopping rule, per-target prediction metric extraction. Architecture-specific new-module init unavoidable; preserve seed and log it.

Required audit: baseline B0 and A/B/C target per-target AUROC/AUPRC, delta, confidence intervals or study-level bootstrap uncertainty caveat due n=58, class support, logits/probability ranges, train/val losses, training seconds, GPU peak VRAM, pretrained matched fraction, BN freeze, SHA/fingerprint and prediction CSV. Sensitivity @ 0.5 is optional diagnostic, **not** AUROC.

## 5. Decision and submission gate
- First run CPU preflight (0 GPU training), then independent baseline and A/B with T4×2 optional parallel independent processes, then C only if warranted.
- Two GPUs must be explicitly bound (`CUDA_VISIBLE_DEVICES=0`, `=1`) to call them truly utilized. If a notebook uses only GPU0, say so. GPU0/GPU1 A/B jobs create **two separately trained single models**, never a fold or ensemble.
- Full Gold58 is repeatedly reused **model-selection** validation and V4 labels previously used Gold57 routing; it is not an untouched independent test. Metric proximity to past Kaggle LB doesn't guarantee current LB.
- Assess gain vs **B0 train300 reference**, not vs 4349 baseline. Reject small/noisy gains despite apparent decimal improvements. If promising, train winner using all **4,349** report-only with same fixed architecture, Gold58 validation, **then** consider ONE standalone Kaggle LB submission. Don't submit the weak 300-studies quick screening checkpoint without user explicitly deciding to do so.
- If local tokens cannot recover information lost during D24×96×96 input resampling, **Crop130 D24×128×128 must be rebuilt from raw DICOM**, not upsample existing cache. Prior R3D-07B 128 resolution comparison was Full-FOV, not exact Crop130.
- LABEL-V6 ongoing; not mixed into this V4 architecture test. DINOv2 Exp57 K32 separate research lane, don't blend into R3D-15.

## 6. Notebook production / user delivery
- Follow `docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md` literally.
- Suggest separate `R3D-15P_Train300_Preflight.ipynb` (CPU, Internet OFF) and `R3D-15AB_Train300_R34_Local_TargetAttention.ipynb` (GPU T4×2, Internet OFF), plus C separately if needed. Persist frozen manifests from preflight as an explicit mounted Dataset or embed deterministic selection rule + exact frozen hash into GPU notebook (never depend on ephemeral /kaggle/working of another session).
- Include: experiment number/title, change vs fixed, owner/slug/name/file and **exact verified Kaggle input root**, accelerator, internet OFF, expected execution time **only based on a real probe**, recommended Save Version name <=60 chars, outputs, exact success gate. No generated-notebook claim before creation.
- Notebook must be self-contained, **clean Save & Run All**, checkpoints and logs in `/kaggle/working/R3D-15*`, no training-on-GPU DICOM caching, no automatic fabricated fallbacks/zero predictions; preflight failure stops training.
- Before handing off: notebook JSON/nbformat parse, all code cells AST parse, worker source parity, bounded path smoke, synthetic forward+backward and gradient path confirmation, 12 finite logits, missing dataset failfast, actual manifest reuse in B0/A/B.
- Do not publish raw MRI or private individual report labels on public GitHub.

## 7. New chat first task
Read this file and the six supporting documents, use **ACTUAL Kaggle roots in §2**, then implement **CPU-only deterministic Train300 selection + audit Notebook** as the first deliverable; do not guess hidden training code. Recover or request exact source code/notebook for successful `R3D-13V4_DDP2_B4_E10_EarlyStop.ipynb` if not accessible and avoid silently reinventing preprocessing/loss. Then deliver paired B0/A/B GPU notebook following the agent rules. Remind user which four Inputs to attach and how to share preflight results.
