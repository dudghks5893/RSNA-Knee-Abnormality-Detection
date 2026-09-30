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
- 다음 작업: **S00-2 pilot target Fixed Val 100 구축**
- 이후: Positive MRI localization audit -> disease-specific candidate rule -> target-specific Top-K -> persistent cache -> S01 baseline

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

질환별 Fixed pseudo Val 100을 만든다.

- Train과 UID 완전 분리
- Positive / Negative 모두 포함
- 가능한 high-confidence sample 우선
- 한 번 고정한 100명은 해당 Specialist의 후속 실험에서 변경하지 않음
- target ROC-AUC를 primary development metric으로 사용
- 정확한 P/N 비율은 pilot target의 confidence distribution을 확인한 뒤 고정

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
S00-2  Fixed pseudo Val 100                     [NEXT]
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
