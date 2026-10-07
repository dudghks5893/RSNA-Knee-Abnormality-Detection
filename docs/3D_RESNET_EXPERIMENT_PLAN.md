# RSNA Knee — 3D ResNet Experiment Plan

최종 업데이트: **2026-10-07**

상태: **R3D-06G 완료 / R3D-06H 수정 재실행 + P3 Fold1/2 confirmation 다음**

이 문서는 신규 3D ResNet 계보의 **현재 결정 사항, 미결정 사항, 진행 순서, 현재 진척 상태**를 기록한다.

완료 결과는 [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md)에 기록한다.
Notebook 작성/전달 규칙은 [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)를 따른다.

---

# 1. 목표

기존 DINOv2 / MIL / Specialist 계보와 독립적으로,
성능 최우선의 knee MRI 12-label multi-label model을 새로 설계한다.

현재 외부 기준점:

- Exp57 Public LB: **0.918**
- SS08 Specialist-only Public LB: **0.876**

신규 계보의 최종 목표는 내부 Validation 최고점이 아니라
**Kaggle hidden-test Public LB에서 Exp57 0.918을 넘는 것**이다.

---

# 2. 확정 모델 구조

고수준 구조는 아래로 고정한다.

~~~text
Knee MRI 3D Volume
        +
Anatomical Segmentation Mask
        ↓
Pretrained 3D ResNet
(34 / 50 / 101)
Full Fine-tuning
        ↓
Transformer
(Self-Attention)
        ↓
Shared Representation
        ↓
12 Label-Specific Heads
        ↓
12 Independent Sigmoid Probabilities
~~~

핵심 원칙:

- MRI는 2D 단일 slice가 아니라 **3D spatial context**를 유지한다.
- ROI는 BBox가 아니라 **Anatomical Segmentation Mask**를 우선한다.
- 원본 MRI를 버리고 ROI만 학습하지 않는다.
- **Full MRI information + anatomical mask information**을 같이 사용한다.
- 3D ResNet은 pretrained weight를 사용하고 전체 backbone을 Full Fine-tuning한다.
- LoRA는 현재 계획에 포함하지 않는다.
- ResNet 자체에는 기본 Self-Attention이 없으므로 뒤 Transformer에서 관계를 통합한다.
- 최종 출력은 하나의 softmax가 아니라 12개 independent sigmoid다.

---

# 3. Segmentation / ROI 전략

## 3.1 확정 사항

- BBox보다 **Anatomical Segmentation Mask**를 사용한다.
- 목표는 병변 자체를 미리 정답처럼 segment하는 것이 아니라,
  무릎의 해부학 구조 위치 정보를 모델에 추가하는 것이다.
- 원본 MRI와 segmentation 정보를 함께 분류 모델에 전달한다.

예상 대상 구조:

- Bone
- Cartilage
- Meniscus
- Ligament / 주변 주요 구조

정확한 mask class 구성은 segmentation data / pretrained model을 확인한 뒤 확정한다.

## 3.2 Segmentation 평가

Primary:

- **Dice**
- **IoU**

반드시:

- 구조별 Dice / IoU
- 전체 macro Dice / IoU
- Validation image/study와 Train 완전 분리

## 3.3 아직 결정하지 않은 사항

아래는 구현 전에 반드시 확정한다.

- segmentation annotation / mask source
- segmentation model architecture
- 2D / 2.5D / 3D segmentation 방식
- anatomical class 수
- MRI + mask를 3D ResNet에 넣는 정확한 fusion 방식
  - input-channel 방식
  - feature-conditioning 방식
  - 기타 방식
- mask가 없는 study에 대한 fallback

새 채팅에서 임의로 하나를 가정하지 말고,
실제 사용 가능한 데이터와 pretrained model을 먼저 확인한 뒤 결정한다.

---

# 4. Backbone 비교

후보:

- **3D ResNet34 + Transformer**
- **3D ResNet50 + Transformer**
- **3D ResNet101 + Transformer**

세 모델 모두 Transformer를 처음부터 붙인 상태로 비교한다.

이유:
최종 목표가 ResNet + Transformer이므로,
ResNet 단독 순위와 Transformer 결합 후 순위가 다를 가능성을 제거한다.

공정한 비교에서 고정할 것:

- Gold fold split
- fold별 pseudo study pool
- segmentation pipeline
- preprocessing
- Transformer architecture
- loss definition
- evaluation code
- checkpoint rule
- random seed policy
- 최대 학습 budget / early-stopping rule

모델마다 달라도 되는 것:

- Learning Rate
- Weight Decay
- Batch Size
- 필요 시 Dropout / scheduler 관련 값

원칙:

**같은 hyperparameter를 강제하는 것이 아니라 같은 탐색 기회를 제공한다.**

---

# 5. Gold58 Validation 전략

Official Gold는 총 **58 studies**이며 12 target 모두 binary ground truth가 있다.

분포:

| Target | Positive | Negative |
|---|---:|---:|
| ACL | 24 | 34 |
| MCL | 9 | 49 |
| Medial Meniscus | 26 | 32 |
| Lateral Meniscus | 23 | 35 |
| Medial OA | 15 | 43 |
| Lateral OA | 11 | 47 |
| PF OA | 21 | 37 |
| Effusion | 35 | 23 |
| Synovitis | 27 | 31 |
| Baker's | 12 | 46 |
| Contusion | 19 | 39 |
| Fracture | 18 | 40 |

## 5.1 3-Fold OOF

Gold58을 multilabel-stratified 3-Fold로 나눈다.

예상 크기:

- Fold 0: 약 19
- Fold 1: 약 19
- Fold 2: 약 20

각 target의 Positive / Negative가 가능한 한 세 Fold에 고르게 들어가게 한다.

각 Fold:

~~~text
Train
= report-only pseudo subset 약 1,000
+ Gold training folds 약 38~39

Validation
= held-out Gold 약 19~20
~~~

세 Fold의 held-out prediction을 합쳐 Gold58 pooled OOF를 만든다.

조건:

- 각 Gold study는 자신을 학습하지 않은 모델에서 정확히 한 번만 예측
- Gold Val UID는 해당 Fold 학습 / HPO / segmentation fitting에 leakage되면 안 됨

---

# 6. 매우 중요한 Pseudo leakage 규칙

기존 V4 pseudo-label routing은 Gold 정보를 이용해 reader / route reliability를 계산한 계보가 있다.

따라서 **새 3-Fold Gold OOF에서 full-data V4 routed pseudo label을 그대로 쓰면 안 된다.**

R3D 계보에서는 다음 중 하나가 필요하다.

1. 새 3-Fold split에 맞춘 **3-Fold leakage-safe pseudo labels를 재생성**
   - Fold k의 pseudo routing / reliability는 Fold k Gold Val을 보지 않고 계산
2. 또는 Gold58과 완전히 독립적으로 생성된 pseudo supervision을 사용

기본 권장안은 1번이다.

또한 Pseudo 1,000 subset은:

- 같은 Fold 안에서는 R34 / R50 / R101이 **완전히 동일한 UID set** 사용
- Fold마다 leakage-safe pseudo labels를 기준으로 subset을 구성
- 12-label distribution을 가능한 한 유지
- confidence가 극단적으로 낮은 pseudo는 우선 제외
- subset manifest를 저장하고 SHA256을 기록

즉 비교의 핵심은:

**같은 Fold / 같은 Train studies / 같은 Val studies / backbone size만 변경**

이다.

---

# 7. 빠른 Backbone Selection 학습량

초기 전체 4,349 pseudo를 전부 사용하지 않는다.

Backbone size selection에서는 Fold별:

- pseudo 약 **1,000 studies**
- Gold Train 약 **38~39 studies**

를 사용한다.

pretrained 3D ResNet 전체를 Full Fine-tuning한다.

기본 비교 횟수:

- R34 + Transformer × 3 Fold
- R50 + Transformer × 3 Fold
- R101 + Transformer × 3 Fold

총 **9 training runs**.

각 run은 clean start이며,
checkpoint initialization / data manifest / seed / hyperparameter를 기록한다.

---

# 8. 평가 지표

## 8.1 Classification primary

모델 선택 1순위:

- **Gold58 pooled OOF Macro AUROC**

2순위:

- **Gold58 pooled OOF Macro AUPRC**

추가 보고:

- target별 AUROC
- target별 AUPRC
- Sensitivity
- Specificity
- F1-score
- Balanced Accuracy

Threshold-dependent metric은 threshold 정책을 반드시 기록한다.
임의로 threshold 0.5를 사용했다면 그 사실을 명시한다.
향후 threshold를 tuning할 경우 Gold OOF leakage가 생기지 않도록 별도 정책을 정한다.

## 8.2 Segmentation

- Dice
- IoU
- structure별 metric
- macro metric

## 8.3 안정성 진단

가능하면 함께 기록:

- Train loss
- Validation loss
- epoch별 Macro AUROC / AUPRC
- target별 prediction distribution
- Fold별 성능
- pooled OOF 성능

---

# 9. Best Checkpoint 규칙

각 Fold의 best checkpoint:

1. **Validation Macro AUROC 최대**
2. 사실상 동률이면 **Macro AUPRC가 높은 epoch**

Threshold-dependent metric은 checkpoint primary criterion으로 사용하지 않는다.

반드시 저장:

- best epoch
- best Macro AUROC
- best Macro AUPRC
- checkpoint filename
- checkpoint SHA256
- model config
- preprocessing config
- segmentation config/version
- train/val manifest SHA
- seed

---

# 10. Hyperparameter 전략

탐색 후보:

- Learning Rate
- Weight Decay
- Batch Size
- 필요 시 Dropout
- 필요 시 scheduler 관련 값

원칙:

- R34 / R50 / R101이 서로 다른 최적값을 가질 수 있다.
- 같은 값을 강제로 쓰지 않는다.
- 세 모델에 **동일한 탐색 budget**을 준다.
- Gold58이 pseudo보다 신뢰도 높은 ground truth이므로 최종 선택은 Gold OOF를 기준으로 한다.
- 그러나 Gold58을 지나치게 반복 최적화하면 validation overfit이 생기므로 탐색 횟수와 실험 이유를 기록한다.

빠른 1차 모델 크기 비교 후 차이가 크면 바로 우승 backbone을 선택할 수 있다.
차이가 매우 작을 때만 추가 HPO / seed 확인을 수행한다.

---

# 11. R3D Experiment ID 계획

## R3D-00 — Data / Segmentation Source Audit

상태: **IN PROGRESS**

목표:

- competition MRI 구조 재확인
- 사용할 anatomical segmentation source 결정
- pretrained segmentation candidate 확인
- mask class / coverage 확인
- 새 Gold58 3-Fold split 생성
- 3-Fold leakage-safe pseudo 생성 방식 확정

## R3D-01 — Anatomical Segmentation Baseline

상태: Planned

목표:

- segmentation pipeline 구축
- Dice / IoU 평가
- mask generation artifact 저장

## R3D-02 — Pseudo1000 + Gold58 3-Fold Manifest

상태: Planned

목표:

- Fold별 leakage-safe pseudo pool 생성
- Fold별 약 1,000 studies 선정
- R34/R50/R101 공통 manifest 고정
- SHA256 기록

## R3D-03A — 3D ResNet34 + Transformer 3-Fold

상태: **Completed — pooled Macro AUROC 0.567267 / selected S1**

## R3D-03B — 3D ResNet50 + Transformer 3-Fold

상태: **Completed — pooled Macro AUROC 0.533494 / selected S2**

## R3D-03C — 3D ResNet101 + Transformer 3-Fold

상태: **Completed — pooled Macro AUROC 0.510364 / selected S2**

## R3D-04 — Gold58 OOF Backbone Selection

상태: **Completed — MedicalNet R34 selected**

비교:

- pooled Macro AUROC
- pooled Macro AUPRC
- target metrics
- runtime / VRAM

여기서 R34 / R50 / R101 중 하나를 선택한다.

## R3D-05 — Selected R34 Representation / Architecture Confirmation

상태: **IN PROGRESS**

### R3D-05A — Global Token vs Spatial Token Fold0 Screen

상태: **Completed — GLOB selected**

| Variant | Macro AUROC | Macro AUPRC |
|---|---:|---:|
| **GLOB** | **0.601827** | 0.499933 |
| SPT27 | 0.595809 | 0.520108 |
| SPT48 | 0.590426 | **0.524856** |

판정:
- primary Macro AUROC 기준 GLOB 유지
- spatial tokens는 AUPRC를 올렸지만 AUROC를 낮췄다
- 3-Fold spatial confirmation은 진행하지 않는다
- target별로 spatial 효과 방향이 달라 향후 label-specific routing 참고 신호로만 보존한다

### R3D-05B — Backbone LR Fine-tune Strength Fold0 Screen

상태: **Completed — LR10 / backbone LR 1e-5 selected**

| Variant | Macro AUROC | Macro AUPRC |
|---|---:|---:|
| **LR10 (1e-5)** | **0.601827** | 0.499933 |
| LR5 (5e-6) | 0.591677 | 0.492868 |
| LR3 (3e-6) | 0.582062 | 0.484103 |
| FRZ | 0.579953 | **0.505985** |

판정:
- lower-LR 방향 개선 없음
- backbone LR **1e-5 고정**
- new-layer LR 5e-5 / WD 1e-4 유지
- lower-LR 추가 탐색 종료

### R3D-05C — Mask ON vs OFF Paired Fold0 Ablation

상태: **Completed — MASK_OFF selected**

| Variant | Macro AUROC | Macro AUPRC |
|---|---:|---:|
| MASK_ON | 0.601827 | 0.499933 |
| **MASK_OFF** | **0.609698** | **0.521793** |

판정:
- current anatomy-token pipeline 제거
- current nnU-Net mask coverage/fusion은 classification net gain 없음
- 후속 기본 classifier는 MASK_OFF
- shuffled-mask / availability-only control은 현재 생략
- segmentation 자체를 영구 폐기한 것은 아니며, 새로운 fusion 설계가 필요할 때만 재검토

## R3D-06 — Series Coverage / Composition

상태: **IN PROGRESS**

### R3D-06A — All-Series Neutral D24×96 Search Cache

상태: **COMPLETED — PASS**

결과:
- 4,407 studies / 24,371 series / 819,078 slice rows exact
- pixel decode failure 0
- 48 shards / 10.04055 GiB
- build 2.553 h
- old cache 1,446 studies / 4,338 series와 volume exact parity PASS
- metadata exact parity PASS
- metadata bundle SHA256: `0aacfaa0e0e19f4ddd541a99b82a00ad547e31e037ee441f9f5599be487d5586`

Notebook:
- `R3D-06A_All-Series_D24x96_Search_Cache.ipynb`
- CPU / Internet Off / Save & Run All
- 추천 Save Version: `R3D-06A All-Series D24x96 Cache`

중요:
- 이 cache는 final-training cache가 아니다.
- series composition / architecture search용이다.
- final resolution과 final series policy가 결정되면 최종 cache를 별도로 만든다.

### R3D-06B — Series Policy Audit

상태: **COMPLETED — PASS**

Full Manifest v2 metadata만 사용해 실제 Series 분포와 후보 정책 입력량을 계산한다.
Pixel decode / GPU training은 하지 않는다.

실제 결과:
- C3: 13,221 series / 54.25% / max3
- P2: 21,886 series / 89.80% / max6
- ALL: 24,371 series / 100% / max14
- Study당 series mean 5.53 / median5 / p90 7 / max14
- 4,406 / 4,407 studies가 3 series 초과
- Fluid/Fat 조합은 (0,0), (1,1) 두 종류만 존재

결정:
- 첫 GPU screen은 C3 vs P2
- ALL은 P2가 이길 때만 후속 saturation test
- R3D-06A parity PASS를 실행 gate로 사용

Notebook:
- `R3D-06B_Series_Policy_Audit.ipynb`
- CPU / Internet Off / Save & Run All
- 추천 Save Version: `R3D-06B Series Policy Audit`

### R3D-06C — Series Composition GPU Screen

상태: **COMPLETED — PASS**

비교:
- C3: canonical 3
- P2: plane별 Top-2 / max6

결과:
- C3: AUROC 0.609698 / AUPRC 0.521793 / best epoch5
- P2: AUROC 0.613282 / AUPRC 0.534338 / best epoch1
- P2-C3: AUROC +0.003584 / AUPRC +0.012546
- P2 runtime 약 +43.3%
- C3는 R3D-05C MASK_OFF reference exact 재현

Target-level:
- AUROC 6 상승 / 6 하락
- AUPRC 5 상승 / 7 하락
- target별 반응이 크게 갈림
- Fold0 20 studies이므로 label-specific series routing은 아직 도입하지 않음

판정:
- 사전 정의 primary metric 기준 P2 winner
- 단, P2를 final policy로 확정하지 않고 saturation 확인 진행

### R3D-06D — Target-Aware Series + Depth Relevance Audit

상태: **COMPLETED — PASS / TARGETQUERY NOT SELECTED**

결과:
- baseline 재학습 없음
- Fold0 TargetQuery-P2: AUROC 0.586461 / AUPRC 0.510576
- Fold1 TargetQuery-P2: AUROC 0.527435 / AUPRC 0.470353
- Frozen P2 Fold0 대비 TargetQuery Fold0:
  - AUROC -0.026820
  - AUPRC -0.023763

판정:
- TargetQuery architecture는 classifier 성능이 낮아 미채택
- Series/Depth relevance는 secondary evidence로만 보존
- 같은 TargetQuery Fold2 반복은 하지 않음

Stricter exploratory Series signal:
- ACL Cor2
- Baker's Ax1
- Contusion Cor1
- Lateral Meniscus Sag1
- Lateral OA Sag1
- Synovitis Sag1

주의:
- 여러 target의 TargetQuery Full AUROC가 0.5 미만
- hard routing 근거로 사용 금지

### R3D-06E — P2 Shared-CLS Fold1/2 Occlusion

상태: **COMPLETED — PASS**

- Fold1: 0.517551 / 0.479572
- Fold2: 0.588586 / 0.528448
- strict Series: Medial Meniscus→Sag1, Synovitis→Sag1
- initial aggregation import failure는 저장 artifact로 복구; GPU 재학습 없음

### R3D-06F — ALL-Series Saturation Fold0/1

상태: **COMPLETED — PASS**

- Fold0 ALL: 0.617594 / 0.540314
- Fold1 ALL: 0.548407 / 0.453375
- AUROC는 P2 대비 Fold0 +0.004312 / Fold1 +0.030856
- primary 기준 ALL이 2/2 Fold 우세

### R3D-06G — ALL Fold2 + P3 Fold0

상태: **COMPLETED — PASS**

- P3 Fold0: 0.624242 / 0.511143
- ALL Fold2: 0.622678 / 0.521740
- ALL은 P2 대비 Fold0/1/2 primary AUROC 모두 우세
- P3 Fold0는 P2/ALL Fold0보다 AUROC 우세
- 따라서 P3 Fold1/2 confirmation 진행

### R3D-06H — Sag1 Target-Specific Input Confirmation

상태: **FAILED ON FIRST FORWARD — FIXED RERUN NEXT**

초기 실행:
- P2 lane / Sag1 lane 모두 학습 시작 전 실패
- 원인: BinaryModel의 `self.type` embedding 이름이 PyTorch `nn.Module.type()` 메서드와 충돌
- 모델/데이터 결과가 아니라 implementation bug
- 수정본: `self.type_emb`, `self.struct_emb`
- Fresh Save & Run All 필요

재실행 목적은 동일:


Targets:
- Medial Meniscus
- Synovitis

Paired binary specialist:
- P2 input control
- Sag1-only input

Fold0 confirmation:
- relevance discovery는 Fold1/2에서 수행했으므로 동일 data로 discovery/confirmation을 반복하지 않음
- 단 Fold0는 전체 R3D architecture search에 사용된 적이 있어 완전 untouched validation으로 과장하지 않음


### Series / Target policy decision rule

R3D-06G / 06H까지 끝난 뒤 다음 순서로 고정한다.

1. 전체 입력 Series policy
- ALL Fold2까지 P2보다 primary AUROC 우세 → ALL 우선
- P3 Fold0가 ALL에 근접/우세 → P3 Fold1/2 추가 확인
- P3 Fold0가 명확히 열세 → P3 중단

2. target-specific policy
- occlusion signal만으로 hard routing 금지
- R3D-06H에서 Sag1-only가 paired P2 specialist보다 실제 AUROC/AUPRC가 좋아야 후보 유지
- 그렇지 않으면 Sag1은 '중요한 정보원'으로만 기록하고 전체 input 유지

3. Series policy는 **ALL로 확정**
- R3D-07 physical geometry / Resolution / Depth로 이동
- D24×96×96 → D24×128×128
- 필요 시 그 다음 D32×128×128
- 한 번에 한 축만 변경


### R3D-06I — P3 Fold1/2 Confirmation

상태: **NEXT — independent parallel candidate**

목적:
- Fold0에서 P3 AUROC 0.624242가 P2 0.613282 / ALL 0.617594보다 높았음
- P3가 우연한 Fold0 효과인지 Fold1/2에서도 반복되는지 확인

실행:
- GPU0 → P3 Fold1
- GPU1 → P3 Fold2
- P2 / ALL baseline은 재학습하지 않고 Frozen Reference 사용

판정:
- P3가 Fold1/2에서도 ALL과 경쟁 또는 우세 → P3 우선 series policy
- P3가 Fold1/2에서 ALL보다 일관되게 열세 → ALL 우선
- mixed → pooled Gold58 및 fold stability로 최종 결정



### R3D-07A / 07B — Geometry First Wave

상태: **NEXT — A/B 병렬**

현재 Series policy:
- base classifier = **ALL**
- Medial Meniscus Sag1-only specialist는 별도 final candidate로 보존
- Synovitis Sag1-only는 기각

남은 시간 동안 연구축은 두 개만 유지한다.

#### Account A — A_R3D-07A

**Physical FOV 140 mm Crop / D24×96×96 / ALL / Fold0**

변경:
- full-frame in-plane FOV → centered 140 mm physical crop

고정:
- D24×96×96
- ALL Series
- R34 GLOB MASK_OFF
- LR / WD / pseudo / Fold0 / epochs / augmentation contract

목적:
- scanner마다 다른 PixelSpacing / FOV를 물리 단위로 정규화하고
  무릎이 입력 화면에서 차지하는 비율을 높이는 효과만 확인

#### Account B — B_R3D-07B

**Full FOV / D24×128×128 / ALL / Fold0**

변경:
- 96×96 → 128×128

고정:
- full-frame FOV
- D24
- ALL Series
- R34 GLOB MASK_OFF
- LR / WD / pseudo / Fold0 / epochs / augmentation contract

목적:
- 작은 병변 / 연골 / meniscus detail 보존을 위해
  in-plane resolution 증가 효과만 확인

Frozen ALL Fold0:
- AUROC 0.617594
- AUPRC 0.540314

판정:
- 07A만 개선 → crop 우선
- 07B만 개선 → resolution 우선
- 둘 다 개선 → 다음 wave에서 140mm + 128 조합
- 둘 다 미개선 → depth / raw-slice geometry를 우선 확인

주의:
- cache는 전체 4,407 study를 다시 만들지 않고
  Fold0 search에 필요한 Gold58 + Fold0 Pseudo1000 UID만 대상으로 생성해 시간 절감
- baseline ALL Fold0는 재학습하지 않음
- A/B Notebook filename과 Save Version에 Account tag 필수

## R3D-07 — Resolution / Depth Screen

상태: Planned

Series policy를 먼저 고정한 뒤:
- D24×96×96 baseline
- D24×128×128
- 필요 시 D32×128×128

처럼 in-plane resolution과 depth를 한 번에 바꾸지 않고 분리해서 비교한다.

## R3D-08 — Final Small HPO + 3-Fold Confirmation

상태: Planned

- 구조/series/resolution 고정 후 new-layer LR / WD 등 최소 범위만 조정
- 반복 Fold0 micro-search 제한
- 최종 후보를 Fold0/1/2에서 확인
- pooled Gold58와 fold stability 기록

## R3D-09 — Full-data Final Training

상태: Planned

선택된 architecture / series / resolution / mask policy를 고정한 뒤 전체 supervision으로 final model을 학습한다.

## R3D-10 — Kaggle Submission

상태: Planned

- hidden-test inference
- submission contract validation
- Public LB 기록
- Exp57 0.918과 직접 비교

---

# 12. 현재 진척 상태

2026-10-05 기준:

- [x] 2026 knee MRI 최신 연구 방향 검토
- [x] DINOv2 신규 계보에서 제외
- [x] 3D ResNet 계열 선택
- [x] R34 / R50 / R101 비교 결정
- [x] Transformer를 모든 backbone candidate에 부착하기로 결정
- [x] Full Fine-tuning 결정
- [x] LoRA 제외
- [x] BBox 대신 Anatomical Segmentation 선택
- [x] Gold58 3-Fold OOF 결정
- [x] 초기 빠른 비교용 pseudo 약 1,000 결정
- [x] primary metric Macro AUROC 결정
- [x] secondary metric Macro AUPRC 결정
- [~] segmentation source / architecture audit 진행 중
- [x] MRI + mask exact fusion 결정 — feature-conditioning / anatomy-token
- [x] pretrained 3D ResNet source 결정 — MedicalNet original common lineage
- [x] Transformer 세부 baseline 결정 — 2L / d512 / 8 heads / FFN2048
- [x] Gold58 3-Fold manifest 생성 — R3D-00A seed 20261059 / 20·19·19 / class coverage PASS
- [~] 3-Fold leakage-safe pseudo 방식 재현 검증 중 — R3D-00A2도 REVIEW → R3D-00A3 V4 Formula Forensic Audit
- [ ] R3D-01 실행
- [ ] R3D-02 실행
- [ ] R3D-03A/B/C 실행
- [ ] R3D-04 backbone 확정
- [ ] full-data 학습
- [ ] submission

다음 채팅에서 가장 먼저 할 일은 **R3D-00**이다.


---

# 13. R3D-00 Audit Update — 2026-10-05

현재 R3D-00은 진행 중이며, 아래 항목은 audit 단계에서 확정했다.

## 13.1 Competition data contract

- 한 study는 여러 MRI series로 구성한다.
- series metadata에는 Sagittal / Coronal / Axial plane과 Fluid_Sensitive / Fat_Suppression 정보가 있다.
- series별 slice 수, spacing, resolution, intensity가 다를 수 있으므로 하나의 series만 고정 선택하는 구조보다 study-level multi-series aggregation을 기본으로 한다.
- Transformer는 series 간 정보를 통합하는 study-level aggregator 역할을 한다.

## 13.2 Pretrained 3D ResNet source

R34 / R50 / R101 초기 비교는 Tencent MedicalNet original pretrained lineage로 고정한다.

- resnet_34.pth — shortcut A
- resnet_50.pth — shortcut B
- resnet_101.pth — shortcut B

MedicalNet의 newer 23-dataset weight는 R34 / R50까지만 제공되고 R101은 동일 계보가 없다.
따라서 R34/R50만 23-dataset weight를 쓰고 R101을 original weight로 쓰지 않는다.
Backbone depth 외의 pretraining corpus 차이를 제거하기 위해 세 모델 모두 original common lineage를 사용한다.

모든 weight는 Kaggle offline input으로 고정하고 실제 파일 SHA256을 notebook contract에서 검증한다.

## 13.3 MRI + anatomical mask fusion

초기 backbone 비교에서는 input-channel concat을 사용하지 않는다.

이유:

- MedicalNet의 pretrained 1-channel stem을 그대로 보존한다.
- anatomical class 수가 변해도 backbone input contract가 변하지 않는다.
- Full MRI information을 mask로 잘라내지 않는다.
- R34 / R50 / R101 비교에서 initialization 차이를 최소화한다.

초기 fusion은 feature-conditioning / anatomy-token 방식으로 고정한다.

흐름:

MRI series
→ pretrained 3D ResNet
→ final 3D feature map
→ common d_model projection
→ global MRI pooling + structure별 mask-weighted pooling
→ series/global token + anatomy structure token
→ Transformer

mask가 없거나 segmentation이 실패한 series도 버리지 않는다.
global MRI token은 항상 유지하고 anatomy token만 생략한다.
mask_present 상태는 metadata / manifest에 기록한다.

## 13.4 Transformer baseline

R3D-03A/B/C의 initial backbone comparison에서는 다음을 공통으로 고정한다.

- d_model: 512
- Transformer encoder layers: 2
- attention heads: 8
- FFN dimension: 2048
- dropout: 0.10
- Pre-LayerNorm
- learnable CLS token
- hard-coded series order positional embedding은 사용하지 않음

각 token에는 가능한 metadata embedding을 더한다.

- Anatomical_Plane
- Fluid_Sensitive
- Fat_Suppression
- global MRI / anatomy token type
- anatomy structure ID

Transformer CLS output을 shared representation으로 사용하고 12개 label-specific sigmoid head로 전달한다.

Transformer 자체 HPO는 initial R34/R50/R101 비교에서는 하지 않고,
R3D-04 backbone 선택 이후 필요할 때만 수행한다.

## 13.5 Segmentation source audit

아직 최종 segmentation source는 고정하지 않았다.
RSNA domain compatibility를 실제로 확인한 뒤 결정한다.

Primary compatibility candidate:

aagatti/nnunet_knee

- 3D nnU-Net
- 공개 weight
- 9 anatomy classes:
  - Femur
  - Tibia
  - Patella
  - Femoral cartilage
  - Medial tibial cartilage
  - Lateral tibial cartilage
  - Patellar cartilage
  - Medial meniscus
  - Lateral meniscus
- bone / cartilage / meniscus coverage가 넓어 OA, meniscus, contusion, fracture target에 유리
- 공개 model card와 연결 논문의 implementation provenance를 최종 확인해야 함
- RSNA의 다양한 sequence / plane에서 직접 compatibility test 필요

Fallback candidate:

KneeXNet-2.5D

- 2026 npj Health Systems peer-reviewed
- 2.5D U-Net + ResNet34 encoder
- sagittal 인접 3-slice context
- 공개 mean IoU 약 0.8108 / mean Dice 약 0.8779
- 4 anatomy structures:
  - distal femoral cartilage
  - proximal tibial cartilage
  - patellar cartilage
  - meniscus
- 코드 / annotation / trained model 공개
- 단점: sagittal/OAI 중심, bone 없음, medial/lateral meniscus 미분리
- GitHub pth 파일은 Git LFS pointer이므로 실제 weight를 Kaggle Dataset으로 별도 고정해야 함

Reference candidate:

SKM-TEA

- Stanford qDESS knee MRI benchmark
- 155 scans
- six tissue segmentation
- pretrained V-Net / U-Net model zoo 존재
- qDESS domain과 큰 source dataset/dependency 때문에 현재 deployment primary가 아니라 reference로 둔다.

Segmentation selection gate:

1. 실제 model/weight provenance 확인
2. Kaggle offline load 확인
3. 공개 annotation에서 structure별 Dice / IoU contract 확인
4. RSNA representative studies에서 Sagittal / Coronal / Axial 및 fluid/fat-suppression 조합별 mask sanity audit
5. mask presence / connected component / normalized volume / slice span 이상치 확인
6. anatomy-only mask 사용
7. pathology mask는 classification target을 직접 암시할 수 있으므로 baseline에서는 사용하지 않음

현재 우선순위는 aagatti/nnunet_knee를 먼저 compatibility test하고,
통과하지 못하면 KneeXNet-2.5D로 내려간다.

## 13.6 New Gold58 3-Fold pseudo policy

새 3-Fold OOF에서는 기존 V4 full-data pseudo나 기존 V4 5-Fold pseudo 파일을 직접 재사용하지 않는다.

기존 V4 Target-Routed Consensus 알고리즘 자체는 유지하되,
새 R3D Gold58 3-Fold의 train-side Gold만으로 Fold별 route / reader skill / reader weight를 다시 fit한다.

기존 핵심 reader:

- report_labels_v2.csv
- report_labels_gpt56sol.csv

유지할 V4 원칙:

- GPT binary output은 confidence에 따라 0.5 방향으로 softening
- public v2 soft label은 severity information 유지
- reader skill은 target별 Gold와 비교
- reader weight는 random보다 높은 skill의 제곱에 비례
- target마다 GPT / v2 / simple weighted blend / availability-aware consensus 네 route 후보 비교
- reader disagreement는 confidence를 낮추는 방향으로 처리
- mild / trace public positive는 낮은 confidence 부여

Fold k:

Gold Train 약 38~39
→ reader skill / route / weight fitting

Gold Val 약 19~20
→ routing / threshold / pseudo subset selection에 절대 사용 금지

또한 full-Gold에서 정한 기존 strict confidence threshold는 새 3-Fold OOF에 그대로 재사용하지 않는다.
초기 Pseudo1000은 새 Fold별 broad soft label + confidence를 기반으로 선정한다.
필요한 strict stage가 생기면 Fold Train Gold만으로 threshold를 새로 정한다.

예정 artifact:

- r3d_gold58_3fold_manifest.csv
- r3d_gold58_3fold_distribution.csv
- r3d_pseudolabels_fold0.csv
- r3d_pseudolabels_fold1.csv
- r3d_pseudolabels_fold2.csv
- r3d_pseudo_fold_policies.csv
- r3d_pseudo_method.json

모든 manifest / pseudo artifact는 SHA256을 기록한다.

## 13.7 R3D-00 남은 작업

- primary segmentation candidate weight/package provenance 최종 확인
- RSNA representative study segmentation compatibility run
- 최종 segmentation source / class 고정
- Gold58 deterministic multilabel 3-Fold manifest 실제 생성
- Fold별 target class coverage 확인
- 새 3-Fold pseudo route policy 실제 생성
- R3D-01 / R3D-02 artifact contract 확정


## 13.8 Two-Account Parallel Execution Policy

사용자 + 팀원 1명으로 Kaggle 실행을 최대 2개까지 병렬 수행할 수 있다.

기본 원칙:

- 서로 결과 의존성이 없는 실험은 A/B 두 계정에서 동시에 실행한다.
- 같은 artifact를 동시에 생성/수정하는 실험은 병렬화하지 않는다.
- 후속 실험이 선행 결과를 필요로 하면 해당 dependency만 기다린다.
- backbone 3-Fold / model-size 비교 단계에서도 가능한 경우 2-run 병렬 실행을 기본으로 한다.

### Current parallel wave — R3D-00

#### R3D-00A — Gold58 3-Fold + V4 Routing Reproduction Audit

상태: **COMPLETED — REVIEW**

- Runtime: CPU
- Internet: Off
- 목적:
  - Gold58 deterministic multilabel 3-Fold manifest 생성
  - fold target class coverage 확인
  - 기존 V4 reader skill / reader weight / route AUC 공식 reproduction audit
- pseudo 생성은 exact reproduction contract 확인 전까지 수행하지 않는다.

Notebook:
- `R3D-00A_Gold58_3Fold_V4_Repro_Audit.ipynb`

#### R3D-00B / B2 — nnU-Net RSNA Compatibility Audit

상태: **B environment failure → B2 READY TO RUN**

- Runtime: T4 x1
- Internet: On
- segmentation candidate:
  - `aagatti/nnunet_knee`
  - self-contained `3d_fullres` checkpoint 우선 compatibility test
- 목적:
  - 공개 test image / GT Dice-IoU validation
  - RSNA representative Sagittal / Coronal / Axial series inference
  - mask structure presence / foreground ratio / connected-component sanity audit

R3D-00B first run:
- Kaggle base environment에 nnU-Net dependency를 직접 설치하면서 NumPy가 2.5.3으로 변경
- 기존 SciPy binary와 ABI 충돌
- `scipy.ndimage` import에서 중단
- segmentation model 자체 실패가 아니라 environment failure로 판정

R3D-00B2 수정:
- isolated virtualenv
- Kaggle base NumPy/SciPy/Pandas version 고정
- `scipy.ndimage` 제거
- Connected Component는 SimpleITK 사용

Notebook:
- `R3D-00B2_nnUNet_RSNA_Compatibility_Audit.ipynb`

두 실험은 독립이므로 **동시에 실행**한다.

### R3D-00A 실행 결과 — 2026-10-05

- Gold58 exactly-once: PASS
- deterministic split seed: `20261059`
- Fold sizes: `20 / 19 / 19`
- 모든 12 target에서 모든 Fold Positive/Negative coverage: PASS
- manifest SHA256: `246f252a1ce4faaafa1b7d30e2c75cde6d79951cb780b0b33bf4f4dd12ad7e4b`
- V2 AUC reproduction: exact
- GPT / reader weight / blend reproduction: REVIEW

원인:
기존 V4 method는 두 reader 공통 Gold overlap `57`건을 calibration에 사용했는데,
R3D-00A는 GPT를 58건 전체로, V2를 57건으로 각각 계산했다.
따라서 GPT AUC와 reader weight가 기존 V4와 달라졌다.

R3D-00A2 결과:

- manifest exact match: PASS
- Common Gold57: PASS
- V2 AUC: 12 target exact
- GPT AUC / skill / weight: FAIL
- broad label oracle max error: 0.58
- confidence formula exact reproduction: FAIL
- overall: REVIEW

해석:
Common57 자체가 핵심 원인이 아니며, 기존 V4는 GPT raw target 대신 confidence 기반 변환 signal을 routing에 사용했다.

다음 CPU audit:
**R3D-00A3 — V4 Formula Forensic Audit**

- master의 route-independent internal reader signals로 raw→reader transform 복구
- 기존 V4 fold0~4 + fold policy 60개 조합을 dynamic-route oracle로 사용
- Gold57 routing AUC / skill / squared weight exact reproduction 재검증
- fold pseudo label / confidence formula exact reproduction
- full-data route / top-level pseudo label은 새 R3D training input으로 직접 재사용 금지

Notebook:
- `R3D-00A3_V4_Formula_Forensic_Audit.ipynb`

다음 dependency:

- 00A reproduction PASS
  → 새 3-Fold leakage-safe pseudo generator 작성 / 실행 가능
- 00B compatibility PASS
  → segmentation candidate A를 R3D-01 baseline으로 승격 가능
- 둘 중 하나가 REVIEW여도 다른 쪽 후속 작업은 독립적으로 계속 진행한다.

---

# 14. R3D-03 / R3D-04 Execution Update — 2026-10-06

## 14.1 Frozen assets used

- Gold58 manifest SHA256: 246f252a1ce4faaafa1b7d30e2c75cde6d79951cb780b0b33bf4f4dd12ad7e4b
- canonical search cache: **1,446 studies**
- nnU-Net anatomy masks: **154 studies**
- MedicalNet offline pretrained:
  - R34 SHA 977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658
  - R50 SHA 5b6189cafbee2f5604a7279b62bc163365aa6a86a377e1dc260a14275cacbd84
  - R101 SHA a26bbcf9b2ad35f048b0fa317234c003f171a4d719760e5c4aff9f793654ebcf

## 14.2 Search result

| Backbone | Screen winner | Pooled Macro AUROC | Pooled Macro AUPRC |
|---|---|---:|---:|
| **R34** | **S1** | **0.567267** | **0.430502** |
| R50 | S2 | 0.533494 | 0.418787 |
| R101 | S2 | 0.510364 | 0.385794 |

R34 is selected.

## 14.3 Precision decision

후속 MedicalNet R34 실험은 pure FP32로 고정한다.

- R34/R50 training에서 AMP forward가 반복적으로 non-finite → FP32 fallback
- R101은 screen의 모든 forward가 FP32 fallback
- FP32 validation은 finite
- AMP retry는 계산을 줄이지 못하고 오히려 중복 forward를 만든다

## 14.4 Architecture issue to test next

현재 baseline:

~~~text
final 3D feature map
→ spatial global average
→ 1 MRI token / series
→ Transformer
~~~

다음:

~~~text
final 3D feature map
→ global token 유지
+ coarse 3D spatial tokens
+ mask-weighted anatomy tokens when available
→ Transformer
~~~

R34 final feature map에서 local spatial evidence가 Transformer까지 전달되는지 R3D-05A에서 먼저 Fold0로 검증한다.

## 14.5 Full-train cache policy

4,349 report-only 전체 DICOM / segmentation cache는 아직 만들지 않는다.

순서:
1. R34 representation 확정
2. segmentation contribution 확인
3. 최종 series 구성 확정
4. 그 뒤 full-train DICOM cache
5. 필요한 경우 segmentation teacher/student artifact 확장
6. final HPO / training

---

# 15. R3D-05A Execution Update — 2026-10-06

- contract: PASS
- GPU T4 x2
- pure FP32 preflight: PASS
- pretrained fraction: 1.0
- cache: 1,446 studies / masks 154
- same Fold0 validation UID order across all variants: PASS

Result:
- GLOB: AUROC 0.601827 / AUPRC 0.499933 / best epoch 9
- SPT27: AUROC 0.595809 / AUPRC 0.520108 / best epoch 8
- SPT48: AUROC 0.590426 / AUPRC 0.524856 / best epoch 8

Conclusion:
coarse spatial token을 shared Transformer에 일괄 추가하는 방식은 primary AUROC 개선이 없었다.
R34 representation은 GLOB를 유지한다.
다음은 lower backbone LR / frozen 비교다.

---

# 16. R3D-05B Execution Update — 2026-10-06

- contract: PASS
- R34 pretrained fraction: 1.0
- FP32 forward/backward: PASS
- backbone freeze contract: PASS
- same Fold0 validation UIDs: PASS
- result ZIP SHA256: 12dd6e311d5ff33b78caab17fd2732cd41033a0276423e84a2caadc8ec0f5026

Result:
- LR10: AUROC 0.601827 / AUPRC 0.499933 / best epoch 9
- LR5: AUROC 0.591677 / AUPRC 0.492868 / best epoch 8
- LR3: AUROC 0.582062 / AUPRC 0.484103 / best epoch 8
- FRZ: AUROC 0.579953 / AUPRC 0.505985 / best epoch 9

Conclusion:
lower LR 또는 backbone freeze는 primary AUROC를 개선하지 않았다.
R34 backbone LR은 1e-5로 고정하고 다음 Mask ON/OFF ablation으로 이동한다.

---

# 17. R3D-05C Execution Update — 2026-10-06

- contract: PASS
- initial model state identical: PASS
- sample UID trace identical: PASS
- same Fold0 validation UIDs: PASS
- pure FP32 preflight: PASS
- result ZIP SHA256: 9ebc077f05572c1b647eff35125db4ae651d17068e512794f95393b0b90620d2

Mask coverage:
- 154 / 1,446 cached studies
- Gold Train: 36 / 38 masked
- Gold Val: 20 / 20 masked
- Pseudo1000: 97 / 1,000 masked

Result:
- MASK_ON: AUROC 0.601827 / AUPRC 0.499933 / best epoch 9
- MASK_OFF: AUROC 0.609698 / AUPRC 0.521793 / best epoch 5
- ON-OFF: AUROC -0.007871 / AUPRC -0.021860

Conclusion:
현재 154-mask coverage + anatomy-token fusion은 classification 성능을 개선하지 않았다.
후속 R3D 기본 classifier는 MASK_OFF로 진행한다.
다음은 all-series neutral cache와 series composition 실험이다.


### R3D-07 cache/runtime separation

R3D-07A/07B의 새 tensor cache는 GPU Notebook 내부에서 만들지 않는다.

Shared prerequisite:
- **Account A**
- `A_R3D-07CACHE_Shared_GeometryDetail_CPU.ipynb`
- Accelerator: None / CPU
- 4개 variant cache를 한 번의 raw decode pass로 생성
- 생성 후 Kaggle Dataset `rsna-knee-r3d07-geometry-cache-v1`로 저장하고 Account B에 공유

GPU training:
- Account A: `A_R3D-07A_Crop130_150_Fold0_DualT4_TRAIN_ONLY.ipynb`
- Account B: `B_R3D-07B_R128_D32_Fold0_DualT4_TRAIN_ONLY.ipynb`

GPU Notebook은 raw competition DICOM을 읽어 cache를 생성하지 않는다.



### R3D-07A result — Physical FOV

상태: **COMPLETED — PASS**

- Full-FOV Frozen ALL Fold0: 0.617594 / 0.540314
- 130 mm D24×96: **0.622257 / 0.508100**
- 150 mm D24×96: 0.618253 / 0.521752
- primary AUROC winner: **130 mm**
- 130 mm AUROC gain vs baseline: **+0.004663**
- 130 mm AUPRC delta: **-0.032215**

현재 gate:
- crop 효과는 약한 positive signal
- 추가 130/140/150 FOV micro-search는 하지 않음
- R3D-07B resolution/depth 결과를 먼저 확인
- 다음 조합 실험은 07B winner가 결정된 뒤 선택


### R3D-07B result — Resolution / Depth

상태: **COMPLETED — PASS**

- Frozen ALL Fold0 D24×96: 0.617594 / 0.540314
- D24×128: **0.607901 / 0.504403**
- D32×96: **0.604305 / 0.504119**

판정:
- simple 96→128 resolution increase: reject
- simple D24→D32 uniform resample: reject
- 추가 160/192/224 또는 D40/D48 숫자 확대는 현재 근거 없음

다음:
- real-slice adjacency / physical spacing-aware depth policy
- CPU-only cache generation
- GPU training-only comparison
- 130 mm crop은 weak positive 후보로 유지하며,
  real-slice geometry winner가 생긴 뒤 조합 여부를 판단


### R3D-08A / R3D-08B — Actual-Slice Preservation

상태: **NEXT — A/B 병렬**

목적:
- 기존 z-axis trilinear interpolation이 작은 병변 정보를 희석하는지 직접 검증
- 단순 D32 interpolation 실패와 real-slice preservation을 구분

R3D-08A:
- Account A
- REAL24_R96
- Fold0 / Fold1 dual-T4
- 원본 actual slice만 사용

R3D-08B:
- Account B
- REAL32_R96
- Fold0 / Fold1 dual-T4
- 원본 actual slice만 사용

공통:
- ALL Series
- R34 GLOB MASK_OFF
- Transformer + CLS
- LR/WD/pseudo/sampling contract 유지
- baseline 재학습 없음
- pretrained matched fraction >0.90 assert
- Fold0/Fold1 sample trace exact assert

후속:
- 명확한 winner만 Fold2 confirmation
- real-slice winner가 생긴 뒤 130 mm crop과 조합 여부 판단


### R3D-08 Actual-Slice screen result

상태: **F0/F1 COMPLETED**

REAL24:
- Fold0: 0.622138 / 0.543167
- Fold1: 0.547613 / 0.453627
- mean ΔAUROC vs Frozen = **+0.001875**
- mean ΔAUPRC vs Frozen = **+0.001553**
- decision: **Fold2 confirmation**

REAL32:
- Fold0: 0.604739 / 0.504463
- Fold1: 0.559398 / 0.450640
- mean ΔAUROC vs Frozen = **-0.000932**
- mean ΔAUPRC vs Frozen = **-0.019293**
- decision: **stop**

다음 experiment:
- R3D-08C — REAL24 Fold2 confirmation
- 기존 F0/F1 REAL24 cache 재사용
- Fold2 pseudo1000에 필요한 missing Study만 CPU delta cache
- GPU notebook은 Fold2 training only


### R3D-08C final result — REAL24 rejected as non-robust

Fold2 REAL24:
- AUROC 0.620144 vs Frozen 0.622678
- AUPRC 0.521160 vs Frozen 0.521740
- ΔAUC -0.002534
- ΔAP -0.000580

REAL24 3-Fold mean:
- ΔAUC +0.000405
- ΔAP +0.000842

Interpretation:
- sign-only auto contract said ADOPT
- experiment decision = **do not adopt**
- Fold0 positive / Fold1 nearly flat negative / Fold2 negative
- gain magnitude too small for Gold58 model selection confidence

Freeze:
- interpolated D24×96 remains current depth/resolution representation

Next:
- 130 mm physical crop Fold1/Fold2 confirmation
- if not robustly positive, final Main R3D input = Full-FOV interpolated D24×96
