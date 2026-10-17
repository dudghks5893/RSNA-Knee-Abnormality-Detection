# Branch-C ConvNeXt — Cumulative Experiment Log

최종 갱신: 2026-10-18

계획은 [CONVNEXT_BRANCH_PLAN.md](CONVNEXT_BRANCH_PLAN.md), 실제 실행/Notebook 상태는 이 문서에 누적한다.

## Current Status

- Branch: C — ConvNeXt Anatomy Expert
- Design: C-DESIGN-V3 FROZEN
- Cache Notebook: READY / STATIC_QA_PASS
- Cache Execution: NOT_RUN
- Training: NOT_RUN
- Public LB: 없음

## 2026-10-18 — C-DESIGN-V3 확정

정정:
- Strict mask로 전체 성능이 낮아진 기존 실험은 Branch-C가 아니라 Branch-A DINO 초기 Stage1 실험이었다.
- C는 아직 모델/전용 데이터/학습 결과가 없었다.
- 이 결과는 C Base에서 coverage를 우선해야 한다는 참고 근거로만 사용한다.

C Base:
- V4 Routed Broad
- 2-Fold
- Report 4,349 + 반대 Gold29 train / own Gold29 val
- ConvNeXt-Small full FT
- 2.5D
- 320 cache → 288 train/val input
- v4 Global + anatomy-local
- 64 windows/Study
- target-specific spatial attention
- target-specific Window MIL
- OA extent / Mirror TTA는 Base 이후 분리 실험

## 2026-10-18 — C-ANATOMY-CACHE320-V1 Notebook 생성

상태:
- STATIC_QA_PASS
- KAGGLE_NOT_RUN

전체 4,407 train Study를 6 Pack으로 생성하도록 고정했다.
Pack당 약 734~735 Study이며 fixed tensor logical upper bound는 약 13.5 GiB/Pack이다.

Cache:
- windows [N,64,3,320,320] uint8
- window_meta [N,64,12] float32
- valid_mask [N,64]
- study_uid
- anchor_method

Anatomy:
- public code/anatomy dataset:
  heliosli/rsna-orthofoundation-fold0-epoch7-20261004
- pinning manifest:
  heliosli/rsna-knee-compact-r7cnxfsss
- anatomy.pt는 R7 manifest의 anchor_weights_sha256와 runtime exact match가 필요.
- projected anchor가 없는 Series는 local selection에서 제외하고 Full FOV만 허용.

Pinned reference source SHA:
- px_cache.py:
  b13e38a7ad3bd496f8027e02209653e224b0926db4f0853eeb0d076a2d6e2632
- knee_anchor_bank_v2.py:
  e564807a129dfcd3c984348917436ee6083066a4d685340587ebd1d3ea14f309
- probe_infer.py:
  a6cc31448019c84be5868d0a2ff1d99719b23b0f86110efc03efff3ce6bd6980

Notebook SHA256:
- P00: a176b40de512766cdb13b3fae83fd0a465294cdeaa8ee523ef47a413c5bbb206
- P01: c3ceefa50f15391ed40f5c0b5ad35f8e0f9916380316d9cfaef5d22a67323e3d
- P02: 0ae90a1fb8af2f77345ccab362b54756c19ee60e0592d9015975ca7250c1ad8a
- P03: 79bbaa42478861de0b8d658280fa60e04163231bdd609fdf6eec30bf0d99f71b
- P04: fcef4d13f4eecea801f4eeb02aeace77e05c5109d97716c49048ac5ffe04e457
- P05: 20c8757440c23ffe9fc3bd2e7f7113b83fc7d984c4b01caaa767b265df5ea5ac
- ZIP bundle:
  93ec0d6c21099e6b4451f23ca3fc64a226d3c2df5f6b7831631921ed75260aed

정적 검증:
- nbformat/JSON PASS
- 모든 Python cell compile PASS
- 각 Notebook source < 1MB PASS
- global /kaggle/input recursive scan 없음
- Pack ID별 별도 Notebook이므로 수동 config 변경 없음
- partial HDF5는 Study failure 1건이라도 있을 경우 final로 승격되지 않음

Required Inputs:
1. RSNA Knee Abnormality Detection competition
2. heliosli/rsna-orthofoundation-fold0-epoch7-20261004
3. heliosli/rsna-knee-compact-r7cnxfsss

Runtime:
- T4 x2 / Internet Off
- anchor segmentation은 cuda:0 사용
- cache rendering/writing은 CPU 중심
- 현재 실제 runtime 미측정.
- Notebook 첫 화면의 예상 범위는 60~180분/Pack이며 Pack00 실행 후 measured value로 교체한다.

### Immediate Next

P00만 먼저 Save & Run All:
- final receipt.json
- study_audit.csv
- HDF5 actual size
- runtime
- anchor method distribution
- global/local window total
을 검증한다.

P00 PASS 전에는 P01~P05를 무조건 대량 실행하지 않는다.

## Public LB table

| Experiment | Model | Public LB | Status |
|---|---|---:|---|
| C-BASE-01 | ConvNeXt-Small Anatomy 2F | — | NOT_RUN |
| C-OA-01 | Base + OA extent aux | — | NOT_RUN |
| C-MIRROR-01 | C anatomical mirror TTA | — | NOT_RUN |

## Cache table

| Cache | Studies | Packs | Resolution | Windows | Status |
|---|---:|---:|---:|---:|---|
| C-ANATOMY-CACHE320-V1 | 4,407 planned | 6 | 320 | max 64 | NOTEBOOK_READY / NOT_RUN |
