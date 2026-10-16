# RSNA Knee — 현재 인수인계 및 문서 탐색

최종 갱신: **2026-10-16**. DINO·S 계보의 최신 authoritative source는 아래 3개 누적 문서다. 과거 개별 문서의 NEXT/CURRENT는 작성 당시 기록이며 최신 지시가 아니다.

| 계열 | 결과 | 로드맵 |
|---|---|---|
| Exp | [Exp01~Exp63](EXP/EXP_EXPERIMENT_HISTORY.md) | [초기 5-Fold 계획](EXP/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md) |
| Specialist | [SS 실험 기록](SPECIALIST/SPECIALIST_EXPERIMENT_LOG.md) | [SS Roadmap](SPECIALIST/SPECIALIST_EXPERIMENT_ROADMAP.md) |
| ResNet·RMIL | [R3D/RMIL History](RESNET_RMIL/EXPERIMENT_HISTORY.md) | [R3D/RMIL Roadmap](RESNET_RMIL/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md) |
| **DINO·S (현재)** | [실험 로그](DINO_S/S1-DINO-CBL2F-01_EXPERIMENT_LOG.md) | [Roadmap](DINO_S/S1-DINO-CBL2F-01_ROADMAP.md) · [Data/Model Contract](DINO_S/S1-DINO-CBL2F-01_DATA_MODEL.md) |

## 최신 확인 결과

- Stage1 V4 Broad DINOv2-Base 2-Fold: Public LB **0.910**.
- Stage1 Broad→V4 Strict FT: Public LB **0.914**.
- S8A Full-MRI Mean MIL: **0.918**.
- S8B target-specific Window Attention MIL: **0.923**.
- S8C target-specific Window+Series Attention MIL: **0.923**.
- V54A 맞춤 Stage1 DINOv2-Base: **0.873** → 현재 V4 계열 대체하지 않음.
- S8B/S8C가 현재 확인된 최고 Public LB **0.923** 동률. 예측 기준선은 더 단순한 S8B, selector 역할은 Series Attention을 가진 S8C.

## 동결된 향후 파이프라인

`Stage1-A Broad DINO 2F → Stage1-B Strict high-confidence FT → Stage2 Full-MRI feature → S8B predictor/S8C selector → Full-MRI Top-K → Stage3 Top-K FT → Stage3 70% + S8B 30%`.

중요: selector ranking은 Hidden Test에서도 동일하게 실행해야 하므로 **정답 label 방향을 쓰지 않는 label-free absolute contribution**으로 고정한다. 최초 Stage3는 Top18로 시작한다.

## 지금 당장 할 다음 실험

**Top-K selector 실행은 보류. 다음 작업은 DINOv2-Small Stage1-A 통제 실험이다.**

- 실험 ID: `S1-DINO-SMALL-V4-2F-V1`.
- V4 Routed Broad, Gold58 29/29, Native224 V3, exact 18-window sampler, Seed20261013, loss/class balance, optimizer/scheduler, max12/patience4, effective Study batch4를 Base와 동일하게 유지.
- 유일한 과학적 변경: DINOv2-Base → DINOv2-Small. Small feature는 CLS384+PatchMean384=768-d, projection 768→256.
- physical Study batch/Window microbatch/checkpoint는 Small에서 throughput benchmark로 다시 선택 가능하지만 effective batch4는 바꾸지 않는다.
- MetaResearch Small model mount path/SHA는 Notebook preflight에서 실제 확인 후 기록하며 추정 SHA를 사용하지 않는다.
- 먼저 Stage1-A Small standalone Gold58/Public LB를 확인한 다음에만 Small Strict FT 및 downstream Stage2 진행 여부를 결정한다.

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
