<!-- CONVNEXT_V2_DESIGN_PHASE_2026_10_18 -->
## 2026-10-18 — Branch-C 설계 재검토 단계 진입

- **실제 학습/캐시 실행 결과는 아직 없음.**
- Current state: `C-DESIGN-V2_REVIEW / NOT_RUN`.
- Branch-A S11 standalone 0.926과 Branch-B Wide96 V3 2F training 경험을 반영해 기존 C-DESIGN-V1을 재검토한다.
- supervision은 LABEL-V6가 아니라 **V4 Routed Broad Base**를 우선 기준으로 검토.
- 후속 **V4 Strict FT**와 2-Fold 구조를 우선 논의.
- exact ConvNeXt pretrained/anatomy anchor가 고정되기 전에는 실행 Notebook 생성 금지.
- high-score ConvNeXt source bundle의 `compact_train.py`, `compact_infer.py`, `knee_anchor_bank_v2.py`, `side_common.py` 계보를 코드 기준으로 audit한 뒤 C-DESIGN-V2를 확정한다.

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
