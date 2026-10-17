# RSNA Knee — Branch A/B/C 통합 인수인계
## Branch-C 상세 설계 시작용 Cold-Start Handoff

최종 상태 기준: **2026-10-18 (KST)**

이 문서는 다음 새 채팅에서 지금까지의 전체 진행 상황을 잃지 않고 바로 이어가기 위한 **실행형 인수인계 문서**다.

다음 채팅의 우선 작업은 **현재 진행 중인 S11 70:30 제출 결과와 Branch-B CoAtNet 학습 결과를 기다리는 동안 Branch-C ConvNeXt Anatomy Expert의 상세 설계를 재검토하고 확정하는 것**이다.

---

# 0. 다음 채팅에서 가장 먼저 해야 할 일

다음 채팅에서는 아래 순서로 시작한다.

1. 이 문서를 읽는다.
2. GitHub 최신 문서를 읽는다.
   - `docs/CURRENT_HANDOFF.md`
   - `docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md`
   - `docs/GPU_BATCH_RESOURCE_MANDATORY_POLICY.md`
   - `docs/DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md`
   - `docs/DINO_S/S1-DINO-CBL2F-01_ROADMAP.md`
   - `docs/COATNET/COATNET_BRANCH_PLAN.md`
   - `docs/COATNET/COATNET_EXPERIMENT_LOG.md`
   - `docs/CONVNEXT/CONVNEXT_BRANCH_PLAN.md`
   - `docs/CONVNEXT/CONVNEXT_EXPERIMENT_LOG.md`
3. **Branch-B V3 학습을 중단하지 않는다.**
4. **S11 70:30 제출 결과를 기다리는 동안 Branch-C 상세 설계를 먼저 진행한다.**
5. Branch-C 학습/캐시 Notebook을 바로 만들지 말고, 아래 “Branch-C 재설계 Gate”를 먼저 확정한다.

---

# 1. 프로젝트 최종 큰 구조

현재 전체 전략은 같은 모델을 직렬로 계속 덧붙이는 방식이 아니다.

```text
Branch-A = DINO Core
Branch-B = CoAtNet Wide-MRI Expert
Branch-C = ConvNeXt Anatomy Expert

최종 목표
= 서로 다른 오류 패턴을 가진 2~3개 Expert를 앙상블
```

현재 역할:

```text
A — DINO Core
Full MRI
→ Stage1 DINO Base
→ S8C MIL / selector
→ Top18
→ S10/S11 DINO 재판독
→ S8C Full-MRI Direct와 hybrid

B — CoAtNet Wide-MRI Expert
96-slice anatomical fixed slots
→ Wide/Dense MRI coverage
→ target-specific Window MIL
→ DINO selector에 독립

C — ConvNeXt Anatomy Expert
Full FOV + anatomy-local views
→ target-specific spatial attention
→ target-specific Window MIL
→ A/B와 다른 CNN + localization error pattern
```

핵심 원칙:

- Branch-B/C는 S8C Top18을 입력으로 사용하지 않는다.
- Branch 수를 늘리는 것이 목적이 아니라 **오류 상관을 낮추는 것**이 목적이다.
- 각 Branch는 standalone Public LB와 ensemble gain을 둘 다 본다.
- 최종 앙상블은 probability 평균뿐 아니라 **per-target percentile-rank**를 우선 검토한다.

---

# 2. Branch-A — DINO Core 현재 확정 상태

## 2.1 현재 주요 Public LB

| 모델 / 제출 | Public LB |
|---|---:|
| **S11 LAST 2F standalone** | **0.926** |
| **S10 LAST 70% + S8C Direct 30%** | **0.926** |
| S10 Top18 Strict FT LAST 2F standalone | 0.923 |
| S8C Window+Series Attention MIL | 0.923 |
| S8B Window Attention MIL | 0.923 |
| S8A Mean MIL | 0.918 |
| Stage1 V4 Strict FT LAST | 0.914 |
| Stage1 V4 Broad DINO Base | 0.910 |
| DINOv2-Small V4 Broad 2F | 0.899 |
| V54A Stage1 | 0.873 |

현재 프로젝트 최고 Public LB는 **0.926**이다.

---


# 2.2 과거 실험 계보에서 이미 닫힌 결론

다음 채팅은 아래 축을 근거 없이 다시 처음부터 반복하지 않는다.

## Historical Exp 계보

과거 강한 기준:

```text
Exp57 Public LB ≈ 0.918
```

이 계보에서 중요한 구조적 교훈은:

```text
Top-K final branch
+
selector/full-MRI direct branch
```

를 결합한 hybrid가 유효했다는 것이다.

이 경험이 현재:

```text
S10/S11 70%
+
S8C Full-MRI Direct 30%
```

구조의 직접적인 근거다.

## Specialist 계보

최종 Specialist submission:

```text
Public LB ≈ 0.876
```

질환별 high-confidence/top-percentile specialist가 일부 local target에서는 높은 Gold score를 보였지만
전체 submission mainline으로는 현재 DINO 계보보다 낮았다.

따라서 target specialist를 별도 주력 Branch로 되돌리지 않는다.

## 3D / R3D 계보

대표 R3D:

```text
R3D-13V4 Gold58 Macro AUROC ≈ 0.680
Public LB ≈ 0.689
```

3D MedicalNet 계보는 현재 2D/2.5D DINO/CoAtNet 전략보다 크게 낮다.

새 evidence 없이 3D mainline으로 회귀하지 않는다.

## RMIL 초기 계보

대표:

```text
RMIL-01
MEAN ≈ 0.576
Attention ≈ 0.544

RMIL-02 K16 Mean ≈ 0.578
```

초기 작은 Window 후보에서는 Attention이 오히려 악화된 사례가 있었다.

교훈:

- Attention 자체를 무조건 좋다고 가정하지 않는다.
- 충분한 후보 coverage와 input quality가 먼저다.
- 현재 S8B/S8C에서 Attention이 실제 Public LB 0.923까지 올라간 것은 Full-MRI feature/candidate 표현이 개선된 뒤의 결과다.

## DINO Small vs Base

이미 실제 2-Fold/Public LB로 비교했다.

```text
DINOv2-Base V4 Broad   0.910
DINOv2-Small V4 Broad  0.899
```

차이:

```text
Base +0.011
```

따라서 현재 DINO Core에서 Small vs Base를 다시 반복하지 않는다.

## S8 MIL progression

```text
S8A Mean MIL                 0.918
S8B Window Attention MIL     0.923
S8C Window+Series Attention  0.923
```

S8C의 중요한 가치는 단순 standalone score만이 아니다.

```text
Full-MRI Direct prediction
+
label-free Top18 selector
```

를 동시에 제공해 S10/S11 hybrid를 가능하게 한다.

## S10 / S11 progression

```text
S10 standalone              0.923
S10 70 + S8C Direct 30      0.926
S11 standalone              0.926
S11 70 + S8C Direct 30      현재 제출 중
```

따라서 현재 Branch-A는 단순히 backbone을 또 바꾸기보다 B/C 독립 expert와 ensemble하는 것이 우선이다.

## LABEL-V6 vs V4

LABEL-V6는 의미 라벨 검토/soft-label 연구로는 중요한 작업이었지만,
실제 모델 실험에서 V4보다 낮은 0.8대 결과가 나왔다.

현재 학습 supervision mainline:

```text
Base:
V4 Routed Broad

High-confidence FT:
V4 Routed Strict
```

Branch-B/C에서 “최신 라벨”이라는 이유만으로 LABEL-V6를 자동 채택하지 않는다.

V4 Strict exact path:

```text
/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/
rsna_knee_pseudolabels_v4_routed_strict.csv
```

known SHA:

```text
bfca4993e5c985d9318d732bf2a0970dd7af9b3beff1d6ff619822042bf7a2c0
```

---

# 3. Branch-A 상세 파이프라인

```text
Stage1-A
DINOv2-Base
V4 Routed Broad
2-Fold
Full-MRI feature backbone

        ↓

Stage1-B
same DINOv2-Base
V4 Strict 고신뢰 추가 FT
2-Fold

        ↓

Stage2 / S8C
Full-MRI feature
target-specific Window Attention
+ Series Attention
2-Fold

        ├─────────────→ Full-MRI Direct prediction
        │
        └─────────────→ label-free Top18 selector

                                ↓

Stage3 / S10
Top18
DINOv2-Base
V4 Strict FT
2-Fold

                                ↓

S11
S10 Top18 동일 center
DETAIL / ANCHOR / CONTEXT Multi-View
DINOv2-Base shared backbone
target-specific fixed logit routing
2-Fold
```

S8C는 두 가지 역할을 동시에 한다.

1. **Full-MRI Direct predictor**
2. **Top18 selector**

따라서 `70% final DINO + 30% S8C`에서 30%는 사진 30%가 아니다.

```text
S8C는 전체 MRI feature로 직접 12-target probability 생성
+
S8C가 중요하다고 선택한 Top18 전부를 S10/S11 DINO가 다시 판독
+
최종 probability를 70:30으로 결합
```

---

# 4. S11 — 완료된 실험

## 4.1 목적

S10의 Top18 selector와 center는 그대로 유지하면서 같은 병변 위치를 서로 다른 physical FOV로 읽는다.

View:

```text
DETAIL   = 110mm / 280
ANCHOR   = 130mm / 224
CONTEXT  = 160mm / 224
```

세 View는 별도 backbone이 아니라 **같은 DINOv2-Base weights를 공유**한다.

Target별 fixed routing은 logits에서 수행한다.

예:

```text
ACL              DETAIL .65 / ANCHOR .30 / CONTEXT .05
MCL              DETAIL .05 / ANCHOR .30 / CONTEXT .65
Medial Meniscus  DETAIL .60 / ANCHOR .35 / CONTEXT .05
Baker's          DETAIL .00 / ANCHOR .15 / CONTEXT .85
...
```

---

# 5. S11 cache / checkpoint 핵심

Multi-View cache:

```text
Pack00
/kaggle/input/datasets/woniyeon/s11-mv-cache-pack-00/
S11_MV_CACHE_PACK_00/multiview_top18_pack00.h5
SHA:
3d33e29478f2d2e58cb0d74fd1df9fcb63eecc9fbb27636005afc5347607cc17

Pack01
/kaggle/input/datasets/yhlucas/s11-mv-cache-pack-01/
S11_MV_CACHE_PACK_01/multiview_top18_pack01.h5
SHA:
4a39538c916fb3c63182d94aba318cd8f1dd594c98c044e1a5b5f79a1513b95b
```

전체:

```text
4407 Studies
79326 Top18 windows
Study overlap 0
Study 누락 0
각 Study 18 windows
ANCHOR = 기존 Native224 selected slice byte parity PASS
```

S11 LAST:

```text
Fold0 LAST SHA
2c962f22a1ebc55de81ee674c0f8e9b2c69001f028bc3db19dd6b114aa8f2dec

Fold1 LAST SHA
6647156f1bad9ed073b135ebea9c5bd4452d9483a17186c69a1dd04d22ae40bf
```

DEV:

```text
Fold0 LAST Gold29 AUC = 0.921638
Fold1 LAST Gold29 AUC = 0.864267

Pooled Gold58
Epoch1 = 0.892728
Epoch2/LAST = 0.887924
```

Local DEV에서는 Epoch1이 높았지만, 기존 DINO 계보에서 LAST가 Public LB에서 더 좋은 전례가 있었기 때문에 LAST를 실제 LB로 확인했다.

결과:

```text
S11 LAST 2F standalone Public LB = 0.926
```

S10 standalone 0.923 대비 **+0.003** 개선이다.

---

# 6. S11 현재 진행 중

현재 제출 중:

```text
0.70 × S11 LAST 2F
+
0.30 × S8C Full-MRI Direct 2F
```

Notebook:

```text
S11_LAST_70_S8C_DIRECT_30_2F_LB_SUBMISSION_V1.ipynb
```

SHA:

```text
1936890da1c28fa1e55fdaf3981cc07e71b2b2b651afbcb39b50c63068b5ff5d
```

Save Version:

```text
S11-LAST70-S8C30-LB-V1
```

정상 공식:

```text
P_S11
= mean(S11 F0 LAST prob, S11 F1 LAST prob)

P_S8C
= mean(S8C F0 Direct prob, S8C F1 Direct prob)

P_FINAL
= 0.70 * P_S11
+ 0.30 * P_S8C
```

**현재 상태: 제출 진행 중 / Public LB 대기.**

---

# 7. S11 70:30 결과가 나오면 다음 결정

## A. LB > 0.926

새 Branch-A main candidate로 승격한다.

예:

```text
0.927+
→ project best 갱신
```

그 다음:

- 무분별한 LB 비율 탐색은 하지 않는다.
- 필요성이 분명할 때만 인접 비율 1개 정도 추가 검토:
  - 80:20 또는
  - 60:40
- 개선이 작으면 70:30 그대로 동결.

## B. LB = 0.926

S11 standalone의 개선은 유효하지만 S8C 30%가 추가 gain을 주지 않은 것으로 본다.

Branch-A serving 후보:

- S11 standalone 0.926
- S10 70:S8C30 0.926

둘을 모두 보존한다.

향후 B/C와 ensemble할 때 correlation/diversity 관점에서 어느 A 예측을 사용할지 비교할 수 있다.

## C. LB < 0.926

S11 standalone 0.926 자체는 유지한다.

70:30 ratio를 여러 개 마구 제출하지 않는다.

Branch-A main은:

- S11 standalone 0.926
- 또는 S10 70:S8C30 0.926

으로 유지하고 Branch-B/C 다양성 확보를 우선한다.

---

# 8. Branch-B — CoAtNet Wide-MRI Expert

## 8.1 현재 실제 상태 — 매우 중요

**사용자는 `B_COATNET_WIDE96_2F_BASE_V3.ipynb`를 이미 실행했다. 현재 학습 진행 중이다.**

따라서:

```text
V3 TRAIN_RUNNING
```

으로 취급한다.

V3를 **임의로 중단하지 않는다.**

V4는 이후 audit에서 개선한 notebook이지만, 이미 정상 학습이 진행 중인 V3를 폐기하기 위한 이유가 아니다.

```text
V3 = 현재 실제 실행 중
V4 = 재실행 필요 시 / 다음 유사 실험에서 사용할 execution-hardening reference
```

V3 notebook:

```text
B_COATNET_WIDE96_2F_BASE_V3.ipynb
SHA:
bb3527a1c8b6fd6f6585295413420720d341ee4c61b8b04de25ca1ee5a6bf3f4
```

V4 prepared notebook:

```text
B_COATNET_WIDE96_2F_BASE_V4.ipynb
SHA:
45f77cd959d984577099b0a67f406b0e3f98296a4950d4b1a7dafeccc04f649f
```

---

# 9. Branch-B Base 학습 계약

## 9.1 2-Fold

DDP가 아니다.

```text
GPU0 → Fold0 independent model
GPU1 → Fold1 independent model
```

Fold0:

```text
Train:
V4 Broad pseudo 4349
+ Gold Fold1 29

Val:
Gold Fold0 29
```

Fold1:

```text
Train:
V4 Broad pseudo 4349
+ Gold Fold0 29

Val:
Gold Fold1 29
```

각 Fold train:

```text
4378 Studies
```

각 Fold validation:

```text
29 Gold
```

---

# 10. Branch-B label

Base supervision:

```text
/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/
rsna_knee_pseudolabels_v4_routed_broad.csv
```

SHA:

```text
93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c
```

중요:

- LABEL-V6 B Soft는 사용하지 않는다.
- LABEL-V6 계열은 실제 모델 실험에서 0.8대였고 V4가 우세했다.
- “최신 라벨”이 아니라 **실제 검증된 최고 supervision V4**를 사용한다.

Pseudo target:

```text
y = V4 soft label
weight = 0.25 + 0.75 × confidence
```

Gold train 29:

```text
binary BCE ×3
pseudo class balance 미적용
```

---

# 11. Branch-B class imbalance

세 단계로 처리한다.

## 11.1 V4 confidence weight

```text
0.25 + 0.75 × confidence
```

## 11.2 Target별 soft class balance

Pseudo 4349만 사용:

```text
P_t = Σ(w × y)
N_t = Σ(w × (1-y))
```

power:

```text
0.70
```

clip:

```text
0.5 ~ 2.5
```

target normalization 포함.

## 11.3 Rare-positive sampling

Strong positive:

```text
soft label >= 0.65
AND confidence >= 0.50
```

multiplier:

```text
MCL        3.0×
Fracture   2.5×
Contusion  2.0×
Baker's    1.5×
PF OA      1.5×
```

복수 질환이면 multiplier를 곱하지 않고 max 하나만 적용한다.

---

# 12. Branch-B pretrained CoAtNet

사용자가 Kaggle Input으로 추가한 모델:

```text
/kaggle/input/models/blueberry808/
coatnet-rmlp-2-rw-384-sw-in12k-ft-in1k/pytorch/default/1/
coatnet_rmlp_2_rw_384_sw_in12k_ft_in1k.pth
```

timm architecture:

```text
coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k
```

중요:

- 이것은 RSNA Knee로 미리 학습한 checkpoint가 아니다.
- ImageNet 계열 pretrained CoAtNet/timm initialization.
- Branch-B에서 Knee에 Full Fine-tuning.
- feature dim = **1024**
- random-init silent fallback 금지.

---

# 13. Branch-B Wide96 cache

고정 layout:

```text
S0 SAG_FLUID      26
S1 SAG_NONFLUID   22
S2 COR_FLUID      18
S3 COR_NONFLUID   12
S4 AXIAL_ANY      18
TOTAL             96
```

Per Study:

```text
volume      [96,384,384] uint8
valid_mask  [96] uint8
```

4 Pack:

```text
P00
/kaggle/input/datasets/yhlucas/b-coat-wide96-cache-pack-00/
B_COAT_WIDE96_CACHE_PACK_00/coat_wide96_native384_pack00.h5
SHA:
304028610a451f598255c6a18c07c4b531f8d9fdabb0fa265695c8a24d326c6f

P01
/kaggle/input/datasets/woniyeon/b-coat-wide96-cache-pack-01/
B_COAT_WIDE96_CACHE_PACK_01/coat_wide96_native384_pack01.h5
SHA:
1d8bc3003517ec34c7c1ba70b398a6525136f40ed12503c95bd6a5b6a5595eb1

P02
/kaggle/input/datasets/yhlucas/b-coat-wide96-cache-pack-02/
B_COAT_WIDE96_CACHE_PACK_02/coat_wide96_native384_pack02.h5
SHA:
ee49f1891c5d10e116d0b9ebab8e860ceddfa70639b3dfa959d5a3416c63be86

P03
/kaggle/input/datasets/woniyeon/b-coat-wide96-cache-pack-03/
B_COAT_WIDE96_CACHE_PACK_03/coat_wide96_native384_pack03.h5
SHA:
5f37b844659f5e3faa389f64c1b7194f2e3b71e7589cbe9378767ce3d7a4f2f1
```

전체 actual:

```text
4407 Studies
423072 logical positions
406966 valid slices
16106 structural missing
1241 Studies with >=1 missing slot
decode failure = 0
selected Series = 20792
all selected Series IOP_IPP ordered
~58.127 GiB
```

Global contracts:

```text
selected slot manifest SHA
2ae3c83c45c7efa46e393d0c23fb266850479830ebca329c3c74c19ff9165f5e

partition SHA
c934b45a305f8e3339a1934332ecd61b32de35160cd8fceb6206ed704752a55c
```

---

# 14. Branch-B architecture / training

Train:

```text
Wide96
→ stochastic 12 valid 3-slice windows / Study
→ 384→320
→ CoAtNet
→ 1024-d features
→ target-specific Window Attention
→ target-specific pooled features
→ 12 logits
```

Validation:

```text
dense 94 center positions
```

Hyperparameter:

```text
Epoch          16 fixed
Backbone LR    4e-5
Head LR        2e-3
WD             .06
Warmup         5%
Scheduler      cosine
FP16
Grad clip      5.0
Effective Study batch / Fold = 16
```

Physical Study Batch:

```text
4 → 2 → 1 benchmark
```

V3 checkpoint policy:

```text
fold0/best.pt
fold1/best.pt
```

기준:

```text
own Gold29 Macro AUROC
```

Base에서는 best 하나만 남긴다.

---

# 15. Branch-B V3 실행 관련 주의

V3 audit에서 발견된 사항:

1. resource probe가 실제 384 HDF5 path보다 가벼운 synthetic 320 probe였음.
2. activation checkpoint와 BN double-update를 막기 위해 BN running stats를 고정하는 구현이 포함됨.
3. 128 real Study runtime projection이 없음.

하지만 이것들은:

- Fold 누수
- label 오류
- cache mapping 오류
- 잘못된 모델
- loss 붕괴

같은 실험 무효 사유는 아니다.

따라서 **이미 V3 actual training loop가 정상 진행 중이면 중단하지 않는다.**

V4는 위 세 점을 개선했다.

---

# 16. Branch-B Base 결과가 나오면 해야 할 작업

## Step B1 — 결과 검증

사용자가 제공해야 하는 것:

- Kaggle 전체 console log
- Fold0/1 training summary
- Fold0/1 best checkpoint
- training history
- Gold29 metric
- review ZIP이 있으면 같이

확인:

```text
Fold0/1 모두 완료?
best epoch?
Gold29 Macro AUROC?
checkpoint SHA?
NaN/OOM/rescue?
실제 physical Study batch?
실제 runtime?
```

V3가 마지막 packaging에서만 실패했다면 먼저 artifact recovery를 시도한다.
이미 완료된 GPU 학습을 곧바로 다시 돌리지 않는다.

---

# 17. Branch-B Base standalone 제출

Base 완료 후 첫 submission:

```text
P_B_BASE
= 0.5 * sigmoid(Fold0 best)
+ 0.5 * sigmoid(Fold1 best)
```

Standalone Public LB 확인.

이 점수는 반드시 기록한다.

목적:

- CoAtNet Wide96 자체 성능 확인
- DINO A와 독립적으로 쓸 가치 확인
- Strict FT 전 baseline 고정

---

# 18. Branch-B 다음 단계 — V4 Strict 고신뢰 FT

사용자 결정:

**Base Broad 학습 후 V4 Strict 고신뢰 라벨로 한 번 더 Fine-tuning하고 Public LB를 확인한다.**

권장 구조는 DINO Stage1 Broad→Strict FT 방식과 대응시킨다.

```text
CoAtNet Base Fold0 best
→ V4 Strict FT Fold0

CoAtNet Base Fold1 best
→ V4 Strict FT Fold1
```

Fold는 유지:

```text
Fold0 train = V4 Strict + opposite Gold29
Fold0 val   = own Gold29

Fold1 train = V4 Strict + opposite Gold29
Fold1 val   = own Gold29
```

### 중요한 checkpoint 정책

Base와 달리 Strict FT에서는 **best와 last를 둘 다 보존하는 방향을 우선 검토**한다.

이유:

DINO 계보에서:

```text
local Gold best보다
last가 Public LB에서 더 좋았던 사례가 있음
```

따라서 Strict FT에서:

```text
best.pt
last.pt
```

둘 다 남겨놓고,

- local Gold
- standalone Public LB

를 함께 본다.

**단, 정확한 FT LR / epoch / freeze 여부 / augmentation / batch는 Base 결과를 본 뒤 다음 채팅에서 설계를 확정한다.**
지금 임의로 Notebook을 만들지 않는다.

---

# 19. Branch-B Strict FT 제출 순서

권장:

1. Base best 2F standalone LB
2. Strict FT `last` 2F standalone LB
3. 필요하면 Strict FT `best` 2F standalone LB
4. B 내부 serving candidate 결정

DINO precedent 때문에 first FT submission은 `last`를 우선 후보로 둘 수 있으나,
Base 학습 결과와 FT train curve를 확인한 뒤 최종 결정한다.

---

# 20. Branch-A + Branch-B ensemble

Branch-B standalone/Strict FT 결과가 나온 다음 수행한다.

A candidate는 그 시점 Branch-A 최고 결과 사용:

- S11 standalone 0.926- 또는 S11 70:S8C30 결과가 더 좋으면 그것
- 필요 시 S10 70:S8C30 0.926도 diversity reference로 유지

B candidate:

- Base best
- 또는 Strict FT last/best 중 Public LB가 좋은 모델

### 1차 ensemble

Branch 간 calibration 차이가 크므로 **per-target percentile rank blend**를 우선한다.

```text
R_A[t] = percentile_rank(A[t])
R_B[t] = percentile_rank(B[t])

Final[t] = wA * R_A[t] + wB * R_B[t]
```

처음부터 target별 복잡한 weight tuning을 하지 않는다.

global fixed weight 후보를 적게 비교한다.

예:

```text
A:B = 70:30
A:B = 60:40
```

Standalone score가 낮더라도 A/B prediction correlation이 낮으면 ensemble 가치가 있을 수 있다.

반드시 기록:

- standalone LB
- A/B global correlation
- target별 rank correlation
- ensemble LB gain

---

# 21. Branch-B optional 후속

Base/Strict/A+B가 끝난 뒤만 검토:

- anatomical mirror TTA
- plain vs mirror
- medial/lateral swap-back
- target-specific TTA exceptions

처음부터 Branch-B core 결과와 TTA를 섞지 않는다.

---

# 22. Branch-C — ConvNeXt Anatomy Expert

## 현재 상태

기존 Git 상태:

```text
C-DESIGN-V1
NOT_RUN
```

그러나 기존 문서는 **바로 실행하기 위한 최종 동결본으로 취급하지 않는다.**

현재 문서에는 다음 오래된 가정이 남아 있었다.

- “latest B soft label”
- single full-data model
- Branch-B 완료 후에만 시작

이제 사용자 결정은:

```text
Branch-B 학습 / S11 제출을 기다리는 동안
Branch-C 상세 설계를 먼저 진행
```

이다.

따라서 다음 채팅의 제1 작업:

**Branch-C C-DESIGN-V1을 현재 A/B에서 얻은 교훈에 맞게 재설계하고 C-DESIGN-V2를 확정한다.**

---

# 23. Branch-C 역할

Branch-C는 DINO/CoAtNet의 단순 backbone 교체가 아니다.

핵심:

```text
Full FOV
+
100mm anatomy-centered local view
+
target-specific spatial attention
+
target-specific Window MIL
+
ConvNeXt CNN inductive bias
```

목적:

- A의 Top18 selector 의존성 없음
- B의 fixed 96-slot MIL과도 다른 표현
- Window 안에서 병변 위치를 spatial attention으로 고름
- Study 안에서 중요한 Window를 MIL attention으로 다시 고름

즉 two-level selection:

```text
feature map spatial attention
        ↓
target-specific window feature
        ↓
window MIL attention
        ↓
prediction
```

---

# 24. Branch-C 현재 draft의 핵심 설계

## Input view

현재 V1 draft:

```text
Sagittal:
Full FOV
+ 100mm joint-local

Axial:
Full FOV
+ 100mm joint-local

Coronal:
Full FOV
+ 100mm medial-local
+ 100mm lateral-local
```

추가 후보:

```text
PF local
posterior/Baker local
```

하지만 V1에서 무조건 모두 넣는 것은 아니다.

---

# 25. Branch-C thin-stack 처리

Series physical spacing:

```text
median slice spacing
```

thin stack gate:

```text
0 < spacing < 1.75mm
```

이면:

```text
target slab ≈ 3.5mm

group_size
= round(3.5 / spacing)

인접 slice average
```

목적:

0.4~1.5mm 3D acquisition의 비슷한 slice가 64-window budget을 독식하지 않게 한다.

---

# 26. Branch-C anatomy anchor

현재 draft는 단순 center crop만 쓰지 않는다.

Primary:

```text
label-free knee anatomy anchor
→ joint center
→ patella reference
→ DICOM world geometry로 각 Series projection
```

Fallback:

```text
segmentation / anchor
→ orthogonal geometry prior
→ field center
```

중요:

**anchor artifact가 실제로 확보되지 않았는데 임의 center crop으로 축소하여 “Branch-C”라고 부르지 않는다.**

다음 채팅에서 반드시 확인:

- exact checkpoint
- source
- license
- SHA
- Kaggle offline mount 가능 여부
- 실제 inference code
- geometry coordinate convention

---

# 27. Branch-C model draft

Backbone:

```text
timm ConvNeXt-Small
ImageNet pretrained
Full Fine-tuning
```

하지만 exact timm model name / checkpoint는 아직 확정 전.

Spatial attention:

```text
ConvNeXt final feature map
[B,C,H,W]

→ target-specific spatial logits
[B,12,H,W]

→ spatial softmax
→ target별 pooled feature
```

Window MIL:

```text
64 target-specific window features
+
metadata embedding

→ target-specific window attention
→ 12 pooled features
→ 12 logits
```

Metadata 후보:

- plane
- view
- relative position
- log spacing
- fluid-sensitive
- fat-suppression

V1 원칙:

metadata는 attention 보조 신호로 사용하고 classifier feature에 직접 무겁게 concatenate하지 않는다.

---

# 28. Branch-C current draft window budget

```text
64 windows / Study
```

초기 quota:

```text
Global ≈ 32
Local  ≈ 32
```

배분:

1. valid Series 최소 1
2. 모든 plane
3. 모든 view
4. 남은 budget을 slice/span 비례
5. relative position stratified

S8C contribution/Top18 사용 금지.

---

# 29. Branch-C current draft preprocessing

Cache:

```text
320×320 uint8
```

Train:

```text
320 → random crop 288
```

Inference:

```text
320 → center crop 288
```

Augmentation draft:

```text
Rotation ±10°
Scale .90–1.10
Gamma .80–1.25
Gain .90–1.10

resolution degradation p=.25
downsample factor 1.25~2.0
→ upsample back
```

금지:

- generic flip
- MixUp
- CutMix
- Random Erasing
- arbitrary strong blur

Mirror는 inference TTA로 분리.

---

# 30. Branch-C label 정책 — 다음 채팅에서 반드시 수정할 부분

기존 문서의 “latest B soft-label dataset”은 폐기해야 한다.

현재 evidence:

```text
LABEL-V6 soft 계열 < V4
```

이므로 Branch-C Base의 1차 supervision은 **V4 Routed Broad를 우선 기준으로 재설계**한다.

후속:

```text
V4 Broad Base
→ V4 Strict high-confidence FT
```

방식이 Branch-C에도 유효한지 다음 채팅에서 결정한다.

다음 채팅에서 확정할 사항:

- Base = V4 Broad인가? → 현재 우선 YES
- Strict FT를 하는가? → 우선 검토 YES
- 2-Fold인가?
- single full-data인가?
- Fold split은 A/B와 동일 Gold29/29인가?
- Base checkpoint best-only인가?
- FT에서 best+last 보존할 것인가?

**기존 single full-data C plan을 자동으로 실행하지 않는다.**

Branch-B에서 사용자가 2-Fold를 명시적으로 선호했고,
Branch-C도 standalone 성능과 FT 비교를 정확히 보려면 2-Fold의 장점이 크므로 다음 채팅에서 다시 결정한다.

---

# 31. Branch-C class imbalance

Branch-C도 A/B와 동일한 기본 철학을 우선 검토한다.

V4 Broad:

```text
confidence weight
= 0.25 + 0.75 × confidence
```

Soft class balance:

```text
power .70
clip .5~2.5
```

Rare-positive sampling:

```text
MCL        3.0×
Fracture   2.5×
Contusion  2.0×
Baker's    1.5×
PF OA      1.5×
```

strong positive:

```text
y >= .65
confidence >= .50
```

다만 C spatial/window attention이 rare-positive sampling에 얼마나 민감한지는 설계 시 다시 검토한다.

---

# 32. Branch-C 기존 hyperparameter draft — 아직 확정 아님

기존 C-DESIGN-V1:

```text
Epoch              16
Windows            64 / Study
Physical batch     2 target
Effective batch    2
Backbone LR        1e-4
Spatial/MIL LR     1e-3
WD                 .05
Warmup             5%
Cosine
FP16
Clip               5.0
Seed               42
```

이 값들을 바로 사용하지 않는다.

다음 채팅에서:

- reference implementation
- ConvNeXt parameter count
- input 288
- 64 windows
- target-specific spatial feature cost
- T4×2 VRAM

을 기반으로 재검증한다.

---

# 33. Branch-C GPU 설계 규칙 — 매우 중요

프로젝트의 mandatory GPU policy를 따른다.

과거 사용자 실측:

```text
Batch 124 이상 가능했던 경험
VRAM 여유 경험
```

이 기록을 무시하고 보수적으로 microbatch를 1/2/4에 고정하면 안 된다.

다만 다른 architecture이므로 같은 batch가 된다고 가정하지도 않는다.

신규 C에서 실제 benchmark:

```text
Window microbatch:
가능한 큰 값 적극 탐색
예: 16 / 32 / 64 / 96 / 124 / 128+

Physical Study batch:
1 / 2 / 4 / 8 가능 범위 실측
```

필수 benchmark:

- real cached Study
- Full Forward
- Backward
- AdamW optimizer step
- AMP
- 실제 augmentation
- I/O
- peak allocated/reserved
- Studies/s
- Windows/s

목표:

```text
1 run 4시간 이내
```

예상:

```text
>4h → 최적화 후 재측정
>=8h → Full TRAIN 시작 금지
```

Window microbatch 1 금지.

---

# 34. Branch-C cache 규칙

캐시 생성은 CPU-only.

GPU training notebook에서 raw DICOM 대규모 decode를 하지 않는다.

순서:

```text
CPU Preflight
→ row/view count
→ exact byte budget
→ pack partition
→ CPU cache build
→ readback
→ SHA
→ Kaggle Dataset 등록
→ GPU training
```

Kaggle project output safety:

```text
/kaggle/working 총 output
14.0GB decimal 이하 권장
physical reserve >= 2GB
```

Pack당 목표:

```text
raw pixel ~15~17GB 이하
```

그러나 14GB project rule과 충돌하지 않도록 실제 cache 설계에서는 더 안전한 pack 크기를 다시 계산한다.

압축에 기대서 한 Pack에 억지로 넣지 않는다.

---

# 35. Branch-C reference material

다음 채팅에서 프로젝트 Files / 기존 업로드 자료를 우선 검색한다.

특히 기존 source bundle에 다음 계보가 있다.

## ConvNeXt R6 / high-score reference

프로젝트에 업로드된 source bundle에서 확인된 요소:

```text
compact_train.py
compact_infer.py
knee_anchor_bank_v2.py
side_common.py
```

또한 high-score ensemble source에서:

```text
our compact ConvNeXt-small model R6
4 fold models
mean logit
flip TTA
Effusion fluid state stacker
Baker's state stacker
```

사용 사례가 있다.

Input/view reference:

- Full FOV
- local views
- coronal bilateral local
- knee anchor
- thin stack slab
- ConvNeXt-small
- target-specific spatial + window reasoning 계보

다음 채팅에서는 이 자료를 실제 코드 단위로 다시 뜯어서 **우리 C-DESIGN-V2에 무엇을 채택하고 무엇을 버릴지** 정한다.

## CoAtNet/Raptor reference

같은 bundle에서:

```text
raptor_infer1_dense96_fast.py
raptor_infer1_dense80_fast.py
rsna-knee-0949-anatomical-mirror.ipynb
```

은 Branch-B와 inference robustness reference로 사용한다.

---

# 36. Branch-C 다음 채팅 상세 설계 TODO

순서대로 진행한다.

## C1. Reference code audit

확인:

- exact ConvNeXt timm model name
- pretrained source/checkpoint
- feature map shape
- R6 training resolution
- 4-fold 구성
- view cache format
- window count
- spatial attention implementation
- MIL implementation
- metadata usage
- thin-stack implementation
- anchor implementation
- Effusion/Baker stacker는 core인지 후속인지

## C2. 우리 데이터에 맞게 단순화/독립성 결정

목표:

```text
고득점 reference의 유효한 아이디어
≠ 코드를 무작정 그대로 복제
```

A/B와 중복되지 않는 C core를 고정한다.

## C3. Label/fold policy 확정

최우선 논의:

```text
V4 Broad Base 2F?
→ V4 Strict FT 2F?
```

Gold58:

```text
Fold0/1 = 기존 frozen 29/29 재사용 여부
```

## C4. Anatomy anchor artifact 확정

artifact가 없으면 cache notebook 생성 금지.

## C5. View set 확정

V1 draft:

```text
Sag full + joint-local
Axial full + joint-local
Cor full + medial + lateral
```

PF/posterior local을 V1에 포함할지 결정.

## C6. Cache resolution/row budget 확정

```text
320 render
288 model
64 windows/Study
```

가 실제 optimal인지 reference와 storage를 보고 결정.

## C7. Model/head architecture 확정

- ConvNeXt-small
- spatial attention
- MIL attention
- metadata embedding
- classifier

## C8. GPU benchmark contract 확정

작은 batch를 임의 고정하지 않는다.

## C9. CPU preflight notebook 생성

모든 설계가 동결된 뒤 생성한다.

---

# 37. Branch-C 결과가 나온 뒤 진행 순서

Branch-C도 동일하게 단계적으로 검증한다.

1. C Base standalone
2. V4 Strict FT를 채택했다면 C Strict standalone
3. mirror TTA
4. A+C
5. B+C correlation
6. A+B+C

초기 final heuristic은 기존 문서에:

```text
A 0.50
B 0.30
C 0.20
```

이 있었지만 **확정 weight가 아니다.**

Standalone LB와 correlation을 보고 결정한다.

우선:

```text
per-target percentile-rank ensemble
```

을 본다.

---

# 38. 현재 Branch별 Pending

## Branch-A

```text
S11 LAST 70 + S8C Direct 30
Public LB 대기
```

## Branch-B

```text
CoAtNet Wide96 V3
2-Fold Base
현재 TRAIN_RUNNING
```

## Branch-C

```text
NOT_RUN
다음 채팅에서 상세 설계 재검토 / C-DESIGN-V2 확정
```

---

# 39. 진행 중 결과가 들어오면 처리하는 방식

새 채팅에서 Branch-C 설계를 진행하다 사용자가 결과를 보내면 즉시 그 결과를 우선 반영하고 다시 C 설계로 돌아간다.

## S11 결과가 오면

Public LB를 DINO_S log + CURRENT_HANDOFF에 기록.

Branch-A main 후보 갱신.

## Branch-B 학습 결과가 오면

CoAtNet EXPERIMENT_LOG에:

- actual resource profile
- Fold best epoch
- Gold29 AUC
- checkpoint SHA
- runtime

기록.

그 뒤:

```text
B Base standalone submission notebook
```

생성.

LB 나온 후:

```text
B V4 Strict FT 설계
```

진행.

---

# 40. Kaggle Notebook 제작 방식

모든 Notebook은 사용자가 **Save & Run All**로 실행 가능해야 한다.

첫 Markdown에 반드시:

- experiment ID
- 목적
- 변경 변수
- 고정 변수
- GPU/CPU
- required Add Input
- exact path
- known SHA
- Save Version 추천 (<60 chars)
- output artifacts
- 예상/실측 runtime gate

코드:

- source <1MB
- 모든 code cell AST 검증
- embedded worker가 있으면 compile 검증
- exact path/SHA gate
- silent fallback 금지
- target order assert
- label universe assert
- Gold leakage assert
- actual GPU count assert
- output atomic save
- checkpoint SHA
- review ZIP은 대용량 모델/cache를 복제하지 않음

---

# 41. CPU / GPU 분리

CPU Notebook:

- DICOM decode
- geometry
- cache
- metadata
- manifest
- SHA
- montage/QA

GPU Notebook:

- persisted cache load
- training
- evaluation
- checkpoint

GPU가 raw DICOM cache 생성 대기 때문에 idle 상태로 오래 남지 않게 한다.

---

# 42. T4×2 independent Fold rule

2-Fold일 경우 기본:

```text
physical GPU0
→ subprocess Fold0

physical GPU1
→ subprocess Fold1
```

각 subprocess:

```text
CUDA_VISIBLE_DEVICES=0
CUDA_VISIBLE_DEVICES=1
```

worker 내부에서는 각각 `cuda:0`으로 보이는 것이 정상.

필수:

- lane별 log
- return code
- summary
- one Fold fail 시 other Fold artifact 보존
- main aggregation 전 두 상태 확인

DDP와 혼동하지 않는다.

---

# 43. 문서 기록 방식

실험 결과는 개별 새 문서를 매번 만들지 않고 각 Branch cumulative 문서에 누적한다.

## Branch-A

```text
docs/DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md
docs/DINO_S/S1-DINO-CBL2F-01_ROADMAP.md
docs/DINO_S/S1-DINO-CBL2F-01_DATA_MODEL.md
```

## Branch-B

```text
docs/COATNET/COATNET_BRANCH_PLAN.md
docs/COATNET/COATNET_EXPERIMENT_LOG.md
docs/COATNET/README.md
```

## Branch-C

```text
docs/CONVNEXT/CONVNEXT_BRANCH_PLAN.md
docs/CONVNEXT/CONVNEXT_EXPERIMENT_LOG.md
docs/CONVNEXT/README.md
```

공통 cold-start:

```text
docs/CURRENT_HANDOFF.md
```

공통 Notebook 운영:

```text
docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md
docs/GPU_BATCH_RESOURCE_MANDATORY_POLICY.md
```

---

# 44. Git에 무엇을 기록하고 무엇을 기록하지 않는가

기록:

- 실제 완료 실험
- Public LB
- checkpoint SHA
- cache SHA
- 실제 runtime
- 실제 batch
- scientific decision
- 현재 상태
- 다음 단계

기록하지 않음:

- 사소한 AssertionError
- 코드 typo 수정 과정
- 임시 debug chronology
- 실행 전 추정값을 완료 결과처럼 기록

예외:

데이터 오염/평가 신뢰/재현성에 영향을 주는 문제는 최종 판정 중심으로 기록한다.

---

# 45. 다음 새 채팅에서 사용할 시작 프롬프트

아래 문장을 새 채팅 첫 메시지로 사용할 수 있다.

```text
RSNA Knee 프로젝트를 이어서 진행하자.

GitHub:
https://github.com/dudghks5893/RSNA-Knee-Abnormality-Detection

가장 먼저 아래 문서를 읽어.
1. docs/RSNA_KNEE_BRANCH_C_START_HANDOFF_2026-10-18.md
2. docs/CURRENT_HANDOFF.md
3. docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md
4. docs/GPU_BATCH_RESOURCE_MANDATORY_POLICY.md
5. docs/CONVNEXT/CONVNEXT_BRANCH_PLAN.md
6. docs/CONVNEXT/CONVNEXT_EXPERIMENT_LOG.md
7. docs/COATNET/COATNET_BRANCH_PLAN.md
8. docs/DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md

현재 상황:
- Branch-A S11 LAST standalone Public LB = 0.926.
- S11 LAST 70% + S8C Direct 30% 제출은 진행 중이며 LB 대기.
- Branch-B CoAtNet Wide96 Base V3 2-Fold가 이미 Kaggle에서 학습 중이다. V4가 있다고 V3를 중단하지 마.
- Branch-B Base가 끝나면 2F standalone LB → V4 Strict 고신뢰 FT → standalone LB → Branch-A와 ensemble 순서로 진행한다.
- Branch-C는 아직 NOT_RUN이며, 현재 진행 중 결과를 기다리는 동안 Branch-C 상세 설계를 먼저 진행한다.
- 기존 Branch-C 문서는 오래된 single full-data/latest-B-soft-label 가정이 일부 남아 있으므로 그대로 training notebook을 만들지 말고 C-DESIGN-V2를 먼저 확정한다.
- Branch-C에서는 ConvNeXt high-score reference, anatomy anchor, Global+Local view, thin-stack 3.5mm slab, target-specific spatial attention + Window MIL을 다시 코드 기준으로 검토한다.
- Branch-C supervision은 V4 Broad Base와 V4 Strict FT 구조를 우선 검토하고, 2-Fold 여부도 Branch-B/DINO 경험을 반영해 다시 결정한다.
- Notebook은 Save & Run All, exact path/SHA, T4×2 자원 벤치마크, 4시간 runtime gate, microbatch=1 금지, CPU cache/GPU train 분리 규칙을 반드시 지켜라.

첫 작업:
현재 기다리는 S11/Branch-B 결과는 건드리지 말고 Branch-C C-DESIGN-V2 상세 설계를 시작해.
먼저 reference code에서 실제 ConvNeXt backbone, view/cache, anatomy anchor, spatial attention, MIL, fold/train 설정을 추출해서 기존 C-DESIGN-V1과 비교하고 어떤 부분을 채택/수정할지 제안해.
```
---

# 46. 최종 요약

현재:

```text
A:
S11 standalone 0.926 COMPLETE
S11 70:S8C30 SUBMISSION_RUNNING

B:
CoAtNet Wide96 Base V3 2F TRAIN_RUNNING
→ 완료 후 standalone
→ Strict FT
→ standalone
→ A+B ensemble

C:
NOT_RUN
→ 지금 바로 detailed design refinement 시작
→ C-DESIGN-V2 freeze
→ CPU cache preflight
→ cache build
→ Base
→ Strict FT 여부
→ standalone
→ TTA
→ A+C / A+B+C
```

다음 채팅의 핵심은 **Branch-C를 성급히 실행하는 것이 아니라, 현재까지 A/B에서 얻은 evidence와 고득점 ConvNeXt reference를 바탕으로 C-DESIGN-V2를 먼저 제대로 확정하는 것**이다.