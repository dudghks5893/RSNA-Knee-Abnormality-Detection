# RSNA Knee — Specialist Model Experiment Log

최종 업데이트: **2026-09-30**

> 이 문서는 12개 질환을 하나의 shared multi-label 모델로 동시에 예측하는 기존 계보와 분리하여,
> **질환별 binary specialist (Yes / No) 모델** 계보만 기록한다.
>
> 아직 Specialist 학습 실험은 시작하지 않았다.
> 2026-09-30 기준으로 pre-experiment data audit와 Specialist 데이터/validation 설계를 먼저 확정하고 있다.

---

# 1. 현재 상태

- **Specialist 완료 학습 실험: 없음**
- **S00-1 Target distribution audit: 완료**
- **S00-2 Target별 Fixed pseudo Val manifest: 완료**
- **S00-3 Lateral Meniscus Training Positive MRI localization audit: 완료**
- 다음 작업: **S00-4 Lateral Meniscus candidate-rule audit Kaggle 실행**
- 이후: target-specific Top-K -> persistent cache -> S01 baseline

현재 전체 프로젝트 기준 최고 Public LB:

- **0.918 — Exp57: 3-Fold Top-24 B3A + 3-Fold Full-MRI Direct 70:30 Hybrid**

가장 최근 K24 / K32 재검증:

| 실험 | K | Fold2 Macro | Fold2 Weak-6 | Public LB |
|---|---:|---:|---:|---:|
| Exp62A-F2-B2Warm | 24 | 0.933333 | 0.911508 | **0.905** |
| Exp62B-F2-B2Warm | 32 | 0.932837 | 0.884127 | **0.905** |

Specialist는 이 shared 계보와 별도의 독립 실험 lineage로 관리한다.
S01이 낮더라도 기존 shared Fold2 결과를 pass/fail gate로 사용하지 않고
Specialist 내부에서 개선 방향을 추적한다.

---

# 2. Specialist 핵심 계약

## Binary target

각 Specialist는 질환 하나만 Yes / No로 예측한다.

- Positive = 해당 질환 있음
- Negative = 해당 질환 없음
- 실제 학습에는 Positive / Negative 모두 필요
- Validation도 Positive / Negative를 함께 사용해 binary discrimination을 평가

## Input selection

초기 질환 위치 분석은 training Positive MRI에서 수행할 수 있다.
그러나 최종 input-selection function은 label blind여야 한다.

따라서:

- Positive 전용 Top-K와 Negative 전용 Top-K를 따로 만들지 않음
- 질환마다 selector는 하나
- 동일 selector를 Positive / Negative / Val / Test에 사용
- Negative Top-K는 질환 관련 해부학적 위치를 보지만 실제 질환은 없는 hard negative 역할

## Gold

Official Gold 58은 모두 Train에 사용한다.

따라서 Specialist에서 별도 Gold validation을 두지 않는다.
Gold train metric은 sanity check 이상의 일반화 근거로 사용하지 않는다.

## Validation

Target별 Fixed pseudo Val 규모를 2026-09-30에 다음과 같이 사전 고정했다.

| Target | Val Total | Val Pos | Val Neg |
|---|---:|---:|---:|
| ACL | 80 | 40 | 40 |
| MCL | 80 | 40 | 40 |
| Medial Meniscus | 80 | 40 | 40 |
| Lateral Meniscus | 80 | 40 | 40 |
| Medial OA | 80 | 40 | 40 |
| Lateral OA | 80 | 40 | 40 |
| PF OA | 80 | 40 | 40 |
| Effusion | 80 | 40 | 40 |
| Synovitis | 50 | 25 | 25 |
| Baker's | 80 | 40 | 40 |
| Contusion | 80 | 40 | 40 |
| Fracture | 60 | 30 | 30 |

선정 계약:

- Gold 58은 전부 Train
- pseudo V4 Strict pool 사용
- Positive / Negative 각각 confidence percentile 50% 이상 90% 미만을 기본 candidate band로 사용
- 최상위 confidence 10%는 가능한 한 Train에 보존
- candidate 부족 시 아래 confidence 구간으로만 순차 확장
- random seed = **20260930**
- Train / Val StudyInstanceUID 완전 분리
- target별 manifest를 한 번 만든 뒤 해당 Specialist lineage에서 고정
- target ROC-AUC = primary development metric
- BCE / prediction distribution = secondary
- pseudo validation이므로 external ground truth로 해석하지 않음

---

# 3. S00-1 — V4 Target Distribution Audit

실행일: **2026-09-30**

사용 파일:

```text
Broad : /kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_broad.csv
Strict: /kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_strict.csv
Gold  : /kaggle/input/competitions/rsna-knee-abnormality-detection/train.csv
```

Pseudo hard class 판정:

```text
Positive = soft target >= 0.5
Negative = soft target < 0.5
```

## 3.1 Broad / Strict distribution

| Target | Broad Total | Broad Pos | Broad Neg | Broad Pos % | Strict Total | Strict Pos | Strict Neg | Strict Pos % | Strict Removed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ACL | 4349 | 1194 | 3155 | 27.45 | 3975 | 827 | 3148 | 20.81 | 374 |
| MCL | 4349 | 680 | 3669 | 15.64 | 4119 | 522 | 3597 | 12.67 | 230 |
| Medial Meniscus | 4349 | 1758 | 2591 | 40.42 | 3593 | 1561 | 2032 | 43.45 | 756 |
| Lateral Meniscus | 4349 | 651 | 3698 | 14.97 | 3910 | 560 | 3350 | 14.32 | 439 |
| Medial OA | 4349 | 1611 | 2738 | 37.04 | 3992 | 1363 | 2629 | 34.14 | 357 |
| Lateral OA | 4349 | 1161 | 3188 | 26.70 | 4064 | 937 | 3127 | 23.06 | 285 |
| PF OA | 4349 | 1975 | 2374 | 45.41 | 3371 | 1794 | 1577 | 53.22 | 978 |
| Effusion | 4349 | 2616 | 1733 | 60.15 | 3808 | 2508 | 1300 | 65.86 | 541 |
| Synovitis | 4349 | 538 | 3811 | 12.37 | 629 | 515 | 114 | 81.88 | 3720 |
| Baker's | 4349 | 1074 | 3275 | 24.70 | 2310 | 1053 | 1257 | 45.58 | 2039 |
| Contusion | 4349 | 729 | 3620 | 16.76 | 4181 | 599 | 3582 | 14.33 | 168 |
| Fracture | 4349 | 299 | 4050 | 6.88 | 1840 | 246 | 1594 | 13.37 | 2509 |

결론:

- 12개 target 모두 Fixed Val 100을 만들 수 있는 기본 class count는 존재한다.
- Strict는 단순히 더 깨끗한 전체 subset이 아니라 target에 따라 class prevalence를 크게 바꿀 수 있다.
- 따라서 Specialist에서 Strict-only를 일괄 기본값으로 사용하지 않는다.
- Synovitis는 Broad 538/3811에서 Strict 515/114로 바뀌므로 특히 주의한다.
- Baker's, Fracture도 strict filtering 후 prevalence 변화가 크다.

## 3.2 Official Gold 58 distribution

| Target | Gold Total | Gold Pos | Gold Neg | Gold Pos % |
|---|---:|---:|---:|---:|
| ACL | 58 | 24 | 34 | 41.38 |
| MCL | 58 | 9 | 49 | 15.52 |
| Medial Meniscus | 58 | 26 | 32 | 44.83 |
| Lateral Meniscus | 58 | 23 | 35 | 39.66 |
| Medial OA | 58 | 15 | 43 | 25.86 |
| Lateral OA | 58 | 11 | 47 | 18.97 |
| PF OA | 58 | 21 | 37 | 36.21 |
| Effusion | 58 | 35 | 23 | 60.34 |
| Synovitis | 58 | 27 | 31 | 46.55 |
| Baker's | 58 | 12 | 46 | 20.69 |
| Contusion | 58 | 19 | 39 | 32.76 |
| Fracture | 58 | 18 | 40 | 31.03 |

Gold와 pseudo prevalence는 일부 target에서 큰 차이가 있다.
Gold 58 자체가 매우 작으므로 Gold prevalence를 전체 population의 정답 분포로 간주해 pseudo 비율을 강제 교정하지 않는다.

---

# 4. V4 Strict threshold 기록

| Target | confidence threshold |
|---|---:|
| ACL | 0.45 |
| MCL | 0.45 |
| Medial Meniscus | 0.45 |
| Lateral Meniscus | 0.45 |
| Medial OA | 0.45 |
| Lateral OA | 0.35 |
| PF OA | 0.35 |
| Effusion | 0.30 |
| Synovitis | 0.20 |
| Baker's | 0.45 |
| Contusion | 0.35 |
| Fracture | 0.35 |

기존 main-line broad pseudo loss:

```text
pseudo target weight = 0.70 x confidence
```

Specialist에서 broad weighting / strict masking / mixed policy 중 무엇을 쓸지는
pilot target baseline 설계를 마친 뒤 controlled experiment로 확인한다.

---

# 5. 현재 Specialist planned sequence

```text
S00-1  Target distribution audit                [DONE]
S00-2  Target별 Fixed pseudo Val manifest       [DONE]
S00-3  Training Positive MRI localization audit [DONE]
S00-4  Disease-specific candidate rule            [DONE]
S00-5  Disease-specific Top-K selector / manifest
S00-6  Persistent Specialist cache
S01     DINOv2-Small + Slice Transformer baseline
S02     Input selection optimization
S03     Pseudo supervision optimization
S04     Hard-negative optimization
S05     Specialist architecture optimization
S06     Training optimization
S07     Public LB validation
S08     Expand to other targets
S09     Target-level shared / specialist hybrid
```

별도 Gold validation 단계는 없다.

---

# 6. 참고 연구

## 6.1 Medical Slice Transformer

- Gustav Müller-Franzes et al., **Medical slice transformer for improved diagnosis and explainability on 3D medical images with DINOv2**, Scientific Reports, 2025
- Link: https://www.nature.com/articles/s41598-025-09041-8
- Knee MRI cohort: 1,199 patients / meniscus tear binary diagnosis
- 구조: 2D DINOv2 image encoder -> slice feature sequence -> 1-layer Slice Transformer -> binary classifier
- 입력: knee MRI 약 224 x 224 x 32
- Knee MRI AUC: MST-DINOv2 **0.85 ± 0.04** vs 3D ResNet **0.69 ± 0.05**
- 전체 MST 약 23M parameters

## 6.2 Natural-domain foundation model medical transfer

- Joana Palés Huix et al., **Are Natural Domain Foundation Models Useful for Medical Image Classification?**, WACV 2024
- Link: https://openaccess.thecvf.com/content/WACV2024/html/Huix_Are_Natural_Domain_Foundation_Models_Useful_for_Medical_Image_Classification_WACV_2024_paper.html

## 6.3 DINOv2 radiology benchmark

- Mohammed Baharoon et al., **Evaluating General Purpose Vision Foundation Models for Medical Image Analysis: An Experimental Study of DINOv2 on Radiology Benchmarks**
- Link: https://arxiv.org/abs/2312.02366

---

# 7. 향후 실험 기록 형식

```text
## Specialist Exp Sxx — 설명형 이름

### 목적
무엇을 한 변수로 검증하는지

### 데이터 / split
Train / Fixed Val / input cache

### 고정 조건
preprocessing / backbone / supervision 등

### 변경 변수
이번 실험에서 실제로 바꾼 것

### 결과
Val ROC-AUC / BCE / Public LB / runtime

### 인사이트
무엇이 확인됐고 다음 실험에 무엇을 남기는지
```

실험 ID만으로 설명하지 않고 항상 설명형 제목을 함께 사용한다.


---

# 8. S00-2 Fixed Val Notebook 실행 계약

정리일: **2026-09-30**

실행 코드는 GitHub에 저장하지 않고, Kaggle notebook Import + Run All 방식으로 진행한다.

고정 계약:

- V4 routed strict pseudo 사용
- Positive = soft target >= 0.5
- Negative = soft target < 0.5
- class별 confidence percentile 50% 이상 90% 미만을 기본 candidate band로 사용
- 최상위 confidence 10%는 가능한 Train에 보존
- candidate 부족 시 아래 confidence 구간으로만 확장
- random seed = 20260930
- Gold 58과 UID overlap 발생 시 즉시 중단
- target별 계획된 P/N 개수를 assertion으로 검증

출력 위치:

`/kaggle/working/specialist_fixed_val_v1/`

주요 출력:

- `acl_fixed_val_v1.csv` 등 target별 12개 manifest
- `specialist_fixed_val_manifest_v1.csv` — 12개 target 통합 manifest
- `specialist_fixed_val_summary_v1.csv` — 실제 P/N 수와 confidence 통계

실행 결과: **PASS**

- 12개 target 모두 계획된 Total / Positive / Negative 수와 정확히 일치
- Gold overlap = 0
- target 내부 UID duplicate = 0
- confidence top-10% Val 사용 = 0
- 모든 target이 기본 confidence percentile band 50–90%만으로 생성되어 band 하향 확장 없음
- 통합 manifest = 910 target-study rows
- 고유 StudyInstanceUID = 815
- target 간 동일 study가 일부 Val에 중복되는 것은 허용된 설계이며 최대 pairwise overlap은 5 studies

고정 artifact fingerprint:

```text
specialist_fixed_val_manifest_v1.csv
SHA256 = 4e80375e688b8419b075a97b63508bb4523512fa91bbde1b3b9003a0bde8fe4a

specialist_fixed_val_summary_v1.csv
SHA256 = a553d194a33127bdcdea1a316c982d2d9a59b40873b8af2951bef608b80906f4

specialist_fixed_val_v1.zip
SHA256 = 201f723147fffed14aa6171030c6d9a825af80ebb99125e63b710db74f8aacb5
```

이후 Specialist notebook에서 fixed validation input을 사용할 때 combined manifest SHA256을 검증해
split이 바뀌지 않았음을 확인한다.

S00-2 완료. 다음 단계는 S00-3 Training Positive MRI Localization Audit이다.


---

# 9. S00-2 실제 실행 결과

실행일: **2026-09-30**

| Target | Val | Pos | Neg | Strict Pos Remaining | Strict Neg Remaining | Pos Conf Mean | Neg Conf Mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| ACL | 80 | 40 | 40 | 787 | 3108 | 0.992398 | 0.887935 |
| MCL | 80 | 40 | 40 | 482 | 3557 | 0.810633 | 0.863654 |
| Medial Meniscus | 80 | 40 | 40 | 1521 | 1992 | 0.892479 | 0.845749 |
| Lateral Meniscus | 80 | 40 | 40 | 520 | 3310 | 0.862020 | 0.862020 |
| Medial OA | 80 | 40 | 40 | 1323 | 2589 | 0.757657 | 0.750865 |
| Lateral OA | 80 | 40 | 40 | 897 | 3087 | 0.588048 | 0.599530 |
| PF OA | 80 | 40 | 40 | 1754 | 1537 | 0.739622 | 0.692426 |
| Effusion | 80 | 40 | 40 | 2468 | 1260 | 0.494636 | 0.541696 |
| Synovitis | 50 | 25 | 25 | 490 | 89 | 0.375841 | 0.392419 |
| Baker's | 80 | 40 | 40 | 1013 | 1217 | 0.814753 | 0.839951 |
| Contusion | 80 | 40 | 40 | 559 | 3542 | 0.752350 | 0.748401 |
| Fracture | 60 | 30 | 30 | 216 | 1564 | 0.592632 | 0.662813 |

모든 target의 Val_Pos_Band_Low / Val_Neg_Band_Low = **0.50**.
따라서 예정된 기본 percentile band만 사용했고 confidence 하한을 추가로 낮출 필요가 없었다.

주의:
Synovitis는 Val 25 Negative를 제외하면 Strict Negative가 89개 남는다.
향후 Specialist Train supervision에서 Strict-only를 기본값으로 쓰지 않고
Broad confidence weighting / high-confidence Negative 보강을 별도 controlled experiment로 검토한다.


---

# 10. S00-3 Lateral Meniscus Localization Audit 실행 계약

준비일: **2026-09-30**

상태: **완료 — PASS**

Pilot target:

- **Lateral Meniscus**

Audit data:

```text
V4 Strict Positive 560
- Fixed Val Positive 40
= Training Strict Positive 520
```

Fixed Val 80명 전체는 audit에서 제외한다.

사용 lineage:

```text
Exp16B-1 original full-MRI features
        ↓
Exp16B-2 original Fold2 best hierarchical MIL
        ↓
Lateral Meniscus target-specific
window attention × series attention
        ↓
Training Positive 520-study localization audit
```

명시적 제외:

- Exp59 refreshed full-MRI features 사용 안 함
- Exp60-F2-B2Warm 사용 안 함
- 기존 12-target max attention을 Lateral Meniscus 위치로 간주하지 않음

이번 단계에서는 최종 Top-K를 확정하지 않는다.
전체 joint-attention 분포와 Top1/4/8/16/24/32 concentration,
Plane / sequence / canonical relative position,
raw Top32 / NMS Top32를 진단한 뒤 S00-4에서 candidate rule을 결정한다.

실행 코드는 repository에 저장하지 않고 Kaggle Import용 notebook artifact로만 관리한다.


---

# 11. S00-3 실제 실행 결과 — Lateral Meniscus Localization Audit

실행일: **2026-09-30**

결과: **PASS**

데이터 계약:

```text
Strict Positive 560
- Fixed Val Positive 40
= Training Positive audit 520
```

Fixed Val 80명 전체는 audit에서 제외됐다.
Gold는 localization discovery에 사용하지 않았다.

사용 lineage:

```text
Exp16B-1 original full-MRI features
        ↓
Exp16B-2 original Fold2 best hierarchical MIL
        ↓
Lateral Meniscus-specific
window attention × series attention
```

Exp59 / Exp60 refreshed branch는 사용하지 않았다.

## 11.1 실행 규모

- Positive studies = 520
- Full-MRI window rows = 101,883
- Series rows = 3,051
- Raw Top32 rows = 16,640
- NMS gap3 Top32 rows = 16,640
- Attention extraction runtime = 약 0.20분
- 각 study의 Lateral Meniscus joint-attention sum = 1.0 검증

## 11.2 Plane 분포

| Plane | Mean attention mass | Median |
|---|---:|---:|
| Axial | 0.362325 | 0.347360 |
| Coronal | 0.326014 | 0.343044 |
| Sagittal | 0.311661 | 0.305294 |

Axial이 평균 1위지만 세 Plane 차이는 작다.
Lateral Meniscus candidate rule에서 한 Plane만 사용하는 근거는 없다.

## 11.3 Sequence 분포

Training Positive 520명 전체 population 기준으로
category 존재율까지 반영해 평균 attention contribution을 계산하면:

| Sequence group | Approx. global mean attention contribution |
|---|---:|
| Axial fluid-sensitive + fat-suppressed | 0.3275 |
| Coronal fluid-sensitive + fat-suppressed | 0.2166 |
| Sagittal fluid-sensitive + fat-suppressed | 0.1812 |
| Sagittal non-fluid / non-fat-suppressed | 0.1305 |
| Coronal non-fluid / non-fat-suppressed | 0.1094 |
| Axial non-fluid / non-fat-suppressed | 0.0348 |

Fluid-sensitive + fat-suppressed series가 합계 약 72.5%로 가장 강하지만,
Sagittal/Coronal non-fluid series도 합계 약 24%를 차지하므로 제거하면 안 된다.
Axial non-fluid series만 평균 기여도가 상대적으로 작아 S00-4 pruning 후보로 둔다.

## 11.4 Relative slice position

전체 기준 상위 bin:

| Relative bin | Mean attention mass |
|---|---:|
| 0.6–0.7 | 0.174473 |
| 0.4–0.5 | 0.165871 |
| 0.5–0.6 | 0.163698 |
| 0.7–0.8 | 0.157018 |
| 0.3–0.4 | 0.104600 |

단, Plane별 peak가 다르다.

- Axial: 중심부 0.3–0.7, 특히 0.4–0.6
- Coronal: 0.4–0.9, 특히 0.5–0.8
- Sagittal: 0.6–0.9가 강하고 0.1–0.4에도 secondary cluster가 존재

전체 Plane 공통 0.2–0.9 범위는 summary 평균 기준 약 91.99%의 attention mass를 포함한다.
보다 aggressive한 plane-specific rule은 S00-4에서 실제 candidate count와 attention retention을 함께 측정해 결정한다.

## 11.5 Top-K concentration

| K | Mean cumulative raw attention mass |
|---:|---:|
| 1 | 0.051343 |
| 4 | 0.165813 |
| 8 | 0.280396 |
| 16 | 0.447494 |
| 24 | 0.566393 |
| 32 | 0.653829 |

Top32도 평균 약 65.4%이므로 이 결과만으로 K32를 확정하지 않는다.

Series attention:

- Top1 series = 31.17%
- Top2 series = 52.02%
- Top3 series = 69.09%
- study당 평균 Series 수 = 5.87

Raw Top32 selected Series 수 평균 = 5.52,
NMS gap3 Top32 = 5.83.

즉 NMS Top32는 거의 전체 Series를 다시 포함하는 수준이다.
따라서 먼저 candidate space를 줄이고, 그 뒤 target-specific NMS + Top-K를 적용하는 순서가 필요하다.

## 11.6 Raw vs NMS Top32

Raw Top32 Plane share:

- Axial 36.05%
- Coronal 34.15%
- Sagittal 29.80%

NMS gap3 Top32 Plane share:

- Sagittal 39.68%
- Coronal 34.54%
- Axial 25.78%

NMS 적용 후 Sagittal 비중이 증가하고 Axial이 감소한다.
이는 Axial high-attention window가 서로 인접한 경우가 상대적으로 많음을 시사한다.
3-slice window 중복 방지를 위해 same-series center gap >= 3은 계속 중요한 후보 규칙이다.

## 11.7 S00-4로 넘기는 결론

현재 확정 가능한 것:

- 세 Plane 모두 유지
- Positive/Negative/Test에 동일한 label-blind rule 사용
- target-specific selector 사용
- same-series overlap control 필요
- K는 아직 미확정
- candidate space pruning을 K보다 먼저 수행

S00-4에서는 다음 범주의 deterministic rule을 정량 비교한다:

1. 전체 Plane + broad relative-position filter
2. plane-specific relative-position ranges
3. plane-specific ranges + low-value sequence pruning
4. 각 규칙의 candidate-window reduction / positive attention retention / per-study minimum retention 비교

S00-4에서 최종 candidate rule을 freeze한 뒤 S00-5 Top-K로 이동한다.

Artifact fingerprint:

```text
lateral_meniscus_localization_audit_summary.json
SHA256 = fa655e94ec00bd9cbf84aac51b91bdec1b5f8e93711dec3917e373b9b5b355f8

lateral_meniscus_attention_concentration.csv
SHA256 = 221930f8943a9ef22e20d4030297977f8c33704d3f7efed46f98f715c8a7bc03

lateral_meniscus_top32_nms_gap3.parquet
SHA256 = 72dc2f88027777be2855449720a5979c37243566a7e4b0f9e33869d1ef919b40

rsna_knee_s00_3_lateral_meniscus_localization_audit_v1.zip
SHA256 = fa70ac6a710df8d123a91d306bed14089d75d324290c98a304e1dfb53b745b1b
```


---

# 12. S00-4 Lateral Meniscus Candidate Rule Audit 실행 계약

준비일: **2026-09-30**

상태: **Kaggle notebook 준비 / 실행 결과 대기**

실행 코드는 repository에 저장하지 않는다.
Kaggle Import용 notebook artifact로만 관리한다.

Input:

- S00-3 Output의 `lateral_meniscus_all_window_attention.parquet`
- S00-3 Output의 `lateral_meniscus_localization_audit_summary.json`

S00-3 source fingerprint:

```text
lateral_meniscus_all_window_attention.parquet
SHA256 = 06cd3904c8961a4b4f526f85e79a70a54fe000a311f6d6c9ebf27739652c70ef

lateral_meniscus_localization_audit_summary.json
SHA256 = fa655e94ec00bd9cbf84aac51b91bdec1b5f8e93711dec3917e373b9b5b355f8
```

비교 rules:

1. R0 — Full MRI
2. R1 — all Plane / relative 0.2–0.9
3. R2 — conservative plane-specific
   - Axial 0.2–0.8
   - Coronal 0.3–0.9
   - Sagittal 0.1–0.9
4. R3 — focused plane-specific
   - Axial 0.2–0.7
   - Coronal 0.4–0.9
   - Sagittal 0.1–0.4 또는 0.6–0.9
5. R4 — R3 + Axial non-fluid/non-fat-suppressed pruning

평가 기준:

- candidate-window reduction
- per-study attention retention
- p10 / min retention
- zero-candidate study
- Plane / sequence retention
- NMS gap3 + K8/16/24/32 simulation

S00-4에서는 자동 winner를 정하지 않는다.
실행 결과를 검토한 뒤 candidate rule 하나를 freeze하고 S00-5로 이동한다.


---

# 12. S00-4 실제 실행 결과 — Lateral Meniscus Candidate Rule Audit

실행일: **2026-09-30**

결과: **PASS**

S00-3의 Training Positive 520명 / 101,883 windows에서
5개 deterministic candidate rule을 동일 조건으로 비교했다.

## 12.1 주요 비교

| Rule | Candidate windows | Reduction | Mean retention | P10 | Min | >=0.90 | >=0.85 | >=0.80 | Zero candidate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R0 Full MRI | 101883 | 0.00% | 1.000000 | 1.000000 | 1.000000 | 520 | 520 | 520 | 0 |
| R1 all-plane rel 0.2–0.9 | 69873 | 31.42% | 0.919902 | 0.879340 | 0.770628 | 417 | 495 | 516 | 0 |
| **R2 conservative plane-specific** | **68242** | **33.02%** | **0.921925** | **0.881625** | 0.750619 | **427** | **497** | **516** | **0** |
| R3 focused plane-specific | 54393 | 46.61% | 0.867250 | 0.816231 | 0.608829 | 116 | 381 | 486 | 0 |
| R4 focused + axial non-fluid prune | 51026 | 49.92% | 0.837359 | 0.717373 | 0.520097 | 96 | 303 | 384 | 0 |

R2는 R1 대비:

- 평균 3.14 windows/study 추가 감소
- total reduction 31.42% -> 33.02%
- mean retention 0.919902 -> 0.921925
- p10 0.879340 -> 0.881625
- >=0.90 study 417 -> 427
- >=0.85 study 495 -> 497
- >=0.80 study 516 -> 516

paired study comparison에서는 R2 retention이 R1보다 높은 study 274,
낮은 study 246으로 mixed지만 평균 delta는 +0.002023이다.
R2의 absolute minimum은 0.750619로 R1보다 낮지만,
80% 이상 retention study 수는 두 rule 모두 516/520이므로
실질적인 low-retention tail 규모는 증가하지 않았다.

## 12.2 Frozen Candidate Rule v1

```text
Axial    : 0.2 <= canonical_relative_position <= 0.8
Coronal  : 0.3 <= canonical_relative_position <= 0.9
Sagittal : 0.1 <= canonical_relative_position <= 0.9
```

추가 sequence pruning 없음.

이 규칙은 metadata-only / label-blind이며
Positive / Negative / Fixed Val / Test에 동일 적용한다.

주의:
candidate rule discovery는 Positive training MRI에서 수행했지만,
runtime에는 pseudo label이나 attention value를 입력하지 않는다.

## 12.3 S00-5 참고 NMS + K simulation

R2 candidate rule + same-series center gap >=3:

| K | Mean selected windows | Full-K studies | Mean attention retention | P10 |
|---:|---:|---:|---:|---:|
| 8 | 8.000 | 520/520 | 0.220593 | 0.161124 |
| 16 | 15.990 | 517/520 | 0.291597 | 0.236510 |
| 24 | 23.640 | 468/520 | 0.320140 | 0.276411 |
| 32 | 29.796 | 338/520 | 0.332169 | 0.297908 |

NMS 이후 K가 커질수록 일부 study에서 full K를 채우지 못한다.
특히 K32는 338/520만 32개를 충족한다.

따라서 S00-5에서는
'항상 정확히 K개를 강제로 채우는가'와
'중복 없는 variable-count를 허용하는가'를 포함해 Top-K contract를 먼저 정량 검증한다.

## 12.4 Artifact fingerprint

```text
lateral_meniscus_candidate_rule_summary.csv
SHA256 = a7e8eacfe4d889a7eccd2038a0396b830d939e0a513389e6178231e47f821d01

lateral_meniscus_candidate_rule_nms_k_summary.csv
SHA256 = 0e8d653fcd05ce4447718ca6efd330e165b6c3261913ceebd7477b0950011fff

lateral_meniscus_candidate_rule_audit_summary.json
SHA256 = c7fec8968d0a694391d584a0f9c1f0ddea07f23623f7875450bd95490bf8b127

lateral_meniscus_candidate_rule_per_study.csv
SHA256 = d6e0bb4b10f476569764dd375ac80a6afa30e5404e8bd5eb044f9534c55cb4a6

rsna_knee_s00_4_lateral_meniscus_candidate_rule_audit_v1.zip
SHA256 = 674b0d10a23e7f5b2589e9095999748789822550711def4ef408fa15e9b412c3
```

S00-4 완료.
다음 단계는 S00-5 Lateral Meniscus target-specific Top-K selector audit이다.
