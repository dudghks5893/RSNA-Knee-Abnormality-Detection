# R3D-14V4 — E7 Standalone Kaggle Submission Notebook

Date: **2026-10-09**.
**STATUS: NOTEBOOK DELIVERED / LOCAL TESTS PASSED / ACTUAL KAGGLE INFERENCE AND PUBLIC LB PENDING.** Do not call it a finished submission until the user reports `FINAL_STATUS: PASS` and Kaggle scores the submission.

## Input and locked model

- Use actual R3D-13V4-DDP E7 `best.pt`, **not** E10 `last.pt`, not training `R3D-13V4-DDP_results.zip` (that ZIP omits .pt).
- Training Gold58 Macro AUROC at E7 **0.6802269985218738**, Macro AUPRC **0.5521237805823017**, 10 full epochs, 2-T4 DDP, 125.708 min. This is **not Public LB**.
- Exact training config SHA256: `78a258125c3fd20fddee55253cd1d3c8be065e48bb4f5071a5020dd6f8b896f5`.
- Submission Notebook filename `R3D-14V4_R34_E7_2GPU_Standalone_Submission.ipynb`, SHA256 `d1f935411853a41c78b3bb7e5036f24a7a80f322cc9af6839a3386c8165390e4`.
- Package `R3D-14V4_Standalone_Submission_Package.zip`, SHA256 `fa44dfc66640433423d81c6e8e4efefe7b11cb48c8198049c7619c178f48cf3d`.
- Worker `R3D-14V4_infer_worker.py`, SHA256 `92d01dea3a60b8ed400736341de9ee22cc1304501ad64b5efe7668898d5c3ac3`.
- Notebook is **self-contained**: writes worker source; no additional worker file Input.
- Competition Add Input + R3D-13V4 completed Notebook **Output Input** including E7 `best.pt` (or verified exact E7 best.pt as private Dataset). No training cache / V4 pseudo dataset / separate R34 pretrain needed for submission.
- Kaggle accelerator **GPU T4×2**, Internet OFF, `Save & Run All`; version name: `R3D-14V4 R34 E7 TwoGPU Standalone`.

## Exact preprocessing and architecture

- Model classes `BasicBlock3D`, `MedicalNetR34`, `MainR3D` copied **verbatim** from successfully executed R3D-13V4 DDP Notebook. Strict `load_state_dict`. E7 epoch/Gold58 metrics and all source config hashes checked. No calibration/blend/fold.
- Original `R3D-12CACHE` actual generator log functions copied **verbatim**: `read_series_image` with SimpleITK `GetGDCMSeriesFileNames`, `normalize_exact_06a` (0.5–99.5 percentile clip; z-score; clamp ±5), `center_crop_pad_mm` (130mm; pixel crop and zero-padding), `resize_volume` trilinear with `align_corners=False` to D24x96x96 and **float16 quantization**, then float32 GPU model input.
- Same Series order as R3D-12CACHE full4407: study/plane (Sagittal, Coronal, Axial), rank descending `4*Fluid*Fat+2*Fluid+Fat`, SeriesInstanceUID ASC, no truncation. All test Series required.
- Independent GPU rank0/1 split test studies by row index modulo 2. **No NCCL/DDP needed in inference, but both T4 GPU0/GPU1 execute different Studies**. This is one single model replicated twice, not an ensemble.
- Competition has example test.csv 3 studies, hidden scorer supplies about 1,300. `sample_submission.csv` used **only for target schema** because example UID rows may not match hidden test. Output order/coverage derived from scored `test.csv`. Merged `submission.csv` columns exact, UID count/order exact, predictions all finite in [0,1], zero missing/fallbacks.
- Kaggle Code Competition **submission.csv** at `/kaggle/working/submission.csv`, GPU Notebook <=9 hours; worker cutoff 8.5h.
- Expected full hidden inference time **NOT measured**. No claim Kaggle run succeeded until actual Saved-Version hidden data inference.

## Tests actually performed locally

- Notebook nbformat validation; every code cell and embedded worker AST parsing PASS.
- The three model classes and the original 5 preprocessing functions match prior source verbatim.
- CPU MainR3D forward/inference produced 12 finite logits; synthetic Series order matched historical sort policy.
- Synthetic volume normalization, physical crop/padding, trilinear resizing float16 shape contract PASS.
- Original training config AST re-evaluation reproduced exact config SHA `78a258...`; synthetic E7 checkpoint strict `weights_only=True` loading (266 MiB) PASS. **Synthetic checkpoint not the user's E7 weights**.
- Two-worker synthetic CSV merge checked sorted real UID ordering, 12 target columns, finite scores, and allowed sample_submission example UID mismatch. PASS.
- ZIP CRC and notebook/worker embedded source parity PASS.

## What to request after Kaggle run

Share saved notebook log or `R3D-14V4/submission_audit.json`, the actual Kaggle Public LB for standalone R3D-14V4 and any execution errors. Compare Public LB directly to Exp57 Public LB **0.918**. Gold58 remains repeated-use/non-independent validation; do not directly compare Gold58 .68023 to Public LB .918.
