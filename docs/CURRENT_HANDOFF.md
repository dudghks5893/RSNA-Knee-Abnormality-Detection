## 2026-10-18 — B/C early stopping + best-only checkpoint policy 확정

Branch-B:
- V3 actual run은 Fold0 NaN → validation crash로 중단.
- Fold1은 Epoch8 Gold29 Macro AUROC 0.896024까지 개선했으나 2F run은 무효.
- 다음 실행: `B_COATNET_WIDE96_2F_BASE_V5_STABLE_ES.ipynb`
- SHA `425ef5c973de1b04513592706416c63ec439d551783f28df7b92f5e8620aa0a5`
- max16 / min6 / patience3 / own Gold29 Macro AUROC early stop / best.pt only.
- B V5는 MIL head FP32, head LR1e-3, non-finite fail-fast, sibling terminate 포함.

Branch-C:
- 다음 실행: `C_CONVNEXT_GEOM64_2F_BASE_V3_ES_STABLE.ipynb`
- SHA `3800699a9dba69947ebeb4e989ee31a46b874c37e23d4194fbfad174f547451a`
- max16 / min6 / patience3 / own Gold29 Macro AUROC early stop / best.pt only.
- no last/epoch/SWA checkpoints.
- non-finite fail-fast + sibling terminate.

## 2026-10-18 — C-BASE-01 ConvNeXt Geometry64 2F training notebook READY

상태: **CACHE_COMPLETE / TRAIN_NOTEBOOK_READY / TRAIN_NOT_RUN**

Authoritative training notebook:
- `C_CONVNEXT_GEOM64_2F_BASE_V1.ipynb`
- SHA256: `d95f4921d7587089c803c0bef0ec15e384fa6d78774ecdc0506c556bf69e74eb`
- source 43,250 bytes (<1MB)
- nbformat PASS / all code AST PASS / embedded worker AST PASS

Scientific contract:
- Backbone: `convnext_small.fb_in22k_ft_in1k`
- official timm pretrained `model.safetensors`
- pretrained bytes: 200,928,946
- pretrained SHA256: `2457488bec2ffcb2061b9e3fdd63360114549615e3e35ef6dc5c5efe549cbbc9`
- C-CACHE-V4 exact 5 HDF5 paths/SHA gate
- 64 windows/Study, 320 cache → 288 train/val
- target-specific spatial attention on final ConvNeXt feature map
- target-specific Window MIL + 8-channel metadata attention gate
- V4 Routed Broad 4,349 + opposite Gold29 train / own Gold29 val
- Fold0 GPU0 / Fold1 GPU1 independent, No DDP
- 16 fixed epochs / no early stopping
- Base checkpoint = Fold own-Gold29 Macro AUROC best.pt only
- encoder LR 1e-4 / head LR 1e-3 / AdamW WD .05 / warmup5% / cosine / FP16 / clip5 / seed42
- rare-positive Study sampler: MCL3, Fracture2.5, Contusion2, Baker1.5, PF OA1.5

Mandatory execution gate before Epoch1:
- exact T4×2
- real HDF5 optimizer-step probe
- physical Study batch 2→1
- Window chunk 64→48→32→24→16→12→8→6→4→2; chunk1 forbidden
- 128 real train Studies per Fold benchmark
- full own-Gold29 validation timing
- both probes run concurrently to include I/O contention
- projected 16ep wall time +10% margin >4h → fail-fast before full training

Required new model input:
- official timm/Hugging Face `timm/convnext_small.fb_in22k_ft_in1k`
- exact safetensors SHA above; random-init/alternative backbone fallback forbidden.

Immediate next:
1. Kaggle Add Input에서 exact ConvNeXt Small pretrained model을 attach.
2. T4×2 / Internet OFF / Save & Run All.
3. probe PASS 및 projected <=4h이면 Notebook이 자동으로 Fold0/Fold1 본학습 시작.
4. projected >4h 또는 input path gate fail이면 full train은 시작하지 않고 probe/input 결과를 공유해 수정.

## 2026-10-18 — C-CACHE-V4 5-Pack FULL CACHE COMPLETE / TRAIN READY

- Final audit: [C_CACHE_V4_FINAL_AUDIT.md](C_CACHE_V4_FINAL_AUDIT.md)
- 5/5 Packs PASS, full readback PASS.
- 4,407 unique Studies, overlap 0, missing 0.
- 282,048 valid windows = exactly 64 per Study.
- decode failure 0 / prep skip 0.
- dense `64×3×320×320 uint8`, total HDF5 about 80.723 GiB.
- Kaggle dataset paths and HDF5 SHA256 are frozen in the final audit.
- rare crop coverage <0.90: 493/282,048 (0.175%), all Axial local views; this is source-FOV<110mm behavior under the frozen available-extent contract, not a regeneration trigger.
- **Cache status: FINAL / DO NOT REBUILD.**
- Immediate next: C-BASE ConvNeXt-Small 2-Fold training notebook and actual T4×2 runtime/resource probe.

## 2026-10-18 Branch-C cache latest

C-CACHE-V3 segmentation-free geometry preflight completed:
- PASS 128/128, 1.77 min
- exact 64 windows = Global32 + Local32
- no external anatomy/segmentation
- dedup ratio 0.9959 → storage dedup is not useful

Final cache storage decision:
- C-CACHE-V4 dense windows
- shape per Study: 64×3×320×320 uint8
- 5 Packs: 882/882/881/881/881
- 5 Pack is the minimum that stays below the 19 GB output cap
- local crop uses 110 mm shift-to-fit; source FOV<110 mm only uses available extent

Next:
- Run P00 first: `C_GEOM_MV320_CACHE_V4_P00.ipynb`
- If final `C GEOM MV320 CACHE PACK PASS`, continue P01~P04.
- Do not run old V1/V2/V3 full-cache notebooks.


## 2026-10-18 — C-CACHE-V3 Preflight V2 PATHFIX

- V1 preflight bug: Competition DICOM directory를 `train_images/`로 잘못 고정해 첫 input gate에서 실패.
- 실제 competition layout은 `train_series/` DICOM directory를 사용한다. 공개 inference 참고에서도 test side는 `test_series/`를 사용.
- 수정 Notebook: `C_CACHE_V3_GEOMETRY_PREFLIGHT_V2_PATHFIX.ipynb`
- SHA256: `cb9fedf405984c7ab8cd84d5172b69c272543e6e75d3dfe564d50064213f632b`
- Input root resolver:
  1. `/kaggle/input/competitions/rsna-knee-abnormality-detection`
  2. `/kaggle/input/rsna-knee-abnormality-detection`
- DICOM root resolver: `train_series/` 우선, `train_images/`는 compatibility fallback만 허용.
- 전체 `/kaggle/input` recursive scan 금지.
- 선택된 competition root / DICOM root는 실행 로그와 receipt에 기록.
- 기존 `C_CACHE_V3_GEOMETRY_PREFLIGHT.ipynb`는 **OBSOLETE / DO_NOT_RUN**.
- 설계(Global+geometry local, max64 overlapping 2.5D, unique-row storage)는 변경 없음.


---



## 2026-10-18 — Hidden-test submission issue / diagnostic-safe resolution

이 항목은 이후 모든 submission Notebook의 공통 robustness contract다.

### 기존 문제
- strict DICOM/header/slice assert가 작은 slice/Series 오류를 Study 실패로 확대할 수 있었음.
- Study 전체 실패 시 neutral `0.5` placeholder를 넣는 fallback은 Notebook 제출 자체는 성공시켜도 실제 MRI inference 실패를 숨길 수 있었음.

### 해결
1. Series 정렬: **IOP/IPP physical position → InstanceNumber → natural filename**.
2. 누락 가능한 header는 무조건 strict assert하지 않고 실제 사용 가능한 geometry를 우선.
3. 개별 slice decode 실패는 nearest-valid decoded slice 등 deterministic slice rescue.
4. bad Series는 skip하고 같은 Study의 다른 실제 Series를 계속 사용.
5. Fold/branch 일부 실패 시 surviving real-image Fold/branch로 rescue.
6. S8C selector가 모두 실패하는 예외에는 label-free deterministic emergency Top18만 허용.
7. **Study-level 0.5 fallback 제거**. 실제 MRI 기반 prediction branch가 하나도 없으면 submission을 억지로 완성하지 않고 intentional FAIL.

### 검증
Diagnostic-safe Notebook:
`S10_LAST_70_S8C_DIRECT_30_2F_LB_SUBMISSION_V3_DIAGNOSTIC_SAFE.ipynb`

실제 hidden test에서 robust DICOM/Stage1/S8C selector/direct/final branch가 실제 이미지 기반으로 완료되었고,
**Study-level neutral 0.5 fallback 0건 / Public LB 0.926**으로 정상 검증됨.

S11 standalone 및 S11 70:30 Notebook은 이 hidden-tested robust path를 기반으로 작성됨.

### 이후 공통 규칙
- slice → Series → Fold → Branch 순서의 실제 이미지 rescue.
- skipped Series / alive Fold / rescue count를 audit CSV/JSON에 기록.
- hidden selector에 V4/Gold 정답 방향 사용 금지.
- **Study-level 0.5 placeholder 금지.**
- real-image prediction branch 0개면 fail-fast.

<!-- ACTUAL_STATUS_2026_10_18_BRANCH_C_START -->
## 2026-10-18 — Branch A/B/C 통합 current status

상세 cold-start 문서:
- [RSNA_KNEE_BRANCH_C_START_HANDOFF_2026-10-18.md](RSNA_KNEE_BRANCH_C_START_HANDOFF_2026-10-18.md)

### Branch-A
- **S11 LAST 2F standalone Public LB = 0.926** 확정.
- 현재 **S11 LAST 70% + S8C Full-MRI Direct 30% submission 진행 중 / LB 대기**.
- Notebook: `S11_LAST_70_S8C_DIRECT_30_2F_LB_SUBMISSION_V1.ipynb`
- SHA: `1936890da1c28fa1e55fdaf3981cc07e71b2b2b651afbcb39b50c63068b5ff5d`
- 결과가 >0.926이면 Branch-A main 승격. =0.926이면 S11 standalone과 S10 hybrid 둘 다 보존. <0.926이면 S11 standalone 0.926을 유지하고 무분별한 ratio search는 하지 않는다.

### Branch-B
- **실제 실행 상태는 V3 TRAIN_RUNNING**.
- 실행 중 Notebook: `B_COATNET_WIDE96_2F_BASE_V3.ipynb`
- SHA: `bb3527a1c8b6fd6f6585295413420720d341ee4c61b8b04de25ca1ee5a6bf3f4`
- Fold0→GPU0 / Fold1→GPU1 independent, DDP=false.
- **V3를 V4가 있다는 이유로 중단하지 않는다.**
- V4(`45f77cd...`)는 재실행 필요 시 또는 다음 유사 실험의 execution-hardening reference다.
- Base 결과 후 순서: **2F standalone LB → V4 Strict 고신뢰 FT → Strict standalone LB → Branch-A와 A+B ensemble**.
- Strict FT에서는 DINO precedent 때문에 `best.pt`와 `last.pt`를 둘 다 보존하는 방향을 우선 검토한다.

### Branch-C
- **C-DESIGN-V4 FROZEN / SEGMENTATION-FREE / PREFLIGHT_READY / NOT_RUN**.
- 역할: ConvNeXt **Geometry Multi-View Spatial Expert**.
- A의 S8C Top18과 B의 fixed Wide96을 재사용하지 않는다.
- DICOM IOP/IPP/PixelSpacing만으로 Global + Center + Anterior/Posterior + Coronal bilateral local views를 생성한다.
- anatomy segmentation model / anatomy.pt / 외부 reference dataset은 실행 dependency에서 제거.
- Study당 최대 64 overlapping 2.5D Window, unique rendered row + window_index cache.
- target-specific spatial attention → target-specific Window MIL.
- supervision 기본값: V4 Routed Broad + frozen Gold58 2-Fold.
- 현재 실행 Notebook: `C_CACHE_V3_GEOMETRY_PREFLIGHT.ipynb`
- SHA: `fda85064c4ce09bdd7501b985055ef90ba6ee39a54be43ea967e810a76e2e3ac`
- Immediate next: 128-Study geometry/capacity preflight → 실제 GB 기준 Pack 수 확정 → full cache build.

### S11 최신 상태 — 2026-10-18

- **S11 LAST 2F standalone Public LB = 0.926** (사용자 보고).
- S10 standalone 0.923 대비 **+0.003**.
- 기존 최고 `S10 70 + S8C Direct 30 = 0.926`과 standalone으로 동점.
- 다음 제출: **`0.70 × S11 LAST 2F + 0.30 × S8C Full-MRI Direct 2F`**.
- 제출 notebook:
  `S11_LAST_70_S8C_DIRECT_30_2F_LB_SUBMISSION_V1.ipynb`
- notebook SHA:
  `1936890da1c28fa1e55fdaf3981cc07e71b2b2b651afbcb39b50c63068b5ff5d`
- 정상 경로는 S11/S8C 각각 Fold0/1 probability mean 후 70:30 probability blend.
- S11 standalone hidden-test inference 경로를 그대로 유지하며 S8C Direct는 selector forward에서 이미 계산되는 값을 재사용.
- Study-level neutral 0.5 fallback 없음.
- **Immediate next: Kaggle T4×2 / Internet OFF / Save & Run All → Public LB 확인.**


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

Branch-C — ConvNeXt Geometry Multi-View Expert (시간 허용 시)
Segmentation-free DICOM geometry
  → Global + physical-offset Local Views
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
- Branch-C는 **Geometry Multi-View + spatial-localization expert**.
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