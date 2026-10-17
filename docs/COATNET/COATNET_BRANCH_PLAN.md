## 2026-10-17 — Branch-B cache PRE-FLIGHT Notebook 준비

Notebook:
`B_COATNET_WIDE96_CACHE_PREFLIGHT_V1.ipynb`

SHA256:
`4b007a789f5c2937a71a1485b4bbe9ef962acad7befc8de7bbd68766ef3914d8`

정적 QA PASS, 14,716 bytes.

PRE-FLIGHT가 실제 Kaggle에서 확인하는 항목:
- Competition `train_series.csv` 원래 순서 + shared 24,371-Series metadata merge
- 5 fixed slots: 26/22/18/12/18
- used Series 재사용 금지
- preferred fluid type 없으면 same-plane fallback
- unused same-plane Series도 없으면 missing slot
- missing slot = future cache zero + valid_mask=0
- selected-slot manifest
- 140mm FOV header-only audit
- sorted UID modulo-4 partition
- Pack별 exact byte budget
- 19GB output safety gate

현재 기존 4,407 metadata에서 확인된 구조적 missing:
- 두 번째 Sagittal Series가 없는 Study: **119**
- 두 번째 Coronal Series가 없는 Study: **1,124**
- Axial Series missing: **0**
이 값은 실제 PRE-FLIGHT에서 competition-order 기반 manifest로 다시 확인한다.

PRE-FLIGHT PASS 후에만 Pack00~03 실제 pixel cache builder 4종을 생성한다.


## 2026-10-17 — 96×384 cache Pack 수 PRE-FLIGHT 확정

Branch-B cache는 **4 Pack**으로 확정한다.

### Exact raw byte calculation

고정 cache shape:
```text
4,407 Studies × 96 slices × 384 × 384 × uint8
= 62,384,504,832 bytes
= 62.3845 GB
= 58.1001 GiB
```

3 Pack:
- 1,469 Studies/Pack
- **20.795 GB / 19.367 GiB** raw
- 19GB saved-output 안전선 초과 → **불가**

4 Pack:
- Study counts: **1102 / 1102 / 1102 / 1101**
- 최대 raw: **15.600 GB / 14.528 GiB**
- 10% headroom + 300MB metadata를 잡아도 최대 약 **17.46 GB**
- 19GB output cap 아래 → **채택**

5 Pack:
- 약 12.47~12.49GB raw/Pack
- 안전하지만 job 수만 증가
- 4 Pack이 충분한 headroom을 가지므로 **불필요**

### Partition contract

```text
sorted StudyInstanceUID
→ row_index % 4
→ Pack00~03
```

예상 Study:
- Pack00 1102
- Pack01 1102
- Pack02 1102
- Pack03 1101

### HDF5 primary shape

각 Pack:
```text
/pixels     [NStudy, 96, 384, 384] uint8
/valid_mask [NStudy, 96] uint8/bool
```

Metadata는 CSV/JSON에 분리:
- study_manifest.csv
- slice_manifest.csv
- slot_manifest/contract
- cache_contract.json
- run_status.json
- file_sha256.json
- review ZIP (HDF5 제외)

HDF5 compression은 V1에서 사용하지 않는다.
Pack별 raw output을 이미 약 15.6GB로 제한했기 때문에 CPU build/read 속도를 우선한다.

### Disk gate

각 Notebook은:
```text
OUTPUT_CAP = 19_000_000_000
PHYSICAL_RESERVE >= 2_000_000_000
anticipated = raw_bytes * 1.10 + 300MB
```
를 사용해 write 전에 fail-fast한다.

### 다음 Branch-B 작업

S11 학습과 병렬 또는 직후:
1. raw competition DICOM / train_series schema preflight
2. 5 anatomical Slot Series-selection rule 실제 dataset coverage audit
3. 96-slice sampling 결과의 missing/fallback 분포 확인
4. 140mm/384 + Series p2/p98 normalization parity/sample montage audit
5. PASS 후 **4개 cache-build Notebook** 생성

현재는 Pack 수/partition/output contract만 확정. 실제 cache build는 아직 NOT_RUN.


# Branch-B CoAtNet Wide-MRI Expert — Authoritative Design & Roadmap

최종 갱신: **2026-10-17**  
상태: **DESIGN_FROZEN / NOT_RUN**  
이 문서는 Branch-B의 authoritative 설계 문서다. 실행 전에 변경이 생기면 여기부터 수정한다.

---

## 1. 프로젝트 전체에서의 위치

현재 Branch-A는 다음 구조다.

```text
Stage1 DINOv2-Base 2F
  ↓
Full-MRI feature
  ↓
S8C MIL 2F
  ├─ Full-MRI direct prediction
  └─ label-free Top18 selector
        ↓
S10/S11 DINOv2-Base Top18 FT 2F
        ↓
DINO Core
```

현재 최고 제출:
```text
0.70 × S10 LAST 2F
+ 0.30 × S8C Full-MRI Direct 2F
= Public LB 0.926
```

Branch-B는 위 파이프라인의 Stage4가 아니다.

```text
Branch-A = DINO Core
Branch-B = CoAtNet Wide-MRI Expert
Branch-C = optional ConvNeXt Anatomy Expert

최종 = independent experts의 rank-space ensemble
```

핵심 목적은 **같은 Top18을 다른 backbone으로 다시 보는 것**이 아니라, 입력 선택 자체를 다르게 하여 Branch-A와 오류 상관성을 낮추는 것이다.

---

## 2. 성능 가설

### B-H1 — Dense MRI coverage
DINO Core는 S8C가 중요한 위치를 선택해 Top18을 재판독한다. Branch-B는 반대로 sagittal/coronal/axial과 fluid/non-fluid를 고정 Slot으로 확보하고 MRI 범위를 넓게 읽는다.

따라서:
- DINO가 놓친 peripheral lesion을 CoAtNet이 보완할 수 있다.
- selector 오류를 독립적으로 회피할 수 있다.
- standalone LB가 Branch-A보다 낮더라도 ensemble gain이 날 수 있다.

### B-H2 — CoAtNet + target-specific MIL
각 3-slice window를 CoAtNet으로 encode한 뒤 12개 질환별 attention을 별도로 학습한다.
ACL, meniscus, OA, effusion, Baker's 등은 서로 필요한 slice가 다르므로 shared pooling보다 target-specific attention이 적합하다는 가설이다.

### B-H3 — 다른 intensity/geometry contract
Branch-A의 Native224 V3(.5/99.5 + z-score + 130mm)와 달리:
- 140mm physical crop
- Series 2/98 percentile mapping
- 384 native cache → train crop 320
을 사용한다.

backbone뿐 아니라 입력 표현까지 달라 ensemble diversity를 확보한다.

---

## 3. 학습 데이터 / 라벨 정책

### Study universe
- **Report studies 4,349개**: 학습
- **Gold58**: 학습 금지, model/checkpoint/SWA selection용 clean gate
- 같은 Study가 train/Gold 양쪽에 들어가면 즉시 중단

### 라벨
주 라벨은 **최신 검증 완료 B soft-label dataset**을 사용한다.

중요:
- 현재 이 문서 작성 시점에는 해당 최종 artifact의 Kaggle dataset path/SHA가 고정되지 않았다.
- 실행 노트북 생성 전에 반드시 실제 파일을 붙이고:
  - row count
  - Study UID universe
  - 12 target columns
  - label / confidence / mask schema
  - SHA-256
  를 문서와 notebook gate에 고정한다.
- 임의로 V4나 다른 pseudo label로 대체하지 않는다.

### Soft-label
- hard 0/1로 재이산화하지 않는다.
- ambiguity를 확률로 유지한다.
- `mask=0`은 loss에서 완전히 제외한다.
- confidence/weight가 존재하면 그대로 loss weight에 포함한다.

---

## 4. Branch-B 입력 구성 — 96-slice anatomical volume

Study마다 최대 5개의 anatomical Slot을 고정한다.

| Slot | 우선 Series | Slice 수 |
|---|---|---:|
| S0 | Sagittal fluid-sensitive | 26 |
| S1 | Sagittal non-fluid | 22 |
| S2 | Coronal fluid-sensitive | 18 |
| S3 | Coronal non-fluid | 12 |
| S4 | Axial | 18 |
| **합계** |  | **96** |

Series 선택:
1. plane 일치
2. fluid/non-fluid 요구가 있으면 해당 조건 우선
3. 이미 사용한 Series는 재사용하지 않음
4. preferred Series가 없으면 같은 plane의 다른 Series로 fallback
5. Slot 자체가 없으면 zero/mask slot으로 남기되 Study 전체를 버리지 않음

### Slice span
각 선택 Series에서 중앙 구간만 쓰지 않는다.

```text
lo = floor(0.02 × N)
hi = floor(0.98 × N) - 1
```

그 구간에서 Slot의 k개 slice를 균등 sampling한다.

목적:
- MCL/LCL/meniscus 등 peripheral anatomy 손실 방지
- Full-MRI coverage 확대

### DICOM order
우선순위:
```text
IOP + IPP physical position
→ InstanceNumber
→ natural filename
```

개별 header 실패는 Series 전체 fail로 확대하지 않는다.

---

## 5. Branch-B preprocessing contract

### DICOM
1. modality LUT
2. MONOCHROME1이면 intensity inversion
3. physical-mm crop
4. resize
5. Series-level intensity normalization

### Geometry
- physical crop: **140 mm**
- cache resolution: **384×384**
- crop center: image center
- requested 140mm가 image FOV보다 크면 available FOV까지만 사용하고 임의 black expansion은 하지 않는 방향을 기본으로 한다. 실행 전 cache parity test에서 확정한다.

### Intensity
선택된 Series slice들의 raw intensity를 모아:
```text
lo = percentile 2
hi = percentile 98
x = clip((x-lo)/(hi-lo+1e-6), 0, 1)
uint8 = round(x×255)
```

ImageNet normalization은 model input 직전에 적용한다.

### Cache
논리 형태:
```text
Study → [96, 384, 384] uint8 + [96] valid mask + slot metadata
```

raw pixel 용량 추정:
```text
4,407 × 96 × 384 × 384 uint8 ≈ 62 GB
```

따라서 20GB급 Kaggle saved-output 제약을 고려하면 **4~5 Pack**이 현실적이다.
- 4 pack이면 대략 15~16GB raw/pack
- 5 pack이면 대략 12~13GB raw/pack

실제 notebook 생성 전 Study별 정확한 row/output byte 계산으로 Pack 수를 최종 확정한다.

---

## 6. Training window sampling

### Train
Study당 **12 windows / epoch**.

각 window:
```text
[c-1, c, c+1] → 3 channels
```

sampling:
- 존재하는 5 Slot 각각 최소 2 windows 우선
- 남는 budget은 모든 valid candidate에 재분배
- epoch마다 중심 위치를 다시 sampling
- 동일 Study의 12 windows는 한 attention bag을 이룸

### Validation / Inference
96-slice representation에서 가능한 **94개 center**를 dense 사용한다.

즉:
```text
TRAIN = stochastic 12-window bag
INFERENCE = dense 94-window bag
```

의도:
- train stochasticity = regularization
- inference dense coverage = lesion miss 감소

---

## 7. Model architecture

### Backbone
```text
timm:
coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k
```

- ImageNet 계열 pretrained initialization
- **Full fine-tuning**
- backbone freeze baseline은 하지 않음

### MIL head

```text
3-slice window
  ↓
CoAtNet backbone
  ↓
feature F
  ↓
LayerNorm(F)
  ↓
Linear(F→256)
  ↓
Tanh
  ↓
Dropout(0.20)
  ↓
Linear(256→12)
  ↓
target-specific attention logits
  ↓ softmax over windows
12 × pooled feature
  ↓
12 independent classifier weights
  ↓
12 logits
```

한 target의 attention은 다른 target의 attention과 공유하지 않는다.

---

## 8. Loss / class imbalance

기본 loss:
```text
masked confidence-weighted soft BCE
```

각 Study/target:
```text
loss_st = BCEWithLogits(logit_st, soft_label_st)
loss_st *= label_confidence_st
loss_st *= mask_st
loss_st *= class_balance_st
```

### class balance
training pseudo studies만 사용해 target별 expected positive/negative mass를 계산:

```text
P_t = Σ(w × y)
N_t = Σ(w × (1-y))
ratio_t = (N_t / P_t)^0.70
class scale clip = [0.5, 2.5]
```

target별 평균 loss scale이 지나치게 달라지지 않게 normalization한다.

### Rare-positive Study sampling
강한 positive:
```text
soft label >= 0.65
AND confidence >= 0.50
```

Study sampling multiplier:
- MCL: **3.0×**
- Fracture: **2.5×**
- Contusion: **2.0×**
- Baker's: **1.5×**
- PF OA: **1.5×**
- others: **1.0×**

여러 rare target을 동시에 가진 Study는 multiplier를 곱하거나 합산하지 않고 **max multiplier 하나만 적용**한다.

목적:
- 희귀 양성의 optimizer exposure 증가
- loss weighting만으로 부족한 rare-target batch 빈도 보강

---

## 9. Data augmentation

384 cache에서 on-the-fly로 수행.

### Spatial
- RandomCrop: **384 → 320**
- Rotation: **±10°**
- Scale: **0.90–1.10**

### Intensity
- Gamma: **0.80–1.25**
- Contrast/Gain: **0.90–1.10**

### 금지
- generic horizontal flip
- vertical flip
- MixUp
- CutMix
- Random Erasing
- strong blur

같은 Study의 12 windows에는 geometry transform을 일관되게 적용해 Study-level anatomy를 깨뜨리지 않는다.

---

## 10. Training hyperparameters

| 항목 | 값 |
|---|---|
| Epoch | **16 fixed** |
| Early stopping | **없음** |
| Physical Study batch | **1** |
| Grad accumulation | **16** |
| Effective Study batch | **16** |
| Train windows | **12 / Study** |
| Val windows | **94 / Study** |
| Backbone LR | **4.0e-5** |
| MIL/head LR | **2.0e-3** |
| Optimizer | AdamW |
| Weight decay | **0.06** |
| Scheduler | Cosine |
| Warmup | **5% total steps** |
| Gradient clip | **5.0** |
| Precision | FP16 autocast |
| Seed | 42 |
| GPU target | Kaggle T4×2 |

GPU 사용:
- Fold training이 아니라 단일 all-pseudo model이므로 두 GPU를 억지 DDP로 묶지 않는다.
- 가장 먼저 2×T4에서 **data/preprocess + model execution 분리 또는 model parallel 가능성**을 benchmark한다.
- reproducibility가 흔들리면 1 GPU training + 다른 GPU auxiliary/cache job이 우선.
- effective batch 16은 유지한다.

---

## 11. Checkpoint / model selection

Gold58은 반복된 dev gate이므로 절대 독립 test라고 부르지 않는다.

- every epoch checkpoint 저장
- epoch 8~16을 후보로 함
- Gold58 Macro AUROC 기준 global top-3 epoch 선택
- top-3 state를 **equal-weight parameter averaging(SWA-style serving checkpoint)** 으로 합친다.
- target별로 서로 다른 epoch를 cherry-pick하지 않는다.
- 최종 Branch-B serving checkpoint는 **1개**로 유지한다.

보조 지표:
- per-target AUROC
- macro AUPRC
- target prediction variance
- Branch-A와 prediction correlation

---

## 12. Inference / TTA

Primary:
```text
96 slices
→ 94 dense 3-slice windows
→ CoAtNet
→ target-specific attention
→ 12 probabilities
```

Optional but planned:
**anatomical mirror TTA 1회**

원칙:
- plain + anatomically mirrored study를 각각 추론
- medial/lateral targets는 mirror output을 원래 의미로 swap
- probability average
- MCL은 plain-only 유지하는 후보를 먼저 사용
- generic image flip과 구분한다

TTA on/off는 같은 checkpoint로 별도 submission을 만들어 Public LB로 확인한다.

---

## 13. Standalone 및 Branch-A ensemble 평가

Branch-B 성공 여부는 standalone LB 하나로만 판단하지 않는다.

필수 제출:
1. B standalone probability
2. B anatomical-mirror TTA
3. A+B rank blend

Rank:
```text
R_A[t] = percentile_rank(P_A[t])
R_B[t] = percentile_rank(P_B[t])
```

첫 blend 후보:
```text
0.70 A + 0.30 B
0.60 A + 0.40 B
0.50 A + 0.50 B
```
은 rank space에서 계산한다.

가중치는 Gold58 하나만으로 최적화하지 않는다.
Public LB와 target-wise behavior를 같이 보고 고정한다.

Branch-B가 standalone 0.926보다 낮아도 A+B가 상승하면 성공이다.

---

## 14. 최종 3-Branch 구조에서의 역할

시간이 충분해 Branch-C까지 완료되면:

```text
Branch-A DINO Core
Branch-B CoAtNet Wide-MRI
Branch-C ConvNeXt Anatomy
        ↓
per-target percentile rank
        ↓
target-wise/global fixed blend
        ↓
submission
```

Branch-B는 **Wide/Dense MRI coverage expert** 역할을 유지한다.

---

## 15. 실행 순서

1. S11/DINO Core 현재 실험 마무리
2. 최신 B soft-label artifact의 실제 path/SHA 고정
3. Branch-B 96-slice cache preflight
4. exact output byte 계산 → 4/5 pack 확정
5. cache build + integrity QA
6. CoAtNet 16ep full-data training
7. Gold58 epoch/SWA selection
8. standalone inference notebook
9. Public LB
10. anatomical mirror TTA submission
11. A+B rank blend
12. 결과를 EXPERIMENT_LOG에 누적
13. 시간이 남으면 Branch-C 진행

---

## 16. 실행 전 필수 Gate

- label artifact SHA
- 4,349 train Study universe
- Gold58 exclusion
- no train/Gold UID intersection
- exact target order 12
- cache Study count
- Slot mask sanity
- 140mm crop contract
- intensity 2/98 parity
- checkpoint pretrained identity
- no Internet dependency
- hidden inference robust DICOM reader
- Study-level silent 0.5 fallback 금지 또는 명시적 diagnostic policy

---

## 17. 외부 참고에서 채택한 아이디어

사용자가 제공한 상위권 CoAtNet/Raptor 자료에서 확인된 패턴:
- CoAtNet + target-specific window attention
- anatomical slot 기반 MRI representation
- wide slice span
- 140mm physical crop
- 384-resolution 계보
- soft probability labels
- dense inference
- anatomical mirror TTA
- checkpoint averaging
- 단일 강한 branch가 과도한 same-family ensemble보다 효율적일 수 있음

이 값들은 **우리 실험에서 아직 재현되지 않은 외부 참고**다. 실제 우리 결과가 나오면 이 문서의 “가설”과 “검증 결과”를 구분해 기록한다.

---

## 18. 다음 새 채팅 시작점

새 채팅에서는:
1. `docs/CURRENT_HANDOFF.md`
2. 이 문서
3. `COATNET_EXPERIMENT_LOG.md`
를 읽는다.

현재 바로 다음 작업은 **Branch-B cache를 만들기 전에 최신 B soft-label artifact/path/SHA와 raw competition DICOM 입력을 고정하고, 96×384 cache의 실제 Pack 설계를 만드는 것**이다.
