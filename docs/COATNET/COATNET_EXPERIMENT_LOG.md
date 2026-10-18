## 2026-10-18 — B V7 standalone 2F Public LB 결과

상태: **TRAIN_COMPLETE / STANDALONE_SUBMITTED / PUBLIC_LB_0.925**

### Training result
- Experiment: `B-COAT-WIDE96-2F-BASE-V7-AMP-RECOVERY-ES`
- Backbone: `coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k`
- Fold0 best: **Gold29 Macro AUROC 0.923407 @ Epoch6**
- Fold1 best: **Gold29 Macro AUROC 0.915820 @ Epoch9**
- checkpoint policy: best.pt only / no last / no SWA
- Fold0 best SHA256: `f984bcc7dde0673c54c7d1dea513280d8abd72aed3ebc0343b6511b0e439bc11`
- Fold1 best SHA256: `759ae6916107cc9a78048a4daf18b0ba31759bbf688dc2c5331ad3092982a585`

Kaggle model dataset:
- `/kaggle/input/datasets/yhlucas/b-coat-wide96-2f-base-model/fold0/best.pt`
- `/kaggle/input/datasets/yhlucas/b-coat-wide96-2f-base-model/fold1/best.pt`

### Standalone submission
Notebook:
- `B_COAT_WIDE96_2F_STANDALONE_SUBMISSION_V1.ipynb`
- local SHA256: `4a6941fab1713ce48b186f01b81e21f349c9738e8448f001524ac1ff051191fc`

Inference:
- hidden DICOM → frozen Wide96 reconstruction
- 26 SAG fluid + 22 SAG non-fluid + 18 COR fluid + 12 COR non-fluid + 18 AXIAL
- 96 slices → 94 dense 3-slice windows
- native384 preprocessing → center320 model input
- Fold0/Fold1 probability mean
- Study-level neutral 0.5 fallback 없음

Actual result:
- **Public LB: 0.925**
- 사용자 측정 hidden 전체 제출 runtime: **약 1시간 30분**
- 공개/샘플 3-Study Save & Run All: **약 1분 5초**

### Decision
- Branch-B는 standalone으로 Branch-A 주력 0.928에 매우 근접한 강한 독립 expert.
- A와 입력/백본이 충분히 달라 ensemble diversity 가치가 높음.
- 다음 실험은 **A+B target-wise percentile-rank blend**.
- 1차 권장 weight는 **A 60% + B 40%**.
- C standalone 0.854는 우선 제외하고 A+B gain을 먼저 검증.

---

## 2026-10-18 — B V3 NaN 중단 / V5 STABLE-ES 준비

상태: **V3 ABORTED / V5 NOTEBOOK READY**

V3 실제 실행 결과:
- Fold0 Epoch1 step600부터 train loss NaN, Epoch1 validation에서 `ValueError: Input contains NaN`로 worker 종료.
- Fold1은 계속 진행되어 Gold29 Macro AUROC가 Epoch8 **0.896024**까지 개선됐으나, 2-Fold run은 Fold0 부재로 무효이므로 사용자가 실행 중단.
- V3는 early stopping이 없고 16 fixed epochs였음.
- V3 checkpoint policy 자체는 올바르게 **own Gold29 Macro AUROC best.pt only / no last / no SWA**였음.

대체 Notebook:
- `B_COATNET_WIDE96_2F_BASE_V5_STABLE_ES.ipynb`
- local SHA256 `425ef5c973de1b04513592706416c63ec439d551783f28df7b92f5e8620aa0a5`

V5 변경:
- max16 epochs
- own Gold29 Macro AUROC early stopping
- min epochs 6 / patience 3
- best.pt only 유지; last/epoch/SWA 없음
- CoAtNet backbone AMP + MIL/head FP32
- head LR 2e-3 → **1e-3**
- non-finite logits/loss/gradient fail-fast
- one Fold failure → sibling Fold 즉시 terminate
- 목적: V3 NaN 재발 방지 + 한 Fold 실패 시 GPU 낭비 방지

<!-- COATNET_BASE_V3_RUNNING_2026_10_18 -->
## 2026-10-18 — B-COAT-WIDE96-2F-BASE-V3 실제 실행 시작

상태: **TRAIN_RUNNING / RESULT_PENDING**

실행 Notebook:
- `B_COATNET_WIDE96_2F_BASE_V3.ipynb`
- SHA `bb3527a1c8b6fd6f6585295413420720d341ee4c61b8b04de25ca1ee5a6bf3f4`

Scientific contract:
- V4 Routed Broad 4,349 + opposite Gold29 train / own Gold29 val.
- Fold0→GPU0 / Fold1→GPU1 independent, **No DDP**.
- V4 pseudo weight `.25+.75*confidence`.
- pseudo soft class balance power .70 / clip .5–2.5.
- rare-positive Study sampling.
- Wide96 Native384 cache.
- CoAtNet RMLP2 1024-d full FT.
- 16 fixed epochs.
- Base checkpoint: Fold별 own Gold29 Macro AUROC `best.pt` 하나.

결과가 오기 전에는 Gold29/epoch/runtime/checkpoint SHA/Public LB를 추정해 기록하지 않는다.

Next after completion:
- Base 2F standalone submission → Public LB.
- V4 Strict FT → standalone LB.
- Branch-A와 A+B ensemble.

## 2026-10-17 — B-COAT-WIDE96-2F-BASE-V4 notebook READY

**상태: TRAIN_READY_V4 / NOT_RUN**

Authoritative notebook:
- `B_COATNET_WIDE96_2F_BASE_V4.ipynb`
- SHA `45f77cd959d984577099b0a67f406b0e3f98296a4950d4b1a7dafeccc04f649f`
- V1/V2/V3: **DO_NOT_RUN**

Audit fixes over V3:
- actual HDF5 384→320 optimizer-step resource probe
- normal training-mode BN preserved; checkpoint recompute cannot double-update running stats
- PB 4→2→1 + Window chunk 12→8→6→4→3→2
- 128 real Study optimizer-inclusive benchmark per Fold
- full Gold29 dense-validation timing included
- 16ep wall-time projection + 10% margin
- >4h projected concurrent wall time → fail-fast before Epoch1
- independent Fold0/GPU0 + Fold1/GPU1, No DDP
- Fold별 `best.pt` only

## 2026-10-17 — B-COAT-WIDE96-2F-BASE-V3 notebook READY

**상태: TRAIN_READY_V4 / NOT_RUN**

Authoritative notebook:
- `B_COATNET_WIDE96_2F_BASE_V3.ipynb`
- SHA `bb3527a1c8b6fd6f6585295413420720d341ee4c61b8b04de25ca1ee5a6bf3f4`
- V1/V2: **OBSOLETE / DO_NOT_RUN**

Training correction:
- **No DDP**
- GPU0=Fold0, GPU1=Fold1 independent
- Fold0 train V4 4,349 + Gold Fold1 29 / val Gold Fold0 29
- Fold1 train V4 4,349 + Gold Fold0 29 / val Gold Fold1 29
- physical Study batch is not fixed: 4→2→1 actual optimizer-step benchmark
- effective Study batch/Fold=16
- 16 fixed epochs, no early stop
- checkpoint policy: **best.pt only per Fold**
- no epoch checkpoints / no last / no SWA / no top3 averaging


## 2026-10-17 — B-COAT-WIDE96-FT-V2 notebook READY

**상태: TRAIN_READY / NOT_RUN**

Authoritative notebook:
- `B_COATNET_WIDE96_FT_V2.ipynb`
- SHA `bd78e9b1c1b0fd5dc65f98c2fde5d67bfb7665440eb49f5eeecdfbd918d1d14c`
- V1: **OBSOLETE / DO_NOT_RUN**

Labels:
- V4 Routed Broad
- path `/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_broad.csv`
- SHA `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`
- 4,349 Studies
- `weight=.25+.75*confidence`

Pretrained:
- `/kaggle/input/models/blueberry808/coatnet-rmlp-2-rw-384-sw-in12k-ft-in1k/pytorch/default/1/coatnet_rmlp_2_rw_384_sw_in12k_ft_in1k.pth`
- architecture `coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k`
- mounted SHA recorded at run time
- backbone pretrained parameter coverage >=99%
- feature dim **1024**

Training:
- T4×2 DDP
- 16 epochs
- global effective Study batch 16
- 12 train windows / 94 dense DEV positions
- activation checkpoint
- window microbatch benchmark 12→8→6→4→3→2, no 1
- Gold58 DEV only
- epoch8~16 top3 global checkpoint parameter average


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


## 2026-10-17 — B-CACHE-96S384-V1 4-Pack 실제 생성 완료

**실행 상태: PASS / CACHE_COMPLETE**

실제 Kaggle HDF5:
- P00: `/kaggle/input/datasets/yhlucas/b-coat-wide96-cache-pack-00/B_COAT_WIDE96_CACHE_PACK_00/coat_wide96_native384_pack00.h5`
  - 1,102 Studies
  - 14.535 GiB
  - SHA `304028610a451f598255c6a18c07c4b531f8d9fdabb0fa265695c8a24d326c6f`
- P01: `/kaggle/input/datasets/woniyeon/b-coat-wide96-cache-pack-01/B_COAT_WIDE96_CACHE_PACK_01/coat_wide96_native384_pack01.h5`
  - 1,102 Studies
  - 14.535 GiB
  - SHA `1d8bc3003517ec34c7c1ba70b398a6525136f40ed12503c95bd6a5b6a5595eb1`
- P02: `/kaggle/input/datasets/yhlucas/b-coat-wide96-cache-pack-02/B_COAT_WIDE96_CACHE_PACK_02/coat_wide96_native384_pack02.h5`
  - 1,102 Studies
  - 14.535 GiB
  - SHA `ee49f1891c5d10e116d0b9ebab8e860ceddfa70639b3dfa959d5a3416c63be86`
- P03: `/kaggle/input/datasets/woniyeon/b-coat-wide96-cache-pack-03/B_COAT_WIDE96_CACHE_PACK_03/coat_wide96_native384_pack03.h5`
  - 1,101 Studies
  - 14.522 GiB
  - SHA `5f37b844659f5e3faa389f64c1b7194f2e3b71e7589cbe9378767ce3d7a4f2f1`

전체:
- 4,407 Studies
- 96 slices/Study
- logical positions 423,072
- valid slices 406,966
- missing slices 16,106
- Studies with >=1 missing slot 1,241
- decode failure 0
- selected non-missing Series 20,792
- selected Series sort method: IOP_IPP 20,792 / 20,792
- physical cache size 약 58.127 GiB

생성 contract:
- 26 SAG fluid
- 22 SAG non-fluid
- 18 COR fluid
- 12 COR non-fluid
- 18 AXIAL
- 2~98% wide span
- selected valid slices p2/p98 intensity mapping
- modality LUT + MONOCHROME1 inversion
- 140mm center crop
- cv2.INTER_AREA → 384×384
- HDF5 `volume [N,96,384,384] uint8`
- HDF5 `valid_mask [N,96] uint8`
- compression 없음

Global reproducibility:
- selected slot manifest SHA `2ae3c83c45c7efa46e393d0c23fb266850479830ebca329c3c74c19ff9165f5e`
- pack partition SHA `c934b45a305f8e3339a1934332ecd61b32de35160cd8fceb6206ed704752a55c`

Full-readback QA:
- P00 PASS
- P01 PASS
- P02 PASS
- P03 PASS

Decision:
- **B-CACHE-96S384-V1은 학습 입력으로 승인.**
- 다음은 최신 B soft-label artifact path/SHA 고정 후 CoAtNet 16ep full-data training.


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


# Branch-B CoAtNet — Cumulative Experiment Log

최종 갱신: **2026-10-17**

이 문서는 CoAtNet 관련 실제 실행 결과만 누적한다. 계획은 [COATNET_BRANCH_PLAN.md](COATNET_BRANCH_PLAN.md)에 기록한다.

## Status

- Branch: **B — CoAtNet Wide-MRI Expert**
- Current state: **TRAIN_READY_V4 / NOT_RUN**
- Design version: **B-DESIGN-V1**
- Baseline 목적 아님. 첫 실행부터 고득점 가설 설계를 사용한다.

## Experiment naming

```text
B-CACHE-96S384-V1
B-COAT-WIDE96-FT-V1
B-COAT-WIDE96-SWA-V1
B-COAT-WIDE96-MIRROR-TTA-V1
AB-RANK-BLEND-V1
```

실제 실행 시 각 항목에 반드시 기록:
- 날짜
- notebook 파일명 / SHA
- Kaggle Save Version
- Inputs 경로 / SHA
- GPU/CPU
- runtime
- 핵심 config
- best/last/SWA checkpoint SHA
- Gold58 DEV
- Public LB
- 실패/경고
- 다음 결정

## Public LB table

| Experiment | Model | Public LB | Status |
|---|---|---:|---|
| — | — | — | NOT_RUN |

## Cache table

| Cache | Studies | Shape/Rows | Packs | SHA | Status |
|---|---:|---|---:|---|---|
| B-CACHE-96S384-V1 | **4,407** | **96×384×384 / Study** | **4** | per-Pack SHA 고정 | **PASS / CACHE_COMPLETE** |

## Checkpoint table

| Experiment | Checkpoint | SHA | Gold58 Macro AUROC | Notes |
|---|---|---|---:|---|
| — | — | — | — | — |

## Decision log

### 2026-10-17 — Branch-B 설계 시작
- DINO Core 뒤에 Stage를 더 붙이지 않고 독립 Branch-B로 구성.
- S8C Top18을 사용하지 않음.
- 96-slice anatomical slots + wide span + 140mm/384 + CoAtNet + target-specific attention.
- 4,349 report studies train, Gold58 training 제외.
- masked confidence-weighted soft BCE + class balance + rare-positive sampling.
- 16 epoch fixed, independent 2-Fold Base; each Fold keeps only own-Gold29 best checkpoint.
- standalone → mirror TTA → Branch-A rank blend 순으로 평가.


## 2026-10-17 — B-CACHE-96S384-V1 PRE-FLIGHT PASS

**실행 상태:** PASS

PRE-FLIGHT:
- 4,407 Studies / 24,371 Series
- selected Series 20,792
- header failures 0
- Pack split = 1,102 / 1,102 / 1,102 / 1,101
- total raw = 62,384,504,832 bytes
- max Pack raw = 15,599,665,152 bytes
- anticipated max Pack incl. reserve = 17,459,631,667 bytes
- output cap = 19,000,000,000 bytes

Artifacts:
- selected slot manifest SHA: `2ae3c83c45c7efa46e393d0c23fb266850479830ebca329c3c74c19ff9165f5e`
- partition SHA: `c934b45a305f8e3339a1934332ecd61b32de35160cd8fceb6206ed704752a55c`
- preflight review ZIP SHA: `ee5c14fdb47091f6388c35d546be9c42d387d5666582b9dbd722685ce307032a`

본 cache notebooks prepared:
- P00 `3804039ba53432ad9c4549eb1736fda3b7b475161b14e59df30f61255139e96c`
- P01 `63d2947640898236117ced84859366b82d89faf85dd44d44b50d81d24ca9ade3`
- P02 `be77d686a5a92ef3ba059ee8712e5013d7b5a95f7a8ab9e4bdca547184e3de17`
- P03 `8849b7900e733792f170f3cb60560281f0589143de2bcddbe51f9fc211ef57bb`
- ZIP `a32b6d45f13f2e25cfedf7ffe9b06e472333e87379e081053c0e5ca75e928f65`

**완료:** Pack00~03 실제 cache 생성 및 full-readback 검증 PASS. **다음:** 최신 B soft-label path/SHA 고정 → CoAtNet 16ep training.