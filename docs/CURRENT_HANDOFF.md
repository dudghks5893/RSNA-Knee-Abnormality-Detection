# RSNA Knee — Current Handoff / New Chat Cold Start

최종 업데이트: **2026-10-08**

이 문서는 새 ChatGPT 채팅에서 **현재 프로젝트를 잘못된 과거 상태로 되돌리지 않고 즉시 이어가기 위한 최우선 인수인계 문서**다.

새 채팅의 AI Agent는 이 문서를 먼저 읽고,
그 다음 아래 문서를 순서대로 확인한다.

1. [CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md](CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md)
2. [3D_RESNET_EXPERIMENT_PLAN.md](3D_RESNET_EXPERIMENT_PLAN.md)
3. [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md)
4. [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)

README와 Specialist / 구 5-Fold 문서의 오래된 "현재", "NEXT", "진행 중" 표현이 이 문서와 충돌하면
**이 문서가 우선**한다.

---

# 1. 지금 무엇을 하고 있는가

Competition:

**RSNA Knee Abnormality Detection**

현재 project best Public LB:

- **0.918**
- **Exp57 — 3-Fold B3A + 3-Fold Full-MRI Direct 70:30 Hybrid**

현재 주력 신규 계보:

- **R3D — MedicalNet 3D ResNet 기반 multi-series 3D MRI classifier**

가장 최근 완료 실험:

- **R3D-10AB — Always Dual vs Mixed 3-Mode Fold0**
- 완료 / PASS
- Full-FOV + Crop130 feature-token fusion 계열은 현재 Crop130 single-view보다 낮아서 **기각**
- Fold1/Fold2 confirmation은 하지 않음

현재 즉시 다음:

1. **R3D-11CACHE**
   - Fold0/1/2 모두를 커버하는 canonical Crop130 search cache 정리
2. **R3D-11**
   - canonical R34 + Crop130 기준
   - Medial Meniscus Sag1-only vs ALL paired 3-Fold confirmation
3. R3D final-training data/budget 결정
4. Final Main R3D 3-Fold
5. R3D standalone hidden-test submission
6. Exp57 + R3D final ensemble

---

# 2. 새 채팅 Agent가 절대 잘못 이해하면 안 되는 현재 Main R3D

현재 Main R3D는 아래로 **동결**되어 있다.

~~~text
Study의 ALL usable MRI Series
        ↓
각 Series에 130 mm physical center crop
        ↓
interpolated D24 × 96 × 96
        ↓
shared MedicalNet ResNet34
        ↓
GLOB — global feature 1 token / Series
        +
Series metadata embedding
        ↓
Transformer Encoder + shared CLS
        ↓
12 label-specific sigmoid heads
~~~

고정 설정:

- Series policy: **ALL**
- physical FOV: **130 mm center crop**
- depth: **interpolated D24**
- in-plane: **96×96**
- Backbone: **MedicalNet R34**
- representation: **GLOB**
- anatomy mask: **OFF**
- Full fine-tuning
- pure FP32
- BatchNorm running stats frozen
- Transformer:
  - d_model 512
  - 2 layers
  - 8 heads
  - FFN 2048
  - dropout 0.10
  - Pre-LN
  - learnable CLS
- backbone LR: **1e-5**
- new-layer LR: **5e-5**
- WD: **1e-4**

다시 열지 않는 축:

- R50 / R101
- coarse spatial-token SPT27/SPT48
- current anatomy-mask fusion
- lower LR / frozen backbone
- P2/P3 cap micro-search
- Crop150 / 140 mm FOV micro-search
- simple 128+ in-plane resolution
- simple D32+ interpolation
- REAL24 / REAL32 nearest actual-slice
- Synovitis Sag1-only
- current Full+Crop Dual-FOV / Mixed3 structure

새 evidence가 생기기 전에는 위 search를 반복하지 않는다.

---

# 3. Exp57을 정확히 이해할 것

Exp57을 단순 "2D DINO 모델"이라고 부르면 안 된다.

Exp57은 서로 다른 두 branch의 2.5D full-MRI system이다.

## 3.1 Fold별 task-tuned DINOv2-Base

각 MRI Series의 모든 slice를 center candidate로 사용하고,
각 candidate를:

~~~text
[previous slice, center slice, next slice]
~~~

3-channel 2.5D window로 만든다.

전처리:

- DICOM physical sorting
- RescaleSlope / RescaleIntercept
- MONOCHROME1 inversion
- full-Series 1–99 percentile normalization
- right-knee laterality normalization
- **130 mm physical center crop**
- 224×224
- 3-slice window

DINO feature:

- CLS 768
- PatchMean 768
- concat = **1536-d float16**

전체:

- 4,407 studies
- 24,371 series
- 819,078 window candidates

## 3.2 Full-MRI Direct branch

~~~text
모든 windows
→ window attention
→ series representation
→ series attention
→ 12 logits
~~~

이 branch는 직접 예측도 하고,
동시에 환자별 중요한 window를 고르는 selector 역할도 한다.

## 3.3 Top-24 B3A branch

각 Fold의 Full-MRI MIL attention이
환자별 중요한 raw 3-slice window 24개를 선택한다.

~~~text
Fold-specific Top24 raw windows
→ task-tuned DINOv2-Base warm-start
→ hierarchical aggregation
→ end-to-end fine-tuning
→ 12 probabilities
~~~

## 3.4 Exp57 final

~~~text
P_B3A_3F    = mean(B3A_F0, B3A_F1, B3A_F2)
P_DIRECT_3F = mean(Direct_F0, Direct_F1, Direct_F2)

P_FINAL =
0.70 × P_B3A_3F
+
0.30 × P_DIRECT_3F
~~~

Public LB:

**0.918**

따라서 최종 R3D ensemble에서 Exp57은
"local 2D model"이 아니라
**2.5D full-MRI hierarchical MIL + attention-selected raw-image refinement system**으로 취급한다.

---

# 4. Validation contract

Official Gold:

- **58 studies**
- 12 binary targets
- deterministic 3-Fold seed: **20261059**

Fold sizes:

- Fold0 = 20
- Fold1 = 19
- Fold2 = 19

Gold manifest SHA256:

`246f252a1ce4faaafa1b7d30e2c75cde6d79951cb780b0b33bf4f4dd12ad7e4b`

주의:

- Gold58은 작다.
- Fold0는 architecture search에 반복 사용되어 **untouched validation이 아니다**.
- 수천분의 일 수준 차이는 구조적 개선이라고 과장하지 않는다.
- 현재 split을 다시 만들지 않는다.

Fold-specific Pseudo1000 Dataset:

`rsna-knee-r3d-3fold-pseudo-v1`

대표 root:

`/kaggle/input/datasets/yhlucas/rsna-knee-r3d-3fold-pseudo-v1`

Pseudo UID SHA:

- Fold0:
  `e96b07e22aa0e4ac40281ce5709841dbadfa3cb61c882c6f1d10b8dccb4e233c`
- Fold1:
  `e3bcab2deb4e4284179fd369a72566e17083eb173750144c55f0c096dee15d98`
- Fold2:
  `d2c482ed154c141a9eb2f1ce83e5ca395c57eb30e5e3a331e319a427c333cc4d`

Expected Study sampling trace SHA:

- Fold0:
  `d0c36a537f9868e6d6f484d5852f922a48d08df1ad7d35d9d241c751ed05f7a3`
- Fold1:
  `724f4b6e5e8604d8d860e42e4eb006a41419a5bb1c5e8738febf803c0624a096`
- Fold2:
  `1e4d28dfce05fb4e364599d59fdd9b691c14734889d2bd9c9d923772c40cb525`

---

# 5. Frozen model assets

MedicalNet Dataset:

`rsna-knee-r3d-medicalnet-pretrained-v1`

R34 SHA256:

`977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`

R34 is final Main R3D backbone.

Historical:
- R50 SHA:
  `5b6189cafbee2f5604a7279b62bc163365aa6a86a377e1dc260a14275cacbd84`
- R101 SHA:
  `a26bbcf9b2ad35f048b0fa317234c003f171a4d719760e5c4aff9f793654ebcf`

R50/R101 재비교는 하지 않는다.

---

# 6. Full-FOV persistent cache 구조를 정확히 기억할 것

Dataset:

`rsna-knee-wide224-persistent-cache-v1`

실제 mounted structure:

Metadata index:

`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d06a_metadata_bundle/series_index.csv`

Volume root:

`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d06a_all_series_d24_96_v1/`

Volume files:

- `volumes_000.npy`
- `volumes_001.npy`
- ...

규모:

- 4,407 studies
- 24,371 series
- 819,078 slices
- 48 shards
- decode failure 0
- 약 10.04 GiB

매우 중요:

R3D-06A raw `series_index.csv`에는
`plane_rank`, `selection_order`가 원래 저장되어 있지 않다.

Canonical ALL policy를 primitive metadata로 재구성한다.

~~~text
plane order:
Sagittal = 0
Coronal = 1
Axial = 2

rank =
4 × Fluid_Sensitive × Fat_Suppression
+ 2 × Fluid_Sensitive
+ Fat_Suppression

sort:
StudyInstanceUID ASC
→ plane order ASC
→ rank DESC
→ SeriesInstanceUID ASC

plane_rank =
Study + Plane group cumcount + 1

selection_order =
Study group cumcount
~~~

새 Notebook에서 없는 derived column을 바로 assert하면 안 된다.

---

# 7. Crop130 cache 상태 — 다음 작업의 핵심

R3D-10에서 정상 mount/사용된 current Crop130 root:

`/kaggle/input/datasets/yhlucas/rsna-knee-r3d-crop130-search-cache-v3/crop130_d24_96`

R3D-10 preflight:

- studies = **1,058**
- paired Series = **5,882**
- Fold0 Gold + Fold0 Pseudo1000 coverage PASS

중요:

**이 v3 cache 하나만으로 Fold1/Fold2도 커버한다고 가정하면 안 된다.**

R3D-09 Fold1/Fold2 confirmation에서는:

- 기존 Fold0 Crop130 base
- Fold1/Fold2에서 추가로 필요한 missing-study delta

를 함께 사용했다.

Kaggle에서 같은 Dataset의 서로 다른 Version을 동시에 mount하는 데 문제가 있었고,
delta Dataset을 새 slug로 재등록해도
`ERRORED_MOUNTING_DATASET / Output 0 B`가 반복된 적이 있다.

따라서 다음은 **R3D-11CACHE**다.

목표:

- 기존 Crop130 base + delta artifact를 한 canonical Dataset으로 합침
- Fold0 / Fold1 / Fold2 Pseudo1000 + Gold58 모두 coverage
- CPU-only
- 가능하면 raw DICOM 재decode 없이 기존 artifact 파일을 합침
- 기존 artifact가 부족할 때만 missing study를 새로 decode

같은 Dataset의 서로 다른 Version을 동시 mount하는 설계는 하지 않는다.

---

# 8. 주요 R3D decision history

## R34 / representation

R34 / R50 / R101 pooled Macro AUROC:

- R34: **0.567267**
- R50: 0.533494
- R101: 0.510364

→ R34

GLOB / spatial token Fold0:

- GLOB: **0.601827**
- SPT27: 0.595809
- SPT48: 0.590426

→ GLOB

Mask:

- MASK_ON 0.601827 / 0.499933
- MASK_OFF **0.609698 / 0.521793**

→ MASK_OFF

## Series

3-Fold mean AUROC:

- P2: 0.573140
- P3: 0.589716
- ALL: **0.596226**

→ ALL

## Crop / resolution / depth

R3D-07A Fold0:

- Full 0.617594 / 0.540314
- Crop130 **0.622257 / 0.508100**
- Crop150 0.618253 / 0.521752

R3D-07B:

- R128 0.607901 / 0.504403 → reject
- D32 0.604305 / 0.504119 → reject

R3D-08 REAL24:

3-Fold mean delta vs interpolated D24:

- AUROC **+0.000405**
- AUPRC **+0.000842**

Fold0만 개선, Fold1/2 AUROC 하락.

→ actual-slice nearest reject
→ **interpolated D24 유지**

R3D-09 Crop130 3-Fold:

- F0 ΔAUC +0.004663
- F1 ΔAUC -0.005823
- F2 ΔAUC +0.033412
- mean ΔAUC **+0.010751**
- mean ΔAUPRC **+0.003722**

→ **Crop130 adopted**

---

# 9. R3D-10AB — 가장 최근 완료 결과

실행:

- Account A
- T4×2
- GPU0 = **ALWAYS_DUAL**
- GPU1 = **MIXED_3MODE**

주의:

Historical Experiment ID가 `R3D-10AB`이지만,
여기서 AB는 두 variant 표시였다.
**Account B에서 실행한 것이 아니다.**

앞으로는 Account tag와 Variant A/B를 혼용하지 않는다.

## ALWAYS_DUAL

매 step:

~~~text
Full-FOV + Crop130
→ one shared R34
→ Full feature + Crop feature
→ FOV embedding
→ shared Transformer
~~~

Best:

- epoch **2**
- AUROC **0.6098085564**
- AUPRC **0.4942921686**
- vs frozen Full ΔAUC **-0.00778515**
- vs frozen Crop130 ΔAUC **-0.01244833**
- runtime **28.22 min**
- pretrained matched fraction = 1.0
- sample trace exact
- PASS

## MIXED_3MODE

Train step mode:

~~~text
FULL_ONLY = 1/3
CROP_ONLY = 1/3
DUAL      = 1/3
~~~

실제 1,920 steps:

- Full 621
- Crop 645
- Dual 654

Checkpoint selection:

- Dual simultaneous Macro AUROC

Best epoch 6:

- Dual: **0.6107038376 / 0.4836953876**
- Full-only: **0.6128357417 / 0.4870971897**
- Crop-only: **0.6045047538 / 0.4802742049**
- Full/Crop probability average: **0.6075728448 / 0.4823133733**

Frozen:
- Crop130 **0.622257 / 0.508100**
- Full **0.617594 / 0.540314**

결론:

- ALWAYS_DUAL reject
- MIXED_3MODE reject
- Fold1/Fold2 confirmation 없음
- Main R3D = **Crop130 single-view**

Result ZIP SHA256:

`da5dbf79b88bbe4c9d8f1537c322cdc0b761356c70ab6d27d6df2bedee52fbe6`

해석 제한:

"Full과 Crop을 함께 사용하는 아이디어 전체"를 영구 기각한 것이 아니다.

현재 실패한 구조는:

~~~text
shared R34
→ Full/Crop separate feature token
→ FOV embedding
→ shared Transformer
~~~

현재 일정에서는 여기서 더 fusion 구조를 튜닝하지 않는다.

---

# 10. Medial Meniscus Sag1 specialist 상태

R3D-06H historical Fold0 paired binary experiment:

Medial Meniscus:

- P2 AUROC **0.677083**
- P2 AUPRC **0.591098**
- Sag1-only AUROC **0.729167**
- Sag1-only AUPRC **0.756302**
- ΔAUROC **+0.052083**
- ΔAUPRC **+0.165204**

강한 signal이다.

Synovitis:

- P2 **0.680000 / 0.757973**
- Sag1 **0.590000 / 0.583247**

→ Synovitis Sag1-only는 기각.

Medial Meniscus 주의:

- R3D-06H는 현재 final Crop130 이전
- visible implementation에서 canonical R34 naming과 다른 부분이 있었음
- 따라서 최종 target-specific candidate로 쓰기 전
  **현재 canonical R34 + Crop130에서 재확인**한다.

---

# 11. R3D-11 exact next design

먼저 R3D-11CACHE를 끝낸 뒤 실행한다.

Target:

**Medial Meniscus**

Control:

~~~text
Crop130
+ ALL Series
+ canonical MedicalNet R34
+ binary Medial Meniscus head
~~~

Candidate:

~~~text
Crop130
+ Sagittal plane_rank = 1 only
+ same canonical MedicalNet R34
+ same binary Medial Meniscus head
~~~

중요:

기존 06H의 P2 control을 그대로 반복하지 않는다.

현재 Main R3D가 ALL이므로
최종 confirmation control은 **ALL**이 더 직접적이다.

가능하면 3-Fold paired:

- Fold0
- Fold1
- Fold2

각 pair:

- same initial model state
- same Study sampling
- same Gold/pseudo data
- same optimizer
- same epochs
- same augmentation RNG
- Series policy만 ALL vs Sag1로 변경

Primary:

**Gold58 pooled OOF Medial Meniscus AUROC**

Secondary:

- pooled AUPRC
- Fold-level AUROC/AUPRC
- fold stability

Sag1-only가 명확히 재현되지 않으면 specialist routing은 종료한다.

---

# 12. R3D-11 이후 작업

## R3D-12 — Final training policy

아직 자동으로 결정하지 말 것:

- Pseudo1000을 그대로 쓸지
- report-only pseudo 전체로 확장할지
- samples/epoch
- epochs
- final budget
- checkpoint policy

특히:

**"final이니까 pseudo 4,349 전체"로 자동 확대 금지.**

Data scope 변경은 독립 실험 변수다.

## R3D-13 — Final Main 3-Fold

Architecture는 위 Main R3D로 고정.

필수:

- 3 Fold checkpoint
- checkpoint SHA
- fold prediction
- pooled OOF
- target metrics
- manifests
- runtime

## R3D-14 — Standalone Public LB

Exp57과 섞기 전에
R3D standalone submission을 먼저 실행한다.

그래야:

- R3D 자체 성능
- Exp57과의 complementarity

를 분리할 수 있다.

## R3D-15 — Final ensemble

후보:

- Exp57
- R3D 3-Fold
- R3D-11을 통과한 경우 Medial Meniscus Sag1 specialist

Public LB ratio micro-search는 제한한다.

---

# 13. Kaggle 작업 방식 — 반드시 지킬 것

## Save & Run All

사용자는 Kaggle에서 **Save & Run All**로 실행한다.

Notebook 오류가 났다고
"그 셀만 다시 실행"을 기본 해결책으로 제안하지 않는다.

Fresh rerun이 필요하면
새 clean session에서 전체 Save & Run All 가능한 Notebook을 준다.

## 오류 후 먼저 artifact 확인

학습 후 마지막 contract / zip 단계에서 실패하면
GPU 재학습부터 하지 않는다.

먼저 확인:

- epoch 완료 여부
- best checkpoint
- prediction CSV
- target metrics
- history
- logs

저장 artifact로 복구 가능하면
CPU/local posthoc recovery를 한다.

## CPU / GPU 분리

새 image/cache 생성:

**CPU-only Notebook**

GPU Notebook:

**training-only**

raw DICOM decode/cache build 때문에
T4를 idle reservation하지 않는다.

## T4×2

같은 Dataset을 공유하는 두 독립 job이면
한 Kaggle session T4×2가 편할 수 있다.

~~~text
physical GPU0 → subprocess 1
physical GPU1 → subprocess 2
~~~

각 subprocess는 `CUDA_VISIBLE_DEVICES`로 분리한다.

## Dataset mount

`Output 0 B + ERRORED_MOUNTING_DATASET`이면:

- Python code error 아님
- training 시작 전
- failed Dataset mount 문제

같은 Dataset의 다른 Version을 동시에 mount할 수 있다고 가정하지 않는다.

---

# 14. Notebook 전달 규칙

새 Notebook을 만들 때 반드시:

- 첫 Markdown에 Experiment / 목적 / Changed / Fixed
- exact Required Kaggle Inputs
- Accelerator
- Internet
- Save Version
- 예상 runtime
- Outputs
- success criterion
- exact path first
- fail-fast
- seed/config
- /kaggle/working output
- SHA / contract
- nbformat validation
- Python AST/syntax
- embedded worker AST
- main-kernel top-level variable audit

를 수행한다.

파일명 앞 `A_` / `B_`는 **Account tag 전용**이다.

T4×2 내부 variant는:

- `GPU0 ALWAYS_DUAL`
- `GPU1 MIXED_3MODE`

처럼 설명형 이름을 사용한다.

---

# 15. GitHub 문서 상태 — 2026-10-08

현재 authoritative documents:

- `docs/CURRENT_HANDOFF.md`
- `docs/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md`
- `docs/3D_RESNET_EXPERIMENT_PLAN.md`
- `docs/EXPERIMENT_HISTORY.md`
- `docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md`

Historical / superseded / research-reference 문서:

- `docs/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md`
- `docs/PUBLIC_RESEARCH_PERFORMANCE_ROADMAP_2026-10-07.md`
- `docs/SPECIALIST_EXPERIMENT_ROADMAP.md`
- `docs/SPECIALIST_EXPERIMENT_LOG.md`

README의 current status도 2026-10-08 기준으로 최신화했다.

---

# 16. 새 채팅에서의 첫 행동

새 채팅 Agent는 사용자가 "이어가자", "다음 진행하자"라고 하면
바로 새 실험 Notebook을 만들기 전에:

1. 이 문서와 Current Roadmap / Plan을 확인
2. 현재 next가 **R3D-11CACHE**인지 확인
3. 현재 Crop130 artifact가 실제로 어디에 mount되어 있는지 확인
4. 기존 R3D-09 base/delta artifact를 재사용할 수 있는지 먼저 확인
5. raw DICOM 재decode가 정말 필요한지 판단
6. R3D-11CACHE의 CPU-only 실행 설계를 제시/생성

한다.

사용자에게 이미 알려진 정보를 다시 처음부터 묻지 않는다.

실제 Kaggle path / artifact가 새로 바뀌었으면
사용자가 준 현재 path를 문서 기억보다 우선한다.

---

# 17. 새 채팅용 한 줄

**현재는 Crop130 single-view Main R3D의 구조 탐색을 끝냈고, 다음은 Crop130 all-fold cache를 정리한 뒤 Medial Meniscus Sag1-only를 canonical R34 + Crop130에서 3-Fold paired confirmation하는 단계다.**
