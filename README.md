# RSNA Knee Abnormality Detection

Kaggle RSNA Knee MRI 연구 결과는 다음 **6개 실험 계열/Branch 폴더**에서 관리해. 원래 이 README에 있던 초기 Exp01~Exp63 전문은 Exp 폴더로 보존·이관했어.

| 실험 계열 | 결과·관측 기록 | 진행 및 계획 |
|---|---|---|
| **01 — Exp** | [Exp 실험 전체 기록](docs/EXP/EXP_EXPERIMENT_HISTORY.md) | [Exp 시절 5-Fold 계획](docs/EXP/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md) |
| **02 — Specialist** | [Specialist 실험 로그](docs/SPECIALIST/SPECIALIST_EXPERIMENT_LOG.md) | [Specialist Roadmap](docs/SPECIALIST/SPECIALIST_EXPERIMENT_ROADMAP.md) |
| **03 — ResNet·RMIL** | [R3D/RMIL 통합 결과](docs/RESNET_RMIL/EXPERIMENT_HISTORY.md) | [R3D/RMIL Roadmap](docs/RESNET_RMIL/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md) |
| **04 — DINO·S / Branch-A** | [S 계열 누적 로그](docs/DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md) | [S 계열 Roadmap](docs/DINO_S/S1-DINO-CBL2F-01_ROADMAP.md) |
| **05 — CoAtNet / Branch-B** | [CoAtNet 실험 로그](docs/COATNET/COATNET_EXPERIMENT_LOG.md) | [CoAtNet 설계/로드맵](docs/COATNET/COATNET_BRANCH_PLAN.md) |
| **06 — ConvNeXt / Branch-C** | [ConvNeXt 실험 로그](docs/CONVNEXT/CONVNEXT_EXPERIMENT_LOG.md) | [ConvNeXt 설계/로드맵](docs/CONVNEXT/CONVNEXT_BRANCH_PLAN.md) |

## 최신 확인 결과 — 2026-10-17

- **현재 최고 Public LB: 0.926**
  - S10 LAST 2F 70% + S8C Full-MRI Direct 2F 30%
- S10 standalone 0.923 / S8C standalone 0.923 → hybrid +0.003.
- DINOv2-Small V4 Broad 2F = 0.899, Base V4 Broad = 0.910. DINO Core main backbone은 Base 유지.
- 현재 DINO Core의 다음 실험은 S11 Multi-View 추가 FT.
- 모델 구성은 Stage를 계속 늘리는 방식 대신 **3 Independent Experts**로 확장:
  - Branch-A: DINO Core
  - Branch-B: CoAtNet Wide-MRI
  - Branch-C: ConvNeXt Anatomy (시간 허용 시)
- 실행 우선순위: **S11 → CoAtNet Branch-B → ConvNeXt Branch-C**.

## 공통 운영 문서

- [현재 인수인계](docs/CURRENT_HANDOFF.md)
- [Kaggle 노트북 / AI Agent 공통 규칙](docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
- [GPU 자원·Batch 정책](docs/GPU_BATCH_RESOURCE_MANDATORY_POLICY.md)
- [LABEL-V6 정책](docs/LABEL_RECONSTRUCTION_POLICY_V2.md)
- [AGENTS.md](AGENTS.md)

**관리 원칙:** 새로운 실험당 별도 `.md` 문서를 만들지 않고, 해당 계열의 **기존 누적 로그·Roadmap·모델 계약**에만 갱신해. 이전 세부 QA·설계 문서는 해당 계열 폴더의 역사적 참고자료로 보존해.
