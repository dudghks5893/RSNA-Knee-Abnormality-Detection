## 2026-10-08 — R3D-13V4-DDP2 replacement delivered (NOT YET RUN)

**This supersedes earlier single-GPU / Series Microbatch 2 / E5 R3D-13V4 Notebook for new execution.** The user preferred the project-proven batching scale and full use of Kaggle T4×2. Do NOT resume legacy single-GPU checkpoint as if it were an equivalent DDP continuation.

- Notebook: `R3D-13V4_DDP2_B4_E10_EarlyStop.ipynb` (self-contained, writes embedded worker script).
- Package: `R3D-13V4_DDP2_Notebook_and_Guide.zip`; SHA256 `9a191e6824be5a927d90ba64834f605bbb917746a79dcd001af0f34228770287`.
- Runtime: Kaggle **GPU T4×2**, Internet OFF, **Save & Run All**, **one synchronized Main model (not folds)**.
- Two torchrun NCCL DDP ranks, each: Study batch 1, Series Microbatch 4, Gradient Accumulation 2. Thus effective Study batch = 4 globally, 1,088 optimizer updates per 4,349-study epoch. Remainder 1 study is loss-corrected via zero-loss dummy process, not a duplicate supervised record.
- Maximum **10 full epochs**; minimum **5**; patience **3** measured using Gold58 Macro AUROC primary / Macro AUPRC tie break. Epoch-cosine scheduler uses max 10 from the start. Seed remains 20261013, FP32, R34 full finetune, BN stats frozen, GLOB/Transformer shared CLS, original V4 soft/conf weighted BCE and other LR/WD unchanged.
- Per-rank actual forward+backward smoke on maximum Series count before training; no claimed GPU memory/speed until Kaggle run.
- Progress log about every 100 unique Studies; last.pt recovery checkpoint ~1,000 studies and every full epoch; best.pt only after a completed Gold58 epoch; training metrics and ZIP (no .pt) preserved.
- Wall stop 9.5h and 30 min margin yields `NEEDS_RESUME`, never false PASS.
- Old single-GPU run should be stopped/archived before starting a new DDP run. Prior standalone model training status does not establish this replacement's completion.
- CPU local tests: two-process Gloo gradient math exact vs serial for group size 1,2,3,4,5; 4,349 UID group coverage in 1,088 steps; Notebook nbformat, code AST, embedded worker exact parity, archive CRC and SHA PASS. **Actual NCCL T4 ×2 Kaggle test is pending.**
- Four required Add Inputs identical to the already PASSED R3D-12V4DATA CPU contract.

Next: start **revised DDP Notebook**, send actual GPU smoke output, epoch logs and `R3D-13V4-DDP_results.zip`. Gold58 is reused/non-independent; standalone LB after training.

---

## 2026-10-08 — R3D-12V4DATA Kaggle CPU preflight ACTUAL PASS

User-provided `R3D-12V4DATA_audit.zip` and full Kaggle Run All console log checked. This is a **completed, executed** CPU preflight, not a projected PASS.

- PASS: 4,349 report-only V4 train UIDs; 58 Gold validation UIDs; no UID duplicates/overlap; all 12 targets.
- Cache: full `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d12cache_full`, 4,407 studies, 24,371 series, 160 shards; contract and index/manifest SHA exact.
- V4 broad CSV mounted: `/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_broad.csv`; SHA256 `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`.
- MedicalNet R34 weights mounted: `/kaggle/input/datasets/yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1/resnet_34.pth`; SHA256 `977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`.
- Official train.csv SHA256 `8ca2203c0e9d61c080c7a314c7cdb51c1b03a1d9eb4770819f7f34af53ef4e33`.
- Independent archive inspection: ZIP CRC PASS, audit JSON status PASS, train/validation disjointness PASS, target distribution 12 rows.
- V4 pseudo mean confidence: Synovitis 0.17318, Effusion 0.43578, Fracture 0.44261, Lateral OA 0.50461. Interpret as supplied heuristic confidence, not measured accuracy.
- Next: **run R3D-13V4_Full4349_R34_Main_KnownMount.ipynb** with GPU, existing four Add Inputs. This is training and is NOT yet executed. Do not assert Kaggle GPU runtime/memory/performance before run.

---

## 2026-10-08 — user-confirmed Kaggle full cache mounted path

The user provided actual Kaggle mounted cache path:
`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d12cache_full`

Kaggle Add Input sidebar lists:
- `rsna_knee_v4_consensus_dataset`
- `rsna-knee-r3d-medicalnet-pretrain`
- `rsna-knee-wide224-persistent-cache-v1` → `r3d12cache_full`

New fixed-input notebook revision (supersedes the earlier versions for user execution):
- `R3D-12V4DATA_CPU_Preflight_KnownMount.ipynb`; SHA256 `d9c7ba710c59b7c581d0c77347aa3e321bfd04bd35d39ec440d923fd03a83be7`
- `R3D-13V4_Full4349_R34_Main_KnownMount.ipynb`; SHA256 `5e8bc3515659bb2a99f5e19a534de472ec4921d34011f0d90363aa077ef364ee`
- `RSNA_Knee_R3D13V4_VerifiedMount_Notebooks.zip`; SHA256 `d26c2da83b42c3e8c3db5085400cf629b6bea6903802bcd23beab30d0318ec56`

Revision fixes the exact full cache path, adds screenshot-known V4 and pretrained dataset candidate names. All original training parameters unchanged. Validation of mount contents / canonical checkpoint shape/SHA and Kaggle execution remains pending. Run CPU preflight before GPU.

---

# R3D-12V4DATA / R3D-13V4 Kaggle Notebook Delivery (2026-10-08)

Status: **NOTEBOOKS DELIVERED; NO KAGGLE EXECUTION RESULT VERIFIED.**

## Purpose

While GPT-6 LABEL-V6 is independently reconstructed, complete a frozen Main R3D baseline using previous **V4 routed broad soft labels** (4,349 report-only studies, 12 targets). Gold58 is validation only. Keep R3D architecture unchanged, then run new LABEL-V6 under the same model/compute/seed conditions for a controlled label comparison.

See [R3D_V4_V6_CONTROLLED_COMPARISON_PLAN.md](R3D_V4_V6_CONTROLLED_COMPARISON_PLAN.md).

## Notebook 1: CPU input preflight

- File: `R3D-12V4DATA_CPU_Preflight.ipynb`
- SHA256: `7bbbb54aca75e0467eefa66fc6611e3fe273cc8ae2b5fd96f709d75d9ec7bbbe`
- Mode: CPU / Internet OFF / Save & Run All.
- Inputs: official competition `train.csv`, existing `rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_broad.csv`, `rsna-knee-r3d-medicalnet-pretrained-v1` canonical R34 weights, and whole R3D-12CACHE `r3d12cache_full/` dataset including 160 .npy volume shards.
- Check Gold58 vs report-only 4349, target order, UID disjointness, R3D-12 cache index & shard manifest SHA, 160 shard presence/size, pretrained R34 exact SHA, V4 scores/confidence and distribution.
- Outputs: `/kaggle/working/R3D-12V4DATA/R3D-12V4DATA_audit.zip`, manifests, distribution, input contract.
- The exact Kaggle *mounted dataset slug* for full `r3d12cache_full/` is not verified. It must be confirmed from user Kaggle Saved Output/Dataset; audit ZIP is not the training cache. The notebook does bounded root-candidate matching and fails fast if absent.

## Notebook 2: GPU full training

- File: `R3D-13V4_Full4349_R34_Main.ipynb`
- SHA256: `e107fb35c7ae74c25768136617f724e1d4d63f8e6b4d48f5b0fa2d4e54c047a8`
- GPU T4x2 or P100 with **only GPU0 used**, Internet OFF, Save & Run All. No unearned claim of GPU1 use.
- Initial model: MedicalNet R34 canonical pretrained SHA `977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`, >99% backbone parameter matching required. Search best.pt not reused.
- Main: ALL Series / Crop130 / interpolated D24x96x96 / R34 GLOB with plane/fluid/fat metadata / Transformer512 2L 8H FFN2048 dropout0.10 PreLN CLS / 12 heads / pure FP32 / BN running stats frozen.
- Train: V4 routed broad 4,349 studies, **five full study passes**, seed 20261013, series microbatch2, accumulation4 studies, backbone LR1e-5, new-layer LR5e-5, AdamW WD1e-4, epoch-cosine. No full DICOM regeneration.
- Objective: V4 soft BCE with absolute per-entry confidence factor `0.25 + 0.75×conf` (not normalized away). Gold58 validation Macro AUROC primary / Macro AUPRC tie-break. Gold58 has been used historically and is not independent validation; previous V4 routing used Gold57.
- Output: full model `best.pt` and `last.pt` (outside ZIP), per-epoch Gold prediction/metrics, training logs/config/manifests/input checksums, `R3D-13V4_results.zip` (no .pt).
- Runtime safety stop at epoch boundary after 9.5h planning budget; report `NEEDS_RESUME` if fewer than 5 complete epochs. Resume from own prior saved `last.pt` output only after matching config, UID/hash and pretrained asset, not from unrelated search checkpoints.

## Verification and missing facts

Local notebook nbformat/code AST checks PASS; actual uploaded V4 label, original 4407-study train CSV and R3D-12CACHE audit metadata agree (V4 4349, Gold58, 24371 series, 160 shards). CPU MedicalNet R34 forward/backward and BN freeze topology checks PASS using synthetic input.

**Not yet run on Kaggle.** Full cache actual mounted path, checkpoint topology matching actual R34 file, GPU OOM/runtime and validation outcomes remain unverified. Do not add expected metrics to EXPERIMENT_HISTORY as completed results.

## Next

1. User adds all four required Kaggle inputs.
2. Run R3D-12V4DATA CPU preflight and provide audit ZIP/log.
3. If PASS, run R3D-13V4 GPU notebook, upload results ZIP/log. Preserve Kaggle Output best.pt.
4. Then make R3D-14V4 standalone submission notebook. Only after V6 canonical release do matched V6 replay.

