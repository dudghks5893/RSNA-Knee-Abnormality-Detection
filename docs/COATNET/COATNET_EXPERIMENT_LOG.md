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
