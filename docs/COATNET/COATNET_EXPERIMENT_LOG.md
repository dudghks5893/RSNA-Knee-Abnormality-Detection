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
- Current state: **NOT_RUN**
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
| B-CACHE-96S384-V1 | TBD | 96×384×384 / Study | 4~5 예정 | TBD | NOT_RUN |

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
- 16 epoch fixed, all-data single model, top-3 epoch parameter averaging.
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

**다음:** CPU에서 Pack00~03 실제 cache 생성 및 review 검증. Training은 아직 NOT_RUN.
