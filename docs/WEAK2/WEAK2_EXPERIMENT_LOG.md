# Weak2 Direct Specialist — Experiment Log

최종 업데이트: 2026-10-21

이 문서는 Weak2 계보의 **실제 실행 결과만 누적**한다. 예정/추정은 Roadmap/Data Contract와 구분한다.

## W2D-00 — Strict All-Series CPU Cache

상태: **PASS — Kaggle CPU cache completed**

### Frozen design

Targets:

```text
Synovitis
Lateral OA
```

Strict V1 source audit:

```text
Synovitis  = 511 positive / 35 negative / 3,803 excluded
Lateral OA = 66 positive / 2,490 negative / 1,793 excluded
Gold58 overlap in Strict train label table = 0
```

Frozen study selection:

```text
All Synovitis mask=1                         = 546 studies
All Lateral OA positives                     = 66 total
Lateral OA positives outside Synovitis pool  = 43
Base union                                   = 589

Lateral OA negatives already in base union   = 214
Additional stratified Lateral OA negatives   = 486
Final Lateral OA negatives                   = 700

Final unique study pool                      = 1,075
Expected total Series                        = 6,014
```

The additional 486 Lateral OA negatives are proportionally stratified by `series_count` with seed `20261021`.

Cache preprocessing frozen for first run:

```text
all Series
6–94% anatomical slice band
K16 max unique slices / Series
150 mm physical center crop
320 × 320
1–99 percentile robust intensity scaling
laterality normalization
no random crop
no horizontal-flip augmentation
CPU only
```

Raw image cache payload estimate:

```text
≈ 9.18 GiB before HDF5 compression
```

### Actual execution result

Kaggle CPU 실행 완료 / **PASS**.

Dataset:

```text
/kaggle/input/datasets/yhlucas/rsna-knee-w2d00-strict-allseries-cache320-v1
```

Measured:

```text
runtime = 30.08 min
studies = 1,075
series = 6,014
Synovitis = 511P / 35N
Lateral OA = 66P / 700N
Gold58 overlap = 0
selected-slice decode failures = 0
PixelSpacing missing on selected slices = 0
unknown laterality Series = 492
```

HDF5 structural gate: **PASS**

Shard sizes:

```text
00: 1,505 Series / 23,958 valid slices / 1.906 GiB
01: 1,501 Series / 23,947 valid slices / 1.902 GiB
02: 1,504 Series / 23,954 valid slices / 1.929 GiB
03: 1,504 Series / 23,957 valid slices / 1.920 GiB
```

Ordering:

```text
IPP_axis0 = 2,500 Series
IPP_axis1 = 2,039 Series
IPP_axis2 = 1,475 Series
```

All 6,014 Series used ImagePositionPatient anatomical ordering. No filename / InstanceNumber fallback was needed in the final selected pool.

Important audit note:
- 492 Series had unresolved laterality, so those Series were cached without left/right normalization.
- This is not a cache integrity failure, but because Lateral OA is side-sensitive it must be explicitly tracked in W2D-01 diagnostics rather than silently ignored.

Output cache SHA256 values are stored in `w2d00_sha256.csv` inside the dataset.


## W2D-01 — RadImageNet R50 DDP Strict

### V1 preflight / profile run — aborted before training

상태: **ABORTED BEFORE EPOCH 1 / resume-smoke loader bug**

입력 preflight는 PASS했다.

```text
T4 x2 detected
Study = 1,075
Series = 6,014
Synovitis = 511P / 35N
Lateral OA = 66P / 700N
Gold58 overlap = 0
RadImageNet SHA256 = 08629f7e7bd3e29b8ee9522ca3f65ce4d010a7ddf74f0ea3c7e3f3d0bbab0734
```

DDP profiler 실측:

| Encoder chunk | Global Study/s | Peak reserved GiB |
| ---: | ---: | ---: |
| 32 | 0.659 | 3.604 |
| 64 | 1.775 | 7.012 |
| 96 | 1.776 | 9.920 |
| 128 | 1.756 | 9.920 |

Study-batch profiler at chunk96:

| Per-GPU Study Batch | GradAccum | Global Study/s | Peak reserved GiB |
| ---: | ---: | ---: | ---: |
| 1 | 4 | 1.776 | 9.920 |
| 2 | 2 | 1.702 | 11.670 |
| 4 | 1 | 1.689 | 10.584 |

Representative balanced probe:

```text
per-GPU Study Batch = 1
GradAccum = 4
Encoder chunk = 96
Global Study/s = 1.338
Peak reserved = 11.049 GiB / 14.562 GiB
```

Failure occurred only at the following resume-smoke load step:

```text
torch.load(w2d01_smoke_resume.pt)
_pickle.UnpicklingError
PyTorch 2.6 default weights_only=True
Unsupported numpy._core.multiarray._reconstruct
```

Root cause:
- W2D resume checkpoints intentionally include optimizer, scheduler, scaler and NumPy/Python RNG states.
- PyTorch 2.6 changed `torch.load` default to `weights_only=True`.
- The checkpoint itself was written successfully; the loader did not explicitly opt out of weights-only mode.
- **No Epoch 1 training started and no learned checkpoint from this failed run is used.**

V2 fix:
- internally generated trusted resume checkpoints use explicit `weights_only=False`
- external `ResNet50.pt` still uses strict weights-only loading
- encoder-chunk selection changed so that candidates within 3% of the fastest throughput prefer lower VRAM; the V1 profile implies chunk64 is preferable to chunk96 because throughput is effectively tied while VRAM is much lower.

## 2026-10-21 — W2D-01 V2 runtime-gate stop / V3 I/O fix

상태: **V2 STOPPED BEFORE TRAINING / V3 NOTEBOOK READY**

V2 checkpoint-resume smoke는 정상 통과했다.

실측 DDP 설정:

```text
encoder chunk 64 : 1.7507 studies/s, reserved 7.01 GiB/GPU
encoder chunk 96 : 1.7459 studies/s, reserved 9.92 GiB/GPU
Study Batch 1 / Accum 4 : 1.7507 studies/s
Study Batch 2 / Accum 2 : 1.6417 studies/s
Study Batch 4 / Accum 1 : 1.5202 studies/s
selected = per-GPU Study Batch 1 / Accum 4 / chunk 64 / Effective Global Batch 8
```

V2 representative probe는 새로운 study 집합을 `/kaggle/input` HDF5에서 random-read 할 때 약 **92.14 s data wait**가 발생해 throughput이 0.3118 studies/s로 떨어졌고, 10 epoch runtime이 10.49 h로 과대 추정되어 의도된 4 h gate에서 중단됐다.

이는 model/DDP/checkpoint 오류가 아니며 **Epoch 1 본학습은 시작되지 않았다**.

V3 수정:
- 4개 HDF5 shard를 먼저 `/kaggle/temp/w2d01_cache`로 sequential staging
- 이후 모든 random training read는 local temp storage 사용
- V2에서 이미 측정한 최적 DDP config를 고정하여 profiling 반복 제거
- local-cache warm-up 후 representative 6 optimizer-step probe
- trusted internal checkpoint는 `weights_only=False`로 resume smoke
- local representative runtime이 4 h gate를 통과해야 본학습 시작
