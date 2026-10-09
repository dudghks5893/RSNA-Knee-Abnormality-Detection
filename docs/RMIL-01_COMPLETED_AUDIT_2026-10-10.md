# RMIL-01 — Window Mean Pooling vs Window Attention — Completed Artifact Audit

Updated: **2026-10-10**. Experiment status: **COMPLETED (Kaggle Save & Run All; both workers PASS)**. Decision: **retain uniform MEAN as the RMIL-02 comparator; do not promote this 4-window shared ATTN**. This is a small, repeatedly used **Gold58 development** comparison, **not a Public LB**.

## Evidence and provenance

- User supplied `RMIL-01_results_for_review.zip` and copied original Kaggle Notebook/log output on 2026-10-10.
- Locally recomputed SHA-256 of received ZIP: `0642f2363003031a9e88c5f5c3e759bb16e95a45eb278d740f0ed204cf26449f`.
- ZIP CRC test PASS: **43 archive entries**, all readable; verified all **38 listed artifact SHA-256 digests** (20 MEAN + 18 ATTN) from two `artifact_sha256.json` manifests. Comparison CSV exactly matches independent per-target delta arithmetic. Best metric/prediction files are byte-identical to the appropriate epoch artifacts.
- Per arm: 58 unique study UID rows, same UID order across arms, 12 target probability columns, finite predictions in [0,1], correct target names; all epochs' reported macro AUROC/AUPRC re-averaged from respective 12 rows and matched training history/summary. Target-positive and target-negative counts sum to 58 and match across arms.
- Kaggle log documents two visible T4s, full cache pixel SHA check of 358 studies / 2,006 Series, strict MedicalNet pretrain SHA check, isolated GPU0=MEAN / GPU1=ATTN subprocesses, separate GPU forward/backward smoke PASS, both return code 0, final ZIP aggregation PASS. These Kaggle-source bytes were **not independently available** outside the Kaggle environment.
- Worker code SHA reported by execution log: `156ed04657bdeb6684a74dfae8a5695e9be4f7b7cf90bf9466a08f476730c21d`.
- **Limits:** ZIP intentionally excludes original `best.pt` binaries, Gold58 ground-truth manifest, full original source cache, and full separate worker console files. Checkpoint SHA below comes from executed console log only, not independently hashed original bytes. AUROC/AUPRC could be cross-checked for artifact consistency, but **not recomputed from ground truth** without labels. No independent hidden-test scoring, OOF estimate or multi-seed significance result.

## Controlled comparison contract

Both arms: Kaggle Account A / isolated physical T4 workers / Internet OFF, Train300 report-only V4 pseudo weighted BCE, repeated Gold58 development val, frozen `R2D_SHARED224_V1` 358-study cache; all Series, **4 native 3-Slice 224×224 130 mm windows per Series**, MedicalNet3D→2D deflated R34 Option-A, full fine-tune, frozen BN running stats, Series metadata + 2L/8H CLS Transformer512 and 12 logits, seed 20261013, FP32, LR backbone 1e-5 / head 5e-5, WD 1e-4, cosine, max10 epochs / min5 / patience3, 4-window microbatch / 4-study accumulation.

The only shared configuration differences are `experiment`, `pooling`, and its descriptive `aggregation`. ATTN is one shared scalar per-window softmax layer initialized to zero (= initial MEAN), **not target-specific MIL**. Source pretrained SHA both: `977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`; cache index SHA both: `664b9b6ef3889e2d1d9694b0fd0424afa32ce8785ea99ddfdfbb53d85e87495e`.

## Best-checkpoint result

| Metric | GPU0 MEAN | GPU1 ATTN | ATTN − MEAN |
|---|---:|---:|---:|
| Gold58 Macro AUROC | **0.5763704369** | 0.5442963023 | **−0.0320741346** |
| Gold58 Macro AUPRC | **0.4507296488** | 0.4158921311 | **−0.0348375177** |
| Best epoch | 4 | 3 | different checkpoint-selection times |
| Completed epochs | 7 | 6 | both EARLY_STOP |
| Train minutes (worker) | 9.2375 | 8.0111 | parallel lanes, not total Notebook runtime |
| Best checkpoint SHA (LOG ONLY) | `3c16685daf3f7cf3533931f4574f781519402c65a34048b70783b1a172ccf053` | `0da183ec108c367f3a6d7aa6c937081d747c1d58f572d7731e3aad00dc06847d` | binary not supplied |

The MEAN best Macro AUROC reproduces prior `R2D-SHARED-A-25D` 0.57637044 to quoted precision. ATTENTION parameter norm was nonzero and increased during training (epoch1 0.013866, best epoch3 0.016846, epoch5 0.021079). This establishes nonzero learned weights, **not** useful attention concentration / faithful clinical selection.

## All 12 target-wise Gold58 best AUROC

| Target | Gold positives | MEAN | ATTN | ATTN − MEAN |
|---|---:|---:|---:|---:|
| ACL | 24 | 0.618873 | 0.541667 | −0.077206 |
| MCL | 9 | 0.709751 | 0.446712 | −0.263039 |
| Medial Meniscus | 26 | 0.597356 | 0.623798 | +0.026442 |
| Lateral Meniscus | 23 | 0.561491 | 0.521739 | −0.039752 |
| Medial OA | 15 | 0.537984 | 0.596899 | +0.058915 |
| Lateral OA | 11 | 0.462282 | 0.582205 | +0.119923 |
| PF OA | 21 | 0.536680 | 0.487773 | −0.048906 |
| Effusion | 35 | 0.665839 | 0.575155 | −0.090683 |
| Synovitis | 27 | 0.641577 | 0.623656 | −0.017921 |
| Baker's | 12 | 0.632246 | 0.615942 | −0.016304 |
| Contusion | 19 | 0.442645 | 0.403509 | −0.039136 |
| Fracture | 18 | 0.509722 | 0.512500 | +0.002778 |

ATTN improves **4/12** targets (notably Lateral OA) and worsens **8/12**, especially MCL, Effusion and ACL; target-wise cherry-picking on reused Gold58 would be unstable, especially MCL **9 positive** and Lateral OA **11 positive**. AUPRC: 0.450730→0.415892 macro decline; individual deltas are available in the original `RMIL-01_target_delta.csv`.

## Decision and next step

1. **RMIL-01 CLOSED:** fixed 4-window shared learned ATTN is **not promoted**; MEAN retained as the stronger controlled comparator. Do not claim universal failure of Attention or superiority of uniform pooling for denser / target-specific inputs.
2. **RMIL-02 NEXT (PLANNED, NOT EXECUTED):** CPU-only preparation of consolidated, physically sorted, adjacency-preserving per-Series 16/24/32 actual Slice window candidate cache. Pin manifest/data SHA, quantify coverage, duplication, Series inclusion, bytes/time, and isolate `window count` from `selection policy`. Keep a 4-window control and equivalent backbone/split/optimization/training budget for subsequent GPU ablation. Estimate costs from CPU preflight before materializing a large cache. Do not reserve T4s for raw DICOM decode.
3. **RMIL-03 target-specific Window/Series attention remains a separate unexecuted hypothesis**. Revisit only after data coverage study; no target-wise Gold58 oracle routing, no multi-fold, no Exp57 blend at this stage.
4. **Final C1/C2/C3 architecture still UNDECIDED.** Project best Exp57 **Public LB 0.918** remains unchanged.

See [active RMIL plan](RMIL_FINAL_ARCHITECTURE_AND_EXPERIMENT_PLAN.md), [Experiment History](EXPERIMENT_HISTORY.md), [current handoff](CURRENT_HANDOFF.md).
