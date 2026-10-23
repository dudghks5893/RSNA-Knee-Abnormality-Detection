> **PROJECT ARCHIVED — 2026-10-23**  
> RSNA Knee competition is closed. Final official result: **Private 0.941 / rank 949**; final MAIN Public **0.958**, Public peak about **240th**. An earlier 70:30 ratio submission scored **Private 0.942**.  
> All `NEXT`, `RUNNING`, `READY`, and future experiment instructions below are historical records only. Do not resume them as active competition work.  
> Authoritative closure: [FINAL_COMPETITION_SUMMARY.md](../FINAL_COMPETITION_SUMMARY.md) and [CURRENT_HANDOFF.md](../CURRENT_HANDOFF.md).

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

# 2026-10-18 — C-CACHE-V3 PREFLIGHT PASS → C-CACHE-V4 5-Pack 본 캐시 동결

상태: **C-DESIGN-V4 / PREFLIGHT_PASS / FULL_CACHE_5PACK_READY / FULL_CACHE_NOT_RUN**

실제 실행 결과:
- 128/128 Studies PASS, error 0
- runtime 1.77 min
- 64 windows/Study exact
- Global 32 / Local 32 exact
- max windows 64 / zero-window Study 0
- sample Series ordering: IOP/IPP 734/734
- external anatomy model 없음 / segmentation 없음
- competition-only input

Storage finding:
- mean unique rendered rows = 191.211 / 192
- mean storage ratio vs dense triplet = 0.9959
- 즉 dedup 절감은 평균 약 0.41%뿐이며 128 Study 중 108 Study는 192/192 unique로 절감이 0이었다.
- 따라서 V4 본 cache는 indirect unique-row/index 구조를 폐기하고 **dense [N,64,3,320,320] uint8**로 단순화한다.
- 이는 sampling/window 의미를 바꾸는 것이 아니라 저장 형식만 단순화하는 결정이다.

Pack count:
- 4 Pack max 1,102 Studies 기준 raw pixel payload가 약 21.66 GB로 19 GB output cap 초과 → 불가.
- 5 Pack counts = 882 / 882 / 881 / 881 / 881.
- max Pack raw pixel payload = 17.3408256 GB (16.1499 GiB).
- metadata + 250 MB safety allowance 포함 약 17.593 GB.
- 따라서 **5 Pack = exact minimum feasible**.
- 이전 preflight JSON의 6-Pack recommendation은 mean projection ×1.15 margin + 16.5 GiB/Pack heuristic에서 나온 보수값이므로 authoritative pack count에서 대체한다.

Local crop correction:
- unshifted 110 mm local crop preflight에서 mean coverage는 0.9730이지만 일부 Study의 min coverage가 0.4416까지 내려갔다.
- V4 full cache는 zero-padding을 기본으로 하지 않는다.
- requested local center가 FOV 밖으로 벗어나면 **110 mm crop 크기를 유지한 채 shift-to-fit**한다.
- source FOV 자체가 110 mm보다 작을 때만 available extent를 사용하고 crop_coverage metadata에 기록한다.
- Global은 physical aspect-ratio preserving letterbox 후 320 resize.

Authoritative full-cache notebooks:
- C_GEOM_MV320_CACHE_V4_P00.ipynb — 882 Studies
- C_GEOM_MV320_CACHE_V4_P01.ipynb — 882
- C_GEOM_MV320_CACHE_V4_P02.ipynb — 881
- C_GEOM_MV320_CACHE_V4_P03.ipynb — 881
- C_GEOM_MV320_CACHE_V4_P04.ipynb — 881
- CPU / Internet OFF / competition input only
- 각 Notebook은 8-Study actual-pixel sanity gate 후 full pack build, full readback QA, HDF5 SHA를 수행한다.
- **실행 순서: P00만 먼저 실행 → PASS 확인 후 P01~P04 병렬/순차 실행.**

---

# 2026-10-18 — C-CACHE-V3 Preflight V2 실패 / V3 QUOTAFIX

상태: **PREFLIGHT_V2_FAIL_QUOTA_ONLY / V3_READY**

실제 Kaggle V2 PATHFIX 결과:
- competition root PASS
- train_series DICOM root PASS
- 4,407 Study / 24,371 Series 확인 PASS
- 128/128 preflight Study geometry/header 처리 성공
- runtime 약 4.7 min
- 실패 지점: 일부 Study에서 `windows > 64` assertion

원인:
- Global/Local family target을 각각 32로 두면서도 모든 valid Series/View group에 1개 seed를 먼저 배정했다.
- family group 수가 32를 넘는 Study에서는 seed 단계만으로 family budget을 초과할 수 있었다.
- 과학적 데이터 설계 문제가 아니라 allocator hard-cap 누락 버그다.

V3 QUOTAFIX:
- Global≈32 / Local≈32 우선 유지
- family group 수가 budget보다 많으면 plane/view strata round-robin으로 coverage group 선택
- residual은 remaining capacity 기준 deterministic 배분
- `sum(quota)<=64`, `len(windows)<=64` hard assertion
- 뒤에서 임의 truncate 금지
- Branch-B full-cache에서 검증된 reader 패턴 반영: *.dcm only, specific_tags, threaded header read, IOP/IPP→Instance→filename fallback
- Required Input은 competition 하나만 유지

Notebook:
- `C_CACHE_V3_GEOMETRY_PREFLIGHT_V3_QUOTAFIX.ipynb`
- SHA256 `5035315bd91d7db98762d2bd7eaf2710987e2c67863fc6d37960e1ee1101daa8`
- STATIC_QA_PASS / KAGGLE_NOT_RUN

V1/V2 preflight notebook은 DO_NOT_RUN.

---

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

# 2026-10-18 — C-DESIGN-V4 AUTHORITATIVE / Segmentation-Free Geometry Multi-View

상태: **DESIGN_V4_FROZEN / V3_PREFLIGHT_READY / CACHE_NOT_RUN / TRAIN_NOT_RUN**

이 섹션이 Branch-C의 최신 authoritative 설계다. 아래의 C-DESIGN-V3/V2/V1 및 anatomy-segmentation 기반 cache notebook은 과거 설계 이력으로만 보존하며 실행하지 않는다.

## 1. 핵심 결정

Branch-C 기본 전처리에서 **무릎 anatomy segmentation network를 완전히 제거**한다.

이유:
- 외부 reference는 참고용이지 재현 자체가 목표가 아님.
- hidden test에서도 segmentation model을 매 Study 추가 실행하면 제출 전체 A+B+C inference latency가 증가.
- 과거 사용자 실험에서 anatomy segmentation preprocessing이 매우 느렸음.
- 공개 참고자료 중 CoAtNet/Raptor 및 compact v1/v2/v3 계열은 segmentation 없이도 physical crop / fixed local prior / target attention으로 동작.
- C의 핵심 차별점은 segmentation이 아니라 **Global + geometry-local multi-view + target-specific spatial attention + Window MIL**이다.

Required Input:
- **RSNA Knee Abnormality Detection competition only**
- 외부 anatomy.pt / cloud_code / reference manifest는 Required Input에서 제거.

## 2. A/B/C 역할 분리

### Branch-A — DINO Search / Selector Expert
- Native224 / 130mm 중심 crop 기반.
- Stage1에서 Study당 18 Window.
- Stage2에서 전체 valid MRI Window를 feature화.
- S8C가 target-specific Window/Series importance를 계산.
- Top18 선택 후 S10/S11이 재판독.
- S11 Multi-View는 **선택된 동일 Top18 center를 110/130/160mm로 확대·축소**.
- 담당: **MRI 전체에서 어디가 중요한지 찾고 집중 재판독**.

### Branch-B — CoAtNet Wide/Dense Coverage Expert
- fixed Wide96 anatomical slot.
- SAG fluid/non-fluid, COR fluid/non-fluid, AXIAL을 명시적으로 확보.
- Native384, 약 140mm center crop.
- Stack 6~94%를 넓게 sampling.
- target-specific Window Attention.
- 담당: **미리 많이 버리지 않고 MRI 전체를 촘촘히 읽어 miss를 줄임**.

### Branch-C — ConvNeXt Geometry Multi-View Spatial Expert
- fixed Wide96이나 S8C Top18을 재사용하지 않음.
- 전체 Series에서 Global + geometry-local view 후보를 생성.
- Study당 최대 64 overlapping 2.5D Window를 coverage-first로 선택.
- 같은 slice 위치라도 Global/Center/Anterior/Posterior/Bilateral 등 **위치가 다른 관찰창**을 만들 수 있음.
- ConvNeXt feature map에서 12 target spatial attention 후 target-specific Window MIL.
- 담당: **각 Window 내부의 어느 해부학적 위치를 봐야 하는지 학습**.

요약:
- A = WHERE among slices?
- B = SEE EVERYTHING densely.
- C = WHERE inside the image / which physical view?

## 3. C-DATA-V4 파이프라인

Raw DICOM
→ DICOM header/geometry parse
→ IOP/IPP physical ordering
→ InstanceNumber / filename fallback
→ plane inference from IOP normal
→ PixelSpacing 기반 physical geometry
→ thin-stack physical slab
→ Global + fixed physical-offset local views
→ 320×320 uint8 rendered rows
→ unique rendered row storage
→ 64 overlapping 2.5D windows via index
→ train RandomCrop 320→288 / val center crop
→ ConvNeXt-Small
→ target-specific Spatial Attention
→ target-specific Window MIL
→ 12 targets

## 4. Segmentation-Free Geometry Views

Local center는 모델이 찾는 것이 아니라 **DICOM patient physical coordinate**를 이용한다.

DICOM patient axes:
- X = L/R
- Y = P/A
- Z = F/H

Plane별 기본 view:

### Sagittal
- GLOBAL
- CENTER local
- ANTERIOR local: patient anterior 방향 physical offset
- POSTERIOR local: patient posterior 방향 physical offset

### Coronal
- GLOBAL
- bilateral local pair: patient L/R 방향 ± physical offset
- laterality가 확실할 때만 medial/lateral 의미를 부여.
- laterality가 불확실하면 BILAT_A/B처럼 symmetric pair로만 사용하고 잘못된 hard semantic을 주지 않음.

### Axial
- GLOBAL
- CENTER local
- ANTERIOR local
- POSTERIOR local

초기 physical constants:
- local FOV: **110 mm**
- anterior/posterior offset: **30 mm**
- coronal bilateral offset: **±30 mm**

이 수치는 C-CACHE-V3 preflight에서 crop coverage를 보고 조정 가능하지만, B의 140mm 단일 center crop 구조를 복제하지 않는다.

## 5. Thin-stack

- median physical spacing < 1.75 mm인 thin stack은 약 3.5 mm slab로 묶음.
- 원본 slice를 단순 stride로 버리는 방식이 아니라 slab averaging.
- 목적: 0.4~1.5mm 3D acquisition의 near-duplicate depth가 64-window budget을 과점하지 않도록 physical depth를 정규화.

## 6. 64-window selection

- 최대 64 Window / Study.
- Window = [prev, center, next].
- overlap 유지.
- stride 3으로 바꿔 window를 줄이지 않음.
- Global family 약 32 / Local family 약 32를 초기 목표.
- 모든 valid Series/View group 최소 coverage 우선.
- 남는 quota는 group capacity에 따라 deterministic 배분.
- group 내 center는 physical-order 전체 범위에 균등 배치.
- 총 candidate가 64 미만이면 valid_mask 사용.

C는:
- A의 Top18 selector 결과를 사용하지 않음.
- B의 fixed 96-slot layout을 사용하지 않음.

## 7. Cache V3 저장 구조

성능 입력과 저장 중복을 분리한다.

학습 Window:
- [20,21,22]
- [21,22,23]
- [22,23,24]
그대로 유지.

저장:
- unique rendered rows를 한 번만 보관.
- window_index가 각 3-channel Window를 재구성.

예:
- pixels = slice20,21,22,23,24
- window_index = [0,1,2], [1,2,3], [2,3,4]

즉 **중복 Window를 제거하지 않고 중복 파일 저장만 제거**한다.

예정 schema:
- pixels: [N_unique,320,320] uint8
- pixel_meta: row-level metadata
- window_index: [N_window,3] int32
- window_meta: [N_window,12] float32
- study_ptr / study_uid / valid_mask

## 8. C-CACHE-V3 Geometry Preflight

Notebook:
`C_CACHE_V3_GEOMETRY_PREFLIGHT.ipynb`

SHA256:
`fda85064c4ce09bdd7501b985055ef90ba6ee39a54be43ea967e810a76e2e3ac`

Status:
- STATIC_QA_PASS
- KAGGLE_NOT_RUN

Required Input:
- RSNA competition only.

Preflight:
- 128 Study deterministic spread sample.
- DICOM IOP/IPP/PixelSpacing만 사용.
- segmentation/network preprocessing 없음.
- Study별 Series/plane/slab/view/window 수 측정.
- Global vs Local window count 측정.
- crop coverage / padding fraction 측정.
- unique rendered rows vs duplicated triplet rows 측정.
- 전체 4,407 Study projected cache GiB 계산.
- 15% safety margin.
- 16.5 GiB/Pack 목표로 recommended Pack count 출력.

Outputs:
- c_cache_v3_preflight_study_metrics.csv
- c_cache_v3_capacity_plan.json
- c_cache_v3_preflight_receipt.json

이 preflight 결과 전에는 2/3/4/5 Pack을 임의 확정하지 않는다.

## 9. C-BASE 모델 구조

Backbone:
- ConvNeXt-Small, ImageNet pretrained, full fine-tuning.
- exact timm ID / offline checkpoint / SHA는 training notebook 전에 고정.

입력:
- 2.5D [prev, center, next].
- cache 320, train 288 random crop, val/test 288 center crop.

Spatial stage:
- 마지막 ConvNeXt spatial feature map을 즉시 GAP하지 않음.
- 12 learned target queries.
- target별 spatial softmax.
- 12 target-specific window feature 생성.

Window MIL stage:
- 최대 64 windows.
- target-specific Window attention.
- metadata gate: plane, view, relative position, spacing, sequence characteristics 등.
- 최종 12 logits.

## 10. Base supervision / Fold

기본:
- V4 Routed Broad 4,349 report Studies.
- Gold58 frozen 29/29 split.
- Fold0 train = V4 4,349 + opposite Gold29 / val own Gold29.
- Fold1 동일 반대 구조.
- Fold0 GPU0 / Fold1 GPU1 independent.
- LABEL-V6 soft는 Base 기본값 아님.

## 11. 후속 실험

Base 이후에만 one-variable experiments:
1. C-OA-01 — high-confidence OA extent auxiliary.
2. C-MIRROR-01 — anatomical mirror inference TTA.
3. resolution 288→320→384.
4. local FOV/offset 조정.
5. window count/density.
6. A+B+C target-wise ensemble.

## 12. 폐기 상태

DO NOT RUN:
- C_ANATOMY_CACHE320_V1_P00~P05
- C_CACHE_V2_SIZE_PREFLIGHT
- anatomy.pt / SKM-TEA segmentation 기반 C-DESIGN-V3 cache path

과거 문서는 설계 변경 이유 추적용 archive로만 유지.

---

# 2026-10-18 — C-CACHE-V2 저장구조 전환 / V1 6-Pack 실행 금지

상태: **C-CACHE-V2_PREFLIGHT_READY / V1_SUPERSEDED**

사용자와 검토 후 C cache 저장구조를 수정한다.

- 학습/추론 Window 선택은 변경하지 않는다.
- 기존 C-BASE 64-window contract는 그대로 유지한다.
- `[20,21,22] / [21,22,23] / [22,23,24]` 같은 overlapping 2.5D Window를 그대로 사용한다.
- 제거하는 것은 **디스크에 반복 저장되는 동일 rendered slice의 복사본뿐**이다.
- V2는 `unique_pixels [N_unique,320,320]` + `window_index [N_window,3]`로 exact reconstruction한다.
- Preflight에서 old duplicated-triplet tensor와 V2 reconstruction을 `np.array_equal`로 전 Study 검증한다.
- 따라서 stride를 3으로 바꾸거나 Window 수를 줄이는 방식은 사용하지 않는다.

공개 참고자료 근거:
- public `px_cache.py`는 `one row per (series, view, slice)`의 per-slice 저장 방식을 사용한다.
- 따라서 V2는 reference의 저장 철학과도 더 가깝다.
- 단, 우리 C는 전체 rendered rows를 모두 보관하지 않고 **선택된 C-BASE 64 windows를 재구성하는 데 실제 필요한 unique rows만 저장**하는 것을 목표로 한다.
- 이 선택은 C-BASE 입력을 바꾸지 않지만, 향후 64보다 더 dense한 window 실험은 별도 cache가 필요할 수 있다.

### Pack 수 결정 방식

기존 V1의 6-Pack은 `64×3×320×320` triplet을 매 Study 고정 저장하는 hard upper-bound에서 정한 값이므로 **실행하지 않는다**.

새 V2:
1. 128 Study를 전체 UID 구간에서 deterministic하게 샘플.
2. 실제 anatomy/local preprocessing과 64-window selector 실행.
3. Study별 unique rendered rows와 실제 V2 payload MiB 측정.
4. old triplet tensor와 V2 reconstruction bit-identical 검증.
5. 전체 4,407 Study projected GiB 계산.
6. projection에 15% margin 적용.
7. Kaggle output 안전 목표 `16.5 GiB / Pack` 기준 최소 Pack 수 추천.
8. 이 결과를 확인한 후에만 full-cache Pack Notebook을 생성한다.

Preflight Notebook:
- `C_CACHE_V2_SIZE_PREFLIGHT.ipynb`
- SHA256: `b87c93434caca77bfa8d0c7413dce8f864a0bb769d8133f41b30b7d18f5eb039`
- Static QA: PASS
- Kaggle execution: NOT_RUN

기존 `C_ANATOMY_CACHE320_V1_P00~P05.ipynb`는 **SUPERSEDED / DO NOT RUN**.

---

# Branch-C ConvNeXt Anatomy Expert — C-DESIGN-V3

최종 갱신: 2026-10-18  
상태: DESIGN_V3_FROZEN / CACHE_NOTEBOOK_READY / CACHE_NOT_RUN / TRAIN_NOT_RUN

이 문서는 Branch-C의 최신 authoritative 설계다. 아래 내용은 과거 C-DESIGN-V1/V2 중 충돌하는 가정을 대체한다.

## 1. Branch-C의 역할

최종 큰 앙상블은 서로 다른 방식으로 같은 Hidden MRI를 읽는 3개 독립 전문가를 목표로 한다.

- Branch-A — DINO Core: 전체 MRI representation, MIL/selector, Top-K 재판독에 강한 범용 판단축.
- Branch-B — CoAtNet Wide-MRI Expert: Wide96, 고해상도, dense multi-slice coverage에 강한 정밀 판독축.
- Branch-C — ConvNeXt Anatomy Expert: Global + anatomy-local ROI, window 내부 spatial localization, Study 내부 window MIL을 동시에 학습하는 해부학 위치 전문 판단축.

C는 A의 S8C Top18을 입력으로 사용하지 않고, B의 fixed Wide96 stack도 재사용하지 않는다. 목적은 같은 예측을 반복하는 모델 수 증가가 아니라 error diversity를 확보하는 것이다.

## 2. 중요한 과거 실험 해석 정정

Strict/high-confidence 라벨에서 mask=0이 많아져 전체 성능이 낮아졌던 것은 Branch-C 실험이 아니다.

그 결과는 Branch-A DINO 초기 Stage1 representation 학습에서 관측된 것이다. Branch-C는 2026-10-18 현재 모델, 학습 결과, 전용 cache가 아직 없었다.

따라서 이 결과는 C에서 다음 교훈으로만 사용한다.

- C Base representation은 가능한 많은 Study를 이용하는 V4 Routed Broad를 우선한다.
- 고신뢰/extent 라벨은 전체 Base dataset을 잘라내는 용도로 쓰지 않는다.
- 향후 OA Extent auxiliary head에서는 extent label이 없는 항목의 auxiliary loss만 mask한다.

## 3. C-BASE-01 전체 파이프라인

Raw DICOM
→ public pinned native preprocessing
→ DICOM geometry / physical ordering
→ thin-stack physical slab
→ anatomy anchor
→ Global + Anatomy Local views
→ 320×320 uint8 cache
→ Study당 최대 64개의 2.5D window
→ ConvNeXt-Small full fine-tuning
→ target-specific spatial attention
→ target-specific Window MIL
→ 12 target prediction

## 4. DICOM / geometry contract

Series 정렬과 preprocessing은 가능한 한 공개 고득점 reference와 동일한 frozen mainline path를 사용한다.

공개 reference code dataset:
- heliosli/rsna-orthofoundation-fold0-epoch7-20261004

현재 cache Notebook은 이 dataset의 mainline training code를 사용하고 다음 public source SHA를 검사한다.

- native_cache.py: c53ce8985406b3b918d9e821d43518479e89d9f946daebd817f378e3949718b9
- native_data.py: f59afe205c8e193369fa3ccd22edcce8df3b293205fc48ddb1dd45169ee43b36
- input_provenance.py: b3a22500c7f976f6ee040239ada5cacecf2326861cb49af1c7d8cfdeeb55fcda
- intensity_mapping.py: 19be2d8cbd6f8971c1288d7512a8cca41d143470c2ba6e9b9096fde035fa9d41
- coronal_views.py: 841f216d2682ae2c0f8afd82fc902b9fa74924d7145b952069dea8b0bbd03c40
- exact_duplicates.py: 51b38db21ce9c5fe2b6278a835983414756b61ac6af81aba380b44b41b075897
- dicom_geometry.py: 12aa501f9704aef15b7a3bbd560951acb6d95b89b7de0141d6cf89fc3f051ab1
- common.py: 8283fa1f8e7ef8cfacbba52df1715636be3c9ad688e39912814e7d5bcf57105f

Hidden inference에서도 동일 preprocessing library를 재사용한다. 학습 cache와 Hidden inference가 서로 다른 임의 crop/sort/normalization path를 갖지 않게 한다.

## 5. Thin-stack physical depth

Reference와 동일한 기본 물리 규칙을 채택한다.

- THIN_MM = 1.75 mm
- SLAB_MM = 3.5 mm
- median physical slice spacing이 0 < spacing < 1.75 mm이면 thin 3D stack으로 판단.
- group_size = round(3.5 / spacing)
- 인접 slice를 평균해 약 3.5 mm slab로 변환.
- 마지막 remainder가 약 half-group 이상이면 마지막 slab로 유지.

목적은 0.4~1.5 mm thin stack에서 거의 같은 위치의 slice가 window budget을 과점하는 것을 막고 2D acquisition과 비슷한 physical depth statistics를 만드는 것이다.

## 6. Anatomy Anchor

C의 local view는 단순 field-center crop을 핵심 방식으로 사용하지 않는다.

Primary:
- 공개 reference의 SKM-TEA 계열 anatomy segmenter로 joint/patella anchor 추정.
- 여러 sagittal candidate를 world LPS에서 합의.
- DICOM geometry를 통해 각 Series pixel grid로 projection.

Fallback:
1. segmentation-derived joint anchor
2. orthogonal slab geometry prior
3. local anchor가 없는 Series는 local view를 학습 입력에서 제외하고 Full FOV만 유지

중요:
- local anchor가 없을 때 center-local을 정상 anatomy local처럼 조용히 사용하는 것은 금지.
- no-geometry/no-anchor 상태는 study_audit에 기록한다.

Anatomy asset 검증:
- code/anatomy dataset: heliosli/rsna-orthofoundation-fold0-epoch7-20261004
- pinning manifest: heliosli/rsna-knee-compact-r7cnxfsss/manifest.json
- Notebook은 anatomy.pt SHA256이 manifest의 anchor_weights_sha256와 정확히 일치할 때만 진행한다.
- reference source knee_anchor_bank_v2.py SHA256:
  e564807a129dfcd3c984348917436ee6083066a4d685340587ebd1d3ea14f309

## 7. View Set — v4

C Base는 처음부터 Global context와 anatomy-local context를 동시에 보존한다.

Sagittal:
- view 0: Full FOV
- view 1: Joint local 100 mm
- view 4: PF local 100 mm
- view 5: Posterior local 100 mm

Coronal:
- view 0: Full FOV
- view 2: Medial local 100 mm
- view 3: Lateral local 100 mm

Axial:
- view 0: Full FOV
- view 1: Joint local 100 mm
- view 4: PF local 100 mm
- view 5: Posterior local 100 mm

PF/posterior/coronal offset semantics는 public px_cache v4 reference를 따른다. 특정 target이 특정 view만 보도록 hard routing하지 않는다. 최종 중요도는 target-specific attention이 학습한다.

Reference px_cache.py SHA256:
b13e38a7ad3bd496f8027e02209653e224b0926db4f0853eeb0d076a2d6e2632

## 8. Cache V1 — 저장 형식

Experiment family:
C-ANATOMY-CACHE320-V1

전체 4,407 train Study를 cache한다. 이유:
- Report 4,349 Study는 V4 Broad Base train에 사용.
- Gold58은 Fold마다 반대쪽 29명을 train에 포함하고 held-out 29명을 validation에 사용하므로 cache에는 4,407 전부 필요.

6 Packs:
- deterministic sorted StudyInstanceUID를 6등분.
- Pack당 약 734~735 Study.
- 최대 logical pixel bytes:
  Study × 64 windows × 3 slices × 320 × 320 × uint8
  ≈ Pack당 13.5 GiB.
- Kaggle /kaggle/working 20GB를 넘지 않도록 6 Pack으로 고정.

HDF5 schema:
- windows: [N_study, 64, 3, 320, 320] uint8
- window_meta: [N_study, 64, 12] float32
- valid_mask: [N_study, 64] uint8
- study_uid: [N_study] UTF-8
- anchor_method: [N_study] UTF-8

meta columns:
- series_idx
- slot
- plane
- view_id
- rel_pos
- log_spacing
- extent_130
- fluid
- fatsat
- slice_order
- n_slices
- real_series_idx

각 Pack은 .partial HDF5에 먼저 기록한다. Study failure가 1건이라도 있으면 release하지 않는다. 전체 QA PASS 후에만 final .h5로 원자적 rename한다.

## 9. Study당 64-window selection

C는 B의 96-slot 고정 구조를 복제하지 않는다.

V1 budget:
- Global target ≈ 32
- Anatomy Local target ≈ 32
- 최대 64 windows/Study

Selection 순서:
1. 모든 valid Series/View group의 최소 coverage.
2. Global family와 Local family 각각 32개를 목표.
3. 남은 quota는 available center 수에 비례해 분배.
4. 한 group 안에서는 physical-order candidate center를 균등하게 선택.
5. 전체 candidate가 64 미만이면 valid_mask로 padding.
6. center마다 prev/center/next 3개를 2.5D window로 저장.
7. local anchor가 projection되지 않은 Series의 local groups는 selection에서 제외.

이 구조는 cache 크기를 bounded하게 만들고 Hidden inference에서 동일한 fixed 64-window contract를 재현하기 쉽게 한다.

## 10. Pixel preprocessing

Public reference mainline을 그대로 기반으로:
- DICOM decode
- geometry/canonical side handling
- Series-level display/intensity mapping
- v4 view crop
- cv2 INTER_AREA resize
- uint8 0~255 output

Cache resolution:
- 320×320

Training:
- 320 → RandomCrop 288

Validation / Hidden inference:
- 320 → deterministic CenterCrop 288

C Base에서 generic train-time horizontal flip은 사용하지 않는다.

## 11. C-BASE-01 모델 구조

Backbone:
- timm ConvNeXt-Small
- ImageNet pretrained 계열
- full fine-tuning
- exact timm model name / checkpoint / SHA / offline Kaggle path는 training Notebook 생성 전에 별도 고정

입력:
- [B_window, 3, 288, 288]
- channel = prev / center / next MRI slice

Stage A — target-specific spatial attention:
- ConvNeXt 최종 spatial feature map을 Global Average Pooling으로 즉시 소실하지 않는다.
- feature map key/value projection.
- 12 learned target queries.
- target별 spatial softmax.
- window마다 12개의 target-specific pooled feature 생성.

Stage B — target-specific Window MIL:
- Study당 최대 64 windows.
- 각 target마다 별도 Window attention.
- attention gate에는 image feature + metadata embedding 사용.
- plane, view type, relative slice position, log spacing, fluid-sensitive, fat-suppression metadata 활용.
- V1에서는 metadata를 최종 classifier feature에 직접 concatenate하지 않고 attention 선택 보조로 우선 사용.

최종:
- 12 target Study feature
- 12 logits

## 12. Base supervision

C-BASE-01은 V4 Routed Broad를 기본 supervision으로 사용한다.

- Report Study 4,349: V4 Routed Broad
- Gold58: 29/29 frozen split 사용
- Fold0: V4 4,349 + Gold Fold1 29 train / Gold Fold0 29 val
- Fold1: V4 4,349 + Gold Fold0 29 train / Gold Fold1 29 val
- GPU0 → Fold0, GPU1 → Fold1 independent
- DDP=false

이 구조는 held-out Gold leakage를 막으면서 두 Fold 모두 full pseudo-labeled universe를 이용한다.

LABEL-V6 soft는 C Base 기본값으로 사용하지 않는다.

## 13. Loss / imbalance

Base loss:
- masked confidence-weighted soft BCE

V4 pseudo sample weight 시작값:
- 0.25 + 0.75 × confidence

Gold:
- weight 1.0

Target class balance 시작 후보:
- P_t = Σ(w × y)
- N_t = Σ(w × (1-y))
- ratio = (N_t/P_t)^0.70
- clip [0.5, 2.5]

Rare-positive Study sampling 시작 후보:
- MCL 3.0×
- Fracture 2.5×
- Contusion 2.0×
- Baker's 1.5×
- PF OA 1.5×
- other 1.0×
- 한 Study가 여러 rare target에 해당하면 multiplier를 곱하지 않고 max만 사용.

이 수치는 training preflight에서 실제 V4 label distribution을 재계산하고 manifest에 기록한 뒤 고정한다.

## 14. Augmentation

Base geometry:
- RandomCrop 320→288
- Rotation ±10°
- Scale 0.90~1.10

Intensity:
- Gamma 0.80~1.25
- Gain/Contrast 0.90~1.10

Resolution robustness:
- p=0.25
- downsample factor 1.25~2.0 후 원래 크기로 복원

Base 금지:
- MixUp
- CutMix
- Random Erasing
- arbitrary strong blur
- generic horizontal flip

Anatomical mirror는 별도 inference TTA 실험으로 분리한다.

## 15. Training hyperparameter initial contract

초기값:
- Epoch: 16 fixed target
- Early stopping: 없음
- Backbone LR: 1.0e-4
- Spatial/MIL/Head LR: 1.0e-3
- Optimizer: AdamW
- Weight decay: 0.05
- Scheduler: cosine
- Warmup: 5%
- Gradient clip: 5.0
- Precision: FP16
- Seed: 42

단, 위 값은 GPU preflight runtime gate를 통과한 뒤 본학습에 사용한다.

Checkpoint:
- Fold별 best.pt + last.pt 둘 다 보존.
- best는 own Gold29 Macro AUROC 우선.
- A 계보에서 validation best와 LB best가 달랐던 경험 때문에 last도 삭제하지 않는다.
- per-target checkpoint cherry-pick은 하지 않는다.

## 16. GPU resource policy

과거 사용자 실측:
- Batch 124+ 가능 경험 및 VRAM 여유 기록이 존재.
- 단, 해당 단위/모델/해상도가 C와 동일하다고 가정하지 않는다.
- 반대로 OOM을 추측해 작은 microbatch를 임의 고정하지 않는다.

C training preflight:
- Window microbatch 후보: 18 / 32 / 64 / 96 / 124 / 128+
- Physical Study Batch 후보: 1 / 2 / 4 / 8+
- 실제 HDF5, Full Forward + Backward + AdamW Step, validation/save 비용 포함.
- 128~256 Study 이상으로 throughput 측정.
- 기록: peak allocated/reserved, Windows/s, Studies/s, I/O, optimizer-step time.
- 한 16ep Fold-pair 목표 ≤4h.
- >4h이면 batch/prefetch/checkpointing/I/O 재최적화.
- ≥8h 예상 신규 본학습 시작 금지.

## 17. OA Extent 후속 실험

C Base와 분리한다.

C-OA-01:
- C-BASE checkpoint에서 추가 FT.
- Main 12-target loss는 V4 Broad를 계속 사용.
- High-confidence OA extent label이 있는 항목에만 auxiliary extent loss 계산.
- extent label이 없는 항목은 extent loss만 mask.
- Study 전체 또는 다른 12-target supervision을 버리지 않는다.

Head:
- Medial OA extent
- Lateral OA extent
- PF OA extent

실제 extent label schema를 확인한 뒤 ordinal / regression / binary auxiliary 중 하나를 고정한다.

C-OA가 전체 Macro를 약간 낮춰도 OA 3 target을 유의미하게 높이면 OA specialist ensemble component로 보존한다.

## 18. Mirror TTA 후속 실험

C-MIRROR-01:
- Base 학습 후 inference-only.
- Original + anatomical mirror.
- generic image flip이 아니라 plane/canonical side semantics를 따른다.
- Medial/Lateral Meniscus 및 Medial/Lateral OA는 semantic swap-back.
- MCL plain-only 여부는 Gold58에서 별도 비교.
- probability 평균 vs logit 평균은 DEV/LB로 한 번 선택 후 고정.

## 19. Resolution 후속 실험

C-BASE-01 320-cache / 288-input 구조가 유효한지 먼저 확인한다.
그 다음 필요 시 384 계열을 별도 controlled experiment로 진행한다.

처음부터 384로 GPU 비용을 크게 쓰지 않는다.

## 20. Evaluation

필수 순서:
1. Gold58 pooled OOF Macro AUROC
2. 12 target AUROC
3. Fold0/Fold1 gap
4. target-specific spatial attention sanity
5. target별 plane/view/window usage
6. C standalone Public LB
7. C best vs last 비교
8. A↔C, B↔C target-wise rank correlation
9. A+C
10. A+B+C

C의 성공 조건은 standalone 절대점수만이 아니다. A/B가 틀리는 Study/target에서 다른 오류 패턴을 만들어 최종 ensemble을 올리는 것이 핵심이다.

## 21. Final ensemble 방향

모든 Branch는 동일 Hidden DICOM을 자기 preprocessing으로 별도 처리한 뒤 12개 Study-level prediction만 합친다.

우선 비교:
- probability blend
- per-target percentile-rank blend

초기 heuristic 예시:
- A 0.50 / B 0.30 / C 0.20

최종 비율은 고정값이 아니다.
Standalone LB, Gold OOF, target-wise complementarity/correlation을 보고 global 또는 target-wise fixed weight로 결정한다.

## 22. Hidden inference contract

Hidden test에서는 train cache를 사용할 수 없으므로 Raw DICOM에서 on-the-fly로 동일 preprocessing을 재현한다.

Hidden Raw DICOM
→ native prepare
→ geometry
→ thin slab
→ anatomy anchor
→ v4 Global/Local render 320
→ 동일 64-window selector
→ center crop 288
→ Fold0/Fold1 prediction mean
→ 12 outputs

공통 submission robustness:
- 실제 MRI 기반 prediction만 허용.
- Study-level neutral 0.5 placeholder 금지.
- individual slice/Series rescue는 허용하되 audit 기록.
- 실제 image prediction branch가 0개면 intentional fail-fast.

## 23. Cache Notebook release

2026-10-18 생성:
- C_ANATOMY_CACHE320_V1_P00.ipynb
- C_ANATOMY_CACHE320_V1_P01.ipynb
- C_ANATOMY_CACHE320_V1_P02.ipynb
- C_ANATOMY_CACHE320_V1_P03.ipynb
- C_ANATOMY_CACHE320_V1_P04.ipynb
- C_ANATOMY_CACHE320_V1_P05.ipynb

각 Notebook:
- clean session Save & Run All
- Internet Off
- T4 x2
- Pack ID 수정 불필요
- source / anatomy hash gate
- partial HDF5 release 금지
- final manifest / study audit / file SHA 생성

Notebook은 현재 정적 JSON 및 Python syntax 검증 PASS 상태이며 Kaggle 실제 실행은 아직 NOT_RUN이다.

## 24. 실행 순서

1. Pack00 Save & Run All.
2. 마지막 receipt + study_audit + HDF5 size/runtime 확인.
3. Pack00에서 오류가 0이고 anatomy/local ratio가 정상인지 확인.
4. P01~P05 병렬/순차 생성.
5. 6 Pack cache integrity 통합 검증.
6. exact ConvNeXt-Small pretrained artifact 고정.
7. C training GPU resource preflight.
8. C-BASE-01 2F.
9. C standalone LB.
10. C-OA-01.
11. C-MIRROR-01.
12. 필요 시 resolution/window density.
13. A+B+C ensemble.

## 25. 변경 이력

- C-DESIGN-V1: single full-data model, Gold58 train 제외, older soft-label 가정이 포함되어 현재 기준과 충돌.
- C-DESIGN-V2: public ConvNeXt reference audit 및 2-Fold/V4 Broad/anatomy gate 재검토 단계.
- C-DESIGN-V3: 2026-10-18 최신 확정. V4 Broad 2-Fold Base, all-4407 cache, v4 anatomy views, fixed 64-window cache, OA extent auxiliary 분리, best+last 보존, 6-Pack cache release contract로 갱신.