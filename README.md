# RSNA Knee Abnormality Detection

Kaggle RSNA Knee MRI 연구 결과는 다음 **7개 실험 계열/Branch 폴더**에서 관리해. 원래 이 README에 있던 초기 Exp01~Exp63 전문은 Exp 폴더로 보존·이관했어.

| 실험 계열 | 결과·관측 기록 | 진행 및 계획 |
|---|---|---|
| **01 — Exp** | [Exp 실험 전체 기록](docs/EXP/EXP_EXPERIMENT_HISTORY.md) | [Exp 시절 5-Fold 계획](docs/EXP/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md) |
| **02 — Specialist** | [Specialist 실험 로그](docs/SPECIALIST/SPECIALIST_EXPERIMENT_LOG.md) | [Specialist Roadmap](docs/SPECIALIST/SPECIALIST_EXPERIMENT_ROADMAP.md) |
| **03 — ResNet·RMIL** | [R3D/RMIL 통합 결과](docs/RESNET_RMIL/EXPERIMENT_HISTORY.md) | [R3D/RMIL Roadmap](docs/RESNET_RMIL/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md) |
| **04 — DINO·S / Branch-A** | [S 계열 누적 로그](docs/DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md) | [S 계열 Roadmap](docs/DINO_S/S1-DINO-CBL2F-01_ROADMAP.md) |
| **05 — CoAtNet / Branch-B** | [CoAtNet 실험 로그](docs/COATNET/COATNET_EXPERIMENT_LOG.md) | [CoAtNet 설계/로드맵](docs/COATNET/COATNET_BRANCH_PLAN.md) |
| **06 — ConvNeXt / Branch-C** | [ConvNeXt 실험 로그](docs/CONVNEXT/CONVNEXT_EXPERIMENT_LOG.md) | [ConvNeXt 설계/로드맵](docs/CONVNEXT/CONVNEXT_BRANCH_PLAN.md) |
| **07 — Weak2 Direct Specialist** | [Weak2 실험 로그](docs/WEAK2/WEAK2_EXPERIMENT_LOG.md) | [Weak2 Roadmap](docs/WEAK2/WEAK2_ROADMAP.md) |

## 5페이지 연구 성과 PDF

- [RSNA Knee 연구 성과 최종 보고서 (PDF)](RSNA_Knee_Research_Final_Report_2026.pdf)
- 외부 독자를 위한 5페이지 기술 보고서: 문제 정의, 데이터·평가 기준, 주요 모델 연구, 앙상블 및 추론 안정화, 최종 평가·한계를 설명.
- Study/Series/Slice, 판독문 기반 약지도 학습, MIL/Attention, Public/Private Macro-AUC 등 핵심 용어를 설명하며, 내부 실험 번호 대신 방법과 성과 중심으로 구성.
- 자체 학습 연구와 외부 공개 checkpoint를 활용한 최종 앙상블을 분리해 서술.
- 최종 공식 성적: **Private 0.941 / 949위**. 최종 MAIN Public **0.958**, Public 최고 위치 약 **240위**.
- 마지막 W2D-05의 Gold58 ROC-AUC: 활막염 **0.8076**, 외측 골관절염 **0.8221** (내부 개발 검증).
- 개발용 Gold58 검증과 공식 Public/Private 점수를 구별하고, 공개 pretrained/reader 활용을 자체 모델 연구와 구분함.

## 대회 최종 결과 — 2026-10-23

> **Competition closed / project archived.**  
> 최신 authoritative summary는 [Final Competition Summary](docs/FINAL_COMPETITION_SUMMARY.md)를 따른다.

| 항목 | 결과 |
|---|---:|
| 최종 MAIN Public LB | **0.958** |
| 최종 MAIN Private LB | **0.941** |
| Public leaderboard 최고 위치 | **약 240위** |
| 공식 최종 순위 | **949위** |

- 마지막 제출 세트에서는 **MAIN 버전만 정상 제출에 성공**했다. MAIN은 공개 CoAt + R6 예측에 자체 W2D-05 보강 모델을 **활막염·외측 골관절염 두 타깃에 각각 27.5%** 결합한 구성으로, Public LB는 기존 최고와 동일한 **0.958**이었다.
- 대회 종료 후 Private leaderboard 공개 결과, 최종 MAIN은 **0.941**.
- Public 0.958은 대회 중 최고 성과이지만 최종 공식 성적은 **Private 0.941 / 949위**로 기록한다.
- 모든 기존 문서의 `NEXT`, `RUNNING`, `CURRENT` 표기는 역사적 기록이며 더 이상 실행 지시가 아니다.
- 추가 Kaggle 실험/제출은 종료하며 저장소는 재현성과 포트폴리오 회고용으로 보존한다.

## 공통 운영 문서

- [대회 최종 요약](docs/FINAL_COMPETITION_SUMMARY.md)
- [현재 인수인계](docs/CURRENT_HANDOFF.md)
- [Kaggle 노트북 / AI Agent 공통 규칙](docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
- [GPU 자원·Batch 정책](docs/GPU_BATCH_RESOURCE_MANDATORY_POLICY.md)
- [LABEL-V6 정책](docs/LABEL_RECONSTRUCTION_POLICY_V2.md)
- [AGENTS.md](AGENTS.md)

**관리 원칙:** 새로운 실험당 별도 `.md` 문서를 만들지 않고, 해당 계열의 **기존 누적 로그·Roadmap·모델 계약**에만 갱신해. 이전 세부 QA·설계 문서는 해당 계열 폴더의 역사적 참고자료로 보존해.
