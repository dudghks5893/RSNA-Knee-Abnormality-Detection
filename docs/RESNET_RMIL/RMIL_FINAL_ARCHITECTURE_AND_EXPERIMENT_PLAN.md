## 2026-10-10 — RMIL-02D 완료·독립 검증: K16 Shared Attention < K16 Mean

**최신 확정 단계: RMIL-02D 두 모델 Kaggle Save & Run All 완료/PASS.** `RMIL-02D_results_for_review.zip` SHA256 `67badca393c11ab7664ca2e8f120e5e93181209a8e96f784bb9bc020377373c8`; ZIP 57파일 CRC PASS, 선언된 **49개 산출물 SHA256 일치**, 58×12 예측·매크로·최적 Epoch·336 GOLD Series Attention 진단 및 공통 초기 가중치 SHA 검증 PASS. K16 Mean의 58×12 예측은 RMIL-02C K16 Mean과 **파일 SHA까지 동일**(정확히 재현).

| V3 동일 캐시·동일 K16 | Macro AUROC | Macro AUPRC(최적 AUROC Epoch) | Best Epoch | 전체 Epoch |
|---|---:|---:|---:|---:|
| **Mean** | **0.577856** | **0.432300** | 5 | 8 |
| Shared Window Attention | 0.564698 | 0.415525 | 9 | 10 |
| Attention − Mean | **−0.013158** | **−0.016775** | | |

Attention은 개선 AUROC 5/12 질환, 악화 7/12. 가장 크게 악화한 Effusion **−0.13416**, 개선한 Fracture **+0.07222**, Lateral OA **+0.07544**, Medial OA **+0.05736**. 실효 Window 평균 **12.888개**, 가중치 엔트로피 **0.94243**, top1 평균 **0.10395**(균등 **0.06367**); Attention은 실제로 학습했으나 전체 성능을 높이지 못함. **일괄 Shared Scalar Attention 승격 보류**.

**다음 실험:** RMIL-03 (K16 V3 동일 조건, 질환별 Window Attention → 질환별 Window+Series Attention) 순차 검증; 개선 효과가 불확실하므로 재현성·샘플 크기 점검. 이후 RMIL-04 전체4,349명 학습 및 Standalone 제출. RMIL-05 2D/MIL 및 RMIL-06 3D 결합은 실제 보완 증거가 있을 때만. 고해상도 320/384/original-varying은 Attention 실험과 분리된 선택적 변수.

**전체 7개 RMIL-01/02C/02D 모델 성능 및 12개 질환별 상세:** [RMIL-02D 완료 통합 보고서](RMIL-02D_K16_MEAN_VS_SHARED_ATTENTION_COMPLETED_2026-10-10.md). **RMIL-01 K4는 다른 픽셀 전처리이므로 V3 순위에 직접 포함 금지.** Gold58 반복 개발 검증으로 통계적 일반화, Public LB 점수 주장 금지. 코드 디버깅 이력은 작성하지 않음.

---

## 2026-10-10 — 최신 결과: RMIL-02B 공통 영상 캐시 생성 완료

**실험 결과:** RMIL-02B V3 Kaggle CPU 전체 실행 **완료** (`PASS_NEW_PREPROCESS_V3`). Train300 + Gold58 **358명**, **2,006 Series**, **66,430 Slice**의 원본 MRI로 공통 224×224 `uint8` 캐시를 생성했습니다. HDF5 **16개 샤드**, 전체 파일 크기 **3,341,400,768 bytes(약 3.34GB)**, 실제 실행 시간 **23.41분**. 개별 샤드는 Kaggle 실행 과정에서 저장 후 읽기·SHA 검증을 수행했습니다.

**독립 감사:** 제공받은 `RMIL-02B_V3_results_for_review.zip` SHA-256 `f21f454542b47c99e3ef4d1503c191a5d1e006387c8d0e5e81e7cd320625fdd8`. ZIP CRC PASS, **메타데이터 7개 파일 SHA 전부 일치**, Study/Series UID 중복 0, 2,006개 Series의 실제 Slice 수·K 중첩/유효 Window·물리 정렬 재검사 오류 0. 단, **영상 HDF5 자체 바이트는 ZIP에 없으므로 독립 SHA 재계산 미완료**. 다음 학습 Notebook은 마운트된 16개 영상 샤드를 다시 SHA 검증합니다.

**K별 실제 Window:** K4 **8,024**, K16 **31,838**, K24 **45,472**, K32 **53,532**(보류). **130mm FOV 바깥 배경 패딩은 24/2,006 Series**, 20% 이상 16개(모두 Axial), 최고 61.14%. 이 패딩 분포는 영상 조건상 확인된 데이터 특성으로 기록하며 임의 제외하지 않습니다.

**다음 단계 — RMIL-02C:** 한글 Notebook `RMIL-02C_K4_K16_K24_Mean_Train300_T4x2_KO.ipynb` (SHA-256 `627aa87ab7327bfdb6eb6be55e6d96503f02aa5f1c03e3dd85e5e8bd708c2c18`) 준비, Kaggle GPU 실행 **전**. Add Input **3개**: 완료된 RMIL-02B V3 Notebook Output 전체(16개 HDF5 샤드 포함), 기존 `rsna-knee-wide224-persistent-cache-v1` frozen Train300/Gold58 메타데이터, `rsna-knee-r3d-medicalnet-pretrained-v1` MedicalNet R34 가중치. **T4×2, Internet OFF, Run All**. GPU0 K4→K16, GPU1 K24, 모두 MedicalNet-deflated R34 2.5D + 메타데이터 Transformer, Train300 V4 soft/conf weighted BCE, Gold58, full fine tune, Mean pooling 및 동일 optimizer/seed 사용. 코드 셀/Worker 문법과 가변 Window HDF5 합성 검사는 PASS이나 **실제 T4 실행 검증 전**이며 성능 결과는 없음. 결과 ZIP `RMIL-02C_results_for_review.zip`에 모델이 아닌 성능·예측·로그를 담고 best.pt는 Output에 각각 보존합니다.

완료 캐시 자세한 검증: [RMIL-02B V3 완료 결과](RMIL-02B_V3_CACHE_COMPLETED_2026-10-10.md). 기존 RMIL-01 K4는 서로 다른 영상 전처리이므로 이번 K4의 비교 기준으로 사용하지 않습니다. 코드 오류 수정 내역은 별도 GitHub 기록으로 만들지 않습니다.

---

# RMIL — High-Score Architecture Candidates & Next Experiments

Updated: **2026-10-10**. **Status: C1/C2/C3 NOT YET SELECTED; RMIL-01 COMPLETED; RMIL-02 NEXT (PLANNED).** This is the new forward-looking imaging-model plan. Existing numbering `EXP-01` is occupied; use **RMIL-01..06**. This does not rename or invalidate previous R2D, RDINO, R3D, SS, Exp57 histories.

## 2026-10-10 — RMIL-01 actual result (supersedes original execution instructions below)

**COMPLETED/AUDITED.** [RMIL-01 artifact audit and 12-target comparison](RMIL-01_COMPLETED_AUDIT_2026-10-10.md): MEAN Gold58 macro AUROC **0.5763704369**, macro AUPRC **0.4507296488**, best epoch4/7 total; shared 4-window ATTN AUROC **0.5442963023**, AUPRC **0.4158921311**, best epoch3/6 total. ATTN − MEAN **−0.0320741346 AUROC**, **−0.0348375177 AUPRC**, 4/12 targets up, 8/12 down. Received review ZIP CRC and all **38 declared internal SHA-256 entries verified**; ZIP SHA `0642f2363003031a9e88c5f5c3e759bb16e95a45eb278d740f0ed204cf26449f`. No binary checkpoints or raw Gold labels inside review ZIP. This is reused development Gold58, not Public LB.

**Decision:** preserve 4-window uniform MEAN as comparator; reject promotion of this *shared scalar* ATTN under current conditions, without claiming target-specific attention cannot work. **RMIL-02 is NEXT, not yet executed**; CPU-first high-coverage actual Slice cache experiment, keep number of candidate windows and selection policy as separate axes. **Important source constraint:** the canonical R2D_SHARED224_V1 cache stores only four selected 3-Slice windows per Series; it cannot produce new, native 16/24/32 windows. Use original raw DICOM or a separately verified full-native-Slice cache, with patient/Series IDs and physical ordering reconciled to frozen manifests. Audit 4-window reconstruction parity (crop, scaling and index/UID) before interpreting any wider-window gain. Do not invent an already-mounted full-Slice Kaggle Input. RMIL-03 still unexecuted. C1/C2/C3, 3-/5-Fold, Exp57 blend remain undecided/deferred. Exp57 best Public LB remains 0.918.

## 2026-10-10 — RMIL-02B0 COMPLETED; RMIL-02B New V2 cache prepared (OVERRIDES older K4 parity hard gate)

**Actual artifact audit PASS**, but **K4 image parity FAIL**: ZIP SHA256 `3f7ee4b7a12db3b0297ed3d11eebce31133d4bc87adeb08687df4ece33c06a27`, CRC PASS, all 5 declared output SHA pass. Diagnostic 9 Series across 3 Studies / 144 candidate pixel transformations, ZERO exact entire-Series matches, best mean MAE 8.476386 and byte match fraction ~0.153%. No cache pixel output, no GPU; existing RMIL-01 score unchanged. **[Detailed completed RMIL-02B0 audit](RMIL-02B0_COMPLETED_PARITY_AUDIT_2026-10-10.md).**

**Decision to avoid repeated uncertain cache-builder archaeology:** original R2D-CACHE-01 exact pixel implementation NOT available; freeze newly specified and reproducible **`RMIL-02B-NATIVE224-V2` preprocessing** for the same 358 Study original DICOM source instead. **A fresh `RMIL-02C-K4-NEW` training baseline is MANDATORY** before interpreting K16 and K24 count effect. Old RMIL-01 0.576370 is historical only; cannot substitute as K4 for new V2. Within new V2 cache compare K4 Mean, K16 Mean, K24 Mean (K32 conditional) from nested selected native Slice center windows, then at matched K compare Mean vs shared attention. RMIL-03 later.

**Prepared new CPU notebook (NOT Kaggle-executed)** `RMIL-02B_Native224_SharedCache_CPU.ipynb`, SHA256 `097c72a070114caa53603180f9813ec16c3edf15ab7dc1ff84c30a279cbc080b`, syntax/nbformat PASS, synthetic nested selector 310 source lengths PASS. Accelerator None, Internet OFF, Save & Run All, 2 existing inputs (competition + `rsna-knee-wide224-persistent-cache-v1`); 358 studies / 2006 Series / 66430 real slices. V2 preproc exact contract spelled out in notebook and [audit](RMIL-02B0_COMPLETED_PARITY_AUDIT_2026-10-10.md), **NOT claimed historical image parity**. Output `RMIL-02B_NATIVE224_V2/shards/shard_###.h5` 220MB-target SHA/atomic, manifest and metadata-only ZIP `RMIL-02B_results_for_review.zip`; keep whole Kaggle Notebook output as next model Input. Kaggle saved output all-working total 14.0GB project cap, ≥2GB physical free. Actual pixels not yet created and GPU experiments not run.

---

## 2026-10-10 — RMIL-02A ACTUAL RESULTS VERIFIED (supersedes previous 'unexecuted 02A' below)

**COMPLETED/PASS_METADATA_PREFLIGHT.** Actual user-supplied `RMIL-02A_results_for_review.zip` independently CRC+all 9 declared file SHA PASS; received ZIP SHA256 `fbabf2840be680d62c636f86af5e4bb1cc87a3c6c2619fe875d0dfca6008520f`. Kaggle CPU preflight on frozen **358 Studies/2006 Series/66430 native Slices**, **0 issues**, DICOM sample decode PASS, ~11.254min header survey. Actual K full Series: 4 **2006**, 16 **1924**, 24 **1513**, 32 **516**. Real unique windows K4 **8024**, K16 **31838**, K24 **45472**, K32 **53532**. **Recommended first mean-only K16 vs K24**, K32 conditional: 1490/2006 Series cannot fill K32. Verified legacy K4 centers exactly fit **`round(linspace(.1*(N-1),.9*(N-1),4))` for all 2006 Series** (metadata indices only; orientation/pixel parity still NOT verified).

**Disk:** 66430×224² uint8 single-channel = **3.104277GiB** pixel bytes; projected *future cache peak* **4.633149184GB decimal**, safely under project **14.0GB all-working-files cap** (runtime effective remaining **13.983781468GB**). This is a budget eligibility projection, not actual generated image-cache bytes. **No new pixel cache created; no new GPU/Gold AUROC results.** The original K4 image transform parity is a HARD GATE.

**NEXT = RMIL-02B0 (prepared, not executed),** `RMIL-02B0_K4_Pixel_Parity_Probe_CPU.ipynb`, local SHA256 `0bf941097a3bdd5db04b4093f6dfe7e853127b5704011db5cbe98251a209804c`: same two Kaggle inputs, CPU only, diagnostic sample comparison for physical order, Crop130, percentiles, normalization and quantization. Only after the actual original R2D-CACHE-01 implementation (preferable) / strict K4 parity is verified may RMIL-02B **358-Study native pixel shards** be built. RMIL-01 is completed and immutable; RMIL-03 after higher K data+shared Attention ablation. Details: [RMIL-02A completed metadata and K feasibility audit](RMIL-02A_COMPLETED_METADATA_AUDIT_2026-10-10.md).

---

## 2026-10-10 — Mandatory RMIL-02B storage-budget preflight

Kaggle persists at most **20GB** of `/kaggle/working` Notebook Output per official docs. Enforce stricter RMIL-02 project **14.0GB decimal TOTAL working-files cap** and runtime free-space check (at least 2GB extra free physical disk reserve). Preflight projected single-channel 224px native Slice cache size from actual counts, budget +30% overhead +300MB staging; do not generate multiple K pixel copies or duplicate cache in ZIP; split into ≤512MB checked shards with per-shard quota recheck. If size exceeds budget, block/split before decode. [Detailed policy](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md). Updated prepared CPU notebook `RMIL-02A_Native_Slice_Preflight_DiskSafe_CPU.ipynb` SHA256 `1516660b1d413aa384a193122593aad21d057832c4405a64be9d9e9e973204dd` emits `disk_budget.json`; Kaggle run pending.

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
