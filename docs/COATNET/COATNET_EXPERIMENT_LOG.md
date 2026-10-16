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
