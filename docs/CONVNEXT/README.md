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

## Current cache action — 2026-10-18

C-CACHE-V3 geometry preflight PASS.

Authoritative next action:
1. Run `C_GEOM_MV320_CACHE_V4_P00.ipynb` first.
2. Require final `C GEOM MV320 CACHE PACK PASS`.
3. Inspect cache_summary / HDF5 size / decode failures / crop coverage.
4. If P00 PASS, run P01~P04.

Frozen storage:
- 5 Packs, counts 882/882/881/881/881
- dense 64×3×320×320 uint8
- no compression
- 8-channel window metadata
- segmentation/anatomy external model 없음


# Branch-C — ConvNeXt Geometry Multi-View Expert

최종 갱신: 2026-10-18

## Current

- Design: **C-DESIGN-V4 AUTHORITATIVE**
- Preprocessing: **Segmentation-Free**
- Preflight: **C-CACHE-V3 READY / STATIC_QA_PASS**
- Cache: NOT_RUN
- Training: NOT_RUN

Branch-C의 목적은 A/B와 다른 오류 패턴을 만드는 것이다.

- A = DINO Search/Selector expert — 전체 MRI에서 중요한 Window를 찾아 Top18 재판독.
- B = CoAtNet Wide/Dense expert — fixed Wide96로 전체 MRI를 촘촘히 coverage.
- C = ConvNeXt Geometry Multi-View Spatial expert — Global + 물리 위치가 다른 Local View를 만들고 Window 내부 spatial attention까지 학습.

## Branch-C data

Raw DICOM
→ IOP/IPP physical ordering
→ PixelSpacing geometry
→ thin stack 3.5mm slab
→ Global + Center + Anterior/Posterior + Coronal bilateral local views
→ unique rendered row cache 320
→ max64 overlapping 2.5D windows
→ ConvNeXt spatial attention
→ Window MIL

**Anatomy segmentation model은 사용하지 않는다.**

## Required Input

- RSNA Knee Abnormality Detection competition only.

외부 reference code/dataset은 아이디어 참고용이며 C 실행 dependency가 아니다.

## Current Notebook

`C_CACHE_V3_GEOMETRY_PREFLIGHT.ipynb`

SHA256:
`fda85064c4ce09bdd7501b985055ef90ba6ee39a54be43ea967e810a76e2e3ac`

- CPU 권장
- Internet Off
- 128 Studies
- actual crop coverage / window distribution / cache size projection 측정
- recommended Pack count 계산

## DO NOT RUN

- C_ANATOMY_CACHE320_V1_P00~P05
- C_CACHE_V2_SIZE_PREFLIGHT
- segmentation-based V3 cache notebooks

## Read order

1. [CONVNEXT_BRANCH_PLAN.md](CONVNEXT_BRANCH_PLAN.md)
2. [CONVNEXT_EXPERIMENT_LOG.md](CONVNEXT_EXPERIMENT_LOG.md)
3. [../CURRENT_HANDOFF.md](../CURRENT_HANDOFF.md)


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


## 2026-10-18 cache preflight current
- Current: `C_CACHE_V3_GEOMETRY_PREFLIGHT_V3_QUOTAFIX.ipynb`
- SHA: `5035315bd91d7db98762d2bd7eaf2710987e2c67863fc6d37960e1ee1101daa8`
- V2 reached 128/128 Study but failed the 64-window hard cap due to allocator overflow.
- V3 fixes quota allocation and adopts validated Branch-B DICOM reader patterns.