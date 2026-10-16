# RSNA Knee — 현재 인수인계 및 문서 탐색

최종 갱신: **2026-10-17**. DINO·S 계보의 최신 authoritative source는 아래 3개 누적 문서다. 과거 개별 문서의 NEXT/CURRENT는 작성 당시 기록이며 최신 지시가 아니다.

| 계열 | 결과 | 로드맵 |
|---|---|---|
| Exp | [Exp01~Exp63](EXP/EXP_EXPERIMENT_HISTORY.md) | [초기 5-Fold 계획](EXP/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md) |
| Specialist | [SS 실험 기록](SPECIALIST/SPECIALIST_EXPERIMENT_LOG.md) | [SS Roadmap](SPECIALIST/SPECIALIST_EXPERIMENT_ROADMAP.md) |
| ResNet·RMIL | [R3D/RMIL History](RESNET_RMIL/EXPERIMENT_HISTORY.md) | [R3D/RMIL Roadmap](RESNET_RMIL/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md) |
| **DINO·S (현재)** | [실험 로그](DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md) | [Roadmap](DINO_S/S1-DINO-CBL2F-01_ROADMAP.md) · [Data/Model Contract](DINO_S/S1-DINO-CBL2F-01_DATA_MODEL.md) |

## 2026-10-17 최신 LB 업데이트

- **S10 LAST 70% + S8C Full-MRI Direct 30% = Public LB 0.926 (현재 최고)**.
- S10 standalone 0.923, S8C standalone 0.923에서 **+0.003 ensemble gain** 확인.
- 이 결과로 Exp57-style 구조인 “selector의 Full-MRI direct 예측 + selector가 고른 Top-K를 재판독한 final model” 조합이 현재 계보에서도 유효함을 확인.
- **DINOv2-Small V4 Broad 2F = Public LB 0.899**.
- Stage1 V4 Broad Base 0.910 대비 Small은 **-0.011**, 따라서 주력 backbone은 계속 DINOv2-Base.
- 현재 다음 실험은 **S11-TOP18-MULTIVIEW-AUG-FT-V1**. 목표는 current best 0.926 초과.
- S11 standalone 개선 후 첫 hybrid는 **70% S11 + 30% S8C Direct**.

### 현재 Public LB

| 모델/제출 | LB |
|---|---:|
| **S10 70 + S8C Direct 30** | **0.926** |
| S8B | 0.923 |
| S8C | 0.923 |
| S10 last 2F | 0.923 |
| S8A | 0.918 |
| Stage1 Strict FT last | 0.914 |
| Stage1 Broad Base | 0.910 |
| DINOv2-Small V4 Broad 2F | 0.899 |
| V54A Stage1 | 0.873 |

## 현재 권장 파이프라인

`Stage1-A Broad → Stage1-B Strict FT → Full-MRI feature → S8C selector/direct → S9 Top18 → S10 Top18 FT → S10 70% + S8C direct 30%`.

S11은 이 파이프라인의 selector/Top18/라벨을 바꾸지 않고 **영상 표현과 augmentation만 확장하는 후속 추가 FT**다.

## 재현성 필수 입력

- Native224 cache: `yhlucas/rmil-04b-full-mri-native224-v3`
- Shared manifest/sampler: `yhlucas/stage1-dino-shared-input-manifest-v1`
- Gold58 split: `yhlucas/rsna-knee-gold58-2fold-v1`
- V4 labels: `yhlucas/rsna-knee-v4-consensus-dataset`
- Stage1 Broad Base checkpoint: `woniyeon/rsna-knee-stage1-v4-f01-best-v1`
- Stage1 Strict FT Base checkpoint: `woniyeon/rsna-knee-s1ft02-b-v4strict-2fold-best-v1`
- S7 Base Full-MRI features: `woniyeon/s7-strictft-fullmri-full4407`
- S8B: `woniyeon/s8-mil-attn`
- S8C: `yhlucas/s8c-hier-attn-mil`

정확한 SHA, LR, loss, Stage별 설정은 반드시 [DINO·S Data/Model Contract](DINO_S/S1-DINO-CBL2F-01_DATA_MODEL.md)를 읽고 복원한다. 공통 Kaggle/GPU 규칙은 [AI Agent Notebook Rules](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md) 및 [GPU Batch Policy](GPU_BATCH_RESOURCE_MANDATORY_POLICY.md)를 따른다.
