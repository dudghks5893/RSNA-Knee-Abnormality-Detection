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
- 다음 작업: **S00-3 Lateral Meniscus Training Positive MRI localization audit — Kaggle 실행**
- 이후: disease-specific candidate rule -> target-specific Top-K -> persistent cache -> S01 baseline

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
S00-3  Training Positive MRI localization audit
S00-4  Disease-specific candidate rule
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

상태: **Kaggle notebook 준비 / 실행 결과 대기**

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
