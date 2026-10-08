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
2. Qwen3-8B / Mistral-Nemo-12B Kaggle GPU reader plan은 **폐기/미실행**. 현재 실행 계약: [LABEL_V6_SOL_CHUNKED_EXECUTION.md](LABEL_V6_SOL_CHUNKED_EXECUTION.md).
3. report-only 4,349 studies를 원본 `train.csv` 행 순서 그대로 **87 chunks**로 고정:
   - Chunk 001–086 = 50 studies / 600 decisions
   - Chunk 087 = 49 studies / 588 decisions
   - 총 52,188 decisions
   - report-only UID manifest SHA256 = `e675c1cfb8e88b3ec00af4fcba77bfb010e324e3a3473b04089da651af630a94`
   - chunk manifest SHA256 = `66179ef419094e6204ea3c39c4696d1da68463320bc9c58168e96d993e5a0cd5`
4. primary reader는 **GPT-5.6 Sol**. 기본 최대 5 chunks/chat으로 18개 chat에 배치하되, context 품질이 우려되면 더 일찍 끊고 최신 cumulative Master/Handoff로 새 chat에서 계속한다.
5. 각 chunk는 모든 study의 12 targets를 직접 판정하고 exact report evidence + Unicode offset + report SHA를 보존한다. 이전 completed chunk는 integrity defect가 없으면 재판정하지 않는다.
6. 4,349 완료 후 4,349 studies / 52,188 decisions 전체 contract, target별 5-state distribution / supervised coverage / positive prevalence / language·script / duplicate consistency를 감사한다.
7. HIGH-review / inference-used / contradiction / ambiguity / distribution anomaly를 **GPT-6 Astra가 원본 report + frozen policy로 독립 재판정**하고 최종 adjudication 후 canonical LABEL-V6를 freeze한다.
8. canonical release 후에만 target별 N_pos/N_neg/mask coverage로 class weight와 **masked per-target BCE → 12-target macro average** loss를 확정한다.
9. canonical label release → R3D-13 single Main full-data → standalone Public LB → 필요 시 Exp57 complementary blend. 동일 canonical manifest를 Exp57 old-vs-new label 비교에도 사용한다.

중요: 공식 Gold는 MRI image-derived consensus label이다. 새 라벨은 공식 영상 판정 기준을 최대한 모사하는 report-derived supervision이며 새로운 ground truth가 아니다.

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

# 7. Crop130 cache 상태

## 현재 Crop130 cache

**R3D-11CACHE 완료/PASS**: 1,446 studies / 8,027 series / 32 float16 shards, 약 3.31 GiB. 기존 cache 통합, raw decode 0.

- 현재 mount: `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d11cache`
- volume/index: `crop130_d24_96/`; Gold와 fold pseudo: `manifests/`.
- Index SHA256: `114bc191102849cc5df8b3f45c3a2b6361446d3e190f5315e13cdf6d002d1ef4`.
- Gold58와 3fold pseudo scope coverage PASS. 최종 4,407명 전체 cache는 아니다.

**R3D-12CACHE Full4407 완료/PASS — 2026-10-08**.

- 4,407 studies / 24,371 unique series.
- reused 8,027 + new 16,344 series.
- ALL + Crop130 + interpolated D24×96×96 + float16.
- 160 shards / 10,780,971,008 bytes (~10.04 GiB).
- decode failures 0; full metadata parity / reused shard SHA / new shard readback / 12-series Crop130 exact parity 모두 PASS.
- runtime 479.195 min (~7h59m).
- series index SHA256: `e72c9238c97e0957bb7fccee91489d23847519dd1aaf01e40620411875abe217`.
- shard manifest SHA256: `bf4a008de5fbf9a239066524b38d0b0632891b83ff2781bde07538ff75bd44a0`.
- audit ZIP SHA256: `73d6b93d678f6922cc72b8103961fc6a7baa67cd8fe41f740709ebbf8c69e39c`.
- study roles: report-only 4,349 / Gold validation 58.
- 학습 입력은 audit ZIP이 아니라 전체 `r3d12cache_full/` Dataset.
- **캐시 생성 단계 종료. 재실행하지 않는다.**


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

# 9. R3D-10AB — 이전 완료 결과

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
- Canonical R34 + Crop130 재확인은 R3D-11에서 완료. 최신 결과와 채택 보류 판단은 1절 참조.

---

# 11. R3D-11 완료 상태

이 문서 1절 결과가 최신이다. 재실행하지 않는다. 구조 탐색은 마무리하며 SAG1은 후보만 보존.

# 12. R3D-11 이후 작업

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

1. R3D-11은 완료/PASS, SAG1 최종 채택은 보류임을 확인한다.
2. 라벨 audit/pilot의 진행 상태와 사용자 리뷰를 이어간다.
3. Full4407 cache의 실제 성공 audit가 도착했는지 확인한다.
4. 최종 단일 모델, train report-only4349 / val Gold58 결정을 유지한다.
5. 추가 구조 탐색이나 기존 cache 전체 재생성을 임의로 시작하지 않는다.

# 17. 새 채팅용 한 줄

**R3D-11에서 SAG1의 fold별 개선을 확인했지만 최종 채택은 보류했다. 다음은 라벨 품질 정비와 Full4407 cache 확인 후 단일 Main R3D 전체 학습이다.**
