# RSNA Knee — 현재 인수인계 및 문서 탐색

최종 갱신: **2026-10-17**. DINO·S 계보의 최신 authoritative source는 아래 3개 누적 문서다. 과거 개별 문서의 NEXT/CURRENT는 작성 당시 기록이며 최신 지시가 아니다.

| 계열 | 결과 | 로드맵 |
|---|---|---|
| Exp | [Exp01~Exp63](EXP/EXP_EXPERIMENT_HISTORY.md) | [초기 5-Fold 계획](EXP/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md) |
| Specialist | [SS 실험 기록](SPECIALIST/SPECIALIST_EXPERIMENT_LOG.md) | [SS Roadmap](SPECIALIST/SPECIALIST_EXPERIMENT_ROADMAP.md) |
| ResNet·RMIL | [R3D/RMIL History](RESNET_RMIL/EXPERIMENT_HISTORY.md) | [R3D/RMIL Roadmap](RESNET_RMIL/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md) |
| **DINO·S / Branch-A (현재 Core)** | [실험 로그](DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md) | [Roadmap](DINO_S/S1-DINO-CBL2F-01_ROADMAP.md) · [Data/Model Contract](DINO_S/S1-DINO-CBL2F-01_DATA_MODEL.md) |
| **CoAtNet / Branch-B** | [누적 실험 로그](COATNET/COATNET_EXPERIMENT_LOG.md) | [Authoritative Plan](COATNET/COATNET_BRANCH_PLAN.md) |
| **ConvNeXt / Branch-C** | [누적 실험 로그](CONVNEXT/CONVNEXT_EXPERIMENT_LOG.md) | [Authoritative Plan](CONVNEXT/CONVNEXT_BRANCH_PLAN.md) |

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


## 2026-10-17 — 최종 모델 구성 방향: 3 Independent Experts

기존 Stage1→2→3 구조는 **Branch-A DINO Core**로 동결한다. 이후 Stage4/Stage5를 계속 덧붙이지 않고, 서로 다른 입력과 backbone을 사용하는 독립 Branch를 병렬로 추가한다.

```text
Branch-A — DINO Core
Stage1 DINOv2-Base 2F
  → S8C Full-MRI MIL/selector 2F
  → S10/S11 Top18 DINO FT 2F
  → 현재 최고 0.926 계보

Branch-B — CoAtNet Wide-MRI Expert
96-slice anatomical slots
  → 140mm / 384
  → CoAtNet
  → target-specific window attention
  → standalone
  → A+B rank blend

Branch-C — ConvNeXt Anatomy Expert (시간 허용 시)
Full-FOV + 100mm anatomy local views
  → thin-stack physical slab
  → ConvNeXt-Small
  → target-specific spatial attention
  → target-specific window MIL
  → A+B+C rank blend
```

### 설계 원칙

- B/C 모두 S8C Top18을 입력으로 사용하지 않는다.
- 목적은 같은 예측을 반복하는 모델 수 증가가 아니라 **오류 다양성**이다.
- Branch-B는 **Wide/Dense MRI coverage expert**.
- Branch-C는 **Anatomy-local + spatial-localization expert**.
- 최종 결합은 probability 단순 평균보다 **per-target percentile-rank ensemble**을 우선 검토한다.
- 현재 첫 실행 우선순위는 **S11 → Branch-B → Branch-C**.
- Branch-B/C는 안전 baseline이 목적이 아니며, 처음부터 고득점 가설 설정을 사용한다.

### Branch-B authoritative 문서

- [CoAtNet 폴더](COATNET/README.md)
- [CoAtNet Branch Plan](COATNET/COATNET_BRANCH_PLAN.md)
- [CoAtNet Experiment Log](COATNET/COATNET_EXPERIMENT_LOG.md)

### Branch-C authoritative 문서

- [ConvNeXt 폴더](CONVNEXT/README.md)
- [ConvNeXt Branch Plan](CONVNEXT/CONVNEXT_BRANCH_PLAN.md)
- [ConvNeXt Experiment Log](CONVNEXT/CONVNEXT_EXPERIMENT_LOG.md)

### 다음 새 채팅 권장 읽기 순서

1. `docs/CURRENT_HANDOFF.md`
2. 현재 작업 Branch의 `*_BRANCH_PLAN.md`
3. 해당 Branch의 `*_EXPERIMENT_LOG.md`
4. Branch-A 작업이면 기존 DINO_S Data/Model Contract 추가 확인

Branch-B/C의 최신 B soft-label 실제 Kaggle path/SHA는 아직 고정 전이다. 실행 노트북을 만들기 전에 반드시 실제 artifact를 확인하고 문서와 notebook gate에 고정한다.

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


### Branch-B cache 상태 — 2026-10-17

- CoAtNet Wide96 metadata/header PRE-FLIGHT **PASS**.
- 4,407 Studies / 24,371 Series / selected 20,792 Series.
- header failure 0.
- Pack 수 **4개 확정**: 1102 / 1102 / 1102 / 1101.
- Pack00~03 본 cache notebooks 제작/정적 QA 완료.
- 아직 실제 HDF5 cache는 NOT_RUN.
- 다음: Pack00~03 CPU Save & Run All → 4개 PASS 검증 → Branch-B CoAtNet 16ep training.
