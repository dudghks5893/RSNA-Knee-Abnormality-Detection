# Weak2 Direct Specialist — Experiment Log

최종 업데이트: 2026-10-21

이 문서는 Weak2 계보의 **실제 실행 결과만 누적**한다. 예정/추정은 Roadmap/Data Contract와 구분한다.

## W2D-00 — Strict All-Series CPU Cache

상태: **PREPARED / NOT EXECUTED ON KAGGLE YET**

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

아직 Kaggle 실행 전이다.

실행 후 이 섹션에 다음을 기록한다.

- actual selected studies/series
- DICOM header/decode failures
- missing PixelSpacing/laterality counts
- actual shard sizes
- runtime
- output SHA256
- PASS/FAIL
