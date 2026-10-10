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

## 2026-10-10 — RMIL-02D K16 Mean vs Shared Window Attention 준비 완료

**현재 단계:** RMIL-02C의 K4/K16/K24 Mean 학습·검증은 모두 완료. K16이 Gold58 Macro AUROC **0.577856**, AUPRC **0.432300**으로 상대적 최고이나 K4 대비 증가는 **+0.003437**이며 개발 검증 Gold58 재사용에 주의.

**다음 RMIL-02D — 실행 전 준비 완료:** 한글 Kaggle Notebook `RMIL-02D_K16_Mean_vs_SharedWindowAttention_T4x2_KO.ipynb` SHA-256 `64e6a086bb4d24c1a449b24c0d3e07a16b0e4db9d8de3eddce073cf604e96d06`. **GPU 학습·검증 결과는 아직 없음**. 새 Mean(K16)과 새 Shared Window Attention(K16)을 **T4×2의 GPU0/GPU1에서 병렬 학습**해 Pooling 효과만 비교. 기존 RMIL-02C K16 체크포인트의 성능은 참고하고 공정한 Pair의 Mean을 이번 실험에서 새로 학습함. Attention은 **Series 내 Window마다 공유 스칼라 Linear→Softmax 가중 평균, 0 초기화**(학습 시작 시 Mean 동일)이며 질환별 Attention이 아님.

**고정 조건:** 새 RMIL-02B V3 이미지 캐시, Train300 V4 soft/conf weighted BCE, Gold58, 동일 K16 선택(전체 31,838 Window), 전체 2,006 Series, MedicalNet3D→ResNet34 deflation Option-A, 512차원/2층/8헤드 메타데이터 Transformer, Backbone full FT, Seed20261013, AdamW, cosine LR, 10 Epoch/최소5/patience3, Window microbatch4, Study accumulation4. 양쪽의 **공통 초기 State SHA**와 16개 HDF5 샤드 SHA/데이터 분리·동일 학습 설정 확인을 강제.

**Kaggle Add Input 3개:** (1) `rmil-02b-native224-v3` → `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`; (2) `rsna-knee-wide224-persistent-cache-v1` → `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1`; (3) `rsna-knee-r3d-medicalnet-pretrained-v1` → `/kaggle/input/datasets/yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1/resnet_34.pth`. **T4×2, Internet OFF, Run All**, Save Version `RMIL-02D K16 Mean vs SharedAttn T4x2`. 예상 소요 55~110분(실측 전).

**출력:** `RMIL-02D-K16-MEAN/`와 `RMIL-02D-K16-ATTN/`의 별도 `best.pt`, 학습곡선·질환별 AUROC/AUPRC·Gold58 예측, Attention 최고 Epoch의 Series별 최대 가중치·엔트로피·실효 K 등 진단. `RMIL-02D_results_for_review.zip`는 메타데이터·로그만 보존, 모델은 Kaggle Output에 유지. Attention 가중치 자체를 병변 위치의 증거로 해석하지 않음.

**Notebook 사전 검사:** nbformat 및 각 코드 셀/내장 Worker 문법 PASS, CPU 합성 네트워크에서 가변 Window 수의 초기 Mean/Attention 출력 일치·초기 공통 가중치 동등·Attention/Encoder 역전파 PASS. 이것은 실제 Kaggle 결과가 아님.

**이후:** RMIL-02D 결과 검증 → 개선이 있더라도 재현성/시간비용 검토 → 필요 시 RMIL-03 질환별 Attention 테스트. 이전 실험 결과를 재판정하거나 수정하지 않으며 단순 코드 오류 이력도 GitHub에 별도 작성하지 않음.

---

## 2026-10-10 — 최신 결과: RMIL-02B 공통 영상 캐시 생성 완료

**실험 결과:** RMIL-02B V3 Kaggle CPU 전체 실행 **완료** (`PASS_NEW_PREPROCESS_V3`). Train300 + Gold58 **358명**, **2,006 Series**, **66,430 Slice**의 원본 MRI로 공통 224×224 `uint8` 캐시를 생성했습니다. HDF5 **16개 샤드**, 전체 파일 크기 **3,341,400,768 bytes(약 3.34GB)**, 실제 실행 시간 **23.41분**. 개별 샤드는 Kaggle 실행 과정에서 저장 후 읽기·SHA 검증을 수행했습니다.

**독립 감사:** 제공받은 `RMIL-02B_V3_results_for_review.zip` SHA-256 `f21f454542b47c99e3ef4d1503c191a5d1e006387c8d0e5e81e7cd320625fdd8`. ZIP CRC PASS, **메타데이터 7개 파일 SHA 전부 일치**, Study/Series UID 중복 0, 2,006개 Series의 실제 Slice 수·K 중첩/유효 Window·물리 정렬 재검사 오류 0. 단, **영상 HDF5 자체 바이트는 ZIP에 없으므로 독립 SHA 재계산 미완료**. 다음 학습 Notebook은 마운트된 16개 영상 샤드를 다시 SHA 검증합니다.

**K별 실제 Window:** K4 **8,024**, K16 **31,838**, K24 **45,472**, K32 **53,532**(보류). **130mm FOV 바깥 배경 패딩은 24/2,006 Series**, 20% 이상 16개(모두 Axial), 최고 61.14%. 이 패딩 분포는 영상 조건상 확인된 데이터 특성으로 기록하며 임의 제외하지 않습니다.

**다음 단계 — RMIL-02C:** 한글 Notebook `RMIL-02C_K4_K16_K24_Mean_Train300_T4x2_KO.ipynb` (SHA-256 `627aa87ab7327bfdb6eb6be55e6d96503f02aa5f1c03e3dd85e5e8bd708c2c18`) 준비, Kaggle GPU 실행 **전**. Add Input **3개**: 완료된 RMIL-02B V3 Notebook Output 전체(16개 HDF5 샤드 포함), 기존 `rsna-knee-wide224-persistent-cache-v1` frozen Train300/Gold58 메타데이터, `rsna-knee-r3d-medicalnet-pretrained-v1` MedicalNet R34 가중치. **T4×2, Internet OFF, Run All**. GPU0 K4→K16, GPU1 K24, 모두 MedicalNet-deflated R34 2.5D + 메타데이터 Transformer, Train300 V4 soft/conf weighted BCE, Gold58, full fine tune, Mean pooling 및 동일 optimizer/seed 사용. 코드 셀/Worker 문법과 가변 Window HDF5 합성 검사는 PASS이나 **실제 T4 실행 검증 전**이며 성능 결과는 없음. 결과 ZIP `RMIL-02C_results_for_review.zip`에 모델이 아닌 성능·예측·로그를 담고 best.pt는 Output에 각각 보존합니다.

완료 캐시 자세한 검증: [RMIL-02B V3 완료 결과](RMIL-02B_V3_CACHE_COMPLETED_2026-10-10.md). 기존 RMIL-01 K4는 서로 다른 영상 전처리이므로 이번 K4의 비교 기준으로 사용하지 않습니다. 코드 오류 수정 내역은 별도 GitHub 기록으로 만들지 않습니다.

---

## 2026-10-10 — RMIL-02B 현재 진행 상태

**진행 단계:** 358명(Train300 + Gold58), 2,006개 Series, 66,430개 Slice를 대상으로 **공통 224×224 단일 채널 캐시**를 생성하는 단계입니다. 현재 사용할 한글 설명판 Notebook은 `RMIL-02B_V3_Native224_FOVSafe_SharedCache_CPU_KO.ipynb` (SHA-256 `3c73cda26e664eb0fbcbd71c9041c7eea658028c896878e03ffb437e30de7753`)이며, **Kaggle 최종 실행 결과는 아직 검증되지 않았습니다.**

**데이터 처리 조건:** 원본 DICOM의 물리적 Slice 순서, 130mm 기준 Crop과 영상 바깥 영역 패딩, Series 단위 정규화, K4 ⊆ K16 ⊆ K24 선택을 동일하게 적용합니다. 생성 파일은 14GB 내부 출력 한도 이내에서 HDF5 샤드로 관리합니다.

**다음 단계:** 캐시 실행 로그 및 검증용 결과 ZIP 확인 → 새로운 공통 전처리 기준의 K4·K16·K24 Mean 학습 → 동일 K에서 Mean·Attention 비교. 과거 RMIL-01의 K4 점수를 새로운 전처리의 비교 기준으로 사용하지 않습니다.

---

# RMIL-02 / RMIL-03 — Native Window Coverage, Controlled Attention Ablation

Updated **2026-10-10**. **APPROVED STUDY DESIGN; NO NEW RMIL-02/03 KAGGLE RESULTS.** `RMIL-01` is already completed and must not be rerun by default. Exact preflight Notebook: `RMIL-02A_Native_Slice_Preflight_DiskSafe_CPU.ipynb` (downloaded notebook artifact; not assumed committed in repository). **Generated notebook integrity:** nbformat+7 Python code-cell syntax checks PASS; local artifact SHA256 `1516660b1d413aa384a193122593aad21d057832c4405a64be9d9e9e973204dd`; no Kaggle runtime execution yet. Kaggle settings: Accelerator None (CPU), Internet OFF, Save & Run All, estimated ~20–90min (not measured); Save Version `RMIL-02A Native Slice Geometry CPU Preflight`. Required Inputs: Competition `RSNA Knee Abnormality Detection` `train.csv`, `train_series.csv`, `train_series/<Study>/<Series>/*.dcm`; Dataset `rsna-knee-wide224-persistent-cache-v1` `R2D_SHARED224_V1/cache_contract.json`, `cache_index_sha256.csv`, `frozen_manifests/`, `allseries4/`. Generated output `RMIL-02A_results_for_review.zip`.

## Scientific questions (isolate effects)

- **H1 window information / count:** Under fixed MedicalNet-deflated R34 2.5D, Train300 V4, Gold58 development split, loss/optimizer/seed/epochs/224px/130mm/metadata Transformer, compare MEAN at **K4 → K16 → K24 → K32**, holding selection policy fixed (deterministic, label-blind, same per-Series definition and no per-target priors). K4 original control and K4 rebuilt control first.
- **H2 window attention:** At the **same actual K and same cached pixels, UID, Series, order, effective-window masks**, GPU0 MEAN vs GPU1 shared scalar softmax Window Attention (zero-init). Only pooling is changed. This must be tested on an expanded K, not extrapolated from RMIL-01 K4.
- Never attribute an effect to K alone when pixel normalization, geometry sorting, cropping or sampling policy also changes. Keep separate `K4_legacy`, `K4_rebuilt` parity controls. If pixel parity fails, resolve before GPU ablation and DO NOT claim causal K effect.
- **RMIL-03 after RMIL-02:** one K/policy selected using pre-registered, conservative Gold58 development criteria; compare **shared Window ATTN → disease-specific Window ATTN → disease-specific Window+Series ATTN**, plus matched MEAN baseline. Twelve explicit target outputs, same source windows, same encoder and training budget, log extra parameters/inference cost. If shared ATTN is poor, keep it as an ablation control, not mandatory deployment architecture. Check any target/window attention alignment without cherry-picking Gold58 label-specific routing.

## 2026-10-10 — RMIL-02B0 COMPLETED; RMIL-02B New V2 cache prepared (OVERRIDES older K4 parity hard gate)

**Actual artifact audit PASS**, but **K4 image parity FAIL**: ZIP SHA256 `3f7ee4b7a12db3b0297ed3d11eebce31133d4bc87adeb08687df4ece33c06a27`, CRC PASS, all 5 declared output SHA pass. Diagnostic 9 Series across 3 Studies / 144 candidate pixel transformations, ZERO exact entire-Series matches, best mean MAE 8.476386 and byte match fraction ~0.153%. No cache pixel output, no GPU; existing RMIL-01 score unchanged. **[Detailed completed RMIL-02B0 audit](RMIL-02B0_COMPLETED_PARITY_AUDIT_2026-10-10.md).**

**Decision to avoid repeated uncertain cache-builder archaeology:** original R2D-CACHE-01 exact pixel implementation NOT available; freeze newly specified and reproducible **`RMIL-02B-NATIVE224-V2` preprocessing** for the same 358 Study original DICOM source instead. **A fresh `RMIL-02C-K4-NEW` training baseline is MANDATORY** before interpreting K16 and K24 count effect. Old RMIL-01 0.576370 is historical only; cannot substitute as K4 for new V2. Within new V2 cache compare K4 Mean, K16 Mean, K24 Mean (K32 conditional) from nested selected native Slice center windows, then at matched K compare Mean vs shared attention. RMIL-03 later.

**Prepared new CPU notebook (NOT Kaggle-executed)** `RMIL-02B_Native224_SharedCache_CPU.ipynb`, SHA256 `097c72a070114caa53603180f9813ec16c3edf15ab7dc1ff84c30a279cbc080b`, syntax/nbformat PASS, synthetic nested selector 310 source lengths PASS. Accelerator None, Internet OFF, Save & Run All, 2 existing inputs (competition + `rsna-knee-wide224-persistent-cache-v1`); 358 studies / 2006 Series / 66430 real slices. V2 preproc exact contract spelled out in notebook and [audit](RMIL-02B0_COMPLETED_PARITY_AUDIT_2026-10-10.md), **NOT claimed historical image parity**. Output `RMIL-02B_NATIVE224_V2/shards/shard_###.h5` 220MB-target SHA/atomic, manifest and metadata-only ZIP `RMIL-02B_results_for_review.zip`; keep whole Kaggle Notebook output as next model Input. Kaggle saved output all-working total 14.0GB project cap, ≥2GB physical free. Actual pixels not yet created and GPU experiments not run.

---

## 2026-10-10 — Selection policy fix BEFORE K ablations: nested additions, not independently resampled K

**Independent audit of RMIL-02A `native_k_candidates.jsonl`:** source Notebook's `uniform_spaced_valid_centers_v1` calls `np.rint(np.linspace(...,k))` separately for K4, K16, K24 and K32. Thus a K16→K24 comparison **does not purely add 8 windows**: it also changes some selected center positions. Preserve the RMIL-02A JSONL as completed **feasibility evidence only**, and do NOT blindly use those columns as the finalized GPU ablation selector.

**Pre-registered RMIL-02B selector v2 = NESTED LEGACY-ANCHORED FARTHEST-POINT:**

1. Physically sorted real Slice center candidates are integers `1..N−2` (actual neighbor triplets exist); decode/ROI parity must establish original physical order direction first.
2. Freeze **legacy K4 anchors** from historical `series_centers`, now confirmed on all 2006 Series to equal `np.rint(np.linspace(.1*(N−1), .9*(N−1), 4))`; require four unique valid indices, deterministic ascending order.
3. To add a window without moving any prior window, repeatedly choose the as-yet-unselected valid center maximizing its integer index distance to its closest already selected center, ties broken by **lowest physical index**. Continue until `min(32,N−2)` unique candidates. Compute `K4`, `K16`, `K24`, `K32` as prefixes of this **one shared ranking** (while sorting those selected indices into physical order only for image assembly). This guarantees nested `set(K4) ⊆ set(K16) ⊆ set(K24) ⊆ set(K32)`; use valid count/masks, never padding treated as real.
4. At fixed K, **MEAN vs SHARED ATTN must consume bit-identical pixels, Series and selected center sets**. K16 Mean vs K24 Mean comparison now adds evidence while holding every old center; resulting global patient information/count and optimization dynamics still change naturally and require small-Gold caveats.
5. If pixel parity reveals historical physical ordering is reversed relative to RMIL-02A, map original K4 anchors to physical positions first and update an explicit versioned policy; do not silently reverse under the same manifest SHA.

**Recommendation from actual K feasibility:** compare **K16 Mean vs K24 Mean** first, K32 conditionally. RMIL-02A recorded 1924/2006 K16 full vs 1513/2006 K24 full vs only 516/2006 K32 full. `native_k_candidates.jsonl` sizes are still valuable for planning; its independent-uniform indices are **not** adopted as the nested v2 training policy.


## 2026-10-10 — RMIL-02A ACTUAL RESULTS VERIFIED (supersedes previous 'unexecuted 02A' below)

**COMPLETED/PASS_METADATA_PREFLIGHT.** Actual user-supplied `RMIL-02A_results_for_review.zip` independently CRC+all 9 declared file SHA PASS; received ZIP SHA256 `fbabf2840be680d62c636f86af5e4bb1cc87a3c6c2619fe875d0dfca6008520f`. Kaggle CPU preflight on frozen **358 Studies/2006 Series/66430 native Slices**, **0 issues**, DICOM sample decode PASS, ~11.254min header survey. Actual K full Series: 4 **2006**, 16 **1924**, 24 **1513**, 32 **516**. Real unique windows K4 **8024**, K16 **31838**, K24 **45472**, K32 **53532**. **Recommended first mean-only K16 vs K24**, K32 conditional: 1490/2006 Series cannot fill K32. Verified legacy K4 centers exactly fit **`round(linspace(.1*(N-1),.9*(N-1),4))` for all 2006 Series** (metadata indices only; orientation/pixel parity still NOT verified).

**Disk:** 66430×224² uint8 single-channel = **3.104277GiB** pixel bytes; projected *future cache peak* **4.633149184GB decimal**, safely under project **14.0GB all-working-files cap** (runtime effective remaining **13.983781468GB**). This is a budget eligibility projection, not actual generated image-cache bytes. **No new pixel cache created; no new GPU/Gold AUROC results.** The original K4 image transform parity is a HARD GATE.

**NEXT = RMIL-02B0 (prepared, not executed),** `RMIL-02B0_K4_Pixel_Parity_Probe_CPU.ipynb`, local SHA256 `0bf941097a3bdd5db04b4093f6dfe7e853127b5704011db5cbe98251a209804c`: same two Kaggle inputs, CPU only, diagnostic sample comparison for physical order, Crop130, percentiles, normalization and quantization. Only after the actual original R2D-CACHE-01 implementation (preferable) / strict K4 parity is verified may RMIL-02B **358-Study native pixel shards** be built. RMIL-01 is completed and immutable; RMIL-03 after higher K data+shared Attention ablation. Details: [RMIL-02A completed metadata and K feasibility audit](RMIL-02A_COMPLETED_METADATA_AUDIT_2026-10-10.md).

---

## 2026-10-10 — Legacy DINO / EXP cache reuse re-evaluation (asset inventory before rebuilding)

**Corrected scope:** `Exp16B-1` / `Exp59` full-MRI caches are **DINO feature embeddings** and cannot recreate source 224px pixels. This does **NOT** mean every historical Exp/DINO 2.5D artifact was feature-only. Earlier project conversations record an **Exp61 series of selected Top24 raw 3-Slice 224px uint8 Window caches** and a separate Top8 Tail/Top32 expansion; those are possible real-pixel reuse sources. **Their current exact Kaggle dataset slug, files, SHA, and availability have NOT been independently verified through the present GitHub docs or a mounted Kaggle runtime.** Do not mark them available until inspected; do not invent mount paths.

- **Strongly reuse SS01 native DICOM inventory/manifest**, if accessible and SHA matches completed SS01 record: `ss01_full_mri_single_slice_manifest.parquet` SHA `315e6443bb2c58d29981b17f92086f35b48a2dfb8bc6ee53bc65000a69bdd1eb`; `ss01_series_summary.parquet` SHA `d88c8e5a1e2e7507de8cfe16523385d8e1bb07c88da82078bdcd0dab8f8c0409`; `ss01_inventory_summary.json` SHA `4d23f8ab468055217fa30365f2efb07470010c85ede36177174fd638e30fe1a8`. The completed historical SS01 audit checked **4,407 Studies / 24,371 Series / 819,078 train slices**, all DICOM headers readable, 0 Series with fewer than 3 slices, and used ~66min CPU/8 workers for full (not Train300-only) survey. Old inventory is metadata, **not** an image pixel cache. Recheck physical geometry and train300/Gold58 study coverage against original before trusting its ordering for new K.
- **Selected Top24/Top32 real Window caches:** candidate to reuse for exact matching triples and small ROI diagnostics **only after** parsing historical manifest mapping **Study UID + Series UID + center SOP UID/index + adjacent SOP indices + preprocessing version + uint8 pixels + original SHA**. Prior DINO normalization/resize/laterality and RMIL-01 `RAW_DICOM_CROP130MM_PCT005_995_ZSCORE_CLAMP5_224_UINT8` are not proven identical. A Study-level Top24 is **not** per-Series K16/24/32 (mean ~5.6 Series/Study); arbitrary previous Top-K cannot be treated as per-Series uniform selection, and some Series may have zero matching windows.
- **SS07 Uniform K96 lossless HDF5** does store selected single-Slice source imagery and valid masks, per historical Specialist docs, but it is **not a complete native Slice volume** nor a guaranteed center±1 triple, and its selection may be per-Study rather than per-Series. It may supply a subset of matching raw centers for a separate 2D diagnostic; it cannot automatically replace new dense per-Series 2.5D cache.
- **Recommended priority:** (A) reuse old manifests/geometry inventories and code if SHA/semantics verified; (B) selectively reuse genuine image windows **only where pixel normalization and all adjacent Slice centers exactly match RMIL**; (C) build **only missing pixels for frozen Train300+Gold58** in disk-capped, versioned native single-channel shards. Never mix differently processed pixels in one causal K ablation.
- For rough planning using historical whole-train average slice count 819078/4407≈186 per Study, **358 Studies ≈66.5k slices** or **~3.11GiB uncompressed 224px 1-channel image bytes**, before metadata/shard overhead; **not a measurement for the frozen subset**. Reconcile against actual SS01 inventory subset and 14GB conservative `/kaggle/working` cap before generation.
- **Potential fast-screening alternative:** use legacy Top24 cached pixels to test an additional *separately labeled* historic Top-K feature/selection policy or metadata coverage only; do not call this K16/24/32 **all-Series controlled** test. New RMIL-03 learned target selection should remain independent from hardcoded Gold58 post-hoc winners.

## Verified asset lineage (GitHub documents, NOT independent Kaggle mount inspection)

- Original full/native image source: competition `RSNA Knee Abnormality Detection`; files `train_series.csv`, `train_series/<StudyInstanceUID>/<SeriesInstanceUID>/<SOPInstanceUID>.dcm`, and `train.csv`. Competition root documented alternatives: `/kaggle/input/competitions/rsna-knee-abnormality-detection` or `/kaggle/input/rsna-knee-abnormality-detection`. **Check existence under these exact roots**; do not recursively scan all `/kaggle/input`. Official train.csv SHA `8ca2203c0e9d61c080c7a314c7cdb51c1b03a1d9eb4770819f7f34af53ef4e33` (older verified mount).
- K4 anchor: dataset `rsna-knee-wide224-persistent-cache-v1`, `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1`; `cache_contract.json`, `cache_index_sha256.csv`, `allseries4/<UID>.json`, `allseries4/<UID>.npy`, `frozen_manifests/train300_manifest.csv`, `gold58_manifest.csv`; index SHA `664b9b6ef3889e2d1d9694b0fd0424afa32ce8785ea99ddfdfbb53d85e87495e`. Previous Kaggle run verified 358 Studies, 2006 Series, 4 3-Slice 224px windows/Series and pixel file SHA, but **source preprocessing function is not in this GitHub repository**.
- R3D-06A full-series cache `r3d06a_all_series_d24_96_v1` (4407 studies, 24371 Series / 819078 slices source count) and R3D-12CACHE `r3d12cache_full` contain **downsampled 96px/D24** volumes, not recoverable 224px native slices. Useful metadata/UID checks only, not interchangeable input pixels.
- Exp16B-1 Full-MRI Feature Cache and Exp16B-2 hierarchical MIL were used by S00-3 localization; **DINO features/attention ranks are NOT raw image files**. S00-3 logged 520 positive Lateral Meniscus studies, 101883 full windows, 3051 Series; S00-4 found label-blind conservative plane intervals with 0.921925 mean historical Lateral Meniscus attention retention on that **training-positive subset**. These exploratory results are not clinical ground truth or proof of 12-target selection gain.
- Specialist Top-K raw window persistent cache planned/used for selected windows; do not assume it contains every Series or every native slice; no confirmed mount contract for reusing it as universal RMIL-02 source.

## Native Slice / geometry preflight — RMIL-02A

**CPU-only, Kaggle Internet OFF, Save & Run All**:
1. Assert pinned K4 cache + immutable Train300 and Gold58 manifests, no overlap; assert official competition series metadata; enumerate **only** the 2006 frozen K4 Series (not 4407-study full decode).
2. Verify StudyInstanceUID, SeriesInstanceUID and stable metadata (plane, fluid, fat) against original train_series.csv. Read DICOM **headers only** (`stop_before_pixels=True`) to survey study/Series counts, projected physical slice location and orientation, missing tags, duplicates, inconsistent stacks, effective valid center count `max(N-2,0)`. Do not use filename ordering as a surrogate for physical ordering.
3. Physical slice order should be projection of `ImagePositionPatient` onto slice normal from `ImageOrientationPatient`, with consistent orientation, tolerance and duplicate detection. Require patient/Series UID matching; missing/ambiguous geometry = BLOCKED, never quietly fallback to `InstanceNumber`.
4. For each Series compute feasible K in {4,16,24,32}, unique candidate center coverage and quantile bins. Keep **legacy K4 center indices from manifest** distinct from new sampling policies. Store selected center indices, neighbor triplets and valid_count/masks rather than duplicating 3-channel pixels. No zero padding counted as real evidence.
5. Estimate per-study/per-series disk/time before deciding to materialize; log headers elapsed seconds and extrapolation caveats. Pinned JSON+CSV+SHA+ZIP output. If raw competition images are missing or a frozen UID is absent, **fail fast**; do not fake asset availability or claim RMIL-02 cache has been generated.
6. **Preprocessing parity gate for RMIL-02B:** the legacy contract identifies `RAW_DICOM_CROP130MM_PCT005_995_ZSCORE_CLAMP5_224_UINT8`, but exact implementation/order and old `series_centers` semantics need inspection from executed original cache-builder Notebook. Without it, image equality cannot be guaranteed. Decode a stratified sample, reconstruct exact legacy 3-slice triplets at old center indices, byte-compare against original `allseries4` on every tested Window, report mismatches. A documented tolerated pixel error criterion must be frozen *before* training, not relaxed after seeing metrics. Otherwise BLOCKED.

## Intended persistent cache design (RMIL-02B, gated)

- Prefer **single-channel uint8 224×224 per physically ordered source Slice**, with UID/Series grouping and manifest center indices, not separate triple copies for each K. At GPU read time assemble real neighboring `[center-1,center,center+1]` 2.5D 3-channel inputs and validity masks. This avoids 16/24/32 redundant windows and permits all K ablations to use same pixel bytes. Save per-Series preprocessing metadata, physical coordinates, orientation, dimensions, source DICOM fingerprints; respect source competition rules when publishing/reusing.
- **Do not use raw DICOM decode in a reserved T4 session**. CPU preprocessing, artifact freeze/publish, then GPU training-only. Preserve train/val exclusion. Test users may get a separate inference cache with identical pipeline if model advances.
- Initial **proposed** count policy: deterministic per-Series evenly spaced *valid centers* with K-limited unique picks; retain K4 legacy anchors as one explicit control rather than claim even sampling matches legacy. Optionally anchored nested center sets for K16/24/32 if K4 indices have trustworthy physical rank meaning. Selection policy is labeled policy-v1 and is fixed *before* Gold58 learning curves.
- Avoid forcing K32 in Series with fewer than 32 valid centers; log `effective_k`, unique centers, fraction of short Series, plane-specific coverage and mask. No duplicate-padding to K. If train-vs-Gold geometry issues differ, report explicitly.

## 2026-10-10 — Kaggle saved Output quota safety (MANDATORY)

Kaggle official Notebooks documentation currently states a **20 GB saved-output limit** for `/kaggle/working` (including files produced by Save & Run All). Do not confuse larger `/kaggle/tmp` scratch with persistent saved output; temporary files do not survive a new run. Never rely on `shutil.disk_usage(...).free` alone: the writable filesystem may report a larger number than the saved-output quota.

**RMIL-02B hard operating policy:**

1. **Conservative project quota = 14,000,000,000 bytes (14.0 GB decimal) TOTAL across all files currently in `/kaggle/working`**, not per-shard or per-cache file, leaving 6GB nominal margin below Kaggle's documented 20GB limit. This includes CSV/JSON manifests, caches, logs, ZIPs, staging, checkpoint or residual files from other experiments. A lower runtime free-space budget overrides this cap.
2. Before any substantial write, count existing regular-file sizes under `/kaggle/working` (do not traverse `/kaggle/input`) and compute `min(14GB − saved_working_bytes, reported_free_bytes − 2GB physical reserve)`. Reject a cache projected to exceed this **effective available budget**.
3. Pre-generation estimate uses **actual counted physically sorted native slices × 224 × 224 × 1 byte**, then **30% overhead + 300MB** for metadata/shard staging and uncertainty. Treat compression as zero benefit until actual files are measured. For 3-channel 2.5D K files, include `3×224×224×sum(effective_k)` if deliberately materializing them; default **single-channel each Slice stored once**, indexed K centers.
4. Save incrementally to multiple **size-limited shards** (e.g. target 256–512MB each). Before each shard, recalculate actual working/output bytes and remaining physical free bytes, and reserve space for a .tmp write, rename and manifests. Write temporary shard, validate CRC/SHA/row counts, atomically rename; on impending quota breach fail early while preserving prior completed shards and machine-readable status.
5. **Do not create a second multi-gigabyte ZIP alongside the same cache**, do not build separate K16/K24/K32 copies, and avoid large intermediate decoded files in working. Use a metadata-only results ZIP, and persist canonical cache shards directly from Notebook Output or as a versioned Dataset with explicit manifest and SHA. If a single run cannot fit, split into independently persisted parts or change cache representation; do not silently exceed limits or assume two Dataset versions can be mounted simultaneously.
6. RMIL-02A preflight should report `disk_budget.json` (`working_output_current_bytes`, saved limit, conservative cap, physical free, `estimated_future_cache_peak_bytes`, candidate single-run eligibility). **RMIL-02A does NOT generate cache**. The **updated** prepared Notebook `RMIL-02A_Native_Slice_Preflight_DiskSafe_CPU.ipynb` SHA256 `1516660b1d413aa384a193122593aad21d057832c4405a64be9d9e9e973204dd` includes this estimator, syntax and Notebook JSON checks pass; not run on Kaggle yet.
7. Apply same budget checks to T4 training outputs/checkpoints (especially duplicated snapshots) and any recovery/output archiving phase. Storage budget checks are independent of GPU memory budgets.

Note: 14GB is **our project safety policy**, not a new official Kaggle platform quota. The official 20GB figure can change; a future run must confirm actual Kaggle limits and mount free space. If discrepancy, choose the stricter cap.

## Preliminary budget — upper bound, not measured

For 2006 Series, uncompressed 3-channel 224×224 uint8 **K32** is **9.00 GiB**; K24 **6.75 GiB**, K16 **4.50 GiB**, K4 **1.13 GiB** (assuming every Series has K valid windows; actual ≤ these). Separate K caches duplicate bytes. A one-channel 224×224 cache holding **30 slices per Series** would be approx **2.81 GiB**; true size depends on real slice counts (some >30), disk formats, compression and batch metadata. At average 35 slices per Series: approx **3.28 GiB**. CPU metadata survey must replace these estimates with measured Series and slice counts/bytes before full cache build. Source ~570 GB entire DICOM tree is **NOT** being duplicated for only Train300/Gold58.

## Efficient GPU design AFTER RMIL-02B parity passes

- **Phase 1:** K4_legacy ↔ K4_rebuilt for exact preprocessing/parity; reuse previously completed RMIL-01 results if pixels/semantics are exact; no blind K4 retraining.
- **Phase 2 (window count):** GPU0 K16 MEAN / GPU1 K32 MEAN, same initialized model and K policy, while K24 deferred pending CPU effective-K distribution and cost. Prior original K4 MEAN 0.576370 is a comparator **only if parity passes**. If no difference or VRAM/runtime limit, select K16 first. Repeat at K24 only when information/cost curve warrants.
- **Phase 3 (pooling):** GPU0 chosen K MEAN vs GPU1 same K shared ATTN, equal seed/samples/schedule, valid masks. Prefer cached encoder feature-only diagnostics **for QA**, not a replacement for full fine-tuning; single-channel pixel cache is used for full train. Isolate window attention from other changes.
- Report all 12 AUROCs, AUPRCs, Gold58 positives/negatives, best epoch, per-epoch train/val loss, runtime, peak VRAM, valid windows/Series/study distributions, trained attention weights and selection concentration diagnostics. Paired UID predictions, confidence uncertainty, no independent-validation claims.

## Historical lessons

- **Exp57 Public LB 0.918**: task-tuned DINOv2-Base, full Series/Window hierarchical MIL feature processing, attention-selected Top24 actual raw windows with end-to-end fine-tuning, and a complementary **Full-MRI Direct** branch; 3-fold means per branch / 70:30 blend. **This is an integrated, multi-variable result**; it does not isolate attention or Top24 alone.
- **SS05**: shared hierarchical MIL used as a selector with per-disease attention ranks; **SS08 pure 12-specialist Public LB 0.876**, despite optimistic pseudo-label Fixed Val target-best mean 0.9341, without Exp57 folds/direct branch. Do not interpret any one omitted component as the isolated causal factor.
- **R3D-15B target attention** Gold58 0.529881 vs R3D-15B0 0.527801 on distinct low-res 3D pipeline: no compelling standalone gain; input/architecture differ and N is small. This is not RMIL-03's 2.5D K-expanded ablation.
- **RMIL-01 K4:** MEAN 0.5763704369 > shared ATTN 0.5442963023 Gold58. Shared ATTN K4 is **not promoted**; K-expanded ATTENTION deserves controlled retest, not assumption of rescue.

## Architecture decisions locked as OPEN

C1 one 2.5D model first; C2 2D+2.5D only with repeatable complementarity; C3 add 3D only with independent complementary gain. No 3-/5-fold or Exp57 blending decision. Practical inference latency/checkpoint count matter. Gold58 is repeatedly used development validation and cannot support confident target-wise oracle routing.
