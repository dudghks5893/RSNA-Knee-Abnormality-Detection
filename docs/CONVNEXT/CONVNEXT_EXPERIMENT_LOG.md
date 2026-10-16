# Branch-C ConvNeXt — Cumulative Experiment Log

최종 갱신: **2026-10-17**

계획은 [CONVNEXT_BRANCH_PLAN.md](CONVNEXT_BRANCH_PLAN.md), 실제 실행 결과는 이 문서에 누적한다.

## Status

- Branch: **C — ConvNeXt Anatomy Expert**
- Current state: **NOT_RUN**
- Design version: **C-DESIGN-V1**
- 실행 우선순위: Branch-B 다음

## Experiment naming

```text
C-ANATOMY-CACHE320-V1
C-CNX-S64-FT-V1
C-CNX-S64-MIRROR-TTA-V1
AC-RANK-BLEND-V1
ABC-RANK-BLEND-V1
```

실제 실행마다 반드시 기록:
- 날짜
- notebook/SHA
- Kaggle Save Version
- input paths/SHA
- anatomy checkpoint identity
- GPU/CPU
- runtime
- cache/view counts
- model config
- checkpoint SHA
- Gold58 DEV
- Public LB
- correlation with A/B
- ensemble LB
- next decision

## Public LB table

| Experiment | Model | Public LB | Status |
|---|---|---:|---|
| — | — | — | NOT_RUN |

## Cache table

| Cache | Studies | Rows/Views | Packs | SHA | Status |
|---|---:|---|---:|---|---|
| C-ANATOMY-CACHE320-V1 | TBD | variable | preflight에서 결정 | TBD | NOT_RUN |

## Decision log

### 2026-10-17 — Branch-C 설계 시작
- 시간이 허락할 경우 Branch-B 이후 진행.
- S8C Top18 비사용.
- Full-FOV + 100mm anatomy-centered local views.
- thin 3D stack은 약 3.5mm slab로 변환.
- ConvNeXt-Small full fine-tuning.
- target-specific spatial attention + target-specific window MIL.
- 64 windows/Study.
- 4,349 report studies full train, Gold58 제외.
- 16 epoch, encoder 1e-4/head 1e-3, WD .05, cosine+5% warmup.
- standalone → mirror TTA → A+C/A+B+C rank blend로 평가.
