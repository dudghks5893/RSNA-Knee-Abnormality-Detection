# RSNA Knee Abnormality Detection

Kaggle RSNA Knee MRI 연구 결과는 다음 **4개 실험 계열 폴더**에서 관리해. 원래 이 README에 있던 초기 Exp01~Exp63 전문은 Exp 폴더로 보존·이관했어.

| 실험 계열 | 결과·관측 기록 | 진행 및 계획 |
|---|---|---|
| **01 — Exp** | [Exp 실험 전체 기록](docs/EXP/EXP_EXPERIMENT_HISTORY.md) | [Exp 시절 5-Fold 계획](docs/EXP/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md) |
| **02 — Specialist** | [Specialist 실험 로그](docs/SPECIALIST/SPECIALIST_EXPERIMENT_LOG.md) | [Specialist Roadmap](docs/SPECIALIST/SPECIALIST_EXPERIMENT_ROADMAP.md) |
| **03 — ResNet·RMIL** | [R3D/RMIL 통합 결과](docs/RESNET_RMIL/EXPERIMENT_HISTORY.md) | [R3D/RMIL Roadmap](docs/RESNET_RMIL/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md) |
| **04 — DINO·S** | [S1FT02·S7·S8 누적 로그](docs/DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md) | [S 계열 Roadmap](docs/DINO_S/S1-DINO-CBL2F-01_ROADMAP.md) |

## 최신 확인 결과 — 2026-10-16

- S8A Mean MIL: **Public LB 0.918** (사용자 보고)
- **S8B 질환별 Window Attention MIL: Public LB 0.923** (사용자 보고, 현재 프로젝트 최고)
- 이전 Exp57: **0.918**, 이전 Full-MRI B2: **0.904**
- S7은 전체 4,407 Studies, 24,371 Series에서 770,336개의 유효 Window 특징을 추출했지만, 앞단 Strict-FT DINO 인코더는 Study당 18 Window로 Fine-tuning됐어.
- S8C 질환별 Window + Series Attention은 **다음 실험 후보**, 아직 미실행. Gold58은 반복 사용된 개발 검증 자료이므로 독립 테스트로 간주하지 않아.

## 공통 운영 문서

- [현재 인수인계](docs/CURRENT_HANDOFF.md)
- [Kaggle 노트북 / AI Agent 공통 규칙](docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
- [GPU 자원·Batch 정책](docs/GPU_BATCH_RESOURCE_MANDATORY_POLICY.md)
- [LABEL-V6 정책](docs/LABEL_RECONSTRUCTION_POLICY_V2.md)
- [AGENTS.md](AGENTS.md)

**관리 원칙:** 새로운 실험당 별도 `.md` 문서를 만들지 않고, 해당 계열의 **기존 누적 로그·Roadmap·모델 계약**에만 갱신해. 이전 세부 QA·설계 문서는 해당 계열 폴더의 역사적 참고자료로 보존해.
