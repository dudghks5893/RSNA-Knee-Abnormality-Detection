## 2026-10-10 — RMIL-03 2×2 통제 실험으로 A/B Notebook 교체 준비 (GPU 미실행)

**설계 변경 이유:** 과거 계정 B의 두 번째 `RMIL-03B Seed20261014` 반복은 재현성 검증에는 유용하지만, GPU4개를 한 번에 쓸 수 있는 상황에서 **새로운 RMIL-03D = Window Mean + 12질환별 Series Attention**을 탐색하는 편이 메커니즘 분리에 더 많은 정보를 줌. 기존 반복형 A/B Notebook **미실행 상태라면 새 2×2 A/B Notebook을 사용**. 이미 실행 중인 학습은 변경된 것처럼 표시하지 말고 그 결과를 별도로 보존.

| 계정/T4 | GPU0 | GPU1 | Seed |
|---|---|---|---|
| A | RMIL-03A: Window Mean / Series Mean | RMIL-03B: Target Window Attn / Series Mean | **20261013** |
| B | **RMIL-03D: Window Mean / Target Series Attn** | RMIL-03C: Target Window Attn / Target Series Attn | **20261013** |

**새 Notebook들 (독립 Kaggle GPU 실행 전; 기존 Notebook과 혼동 금지):**
- A: `RMIL-03_2x2_A_K16_Attention_T4x2_KO.ipynb`, SHA256 `4e87a2a5a4dd9c5827965b15727668ec191d04b08ce78302f99505735aae8556`
- B: `RMIL-03_2x2_B_K16_Attention_T4x2_KO.ipynb`, SHA256 `e768935cdfb8be785302f301c1a77cd5ffee07c2bd4f4b0ea6075b4d504ced0c`
- 두 Notebook 내 **동일한 Worker 소스 SHA256** `f0ec2d32c7d6170041e6de1a62ddcdde98aa721a400f98a6a989c04338502c03`, 동일 Seed/모델 초기 전체 State SHA 및 초기 Forward 동등 검사. 다른 Kaggle 세션 간 비트-동일 최종 재현은 보장하지 않지만 A/B 통제 조건 확인 후 교차 비교.
- Notebook nbformat / 모든 코드 셀 + Worker AST **PASS**, **CPU 합성 모델 테스트:** 4종(03A/03B/03D/03C) 초기 Model 전체 State 동등, Window/Series Attention Softmax 합 1, 12-logit 초기 출력 일치, 03D Series-only 및 03C 이중 Attention 기울기와 Encoder 기울기 전부 PASS. **실제 Kaggle 실험 결과 아직 미수령**.
- **Four-cell factorial:** Window 효과 03B−03A (Series Mean), 03C−03D (Series Attn); Series 효과 03D−03A (Window Mean), 03C−03B (Window Attn). 상호작용 `(03C−03D)−(03B−03A)`. 개발 검증 Gold58을 반복 사용하므로 작은 차이와 변수 선택편향 주의.
- V3 native224 K16 31,838 Windows / Train300 V4 soft-label confidence BCE / Gold58 / 2,006 Series·358명, full FT MedicalNet R34·CLS Transformer 동일. 입력 dataset 3개(캐시 / frozen manifest / pretrained) 모두 고정 경로, **/kaggle/input 전체 재귀 탐색 없음**. T4×2·Internet OFF·Save & Run All를 A/B 각 계정에서 수행. B 계정의 yhlucas 데이터셋 권한 확인. 운영상 Kaggle 계정별 GPU 용량/할당량 제약 확인.
- Save Version A `RMIL-03 2x2 A Window Effect T4x2`, B `RMIL-03 2x2 B Combined Effect T4x2`; 계정당 예상 65–140분 **미측정**. 각 계정 `RMIL-03-A_results_for_review.zip` / `RMIL-03-B_results_for_review.zip` + 실제 독립 `best.pt` 보존. **최종 계정 간 4-way 통합 지표/interaction/Bootstrap은 두 ZIP을 모두 받은 뒤 계산**.
- 기존 RMIL-03 2계정 `Seed 13/14` 반복형 버전은 **2×2 버전이 우선**이며, 두 실행 결과가 혼합되면 강력한 Pair 통제 비교로 주장하지 않음. LABEL-V6 미사용(`CANDIDATE_NOT_RELEASED`), Gold58 독립 테스트 아님.

---

## 2026-10-10 — RMIL-03 A/B 계정 동시 병렬 Notebook 준비 (GPU 실제 학습 전)

사용자가 **Kaggle 팀원 1명 추가로 두 계정(A/B), 계정당 T4×2 = 총 4GPU 동시 학습**이 가능하다고 확인함. A/B에 서로 다른 독립 Notebook 두 개 준비. **모든 기존 RMIL-01~02D 결과 동결.**

| Kaggle 계정 | 물리 GPU0 | 물리 GPU1 | Pair 내부 Seed | 독립 검증 질문 |
|---|---|---|---|---|
| **A** | `RMIL-03A-K16-MEAN`: 질환별 Head, Window Mean/Series Mean | `RMIL-03B-K16-TARGET_ATTN-seed13`: 질환별 Window Attention / Series Mean | **20261013** | Window Attention만 바꾸는 효과 |
| **B** | `RMIL-03B-K16-TARGET_ATTN-seed14`: 질환별 Window Attention / Series Mean | `RMIL-03C-K16-WINDOW_SERIES_ATTN`: 질환별 Window **+** 질환별 Series Attention | **20261014** | Window 구조 고정 후 Series Attention만 추가하는 효과 |

- A `RMIL-03_A_K16_Attention_T4x2_Parallel_KO.ipynb`, SHA-256 `91920eb52b194ab1462f06285370714395881c8c927d64c90c3c5fe3372d76c4`.
- B `RMIL-03_B_K16_Attention_T4x2_Parallel_KO.ipynb`, SHA-256 `9e4805b98fee62c5c7c81168cc6d0287e93e19e47be736854950a8af40573bb0`.
- **A와 B Notebook은 동일 Worker 코드** SHA-256 `a10ec735ee85cf64cebea90c846fd8324d07664ddf04e0f7b8757e6352e94a3d`. 동일 512-d ResNet34+공유 CLS Transformer+12질환 Head, 비교 Pair 안에서는 전체 초기 State SHA/첫 Study 출력 일치 검사. 모든 모델에 `nn.Linear(512,12)` 질환별 Window Attention과 `[12,512]` 질환별 Series Attention 매개변수를 동일하게 0으로 등록하되, 실험마다 필요한 Softmax 경로만 활성화. **A 계정 03A↔03B는 동일 Seed; B 계정 03B↔03C는 동일 Seed. 다른 Seed의 A03B↔B03C를 paired 비교하지 말 것.**
- **실행 전 검증:** Notebook nbformat / 전 코드 셀 AST / 내장 Worker AST / 공통 SHA 검사 통과, CPU 합성 실제 `StudyModel` Forward/Backward 3종(MEAN/TARGET_ATTN/TARGET_WINDOW_SERIES_ATTN), 12개 logit, 초기 3종 출력 일치, Window/Series/Encoder gradient, Attention Softmax 합 1 확인 통과. **실제 Kaggle T4 동작, 데이터셋 접근권 및 학습 완료는 미확인**.
- **입력 3개:** `yhlucas/rmil-02b-native224-v3` (고정 root `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`), `rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1`, `yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1/resnet_34.pth`. **B 계정에서 yhlucas 소유 Dataset을 실제 Add Input으로 읽을 수 있는지 필수 확인**. 비공개 개인 Dataset은 Notebook 팀원 권한과 다를 수 있음. 16 HDF5 shard/manifest/weight SHA 실제 검증.
- **공통:** V3 224px K16 (Train300 V4 soft/conf BCE, Gold58), ResNet34 Full FT, AdamW/Cosine/FP32, Epoch≤10/min5/patience3, T4×2, Internet OFF, Save & Run All. 예상 계정당 65~140분(**미측정**); 동시 가동은 Kaggle GPU 할당량/세션 정책 조건. `LABEL-V6` 후보 데이터 **사용 금지(CANDIDATE_NOT_RELEASED)**.
- **산출:** A `RMIL-03-A_results_for_review.zip`, B `RMIL-03-B_results_for_review.zip`. 4개 `best.pt`는 각 Kaggle Notebook Output에 보존하고 리뷰 ZIP에 미포함. Pair별 12질환 AUROC/AUPRC, 58×12 예측·출력 SHA/Bootstrap/Attention 진단·worker 로그, 03C에는 Series Attention Study×Target 진단 추가.
- 과거 공유한 단일 A 전용 `RMIL-03B_K16_TargetWindowAttention_vs_MatchedMean_T4x2_KO.ipynb`보다 **이번 A/B 공동 Worker 버전을 우선 사용**. 사용자에게 **둘 다 교체된 최종 A/B Notebook으로 실행**하도록 안내.

**후속:** A/B 두 ZIP 및 로그를 함께 받아 무결성/비교 → 조건부 해상도/Full-data 실험. Gold58 반복 개발 검증으로 일반화/임상 위치 입증 아님.

---

## 2026-10-10 — RMIL-03B 질환별 Window Attention Notebook 준비 완료 (GPU 미실행)

**파일:** `RMIL-03B_K16_TargetWindowAttention_vs_MatchedMean_T4x2_KO.ipynb`; SHA-256 `29e4a6b0cebb31ae957d9dcb01718a6503aeaf51478401ed9424b1249a315f60`. **Notebook/Worker 문법, CPU 합성 12질환 Forward·초기 Mean 동등·Encoder/Attention 역전파 테스트 통과. Kaggle GPU 학습 결과는 아직 없음.**

**단계:** RMIL-02D 완료 후 **RMIL-03B (질환별 Window Attention)**를 먼저 검증; **RMIL-03C (질환별 Series Attention)**는 다른 변수를 바꾸지 않는 별도 후속 실험으로 분리. GPU0=`RMIL-03A-K16-MEAN` **신규 matched Mean**, GPU1=`RMIL-03B-K16-TARGET_ATTN` **12개 질환별 Window Attention**. 양쪽에 **동일한 질환별 Target Projection/12개 Head**, **동일한 공유 Series CLS Transformer**, **동일한 균등 Series 집계**, 초기 Attention Linear(512→12) 가중치 전부 0, 전체 모델 초기 State SHA 및 첫 환자 초기 Logit 동등 검사. Attention의 12개 출력은 Window 축에서 별도 softmax되며 모든 질환의 Backbone은 하나로 공유. **과거 RMIL-02C/02D K16 Mean 0.577856은 아키텍처·Head 구성이 달라 1차 통제군으로 사용하지 않음.**

**입력/학습 고정:** 358명(Train300 V4/Gold58), 2006 Series, 66430 원본 Slice, `RMIL-02B-NATIVE224-V3` **공통 224px 캐시**, K16 총 31838 인접 3-Slice Window, MedicalNet-deflated R34 전체 FT, Seed20261013, AdamW cosine LR backbone1e-5/head5e-5, WD1e-4, Epoch≤10,min5,patience3, 4 Window microbatch/4 Study accumulation, T4×2, Internet OFF, Save & Run All. 입력 3개 Kaggle datasets는 RMIL-02D와 동일. Save Version: `RMIL-03B K16 TargetAttn vs Mean T4x2`. 실행 예상 약 65~140분 **미실측**.

**Output:** `RMIL-03A-K16-MEAN/best.pt`, `RMIL-03B-K16-TARGET_ATTN/best.pt`는 Notebook Output에 유지. 검토용 `RMIL-03B_results_for_review.zip`에는 각 Epoch AUROC/AUPRC/예측·12타깃별 메트릭·Target별 집중도·1000회 쌍체 Gold58 Bootstrap CI·콘솔 로그/설정/SHA만 저장. HDF5 16 Shard 실제 SHA, GPU 할당, 모든 질환·Gold 58명, Attention 합계1, 초기 공통 SHA/첫 예측 동등, ZIP CRC를 실제 실행에서 검증. Gold58은 **반복된 개발 검증**, 독립 일반화·Public LB 지표가 아님.

**다음:** Kaggle 실행 후 결과 ZIP·로그 수령 → 독립 검증 → RMIL-03C 진행 여부 판단. LABEL-V6는 현재 사용하지 않으며 `CANDIDATE_NOT_RELEASED` 유지. 원본 해상도 320/384/Native 실험은 Attention 효과와 분리해서 추후 비교.

---

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

## 2026-10-10 — RMIL-02C 완료: K4·K16·K24 Mean 통제 비교

**완료 상태:** T4×2에서 K4·K16·K24 3개 Mean 모델 모두 정상 학습·Gold58 평가·ZIP 산출 완료. 수령 ZIP 70개 항목 CRC 및 60개 산출물 SHA-256 **독립 검증 통과**. 캐시 `rmil-02b-native224-v3`의 HDF5 **16개 실제 SHA-256 Kaggle 재검사 PASS**. 358명(Train300/Gold58), 2,006 Series, 66,430 Slice, seed20261013, MedicalNet-deflated R34 2.5D+Transformer, 동일 학습 설정. 이전 RMIL-01 K4 값은 픽셀 전처리가 달라 직접 비교하지 않음.

| 지표 | K4 | K16 | K24 |
|---|---:|---:|---:|
| Gold58 Macro AUROC | 0.574420 | **0.577856** | 0.577402 |
| Gold58 Macro AUPRC(최적 AUROC Epoch에서) | 0.428417 | **0.432300** | 0.425870 |
| 최고 AUROC Epoch / 전체 Epoch | 4/7 | 5/8 | 3/6 |
| 학습 시간(분) | 20.92 | 54.53 | 55.51 |

K16은 K4보다 AUROC +0.003437, K24보다 +0.000454; K16/24 Window 증가로 큰 전체 성능 개선은 관찰되지 않음. 질환별 최고 AUROC는 K4·K16·K24 각각 4/12개. K16 Effusion +0.052, K24 Medial OA +0.093(모두 K4 대비); Lateral Meniscus와 Fracture는 큰 K에서 약화. **AUPRC의 단독 최고 Epoch는 AUROC 최적 Epoch와 다르므로 지표별 서로 다른 Epoch 점수를 결합하지 않음**. Gold58 반복 소규모 개발 검증으로 유의성·일반화 증명 불가.

**다음:** RMIL-02D는 우선 **K16 Mean vs K16 Shared Window Attention**으로 같은 V3 공통 캐시/윈도우/모델 계약에서 pooling 효과를 격리. K24의 질환별 이점은 탐색적으로 보존하되 전면 채택하지 않음. 실제 GPU 실행 전 Notebook 필요. [질환별 AUROC/AUPRC·Epoch·자원·무결성 전체 결과](RMIL-02C_K4_K16_K24_MEAN_COMPLETED_2026-10-10.md).

---

**RMIL-02C 캐시 입력 경로 확정 (2026-10-10):** 사용자가 Kaggle Dataset `yhlucas/rmil-02b-native224-v3`로 등록했으며 정확한 하위 폴더는 `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`입니다. 후속 K4·K16·K24 학습은 **이 경로 하나만 사용**하고 그 안의 `shards/shard_000.h5`~`shard_015.h5`, `series_index.csv`, `k_selection.jsonl`, `cache_contract.json`, `shard_sha256.csv`를 실행 전에 검사합니다. 경로를 고정한 한글 Notebook은 `RMIL-02C_K4_K16_K24_Mean_T4x2_경로확정.ipynb` (SHA-256 `44c92cac63126c5b477ed0a1864c473587df14a0fc19dce56374930e68898e4d`); 코드 문법 검증 PASS, **Kaggle GPU 실행은 아직 미검증**입니다.

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

# RSNA Knee — Current Experiment State & Roadmap


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

## 2026-10-10 — MANDATORY RMIL-02 20GB output guard

**RMIL-02A CPU metadata preflight notebook revised with disk budget evaluation:** `RMIL-02A_Native_Slice_Preflight_DiskSafe_CPU.ipynb` SHA256 `1516660b1d413aa384a193122593aad21d057832c4405a64be9d9e9e973204dd`; **not executed**. `disk_budget.json` estimates cache size and checks `/kaggle/working` effective space. Kaggle documents **20GB** saved Notebook output; project caps ALL saved working files at **14.0GB decimal**, reserves free disk margin, stores one channel/native slice, targets 256–512MB atomic shards and metadata-only ZIP, rejects/splits cache when estimated or actual bytes exceed budget. Details in [RMIL-02/03 protocol](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md). RMIL-01 remains completed.

---

## 2026-10-10 — UPDATED RMIL-02/03 K-VS-ATTENTION PROTOCOL (SUPERSEDES PRIOR NEXT BELOW)

**NEXT = RMIL-02A CPU metadata/geometry/asset preflight ONLY** (prepared Notebook, not run), then **RMIL-02B** native Slice cache creation after K4 parity validation, then **RMIL-02C** K-Mean count test and same-K Mean-vs-shared-ATTN test. DICOM input mount must be confirmed; no new high-res full Slice cache already verified. Old `R2D_SHARED224_V1` contains only 4 windows/Series; existing R3D caches are D24×96, and Exp16B full-MRI feature cache does not store source pixels. Use exact competition path candidates and source asset checks, never global `/kaggle/input` recursive search. **[Full approved plan and uncertainty/QA gates](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md).**

**Two isolated hypotheses:** K effect from K4/16/24/32 with MEAN constant, and Attention effect in matched *same K* MEAN-vs-shared-ATTN (K24/32 conditional on CPU audit). Preserve K4 legacy input parity. No RMIL-01 rerun. RMIL-03 separate target-window then target-window+Series comparison at chosen K; no unseen results claimed. All C1/C2/C3, fold/blend decisions remain pending; best Public LB Exp57 0.918. Older stale NEXT text below is archived.

---

## 2026-10-10 — CURRENT ACTIVE WORK: RMIL-02 CPU coverage preflight (overrides old RMIL-01 NEXT below)

**RMIL-01 COMPLETED / AUDITED:** [actual received ZIP/target metrics audit](RMIL-01_COMPLETED_AUDIT_2026-10-10.md). GPU0 MEAN Gold58 AUROC **0.5763704369**, AUPRC **0.4507296488**, best E4; GPU1 shared 4-window ATTN AUROC **0.5442963023**, AUPRC **0.4158921311**, best E3. Differences **−0.0320741346 AUROC**, **−0.0348375177 AUPRC** (ATTN minus MEAN); 4/12 target AUROC improvements, 8/12 declines. Both workers PASS; review ZIP 43 entries, all 38 declared artifact hashes PASS, source ZIP SHA recorded. Checkpoint bytes/Gold58 label manifest absent from ZIP; this is non-independent Gold development validation only. **MEAN retained as comparator**, shared ATTN not promoted.

**NEXT, UNEXECUTED RMIL-02:** CPU-only actual-Slice 16/24/32 windows-per-Series candidate cache design/preflight, geometry sorting, adjacency, deduplication, window coverage, SHA and persistent storage/runtime budget. Separate window count from selection policy, preserve Train300/Gold58 split and controlled MEAN model optimization for subsequent GPU ablation. Do not launch GPU for raw DICOM decoding; do not falsely claim dataset prepared.

**Unchanged:** RMIL-03 target-specific Window/Series MIL later; RMIL-04 full4349 after pilots; optional RMIL-05 2D and RMIL-06 3D only with repeatable added value. C1/C2/C3 all undecided. No 3/5-Fold or Exp57 automatic blend. Best verified project Public LB Exp57 **0.918**, unchanged. Old 'RMIL-01 immediate next' below superseded.

---

## 2026-10-10 — CURRENT ACTIVE WORK: RMIL-01 Window Pooling (supersedes all older future tasks below)

**Immediate next:** `RMIL-01`, controlled **2.5D R34 MEAN vs learned Window Attention**, Train300/Gold58, frozen shared 224×224 cache, T4×2, Internet OFF. Notebook prepared, **no Kaggle results yet**. Existing `EXP-01` name already occupied. GPU0=MEAN / GPU1=ATTN. Zero-init attention = initial Mean; only pooled feature selection changes. Read [RMIL experiment contract & architecture candidates](RMIL_FINAL_ARCHITECTURE_AND_EXPERIMENT_PLAN.md) FIRST.

**New active research order:** RMIL-01 pooling → RMIL-02 high-coverage actual Slice cache → RMIL-03 target-specific Window+Series Attention → RMIL-04 full4349 single expert and standalone LB → RMIL-05 optional 2D complementary expert → RMIL-06 optional 3D complementary expert.

**Three UNDECIDED final configurations:** C1 **one 2.5D target-aware MIL CNN**, C2 **2D+2.5D**, C3 **2D+2.5D+3D** (3D contingent on independent gain). **No committed 3/5-Fold or Exp57 ensemble**, since >10 models could be inefficient. Exp57 **Public LB 0.918** preserved as benchmark, not mandatory part of final. V6 label candidate not canonical until audited.

**Recently completed and now logged:** R2D-SHARED 4, RDINO-01 4, R3D-15 3 (11 actual results); see [full 11 ZIP SHA audit and metrics](R2D_RDINO_R3D15_COMPLETED_AUDIT_2026-10-10.md). Most favorable Train300/Gold58 score R2D-SHARED-A-25D AUROC **0.57637044**, not comparable to Exp57 Public LB 0.918. R3D-14V4 standalone user-reported Public LB **0.689** also completed; earlier below-text describing R3D-12/R3D-14 as 'NEXT' is historical and superseded.

---

최종 업데이트: **2026-10-10**

이 문서는 **현재 상태와 다음 작업만 기록하는 기준 문서**다.
오래된 계획/상태를 아래에 누적하지 않는다.

- 완료된 실험의 상세 기록: [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md)
- 앞으로의 R3D 실행 계획: [3D_RESNET_EXPERIMENT_PLAN.md](3D_RESNET_EXPERIMENT_PLAN.md)
- Kaggle Notebook 작성/복구 규칙: [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
- 새 채팅 인수인계: [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md)

이 문서와 위 3개 문서가 과거 README / Specialist 문서의 오래된 "현재 다음" 문구보다 우선한다.

## 2026-10-08 — 병렬 작업 결정: 기존 V4로 R3D 선행 학습

**현재 Kaggle/R3D lane의 다음 작업은 V6를 기다리는 것이 아니라 V4 baseline을 먼저 완성하는 것이다.**
새 LABEL-V6 라벨링은 별도 GPT-6 채팅에서 병렬 진행하며, 이 결정은 기존 frozen Main 구조나 R3D-12CACHE 완료 상태를 바꾸지 않는다.

1. **R3D-12V4DATA:** 기존 V4 Routed Broad / official Gold58 / R3D-12CACHE full-volume Kaggle Input 검증 및 label-distribution/loss/runtime preflight (CPU 우선, GPU smoke/profile만 별도).
2. **R3D-13V4:** MedicalNet R34 pretrained에서 단일 Main을 새로 학습. Train=V4 report-only4349 (soft target + confidence), validation=Gold58 (학습 제외).
3. **R3D-14V4:** standalone hidden-test Kaggle LB 제출. Exp57 Public LB 0.918과 비교.
4. **LABEL-V6 canonical release 이후:** 같은 구조/seed/budget/검증으로 R3D-13V6를 처음부터 학습 → R3D-14V6 standalone → V4/V6 target별/전체 비교.
5. 별도의 합의 근거가 생긴 경우에만 Exp57 blend, 선택적 3/5fold 확장. 과거 pseudo-only specialist/구 구조 탐색 반복 금지.

**경계조건:** R3D-12CACHE raw volume 생성+로컬 audit PASS이나 10.04GiB 전체 Kaggle Dataset 등록과 정확한 mount root는 아직 독립 확인되지 않았다. V4 broad all 52,188 target soft scores non-null, strict 39,792 non-null. V4 routing은 과거 Gold57을 사용했으므로 Gold58 validation은 독립 test가 아니다. V4와 V6의 first-run은 가능한 한 라벨 이외 요인을 고정해야 공정하게 비교할 수 있다.

상세 실행·비교 계약: [R3D_V4_V6_CONTROLLED_COMPARISON_PLAN.md](R3D_V4_V6_CONTROLLED_COMPARISON_PLAN.md).


---

# 1. 현재 프로젝트 기준점

## Public Leaderboard

현재 프로젝트 최고 Public LB:

- **0.918**
- **Exp57 — 3-Fold B3A + 3-Fold Full-MRI Direct 70:30 Hybrid**

Exp57은 단순 2D 모델이 아니다.

요약 구조:

~~~text
전체 MRI 모든 Series / 3-slice windows
        ↓
Fold별 task-tuned DINOv2-Base
        ↓
Fold별 Full-MRI Hierarchical MIL
        ├─ Direct probability branch
        └─ attention으로 환자별 Top-24 raw windows 선택
                    ↓
          Fold별 B3A end-to-end model

P_B3A_3F    = mean(F0, F1, F2)
P_DIRECT_3F = mean(F0, F1, F2)

P_FINAL = 0.70 × P_B3A_3F + 0.30 × P_DIRECT_3F
~~~

- Exp57 Public LB = **0.918**
- SS08 Specialist-only Public LB = **0.876**
- 따라서 R3D는 최종적으로 Exp57과 **상보적 ensemble** 가능성까지 확인해야 한다.

---

# 2. 현재 R3D 한 줄 상태

현재 Main R3D:

~~~text
ALL Series
→ 130 mm physical center crop
→ interpolated D24 × 96 × 96
→ MedicalNet R34
→ GLOB
→ metadata embedding
→ Transformer + shared CLS
→ 12 target heads
~~~

현재 고정값:

- Series policy: **ALL**
- physical FOV: **130 mm center crop**
- depth: **interpolated D24**
- in-plane: **96×96**
- Backbone: **MedicalNet R34**
- Representation: **GLOB**
- Anatomy mask: **OFF**
- Aggregator: **Transformer + shared CLS**
- Full fine-tuning
- pure FP32
- BatchNorm running stats frozen
- Backbone LR: **1e-5**
- New-layer LR: **5e-5**
- Weight Decay: **1e-4**

## R3D-11 결과 검토 — 2026-10-08

- 대상: **Medial Meniscus 단일 target**. 아래 AUROC/AUPRC는 12-target Macro 값이 아니다.
- Pipeline / paired contracts: **PASS**. 자동 adoption_status: **REVIEW_REQUIRED**.
- 검토 결론: **SAG1은 유망 후보로 보존하되 최종 specialist 채택·hard routing은 보류**. Main은 ALL 유지. 이번 결과만으로 specialist 추가 학습을 시작하지 않는다.

| Scope | ALL AUROC | SAG1 AUROC | ΔAUROC | ALL AUPRC | SAG1 AUPRC |
|---|---:|---:|---:|---:|---:|
| F0 | 0.531250 | 0.697917 | +0.166667 | 0.426910 | 0.618876 |
| F1 | 0.555556 | 0.777778 | +0.222222 | 0.649439 | 0.823719 |
| F2 | 0.659091 | 0.738636 | +0.079545 | 0.730888 | 0.770433 |
| Pooled Gold58 OOF | 0.582933 | 0.606971 | +0.024038 | 0.553281 | 0.599431 |

해석:

- 세 fold 모두 AUROC/AUPRC 개선. Pooled AUPRC Δ = **+0.046150**.
- Pooled AUROC 차이의 descriptive paired bootstrap 95% 구간: **[-0.193510, +0.238011]**. 선택된 checkpoint에 조건부이며 epoch/구조 선택 및 fold 간 의존성을 보정한 독립 검정이 아니다. 우월성 확정 불가.
- Fold마다 점수 분포가 달라 fold 내부 순위 개선이 pooled 순위 개선으로 그대로 이어지지 않는다. SAG1 F0 확률 범위 **0.44657543–0.44822356**으로 매우 좁다. ALL F1은 전원 0.5 초과. 원인 확정은 하지 않으며 calibration/학습 안정성 점검 대상이다.
- SAG1 pooled threshold 0.5 sensitivity **0.076923**, specificity **1.0**. 높은 fold AUROC만으로 임계값 성능이나 확률 품질을 보장하지 않는다. Gold58에 사후 calibration을 맞춰 개선으로 보고하지 않는다.
- Gold58은 epoch 선택과 반복 실험에 사용된 model-selection validation이다. 독립 최종 test로 부르지 않는다.

재현·검증:

- Gold58 unique UID, 양성26/음성32. 저장 OOF 예측에서 pooled AUROC/AUPRC를 재계산해 metrics.csv와 일치 확인.
- Canonical MedicalNet R34 pretrained matched fraction 1.0; Crop130 interpolated D24×96×96; FP32; BN stats frozen; MASK_OFF.
- 각 fold ALL/SAG1의 초기 모델 SHA, study sampling trace, 공통 SAG1 증강 trace 일치. 세 paired contracts PASS.
- 10 epochs × 192 study draws; fold-specific Pseudo1000 + training Gold; Gold sampling probability .25; accumulation4. 실제 unique sampled studies F0 799/F1 788/F2 788.
- 매 epoch 종료 후 validation. AUROC 우선/AUPRC tie-break. ALL best epoch F0/F1/F2 = **5/3/6**, SAG1 = **6/8/4**.
- ALL runtime 약 **32.3–32.9분/fold**, SAG1 **6.8–7.0분/fold**. 병렬 실행 조건의 관측치이며 최종 full-data 시간 추정으로 직접 쓰지 않는다.
- Historical normalized weighted BCE 유지: 단일 target의 양수 scalar weight는 분자/분모에서 상쇄된다. pseudo .35 및 confidence가 의도한 sample attenuation으로 작동한다고 해석하지 않는다. 최종 학습에서 unknown mask와 loss 정규화를 명시적으로 재설계한다.
- 여섯 best.pt는 search 산출물. 최종 모델 초기화에 재사용하지 않는다.
- 결과 원본: `A_R3D-11_results_no_pt.zip`; SHA256 `b6bd762858cc581b6f025dd9d155292f67c817f554d2f1f2479658a669af8848`.

## 확정된 최종 학습 방향

- **단일 Main R3D 모델**, 3-fold 최종 학습 아님. 기존 3-fold는 구조 비교용이었다.
- 학습 범위: **report-only 4,349 studies 전체**. 검증: **공식 Gold58 전원**, 학습에서 제외.
- 신규 라벨에서 supervision이 전혀 없는 study는 손실에 기여할 수 없다. 실제 유효 supervision 수는 audit 후 별도로 기록한다.
- Main: ALL → Crop130 → interpolated D24×96×96 → MedicalNet R34 → GLOB + metadata → Transformer/shared CLS → 12 heads.
- Search best.pt를 이어 학습하지 않고 MedicalNet pretrained에서 새로 시작한다.
- Epoch은 전체 학습 목록 순회를 기준으로 한다. 192 draws/epoch search budget을 최종 학습에 그대로 적용하지 않는다.
- Epoch 종료 시 Gold58 12-target Macro AUROC 우선, Macro AUPRC tie-break로 best.pt 선정. Epoch 수/compute budget/unknown mask 및 loss 정규화의 구체 구현은 아직 확정 전.
- Gold58은 이미 반복 탐색에 사용되었으므로 untouched test가 아니다.
- 먼저 standalone R3D Public LB 확인, 이후 Exp57(0.918)과 ensemble 상보성 검토. SAG1은 보류 후보이며 자동 추가하지 않는다.

## 바로 다음 작업

1. **Competition-aligned report label policy v2 freeze 완료**: [LABEL_RECONSTRUCTION_POLICY_V2.md](LABEL_RECONSTRUCTION_POLICY_V2.md).
2. Qwen3-8B / Mistral-Nemo-12B Kaggle GPU reader plan은 **폐기/미실행**. 현재 실행 계약: [LABEL_V6_GPT6_CHUNKED_EXECUTION.md](LABEL_V6_GPT6_CHUNKED_EXECUTION.md).
3. report-only 4,349 studies를 원본 `train.csv` 행 순서 그대로 **87 chunks**로 고정:
   - Chunk 001–086 = 50 studies / 600 decisions
   - Chunk 087 = 49 studies / 588 decisions
   - 총 52,188 decisions
   - report-only UID manifest SHA256 = `e675c1cfb8e88b3ec00af4fcba77bfb010e324e3a3473b04089da651af630a94`
   - chunk manifest SHA256 = `66179ef419094e6204ea3c39c4696d1da68463320bc9c58168e96d993e5a0cd5`
4. primary reader는 **GPT-6**. 기본 최대 5 chunks/chat으로 18개 chat에 배치하되, context 품질이 우려되면 더 일찍 끊고 최신 cumulative Master/Handoff로 새 chat에서 계속한다.
5. 각 chunk는 모든 study의 12 targets를 직접 판정하고 exact report evidence + Unicode offset + report SHA를 보존한다. 이전 completed chunk는 integrity defect가 없으면 재판정하지 않는다.
6. 4,349 완료 후 4,349 studies / 52,188 decisions 전체 contract, target별 5-state distribution / supervised coverage / positive prevalence / language·script / duplicate consistency를 감사한다.
7. HIGH-review / inference-used / contradiction / ambiguity / distribution anomaly를 **GPT-6 Astra가 원본 report + frozen policy로 독립 재판정**하고 최종 adjudication 후 canonical LABEL-V6를 freeze한다.
8. canonical release 후에만 target별 N_pos/N_neg/mask coverage로 class weight와 **masked per-target BCE → 12-target macro average** loss를 확정한다.
9. canonical label release → R3D-13 single Main full-data → standalone Public LB → 필요 시 Exp57 complementary blend. 동일 canonical manifest를 Exp57 old-vs-new label 비교에도 사용한다.

중요: 공식 Gold는 MRI image-derived consensus label이다. 새 라벨은 공식 영상 판정 기준을 최대한 모사하는 report-derived supervision이며 새로운 ground truth가 아니다.

### GPT-6 실행·다음 채팅 인수인계 보강 (2026-10-08)

- 사용자용 새 배포본: `RSNA_Knee_LABEL_V6_GPT6_Reviewed_Workbench.zip` (`LABEL_V6_GPT6_Chat01_START.zip`부터 시작).
- 기존 GPT-5.6 Sol 이름의 Chat Pack/프롬프트는 **SUPERSEDED**; 원본 chunk data와 Policy V2 SHA는 변경되지 않음.
- 입력 완전성: 원본 순서 4,349 UID / 87 chunk / 52,188 decision; Source UID index / chunk SHA 검증.
- 실제 Chunk 완료 시 누적 Master(.jsonl.gz) + 감사 JSON + Handoff JSON + 다음 단계 프롬프트를 묶은 `HANDOFF_BUNDLE.zip` 전달.
- 다음 Chat에서는 **다음 Chat Pack + 직전 Handoff Bundle** 두 ZIP을 올려 SHA와 이전 12-target per UID 범위를 검증 후 다음 chunk만 append. 조기 채팅 종료 시에는 동일 Chat Pack으로 재개.
- 단일 GPT-6 reader 결과는 candidate. 코드를 통한 구조적 PASS만으로 임상/대회 의미 정확성은 증명되지 않음. 고위험 및 샘플 감사 후 GPT-6 Astra(이용 가능 시) 검토, canonical release, 분포·class weight 확정.
- 실행 계약: [LABEL_V6_GPT6_CHUNKED_EXECUTION.md](LABEL_V6_GPT6_CHUNKED_EXECUTION.md).


---

# 3. Frozen validation / pseudo contract

## Gold58

- Official Gold: **58 studies**
- deterministic multilabel 3-Fold seed: **20261059**
- Fold sizes:
  - F0 = 20
  - F1 = 19
  - F2 = 19
- 모든 target에서 모든 Fold Positive / Negative coverage 존재
- manifest SHA256:
  `246f252a1ce4faaafa1b7d30e2c75cde6d79951cb780b0b33bf4f4dd12ad7e4b`

주의:

- Gold58은 작다.
- 수천분의 일 수준 차이는 구조적 개선으로 과장하지 않는다.
- Fold0는 많은 architecture search에 사용되어 **untouched validation이 아니다**.
- 현재는 split을 다시 만들지 않는다.

## Fold-specific Pseudo1000

Dataset:

`rsna-knee-r3d-3fold-pseudo-v1`

대표 root:

`/kaggle/input/datasets/yhlucas/rsna-knee-r3d-3fold-pseudo-v1`

Pseudo UID SHA256:

- F0: `e96b07e22aa0e4ac40281ce5709841dbadfa3cb61c882c6f1d10b8dccb4e233c`
- F1: `e3bcab2deb4e4284179fd369a72566e17083eb173750144c55f0c096dee15d98`
- F2: `d2c482ed154c141a9eb2f1ce83e5ca395c57eb30e5e3a331e319a427c333cc4d`

Sample trace SHA:

- F0: `d0c36a537f9868e6d6f484d5852f922a48d08df1ad7d35d9d241c751ed05f7a3`
- F1: `724f4b6e5e8604d8d860e42e4eb006a41419a5bb1c5e8738febf803c0624a096`
- F2: `1e4d28dfce05fb4e364599d59fdd9b691c14734889d2bd9c9d923772c40cb525`

---

# 4. Frozen R3D assets

## MedicalNet

Dataset:

`rsna-knee-r3d-medicalnet-pretrained-v1`

R34 SHA256:

`977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`

현재 R3D Main에서는 R50 / R101을 다시 비교하지 않는다.

## Full-FOV persistent cache

Dataset:

`rsna-knee-wide224-persistent-cache-v1`

실제 구조는 metadata와 volume shard가 분리되어 있다.

Metadata:

`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d06a_metadata_bundle/series_index.csv`

Volume root:

`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d06a_all_series_d24_96_v1/`

규모:

- 4,407 studies
- 24,371 series
- 819,078 slices
- 48 shards
- decode failure 0

중요:

R3D-06A raw `series_index.csv`에는
`plane_rank` / `selection_order`가 원래 저장되어 있지 않다.

기존 ALL policy와 동일하게 런타임에서 재구성한다.

~~~text
plane order:
Sagittal → Coronal → Axial

rank =
4 × Fluid_Sensitive × Fat_Suppression
+ 2 × Fluid_Sensitive
+ Fat_Suppression

tie-break:
SeriesInstanceUID ascending
~~~

그 뒤 study/plane별 `plane_rank`,
study별 `selection_order`를 생성한다.

## 현재 Crop130 cache

**R3D-11CACHE 완료/PASS**: 1,446 studies / 8,027 series / 32 float16 shards, 약 3.31 GiB. 기존 cache 통합, raw decode 0.

- 현재 mount: `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d11cache`
- volume/index: `crop130_d24_96/`; Gold와 fold pseudo: `manifests/`.
- Index SHA256: `114bc191102849cc5df8b3f45c3a2b6361446d3e190f5315e13cdf6d002d1ef4`.
- Gold58와 3fold pseudo scope coverage PASS. 최종 4,407명 전체 cache는 아니다.

**R3D-12CACHE Full4407 완료/PASS — 2026-10-08**.

- 전체 **4,407 studies / 24,371 unique series**.
- 기존 R3D-11CACHE **8,027 series 재사용** + 누락 **16,344 series 신규 생성**.
- ALL usable Series / Crop130 / interpolated D24×96×96 / float16, 총 **160 shards / 10,780,971,008 bytes (~10.04 GiB)**.
- raw decode failures **0**.
- full Study/Series metadata parity PASS.
- 기존 shard SHA equality PASS / 신규 shard readback PASS.
- 기존 Crop130 12-series raw rebuild exact parity PASS (max abs 0).
- runtime **479.195 min (~7h59m)**.
- `series_index.csv` SHA256: `e72c9238c97e0957bb7fccee91489d23847519dd1aaf01e40620411875abe217`.
- `shard_manifest.csv` SHA256: `bf4a008de5fbf9a239066524b38d0b0632891b83ff2781bde07538ff75bd44a0`.
- audit ZIP SHA256: `73d6b93d678f6922cc72b8103961fc6a7baa67cd8fe41f740709ebbf8c69e39c`.
- `study_roles.csv`: report-only train 4,349 / Gold validation 58 exact.
- 학습용 artifact는 audit ZIP이 아니라 `r3d12cache_full/` 전체 Dataset이다.
- **캐시 축은 종료. 재생성하지 않는다.**


---

# 5. Series / geometry 연구의 최종 결정

## Series policy

3-Fold mean Macro AUROC:

- P2: 0.573140
- P3: 0.589716
- **ALL: 0.596226**

결론:

- **ALL 고정**
- P4 / max-N 추가 search 없음

## Physical crop

Crop130 3-Fold confirmation:

| Fold | Full-FOV AUROC | Crop130 AUROC | ΔAUROC |
|---|---:|---:|---:|
| F0 | 0.617594 | 0.622257 | +0.004663 |
| F1 | 0.548407 | 0.542584 | -0.005823 |
| F2 | 0.622678 | 0.656090 | +0.033412 |

3-Fold mean:

- Full-FOV AUROC: **0.596226**
- Crop130 AUROC: **0.606977**
- mean ΔAUROC: **+0.010751**
- mean ΔAUPRC: **+0.003722**

결론:

- **Crop130 채택**
- fold heterogeneity는 있지만 primary AUROC 평균 개선 크기가 의미 있음

## 기각된 geometry/input

추가 탐색하지 않는다.

- Crop150
- Full-FOV 128×128
- simple D32 interpolation
- REAL32 nearest actual-slice
- REAL24 nearest actual-slice
- Full/Crop Dual-FOV feature-token fusion
- Mixed3 Full/Crop/Dual training

---

# 6. R3D-08 / 09 / 10 핵심 결과

## R3D-08C — REAL24 최종

3-Fold mean delta:

- AUROC **+0.000405**
- AUPRC **+0.000842**

자동 sign-only rule은 ADOPT였지만 실제 판정:

- **KEEP interpolated D24**
- gain이 noise 수준
- Fold1/Fold2 AUROC 하락

## R3D-09AB — Crop130 confirmation

3-Fold mean delta:

- AUROC **+0.010751**
- AUPRC **+0.003722**

판정:

- **ADOPT Crop130**
- Main input freeze

## R3D-10AB — Dual-FOV screen

Fold0 frozen:

- Full-FOV: **0.617594 / 0.540314**
- Crop130: **0.622257 / 0.508100**

Always Dual:

- AUROC **0.609809**
- AUPRC **0.494292**
- vs Crop130 ΔAUROC **-0.012448**

Mixed3:

- training modes:
  - Full-only 621
  - Crop-only 645
  - Dual 654
- best Dual AUROC **0.610704**
- best Dual AUPRC **0.483695**
- same checkpoint Full-only AUROC **0.612836**
- Crop-only AUROC **0.604505**
- probability avg AUROC **0.607573**

판정:

- **Dual-FOV / Mixed3 기각**
- Fold1/Fold2 confirmation 없음
- Main R3D = Crop130 single-view 유지

R3D-10 result ZIP SHA256:

`da5dbf79b88bbe4c9d8f1537c322cdc0b761356c70ab6d27d6df2bedee52fbe6`

---

# 7. Target-specific Series 상태

## Medial Meniscus

R3D-06H Fold0 paired binary specialist:

- P2: 0.677083 / 0.591098
- Sag1-only: **0.729167 / 0.756302**
- ΔAUROC **+0.052083**
- ΔAUPRC **+0.165204**

강한 신호다.

R3D-11 재확인은 완료했으며 위 결과가 우선한다. 과거 06H 참고:

- 06H는 현재 final Main input인 Crop130 이전 실험
- visible 06H implementation에는 canonical R34 naming과 다른 부분이 있어
  최종 specialist 근거로 그대로 쓰지 않는다
- Canonical R34 + Crop130 재확인은 R3D-11에서 완료했고 최종 채택은 보류했다.

## Synovitis

R3D-06H:

- P2: **0.680000 / 0.757973**
- Sag1-only: 0.590000 / 0.583247

결론:

- **Sag1-only hard routing 기각**
- 다시 열지 않는다

---

# 8. R3D-11 검토 완료

상세 수치와 검토는 이 문서 2절 및 EXPERIMENT_HISTORY.md 참조. 세 fold 개선이지만 최종 SAG1 채택은 보류.

# 9. 최종 실행 방향

## 확정된 최종 학습 방향

- **단일 Main R3D 모델**, 3-fold 최종 학습 아님. 기존 3-fold는 구조 비교용이었다.
- 학습 범위: **report-only 4,349 studies 전체**. 검증: **공식 Gold58 전원**, 학습에서 제외.
- 신규 라벨에서 supervision이 전혀 없는 study는 손실에 기여할 수 없다. 실제 유효 supervision 수는 audit 후 별도로 기록한다.
- Main: ALL → Crop130 → interpolated D24×96×96 → MedicalNet R34 → GLOB + metadata → Transformer/shared CLS → 12 heads.
- Search best.pt를 이어 학습하지 않고 MedicalNet pretrained에서 새로 시작한다.
- Epoch은 전체 학습 목록 순회를 기준으로 한다. 192 draws/epoch search budget을 최종 학습에 그대로 적용하지 않는다.
- Epoch 종료 시 Gold58 12-target Macro AUROC 우선, Macro AUPRC tie-break로 best.pt 선정. Epoch 수/compute budget/unknown mask 및 loss 정규화의 구체 구현은 아직 확정 전.
- Gold58은 이미 반복 탐색에 사용되었으므로 untouched test가 아니다.
- 먼저 standalone R3D Public LB 확인, 이후 Exp57(0.918)과 ensemble 상보성 검토. SAG1은 보류 후보이며 자동 추가하지 않는다.

## 바로 다음 작업

1. 원본 report 기반 라벨 감사/재구축: 공식 target 정의 확인 → 근거 문장과 상태를 보존하는 소규모 pilot → 애매한 사례 사용자 리뷰.
2. `positive / negative / uncertain / not-mentioned / insufficient`를 구분. 언급 없음·불완전 report를 자동 음성으로 만들지 않는다. LLM 자기 확신을 calibrated probability로 취급하지 않는다.
3. 기존 V4 full-data routing은 CommonGold57을 이용해 reader/target 정책을 골랐다. 이를 그대로 학습하고 Gold58을 독립 검증이라 부르지 않는다. 새 라벨 정책은 Gold 결과에 맞춰 조정하지 않는다.
4. 병행한 R3D-12CACHE 완료 audit 확인 후 새 라벨 manifest, supervision coverage와 최종 loss/budget 확정.
5. 단일 Main full-data 학습 → standalone 제출 → 필요 시 Exp57 blend 평가.

라벨 재생성 자체는 아직 시작하지 않았다. 현재 원본 report/V4 master/method/old audit 자료는 확보했으며 원래 추출 prompt·근거 문장은 제공 자료에 없다.


---

# 10. 더 이상 하지 않는 작업

근거 없이 다시 열지 않는다.

- R50 / R101
- GLOB vs coarse spatial-token 재비교
- anatomy mask current fusion
- lower backbone LR / frozen backbone
- P2 / P3 / Series cap micro-search
- Synovitis Sag1-only
- Crop 130/140/150 micro-search
- Full-FOV 128/160/192/224 resolution search
- simple D32/D40/D48 interpolation
- REAL24 / REAL32 nearest-slice
- R3D-10 Dual-FOV Fold1/2 confirmation

새 evidence가 생기기 전까지 위 항목은 closed다.

---

# 11. Kaggle 운영 핵심

- 새로운 image/cache 생성 = **CPU-only Notebook**
- GPU Notebook = **training-only**
- Save & Run All 전제
- 전체 `/kaggle/input` recursive search 금지
- exact mounted path 우선
- 같은 Dataset의 서로 다른 Version 동시 mount에 의존하지 않음
- mount 단계에서 `Output 0 B / ERRORED_MOUNTING_DATASET`이면 Python code error로 해석하지 않음
- 실패 시 재학습 전에 기존 artifact가 완성됐는지 먼저 확인
- T4×2에서 독립 Fold/variant를 GPU0/GPU1 subprocess로 병렬 실행 가능
- 한 계정에서 input을 공유할 수 있으면 굳이 Account A/B 두 세션으로 분리하지 않아도 됨

---

# 12. 문서 우선순위

새 채팅에서 판단이 충돌하면 다음 순서를 따른다.

1. **CURRENT_HANDOFF.md**
2. **CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md**
3. **3D_RESNET_EXPERIMENT_PLAN.md**
4. **EXPERIMENT_HISTORY.md**
5. AI_AGENT_KAGGLE_NOTEBOOK_RULES.md — 실행 규칙
6. README 및 과거 Specialist 문서 — historical reference

과거 문서에
"NEXT", "현재 다음", "진행 중"이 남아 있어도
이 문서의 2026-10-08 상태와 충돌하면 **과거 기록으로만 해석**한다.

