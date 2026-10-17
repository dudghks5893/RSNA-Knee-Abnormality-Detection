# Branch-C — ConvNeXt Anatomy Expert

최종 갱신: 2026-10-18

## 현재 상태

- Design: C-DESIGN-V3 FROZEN
- Cache Notebook: **V2 PREFLIGHT READY / STATIC_QA_PASS**
- Cache: NOT_RUN — **V1 6-Pack은 SUPERSEDED / DO NOT RUN**
- Training: NOT_RUN

Branch-C는 RSNA Knee 최종 A+B+C 앙상블의 세 번째 독립 전문가다.

- A = DINO Core / representation + selector + Top-K
- B = CoAtNet Wide-MRI Expert / dense multi-slice
- C = ConvNeXt Anatomy Expert / Global + anatomy-local + spatial attention + Window MIL

C는 A의 Top18 또는 B의 fixed Wide96 입력을 재사용하지 않는다.

## 문서 읽는 순서

1. [CONVNEXT_BRANCH_PLAN.md](CONVNEXT_BRANCH_PLAN.md) — 최신 authoritative C-DESIGN-V3
2. [CONVNEXT_EXPERIMENT_LOG.md](CONVNEXT_EXPERIMENT_LOG.md) — Notebook/실행/점수 누적 기록
3. [../CURRENT_HANDOFF.md](../CURRENT_HANDOFF.md) — 전체 A/B/C 상태

## 현재 cache contract

- C-ANATOMY-CACHE320-V1
- all train 4,407 Study
- 6 Pack
- 320×320 uint8
- max 64 2.5D windows/Study
- v4 Full FOV + anatomy-local
- thin <1.75 mm → 약 3.5 mm slab
- local anchor가 없는 Series는 local selection에서 제외; Full FOV는 유지
- anatomy.pt SHA는 public R7 manifest로 runtime exact pinning

## Cache Notebook

생성 완료:
- C_ANATOMY_CACHE320_V1_P00.ipynb ~ P05.ipynb

Kaggle:
- T4 x2
- Internet Off
- Pack별 Save & Run All
- Pack ID 수동 수정 불필요

Immediate next:
- P00 먼저 실행
- receipt / study audit / actual runtime / anchor method / Global:Local 분포 확인
- PASS 후 P01~P05 진행

ConvNeXt training Notebook은 cache P00 및 전체 cache QA 후 생성한다.

## C-CACHE-V2 — 현재 실행 항목

- 실행할 Notebook: `C_CACHE_V2_SIZE_PREFLIGHT.ipynb`
- 목적: Window는 그대로 두고 per-slice 저장 중복만 제거했을 때 실제 전체 cache 용량과 최소 Pack 수 측정
- 128 Study에서 old triplet vs unique-pixel+index reconstruction bit-parity 검증
- safe target: 16.5 GiB/Pack, projected total에 15% margin
- 이 결과 전에는 full cache Pack 수를 확정하지 않는다.
- 기존 `C_ANATOMY_CACHE320_V1_P00~P05`는 실행 금지.
