# Weak2 Direct Specialist — Roadmap

최종 업데이트: 2026-10-21

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
- 예상 single-run 학습시간이 4시간을 크게 초과하면 batch/I/O를 먼저 최적화
- 8시간 이상 예상이면 본학습 시작 금지


## W2D-01 proposed run contract

```text
Epochs: 10 fixed
Early stopping: OFF
Train draws/epoch: 1,024
Train slices/Series: stochastic-stratified K8 from cached K16
Inference slices/Series: K16
Optimizer: AdamW
AMP: FP16
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
