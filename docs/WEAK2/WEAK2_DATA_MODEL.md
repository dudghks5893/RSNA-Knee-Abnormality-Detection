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

## 6. Planned model — W2D-01

Cache가 PASS한 뒤에만 GPU 학습으로 이동한다.

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

## 7. Documentation policy

이 계보는 `docs/WEAK2/`에만 누적한다.

- 실제 실행/결과: `WEAK2_EXPERIMENT_LOG.md`
- 현재 상태/다음 작업: `WEAK2_ROADMAP.md`
- 데이터/모델 계약: 이 파일

Kaggle notebook source는 GitHub에 저장하지 않는다. GitHub에는 **문서만** 남긴다.
