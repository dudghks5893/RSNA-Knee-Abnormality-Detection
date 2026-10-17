### Branch-B training 상태 — 2026-10-17

- Wide96 Native384 cache 4 Pack: **COMPLETE / PASS**
- supervision: **V4 Routed Broad**, 4,349 Studies, SHA `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`
- V4 pseudo weight: `0.25 + 0.75×confidence`
- LABEL-V6 B는 Branch-B 학습에 사용하지 않음
- CoAtNet pretrained:
  `/kaggle/input/models/blueberry808/coatnet-rmlp-2-rw-384-sw-in12k-ft-in1k/pytorch/default/1/coatnet_rmlp_2_rw_384_sw_in12k_ft_in1k.pth`
- feature dim: **1024**
- authoritative notebook: `B_COATNET_WIDE96_2F_BASE_V4.ipynb`
- notebook SHA: `45f77cd959d984577099b0a67f406b0e3f98296a4950d4b1a7dafeccc04f649f`
- V1/V2/V3: **DO_NOT_RUN**
- training mode: **Fold0→GPU0 / Fold1→GPU1 independent; DDP=false**
- Fold0: train V4 4349 + Gold Fold1 29 / val Gold Fold0 29
- Fold1: train V4 4349 + Gold Fold0 29 / val Gold Fold1 29
- physical Study batch: **4→2→1 actual training-graph benchmark**
- effective Study batch: **16 / Fold**
- V4: real HDF5 384→320 optimizer-step resource probe + **128 real Study runtime projection**
- V4: activation checkpoint uses **BN-safe recompute**; BatchNorm is not globally frozen
- projected concurrent 16ep wall time > **4.0h**이면 Epoch1 전에 block
- Base checkpoint: **Fold별 own Gold29 Macro AUROC best.pt 하나만 저장**
- no last / no SWA / no top3 averaging in Base
- immediate next: **V4 T4×2 Save & Run All → real HDF5 resource probe → 128-Study runtime gate → two independent 16ep folds → fold0/best.pt + fold1/best.pt**


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



### S11 상태 — 2026-10-17

- hidden-test diagnostic-safe 0.926 제출 **정상 제출 + Public LB 0.926** 확인.
  - 따라서 기존 robust DICOM / Stage1 / S8C selector path가 hidden에서도 실제 이미지 기반 예측으로 완료됨.
  - Study-level neutral 0.5 placeholder는 사용되지 않음.
- S11 Multi-View 2Fold training **COMPLETE**.
  - Fold0 LAST Gold29 AUC 0.921638
  - Fold1 LAST Gold29 AUC 0.864267
  - pooled Gold58 DEV Epoch1 0.892728 / Epoch2(LAST) 0.887924
- S11 LAST checkpoint SHA:
  - F0 `2c962f22a1ebc55de81ee674c0f8e9b2c69001f028bc3db19dd6b114aa8f2dec`
  - F1 `6647156f1bad9ed073b135ebea9c5bd4452d9483a17186c69a1dd04d22ae40bf`
- S11 LAST 2F standalone submission notebook generated; local SHA:
  `8704eb57f9a6e19b0befa842c8de9d3e9ce8ab3590575548fddec851a8e06739`.
- **Immediate next:** S11 LAST standalone Public LB → if useful, `S11 70 + S8C Direct 30`.
- Epoch1 is locally stronger than LAST on pooled Gold58 DEV and remains a follow-up submission candidate if retained.


### Branch-B cache 상태 — 2026-10-17

- CoAtNet Wide96 metadata/header PRE-FLIGHT **PASS**.
- Wide96 Native384 실제 HDF5 cache **4 Pack 전부 PASS / CACHE_COMPLETE**.
- Study split: **1102 / 1102 / 1102 / 1101 = 4,407 Studies**.
- HDF5 structure: `volume [N,96,384,384] uint8` + `valid_mask [N,96]`.
- logical positions: 423,072 / valid 406,966 / missing 16,106 / decode failure 0.
- selected non-missing Series: 20,792; 실제 sort는 전부 IOP_IPP.
- Dataset paths/SHA는 `docs/COATNET/COATNET_BRANCH_PLAN.md` 최상단에 authoritative하게 기록.
- Branch-B CoAtNet 16ep 본학습 notebook 생성 완료: `B_COATNET_WIDE96_FT_V1.ipynb`, SHA `5ba2c615cf6dad9fb573b6929ac45aa236643922e2c61df2a0b680c61b269109`.
- **다음:** 최신 B soft-label artifact + exact CoAtNet pretrained weight를 Kaggle input에 고정 → Save & Run All.
