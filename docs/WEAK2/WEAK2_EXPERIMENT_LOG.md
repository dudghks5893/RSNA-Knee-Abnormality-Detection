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
