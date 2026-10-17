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
