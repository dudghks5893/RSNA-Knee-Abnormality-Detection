# RSNA Knee — Rules for AI coding agents

**2026-10-21 이후 최우선 문서 정책:** 기존 계열에 더해 사용자 지시로 **Weak2 Direct Specialist**를 독립 계열로 분리한다. 각 계열은 **기존 누적 문서에만 기록**하며, Weak2도 아래 3개 누적 문서만 갱신한다.

| 실험 계열 | 실제 결과 누적 | 로드맵 / 계약 |
| --- | --- | --- |
| Exp01~Exp63 | `docs/EXP/EXP_EXPERIMENT_HISTORY.md` | `docs/EXP/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md` (역사적) |
| Specialist SS | `docs/SPECIALIST/SPECIALIST_EXPERIMENT_LOG.md` | `docs/SPECIALIST/SPECIALIST_EXPERIMENT_ROADMAP.md` |
| R3D, R2D, RMIL | `docs/RESNET_RMIL/EXPERIMENT_HISTORY.md` | `docs/RESNET_RMIL/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md` |
| S1, S1FT02, S7, S8 및 이후 S | `docs/DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md` | `docs/DINO_S/S1-DINO-CBL2F-01_ROADMAP.md`, `docs/DINO_S/S1-DINO-CBL2F-01_DATA_MODEL.md` |\n| Weak2 Direct (W2D) | `docs/WEAK2/WEAK2_EXPERIMENT_LOG.md` | `docs/WEAK2/WEAK2_ROADMAP.md`, `docs/WEAK2/WEAK2_DATA_MODEL.md` |

- Weak2 Direct는 기존 selector 기반 Specialist SS와 분리한다. 목적은 **Synovitis + Lateral OA 전용 selector-free 단일 predictor**이며, Kaggle notebook source는 GitHub에 저장하지 않고 문서만 남긴다.\n- RMIL-04C02의 ResNet vs DINO-Small 비교는 모델 종류가 아니라 **RMIL 실험 번호** 기준으로 ResNet·RMIL에 보관한다.
- **새로운 실험, QA 또는 버그 수정마다 새 Markdown 보고서를 생성하지 않는다.** 해당 계열 누적 파일을 업데이트한다.
- 공통 노트북/GPU/라벨 정책은 `docs/`에 둔다. [현재 인수인계](docs/CURRENT_HANDOFF.md), [Kaggle 규칙](docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md), [GPU 정책](docs/GPU_BATCH_RESOURCE_MANDATORY_POLICY.md)부터 확인한다.
- 과거 개별 보고서의 `NEXT`, `CURRENT` 등은 해당 문서 작성 당시 상태로, 현재 최신 결정과 충돌 시 과거 기록으로 취급한다.

## Kaggle GPU 자원 정책

## Highest priority: limited Kaggle GPU budget

The user reports **previous GPU memory profiling found substantial VRAM headroom even at Batch Size >=124** in early experiments (exact historic model/microbatch semantics not established). This repeated user-reported result **MUST NOT BE FORGOTTEN**. Never presume T4 GPUs necessarily require Window Microbatch=1 or 4. The RMIL-04C02 DINOv2-Small microbatch=1 choice without profiling incurred **217.15 minutes/epoch** (compare R34 46.33 min/epoch) and consumed limited GPU budget. Avoid repeating.

**Important:** Historic Batch>=124 is **not** a blanket guarantee for DINOv2 Full Fine-tuning K16. Test actual memory and end-to-end throughput of *this* model/input/backward before claiming a batch is safe. Keep Study Global Batch and Window Microbatch separately documented. Report choices that affect runtime/VRAM; do not silently lower batches. Profile Window microbatches upward from realistic sizes, record measured peak VRAM and steps/sec, estimate 5–10 Epoch total vs Kaggle session/time budget, verify checkpoint resumption before lengthy training. Request user review of material changes.



## 재현성·안전성 규칙

## Reproducibility and safety

- Always keep input exact Kaggle dataset/model paths, pinned hashes, data split and Gold58 handling; never mix Gold58 into train labels.
- LABEL-V6 is `CANDIDATE_NOT_RELEASED` until explicit release.
- All Kaggle notebooks: Korean cell descriptions, unambiguous numbered Add Input, Internet OFF, GPU/CPU settings, Save & Run All execution, experiment ID, save name <60 characters, runtime/budget assumptions, full code & output structural QA.
- DDP smoke needs **2+ consecutive optimizer steps**, plus actual full pipeline forward/backward/optimizer, output package dry-run, and a tested resume path.
- Do not claim Kaggle GPU tests or Kaggle LB submissions unless actual logs/artifacts confirm.
