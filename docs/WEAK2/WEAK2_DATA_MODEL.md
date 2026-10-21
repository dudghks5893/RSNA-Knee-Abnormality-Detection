# Weak2 Direct Specialist — Data / Model Contract

최종 업데이트: 2026-10-21

## 1. 목적

기존 CoAt384 + S6F0 계보에서 상대적으로 약한 두 타깃만 보강하는 **단일 추가 예측 모델**을 만든다.

- Target 1: **Synovitis**
- Target 2: **Lateral OA**
- 별도 learned selector 모델을 붙이지 않는다.
- 하나의 RadImageNet ResNet50 backbone을 공유하고, target-specific hierarchical attention/head로 두 타깃을 예측한다.
- 최종 hidden-test 제출에서 추가 checkpoint는 **Weak2 모델 1개**만 사용한다.
- Fold ensemble은 기본 설계가 아니다. **Single model only**.

## 2. Label source

Kaggle Input:

```text
/kaggle/input/datasets/yhlucas/rsna-knee-version-a-strict-v1/STRICT_V1
```

사용 파일:

```text
STRICT_V1_TRAIN_LABELS_12_TARGETS.csv
GOLD58_UIDS_ONLY_NO_LABEL_VALUES.csv
STRICT_V1_DISTRIBUTION.csv
SCHEMA.json
```

Version A Strict V1 규칙을 그대로 따른다.

- label은 hard binary 0/1만 사용한다.
- `mask=0`인 target은 0으로 해석하지 않고 **loss에서 완전히 제외**한다.
- Gold58 UID는 train/cache selection에서 완전히 제외한다.
- Strict V1 자체가 Gold58을 training record에서 제외한 상태인지 실행 시 다시 assert한다.

Strict V1 전체 분포:

| Target | Positive | Negative | Excluded |
| --- | ---: | ---: | ---: |
| Synovitis | 511 | 35 | 3,803 |
| Lateral OA | 66 | 2,490 | 1,793 |

## 3. Weak2 study pool — frozen V1 policy

목표는 두 target의 **확실한 0/1만 사용**하면서 Lateral OA의 과도한 negative를 줄이고, Synovitis의 희소 negative는 모두 보존하는 것이다.

### 3.1 Base pool

1. Synovitis `mask=1` 전부 사용
   - 511 positive
   - 35 negative
   - 546 studies

2. Lateral OA positive `mask=1,label=1` 전부 추가
   - 전체 66 positive
   - 이 중 23은 이미 Synovitis-valid pool과 겹침
   - 새로 추가되는 study = 43

따라서 base union:

```text
589 unique studies
```

이 589명 안에는 이미:

```text
Lateral OA positive = 66
Lateral OA negative = 214
```

가 포함된다.

### 3.2 Lateral OA negative downsampling

Lateral OA negative는 최종 **700 unique studies**만 사용한다.

이미 base union에 포함된 negative 214명은 반드시 유지하고, 나머지 negative pool에서 **486명**을 추가한다.

추가 486명은 단순 전역 random이 아니라 `series_count`별 분포를 보존하는 proportional stratified sampling을 사용한다.

- Seed: `20261021`
- Gold58 overlap: 0 강제
- sampled UID manifest를 cache artifact에 저장
- 재실행 시 동일 UID 집합이 재현되어야 한다.

최종 Weak2 unique study pool:

```text
1,075 studies
```

최종 target coverage:

```text
Synovitis : 511 positive / 35 negative
Lateral OA:  66 positive / 700 negative
```

한 study에서 한 target만 mask=1이면 다른 target loss는 계산하지 않는다.

## 4. Cache preprocessing — W2D-00

기존 selector 기반 Top-K cache를 재사용하지 않는다. Weak2는 **모든 Series를 보존**한 새로운 CPU cache를 만든다.

Expected selected-series count from Strict V1 `series_count`:

```text
6,014 series / 1,075 studies
mean 5.59 series per study
```

### 4.1 Series policy

- 선택된 study의 **모든 Series를 사용**
- 특정 Plane/sequence를 사전에 버리지 않는다.
- learned selector 없음
- 각 Series 내부에서만 sparse slice sampling 수행

### 4.2 Slice ordering

우선순위:

1. `ImagePositionPatient`의 dominant physical axis
2. `InstanceNumber`
3. natural filename sort

raw filename 순서를 anatomical ordering으로 간주하지 않는다.

### 4.3 Slice sampling

각 Series:

```text
anatomical ordered slices
→ central useful band 6% ~ 94%
→ 최대 K=16 evenly spaced unique slices
→ K<16이면 zero padding + valid_mask
```

중복 slice를 만들어 K16을 채우지 않는다.

Cache:
- K16 / Series

향후 Train:
- valid K16 중 epoch마다 stochastic subsampling을 적용할 수 있음
- minority study oversampling은 cache 복제가 아니라 DataLoader에서 동적으로 수행

### 4.4 Spatial preprocessing

고정:

```text
150 mm × 150 mm physical center crop
→ 320 × 320 resize
```

- `PixelSpacing`의 row/column spacing을 각각 사용
- **random crop 없음**
- 병변 정보가 잘릴 수 있는 320→288 random crop은 사용하지 않는다.
- train/validation/inference 모두 같은 150 mm 중심 FOV를 기준으로 한다.

### 4.5 Intensity preprocessing

각 selected slice:

```text
modality LUT
→ 1st–99th percentile robust clipping
→ [0,255] uint8
```

RadImageNet 학습 시 모델 입력 normalization은:

```text
x / 127.5 - 1.0
```

을 사용한다. ImageNet mean/std를 RadImageNet weight에 사용하지 않는다.

### 4.6 Laterality normalization

모든 knee를 동일 orientation으로 정규화한다.

Right knee:

- Coronal / Axial: image horizontal flip
- Sagittal: slice sequence reverse

Lateral OA가 있으므로 training augmentation에서 horizontal flip은 금지한다.

### 4.7 Cache format

4개 HDF5 shard로 저장한다.

각 shard:

```text
images              uint8   [N_series, 16, 320, 320]
valid_mask          uint8   [N_series, 16]
relative_position   float32 [N_series, 16]
source_slice_index  int32   [N_series, 16]
```

Series/Study identity와 MRI metadata는 CSV manifest에서 관리한다.

Raw image payload 예상 크기:

```text
6,014 × 16 × 320 × 320 × uint8 ≈ 9.18 GiB
```

HDF5 LZF compression을 사용하므로 실제 파일 크기는 실행 후 기록한다.

## 5. W2D-00 output contract

필수 output:

```text
w2d00_cache_shard_00.h5
w2d00_cache_shard_01.h5
w2d00_cache_shard_02.h5
w2d00_cache_shard_03.h5
w2d00_study_manifest.csv
w2d00_series_manifest.csv
w2d00_selection_audit.csv
w2d00_cache_summary.json
w2d00_sha256.csv
w2d00_metadata_bundle.zip
```

Final gate:

- study = 1,075
- expected Series = 6,014; actual `train_series.csv`와 exact match 검증
- Synovitis = 511P / 35N
- Lateral OA = 66P / 700N
- Gold58 overlap = 0
- duplicate Study/Series cache index = 0
- NaN/invalid label contract = 0
- 4 HDF5 shard 모두 readable
- SHA256 출력

## 6. W2D-00 measured cache / W2D-01 model contract

W2D-00 cache는 **PASS**했고 다음 Dataset으로 게시되었다.

```text
/kaggle/input/datasets/yhlucas/rsna-knee-w2d00-strict-allseries-cache320-v1
```

Measured cache:
- 1,075 studies
- 6,014 Series
- runtime 30.08 min CPU
- decode failures 0
- selected-slice PixelSpacing missing 0
- unknown laterality 492 Series
- HDF5 structural gate PASS

W2D-01 pretrained backbone input:

```text
Kaggle Dataset: marwanmath/resnet-50-radimagenet-marwan
File: ResNet50.pt
Backbone: RadImageNet ResNet50
```

Kaggle에서는 **Add Input → Datasets**에서 위 Dataset을 추가한다.

GPU 학습 구조:

```text
All-Series K16 cache
→ RadImageNet ResNet50
→ slice features
→ target-specific Slice Attention
→ target-specific Series Attention
→ Synovitis head
→ Lateral OA head
```

학습 정책:

- one model / one checkpoint
- T4 ×2 **DDP**
- no fold ensemble
- DDP smoke는 실제 forward/backward/optimizer를 2 step 이상 검증
- batch/microbatch는 실제 VRAM/throughput profiling 후 결정
- user의 과거 Batch 124+ headroom 기록을 무시하지 않되 현재 320px all-Series R50에 그대로 가정하지 않는다.
- Synovitis negative와 Lateral OA positive는 dynamic oversampling + 매 draw 다른 slice/intensity augmentation
- cache 파일 자체를 복제하지 않는다.
- class weight와 oversampling을 동시에 극단적으로 적용하지 않는다.
- Gold58은 optimization / hyperparameter / checkpoint selection에 사용하지 않는다.


### W2D-01 frozen training design — proposed 2026-10-21

#### Architecture

```text
320×320 grayscale slice
→ RadImageNet ResNet50 trunk (strict ResNet50.pt load)
→ 2048-d slice feature
→ Linear 2048→512 + LayerNorm/GELU
→ plane / fluid-sensitive / relative-position embedding
→ 1-layer Slice Transformer (d=512, 8 heads, FFN=1024)
→ target-specific gated Slice Attention
→ target-specific gated Series Attention
→ independent Synovitis / Lateral OA binary heads
```

The model remains one checkpoint. Slice/Series attention is internal to the predictor and is not a separate selector.

#### Slice policy

Cache K16 is preserved. Training uses **K8 stochastic-stratified slices per Series**:
- ordered K16 is divided into 8 spatial bins
- one valid slice is sampled from each bin
- order is preserved
- no random spatial crop / no horizontal flip / no geometric rotation
- mild Series-consistent intensity augmentation only

Inference/diagnostic uses all valid K16 slices.

#### Imbalance sampler

Each epoch contains 1,024 study draws:

```text
Synovitis-focused lane: 512
  341 positive + 171 negative

Lateral-OA-focused lane: 512
  171 positive + 341 negative
```

Sampling is deterministic from `SEED + epoch`, with replacement only when the requested class draw count exceeds its unique pool. Every repeated study gets a newly sampled K8 slice set and new mild intensity augmentation.

All available target labels on a drawn study are still used; mask=0 remains excluded.

Loss:
- masked BCEWithLogits
- Synovitis: positive weight 1.0 / negative weight 2.0
- Lateral OA: positive weight 2.0 / negative weight 1.0
- per-target weighted loss is normalized by valid weight sum
- final loss = 0.5 × Synovitis loss + 0.5 × Lateral-OA loss
- no focal/asymmetric loss in V1

#### Optimizer / LR

```text
Optimizer: AdamW
Weight decay: 1e-4
Gradient clip: 1.0
AMP: FP16
Epochs: fixed 10
Early stopping: OFF
Warmup: 5% optimizer steps
Scheduler: cosine decay to 0.1 × initial LR
```

Discriminative LR — revised after CoAt lineage review:
- stem + layer1: **5e-6**
- layer2: **1e-5**
- layer3: **2e-5**
- layer4: **4e-5**
- projection / Transformer / attention / heads: **1e-3**

Rationale: the successful CoAt branch used a much stronger newly-initialized MIL/head LR (2e-3, later stabilized at 1e-3) while keeping the pretrained backbone substantially lower (4e-5). W2D-01 follows that separation rather than applying 1e-3 to the pretrained RadImageNet trunk.

Epoch 1 is a true **head warm-up**: the entire RadImageNet backbone is frozen and only the newly initialized projection / Transformer / attention / heads train at 1e-3. Epoch 2–10 rebuild DDP with the full backbone trainable and the discriminative LRs above. BatchNorm running statistics remain frozen to pretrained RadImageNet statistics; affine parameters follow the layer trainability.

#### DDP batch policy

T4×2 DDP. Training K8 gives approximately 44.8 slices/study on average and at most 96 slices/study in the current cache.

The notebook profiles worst-case high-Series studies with actual forward/backward/optimizer for at least 2 consecutive optimizer steps.

Profiling is two-stage and uses actual T4×2 DDP forward/backward/optimizer work.

1. Encoder slice-microbatch candidates: 32 / 64 / 96 / 128 slices.
2. With the fastest safe encoder chunk fixed, per-GPU Study Batch candidates:
   - 1 / GradAccum 4 → Global Effective Batch 8
   - 2 / GradAccum 2 → Global Effective Batch 8
   - 4 / GradAccum 1 → Global Effective Batch 8

Every candidate must complete at least 2 consecutive optimizer steps. The selected configuration then runs a representative balanced-data probe and a real save→load→continue resume smoke before full training. The highest-throughput configuration that passes VRAM and stability gates is selected automatically. Batch size is not reduced pre-emptively.

#### Checkpoint policy

No validation-based `best.pt` is used because Gold58 is untouched and the scarce 35 Synovitis negatives are not removed for a noisy internal holdout.

- every epoch: overwrite `w2d01_resume_last.pt`
  - raw model
  - EMA model
  - optimizer / scheduler / GradScaler
  - epoch / global step
  - RNG states
  - sampler seed/state
  - full config / input paths / cache SHA lineage
- EMA starts when full backbone is unfrozen; decay = 0.995
- final deploy checkpoint: `w2d01_r50_ema_e10.pt`
- raw epoch-10 checkpoint is also saved as a safety artifact but is not the primary submission model

Gold58 is evaluated only after the final checkpoint is frozen and is not used to choose epoch, LR, sampler or checkpoint.

## 7. Documentation policy

이 계보는 `docs/WEAK2/`에만 누적한다.

- 실제 실행/결과: `WEAK2_EXPERIMENT_LOG.md`
- 현재 상태/다음 작업: `WEAK2_ROADMAP.md`
- 데이터/모델 계약: 이 파일

Kaggle notebook source는 GitHub에 저장하지 않는다. GitHub에는 **문서만** 남긴다.
