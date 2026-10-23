# Weak2 Direct Specialist — Roadmap

최종 업데이트: 2026-10-23

## FINAL STATUS — Competition closed

> **ARCHIVED / NO NEXT RUN**
>
> 대회는 2026-10-23 기준 종료되었다. 이 문서 아래의 `Next`, `execution plan`, `training pending`은 당시 계획을 보존한 역사적 기록이며 더 이상 실행하지 않는다.

Weak2 최종 흐름:
- W2D-00 all-Series cache PASS
- W2D-01 계열에서 loader / I/O / orchestration / AMP transition 문제를 진단 및 수정
- W2D-03 SoftReg specialist training PASS
- W2D-03 Gold58 EMA E6: Synovitis **0.756272**, Lateral OA **0.802708**, macro **0.779490**
- W2D-03 target injection submission: **Public 0.955**, 기존 0.955 base 대비 gain 없음
- **W2D-05 final specialist:** Gold58 활막염 Stage A RAW **0.807646**, 외측 골관절염 Stage B RAW **0.822050** (두 타깃 모두 0.8 이상)
- 마지막 MAIN: 공개 CoAt + R6 base에 W2D-05를 두 타깃 각각 **27.5%** 혼합, Public **0.958** (기존과 동일), Private **0.941**
- 이후 최종 전체 계보의 MAIN submission은 **Public 0.958 / Private 0.941**
- 공식 최종 순위 **949위**

결론:
- Weak2 추가 실험은 종료.
- Public LB를 위한 추가 specialist weight search를 하지 않는다.
- 향후 아이디어 재사용 시 별도 프로젝트로 분리한다.
- 대회 최종 요약은 [../FINAL_COMPETITION_SUMMARY.md](../FINAL_COMPETITION_SUMMARY.md)를 따른다.

## Current goal

CoAt384 + S6F0의 약한 두 타깃인 **Synovitis / Lateral OA**만 보강하는 selector-free single model을 만든다.

Backbone:

```text
RadImageNet ResNet50
```

Final operating contract:

```text
1 additional predictor model
2 target outputs
0 learned selector checkpoints
0 fold ensemble
```

## Current status

### W2D-00 — Strict All-Series CPU Cache

상태: **PASS — cache dataset published**

목적:

- Strict V1 hard 0/1만 사용
- Gold58 완전 제외
- 1,075-study frozen train pool 생성
- 모든 Series 보존
- 150 mm center FOV / 320px / K16 per Series cache 생성
- GPU quota 0 사용

Expected contract:

```text
Studies = 1,075
Series  = 6,014 expected from Strict metadata
Synovitis = 511P / 35N
Lateral OA = 66P / 700N
```

Kaggle setting:

```text
Accelerator: None (CPU)
Internet: Off
Save & Run All
Save Version: W2D-00 Strict All-Series Cache 320
```

실행 결과:

```text
Dataset: /kaggle/input/datasets/yhlucas/rsna-knee-w2d00-strict-allseries-cache320-v1
Runtime: 30.08 min
Studies: 1,075
Series: 6,014
HDF5 structural gate: PASS
Decode failures: 0
PixelSpacing missing: 0
Unknown laterality Series: 492
```

## Next — W2D-01 RadImageNet R50 DDP

W2D-00가 PASS했으므로 다음 단계로 진행한다.

목표:

```text
single RadImageNet R50
+ target-specific slice/series attention
+ Synovitis head
+ Lateral OA head
```

GPU:

```text
T4 ×2
DDP
single model
```
Model pretraining input for W2D-01:

```text
Kaggle Dataset: marwanmath/resnet-50-radimagenet-marwan
Required file: ResNet50.pt
```

This is added through Kaggle **Add Input → Datasets**, not Kaggle Models. The W2D-01 notebook must resolve the exact mounted path under that dataset root and strict-load the RadImageNet ResNet50 trunk.


학습 전에 반드시:

- full pipeline DDP 2 optimizer-step smoke
- actual GPU peak allocated/reserved
- studies/sec, series/sec, slices/sec
- DataLoader/HDF5 wait time
- batch candidate throughput benchmark
- 예상 epoch / total runtime
- checkpoint save/load/resume dry-run

을 확인한다.

## Training data imbalance policy — planned

Cache에는 unique study를 한 번만 저장한다.

학습 때만 dynamic sampler를 사용한다.

### Synovitis

Raw strict pool:

```text
511 positive
35 negative
```

- 35 negative를 모두 보존
- minority negative를 여러 번 draw
- draw마다 slice subset / mild intensity augmentation을 새로 생성
- moderate class weight 추가
- oversampling × class weight를 동시에 inverse-frequency 수준으로 과도하게 적용하지 않음

### Lateral OA

Frozen pool:

```text
66 positive
700 negative
```

- positive dynamic oversampling
- negative 700은 fixed V1 pool
- positive draw마다 다른 slice/intensity realization
- moderate positive class weight

## Gold58 policy

Gold58은 W2D 계보의 train/cache selection/optimization/checkpoint choice에 사용하지 않는다.

최종 checkpoint를 먼저 고정한 뒤 diagnostic comparison을 1회 수행한다.

## Stop conditions

- W2D-00 cache contract가 맞지 않으면 GPU 학습 금지
- DDP smoke가 2 optimizer step 이상 통과하지 못하면 본학습 금지
- OOM / non-finite loss / non-finite gradient / checkpoint-resume failure는 본학습 금지
- **예상 runtime만으로는 더 이상 학습을 중단하지 않는다.**


## W2D-01 proposed run contract

```text
Epochs: 10 fixed
Early stopping: OFF
Train draws/epoch: 1,024
Train slices/Series: stochastic-stratified K8 from cached K16
Inference slices/Series: K16
Optimizer: AdamW
Head/new-module LR: 1e-3
Backbone max LR: 4e-5 (layer-wise 5e-6 / 1e-5 / 2e-5 / 4e-5)
Epoch 1: backbone frozen, new modules only
Epoch 2–10: full backbone discriminative FT
AMP: FP16 backbone + FP32 aggregation/head
Gradient clip: 1.0
Scheduler: 5% warmup + cosine
Primary checkpoint: EMA decay 0.995, frozen after Epoch 10
```

DDP preflight chooses among per-GPU Study Batch 1/2/4 while holding Global Effective Batch at 8 using gradient accumulation. The candidate must complete at least two full optimizer steps and report peak allocated/reserved VRAM plus throughput before the full run begins.

Primary checkpoint naming:

```text
w2d01_r50_ema_e10.pt
w2d01_resume_last.pt
```

No Gold58 metric is used during training or checkpoint selection.


### W2D-01 Notebook prepared — 2026-10-21

상태: **Notebook prepared / Kaggle execution pending**

Notebook delivery name:

```text
W2D-01_RadImageNet_R50_DDP_Strict.ipynb
```

Recommended Kaggle Save Version:

```text
W2D-01 R50 Weak2 DDP Strict V1
```

Runtime:

```text
Accelerator: T4 x2
Internet: Off
Save & Run All
```

The notebook automatically:
- verifies exact cache / Strict / RadImageNet inputs
- profiles encoder slice microbatch 32/64/96/128
- profiles per-GPU Study Batch 1/2/4 at Global Effective Batch 8
- runs a representative throughput probe
- runs real save→load→continue resume smoke
- stops before training when projected runtime exceeds the 4-hour W2D gate
- trains Epoch1 head-only at LR 1e-3
- trains Epoch2–10 full discriminative FT with backbone max LR 4e-5 and new modules LR 1e-3
- writes `w2d01_resume_last.pt`, `w2d01_r50_raw_e10.pt`, and primary `w2d01_r50_ema_e10.pt`

GitHub remains documentation-only; notebook source is not committed.


### W2D-01 V2 status — 2026-10-21

V1 did not reach Epoch 1. DDP profiling passed, but the resume-smoke load failed because PyTorch 2.6 defaults `torch.load` to `weights_only=True` while the internally generated resume checkpoint contains optimizer/RNG state.

V2:
- trusted internal resume checkpoints: explicit `weights_only=False`
- RadImageNet external weight: weights-only strict load unchanged
- near-tied encoder chunks use lower-VRAM tie-break. V1 measurements make chunk64 the expected selection instead of chunk96.
- per-GPU Study Batch1 / GradAccum4 remains the expected batch winner from V1 profile.
- full training settings/LR/epochs/EMA remain unchanged.

## W2D-01 V3 execution plan

V2는 resume smoke까지 PASS했으나 remote HDF5 random I/O 때문에 runtime gate에서 중단되었다. 본학습은 시작되지 않았다.

V3는 다음을 고정한다.

```text
HDF5 stage: /kaggle/input → /kaggle/temp/w2d01_cache
per-GPU Study Batch = 1
GradAccum = 4
Encoder chunk = 64
Effective Global Batch = 8
```

Local-cache warm-up과 representative timed probe 후 10-epoch 예상시간이 4시간 이내일 때만 Epoch 1을 시작한다.


## W2D-01 V4 execution plan — 2026-10-21

V4는 사용자의 GPU-headroom 지시에 따라 runtime gate와 batch policy를 수정한다.

```text
HDF5 local staging: /kaggle/temp/w2d01_cache
Encoder chunk: 64 fixed
Batch candidates after staging:
  B1 / Accum4 → Effective Global 8
  B2 / Accum2 → Effective Global 8
  B4 / Accum1 → Effective Global 8
  B8 / Accum1 → Effective Global 16
```

Selection:
- actual local-cache forward/backward/optimizer throughput 기준
- reserved VRAM < 92%
- OOM/failed candidate 제외
- best throughput의 5% 이내라면 더 큰 per-GPU Study Batch 우선

Runtime:
- 예상시간은 로그에만 출력
- 4 h / 8 h projected-runtime gate 제거
- actual numerical / OOM / resume safety gate만 유지

Notebook delivery:
```text
W2D-01_RadImageNet_R50_DDP_Strict_V4.ipynb
Save Version: W2D-01 R50 Weak2 DDP Strict V4
```
