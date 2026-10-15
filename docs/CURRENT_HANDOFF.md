# RSNA Knee — 현재 인수인계 및 문서 탐색

최종 폴더 정리: **2026-10-16**. 이전 98KB 통합 인수인계의 원문은 [ResNet·RMIL 과거 인수인계](RESNET_RMIL/CURRENT_HANDOFF_HISTORICAL.md)에서 보존하며, 오래된 NEXT는 현재 지시가 아니다.

| 계열 | 결과 | 로드맵 |
|---|---|---|
| Exp | [Exp01~Exp63](EXP/EXP_EXPERIMENT_HISTORY.md) | [초기 5-Fold 계획](EXP/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md) |
| Specialist | [SS 실험 기록](SPECIALIST/SPECIALIST_EXPERIMENT_LOG.md) | [SS Roadmap](SPECIALIST/SPECIALIST_EXPERIMENT_ROADMAP.md) |
| ResNet·RMIL | [R3D/RMIL History](RESNET_RMIL/EXPERIMENT_HISTORY.md) | [R3D/RMIL Roadmap](RESNET_RMIL/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md) |
| **DINO·S (최신)** | [S1FT02/S7/S8 로그](DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md) | [S Roadmap](DINO_S/S1-DINO-CBL2F-01_ROADMAP.md) · [데이터 모델](DINO_S/S1-DINO-CBL2F-01_DATA_MODEL.md) |

## 최신 기준 실험 상태

- S8A Mean MIL: **Kaggle Public LB 0.918** (사용자 공유)
- **S8B disease-specific Window Attention MIL: Public LB 0.923**, 현재 프로젝트 최고.
- 이전 Exp57 **0.918**, 이전 B2 Full MRI MIL **0.904**.
- DINO Stage1 Strict FT는 Study당 18개의 3-Slice Window를 학습. S7/S8은 해당 encoder를 사용하여 4,407 Studies, 24,371 Series, 770,336개의 모든 유효 Window 특징을 추출·MIL 학습. 두 단계를 혼동하지 않는다.
- Gold58은 반복 개발 검증에 사용돼 완전 독립 Test가 아님. Kaggle Private LB 미확인.
- 다음 **제안 단계(미실행)**: S8C Window+Series Attention 구조 비교; GPU 예산 및 학습 전 contract 확인.

**실험 관련 새 기록은 해당 4개 폴더의 기존 로그/로드맵에만 누적한다.** 공통 실행 규칙은 [AI Agent Notebook Rules](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md) 및 [GPU Batch Policy](GPU_BATCH_RESOURCE_MANDATORY_POLICY.md), 라벨은 [Label Policy V2](LABEL_RECONSTRUCTION_POLICY_V2.md)를 따른다.
