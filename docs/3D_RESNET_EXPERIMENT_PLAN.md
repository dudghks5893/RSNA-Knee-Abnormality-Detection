# RSNA Knee — 3D ResNet Experiment Plan

최종 업데이트: **2026-10-05**

상태: **R3D-00 진행 중**

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

상태: Planned

## R3D-03B — 3D ResNet50 + Transformer 3-Fold

상태: Planned

## R3D-03C — 3D ResNet101 + Transformer 3-Fold

상태: Planned

## R3D-04 — Gold58 OOF Backbone Selection

상태: Planned

비교:

- pooled Macro AUROC
- pooled Macro AUPRC
- target metrics
- runtime / VRAM

여기서 R34 / R50 / R101 중 하나를 선택한다.

## R3D-05 — Selected Backbone HPO / Confirmation

상태: Planned

필요할 때만 수행한다.
R3D-04에서 차이가 명확하면 과도한 추가 tuning을 하지 않는다.

## R3D-06 — Full-data Final Training

상태: Planned

선택된 architecture / preprocessing / segmentation을 고정한 뒤
전체 사용 가능한 training supervision으로 최종 학습한다.

Final training에서 Gold를 다시 포함하는 정확한 방식과 Fold ensemble 여부는
R3D-04/05 결과를 보고 결정한다.

## R3D-07 — Kaggle Submission

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
- [ ] Gold58 3-Fold manifest 생성
- [~] 3-Fold leakage-safe pseudo 방식 확정 / artifact 생성 전
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

상태: **READY TO RUN**

- Runtime: CPU
- Internet: Off
- 목적:
  - Gold58 deterministic multilabel 3-Fold manifest 생성
  - fold target class coverage 확인
  - 기존 V4 reader skill / reader weight / route AUC 공식 reproduction audit
- pseudo 생성은 exact reproduction contract 확인 전까지 수행하지 않는다.

Notebook:
- `R3D-00A_Gold58_3Fold_V4_Repro_Audit.ipynb`

#### R3D-00B — nnU-Net RSNA Compatibility Audit

상태: **READY TO RUN**

- Runtime: T4 x1
- Internet: On
- segmentation candidate:
  - `aagatti/nnunet_knee`
  - self-contained `3d_fullres` checkpoint 우선 compatibility test
- 목적:
  - 공개 test image / GT Dice-IoU validation
  - RSNA representative Sagittal / Coronal / Axial series inference
  - mask structure presence / foreground ratio / connected-component sanity audit

Notebook:
- `R3D-00B_nnUNet_RSNA_Compatibility_Audit.ipynb`

두 실험은 독립이므로 **동시에 실행**한다.

다음 dependency:

- 00A reproduction PASS
  → 새 3-Fold leakage-safe pseudo generator 작성 / 실행 가능
- 00B compatibility PASS
  → segmentation candidate A를 R3D-01 baseline으로 승격 가능
- 둘 중 하나가 REVIEW여도 다른 쪽 후속 작업은 독립적으로 계속 진행한다.
