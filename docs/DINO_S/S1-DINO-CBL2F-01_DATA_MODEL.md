## 2026-10-17 — S10/S11 데이터·모델 계약 갱신

### S10 확정

- `S10-BASE-TOP18-STRICT-FT-V1` last 2F Public LB **0.923** (사용자 보고).
- S9 Top18 고정, Stage1-B last init, V4 Strict 추가 FT.
- local pooled DEV: epoch0/reference **0.894507**, last(epoch2) **0.893824**. local 감소만으로 checkpoint를 폐기하지 않음.
- last SHA: Fold0 `e30d268a039dbf64a6ba082d4c85cdb1e1ed2090c70e59d9165b3cfe83083908`, Fold1 `02232b0bdcf8062564d04feda43f9fe6ea09edd1553a7025caaf19ac701ee1b3`.

### Final blend 우선 계약

현재 첫 제출 후보는 `0.70 × S10 + 0.30 × S8C Full-MRI Direct`. S8C는 동일 full-MRI forward에서 direct probability와 label-free contribution을 모두 산출한다. S8B는 첫 blend에서는 제외하며 별도 ablation 후보로 보존.

### S11 Multi-View data contract

실험 ID: `S11-TOP18-MULTIVIEW-AUG-FT-V1`.

**Source/selection**
- center 위치는 S9 S8C-only V2 Top18 manifest에서 고정.
- 4,407 Studies 기준 총 79,326 selected centers가 기준 universe.
- 기존 `rmil-04b-full-mri-native224-v3`는 이미 130mm/224로 변환되어 160mm 바깥 정보가 없어 S11 새 View 생성 source로 사용하지 않는다.
- 원본 competition DICOM 또는 동일 raw geometry를 보존한 source에서 새 cache 생성.
- Series slice ordering/RescaleSlope/Intercept/MONOCHROME 처리와 UID/SID integrity는 기존 hidden-test robust loader 계약을 유지.

**View**
1. ANCHOR: 130mm / 224. 기존 S10 Native224 V3와 byte/parity를 우선 검증. 기존 130mm padding 정책 유지.
2. DETAIL: requested 110mm / 280. original available FOV가 부족하면 padding 없이 available extent 사용.
3. CONTEXT: requested 160mm / 224. original available FOV가 부족하면 padding 없이 available extent 사용.
4. DETAIL/CONTEXT coverage: `min(1, min(available_h_mm, available_w_mm) / requested_fov_mm)`를 metadata에 저장.
5. 모든 View는 3-slice `[center-1, center, center+1]`.

**Normalization**
- ANCHOR는 기존 S10 exact Native224 V3 normalization을 유지.
- DETAIL/CONTEXT는 해당 View crop의 전체 Series를 기준으로 percentile 0.5/99.5 → clip → z-score → [-5,5] → resize → uint8.
- preprocessing은 학습/hidden test 동일 구현을 사용.

**Augmentation**
- 3 slice channel에 동일 affine/intensity parameter.
- DETAIL: ±4° / translate±2% / scale .98–1.02 / gamma .96–1.04 / gain±4%.
- ANCHOR: ±6° / ±3% / .96–1.04 / gamma .94–1.06 / gain±6%.
- CONTEXT: ±8° / ±4% / .94–1.06 / gamma .92–1.08 / gain±8%.
- horizontal flip, Cutout, MixUp, strong blur 제외.
- deterministic seed: StudyUID + SeriesUID + center + view + epoch.

**Model/routing**
- init S10 last same Fold.
- 3 View가 하나의 DINOv2-Base/FeatureDINO parameter를 공유.
- 각 View에서 12 target logits 생성 후 target별 fixed routing weight로 **logit** 결합 후 BCEWithLogits loss.
- routing matrix:
  ACL .65/.30/.05; MCL .05/.30/.65; Medial Meniscus .60/.35/.05; Lateral Meniscus .55/.40/.05; Medial OA .65/.30/.05; Lateral OA .60/.35/.05; PF OA .50/.40/.10; Effusion .05/.30/.65; Synovitis .10/.40/.50; Baker's 0/.15/.85; Contusion .15/.45/.40; Fracture .40/.45/.15 (DETAIL/ANCHOR/CONTEXT).
- learned router 없음.

**Training**
- V4 Strict + opposite Gold29, S10 loss/class balance/LR 계약 유지.
- 2 epochs fixed; early stop 없음. Gold29 metrics는 기록용.
- epoch1/epoch2(last) 모두 저장.
- effective Study batch4 유지. multi-view benchmark에서 physical batch/window microbatch 선택; microbatch=1 금지.

---
## 2026-10-16 — Canonical Stage Pipeline Contract (향후 DINO·S 기본 설계)

### Stage1-A — Broad DINO 2-Fold

- Pixel source: `yhlucas/rmil-04b-full-mri-native224-v3`, 5 Packs. Native224 V3 / 130mm center crop / Series normalization / uint8.
- Series/sampler: `yhlucas/stage1-dino-shared-input-manifest-v1`.
  - `common_series_manifest.csv` SHA `e77023a00103f38dd53f6eb62fb142cf3358e0fc4acfe0b85d908c2c190939ea`.
  - `sampler_reference.py` SHA `8ce97e7cebf0c75597e6bd8ea8c262bfb6596dfdcbf0975b8d31101fe125052c`.
  - Study마다 18 Window, 모든 Series 최소 1개, central20–80 후보, Window=[center-1,center,center+1].
- Broad label: `/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_broad.csv`; known SHA `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`.
- Gold: `yhlucas/rsna-knee-gold58-2fold-v1`; manifest SHA `a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`, split SHA `6e66444e12a62c3f73670e421b939f1b286e21e496c29040754a72b1d18b4876`. Fold train = 4,349 pseudo + opposite Gold29 = 4,378, validation=own Gold29.
- V4 pseudo weight `0.25+0.75×confidence`; pseudo-only weighted soft prevalence class balance power0.70, raw scale cap0.5..2.5, target-normalized; Gold row neutral BCE×3; fixed 12-target denominator.
- Optimizer: AdamW β=(.9,.999), eps1e-8, WD .05 excluding bias/norm/token; LR early1e-6 / mid3e-6 / late1e-5 / head2e-4; warmup5%→linear decay; FP16 AMP; grad clip1.0.
- max12, patience4, minimum4 epochs, best checkpoint = held-out Gold29 Macro AUROC.
- Parallelism: Fold0 GPU0 / Fold1 GPU1 independent subprocess; effective Study batch=4/Fold. Physical batch/microbatch/checkpoint are throughput implementation details and must be benchmarked.
- Base historical checkpoint: `woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold{0,1}/best.pt`; SHA F0 `15bd9189eac7a7366239a0747e671f0f567a40a2db660e7054e2de26eb01e629`, F1 `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5`; Public LB 0.910.

### Stage1-B — High-confidence V4 Strict Fine-tuning

- Init: same-fold Stage1-A best checkpoint.
- Strict label: `/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_strict.csv`; SHA `bfca4993e5c985d9318d732bf2a0970dd7af9b3beff1d6ff619822042bf7a2c0`.
- Same image cache, Gold split, sampler and 18 Window semantics.
- Strict pseudo: target mask preserved, confidence-weighted soft labels; pseudo-only soft class balancing power0.70 cap0.5..2.5 + target coverage correction power0.35; Gold neutral BCE×3; fixed 12×batch denominator.
- max3, patience1. Fine-tune LR early1e-7 / mid3e-7 / late1e-6 / head2e-5, WD .05, AMP, grad clip1.0. Runtime benchmark may choose physical batch; effective Study batch remains4.
- Current Base refined encoders used by S7: `/kaggle/input/datasets/woniyeon/rsna-knee-s1ft02-b-v4strict-2fold-best-v1/fold{0,1}/last.pt`; SHA F0 `b4e7d29d3ae0e7ff999c3fb0119dc6126ddd5d5a006c69868818bc440c895aa4`, F1 `966fdfe174c995bfbd8855b520440c508a6aa8539eee9cb5a5f724402b538d79`. 사용자 보고 Public LB 0.914.

### Stage2 — Full-MRI feature extraction

- Stage1-B encoder only; head prediction은 feature cache 생성에 사용하지 않는다.
- 4,407 Studies / 24,371 Series / 819,078 source slices.
- 모든 valid center `1..N-2`의 3-Slice Window: 총 **770,336 Windows/Fold**.
- Base feature = CLS768 + PatchMean768 = 1536-d, cache precision FP16.
- Root: `/kaggle/input/datasets/woniyeon/s7-strictft-fullmri-full4407/fold{0,1}/features.h5`.
- Feature cache는 **backbone size와 Fold checkpoint에 종속**. DINO-Small 실험이 Stage2로 진입하면 Base S7 cache를 재사용하지 않고 Small 전용 cache를 새로 생성한다.

### Stage2 — MIL Predictor / Selector

Common supervision: V4 Strict valid target + weight `0.25+0.75×conf`; Gold row ×3. Executed S8 loss는 `(BCE×mask×weight).sum() / (mask×weight).sum().clamp_min(1)`. AdamW LR2e-4, WD.01, 8 epochs, batch=1 Study, seed `20261015+fold`.

- **S8B predictor**: feature_dim→LN→Linear256→GELU→Dropout.1 → target-specific Window Attention → Series Mean → target-specific Linear. Public LB **0.923**.
  - checkpoints `woniyeon/s8-mil-attn/fold{0,1}/best.pt`
  - SHA F0 `0bbe9d1b532cc933ca346e426c612abf7cbf388e991baa0875f14986e3176770`
  - SHA F1 `e52b42565c79476ce342c75e76be078077a8c94fa88e31ee361408e6b0fd3615`
- **S8C selector**: target-specific Window Attention → target-specific Series Attention → target-specific Linear. Public LB **0.923**.
  - checkpoints `yhlucas/s8c-hier-attn-mil/fold{0,1}/best.pt`
  - SHA F0 `1b16bd88d3a5a13d93bbfb45ac12561e516a17cbf8d34fab50204bf09a67cfa8`
  - SHA F1 `506e73b7462195b3091b60508aa8781200f1d72c8c0469d8cea57a8b11771155`
- 역할 고정: **S8B = 최종 30% MIL predictor**, **S8C = Top-K selector**. S8C가 S8B보다 예측 점수가 높아서가 아니라 Series 중요도를 직접 표현할 수 있기 때문에 selector로 사용.

### Stage2 → Top-K Selection Contract

- Window target contribution:
  `c[s,w,t] = SeriesAttn[s,t] × WindowAttn[s,w,t] × dot(ProjectedWindow[s,w], HeadWeight[t])`.
- Selection importance는 `|c|`를 사용하여 label-free로 유지. **V4/Gold 정답 방향을 selection에 사용하지 않는다**; Hidden Test에서도 동일 알고리즘이 가능해야 한다.
- 각 Study/target 내부 percentile rank → Window score = target별 rank 최대값; tie-break = target rank 평균.
- Pseudo: S8C Fold0/Fold1 rank 평균. Gold Stage3 validation: 자기 OOF Fold selector만. Hidden Test: Fold0/Fold1 평균.
- Diversity: Series coverage 우선, 같은 Series center gap≥3 NMS; 부족하면 gap2→1→0.
- 하나의 순서에서 nested K={18,24,32,48,64}. 최초 Stage3는 **Top18**.
- S8B score/rank agreement는 diagnostic만 저장, canonical ranking에는 미혼합.
- 현재 상태: **설계 동결 / 전체 selector 실행 보류**.

### Stage3 — Top-K DINO Fine-tuning Contract

- Init: Stage1-B same-fold refined DINO checkpoint.
- Training input: Stage2 S8C가 선택한 raw Native224 3-Slice Top18. Epoch별 random 20–80 resampling 대신 고정 Top18 manifest를 사용.
- Supervision: Stage1-B와 동일한 V4 Strict + opposite Gold29, 동일 mask/confidence/class balance, Gold neutral BCE×3.
- Fine-tune LR/optimizer는 Stage1-B와 동일: 1e-7/3e-7/1e-6, head2e-5, WD.05, AMP, grad clip1.0, max3/patience1, best Gold29 Macro AUROC.
- Gold validation의 Top18은 반드시 해당 Gold Study가 MIL training validation이었던 **OOF selector Fold**에서 선택.
- Top18이 기준 개선을 만들면 다음 실험으로 Top32를 비교. K 증가는 selector 효과와 혼합하지 않는다.

### Final Inference / Blend Contract

1. Stage1-B Fold encoder로 Test의 전체 valid Window feature 생성.
2. S8B Fold0/1 → full-MRI MIL probabilities; Fold probability 50:50 mean = `p_mil`.
3. S8C Fold0/1 → label-free selector score → Test Top-K.
4. Stage3 Fold0/1 DINO → 선택된 Top-K 예측; Fold probability 50:50 mean = `p_stage3`.
5. 최종: **`p_final = 0.70 × p_stage3 + 0.30 × p_mil`**.
6. 첫 canonical 버전은 probability blend만 사용. logit blend, target별 blend weight, calibration은 별도 ablation 없이는 넣지 않는다.

### DINOv2-Small Stage1-A Control Experiment

- 목적: 현재 pipeline을 바꾸지 않고 **backbone size만 Base→Small**로 변경해 Stage1-A 성능을 확인.
- 실험 ID: `S1-DINO-SMALL-V4-2F-V1`.
- 그대로 유지: V4 Broad/Gold split/sampler/18 Windows/Native224 V3/Seed20261013/V4 class balance/Gold×3/effective Study batch4/LR bands/head LR/scheduler/max12/patience4/best metric.
- 변경: DINOv2-Small hidden=384, 12 transformer layers, CLS384+PatchMean384=**768-d**, projection `LayerNorm768→Linear768→256`. 나머지 target attention/head 구조 동일.
- MetaResearch DINOv2 Small pretrained Kaggle model을 사용하되 **실제 mounted path와 SHA는 preflight에서 검증 후 본 문서에 기록**. Base SHA를 Small에 재사용하지 않는다.
- 처리량 benchmark는 Small에서 다시 수행하며 가능한 큰 physical Study batch/Window microbatch를 시험한다. 이는 속도 구현 최적화이며 effective batch4는 고정.
- 1차 종료점: Gold58 pooled DEV + 2-Fold standalone Public LB. 결과 전에는 Strict FT/Stage2 Small을 자동 진행하지 않는다.

---
## 2026-10-16 — V54A Stage1 데이터·모델 계약

- Label dataset: `/kaggle/input/datasets/yhlucas/rsna-knee-v54a-label-dataset/V54A_train_labels.csv`; SHA256 `0e390e3fdd27f0974e54fa9649fdd9a50d104b9550570dfd9a0e7e659ac7c399`.
- V54A active cells: **51,332 / 52,188**, 모든 12 target mask=0인 pseudo Study 21개는 zero-gradient라 train UID에서 제외.
- Fold별 train: **4,328 active pseudo + Gold29 = 4,357 Studies**; validation Gold29.
- Backbone/input: DINOv2-Base Full FT, Native224 V3, Study당 18×3-slice Window, 기존 sampler seed 20261013.
- Supervision: V54A soft/mask/weight 그대로 + directional soft-mass imbalance correction + target-mass mild correction + fixed 12×batch denominator; Gold row binary BCE ×3.
- Speed-selected runtime: physical Study batch **4**, window microbatch **72**, activation checkpoint **OFF**, effective Study batch 4, AdamW fused.
- Fold0 best epoch 5, SHA `786b5851cd57bacfe6bad1f94043f68ac477aadacf870bd51d742f12ccdd4743`.
- Fold1 best epoch 9, SHA `73a9006f24c1b84e993ae39a4d46e36a8da8b586f698c1d4a6ff6a1e248317ad`.
- Gold58 pooled DEV Macro AUROC **0.843255** / Macro AUPRC **0.772313**.
- Public LB **0.873** (`S1-V54A-DINO-2F-LB-V1`, 사용자 보고).
- V4 Broad 0.910 대비 -0.037, V4 Broad→Strict FT 0.914 대비 -0.041; 현 시점 주력 encoder로 채택하지 않음.

---
## 2026-10-16 — S8C Hierarchical MIL 모델 계약

- Architecture: `TARGET_WINDOW_ATTN_TARGET_SERIES_ATTN`
- Per Series: 1536-d S7 Window feature → LN → Linear256 → GELU → Dropout0.1 → target-specific Window Attention → [12,256].
- Across Series: trainable `series_query[12,256]`로 target-specific Series Attention → [12,256] → target-specific linear head.
- `series_query`는 zero-init; 초기 Series Attention은 exact uniform mean.
- S7 feature checkpoint contract는 기존 S8과 동일: Fold0 `b4e7d29d3ae0e7ff999c3fb0119dc6126ddd5d5a006c69868818bc440c895aa4`, Fold1 `966fdfe174c995bfbd8855b520440c508a6aa8539eee9cb5a5f724402b538d79`.
- S8C Fold0 best epoch 1: `/kaggle/input/datasets/yhlucas/s8c-hier-attn-mil/fold0/best.pt`, SHA256 `1b16bd88d3a5a13d93bbfb45ac12561e516a17cbf8d34fab50204bf09a67cfa8`.
- S8C Fold1 best epoch 3: `/kaggle/input/datasets/yhlucas/s8c-hier-attn-mil/fold1/best.pt`, SHA256 `506e73b7462195b3091b60508aa8781200f1d72c8c0469d8cea57a8b11771155`.
- Public LB: **0.923** (`S8C-HIER-ATTN-LB-2F-V1`, 사용자 보고). S8B 0.923과 동률.

---
## 2026-10-16 — S7/S8 최신 Fold별 모델·영상 입력 계약

- **Stage1 Strict-FT DINOv2-Base**: Train Pseudo4,349 + Gold29 각 Fold, 다른 Gold29 검증. Study당 **18×(3 인접 Slice) Window**, 사용 가능한 모든 Series에 분산, 중심 20~80% 후보. 
- **S7**: 고정된 Stage1 Fold별 Encoder로 전체 4,407 Studies, 24,371 Series, 819,078 원본 Slice 중 유효 center 1..n−2에서 770,336개 3-Slice Window를 Fold별 1536-d (CLS768 + PatchMean768, fp16) 특징으로 추출.
- **S8A**: 전체 Window→Series 내 Mean→Series Mean MIL→Fold별 sigmoid 확률 평균, Public LB **0.918**.
- **S8B**: 전체 Window→질환별 Window Attention→Series Mean MIL→Fold별 sigmoid 확률 평균, Public LB **0.923**. **질환별 Series Attention은 미사용**.
- **S8C**: 전체 Window→질환별 Window Attention→질환별 Series Attention→Fold별 sigmoid 확률 평균, Public LB **0.923**. S8B와 동률이므로 더 단순한 S8B를 현재 대표 기준선으로 유지.
- **Strict FT checkpoints:** `/kaggle/input/datasets/woniyeon/rsna-knee-s1ft02-b-v4strict-2fold-best-v1/fold{0,1}/last.pt`; Fold0 SHA256 `b4e7d29d3ae0e7ff999c3fb0119dc6126ddd5d5a006c69868818bc440c895aa4`, Fold1 `966fdfe174c995bfbd8855b520440c508a6aa8539eee9cb5a5f724402b538d79`.
- **S8A MIL** `/kaggle/input/datasets/yhlucas/s8-mil-mean/fold{0,1}/best.pt`; Fold0 SHA `7c5ff6743b1c525f47a9adb9dc8613056eba602315f465675e1b33e97378310b`; Fold1 `12cbb9fb2771305fac37c9901afcf04d3faa28de89daf6df9c1de730d4623c9b`.
- **S8B MIL** `/kaggle/input/datasets/woniyeon/s8-mil-attn/fold{0,1}/best.pt`; Fold0 SHA `0bbe9d1b532cc933ca346e426c612abf7cbf388e991baa0875f14986e3176770`; Fold1 `e52b42565c79476ce342c75e76be078077a8c94fa88e31ee361408e6b0fd3615`.
- Kaggle T4×2, Internet OFF, V3_HIDDENFIX 일반 공개 Test 3 Studies/15 Series `SUBMISSION_SUCCESS`; 점수는 사용자 보고. Gold58 반복 개발 검증 자료이지 독립 Test가 아님.

---

# S1-DINO-CBL2F-01 — 데이터·모델 기준 명세 (누적 관리)

- **실험 ID:** `S1-DINO-CBL2F-01` (2026-10-13 신규; 기존 GitHub 파일명/코드 검색에서 중복 미발견)
- **목표:** DINOv2-Base Stage1 지도 Fine-tuning을 STRICT V1과 V4 라벨 정책으로 비교하고, 이후 Full-MRI 특징 캐시·질환별 MIL·Top-K Selector로 확장.
- **운영:** 이 실험군의 Markdown은 본 문서(DATA_MODEL), ROADMAP, EXPERIMENT_LOG **3개만** 만들고 계속 편집한다. 실험·버그·노트북 버전마다 .md 신설 금지.
- **최신 실행 상태(2026-10-13):** A/B Stage1 2-Fold TRAIN 완료 및 Gold58 OOF 재계산 확인. LB V2 Notebook 정적 QA 완료 후 사용자 보고 Public LB A=0.861/B=0.910 수신(실제 제출 스크립트 독립 감사 미완료). 이후 섹션의 V6/V7 미검증 문구는 당시 이력이다.
- **출처:** 로컬 공개된 A/B V6 노트북, 사용자 제공 STRICT/V4 원본 ZIP, Gold58 사용자 제공 정답, 기존 GitHub cache 명세. 최신 노트북 설정이 바뀌면 해당 변경 이력과 SHA를 이 문서에 갱신.

## 2026-10-13 — 실제 PREFLIGHT 오류 수정: V7 WorkerFix

- **새 노트북:** A `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb` (SHA256 `e603978948c0d6d378385105b1b3d8088e8771b3f40e5f53b66d838d1f31e1c0`), B `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb` (SHA256 `5e99513024329483cacc114fb814f83b35b06dfd924705b744451d18c458a84c`).
- V6에서 `worker_path` 미정의로 `subprocess.Popen` 이전에 `NameError` 발생. V7은 Worker 문자열을 `/kaggle/working/STAGE1_DINO_<LABEL>_DUALFOLD/stage1_<label>_worker.py`에 기록하고, 파일 존재·크기·AST를 검증 후 Fold0/1 실행.
- 양쪽 V7은 notebook nbformat/AST, embedded Worker AST, 파일 생성/읽기, 독립 2-프로세스 **CPU mock-launch PASS**. 실제 Kaggle T4×2 PREFLIGHT / TRAIN 아직 미검증.
- **그 외 Label, Loss, Class Balancing, Gold, 모델, Batch 및 Hyperparameters 모두 V6과 동일.** B에도 동일한 V6 결함이 있어 B 노트북도 교체해야 한다.
- V6 파일은 과거 입력 버전 참조용이며 현재 실행 추천 파일은 **V7**이다.

## 1. 공통 데이터 파이프라인

```text
공통 MRI cache: 4,407 Studies = pseudo train 4,349 + Gold58
24,371 Series / 819,078 Slice (총 5 Pack, 190 HDF5 shards)
  -> 물리 위치에 따라 Slice 정렬, 130mm 중심 Crop, Series별 정규화
  -> Native224 V3 uint8 224×224 슬라이스
  -> 이웃 Slice [center-1, center, center+1] 3채널 Window
  -> 1 Study당 18 Window/epoch, 각 Series 포함, center 대략 20~80% 범위 순환 선택
  -> Meta DINOv2-Base CLS768 + PatchMean768 = 1536차원
  -> Stage1 학습용 Projection256 + 타깃별 Window Attention + 12 logits
  -> Study 단위 BCE Loss (Window별 환자 라벨 복제 학습 금지)
```

- **공통 캐시:** `yhlucas/rmil-04b-full-mri-native224-v3`
  - `/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results/RMIL-04B_PACK_00`
  - `/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results (1)/RMIL-04B_PACK_01` ... `results (4)/RMIL-04B_PACK_04`
  - 각 Pack의 `series_index.csv`, `shard_sha256.csv`, `run_status.json`, `shards/*.h5` 등. 기존 RMIL-04C00 190/190 SHA 확인 이력은 존재하지만 **이번 A/B 원격 마운트 검증은 별도**.
- **공통 Series/Sampler:** `yhlucas/stage1-dino-shared-input-manifest-v1`
  - `common_series_manifest.csv`: 24,371 Series; SHA256 `e77023a00103f38dd53f6eb62fb142cf3358e0fc4acfe0b85d908c2c190939ea`.
  - `sampler_reference.py`: SHA256 `8ce97e7cebf0c75597e6bd8ea8c262bfb6596dfdcbf0975b8d31101fe125052c`.
  - 중앙 유효 Center 후보 483,096개; Stage1 18개/Study/Epoch는 **전체 Slice나 전체 Window를 모두 역전파하지 않는다**.
- **공통 Gold58 메타데이터 — 기존 R2D Input 대체:** `yhlucas/rsna-knee-gold58-2fold-v1`, 예상 root `/kaggle/input/datasets/yhlucas/rsna-knee-gold58-2fold-v1`.
  - `gold58_manifest.csv`: 58×12 binary Gold; SHA256 `a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`.
  - `gold58_2fold_manifest.csv`: UID→gold_fold(0/1), SHA256 `6e66444e12a62c3f73670e421b939f1b286e21e496c29040754a72b1d18b4876`.
  - `gold58_fold_class_coverage.csv`, `dataset_contract.json`, `README.md`.
  - **주의:** 로컬 ZIP 패키지 제작 완료, **사용자의 실제 Kaggle Dataset 등록/마운트는 미확인**. `gold58_fold_class_coverage.csv`는 학습 라벨이 아니라 검증 통계.
- **공통 pretrained Model:** MetaResearch DINOv2 PyTorch `base/1`, `pytorch_model.bin`; 후보 `/kaggle/input/models/metaresearch/dinov2/pytorch/base/1/pytorch_model.bin`; SHA256 `014965d9e330e7f4bff8ddcbee9df5e4f2ca032b2f5180942a6edb454783e75d`.

## 2. 라벨 데이터 계정별 구성

| 구분 | A: STRICT V1 | B: V4 |
|---|---|---|
| Kaggle Add Input | `yhlucas/rsna-knee-version-a-strict-v1` | `yhlucas/rsna-knee-v4-consensus-dataset` |
| 파일 | `STRICT_V1/STRICT_V1_TRAIN_LABELS_12_TARGETS.csv` | `rsna_knee_pseudolabels_v4_routed_broad.csv` |
| SHA256 (사용자 원본 ZIP 추출 파일) | `c66810ed4bf35a3fffe35d404aa7eceac860e5f28a013ee2ae7fdf0032497168` | `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c` |
| 의사라벨 Study | 4,181 (168 fully-masked Study 제외) | 4,349 |
| 타깃별 유효성 | 32,163 / 52,188, 나머지 20,025 mask=0 (전체 4,349 기준) | 4,349×12 Soft Label+Confidence |
| Fold별 Train | pseudo 4,181 + Gold train29 = 4,210 | pseudo 4,349 + Gold train29 = 4,378 |
| Fold별 Validation | held-out Gold29 | 같은 held-out Gold29 |

STRICT V1 분포는 **전체 4,349 후보 기준**, pseudo supervised train 4,181개의 유효 라벨 수는 동일하다.

| Target | STRICT Positive | STRICT Negative | Masked / excluded |
|---|---:|---:|---:|
| ACL | 339 | 3,366 | 644 |
| MCL | 37 | 3,724 | 588 |
| Medial Meniscus | 1,525 | 2,446 | 378 |
| Lateral Meniscus | 542 | 3,266 | 541 |
| Medial OA | 212 | 2,398 | 1,739 |
| Lateral OA | 66 | 2,490 | 1,793 |
| PF OA | 204 | 2,268 | 1,877 |
| Effusion | 542 | 2,679 | 1,128 |
| Synovitis | 511 | 35 | 3,803 |
| Baker's | 100 | 1,568 | 2,681 |
| Contusion | 364 | 2,367 | 1,618 |
| Fracture | 165 | 949 | 3,235 |

V4 Soft Label은 단순 0/1로 전환하거나 다수 클래스를 일괄 삭제하지 않는다. 원본 컬럼은 12개 score + 각 `__conf`이며 `confidence_floor=0.25`를 적용한다. 평균 Confidence가 매우 낮은 Synovitis 등에는 label noise 경고를 남긴다.

## 3. 확정된 Gold58 2-Fold

- Seed `20261013`; Fold0 held-out29, Fold1 held-out29. 각 UID는 validation으로 **정확히 한 번** 등장.
- 각각의 12개 타깃에 양성/음성 최소 1명 이상이 존재하여 **Fold×Target AUROC 24개가 계산 가능**. 예시 MCL: Fold0 4+/25−, Fold1 5+/24−.
- **Fold0:** Gold Group1(반대 29)로 학습, Fold0 29로 검증. **Fold1:** Gold Group0로 학습, Fold1 29로 검증. A/B 동일 UID Fold 매핑.
- Gold 반복 사용으로 인해 결과는 개발/교차검증 성능이며 독립 테스트가 아니다.
- **정책 차이:** 원본 STRICT V1 Release README는 Gold58 튜닝/학습을 제한한다. 현 노트북의 `CUSTOM_GOLD_2FOLD_TRAIN`은 **별도의 사용자 승인 연구 프로토콜**이므로 STRICT 공식 릴리스 준수 결과라고 표기하지 않는다. Stage1 이후 MIL/Selector에서도 같은 Fold의 held-out Gold 라벨·예측/선택 정보를 누설하면 안 된다.

## 4. Stage1 모델과 학습 설정 (V6 노트북 실물 기준)

| 항목 | 설정 |
|---|---|
| Backbone | Meta DINOv2-Base, ViT-B/14, full fine-tuning, CLS+PatchMean 1536d |
| Input | `[18, 3, 224, 224]` / Study; Window=인접 3 Slice |
| Head | LayerNorm1536→Linear256→GELU→Dropout0.10, 타깃별 Window Attention, 12 logits, Mean residual 0.1 |
| Runtime | 각 계정 Kaggle T4×2, GPU0→Fold0, GPU1→Fold1 **완전 독립 1-GPU subprocess 2개**, DDP 아님 |
| Study batch | physical 1/GPU, Gradient Accumulation 4, effective 4/**Fold** (양 Fold 합산 batch8로 해석 금지) |
| Window microbatch | PREFLIGHT에서 18→12→8→4를 GPU 시간/VRAM으로 시험 후 선정. 과거 Batch≥124의 여유와 동일한 연산 단위라고 가정하지 않음 |
| Optimizer | AdamW β=(0.9,0.999), eps=1e−8, weight decay 0.05(편향/정규화 등 제외) |
| Backbone LR | early layer 1e−6, middle 3e−6, late 1e−5 (그 외 encoder 1e−6) |
| Head LR | 2e−4 |
| Scheduler | warmup 5% optimizer steps → linear decay |
| Numeric | FP16 AMP + GradScaler, activation checkpoint, gradient clipping 1.0 |
| Epoch / stopping | max12, patience4, 최소 4 Epoch 조건 |
| Best checkpoint | held-out Gold29 Macro AUROC 최대 |
| 보조 지표 | Macro AUPRC, 12 target AUROC/AUPRC, Recall/Precision/F1/Specificity/Balanced Accuracy @ threshold0.5, confusion matrix |
| 저장 | Fold별 `best.pt`, `last.pt`, epoch history, predictions, class weights, logs, integrity report; 종료 후 OOF58 결합 |

**A/STRICT 전용 Loss:** mask=0인 타깃은 gradient=0. 유효 pseudo 라벨로만 class balancing; 양성/음성 양쪽 빈도 보정 power0.70, ratio>20일 때 다수 타깃 loss만 Epoch마다 회전 감소(cap20×희소 클래스), target count correction power0.35. 희소 클래스 사례는 매 Epoch 유지. Study 자체나 타깃 외 다른 질환 정보 삭제 금지.

**B/V4 전용 Loss:** soft BCE의 양성·음성 항 별도 보정 power0.70, 가중치 [0.5,2.5], 정규화; per-target confidence weight `0.25+0.75×conf`, 모든 4,349 Study 유지. 양·음 soft mass 기준; 0.5로 hard threshold하여 삭제하지 않음.

**Gold 학습 행:** pseudo-derived class weights 적용하지 않는 neutral BCE ×3. Loss denominator는 12개 타깃으로 고정하여 Gold×3/Confidence가 분자분모 상쇄되지 않음.

**비교 해석:** A/B는 라벨 구성뿐 아니라 실제 유효 타깃 수·Loss 보정 방식도 다르다. 결과가 달라져도 '라벨 정확도 효과' 단독 원인으로 결론 내리지 말 것. 필요 시 공통 UID/타깃 마스크와 동일 Loss의 추가 통제 실험.

## 5. Notebook 및 Input 운용 상태

- A: `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb`; 파일 SHA256 `e603978948c0d6d378385105b1b3d8088e8771b3f40e5f53b66d838d1f31e1c0`
- B: `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb`; 파일 SHA256 `5e99513024329483cacc114fb814f83b35b06dfd924705b744451d18c458a84c`
- 두 파일은 대화 산출물이며 **현재 GitHub에 노트북 바이너리를 커밋했다는 뜻이 아님**. 최신 구현으로 교체 시 파일명·SHA·설정을 본 문서에서 갱신.
- **Add Input 5개/계정:** 공통 ① Native224 cache ② shared manifest ③ 전용 Gold58 ④ official DINOv2 Base 모델, 개별 ⑤ STRICT/V4 라벨.
- 구 R2D `rsna-knee-wide224-persistent-cache-v1`은 이 Stage1 Gold Input에서 **사용하지 않음**.

## 2026-10-13 — Stage1 학습 완료 체크포인트 계약

- **B V4 우선 Stage2 후보:** Fold0 best.pt SHA256 `15bd9189eac7a7366239a0747e671f0f567a40a2db660e7054e2de26eb01e629` (Best Epoch8, Gold29 AUC0.892702); Fold1 `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5` (Epoch9, AUC0.868232).
- **A STRICT 보존 후보:** Fold0 best.pt `e5ae8a3a2b30d5bf71a19aabc7cfba888bb05d91b152d82931c3d44f3d4387a6` (Epoch9, AUC0.838365); Fold1 `954d099a0e4274c1ee4581fc8c518fd3f30dcafff39e4d2ed941eb9224704935` (Epoch7, AUC0.785654).
- **모델 아키텍처·입력·학습 Loss 계약은 본 문서의 V7 설정과 동일**. Fold0 validation Gold29와 Fold1 validation Gold29의 모델을 혼동하지 않는다. 두 Fold 각각 독립 encoder+head 전체 checkpoint이며 1536d feature는 **DINO Encoder의 CLS768+PatchMean768 출력**을 사용한다. 저장된 best.pt는 `model`, `epoch`, `fold`, `label_mode`, `config` 및 `metric_auc`가 포함된 torch checkpoint.
- **실물 확보 상태:** 사용자 공유 review ZIP은 `.pt` 바이너리를 제외하므로 보고된 SHA값은 `training_summary.json`에 대한 신뢰이며 **실제 `.pt` 파일 바이트 검증은 미완료**. Kaggle Output에서 추출해 별도 Dataset Add Input으로 등록한 뒤 일치 확인 필요. 모델 파일을 새 GitHub 문서에 넣는 게 아니라 기존 본 데이터·모델 문서에서 registry 업데이트.
- **성과 참조:** Gold58 DEV OOF Macro AUROC A=0.811284, B=0.871112. 세부 Target/F1/Recall 및 해석은 동일 실험 ID의 `EXPERIMENT_LOG.md` 참조.

## 2026-10-13 — 2-Fold LB Test Data and Checkpoint Input contract

- A Strict and B V4 are distinct Code Competition notebook submissions. For each, Fold0 and Fold1 best weights must be loaded strict, output sigmoid probabilities and then average 50:50. Gold58 is never a scoring inference input.
- Proposed (not published/verified) checkpoint datasets: yhlucas/rsna-knee-stage1-strict-f01-best-v1 and yhlucas/rsna-knee-stage1-v4-f01-best-v1, root filenames fold0_best.pt and fold1_best.pt. The four exact SHAs are in previous Stage1 checkpoint contract section. Do not use TRAIN review ZIP as weights.
- Raw test data is sourced from competition RSNA Knee Abnormality Detection, test.csv/test_series.csv/sample_submission.csv and test_series/<Study>/<Series>/*.dcm. Existing HDF5 Native224 V3 training cache contains only 4,407 train/Gold subjects; it cannot supply hidden test studies.
- Preprocessing reproduces RMIL-04B Native224 V3: DICOM physical slice sort by normal dot ImagePositionPatient; 130mm center crop (pad outside -5 after normalization); MONOCHROME1 inversion; per-Series 0.5/99.5 percentile clip sampled at <=200k pixel stride; Series mean/std Zscore; clip +-5; resize OpenCV INTER_AREA (224x224); uint8 np.rint((z+5)*25.5). Use 18 Window sampler SHA 8ce97e7cebf0c75597e6bd8ea8c262bfb6596dfdcbf0975b8d31101fe125052c, epoch0, [center-1,center,center+1].
- Original FeatureDINO model class source SHA256 b385856a8e5ecfcd81da42c417dc1ba96ca5cb4f3d345a44a162907c32ad0874 is identical in A/B training ZIPs; notebook preserves it. MetaResearch Dinov2 PyTorch Base v1 original model pinned via SHA is also needed to reconstruct the exact encoder init/config.
- Notebook SHA A 268187b2ab0db2390a008cb627adaa0e8aa731b2ff8f35560cdaf85856d59eb1; B a0c7bd71d50f5e652f49ee1f23398be1eceb8b34b6fcc2b4195e6b60ebe04392. Static AST, nbformat, sampler parity 20 Studies/360 Windows, synthetic pixel byte parity 12 Slices/3 Triplets PASS. Full Kaggle inference and official LB UNVERIFIED.
- T4x2 two full models running parallel GPU inference; Internet OFF; Kaggle Submission Code runtime <=9h. Output submission.csv strict shape/range/Study UID/12 columns/SHA. If a Study has corrupt DICOM, neutral fallback is logged; high fallback rate invalidates quality claims.

## 2026-10-13 — V2 LB Checkpoint path correction (current)

- **A STRICT:** `/kaggle/input/datasets/yhlucas/rsna-knee-stage1-strict-f01-best-v1/fold0/best.pt` and `/fold1/best.pt` under the same root. User-provided exact structure. V2 Notebook SHA `d272241254c8222004a74dbf34def355a6093cc7ef588d5852a22e965a89bdb0`.
- **B V4:** `/kaggle/input/datasets/woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold0/best.pt` and `/fold1/best.pt` under the same root. **Owner `woniyeon` (not `yhlucas`).** V2 Notebook SHA `2c7323124de1b5fa3a2de2463618f19b6a342a9c7e060abe8a9a0dcf0ce2cb95`.
- Supersedes V1 **checkpoint root-level `fold0_best.pt`, `fold1_best.pt` assumptions**; model SHA and scientific configuration unchanged. Actual Kaggle mount and model file bytes not independently tested; notebook validates file presence and SHA before inference.

## 2026-10-13 — Historical Batch vs future throughput policy

- V7 Stage1 physical StudyBatch1/GPU, gradaccum4, Window microbatch18, HDF5 synchronous and activation checkpoint ON were the **completed run settings**; they must not be reused without profiling as next-stage defaults.
- User reports older Batch124+ simultaneous operation and ~20GB spare VRAM; user weekly GPU allocation 30h. Which device(s) owned that spare VRAM and whether Batch124 refers to Study/Window are unknown, but speculative OOM avoidance is not an acceptable reason to force small batches.
- Next study benchmarks actual 128-256 MRI studies, optimizer steps, Study batch 1/2/4/8+, Window microbatch 18/32/64/96/124/128+, checkpoint ON/OFF, HDF5 prefetch, and 2GPU mode; selects measured max throughput. Full TRAIN aims <=4h, >=8h estimated blocks, weekly 30h quota is mandatory. No pretrained/label/input semantics change under this policy update.
- References: [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](../AI_AGENT_KAGGLE_NOTEBOOK_RULES.md), [GPU_BATCH_RESOURCE_MANDATORY_POLICY.md](../GPU_BATCH_RESOURCE_MANDATORY_POLICY.md).

## 2026-10-13 — 제출 모델 공식 Public LB 사용자 보고 (결과와 출처)

- 두 V2 Notebook의 A STRICT 2-Fold 및 B V4 2-Fold sigmoid probability equal-mean 제출에 대한 **사용자 보고 Public LB**: **A=0.861**, **B=0.910**. 제출 스크립트/CSV 및 숨겨진 Test 실패 UID 감사 자료는 별도로 수신하지 않았으므로 그 실행 세부 정보를 PASS로 단정하지 않는다.
- 개발 Gold58 OOF Macro AUROC: **A=0.811284**, **B=0.871112**. External Public LB 우위(B−A=+0.049)는 별도 test 결과이고 OOF/Both are not directly paired distribution metrics.
- 기존 프로젝트 최고 Exp57 Public LB **0.918** (3-fold selector + full MRI direct 70:30) 대비 **B=−0.008**, **A=−0.057**. B는 next full-MRI encoder candidate; stage1 checkpoints preserved.
- 모델 아키텍처/전처리/생성된 checkpoint hash는 V7 학습 및 V2 추론 명세에서 **변경 없음**. 이번 업데이트는 결과 기록이며 새 GPU 추론/학습 실행이 아님.

## 6. 변경·감사 원칙

각 데이터셋의 Kaggle 게시 버전, 실제 mounted path, SHA, UID 교집합, mask, 라벨 정합성은 실측 때 이 문서에 갱신한다. QA 'PASS'와 GPU 학습 'COMPLETE'를 혼동하지 않는다. 모델 설정 변경은 이유/영향과 이전 값까지 남긴다.

- [계획 및 현재 단계](S1-DINO-CBL2F-01_ROADMAP.md)
- [실제 실행 결과 누적 로그](S1-DINO-CBL2F-01_EXPERIMENT_LOG.md)
- [프로젝트 공통 Kaggle Notebook 규칙](../AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)


## 2026-10-14 — S1FT02 Broad→Strict 재학습 입력/클래스 가중치 계약 (계획)

- Common warm-start checkpoint B V4 Broad: `/kaggle/input/datasets/woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold0/best.pt` SHA `15bd9189eac7a7366239a0747e671f0f567a40a2db660e7054e2de26eb01e629`, Fold1 `/fold1/best.pt` SHA `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5`.
- A source: `yhlucas/rsna-knee-version-a-strict-v1/STRICT_V1/STRICT_V1_TRAIN_LABELS_12_TARGETS.csv`, SHA `c66810ed4bf35a3fffe35d404aa7eceac860e5f28a013ee2ae7fdf0032497168`. B source: `yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_strict.csv`, SHA `bfca4993e5c985d9318d732bf2a0970dd7af9b3beff1d6ff619822042bf7a2c0`.
- Other inputs same Stage1: 5Pack Native224 V3, Shared Series Manifest/Sampler SHA, Gold58 frozen 29/29 split, MetaResearch DINOv2 Base/1 pretrained. No competition input for cached training, Competition required for later LB inference.
- Pseudo-only target loss: A hard binary + Mask + majority-rotation cap20:1 + inverse-frequency power0.7 + coverage power0.35; B routed strict Soft + Confidence + Mask + soft pos/neg weighted prevalence inverse power0.7 cap0.5..2.5 + coverage power0.35. Gold29 neutral BCE×3, no pseudo class priors. Unmentioned Mask=0 never converted to negative.
- New model datasets for submission are **proposed only**, not yet registered: A `yhlucas/s1ft02-a-strictv1-f01-v1`, B `woniyeon/s1ft02-b-v4strict-f01-v1`; require `fold0/best.pt`, `fold1/best.pt`, `fold0/training_summary.json`, `fold1/training_summary.json`. Submission notebooks fail-fast on missing files, audit checkpoint SHA from training summary. Both Fold models initialized from same V4 Broad; previously trained A Strict model is not used.
- The training notebooks alter Study physical batching/DataLoader and turn checkpointing into a performance-tested switch while preserving architecture StateDict key names. Model checkpoint actual GPU load/Baseline Val parity not confirmed until Kaggle GPU preflight.
