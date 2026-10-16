# Branch-C ConvNeXt Anatomy Expert — Authoritative Design & Roadmap

최종 갱신: **2026-10-17**  
상태: **DESIGN_FROZEN / NOT_RUN**

---

## 1. 역할

Branch-C는 세 번째 독립 전문가다.

```text
A = DINO Core
B = CoAtNet Wide-MRI Expert
C = ConvNeXt Anatomy Expert
```

C의 목적은:
- DINO selector와 독립
- CoAtNet fixed 96-slot과도 독립
- **window 내부 spatial localization + Study 내부 window selection**을 동시에 학습
- Full FOV와 anatomy-centered local view를 함께 사용
- CNN inductive bias로 Transformer/CoAtNet과 다른 error pattern 생성

---

## 2. 성능 가설

### C-H1 — Two-level attention
Window 전체를 하나의 feature로 평균하기 전에 **target-specific spatial attention**으로 window 내부 위치를 고른다.
그 뒤 Study 전체 windows 사이에서 다시 target-specific MIL attention을 한다.

```text
pixel/feature-map spatial attention
→ target-specific window feature
→ target-specific window attention
→ prediction
```

### C-H2 — Global + local view complementarity
Full FOV는 anatomy context와 large lesion을 유지하고, 100mm local view는 cartilage/meniscus/ACL/PF/Baker 영역의 effective resolution을 높인다.

### C-H3 — Physical slice spacing
thin 3D stack을 index 단위로 과밀 sampling하지 않고 약 3.5mm slab로 변환해 2D acquisition과 비슷한 physical depth representation을 만든다.

---

## 3. 학습 데이터 / 라벨

Branch-B와 동일한 label universe를 사용해 architecture/input 차이를 비교 가능하게 한다.

- Report studies 4,349: train
- Gold58: train 금지, dev gate
- 최신 검증 완료 B soft-label dataset
- `mask=0` excluded
- confidence/weight 유지
- 실행 전에 path + SHA 반드시 고정
- 임의 다른 pseudo-label로 교체 금지

---

## 4. Native source / geometry

가능하면 raw DICOM에서 매번 재처리하지 않고 **native physical-order cache**를 기반으로 view cache를 만든다.

필수 native metadata:
- StudyInstanceUID
- SeriesInstanceUID
- plane
- slice physical positions
- pixel spacing
- side/orientation
- fluid-sensitive
- fat-suppression
- native shape

원본이 불완전하면 raw competition DICOM으로 fallback하되, 동일 geometry contract를 유지한다.

---

## 5. Thin-stack physical depth handling

Series slice spacing:
- median physical spacing 계산
- `0 < spacing < 1.75 mm`이면 thin 3D stack으로 간주

thin stack:
```text
target slab ≈ 3.5 mm
group_size = round(3.5 / spacing)
인접 slice 평균
```

너무 작은 remainder는 버리고, 충분한 remainder는 마지막 slab으로 포함한다.

목적:
- 0.4~1.5mm 3D MRI에서 거의 같은 위치의 slice가 window budget을 점유하는 문제 방지
- physical receptive depth 통일

---

## 6. Anatomy anchor

Branch-C는 local crop 중심을 단순 image center로만 잡지 않는다.

Primary:
- public/available knee anatomy segmentation model(SK-MTEA 계열 등)로 joint center와 patella reference 추정
- 여러 sagittal candidate가 있으면 world-coordinate consensus
- 각 Series DICOM geometry로 projection

Fallback:
1. segmentation anchor
2. orthogonal slab geometry prior
3. field center

이 anchor는 label-free preprocessing으로만 사용한다.

실행 전:
- exact segmentation checkpoint
- license/availability
- SHA
- Kaggle offline mount
를 확인한다.

만약 segmentation artifact를 확보하지 못하면 **Branch-C 전체를 단순 center-crop baseline으로 축소하지 않는다.** anatomy branch의 핵심 가설이 깨지므로 실행을 보류하고 문서를 갱신한다.

---

## 7. View set

### Sagittal / Axial
기본:
- View 0: **Full FOV**
- View 1: **100mm joint-centered local**

성능/시간 허용 시:
- PF local: patella/anterior reference 중심
- posterior local: Baker/PCL/poplietal region

### Coronal
기본:
- Full FOV
- 100mm medial local
- 100mm lateral local

처음부터 모든 fancy view를 무조건 넣기보다 **고득점 가설에 필요한 Global + Joint Local을 필수**, PF/posterior는 cache 용량과 anchor reliability가 확인되면 포함한다.

현재 V1 권장:
```text
Sagittal: full + joint-local
Axial:    full + joint-local
Coronal:  full + medial-local + lateral-local
```

---

## 8. Pixel preprocessing

### Cache resolution
- render/cache: **320×320 uint8**

### Intensity
Series display/intensity mapping은 Branch-B와 완전히 같게 강제하지 않는다.
Branch-C 기본:
- modality LUT
- MONOCHROME1 inversion
- robust per-Series mapping
- output [0,255] uint8

최종 percentile/windowing recipe는 cache preflight에서 user-supplied high-score ConvNeXt code와 우리의 native cache parity를 비교해 고정한다.

### Training crop
```text
320 → random 288
```

### Inference
```text
320 → center 288
```

---

## 9. Window construction / bag

각 window는 physical-order 3-slice input.

```text
[c-1, c, c+1]
```

thin-stack slab conversion 후 만든 slice sequence를 사용한다.

### Budget
**64 windows / Study**

1차 quota:
```text
Global views ≈ 32
Local views  ≈ 32
```

배분 순서:
1. 모든 valid Series 최소 1
2. 모든 plane coverage
3. 각 view coverage
4. 남은 budget을 slice/span에 비례 배분
5. relative-position이 한쪽에 몰리지 않게 stratified selection

S8C contribution/Top18은 사용하지 않는다.

---

## 10. Model architecture

### Backbone
```text
timm ConvNeXt-Small
pretrained ImageNet-22k/1k 계열
full fine-tuning
```

실행 전 timm model name과 pretrained checkpoint identity를 실제 Kaggle offline artifact 기준으로 고정한다.

### Spatial attention
ConvNeXt 마지막 feature map:
```text
[B, C, H, W]
```

Target별 spatial logits:
```text
Conv1x1 / lightweight target projection
→ [B, 12, H, W]
→ spatial softmax
```

각 target별 pooled window feature:
```text
f_window[target, C]
```

### Window MIL attention
64 window에 대해 target별 attention:
```text
LayerNorm
+ metadata embedding
→ MLP
→ 12 window-attention logits
→ softmax over windows
```

Metadata는 attention에만 보조적으로 사용:
- plane
- view type
- relative slice position
- log slice spacing
- fluid-sensitive
- fat-suppression

classifier feature 자체에 metadata를 직접 concatenate하지 않는 것을 V1 기본으로 한다.

---

## 11. Loss / imbalance

Branch-B와 동일한 base policy.

```text
masked confidence-weighted soft BCE
```

class balance:
```text
P_t = Σ(w×y)
N_t = Σ(w×(1-y))
ratio = (N_t/P_t)^0.70
clip [0.5, 2.5]
```

Rare-positive sampling:
- MCL 3.0×
- Fracture 2.5×
- Contusion 2.0×
- Baker's 1.5×
- PF OA 1.5×
- others 1.0×

strong positive gate:
```text
y >= 0.65 AND confidence >= 0.50
```

복수 rare target은 max multiplier만 사용.

---

## 12. Data augmentation

### Geometry
- RandomCrop: 320→288
- Rotation: ±10°
- Scale: 0.90–1.10

### Intensity
- Gamma: 0.80–1.25
- Contrast/Gain: 0.90–1.10

### Resolution robustness
p=0.25:
```text
downsample factor 1.25~2.0
→ upsample back
```

목적: scanner/resolution 차이 robustness.

### 금지
- MixUp
- CutMix
- Random Erasing
- arbitrary strong blur
- generic train-time horizontal flip

anatomical mirror는 inference TTA로 분리한다.

---

## 13. Training hyperparameters

| 항목 | 값 |
|---|---|
| Epoch | **16 fixed** |
| Early stopping | **없음** |
| Windows | **64 / Study** |
| Physical Study batch | **2 목표** |
| Effective Study batch | **2 고정** |
| Backbone LR | **1.0e-4** |
| Spatial/MIL/head LR | **1.0e-3** |
| Optimizer | AdamW |
| Weight decay | **0.05** |
| Scheduler | cosine |
| Warmup | **5%** |
| Gradient clip | **5.0** |
| Precision | FP16 |
| Seed | 42 |

### GPU memory policy
window backbone microbatch benchmark:
```text
32 preferred
16 acceptable
8 minimum
1 forbidden
```

Study batch 2가 OOM이면:
```text
physical batch 1
grad accumulation 2
effective batch 2 유지
```

---

## 14. Full-data model policy

V1은 2-fold ensemble로 시작하지 않는다.

```text
4,349 report studies full train
Gold58 excluded
single ConvNeXt serving model
```

이유:
- 시간이 제한적
- Branch-C의 역할은 동일-family fold ensemble보다 architecture diversity 확보
- high-score references에서도 all-data ConvNeXt 모델이 강한 사례가 있었음

Checkpoint:
- every epoch 저장
- Gold58 global macro AUROC로 candidate 확인
- 필요하면 top-2/3 epoch parameter average
- per-target checkpoint cherry-pick 금지

---

## 15. Inference / TTA

Primary:
```text
64 windows
→ spatial attention
→ window MIL
→ 12 probabilities
```

TTA:
- plain
- anatomical mirror
- medial/lateral semantic outputs swap-back
- logit 또는 probability 평균은 **public DEV/LB 비교 후 하나로 고정**
- MCL plain-only 후보 별도 비교 가능

Branch-C standalone은 TTA off/on을 둘 다 기록한다.

---

## 16. Cache capacity planning

Branch-C cache는 Study마다 Series 수와 view 수가 달라 Branch-B보다 row 수 변동이 크다.

따라서 Pack 수를 문서에서 임의로 고정하지 않는다.

cache preflight에서:
1. 4,407 Study 전체 예상 row count
2. 320×320 uint8 bytes
3. metadata bytes
4. 20GB saved-output headroom
을 계산한다.

Pack 목표:
```text
15~17 GB raw pixels / pack 이하
```

압축에 기대어 1개 output에 몰아넣지 않는다.

---

## 17. Evaluation / ensemble

필수:
1. C standalone
2. C mirror TTA
3. A+C rank blend
4. B 완료 시 A+B+C rank blend

prediction correlation:
- corr(A,C)
- corr(B,C)
- target-wise rank correlation

최종 후보:
```text
R_A = per-target percentile rank(A)
R_B = per-target percentile rank(B)
R_C = per-target percentile rank(C)
```

초기 3-branch heuristic:
```text
A 0.50
B 0.30
C 0.20
```

단, 이는 최종 확정값이 아니다.
실제 standalone LB와 complementarity를 본 뒤 global 또는 target-wise fixed weights로 결정한다.

---

## 18. 실행 순서

Branch-C는 Branch-B 뒤에 진행.

1. Branch-B standalone/A+B 결과 확인
2. anatomy segmentation artifact 확보 및 SHA 고정
3. C cache preflight
4. Global+Local cache build
5. integrity QA
6. ConvNeXt 16ep full-data training
7. checkpoint selection/average
8. standalone submission
9. anatomical mirror TTA
10. A+C / A+B+C rank blend
11. 결과 EXPERIMENT_LOG 누적

---

## 19. 실행 전 Gate

- label artifact SHA
- Gold58 exclusion
- anatomy checkpoint SHA/license/offline access
- DICOM geometry integrity
- thin-stack slab parity
- view-coordinate sanity
- cache row counts
- Full/Local ratio
- target order
- pretrained ConvNeXt identity
- GPU microbatch benchmark
- no silent Study-level 0.5 fallback in diagnostic version
- final submission robust-reader policy 별도 명시

---

## 20. 외부 참고에서 채택한 아이디어

사용자가 제공한 고득점 ConvNeXt 자료에서 확인된 패턴:
- ConvNeXt-Small
- multiple folds/TTA가 ensemble component로 활용됨
- full FOV + 100mm local views
- coronal bilateral local views
- thin stack → physical slab
- anatomy anchor
- target-specific spatial attention
- window MIL
- 64 windows/Study
- 288 training/inference crop 계보
- rare target oversampling
- Effusion/Baker 특화 state 처리 사례

우리 V1에서는 과도한 특수 head/staker를 처음부터 붙이지 않고 **spatial attention + window MIL + anatomy views**까지를 core architecture로 본다.
Effusion/Baker 전용 auxiliary stacker는 C core 결과가 나온 뒤 필요할 때만 추가한다.

---

## 21. 새 채팅 시작점

새 채팅에서는:
1. `docs/CURRENT_HANDOFF.md`
2. 이 문서
3. `CONVNEXT_EXPERIMENT_LOG.md`
를 읽는다.

Branch-C의 바로 다음 작업은 Branch-B가 완료된 뒤 **anatomy checkpoint를 실제 확보하고, Global+Local 320 cache의 row/Pack preflight를 설계하는 것**이다.
