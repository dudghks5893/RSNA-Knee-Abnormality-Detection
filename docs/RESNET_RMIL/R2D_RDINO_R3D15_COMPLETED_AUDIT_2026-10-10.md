# R2D / RDINO / R3D-15 — Completed Train300 Pilot Evidence

Updated: **2026-10-10**. Results are from **eleven user-provided, audited Kaggle output ZIPs** with saved best Gold58 metrics and **artifact_sha256.json**. Audit independently checked archive CRC, all recorded file SHA entries, and summary versus metrics consistency; binary `best.pt` not included in review ZIP. These numbers are *not* Public LB.

## Shared experiment contracts

- **All:** Train300 report-only V4 pseudo labels (confidence-weighted soft BCE) / **Gold58** official binary labels as repeated development validation, 12 targets. Full 3D R3D-15 and 2D/2.5D models use distinct image caches/input representations. Do not claim strict 2D-vs-3D causal parity.
- **R2D / RDINO:** canonical `R2D_SHARED224_V1` with 358 studies / 2,006 series; all Series, 4 native 3-Slice windows/Series, 130mm crop, 224×224 uint8, frozen UID/index SHA `664b9b6ef3889e2d1d9694b0fd0424afa32ce8785ea99ddfdfbb53d85e87495e`; GPU0=2D center x3, GPU1=2.5D adjacent x3, per-Series 4-window **uniform feature mean** followed by metadata-aware 2-layer/8-head CLS Transformer 512, 12 logits, full fine-tuning, max10 epochs, separate backbone 1e-5/head 5e-5.
- **R2D A:** MedicalNet 3D R34 pretrained **deflated to 2D**, Option A shortcuts; source original weights SHA `977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`.
- **R2D B:** RadImageNet ResNet50 pretrained, source as recorded per ZIP.
- **RDINO A/B:** public Kaggle MetaResearch DINOv2-Small / Base Hugging Face `pytorch_model.bin`, strict offline load; Small weights SHA `1051e25b2ed69ddad24f3c41e7b6eed6e7f7d012103ea227e47eb82e87dc2050`, Base `014965d9e330e7f4bff8ddcbee9df5e4f2ca032b2f5180942a6edb454783e75d`; identical common cache but model-specific normalize. V1 crashed before GPU due `scale` vs `SCALE` NameError; **V2 fixed**, both arms completed.
- **R3D-15 B0/A/B:** MedicalNet R34, full 3D 96×96 D24 data pilot with separate full-volume cache and altered spatial/target attention, not same pixel inputs as R2D. B0 canonical GLOB, A local-feature arm, B target-attention arm. Full model paths/splits refer to original R3D-15 notebooks. Not a fold ensemble.

## All 11 Gold58 best-checkpoint scores

| Rank | ID | Model/Input | Macro AUROC | Macro AUPRC | Best epoch |
|---:|---|---|---:|---:|---:|
| 1 | R2D-SHARED-A-25D | R34 2.5D | **0.57637044** | **0.45072965** | 4 |
| 2 | R2D-SHARED-A-2D | R34 2D | 0.56675919 | 0.42439995 | 7 |
| 3 | R2D-SHARED-B-2D | RadImageNet R50 2D | 0.56401818 | 0.42959922 | 10 |
| 4 | R2D-SHARED-B-25D | RadImageNet R50 2.5D | 0.54585481 | 0.41233657 | 10 |
| 5 | A_RDINO-01-small-25D | DINOv2 Small 2.5D | 0.53745700 | 0.42160187 | 3 |
| 6 | B_RDINO-01-base-25D | DINOv2 Base 2.5D | 0.53659501 | 0.39696317 | 2 |
| 7 | B_RDINO-01-base-2D | DINOv2 Base 2D | 0.53208528 | 0.40460075 | 4 |
| 8 | R3D-15A | MedicalNet R34 3D local | 0.53149877 | 0.39425334 | 4 |
| 9 | R3D-15B | MedicalNet R34 3D target-aware | 0.52988099 | 0.40433116 | 5 |
| 10 | A_RDINO-01-small-2D | DINOv2 Small 2D | 0.52820586 | 0.40932126 | 6 |
| 11 | R3D-15B0 | MedicalNet R34 3D baseline | 0.52780057 | 0.39747513 | 5 |

**Observed within-Backbone 2.5D - 2D AUROC:** R34 +0.009611; RadImageNet R50 -0.018163; DINO-S +0.009251; DINO-B +0.004510. Thus 3/4 directionally favor 2.5D but general superiority is **not proven**. DINO S vs B 2.5D difference is negligible; extra capacity did not demonstrate benefit here.

## Target-wise observed 11-model winners (descriptive, not deployment policy)

| Target | Best model | AUROC |
|---|---|---:|
| ACL | R3D-15A (3D) | 0.627451 |
| MCL | R2D-SHARED-A-25D | 0.709751 |
| Medial Meniscus | R2D-SHARED-A-2D | 0.599760 |
| Lateral Meniscus | R2D-SHARED-A-25D | 0.561491 |
| Medial OA | B_RDINO-01-base-25D | 0.739535 |
| Lateral OA | B_RDINO-01-base-2D | 0.702128 |
| PF OA | B_RDINO-01-base-25D | 0.637066 |
| Effusion | R2D-SHARED-A-25D | 0.665839 |
| Synovitis | R2D-SHARED-A-25D | 0.641577 |
| Baker's | R2D-SHARED-A-25D | 0.632246 |
| Contusion | R3D-15A (3D) | 0.500675 |
| Fracture | A_RDINO-01-small-25D | 0.545833 |

Do not choose experts based on these winners: 11 models × 12 targets were inspected on the same repeatedly used **58 studies** (e.g. MCL positives only 9, Lateral OA positives 11). ACL R3D win margin is small; Contusion 0.501 is nearly random. The hypothetical target-wise oracle AUROC is **not an honest deployable model score**.

## Relevant older full-data/leaderboard context

- **Exp57 Public LB 0.918**, 3-Fold Top24 B3A + Full-MRI Direct 70:30 (strongest available public leaderboard baseline).
- **SS08 12-specialist-only Public LB 0.876**; pseudo FixedVal 0.9341 did not generalize to hidden test and removing Exp57 Full branch/folds confounds mechanism.
- **R3D-13V4 full4349 Gold58 0.680227 / Public LB 0.689 (R3D-14V4)**; low resolution and different representation may be bottlenecks; cannot infer causality from one comparison.
- **Later development note (2026-10-10):** RMIL-01 did subsequently complete; Gold58 K4 MEAN 0.57637044 vs shared ATTN 0.54429630. Details in [RMIL-01 completed audit](RMIL-01_COMPLETED_AUDIT_2026-10-10.md). The older eleven-run table above remains unchanged. Follow-on native K/Attention ablations are PLANNED, see [RMIL-02/03 approved protocol](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md).

## Audit details and provenance

Inspected user-provided ZIPs: `R2D-SHARED-A-2D_results.zip`, `R2D-SHARED-A-25D_results.zip`, `R2D-SHARED-B-2D_results.zip`, `R2D-SHARED-B-25D_results.zip`, `A_RDINO-01-small-2D_results.zip`, `A_RDINO-01-small-25D_results.zip`, `B_RDINO-01-base-2D_results.zip`, `B_RDINO-01-base-25D_results.zip`, `R3D-15B0_results.zip`, `R3D-15A_results.zip`, `R3D-15B_results.zip`. For all 11 ZIPs, all recorded file SHA-256 digests matched ZIP entries, and 12 per-target metrics were present. Existing audits confirm 58 unique UIDs, probability validity; full binary checkpoints were not in ZIPs and so were not independently reloaded. No hidden-test Public LB for these 11 pilots.

Recommended next: **[RMIL-02/03 native Window experiment protocol](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md)** and **[RMIL architecture & roadmap](RMIL_FINAL_ARCHITECTURE_AND_EXPERIMENT_PLAN.md)**.
