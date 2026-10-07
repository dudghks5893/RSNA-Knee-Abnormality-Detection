# RSNA Knee — 3D ResNet Experiment Plan

최종 업데이트: **2026-10-08**

상태: **R3D-10AB 완료 / Dual-FOV 기각 / Crop130 single-view Main 유지**

이 문서는 **앞으로 무엇을 할지**를 기록한다.
완료 결과는 [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md)에 기록하고,
현재 기준점은 [CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md](CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md)를 따른다.

Kaggle Notebook 작성/복구 규칙:
[AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)

---

# 1. 최종 목표

기존 Exp57 Public LB **0.918**을 기준점으로 유지하면서,
독립적인 3D MRI 계보의 실제 hidden-test 성능과 Exp57과의 상보성을 확인한다.

R3D의 성공 기준은 내부 Gold58 점수만이 아니다.

최종적으로 확인해야 할 것은:

1. R3D standalone Public LB
2. Exp57 대비 차이
3. Exp57 + R3D ensemble의 net gain
4. Medial Meniscus Sag1 specialist가 target-specific 보완에 실제 기여하는지

---

# 2. 현재 확정 Main R3D

~~~text
ALL Series
→ 130 mm physical center crop
→ interpolated D24 × 96 × 96
→ MedicalNet R34
→ GLOB token / series
→ metadata embedding
→ Transformer + shared CLS
→ 12 independent sigmoid heads
~~~

고정:

- Backbone: **MedicalNet R34**
- R50 / R101 재비교 없음
- Full fine-tuning
- pure FP32
- BN running stats frozen
- Series = **ALL**
- Crop = **130 mm**
- Depth = **interpolated D24**
- In-plane = **96×96**
- Representation = **GLOB**
- Anatomy mask = **OFF**
- Backbone LR = **1e-5**
- New-layer LR = **5e-5**
- WD = **1e-4**
- Transformer:
  - d_model 512
  - 2 layers
  - 8 heads
  - FFN 2048
  - dropout 0.10
  - Pre-LN
  - learnable CLS

현재 구조를 다시 흔드는 micro-search는 중단한다.

---

# 3. 완료된 decision gates

## Backbone

- R34 pooled Macro AUROC: 0.567267
- R50: 0.533494
- R101: 0.510364
- **R34 selected**

## Representation

- GLOB: 0.601827
- SPT27: 0.595809
- SPT48: 0.590426
- **GLOB selected**

## Backbone LR

- 1e-5: 0.601827
- 5e-6: 0.591677
- 3e-6: 0.582062
- frozen: 0.579953
- **1e-5 selected**

## Anatomy mask

- MASK_ON: 0.601827
- MASK_OFF: 0.609698
- **MASK_OFF selected**

## Series

3-Fold mean AUROC:
- P2 0.573140
- P3 0.589716
- ALL **0.596226**
- **ALL selected**

## Physical FOV

Crop130 3-Fold:
- mean ΔAUROC vs Full = **+0.010751**
- mean ΔAUPRC = **+0.003722**
- **Crop130 selected**

## Depth / detail

Rejected:
- R128
- simple D32 interpolation
- REAL24 nearest actual-slice
- REAL32 nearest actual-slice

Depth representation:
- **interpolated D24 유지**

## Dual-FOV

R3D-10AB Fold0:
- Frozen Crop130 0.622257
- Frozen Full 0.617594
- Always Dual 0.609809
- Mixed3 Dual 0.610704

결론:
- **Dual-FOV current fusion reject**
- Fold1/Fold2 confirmation 없음
- Crop130 single-view 유지

---

# 4. 다음 prerequisite — R3D-11CACHE

## 목적

Medial Meniscus specialist를 3-Fold paired confirmation하기 전에
Crop130 cache를 한 mounted Dataset으로 정리한다.

현재 stable Crop130 root:

`/kaggle/input/datasets/yhlucas/rsna-knee-r3d-crop130-search-cache-v3/crop130_d24_96`

현재 확인된 scope:
- 1,058 studies
- Fold0 Gold + Fold0 Pseudo1000 중심

R3D-09 Fold1/Fold2에서는
별도 delta cache를 함께 사용했다.

따라서 R3D-11 전에:

~~~text
Fold0 base Crop130
+
Fold1/Fold2 missing-study Crop130 delta
        ↓
single canonical Crop130 search Dataset
~~~

으로 정리한다.

## 원칙

우선순위:

1. 기존 base/delta artifact를 파일 수준으로 합쳐 재사용
2. 기존 artifact가 불완전할 때만 missing studies CPU build
3. raw DICOM 전체 재decode는 마지막 수단

Runtime:
- **CPU only**
- GPU 예약 금지

Contract:

- Gold58 coverage
- F0 Pseudo1000 coverage
- F1 Pseudo1000 coverage
- F2 Pseudo1000 coverage
- Full-FOV metadata와 Study/Series UID exact parity
- volume shard existence
- row_in_shard valid
- crop = 130 mm
- target shape = D24×96×96
- decode failure = 0 if any new build occurred

Output은 가능한 한:
- 하나의 Dataset slug
- 하나의 active Version
- exact mounted root

로 고정한다.

같은 Dataset의 여러 Version을 동시에 mount하는 설계는 금지한다.

---

# 5. R3D-11 — Medial Meniscus Sag1 Canonical Confirmation

상태: **NEXT AFTER R3D-11CACHE**

## 배경

R3D-06H Fold0에서:

- P2 binary specialist: 0.677083 / 0.591098
- Sag1-only binary specialist: **0.729167 / 0.756302**
- ΔAUROC **+0.052083**
- ΔAUPRC **+0.165204**

강한 신호였지만:

- 현재 Main input Crop130 이전 실험
- final canonical R34 contract와 완전히 동일하지 않은 구현 흔적이 있음
- 따라서 최종 ensemble에 쓰기 전 재확인이 필요

## 새로운 paired design

Target:
- **Medial Meniscus only**

Control:

~~~text
Crop130
+ ALL Series
+ canonical R34
+ binary Medial Meniscus head
~~~

Candidate:

~~~text
Crop130
+ Sagittal plane_rank=1 only
+ same canonical R34
+ same binary Medial Meniscus head
~~~

중요:

기존 P2 control이 아니라
**현재 Main policy와 직접 비교 가능한 ALL control**을 사용한다.

## Validation

가능하면 3-Fold paired confirmation:

- F0
- F1
- F2

Gold split은 현재 R3D Gold58 그대로 유지.

각 Fold:

- training-side Gold
- 해당 fold Pseudo1000
- held-out Gold validation
- ALL / Sag1 pair는 같은 Study sampling trace
- same initial model state
- same optimizer
- same augmentation RNG
- same epochs
- only Series policy changes

## Primary metric

- **Gold58 pooled OOF Medial Meniscus AUROC**

Secondary:

- pooled AUPRC
- Fold별 AUROC
- Fold별 AUPRC
- stability / failure pattern

## Gate

Sag1-only candidate 유지:

- pooled AUROC가 ALL control보다 명확히 우세
- AUPRC도 치명적으로 악화되지 않음
- 특정 Fold에서 catastrophic collapse 없음

그렇지 않으면:

- Medial Meniscus specialist routing 종료
- final R3D는 12-target Main만 사용

---

# 6. R3D-12 — Main Final Training Policy Decision

R3D-11 뒤 반드시 사용자와 먼저 결정한다.

미결정 항목:

- final train에서 Pseudo1000 유지 여부
- report-only pseudo를 더 확장할지
- samples/epoch
- epochs
- checkpoint policy
- training compute budget
- 기존 search checkpoint 재사용 / fresh final training 여부

금지:

**Search가 Pseudo1000이었다는 이유만으로 final도 자동 Pseudo1000로 확정하지 않는다.**

반대로:

**Final이니까 자동으로 4,349 pseudo 전체를 쓰지도 않는다.**

data scope 변경은 성능에 큰 영향을 주는 독립 변수다.
사용자와 명시적으로 결정하고 문서화한 뒤 실행한다.

---

# 7. R3D-13 — Final Main 3-Fold

확정 architecture:

- Crop130
- ALL
- interpolated D24×96×96
- MedicalNet R34
- GLOB
- MASK_OFF
- Transformer + shared CLS
- 12 heads

필수 artifact:

- Fold0 best checkpoint + SHA
- Fold1 best checkpoint + SHA
- Fold2 best checkpoint + SHA
- fold validation predictions
- pooled Gold58 OOF predictions
- pooled target metrics
- exact train/val manifests
- training config
- runtime / GPU summary

이 단계에서는 search용 baseline을 다시 비교하지 않는다.

---

# 8. R3D-14 — Hidden-Test Standalone Submission

Exp57과 섞기 전에 R3D standalone을 먼저 제출한다.

목적:

- R3D 자체 hidden-test generalization 측정
- internal Gold58 ↔ Public LB gap 확인
- Exp57 complementarity와 standalone 성능을 분리

기본 inference:

~~~text
Hidden Study
→ all usable Series
→ 130 mm physical crop
→ interpolated D24×96×96
→ Fold0 R34
→ Fold1 R34
→ Fold2 R34
→ probability mean
→ submission.csv
~~~

정확한 fold ensemble은 R3D-12 final policy에서 확정한다.

---

# 9. R3D-15 — Final Ensemble

입력 후보:

1. **Exp57** — Public LB 0.918
2. **R3D final 3-Fold**
3. **Medial Meniscus Sag1 specialist** — R3D-11 PASS 시에만

Exp57은:

- 3-Fold B3A
- 3-Fold Full-MRI Direct
- 70:30

으로 이미 완성된 강한 baseline이다.

R3D는 Exp57과 architecture / representation이 다르므로
standalone이 약간 낮아도 ensemble value가 있을 수 있다.

실행 전 가능하면:

- prediction correlation
- target별 delta
- ranking disagreement
- especially weak target behavior

를 먼저 확인한다.

Public LB에 ratio를 반복적으로 맞추는 식의 micro-search는 하지 않는다.

---

# 10. Closed experiments

새 evidence가 생기기 전에는 재오픈하지 않는다.

- R50 / R101
- spatial token SPT27 / SPT48
- current anatomy mask fusion
- lower LR / frozen R34
- Series cap P2/P3/P4
- Synovitis Sag1-only
- Crop150 / 140 mm micro-search
- R128 이상 단순 resolution search
- simple D32+ interpolation
- REAL24 / REAL32 nearest actual-slice
- Full+Crop Always Dual
- Full/Crop Mixed3
- R3D-10AB Fold1/Fold2

---

# 11. Resource execution plan

## CPU lane

사용:
- DICOM decode
- cache generation
- cache consolidation
- manifest / policy audit
- SHA / parity validation

금지:
- CPU preprocessing 때문에 T4를 예약해 두는 구조

## GPU lane

사용:
- training
- validation
- model inference

새 image/cache generation을 GPU notebook에 넣지 않는다.

## T4×2

한 Kaggle session에서 독립 lane을 병렬 실행할 수 있으면:

~~~text
GPU0 → experiment/fold lane 1
GPU1 → experiment/fold lane 2
~~~

subprocess + `CUDA_VISIBLE_DEVICES` 방식 사용 가능.

두 Kaggle 계정을 쓰는 것보다
같은 Input을 공유해야 하는 경우 한 계정 T4×2가 더 편하면
한 세션 병렬을 우선할 수 있다.

---

# 12. Experiment numbering going forward

- **R3D-11CACHE** — consolidated Crop130 3-Fold cache
- **R3D-11** — Medial Meniscus Sag1 canonical paired confirmation
- **R3D-12** — final-training data/budget decision
- **R3D-13** — final Main 3-Fold
- **R3D-14** — standalone hidden-test submission
- **R3D-15** — final Exp57 + R3D ensemble

번호는 실제 실행 결과에 따라 세부 suffix를 추가할 수 있으나,
새 채팅에서 임의로 과거 번호를 재사용하지 않는다.
