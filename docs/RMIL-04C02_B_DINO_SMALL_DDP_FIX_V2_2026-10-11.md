# RMIL-04C02 B — DINOv2 Small DDP reducer bug fixed V2

**2026-10-11 — prior B notebook crashed at Full Train first batch (no epoch completed). Updated B notebook is ready; actual Kaggle T4x2 rerun has NOT yet occurred.** ResNet notebook is unchanged.

## Kaggle failure evidence
- Submitted Kaggle log `붙여넣은 텍스트(1)(20261011-102827).txt`. MRI five pack 190 HDF5 SHA gate and V4 schema passed. DINO strict pretrain model SHA verified; GPU Tesla T4 x2; first GPU smoke returned `PASS_REAL_2RANK_GPU_SMOKE` in 0.93 min, then `PHASE FULL_TRAIN` failed in 0.52 min with `RuntimeError: Expected to have finished reduction in the prior iteration`; rank1: `Parameter indices which did not receive grad for rank 1: 2`. No completed epoch, no valid full cohort checkpoint.
- Likely class of bug: DINOv2 pretrained `encoder.embeddings.mask_token` is used in masked-token pretraining when `bool_masked_pos` is provided; our classification forward omits masking; DDP was `find_unused_parameters=False`. The reducer index=2 is not authoritative evidence of a specific named parameter; modified Notebook will print indexed runtime named parameters and fail-fast on unexpected no-grad names.
- Earlier smoke only ran one optimizer step and did not test the subsequent DDP reducer `_rebuild_buckets()` invocation; thus old smoke PASS did not guarantee second-step correctness.

## Corrected B notebook (replaces `RMIL-04C02_B_DINOv2Small_Full4349_K16_T4x2.ipynb`)
- Filename `RMIL-04C02_B_DINOv2Small_Full4349_K16_T4x2_DDP_FIX_V2.ipynb`
- **Notebook SHA256** `a0d18b42ae006ddbf5cdd43af0ba33033bf572a8f42b3dcd7b2b77634971ceb1`
- **Embedded worker SHA256** `e2ce001a15b384e1cccc661bb412685a54e5332a609728a5914fe9c8f0e38533`.
- Changes: strict Small checkpoint load **then** freeze optional `mask_token` requires_grad; DDP `find_unused_parameters=True`; print indexed parameter names, after each smoke full backward and after first real full-training batch assert every remaining trainable param has a gradient, returning names on failure; smoke now performs two consecutive synchronized optimizer steps using largest four K16 TRAIN studies, then largest Gold58 study eval and torch.save/torch.load; Notebook outer gate requires smoke JSON `smoke_optimizer_steps==2`.
- Other behavior unchanged: source4 Add Input (exact user-mount paths), MRI Full4,407/Train4,349/Gold58, K16 Mean, 12 targets, V4 broad SHA pinned, ResNet-independent DINO model-specific ImageNet norm and optimizer, 10 epoch max / 5 min / patience3, T4×2 DDP, global batch4, per-target loss, checkpoint best/last and ZIP finalizer. LABEL-V6 `CANDIDATE_NOT_RELEASED`, not trained.

## Verification
- **Reproduced same second-forward DDP reducer crash** on two CPU Gloo ranks using a DINO-like class with unused mask_token and nonreentrant activation checkpoint (old config exited with failure); freeze mask and unused detection passed two complete synchronized optimizer steps (fixed config exit 0). This structural test is **not** the full original Kaggle pretrained DINO model execution.
- `nbformat.validate`, code-cell AST and embedded worker AST PASS, final-result artifact export synthetic End-to-End test PASS, unchanged input paths and label preflight checks PASS (13 automated structural checks).
- **Kaggle real T4 GPU test pending;** need new Notebook Save & Run All with exact same four inputs. Expected markers: `GPU_SMOKE_DDP_STEP 1/2 PASS`, `GPU_SMOKE_DDP_STEP 2/2 PASS`, `PHASE FULL_TRAIN`, `EPOCH_COMPLETED`, `FINAL PASS`. No result claims before output.
- Run name suggestion `RMIL04C02 B DINOv2Small DDP Fix2 T4x2`. Save & Run All / Internet OFF. A ResNet original notebook unchanged.
