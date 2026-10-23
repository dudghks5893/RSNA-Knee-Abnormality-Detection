# Weak2 Direct Specialist — Experiment Log

최종 업데이트: 2026-10-23

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


## 2026-10-21 — W2D-01 V4 prepared after batch-policy review

상태: **V4 NOTEBOOK READY / TRAINING NOT STARTED YET**

V2 실측에서 per-GPU Study Batch 1이 선택된 이유는 VRAM 부족이 아니라 throughput이었다.

```text
B1 / Accum4 = 1.7507 studies/s
B2 / Accum2 = 1.6417 studies/s
B4 / Accum1 = 1.5202 studies/s
```

따라서 Study Batch 1은 당시 profiler 기준으로 합리적인 선택이었지만, 해당 측정은 remote HDF5 I/O 영향을 받았다. 사용자의 요청에 따라 V4에서는 local HDF5 staging 이후 다시 batch를 비교한다.

V4 changes:
- 4 h projected-runtime gate 제거
- runtime estimate는 informational only
- encoder chunk 64 고정
- local-cache candidates: B1/A4, B2/A2, B4/A1, B8/A1
- B8는 Effective Global Batch 16으로 허용
- best throughput의 5% 이내에서는 더 큰 real Study Batch를 우선
- local-cache representative probe와 resume smoke는 유지
- actual OOM / non-finite / resume failure만 hard stop

No Epoch 1 training from V1/V2/V3 is reused.


## 2026-10-21 — W2D-01 V4 orchestration failure / V5 fix

상태: **V4 ABORTED BEFORE TRAIN / V5 NOTEBOOK READY**

V4 actual:
- input preflight PASS
- HDF5 local staging PASS: 7.66 GiB copied to `/kaggle/temp/w2d01_cache` in 1.71 min
- failure before any GPU profiling/training
- root cause: notebook refactor removed controller helper definitions `run_profile()` and `torchrun_cmd()`
- observed exception: `NameError: name 'run_profile' is not defined`
- no Epoch 1 training was started

V5:
- restores `torchrun_cmd()` + `run_profile()` in the same profiling cell to remove cell-order/refactor dependency
- keeps T4×2 DDP and local HDF5 staging
- runtime hard limit remains disabled
- local-cache batch candidates:
  - B1 / Accum4 → effective global 8
  - B2 / Accum2 → effective global 8
  - B4 / Accum1 → effective global 8
  - B8 / Accum1 → effective global 16
- encoder chunk fixed at 64
- candidates run real forward/backward/optimizer profiling
- among candidates within 5% of fastest throughput, prefer the larger Study Batch


## 2026-10-21 — W2D-01 V5 partial run / V6 transition fix

V5 advanced beyond all preflight/profiling gates and reached real training.

Measured V5 local-cache DDP:
```text
T4 x2 DDP
B1/A4 = 3.3115 studies/s
B2/A2 = 3.2483 studies/s
B4/A1 = 3.2364 studies/s
B8/A1 = 3.4417 studies/s  <-- selected
representative B8/A1 = 3.6468 studies/s
peak reserved = 8.99 GiB / 14.56 GiB
```

Epoch1 head warm-up completed:
```text
epoch=1
effective global batch=16
train loss=0.55959
elapsed=1.33 min
Synovitis sampled AUC=0.73128
Lateral OA sampled AUC=0.80042
checkpoint saved: w2d01_resume_last.pt
```

V5 failed at the first Epoch2 full-backbone step:
```text
RuntimeError: Non-finite grad norm at epoch=2 step=65
```

Interpretation:
- Not an OOM, DDP, HDF5 or runtime-limit failure.
- The failing gradient is computed before the optimizer LR update, so this specific first-step non-finite gradient cannot be attributed to LR magnitude applied by that step.
- The problematic transition reused the Epoch1 head-only optimizer/scheduler/GradScaler state when the full RadImageNet backbone was unfrozen.
- The head-only phase allowed the AMP scaler to evolve under a much easier gradient path; carrying that scaler into the first backbone backward is numerically fragile.

V6 fix:
- Keep measured fastest config fixed: T4x2, B8/GPU, Accum1, encoder chunk64, global batch16.
- Remove redundant profiling/smoke reruns.
- Epoch1 -> Epoch2 loads model weights only.
- Full-FT optimizer and scheduler are recreated.
- Full-FT GradScaler restarts at init_scale=1024.
- Standard AMP overflow behavior is respected: skip optimizer step and back off the scaler.
- Hard fail only after 8 consecutive overflow skips.
- LR contract unchanged: backbone max 4e-5, new modules 1e-3.
- Runtime-limit gate remains disabled.


## W2D-03 — Soft-Label + Diversity Regularization

상태: **PASS / TRAINING COMPLETE / GOLD58 DIAGNOSTIC COMPLETE**

W2D-01에서 확인된 과적합과 score saturation을 완화하기 위한 후속 specialist다.

Training source:
- W2D-00과 동일한 **1,075 studies / 6,014 Series**
- Gold58은 training에 사용하지 않음
- source Strict CSV의 hard 0/1 자체는 수정하지 않음

Training-time soft target:
```text
Synovitis   : 0 -> 0.10 / 1 -> 0.90
Lateral OA  : 0 -> 0.05 / 1 -> 0.95
```

Regularization / sampling:
```text
draws per epoch     = 1,200
max repeat/study    = 2
train K             = stochastic 6 / 8 / 10 / 12
slice dropout       = 0.10
series dropout      = 0.15
random crop         = OFF
horizontal flip     = OFF
Transformer dropout = 0.20
Head dropout        = 0.30
epochs              = 6 fixed
EMA decay           = 0.995
```

Primary checkpoint:
```text
w2d03_r50_ema_e6.pt
```

Gold58 diagnostic:

| variant | Macro AUROC (2 target) | Synovitis AUROC | Lateral OA AUROC |
|---|---:|---:|---:|
| **EMA E6** | **0.779490** | **0.756272** | **0.802708** |
| RAW E6 | 0.771753 | 0.756272 | 0.787234 |

Gold58는 checkpoint training/selection에 사용하지 않고 학습 종료 후 diagnostic으로만 평가했다.

### S13 hidden submission

W2D-03을 기존 CoAt384 + S6 target-balanced percentile-rank base에 두 target만 추가했다.

```text
Synovitis:
80% Base + 20% W2D-03

Lateral OA:
65% Base + 35% W2D-03
```

Fast subprocess 구조로 CoAt → S6 → W2D를 순차 실행하고 각 stage 종료 후 CUDA context를 정리했다.

실행 결과:
- submission generation PASS
- test preview 기준 controller runtime 약 **5.5 min**
- fixed Study-level 0.5 final fallback 사용하지 않음
- **Public LB = 0.955**

결론:
- W2D-03은 Gold58 diagnostic에서는 W2D-01 대비 개선된 specialist signal을 보였지만,
- 기존 0.955 CoAt384 + S6 계보에 추가했을 때 leaderboard 상승은 확인되지 않았다.



## W2D-05 — Final selected target specialists

**Status: GOLD58 DEVELOPMENT DIAGNOSTIC COMPLETE / MAIN SUBMITTED**

W2D-03 이후 추가된 최종 보강 실험에서 두 타깃의 별도 Stage checkpoint를 선택했다.

| Target | Selected checkpoint | Gold58 ROC-AUC |
|---|---|---:|
| Synovitis | Stage A RAW | **0.807646** |
| Lateral OA | Stage B RAW | **0.822050** |

- Gold58 개발 평가(n=58)는 공식 hidden-test/Private 점수가 아니다.
- 기존 W2D-03 Gold58 EMA 0.756272/0.802708은 이전 실험 이력으로 보존한다.
- 최종 MAIN은 공개 CoAt + R6 base에 위 W2D-05를 두 타깃 각각 **27.5%** percentile-rank 혼합.
- 해당 타깃: `Final = 0.725 × Base rank + 0.275 × W2D-05 rank`.
- 다른 10개 타깃은 기존 base 예측 유지.
- 최종 정상 MAIN 제출: **Public 0.958 / Private 0.941**, 공식 최종 순위 **949위**.
- Public 0.958은 기존 점수와 동일해 추가 Public 상승은 확인되지 않았다.

## 2026-10-23 — Competition close / final leaderboard

상태: **COMPETITION CLOSED / NO FURTHER EXPERIMENTS**

마지막 submission set:
- **MAIN 버전만 정상 제출 성공**
- MAIN Public LB = **0.958**
- 대회 중 Public leaderboard 최고 위치 = **약 240위**

대회 종료 후 Private:
- Final MAIN Private LB = **0.941**
- 공식 최종 순위 = **949위**

따라서 Public 0.958은 대회 중 최고 Public 성과로 기록하되,
최종 공식 결과는 **Private 0.941 / 949위**로 고정한다.

Weak2 포함 모든 후속 tuning은 종료한다.
