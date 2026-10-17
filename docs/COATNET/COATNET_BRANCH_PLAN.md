<!-- COATNET_V3_ACTUAL_RUNNING_2026_10_18 -->
## 2026-10-18 — Actual execution override: V3 TRAIN_RUNNING

**실제 현재 상태가 이 섹션보다 우선한다.**

- 사용자가 이미 `B_COATNET_WIDE96_2F_BASE_V3.ipynb`를 Kaggle에서 실행함.
- V3 SHA: `bb3527a1c8b6fd6f6585295413420720d341ee4c61b8b04de25ca1ee5a6bf3f4`
- 상태: **BASE_V3 / TRAIN_RUNNING**
- GPU0=Fold0 / GPU1=Fold1 independent, DDP=false.
- V4(`B_COATNET_WIDE96_2F_BASE_V4.ipynb`, SHA `45f77cd...`)는 audit 개선본이지만 **정상 진행 중인 V3를 중단시키는 근거가 아니다**.
- V3의 known execution caveat(synthetic 320 resource probe, BN running-stat freeze, 128-real-Study runtime gate 없음)는 Fold/label/cache/loss 무효 사유가 아니다. 정상 train loop가 진행되면 끝까지 보존한다.

Base 완료 후:
1. Fold0/1 best, history, Gold29, runtime, actual batch 검증.
2. **Base best 2F standalone Public LB**.
3. same-fold Base best init으로 **V4 Strict high-confidence FT** 설계.
4. Strict FT에서는 `best.pt` + `last.pt` 보존을 우선 검토.
5. Strict standalone LB.
6. 최종 Branch-B serving candidate 선택.
7. 현재 Branch-A best와 **A+B rank/probability ensemble** 평가.

## 2026-10-17 — V3 audit correction / V4 authoritative

상태: **CACHE_COMPLETE / TRAIN_READY_V4 / NOT_RUN**

Authoritative notebook:
- `B_COATNET_WIDE96_2F_BASE_V4.ipynb`
- SHA256 `45f77cd959d984577099b0a67f406b0e3f98296a4950d4b1a7dafeccc04f649f`
- V1/V2/V3: **OBSOLETE / DO_NOT_RUN**

V4 keeps the independent 2-Fold scientific design:
- GPU0=Fold0 / GPU1=Fold1, **No DDP**
- Fold0 train = V4 Broad 4,349 + Gold Fold1 29 / val = Gold Fold0 29
- Fold1 train = V4 Broad 4,349 + Gold Fold0 29 / val = Gold Fold1 29
- V4 pseudo weight = `0.25 + 0.75 × confidence`
- pseudo-only class balance power .70 / clip .5–2.5
- rare-positive Study sampling retained
- Base checkpoint = Fold별 own Gold29 Macro AUROC `best.pt` 하나만 유지
- no last / no SWA / no top3 averaging

V3 audit에서 수정한 실행 안정성:
1. resource probe가 synthetic 320 input이 아니라 **실제 Wide96 HDF5 → 384→320 augmentation → forward/backward/AdamW** 전체 경로를 사용
2. CoAtNet BatchNorm을 전역 eval/freeze하지 않음. activation-checkpoint recompute에서만 running-stat second update를 차단
3. physical Study batch `4→2→1`, window microbatch `12→8→6→4→3→2`를 분리 benchmark
4. 선택된 공통 profile로 **Fold별 128 real Studies optimizer-inclusive throughput** 측정
5. own Gold29 dense validation 시간까지 포함해 16ep runtime projection
6. 10% safety margin 포함 projected concurrent wall time > **4.0h** 이면 Epoch1 전에 fail-fast

## 2026-10-17 — Branch-B Base 학습 구조 교정 / V3 authoritative

상태: **CACHE_COMPLETE / TRAIN_READY_V4 / NOT_RUN**

사용자 최종 결정에 따라 V1/V2의 `single all-data model + T4×2 DDP + SWA` 설계는 폐기한다.

Authoritative notebook:
- `B_COATNET_WIDE96_2F_BASE_V4.ipynb`
- SHA256 `45f77cd959d984577099b0a67f406b0e3f98296a4950d4b1a7dafeccc04f649f`
- V1/V2: **OBSOLETE / DO_NOT_RUN**

### Base 2-Fold contract

```text
GPU0 → Fold0 독립 모델
Train = V4 Broad 4,349 + Gold Fold1 29
Val   = Gold Fold0 29
→ fold0/best.pt

GPU1 → Fold1 독립 모델
Train = V4 Broad 4,349 + Gold Fold0 29
Val   = Gold Fold1 29
→ fold1/best.pt
```

- **DDP 사용 안 함**
- 두 GPU는 서로 다른 Fold 모델을 동시에 학습
- 각 Fold train = 4,378 Studies
- 각 Fold val = own Gold29
- V4 pseudo 4,349는 양 Fold 공통
- opposite Gold29는 binary BCE ×3
- own Gold29는 checkpoint selection용 validation

### Physical Study batch

Study batch=1 고정 폐기.

각 GPU에서 실제 CoAtNet forward + backward + AdamW step으로:
- PB4: window chunk 12→8→6→4→3→2
- 실패 시 PB2 동일 검사
- 실패 시 PB1 동일 검사
- microbatch1 금지

두 GPU가 모두 통과하는 가장 큰 공통 physical batch를 사용한다.

Fold별 effective Study batch는 16으로 고정:
- PB4 → grad accumulation 4
- PB2 → grad accumulation 8
- PB1 → grad accumulation 16

### Base checkpoint policy

초기 Base 모델은 Fold별 **best checkpoint 하나만 유지**한다.

- 16 fixed epochs
- early stopping 없음
- 기준: own Gold29 Macro AUROC
- best 갱신 시 같은 `best.pt` atomic overwrite
- 저장: `fold0/best.pt`, `fold1/best.pt`
- 저장하지 않음: epoch별 model checkpoint, `last.pt`, SWA, top3 parameter averaging
- epoch별 metric/history CSV는 유지

향후 Fine-tuning Stage에서는 목적에 따라 `last.pt` 사용 여부를 별도로 정한다.


## 2026-10-17 — Branch-B training input 최종 수정 / V2 authoritative

상태: **CACHE_COMPLETE / TRAIN_READY_V4**

### Supervision 최종 선택

Branch-B CoAtNet은 LABEL-V6 B가 아니라, 기존 비교에서 실제 성능이 가장 좋았던 **V4 Routed Broad**를 사용한다.

정확한 Kaggle path:

```text
/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_broad.csv
```

SHA256:

```text
93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c
```

Contract:
- 4,349 report/pseudo Studies
- 12 targets
- 각 target마다 `target` + `target__conf`
- all target mask = 1
- supervision weight = **0.25 + 0.75 × confidence**
- class-balance = pseudo-only confidence-weighted soft prevalence, power .70, clip .5–2.5
- Gold58은 train에 넣지 않고 DEV gate only

### CoAtNet pretrained weight

사용자가 Kaggle input에 추가한 exact path:

```text
/kaggle/input/models/blueberry808/coatnet-rmlp-2-rw-384-sw-in12k-ft-in1k/pytorch/default/1/coatnet_rmlp_2_rw_384_sw_in12k_ft_in1k.pth
```

Architecture:

```text
coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k
```

- random-init fallback 금지
- notebook 실행 시 mounted .pth SHA를 계산해 run_config에 기록
- checkpoint wrapper/prefix 정규화 후 backbone key+shape 매칭
- pretrained parameter element coverage >= 99% 필수
- CoAtNet backbone `num_features = 1024` 강제 검증

### Authoritative training notebook

`B_COATNET_WIDE96_2F_BASE_V4.ipynb`

SHA256:

`45f77cd959d984577099b0a67f406b0e3f98296a4950d4b1a7dafeccc04f649f`

V1/V2는 **OBSOLETE / DO_NOT_RUN**.

V3:
- Fold0→GPU0 / Fold1→GPU1 독립 학습, **No DDP**
- Fold f train = V4 Broad 4,349 + opposite Gold29
- Fold f validation = own Gold29
- 16 fixed epochs / no early stop
- physical Study batch 4→2→1 real training-graph benchmark
- effective Study batch/Fold = 16
- 12 stochastic windows/Study
- 94 dense validation positions
- backbone LR 4e-5 / head LR 2e-3 / WD .06
- cosine + warmup 5% / FP16
- Fold별 own Gold29 Macro AUROC best만 `best.pt`
- no last / no SWA / no top3 averaging


## 2026-10-17 — B-COAT-WIDE96-FT-V1 본학습 Notebook 생성

Notebook:
`B_COATNET_WIDE96_FT_V1.ipynb`

Local SHA256:
`5ba2c615cf6dad9fb573b6929ac45aa236643922e2c61df2a0b680c61b269109`

Static QA:
- nbformat PASS
- all code AST PASS
- embedded DDP worker compile PASS
- notebook source 50,012 bytes (<1MB)

핵심:
- 4-Pack Wide96 Native384 SHA gate
- 4,349 report studies train / Gold58 train 제외
- CoAtNet `coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k`
- 2×T4 DDP, single serving model
- per-GPU Study batch1 × 2 GPU × grad-accum8 = global effective Study batch16
- 12 stochastic windows/Study/epoch
- 384→320 random crop + mild affine/intensity augmentation
- target-specific window attention
- masked confidence-weighted soft BCE
- class balance power .70 / cap .5–2.5
- rare-positive Study sampling
- 16 fixed epochs / no early stop
- backbone LR 4e-5 / head LR 2e-3 / WD .06 / cosine / 5% warmup
- epoch01~16 model checkpoints
- epoch8~16 Gold58 Macro AUROC global top3 parameter averaging → `swa_top3.pt`

실행 전 아직 외부 입력으로 고정되지 않은 2개:
1. 최신 최종 B soft-label Kaggle artifact/path/SHA
2. exact pretrained CoAtNet `model.safetensors`

Notebook은 둘을 임의 대체하지 않는다.
- B label: 4,349 unique report Study + 12 target + soft/confidence(or weight)/mask schema를 검증해 정확히 1개 후보만 허용
- pretrained: SHA `91570c7af10fea0af03c1b0a49be3e4775596239890eb4193c75129b3045623e` exact file만 허용
- random-init / V4 Strict silent fallback 금지


## 2026-10-17 — B-CACHE-96S384-V1 실제 생성 완료 / 4-Pack Dataset 고정

상태: **CACHE_COMPLETE / TRAIN_READY_V4**

Branch-B CoAtNet용 Wide96 Native384 본 cache 4개 Pack의 실제 Kaggle 생성 및 full-readback QA가 모두 완료되었다.

### 실제 Dataset 경로

```text
Pack00
/kaggle/input/datasets/yhlucas/b-coat-wide96-cache-pack-00/B_COAT_WIDE96_CACHE_PACK_00/coat_wide96_native384_pack00.h5

Pack01
/kaggle/input/datasets/woniyeon/b-coat-wide96-cache-pack-01/B_COAT_WIDE96_CACHE_PACK_01/coat_wide96_native384_pack01.h5

Pack02
/kaggle/input/datasets/yhlucas/b-coat-wide96-cache-pack-02/B_COAT_WIDE96_CACHE_PACK_02/coat_wide96_native384_pack02.h5

Pack03
/kaggle/input/datasets/woniyeon/b-coat-wide96-cache-pack-03/B_COAT_WIDE96_CACHE_PACK_03/coat_wide96_native384_pack03.h5
```

### Pack별 실제 결과

| Pack | Studies | HDF5 size | HDF5 SHA256 | Valid slices | Missing slices | Missing-slot Studies | Decode failures |
|---|---:|---:|---|---:|---:|---:|---:|
| 00 | 1,102 | 14.535 GiB | `304028610a451f598255c6a18c07c4b531f8d9fdabb0fa265695c8a24d326c6f` | 102,012 | 3,780 | 289 | 0 |
| 01 | 1,102 | 14.535 GiB | `1d8bc3003517ec34c7c1ba70b398a6525136f40ed12503c95bd6a5b6a5595eb1` | 101,558 | 4,234 | 327 | 0 |
| 02 | 1,102 | 14.535 GiB | `ee49f1891c5d10e116d0b9ebab8e860ceddfa70639b3dfa959d5a3416c63be86` | 101,746 | 4,046 | 313 | 0 |
| 03 | 1,101 | 14.522 GiB | `5f37b844659f5e3faa389f64c1b7194f2e3b71e7589cbe9378767ce3d7a4f2f1` | 101,650 | 4,046 | 312 | 0 |
| **TOTAL** | **4,407** | **58.127 GiB** | — | **406,966** | **16,106** | **1,241** | **0** |

총 logical slice positions:
`4,407 × 96 = 423,072`.

따라서:
- valid = **406,966**
- zero/mask missing = **16,106**
- decode failure = **0**
- missing은 DICOM decode 오류가 아니라 구조적으로 해당 second-Series Slot이 없는 경우다.

### 실제 HDF5 구조

각 Pack:
```text
volume      [NStudy, 96, 384, 384] uint8
valid_mask  [NStudy, 96]           uint8
```

`valid_mask=1`:
- 실제 선택/복호화된 acquisition slice

`valid_mask=0`:
- 구조적으로 Slot이 없거나 decode가 실패한 위치
- 이번 실제 build에서는 decode failure가 0이므로 모두 구조적 missing에서 발생

### 96-slice anatomical layout

```text
S0 SAG_FLUID      26
S1 SAG_NONFLUID   22
S2 COR_FLUID      18
S3 COR_NONFLUID   12
S4 AXIAL_ANY      18
TOTAL             96
```

Series 선택 규칙:
1. 동일 Study 내 Series 재사용 금지
2. requested plane 일치
3. fluid/non-fluid 조건이 있으면 preferred Series 우선
4. preferred가 없으면 같은 plane의 unused Series fallback
5. 두 번째 같은-plane Series 자체가 없으면 해당 Slot zero + mask 0

PRE-FLIGHT에서 확인한 전체 구조적 missing:
- SAG_NONFLUID missing Study: **119**
- COR_NONFLUID missing Study: **1,124**
- AXIAL missing: **0**
- 적어도 1개 Slot missing Study: **1,241**

### 생성 과정

각 선택 Series에서:
```text
DICOM physical ordering
IOP/IPP
→ InstanceNumber
→ filename fallback
```

실제 4-Pack build의 **20,792 selected non-missing Series 전부 IOP_IPP ordering**으로 처리되었다.

그 다음:
```text
Series slices
→ 2~98% span
→ Slot별 k개 균등 sampling
→ modality LUT
→ MONOCHROME1 inversion if needed
→ selected valid slices 기반 p2/p98 intensity normalization
→ 140mm physical center crop
→ cv2.INTER_AREA
→ 384×384 uint8
→ Study 고정 96-slice volume
```

HDF5 compression은 사용하지 않았다.

### QA / reproducibility binding

PRE-FLIGHT global contracts:
- selected-slot manifest SHA:
  `2ae3c83c45c7efa46e393d0c23fb266850479830ebca329c3c74c19ff9165f5e`
- pack partition SHA:
  `c934b45a305f8e3339a1934332ecd61b32de35160cd8fceb6206ed704752a55c`

Pack partition:
```text
sorted StudyInstanceUID
→ row_index % 4
→ Pack00/01/02/03
```

각 Pack에서:
- Study별 volume + mask SHA 생성
- HDF5 전체 readback
- Study SHA 재검증
- valid_mask sum parity
- final HDF5 SHA 생성
을 모두 통과했다.

### CoAtNet loader에서의 사용

Cache 자체는 96개의 2D slice다.

학습/추론 시:
```text
96 slices
→ [c-1, c, c+1] 3-channel window
```

- train: Study당 stochastic **12 windows/epoch**
- validation/inference: 가능한 **94 dense overlapping windows**
- `valid_mask`로 missing 위치가 포함된 window를 제외/마스킹한다.

### 다음 단계

Cache 생성은 완료되었다. 다음 Branch-B 실제 작업은:
1. 최신 B soft-label artifact의 실제 Kaggle path/SHA 고정
2. 4개 HDF5 path/SHA input gate
3. Gold58 train exclusion gate
4. CoAtNet 16-epoch full-data training notebook 생성
5. standalone → mirror TTA → A+B rank blend 평가


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

Pack00~03 실제 HDF5 cache build 및 full-readback QA까지 완료. 상세 경로/SHA는 이 문서 최상단의 CACHE_COMPLETE 섹션을 authoritative source로 사용한다.


# Branch-B CoAtNet Wide-MRI Expert — Authoritative Design & Roadmap

최종 갱신: **2026-10-17**  
상태: **CACHE_COMPLETE / TRAIN_NOT_RUN**  
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

### Study universe / 2-Fold
- **V4 Report/Pseudo 4,349개**: 양 Fold 공통 학습
- **Gold58**: 29/29 두 Fold로 분할
- Fold0 train = pseudo 4,349 + Gold Fold1 29 / val = Gold Fold0 29
- Fold1 train = pseudo 4,349 + Gold Fold0 29 / val = Gold Fold1 29
- 각 Fold validation Gold29는 해당 Fold train에서 완전 제외

### 라벨
주 라벨은 **V4 Routed Broad**를 사용한다.

- path: `/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_broad.csv`
- SHA: `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`
- 4,349 Studies × 12 targets
- `weight = 0.25 + 0.75 × confidence`
- Gold58은 학습 제외, DEV gate only

hard 0/1로 재이산화하지 않는다.
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
| Physical Study batch | **4→2→1 실측 benchmark** |
| Grad accumulation | **16 / selected physical batch** |
| Effective Study batch | **16 / Fold** |
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
- **Fold0 → GPU0, Fold1 → GPU1 독립 학습**
- **DDP 사용 안 함**
- physical Study batch는 각 GPU에서 4→2→1 순으로 실제 training graph benchmark
- 두 GPU가 모두 가능한 가장 큰 공통 physical batch 사용
- effective batch는 Fold별 16 유지

---

## 11. Checkpoint / model selection

Gold58은 반복된 dev gate이므로 절대 독립 test라고 부르지 않는다.

- Base stage는 **Fold별 best checkpoint 하나만 저장**
- 기준: 해당 Fold의 held-out Gold29 Macro AUROC
- best 갱신 시 같은 `best.pt`를 overwrite
- epoch별 model checkpoint 저장 안 함
- Base stage `last.pt` 저장 안 함
- SWA/top3 parameter averaging 안 함
- 최종 Base checkpoints: `fold0/best.pt`, `fold1/best.pt`

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
6. CoAtNet 16ep independent 2-Fold Base training
7. Fold별 Gold29 best checkpoint selection
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

현재 바로 다음 작업은 **최신 B soft-label artifact의 실제 Kaggle path/SHA를 고정한 뒤, 완료된 4-Pack HDF5를 사용해 CoAtNet 16-epoch 본학습 notebook을 만드는 것**이다.


---

## 2026-10-17 — Wide96 Cache PRE-FLIGHT 실제 PASS / Pack00~03 본 Cache 준비

### PRE-FLIGHT 실제 결과

실행 Notebook:
`B_COATNET_WIDE96_CACHE_PREFLIGHT_V1.ipynb`

상태:
`B_COAT_WIDE96_CACHE_PREFLIGHT_PASS`

검증:
- Studies: **4,407**
- Series: **24,371**
- selected non-missing Series: **20,792**
- DICOM header audit fail: **0**
- 140mm FOV audit: PASS
- global slot manifest SHA256:
  `2ae3c83c45c7efa46e393d0c23fb266850479830ebca329c3c74c19ff9165f5e`
- global pack partition SHA256:
  `c934b45a305f8e3339a1934332ecd61b32de35160cd8fceb6206ed704752a55c`
- review ZIP SHA256:
  `ee5c14fdb47091f6388c35d546be9c42d387d5666582b9dbd722685ce307032a`

Slot coverage:
- SAG_FLUID: 4,407 present / 0 missing
- SAG_NONFLUID: 4,288 present / 119 missing
- COR_FLUID: 4,407 present / 0 missing
- COR_NONFLUID: 3,283 present / 1,124 missing
- AXIAL_ANY: 4,407 present / 0 missing
- Studies with >=1 missing Slot: **1,241**

140mm severe shortage(`coverage_min < .8`):
- SAG_FLUID 0%
- SAG_NONFLUID 0%
- COR_FLUID 0%
- COR_NONFLUID ~0.03%
- AXIAL ~0.91%

### Pack 수 확정

```text
Pack00 = 1,102 Studies
Pack01 = 1,102 Studies
Pack02 = 1,102 Studies
Pack03 = 1,101 Studies
```

각 최대 raw volume 약 15.60GB, 10% + 300MB reserve 포함 약 17.46GB로 19GB safety cap 내.

따라서 **4 Pack canonical**로 확정. 5 Pack으로 늘리지 않는다.

### 본 Cache Notebook

- `B_COATNET_WIDE96_CACHE_PACK_00_V1.ipynb`
  SHA `3804039ba53432ad9c4549eb1736fda3b7b475161b14e59df30f61255139e96c`
- `B_COATNET_WIDE96_CACHE_PACK_01_V1.ipynb`
  SHA `63d2947640898236117ced84859366b82d89faf85dd44d44b50d81d24ca9ade3`
- `B_COATNET_WIDE96_CACHE_PACK_02_V1.ipynb`
  SHA `be77d686a5a92ef3ba059ee8712e5013d7b5a95f7a8ab9e4bdca547184e3de17`
- `B_COATNET_WIDE96_CACHE_PACK_03_V1.ipynb`
  SHA `8849b7900e733792f170f3cb60560281f0589143de2bcddbe51f9fc211ef57bb`
- Bundle ZIP SHA:
  `a32b6d45f13f2e25cfedf7ffe9b06e472333e87379e081053c0e5ca75e928f65`

각 notebook은 PRE-FLIGHT manifest/partition을 다시 결정적으로 생성한 뒤 위 SHA와 byte-exact 일치해야만 pixel cache를 시작한다.

Cache output:
- `volume [NStudy,96,384,384] uint8`
- `valid_mask [NStudy,96] uint8`
- missing Slot = zero + mask 0
- selected-slice p2/p98
- 140mm center crop
- cv2 INTER_AREA → 384
- compression 없음
- Study별 SHA + 전체 HDF5 full readback QA
- review ZIP은 HDF5 제외

### 다음 단계

Pack00~03를 CPU Kaggle에서 실행. 각 Pack이
`B COAT WIDE96 CACHE PACK PASS`
를 출력한 후에만 4개 HDF5를 training input으로 등록하고 CoAtNet 16-epoch full-data training notebook을 만든다.
