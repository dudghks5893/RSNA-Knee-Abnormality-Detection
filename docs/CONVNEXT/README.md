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
