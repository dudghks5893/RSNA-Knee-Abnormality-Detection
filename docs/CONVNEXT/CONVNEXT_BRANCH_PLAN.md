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
