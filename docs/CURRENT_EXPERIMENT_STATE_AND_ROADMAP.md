# RSNA Knee Abnormality Detection — 현재 실험 상태 / 데이터 계보 / 다음 로드맵

최종 업데이트: **2026-09-24**

이 문서는 채팅이 바뀌어도 실험을 그대로 이어갈 수 있도록,
현재까지의 데이터 생성 방식, 모델 계보, 정확한 설정값, 결과, 해석,
현재 진행 위치, 다음 실험 순서를 한 곳에 고정해 두는 문서다.

내부 추적용 ID(Exp16B-2, B3A 등)는 보조적으로만 사용한다.
실험 기록 제목은 가능한 한 **누가 봐도 무엇을 바꿨는지 바로 이해할 수 있는 설명형 이름**을 사용한다.

---

# 1. 현재 가장 중요한 결론

현재 Public LB 최고 기록은:

- **0.907**
- 실험 내용:
  **전체 MRI에서 환자별 중요 영상 24개를 선택한 뒤,
  기존 무릎 MRI 학습 가중치를 이어받아 DINOv2-Base + 계층적 MIL을 end-to-end 재학습**
- 내부 추적 ID: **Exp16B-3A**

비교 실험:

- 동일한 Top-24를 사용하되
  일반 pretrained DINOv2-Base + 새 랜덤 MIL에서 시작한 clean-start 모델
- Public LB: **0.903**
- 내부 추적 ID: **Exp16B-3B**

이 결과로 현재 가장 중요한 인사이트는 다음과 같다.

1. 기존의 고정된 Wide9 위치 입력보다,
   **환자별로 전체 MRI에서 중요한 영상을 선택하는 방식이 실제 hidden test에서도 크게 유리했다.**
2. 동일한 Top-24를 사용한 clean-start 모델도 0.903이므로,
   성능 상승의 핵심은 **환자별 중요 영상 선택 자체**에 있다는 근거가 강하다.
3. 기존 무릎 MRI 학습 가중치를 이어받은 warm-start 모델이
   clean-start보다 Public LB에서 **+0.004** 높아,
   초기화도 추가적인 이득을 준다.
4. Fold2 Gold validation은 11명뿐이므로,
   작은 CV 차이를 과신하지 않는다.
   실제 Public LB와 함께 해석해야 한다.

---

# 2. 절대 바꾸지 말아야 할 기본 데이터 / 전처리 계약

## 전체 train 규모

- Study: **4,407**
- MRI Series: **24,371**
- 전체 3-slice window 중심 후보: **819,078**

## DICOM 정렬

우선순위:

1. `ImageOrientationPatient` + `ImagePositionPatient`
2. 위 값으로 physical slice position 계산
3. 불가능하면 `InstanceNumber`
4. 마지막 fallback은 filename natural sort

## 픽셀 전처리

각 DICOM:

- `RescaleSlope`
- `RescaleIntercept`
- `MONOCHROME1`이면 intensity invert
- **130 mm physical center crop**
- **224 × 224 resize**

Series 전체:

- 전체 Series 기준 **1–99 percentile normalization**
- 결과는 **uint8**

## Laterality 정규화

판단 우선순위:

1. `ImageLaterality`
2. `Laterality`
3. DICOM geometric center fallback

오른쪽 무릎:

- Coronal / Axial: horizontal flip
- Sagittal: slice order reverse
- Sagittal reverse 시 metadata row order도 함께 reverse

## 3-slice window

각 center slice마다:

`[previous, center, next]`

를 3채널 입력처럼 구성한다.

경계에서는 nearest valid index를 사용한다.

---

# 3. Supervision 계약

현재 주력 supervision은 **V4 pseudo labels**이다.

Fold2 기준:

- Train total: **4,396**
- Gold: **47**
- Pseudo: **4,349**
- Validation Gold: **11**
- Validation Fold: **2**
- pseudo weight: **0.70 × confidence**

Master Label v2는 이미지 모델 실험에서 성능이 떨어졌으므로
현재 주력 supervision으로 사용하지 않는다.

---

# 4. 모델 계보

## 4.1 기존 강한 고정 위치 이미지 모델

설명형 이름:

**고정된 6개 MRI 구역에서 각 9개 슬라이스를 보는 DINOv2-Base 모델**

내부 ID: **Exp11B**

입력:

- 6 MRI slots
- Sagittal / Coronal / Axial
- fluid-sensitive / non-fluid-sensitive
- slot당 Wide9
- 기존 54 slice 구성

Backbone:

- DINOv2-Base
- hidden 768
- 12 blocks

학습:

- physical batch = **4**
- grad accumulation = **1**
- effective batch = **4**

Fold2:

- Macro AUC: **0.9427579365**
- Weak-6 AUC: **0.9053571429**

Public LB:

- **0.872**

Checkpoint:

`rsna_knee_exp11b_dinov2_base_head768_fold2_fold2_best.bin`

이 checkpoint의 backbone이 이후 전체 MRI feature 생성의 출발점이 되었다.

---

# 5. 전체 MRI feature 생성 — 1세대

설명형 이름:

**전체 MRI의 모든 Series와 모든 slice를 기존 무릎 MRI DINOv2-Base로 특징 추출**

내부 ID: **Exp16B-1**

전체 train:

- 4,407 studies
- 24,371 series
- 819,078 windows

Feature extractor:

- Exp11B에서 task-tuned 된 DINOv2-Base backbone
- 각 window feature:
  - CLS token
  - patch mean
  - concat
- feature dim = **1536**

저장:

- feature dtype = **float16**
- 이후 MIL 학습 시 float32로 로드

relative position:

- float16 저장

실행 결과:

- 전체 처리 완료
- decode error = **0**
- 약 **223.23분**

중요:

- 전체 Series 기준 1–99 percentile normalization을 사용한다.
- 원래 Wide9 모델의 선택된 9장 기준 normalization과는 다르다.
- 이후 full-MRI 계열 실험은 이 B1 전처리 계약을 따라야 한다.

---

# 6. 전체 MRI 특징을 계층적으로 통합해 직접 예측

설명형 이름:

**전체 MRI 모든 슬라이스 특징을 질환별로 계층적으로 통합해 12개 질환을 직접 예측**

내부 ID: **Exp16B-2**

입력:

- Exp16B-1 전체 feature cache

구조:

- feature projection
- plane embedding
- fluid embedding
- fat suppression embedding
- relative position MLP
- target-specific window attention
- target-specific series attention
- 12개 target classifier

즉 이 모델은 단순 selector가 아니라
**그 자체로 최종 12개 질환을 예측할 수 있는 full-MRI prediction model**이다.

Fold2 best:

- Best epoch: **10**
- Macro AUC: **0.9541666667**
- Weak-6 AUC: **0.9152777778**

Target별 AUC:

- ACL: 1.000000
- MCL: 1.000000
- Medial Meniscus: 1.000000
- Lateral Meniscus: 0.8571428571
- Medial OA: 0.9583333333
- Lateral OA: 1.000000
- PF OA: 0.8928571429
- Effusion: 1.000000
- Synovitis: 0.8666666667
- Baker's: 1.000000
- Contusion: 1.000000
- Fracture: 0.875000

Checkpoint:

`exp16b2_full_data_hierarchical_target_mil_fold2_v2_best.bin`

---

# 7. 환자별 Top-24 선택

설명형 이름:

**전체 MRI에서 질환별 중요도를 계산해 환자마다 중요한 24개 3-slice window 선택**

내부 ID: **Exp16B-2.5**

중요도 계산:

- Exp11B task-tuned DINO feature
- Exp16B-2 hierarchical MIL의
  - window attention
  - series attention
- joint attention 사용
- 12개 target 중 최대값:
  `target_aware_score = max over 12 targets(joint_attention)`

중복 억제:

- 같은 Series
- center index 차이 **3 이상**
- same-series NMS
- Top-24가 채워지지 않으면 남은 후보를 NMS 없이 fallback

전체 결과:

- 4,407 studies 모두 Top-24 생성
- 평균 선택 Series 수: **5.478103**
- median: 5
- min: 3
- max: 13
- NMS fallback total: **9**
- 평균 expanded attention coverage: **0.821140**
- median: **0.835358**
- min: **0.442223**
- max: **0.978820**
- decode errors: **0**

최종 image cache:

- shape: **[4407, 24, 3, 224, 224]**
- dtype: **uint8**
- 약 **15.92 GB**

---

# 8. 현재 최고 모델 — 기존 무릎 MRI 가중치를 이어받은 Top-24 end-to-end 모델

설명형 이름:

**환자별 중요 영상 24개 + 기존 무릎 MRI 학습 가중치를 이어받아 전체 모델 재학습**

내부 ID: **Exp16B-3A**

입력:

- Exp16B-2.5 Top-24 raw windows

초기화:

- DINOv2-Base backbone:
  **Exp11B task-tuned backbone**
- Hierarchical MIL head:
  **Exp16B-2 trained MIL**

학습:

- physical batch = **4**
- grad accumulation = **1**
- effective batch = **4**
- T4 ×2
- full layer-wise fine-tuning
- gradient checkpointing = True
- max epochs = 12
- early stopping patience = 4
- validation interval = 275 optimizer updates

Learning rate:

- MIL head: **2e-4**
- backbone late: **1e-5**
- backbone mid: **3e-6**
- backbone early: **1e-6**
- weight decay: **1e-4**
- warmup ratio: **0.05**
- min LR ratio: **0.01**

Optimizer groups:

- early: 28.358M
- mid: 28.358M
- late: 28.358M
- norm: 0.002M
- misc: 1.506M
- MIL: 0.761M

전체 trainable params:

- 약 **87.34M**

Best checkpoint:

- epoch: **4**
- step: **828 / 1099**
- validation event: **18**
- optimizer updates total: **4,125**
- Macro AUC: **0.9534722222**
- Weak-6 AUC: **0.9327380952**

Target별 AUC:

- ACL: 1.000000
- MCL: 1.000000
- Medial Meniscus: 0.964286
- Lateral Meniscus: 0.928571
- Medial OA: 0.916667
- Lateral OA: 1.000000
- PF OA: 0.928571
- Effusion: 0.928571
- Synovitis: 0.900000
- Baker's: 1.000000
- Contusion: 1.000000
- Fracture: 0.875000

Checkpoint:

`rsna_knee_exp16b3a_top24_warmstart_dinov2_base_hierarchical_mil_fold2_fold2_best.bin`

Public LB:

- **0.907**

Hidden-test inference:

```text
hidden test 전체 MRI
→ Exp11B task-tuned DINOv2로 모든 slice feature 추출
→ Exp16B-2가 환자별 중요도 계산
→ Top-24 선택
→ Exp16B-3A가 최종 12개 질환 예측
```

중요:

- B3A 자체는 full MRI에서 Top-24를 찾는 모델이 아니다.
- B3A는 이미 선택된 Top-24를 입력으로 받는다.
- hidden test에서는 Top-24가 미리 없으므로
  selector 단계가 반드시 필요하다.

---

# 9. Clean-start 비교 모델

설명형 이름:

**동일한 환자별 중요 영상 24개를 사용하되 일반 pretrained DINOv2부터 새로 학습**

내부 ID: **Exp16B-3B**

B3A와 동일:

- 같은 Top-24
- 같은 DINOv2-Base architecture
- 같은 Hierarchical MIL architecture
- 같은 Fold2 split
- 같은 V4 pseudo labels
- 같은 optimizer / LR / scheduler
- 같은 augmentation
- physical batch 4
- grad accumulation 1

차이:

- backbone:
  generic pretrained DINOv2-Base
- MIL:
  fresh random initialization
- Exp11B / Exp16B-2 학습 가중치를 초기화에 사용하지 않음

Best:

- epoch: **6**
- step: **1099 / 1099**
- validation event: **29**
- optimizer updates: **6,594**
- Macro AUC: **0.9247023810**
- Weak-6 AUC: **0.8799603175**

Public LB:

- **0.903**

해석:

- Top-24 자체의 효과가 매우 크다.
- warm-start가 추가로 +0.004 LB 이득.
- CV에서 A/B 차이는 크게 보였지만 Public LB 차이는 작다.
- Fold2 Gold 11명의 변동성을 다시 확인했다.

---

# 10. 현재 진행 중인 실험

## 상태: 진행 중

설명형 이름:

**전체 MRI 모든 슬라이스 특징을 계층적으로 통합하는 모델 자체를 hidden test 최종 예측으로 사용**

목적:

Top-24로 압축하지 않고
Exp16B-2 full-MRI model 자체가 hidden test에서 얼마나 강한지 확인.

추론:

```text
hidden test 전체 MRI
→ 모든 Series / 모든 slice
→ Exp11B task-tuned DINOv2 feature 추출
→ Exp16B-1과 동일하게 feature float16 저장 정밀도 재현
→ Exp16B-2 hierarchical MIL
→ 12개 질환 직접 예측
```

현재 Notebook:

`rsna_knee_full_mri_all_slice_feature_hierarchical_mil_fold2_public_lb_submission_v2.ipynb`

v1 오류:

- stale variable `B2_FILENAME / B2_PATH`가 남아
  `NameError` 발생
- 모델 / inference 논리 문제는 아니었음

v2 수정:

- stale variable 제거
- syntax validation 통과
- 현재 **Kaggle 전체 실행 결과 대기 중**

필요 Inputs:

1. Competition:
   `rsna-knee-abnormality-detection`
2. Kaggle Model:
   Meta Research / DINOv2 / PyTorch / Base / 1
3. Exp11B checkpoint:
   `rsna_knee_exp11b_dinov2_base_head768_fold2_fold2_best.bin`
4. Exp16B-2 checkpoint:
   `exp16b2_full_data_hierarchical_target_mil_fold2_v2_best.bin`

Runtime:

- T4 ×2
- Internet Off
- Notebook submission 방식
- 직접 submission.csv 수동 업로드 방식으로 설명하지 말 것

이 실험의 Public LB가 아직 나오지 않았다.

---

# 11. 현재 확정 로드맵

이 순서를 임의로 바꾸지 않는다.
새 결과가 나오면 근거를 기록한 뒤 변경한다.

## 1. 전체 MRI B2 직접 예측 Public LB

현재 진행 중.

목적:

- full-MRI prediction model 자체의 hidden-test 일반화 확인
- Top-24 최종 이미지 모델이 왜 좋아졌는지 분해
- 이후 ensemble 기준점 확보

---

## 2. 현재 최고 Top-24 모델 + 전체 MRI 직접 예측 모델 앙상블

조건:

- 1번 Public LB 확인 후 진행

후보:

- Exp16B-3A 예측
- Exp16B-2 직접 예측

처음에는 단순 probability blend 위주로 비교.

예시 후보:

- A 0.8 + B2 0.2
- A 0.7 + B2 0.3
- A 0.6 + B2 0.4
- 0.5 + 0.5

정확한 비율은 1번 Public LB와 prediction distribution 확인 후 결정한다.

목적:

- Top-24 raw image model과
- full-MRI feature model의 서로 다른 정보 사용 여부 확인

새 학습 비용이 거의 없으므로 우선순위가 높다.

---

## 3. 현재 최고 B3A backbone으로 전체 MRI feature 재생성

설명형 이름:

**현재 최고 Top-24 이미지 모델에서 학습된 DINOv2 backbone으로 전체 MRI 모든 슬라이스 특징을 다시 생성**

핵심 가설:

B3A는 Public LB 0.907까지 성능이 향상됐으므로
Exp11B backbone과 다른, 더 질환 판별에 적합한 feature space를 배웠을 가능성이 있다.

절대 주의:

- B3A의 MIL을 그대로 전체 100~500+ windows에 바로 적용하지 않는다.
- B3A는 학습 당시 Top-24만 입력받았다.
- 24개 attention 환경과 수백 개 full-MRI attention 환경은 다르다.

따라서 B3A에서 사용하는 것은 우선 **DINOv2 backbone**이다.

전체 data contract는 Exp16B-1과 동일하게 유지:

- 4,407 studies
- 24,371 series
- 819,078 windows
- same DICOM sort
- same 130 mm crop
- same 224 resize
- same full-series 1–99 percentile normalization
- same laterality canonicalization
- same 3-slice windows
- CLS + patch mean
- feature dim 1536
- feature 저장 dtype float16
- relative position float16

B3A backbone checkpoint source:

`rsna_knee_exp16b3a_top24_warmstart_dinov2_base_hierarchical_mil_fold2_fold2_best.bin`

checkpoint에서 backbone state만 정확히 추출해 사용한다.

---

## 4. B3A backbone feature로 새로운 full-MRI selector 재학습

설명형 이름:

**현재 최고 이미지 모델의 feature 공간에서 전체 MRI 중요 영상 선택 모델을 새로 학습**

중요:

기존 Exp16B-2 MIL weights를 그대로 붙이지 않는다.

이유:

- 기존 B2 MIL은 Exp11B feature space에서 학습됨
- B3A backbone은 end-to-end fine-tuning 후 feature distribution이 달라졌을 수 있음
- 기존 B2 MIL을 그대로 쓰면 feature-space mismatch가 생긴다

기본 실험:

- architecture는 Exp16B-2와 동일한 Hierarchical MIL
- feature input만 B3A backbone 기반 새 full-MRI feature로 교체
- MIL은 **fresh initialization**
- Fold2 split 동일
- V4 supervision 동일
- 가능한 한 B2와 동일한 optimizer/training recipe 유지
- 비교 변수는 feature source가 되도록 통제

검증:

- Fold2 Macro AUC
- Weak-6 AUC
- target별 AUC

기존 기준:

- B2 Macro: 0.954167
- B2 Weak-6: 0.915278

---

## 5. 기존 selector와 새 selector 비교

반드시 아래를 함께 본다.

### 예측 성능

- Fold2 Macro
- Fold2 Weak-6
- target별 AUC

### 선택 변화

- 기존 Top-24 vs 새 Top-24 overlap
- study별 overlap 분포
- 평균 / median overlap
- 최소 / 최대 overlap

예시 해석:

- overlap 22~24 수준:
  거의 동일한 영상을 선택
  → selector 재생성의 실익이 작을 수 있음

- overlap 10~15 수준:
  중요 영상 판단이 크게 달라짐
  → 새 feature space가 evidence selection을 바꾼다는 신호

### 추가 진단

- selected series count
- target별 attention concentration
- Top-K cumulative attention coverage
- expanded ±1 slice coverage
- NMS fallback count

---

## 6. 새 selector로 전체 4,407 study Top-24 재생성

조건:

5번에서 새 selector가 충분한 근거를 보였을 때 진행.

정책 기본값:

- target-aware score = max over 12 target joint attention
- same-Series NMS center gap >= 3
- Top-24
- 부족하면 fallback fill

새 cache는 기존 cache와 별도 이름으로 저장한다.

기존 cache를 덮어쓰지 않는다.

---

## 7. 새 Top-24로 최종 이미지 모델 재학습

목적:

2세대 patient-specific selection pipeline 완성.

개념:

```text
1세대
Exp11B backbone
→ B2 selector
→ Top-24
→ B3A
→ Public LB 0.907

2세대 후보
B3A backbone
→ 새 full-MRI selector
→ 새 Top-24
→ 새 end-to-end final model
→ Public LB ?
```

초기 비교에서는
기존 B3A와 가능한 한 동일한 학습 recipe를 유지한다.

변수:

- 새 selector가 만든 Top-24

필요 시 이후 초기화 전략을 별도 ablation 한다.

---

## 8. Top-16 / Top-24 / Top-32 비교

이 실험은 selector 개선 뒤에 한다.

이유:

현재 selector를 기준으로 K를 먼저 최적화하면
새 selector가 만들어졌을 때 다시 반복해야 할 수 있다.

순서:

1. 어떤 영상을 고를지 개선
2. 몇 장을 고를지 최적화

기본 후보:

- Top-16
- Top-24
- Top-32

나머지 조건은 최대한 동일하게 유지.

---

## 9. 최종 구조 확정 후 5-Fold 학습 + ensemble

가장 마지막에 진행.

이유:

현재 구조가 아직 변경될 가능성이 있다.
지금 5-Fold를 먼저 하면
새 selector 성공 시 전체를 다시 반복해야 한다.

중요한 leakage 원칙:

각 Fold는 반드시 Fold-specific이어야 한다.

즉 Fold f에서는:

- Fold f Gold validation을 encoder / selector / final model 학습에 사용하지 않음
- Fold별 backbone
- Fold별 full-MRI feature
- Fold별 selector
- Fold별 Top-K
- Fold별 final model

hidden test에서도
각 Fold 파이프라인이 자기 selector로 Top-K를 다시 고른 뒤 예측하고,
마지막에 Fold prediction을 평균한다.

---

# 12. 현재 로드맵 한 줄 버전

```text
[현재]
1. 전체 MRI B2 직접 예측 Public LB

[아주 저비용]
2. B3A + B2 직접예측 앙상블

[다음 핵심 실험]
3. B3A backbone으로 전체 MRI feature 재생성
4. 그 feature로 새로운 전체 MRI selector 재학습
5. 기존 selector와 새 selector 비교
   - Fold2 Macro / Weak6
   - Top-24 overlap
   - 선택 Series 수
   - attention coverage
6. 새 selector로 전체 4,407 study Top-24 재생성
7. 새 Top-24로 최종 이미지 모델 재학습

[그 다음]
8. Top-16 / Top-24 / Top-32 비교

[구조 확정 후]
9. 최종 방식 5-Fold 학습 + ensemble
```

---

# 13. 실험 기록 원칙

앞으로 README / 문서 / 커밋에는
`B3A`, `B2.5` 같은 내부 ID만 적지 않는다.

권장:

- “전체 MRI 모든 슬라이스 특징을 질환별로 통합해 직접 예측”
- “환자별 중요 영상 24개 + 기존 무릎 MRI 학습 가중치를 이어받아 재학습”
- “현재 최고 이미지 모델의 backbone으로 전체 MRI 특징을 재생성”
- “새 feature 공간에서 환자별 중요 영상 선택 모델을 재학습”

내부 ID는 괄호 보조 표기로만 사용한다.

예:

**환자별 중요 영상 24개 + 기존 무릎 MRI 가중치 이어받기 (Exp16B-3A)**

---

# 14. 실수 방지 체크리스트

새 notebook을 만들기 전에 반드시 확인한다.

1. Competition submission은 **Notebook submission**
   - `/kaggle/working/submission.csv` 생성
   - Save Version / Run All
   - Notebook output을 Competition Submission으로 제출
   - 사용자에게 “submission.csv를 직접 업로드”라고 안내하지 않는다.

2. physical batch / grad accumulation을 임의로 바꾸지 않는다.
   - B3 계열 기준: **4 / 1 / effective 4**

3. DICOM preprocessing을 임의 변경하지 않는다.

4. full-MRI B1 계열은
   **Series 전체 1–99 percentile normalization**을 사용한다.

5. right Sagittal은
   volume과 metadata order를 함께 reverse한다.

6. B3A 기반 새 full-MRI selector 실험에서
   **기존 B2 MIL을 그대로 재사용하지 않는다.**
   우선 fresh MIL로 feature-source effect를 검증한다.

7. B3A 자체를 수백 개 full-MRI window에 바로 넣어
   selector처럼 쓰지 않는다.

8. Fold2는 Gold 11명뿐이다.
   작은 AUC 차이를 확정적 결론으로 표현하지 않는다.

9. Public LB가 크게 움직이면
   CV와 LB의 관계를 함께 기록한다.

10. 기존 dataset / cache / checkpoint를 덮어쓰지 않는다.
    새 실험은 새 slug / filename을 사용한다.

---

# 15. 현재 즉시 다음 액션

현재 해야 할 일은 하나다.

**`rsna_knee_full_mri_all_slice_feature_hierarchical_mil_fold2_public_lb_submission_v2.ipynb`를 Kaggle에서 전체 실행하고 결과를 확인한다.**

성공 조건:

- Exp11B task-tuned feature extractor load PASS
- full-MRI Hierarchical prediction model load PASS
- visible test studies 전체 inference 완료
- decode error 확인
- submission shape / columns / probability range 검증
- final PASS
- 이후 Notebook submission
- Public LB 기록

그 다음은 이 문서의 로드맵 **2번 → 3번** 순서로 진행한다.
