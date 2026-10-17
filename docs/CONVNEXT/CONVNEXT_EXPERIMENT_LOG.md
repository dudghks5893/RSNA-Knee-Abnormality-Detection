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

## 2026-10-18 — C-CACHE-V3 Geometry Preflight V3 PASS / V4 full cache ready

실제 Kaggle 결과:
- status PASS
- elapsed 1.77 min
- 128/128 Study, errors 0
- every Study = 64 windows
- Global32 / Local32
- mean groups 20.96, max 49
- mean unique rows 191.211 / dense 192
- dedup ratio 0.9959
- mean payload 18.6766 MiB/Study
- naive projected full cache mean 80.379 GiB
- IOP/IPP ordering on all 734 sampled Series

결정:
1. unique-row/index storage는 절감이 거의 없어 폐기.
2. dense 64×3×320×320 uint8 cache로 단순화.
3. exact 19 GB output-cap 계산으로 5-Pack이 최소 feasible.
4. local 110 mm crop은 shift-to-fit; FOV<110 mm일 때만 available extent.
5. V4 5-Pack production notebooks static QA PASS, Kaggle NOT_RUN.

V3 preflight artifacts:
- metrics SHA 06827c88dc9219367f4f9ca3b51e3958478d0c09f7e7c91fd7126fc003c4eb6b
- capacity plan SHA e62cfed65b153b7ad29a90bb57a1d7c6a73699f2ccd7d80ae7e675125e595265
- receipt SHA 80b6b31385408aece46aff00128fa234940888c618adbf81fc9041f33ccc7903

V4 Notebook SHA:
- P00 bc9c96f9bcd50bc0d044e7dee704d968a06021349a4a241b6f1f518f9241c23c
- P01 301c219edddbc45531f58757ef9bef4ced38ec219e37568b0d1c88feb61c66fb
- P02 1961f9f57dc85fb4c9c12beee1cbcb655cccdfadeb164b8478bc1d38eee75382
- P03 588c1d43b602a2e5937a0648034e133cdcd6d14e62183d56437a27e0a4765a8f
- P04 b346aab589f3cd9e1002c4b4fbad296f5c8d8080c09f23e85c231a491623e1ea


## 2026-10-18 — C-CACHE-V3 V2 PATHFIX 실제 실행 실패, V3 QUOTAFIX 준비

V2 실제 실행은 128/128 Study를 약 4.7분에 geometry/header audit 완료했으나 마지막 `windows<=64` gate에서 FAIL.
원인은 family별 모든 group 1-window seed가 32-window family budget보다 커질 수 있었던 allocator 버그.
DICOM path/geometry failure는 0건이므로 segmentation-free design 자체는 유지한다.

V3:
- plane/view strata round-robin seed
- total 64 hard cap
- deterministic capacity refill
- B cache에서 검증된 threaded specific-tag DICOM header reader 패턴 반영
- Notebook SHA256: `5035315bd91d7db98762d2bd7eaf2710987e2c67863fc6d37960e1ee1101daa8`
- 상태: STATIC_QA_PASS / KAGGLE_NOT_RUN

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

# Branch-C ConvNeXt — Cumulative Experiment Log

## 2026-10-18 — C-DESIGN-V4 / Segmentation-Free Geometry Multi-View 전환

상태:
- DESIGN_V4_FROZEN
- C-CACHE-V3 PREFLIGHT READY
- CACHE_NOT_RUN / TRAIN_NOT_RUN

핵심 변경:
- anatomy segmentation network 제거.
- 외부 heliosli anatomy/code/manifest Dataset을 Required Input에서 제거.
- RSNA competition DICOM만으로 C preprocessing 구성.
- Global + CENTER + ANTERIOR/POSTERIOR + CORONAL BILATERAL physical views.
- local crop는 DICOM IOP/PixelSpacing 기반 physical offset.
- 64 overlapping 2.5D Window 유지.
- 저장은 unique rendered rows + window_index.
- B의 fixed Wide96/140mm center crop과 A의 S8C Top18을 사용하지 않음.
- C의 차별화는 target-specific spatial attention + geometry multi-view + Window MIL.

새 Preflight:
- Notebook: `C_CACHE_V3_GEOMETRY_PREFLIGHT.ipynb`
- SHA256: `fda85064c4ce09bdd7501b985055ef90ba6ee39a54be43ea967e810a76e2e3ac`
- Input: RSNA Knee competition only
- 128 Study deterministic spread sample
- Static QA PASS
- Kaggle NOT_RUN
- 출력: crop coverage, Global/Local distribution, unique-row storage ratio, projected total GiB, recommended Pack count

폐기:
- C_ANATOMY_CACHE320_V1_P00~P05
- C_CACHE_V2_SIZE_PREFLIGHT
- segmentation-based C-DESIGN-V3 cache path
모두 DO_NOT_RUN.

Immediate next:
- C_CACHE_V3_GEOMETRY_PREFLIGHT Save & Run All
- capacity_plan + receipt 확인
- 그 결과로 full-cache Pack 수 확정
- full-cache Pack Notebook 생성



## 2026-10-18 — C-CACHE-V2 preflight로 전환

**V1 6-Pack Notebook은 SUPERSEDED / DO NOT RUN.**

이유:
- V1은 Study당 64개 2.5D triplet을 그대로 저장해 overlapping Window 사이의 동일 slice가 디스크에 반복 저장될 수 있었다.
- 성능에 영향을 주는 Window 중복을 제거하는 것이 아니라, 저장 중복만 제거하기로 결정했다.

V2 contract:
- C-BASE의 64 Window 선택은 완전히 동일.
- unique rendered pixels를 한 번 저장.
- 각 Window는 3개의 pixel-row index로 재구성.
- old triplet representation과 `np.array_equal` bit-parity를 preflight에서 검사.
- stride/window sampling 변경 없음.

새 Notebook:
- `C_CACHE_V2_SIZE_PREFLIGHT.ipynb`
- SHA256 `b87c93434caca77bfa8d0c7413dce8f864a0bb769d8133f41b30b7d18f5eb039`
- 128 Study deterministic spread sample
- Output: study metrics / capacity plan / receipt
- safe pack target: 16.5 GiB
- full 4,407 projected size에 15% margin 적용 후 권장 Pack 수 산출
- STATIC_QA_PASS / KAGGLE_NOT_RUN

Immediate next:
1. V2 preflight Save & Run All.
2. `c_cache_v2_capacity_plan.json` 확인.
3. 추천 Pack 수로 full-cache Notebook 생성.
4. Pack00 실제 build QA 후 나머지 Pack 실행.



최종 갱신: 2026-10-18

계획은 [CONVNEXT_BRANCH_PLAN.md](CONVNEXT_BRANCH_PLAN.md), 실제 실행/Notebook 상태는 이 문서에 누적한다.

## Current Status

- Branch: C — ConvNeXt Anatomy Expert
- Design: C-DESIGN-V3 FROZEN
- Cache Notebook: READY / STATIC_QA_PASS
- Cache Execution: NOT_RUN
- Training: NOT_RUN
- Public LB: 없음

## 2026-10-18 — C-DESIGN-V3 확정

정정:
- Strict mask로 전체 성능이 낮아진 기존 실험은 Branch-C가 아니라 Branch-A DINO 초기 Stage1 실험이었다.
- C는 아직 모델/전용 데이터/학습 결과가 없었다.
- 이 결과는 C Base에서 coverage를 우선해야 한다는 참고 근거로만 사용한다.

C Base:
- V4 Routed Broad
- 2-Fold
- Report 4,349 + 반대 Gold29 train / own Gold29 val
- ConvNeXt-Small full FT
- 2.5D
- 320 cache → 288 train/val input
- v4 Global + anatomy-local
- 64 windows/Study
- target-specific spatial attention
- target-specific Window MIL
- OA extent / Mirror TTA는 Base 이후 분리 실험

## 2026-10-18 — C-ANATOMY-CACHE320-V1 Notebook 생성

상태:
- STATIC_QA_PASS
- KAGGLE_NOT_RUN

전체 4,407 train Study를 6 Pack으로 생성하도록 고정했다.
Pack당 약 734~735 Study이며 fixed tensor logical upper bound는 약 13.5 GiB/Pack이다.

Cache:
- windows [N,64,3,320,320] uint8
- window_meta [N,64,12] float32
- valid_mask [N,64]
- study_uid
- anchor_method

Anatomy:
- public code/anatomy dataset:
  heliosli/rsna-orthofoundation-fold0-epoch7-20261004
- pinning manifest:
  heliosli/rsna-knee-compact-r7cnxfsss
- anatomy.pt는 R7 manifest의 anchor_weights_sha256와 runtime exact match가 필요.
- projected anchor가 없는 Series는 local selection에서 제외하고 Full FOV만 허용.

Pinned reference source SHA:
- px_cache.py:
  b13e38a7ad3bd496f8027e02209653e224b0926db4f0853eeb0d076a2d6e2632
- knee_anchor_bank_v2.py:
  e564807a129dfcd3c984348917436ee6083066a4d685340587ebd1d3ea14f309
- probe_infer.py:
  a6cc31448019c84be5868d0a2ff1d99719b23b0f86110efc03efff3ce6bd6980

Notebook SHA256:
- P00: a176b40de512766cdb13b3fae83fd0a465294cdeaa8ee523ef47a413c5bbb206
- P01: c3ceefa50f15391ed40f5c0b5ad35f8e0f9916380316d9cfaef5d22a67323e3d
- P02: 0ae90a1fb8af2f77345ccab362b54756c19ee60e0592d9015975ca7250c1ad8a
- P03: 79bbaa42478861de0b8d658280fa60e04163231bdd609fdf6eec30bf0d99f71b
- P04: fcef4d13f4eecea801f4eeb02aeace77e05c5109d97716c49048ac5ffe04e457
- P05: 20c8757440c23ffe9fc3bd2e7f7113b83fc7d984c4b01caaa767b265df5ea5ac
- ZIP bundle:
  93ec0d6c21099e6b4451f23ca3fc64a226d3c2df5f6b7831631921ed75260aed

정적 검증:
- nbformat/JSON PASS
- 모든 Python cell compile PASS
- 각 Notebook source < 1MB PASS
- global /kaggle/input recursive scan 없음
- Pack ID별 별도 Notebook이므로 수동 config 변경 없음
- partial HDF5는 Study failure 1건이라도 있을 경우 final로 승격되지 않음

Required Inputs:
1. RSNA Knee Abnormality Detection competition
2. heliosli/rsna-orthofoundation-fold0-epoch7-20261004
3. heliosli/rsna-knee-compact-r7cnxfsss

Runtime:
- T4 x2 / Internet Off
- anchor segmentation은 cuda:0 사용
- cache rendering/writing은 CPU 중심
- 현재 실제 runtime 미측정.
- Notebook 첫 화면의 예상 범위는 60~180분/Pack이며 Pack00 실행 후 measured value로 교체한다.

### Immediate Next

P00만 먼저 Save & Run All:
- final receipt.json
- study_audit.csv
- HDF5 actual size
- runtime
- anchor method distribution
- global/local window total
을 검증한다.

P00 PASS 전에는 P01~P05를 무조건 대량 실행하지 않는다.

## Public LB table

| Experiment | Model | Public LB | Status |
|---|---|---:|---|
| C-BASE-01 | ConvNeXt-Small Anatomy 2F | — | NOT_RUN |
| C-OA-01 | Base + OA extent aux | — | NOT_RUN |
| C-MIRROR-01 | C anatomical mirror TTA | — | NOT_RUN |

## Cache table

| Cache | Studies | Packs | Resolution | Windows | Status |
|---|---:|---:|---:|---:|---|
| C-ANATOMY-CACHE320-V1 | 4,407 planned | 6 | 320 | max 64 | NOTEBOOK_READY / NOT_RUN |