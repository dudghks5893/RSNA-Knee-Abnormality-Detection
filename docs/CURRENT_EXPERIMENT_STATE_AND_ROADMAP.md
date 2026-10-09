# RSNA Knee — Current Experiment State & Roadmap


## 2026-10-10 — CURRENT ACTIVE WORK: RMIL-02 CPU coverage preflight (overrides old RMIL-01 NEXT below)

**RMIL-01 COMPLETED / AUDITED:** [actual received ZIP/target metrics audit](RMIL-01_COMPLETED_AUDIT_2026-10-10.md). GPU0 MEAN Gold58 AUROC **0.5763704369**, AUPRC **0.4507296488**, best E4; GPU1 shared 4-window ATTN AUROC **0.5442963023**, AUPRC **0.4158921311**, best E3. Differences **−0.0320741346 AUROC**, **−0.0348375177 AUPRC** (ATTN minus MEAN); 4/12 target AUROC improvements, 8/12 declines. Both workers PASS; review ZIP 43 entries, all 38 declared artifact hashes PASS, source ZIP SHA recorded. Checkpoint bytes/Gold58 label manifest absent from ZIP; this is non-independent Gold development validation only. **MEAN retained as comparator**, shared ATTN not promoted.

**NEXT, UNEXECUTED RMIL-02:** CPU-only actual-Slice 16/24/32 windows-per-Series candidate cache design/preflight, geometry sorting, adjacency, deduplication, window coverage, SHA and persistent storage/runtime budget. Separate window count from selection policy, preserve Train300/Gold58 split and controlled MEAN model optimization for subsequent GPU ablation. Do not launch GPU for raw DICOM decoding; do not falsely claim dataset prepared.

**Unchanged:** RMIL-03 target-specific Window/Series MIL later; RMIL-04 full4349 after pilots; optional RMIL-05 2D and RMIL-06 3D only with repeatable added value. C1/C2/C3 all undecided. No 3/5-Fold or Exp57 automatic blend. Best verified project Public LB Exp57 **0.918**, unchanged. Old 'RMIL-01 immediate next' below superseded.

---

## 2026-10-10 — CURRENT ACTIVE WORK: RMIL-01 Window Pooling (supersedes all older future tasks below)

**Immediate next:** `RMIL-01`, controlled **2.5D R34 MEAN vs learned Window Attention**, Train300/Gold58, frozen shared 224×224 cache, T4×2, Internet OFF. Notebook prepared, **no Kaggle results yet**. Existing `EXP-01` name already occupied. GPU0=MEAN / GPU1=ATTN. Zero-init attention = initial Mean; only pooled feature selection changes. Read [RMIL experiment contract & architecture candidates](RMIL_FINAL_ARCHITECTURE_AND_EXPERIMENT_PLAN.md) FIRST.

**New active research order:** RMIL-01 pooling → RMIL-02 high-coverage actual Slice cache → RMIL-03 target-specific Window+Series Attention → RMIL-04 full4349 single expert and standalone LB → RMIL-05 optional 2D complementary expert → RMIL-06 optional 3D complementary expert.

**Three UNDECIDED final configurations:** C1 **one 2.5D target-aware MIL CNN**, C2 **2D+2.5D**, C3 **2D+2.5D+3D** (3D contingent on independent gain). **No committed 3/5-Fold or Exp57 ensemble**, since >10 models could be inefficient. Exp57 **Public LB 0.918** preserved as benchmark, not mandatory part of final. V6 label candidate not canonical until audited.

**Recently completed and now logged:** R2D-SHARED 4, RDINO-01 4, R3D-15 3 (11 actual results); see [full 11 ZIP SHA audit and metrics](R2D_RDINO_R3D15_COMPLETED_AUDIT_2026-10-10.md). Most favorable Train300/Gold58 score R2D-SHARED-A-25D AUROC **0.57637044**, not comparable to Exp57 Public LB 0.918. R3D-14V4 standalone user-reported Public LB **0.689** also completed; earlier below-text describing R3D-12/R3D-14 as 'NEXT' is historical and superseded.

---

최종 업데이트: **2026-10-10**

이 문서는 **현재 상태와 다음 작업만 기록하는 기준 문서**다.
오래된 계획/상태를 아래에 누적하지 않는다.

- 완료된 실험의 상세 기록: [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md)
- 앞으로의 R3D 실행 계획: [3D_RESNET_EXPERIMENT_PLAN.md](3D_RESNET_EXPERIMENT_PLAN.md)
- Kaggle Notebook 작성/복구 규칙: [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
- 새 채팅 인수인계: [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md)

이 문서와 위 3개 문서가 과거 README / Specialist 문서의 오래된 "현재 다음" 문구보다 우선한다.

## 2026-10-08 — 병렬 작업 결정: 기존 V4로 R3D 선행 학습

**현재 Kaggle/R3D lane의 다음 작업은 V6를 기다리는 것이 아니라 V4 baseline을 먼저 완성하는 것이다.**
새 LABEL-V6 라벨링은 별도 GPT-6 채팅에서 병렬 진행하며, 이 결정은 기존 frozen Main 구조나 R3D-12CACHE 완료 상태를 바꾸지 않는다.

1. **R3D-12V4DATA:** 기존 V4 Routed Broad / official Gold58 / R3D-12CACHE full-volume Kaggle Input 검증 및 label-distribution/loss/runtime preflight (CPU 우선, GPU smoke/profile만 별도).
2. **R3D-13V4:** MedicalNet R34 pretrained에서 단일 Main을 새로 학습. Train=V4 report-only4349 (soft target + confidence), validation=Gold58 (학습 제외).
3. **R3D-14V4:** standalone hidden-test Kaggle LB 제출. Exp57 Public LB 0.918과 비교.
4. **LABEL-V6 canonical release 이후:** 같은 구조/seed/budget/검증으로 R3D-13V6를 처음부터 학습 → R3D-14V6 standalone → V4/V6 target별/전체 비교.
5. 별도의 합의 근거가 생긴 경우에만 Exp57 blend, 선택적 3/5fold 확장. 과거 pseudo-only specialist/구 구조 탐색 반복 금지.

**경계조건:** R3D-12CACHE raw volume 생성+로컬 audit PASS이나 10.04GiB 전체 Kaggle Dataset 등록과 정확한 mount root는 아직 독립 확인되지 않았다. V4 broad all 52,188 target soft scores non-null, strict 39,792 non-null. V4 routing은 과거 Gold57을 사용했으므로 Gold58 validation은 독립 test가 아니다. V4와 V6의 first-run은 가능한 한 라벨 이외 요인을 고정해야 공정하게 비교할 수 있다.

상세 실행·비교 계약: [R3D_V4_V6_CONTROLLED_COMPARISON_PLAN.md](R3D_V4_V6_CONTROLLED_COMPARISON_PLAN.md).


---

# 1. 현재 프로젝트 기준점

## Public Leaderboard

현재 프로젝트 최고 Public LB:

- **0.918**
- **Exp57 — 3-Fold B3A + 3-Fold Full-MRI Direct 70:30 Hybrid**

Exp57은 단순 2D 모델이 아니다.

요약 구조:

~~~text
전체 MRI 모든 Series / 3-slice windows
        ↓
Fold별 task-tuned DINOv2-Base
        ↓
Fold별 Full-MRI Hierarchical MIL
        ├─ Direct probability branch
        └─ attention으로 환자별 Top-24 raw windows 선택
                    ↓
          Fold별 B3A end-to-end model

P_B3A_3F    = mean(F0, F1, F2)
P_DIRECT_3F = mean(F0, F1, F2)

P_FINAL = 0.70 × P_B3A_3F + 0.30 × P_DIRECT_3F
~~~

- Exp57 Public LB = **0.918**
- SS08 Specialist-only Public LB = **0.876**
- 따라서 R3D는 최종적으로 Exp57과 **상보적 ensemble** 가능성까지 확인해야 한다.

---

# 2. 현재 R3D 한 줄 상태

현재 Main R3D:

~~~text
ALL Series
→ 130 mm physical center crop
→ interpolated D24 × 96 × 96
→ MedicalNet R34
→ GLOB
→ metadata embedding
→ Transformer + shared CLS
→ 12 target heads
~~~

현재 고정값:

- Series policy: **ALL**
- physical FOV: **130 mm center crop**
- depth: **interpolated D24**
- in-plane: **96×96**
- Backbone: **MedicalNet R34**
- Representation: **GLOB**
- Anatomy mask: **OFF**
- Aggregator: **Transformer + shared CLS**
- Full fine-tuning
- pure FP32
- BatchNorm running stats frozen
- Backbone LR: **1e-5**
- New-layer LR: **5e-5**
- Weight Decay: **1e-4**

## R3D-11 결과 검토 — 2026-10-08

- 대상: **Medial Meniscus 단일 target**. 아래 AUROC/AUPRC는 12-target Macro 값이 아니다.
- Pipeline / paired contracts: **PASS**. 자동 adoption_status: **REVIEW_REQUIRED**.
- 검토 결론: **SAG1은 유망 후보로 보존하되 최종 specialist 채택·hard routing은 보류**. Main은 ALL 유지. 이번 결과만으로 specialist 추가 학습을 시작하지 않는다.

| Scope | ALL AUROC | SAG1 AUROC | ΔAUROC | ALL AUPRC | SAG1 AUPRC |
|---|---:|---:|---:|---:|---:|
| F0 | 0.531250 | 0.697917 | +0.166667 | 0.426910 | 0.618876 |
| F1 | 0.555556 | 0.777778 | +0.222222 | 0.649439 | 0.823719 |
| F2 | 0.659091 | 0.738636 | +0.079545 | 0.730888 | 0.770433 |
| Pooled Gold58 OOF | 0.582933 | 0.606971 | +0.024038 | 0.553281 | 0.599431 |

해석:

- 세 fold 모두 AUROC/AUPRC 개선. Pooled AUPRC Δ = **+0.046150**.
- Pooled AUROC 차이의 descriptive paired bootstrap 95% 구간: **[-0.193510, +0.238011]**. 선택된 checkpoint에 조건부이며 epoch/구조 선택 및 fold 간 의존성을 보정한 독립 검정이 아니다. 우월성 확정 불가.
- Fold마다 점수 분포가 달라 fold 내부 순위 개선이 pooled 순위 개선으로 그대로 이어지지 않는다. SAG1 F0 확률 범위 **0.44657543–0.44822356**으로 매우 좁다. ALL F1은 전원 0.5 초과. 원인 확정은 하지 않으며 calibration/학습 안정성 점검 대상이다.
- SAG1 pooled threshold 0.5 sensitivity **0.076923**, specificity **1.0**. 높은 fold AUROC만으로 임계값 성능이나 확률 품질을 보장하지 않는다. Gold58에 사후 calibration을 맞춰 개선으로 보고하지 않는다.
- Gold58은 epoch 선택과 반복 실험에 사용된 model-selection validation이다. 독립 최종 test로 부르지 않는다.

재현·검증:

- Gold58 unique UID, 양성26/음성32. 저장 OOF 예측에서 pooled AUROC/AUPRC를 재계산해 metrics.csv와 일치 확인.
- Canonical MedicalNet R34 pretrained matched fraction 1.0; Crop130 interpolated D24×96×96; FP32; BN stats frozen; MASK_OFF.
- 각 fold ALL/SAG1의 초기 모델 SHA, study sampling trace, 공통 SAG1 증강 trace 일치. 세 paired contracts PASS.
- 10 epochs × 192 study draws; fold-specific Pseudo1000 + training Gold; Gold sampling probability .25; accumulation4. 실제 unique sampled studies F0 799/F1 788/F2 788.
- 매 epoch 종료 후 validation. AUROC 우선/AUPRC tie-break. ALL best epoch F0/F1/F2 = **5/3/6**, SAG1 = **6/8/4**.
- ALL runtime 약 **32.3–32.9분/fold**, SAG1 **6.8–7.0분/fold**. 병렬 실행 조건의 관측치이며 최종 full-data 시간 추정으로 직접 쓰지 않는다.
- Historical normalized weighted BCE 유지: 단일 target의 양수 scalar weight는 분자/분모에서 상쇄된다. pseudo .35 및 confidence가 의도한 sample attenuation으로 작동한다고 해석하지 않는다. 최종 학습에서 unknown mask와 loss 정규화를 명시적으로 재설계한다.
- 여섯 best.pt는 search 산출물. 최종 모델 초기화에 재사용하지 않는다.
- 결과 원본: `A_R3D-11_results_no_pt.zip`; SHA256 `b6bd762858cc581b6f025dd9d155292f67c817f554d2f1f2479658a669af8848`.

## 확정된 최종 학습 방향

- **단일 Main R3D 모델**, 3-fold 최종 학습 아님. 기존 3-fold는 구조 비교용이었다.
- 학습 범위: **report-only 4,349 studies 전체**. 검증: **공식 Gold58 전원**, 학습에서 제외.
- 신규 라벨에서 supervision이 전혀 없는 study는 손실에 기여할 수 없다. 실제 유효 supervision 수는 audit 후 별도로 기록한다.
- Main: ALL → Crop130 → interpolated D24×96×96 → MedicalNet R34 → GLOB + metadata → Transformer/shared CLS → 12 heads.
- Search best.pt를 이어 학습하지 않고 MedicalNet pretrained에서 새로 시작한다.
- Epoch은 전체 학습 목록 순회를 기준으로 한다. 192 draws/epoch search budget을 최종 학습에 그대로 적용하지 않는다.
- Epoch 종료 시 Gold58 12-target Macro AUROC 우선, Macro AUPRC tie-break로 best.pt 선정. Epoch 수/compute budget/unknown mask 및 loss 정규화의 구체 구현은 아직 확정 전.
- Gold58은 이미 반복 탐색에 사용되었으므로 untouched test가 아니다.
- 먼저 standalone R3D Public LB 확인, 이후 Exp57(0.918)과 ensemble 상보성 검토. SAG1은 보류 후보이며 자동 추가하지 않는다.

## 바로 다음 작업

1. **Competition-aligned report label policy v2 freeze 완료**: [LABEL_RECONSTRUCTION_POLICY_V2.md](LABEL_RECONSTRUCTION_POLICY_V2.md).
2. Qwen3-8B / Mistral-Nemo-12B Kaggle GPU reader plan은 **폐기/미실행**. 현재 실행 계약: [LABEL_V6_GPT6_CHUNKED_EXECUTION.md](LABEL_V6_GPT6_CHUNKED_EXECUTION.md).
3. report-only 4,349 studies를 원본 `train.csv` 행 순서 그대로 **87 chunks**로 고정:
   - Chunk 001–086 = 50 studies / 600 decisions
   - Chunk 087 = 49 studies / 588 decisions
   - 총 52,188 decisions
   - report-only UID manifest SHA256 = `e675c1cfb8e88b3ec00af4fcba77bfb010e324e3a3473b04089da651af630a94`
   - chunk manifest SHA256 = `66179ef419094e6204ea3c39c4696d1da68463320bc9c58168e96d993e5a0cd5`
4. primary reader는 **GPT-6**. 기본 최대 5 chunks/chat으로 18개 chat에 배치하되, context 품질이 우려되면 더 일찍 끊고 최신 cumulative Master/Handoff로 새 chat에서 계속한다.
5. 각 chunk는 모든 study의 12 targets를 직접 판정하고 exact report evidence + Unicode offset + report SHA를 보존한다. 이전 completed chunk는 integrity defect가 없으면 재판정하지 않는다.
6. 4,349 완료 후 4,349 studies / 52,188 decisions 전체 contract, target별 5-state distribution / supervised coverage / positive prevalence / language·script / duplicate consistency를 감사한다.
7. HIGH-review / inference-used / contradiction / ambiguity / distribution anomaly를 **GPT-6 Astra가 원본 report + frozen policy로 독립 재판정**하고 최종 adjudication 후 canonical LABEL-V6를 freeze한다.
8. canonical release 후에만 target별 N_pos/N_neg/mask coverage로 class weight와 **masked per-target BCE → 12-target macro average** loss를 확정한다.
9. canonical label release → R3D-13 single Main full-data → standalone Public LB → 필요 시 Exp57 complementary blend. 동일 canonical manifest를 Exp57 old-vs-new label 비교에도 사용한다.

중요: 공식 Gold는 MRI image-derived consensus label이다. 새 라벨은 공식 영상 판정 기준을 최대한 모사하는 report-derived supervision이며 새로운 ground truth가 아니다.

### GPT-6 실행·다음 채팅 인수인계 보강 (2026-10-08)

- 사용자용 새 배포본: `RSNA_Knee_LABEL_V6_GPT6_Reviewed_Workbench.zip` (`LABEL_V6_GPT6_Chat01_START.zip`부터 시작).
- 기존 GPT-5.6 Sol 이름의 Chat Pack/프롬프트는 **SUPERSEDED**; 원본 chunk data와 Policy V2 SHA는 변경되지 않음.
- 입력 완전성: 원본 순서 4,349 UID / 87 chunk / 52,188 decision; Source UID index / chunk SHA 검증.
- 실제 Chunk 완료 시 누적 Master(.jsonl.gz) + 감사 JSON + Handoff JSON + 다음 단계 프롬프트를 묶은 `HANDOFF_BUNDLE.zip` 전달.
- 다음 Chat에서는 **다음 Chat Pack + 직전 Handoff Bundle** 두 ZIP을 올려 SHA와 이전 12-target per UID 범위를 검증 후 다음 chunk만 append. 조기 채팅 종료 시에는 동일 Chat Pack으로 재개.
- 단일 GPT-6 reader 결과는 candidate. 코드를 통한 구조적 PASS만으로 임상/대회 의미 정확성은 증명되지 않음. 고위험 및 샘플 감사 후 GPT-6 Astra(이용 가능 시) 검토, canonical release, 분포·class weight 확정.
- 실행 계약: [LABEL_V6_GPT6_CHUNKED_EXECUTION.md](LABEL_V6_GPT6_CHUNKED_EXECUTION.md).


---

# 3. Frozen validation / pseudo contract

## Gold58

- Official Gold: **58 studies**
- deterministic multilabel 3-Fold seed: **20261059**
- Fold sizes:
  - F0 = 20
  - F1 = 19
  - F2 = 19
- 모든 target에서 모든 Fold Positive / Negative coverage 존재
- manifest SHA256:
  `246f252a1ce4faaafa1b7d30e2c75cde6d79951cb780b0b33bf4f4dd12ad7e4b`

주의:

- Gold58은 작다.
- 수천분의 일 수준 차이는 구조적 개선으로 과장하지 않는다.
- Fold0는 많은 architecture search에 사용되어 **untouched validation이 아니다**.
- 현재는 split을 다시 만들지 않는다.

## Fold-specific Pseudo1000

Dataset:

`rsna-knee-r3d-3fold-pseudo-v1`

대표 root:

`/kaggle/input/datasets/yhlucas/rsna-knee-r3d-3fold-pseudo-v1`

Pseudo UID SHA256:

- F0: `e96b07e22aa0e4ac40281ce5709841dbadfa3cb61c882c6f1d10b8dccb4e233c`
- F1: `e3bcab2deb4e4284179fd369a72566e17083eb173750144c55f0c096dee15d98`
- F2: `d2c482ed154c141a9eb2f1ce83e5ca395c57eb30e5e3a331e319a427c333cc4d`

Sample trace SHA:

- F0: `d0c36a537f9868e6d6f484d5852f922a48d08df1ad7d35d9d241c751ed05f7a3`
- F1: `724f4b6e5e8604d8d860e42e4eb006a41419a5bb1c5e8738febf803c0624a096`
- F2: `1e4d28dfce05fb4e364599d59fdd9b691c14734889d2bd9c9d923772c40cb525`

---

# 4. Frozen R3D assets

## MedicalNet

Dataset:

`rsna-knee-r3d-medicalnet-pretrained-v1`

R34 SHA256:

`977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`

현재 R3D Main에서는 R50 / R101을 다시 비교하지 않는다.

## Full-FOV persistent cache

Dataset:

`rsna-knee-wide224-persistent-cache-v1`

실제 구조는 metadata와 volume shard가 분리되어 있다.

Metadata:

`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d06a_metadata_bundle/series_index.csv`

Volume root:

`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d06a_all_series_d24_96_v1/`

규모:

- 4,407 studies
- 24,371 series
- 819,078 slices
- 48 shards
- decode failure 0

중요:

R3D-06A raw `series_index.csv`에는
`plane_rank` / `selection_order`가 원래 저장되어 있지 않다.

기존 ALL policy와 동일하게 런타임에서 재구성한다.

~~~text
plane order:
Sagittal → Coronal → Axial

rank =
4 × Fluid_Sensitive × Fat_Suppression
+ 2 × Fluid_Sensitive
+ Fat_Suppression

tie-break:
SeriesInstanceUID ascending
~~~

그 뒤 study/plane별 `plane_rank`,
study별 `selection_order`를 생성한다.

## 현재 Crop130 cache

**R3D-11CACHE 완료/PASS**: 1,446 studies / 8,027 series / 32 float16 shards, 약 3.31 GiB. 기존 cache 통합, raw decode 0.

- 현재 mount: `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d11cache`
- volume/index: `crop130_d24_96/`; Gold와 fold pseudo: `manifests/`.
- Index SHA256: `114bc191102849cc5df8b3f45c3a2b6361446d3e190f5315e13cdf6d002d1ef4`.
- Gold58와 3fold pseudo scope coverage PASS. 최종 4,407명 전체 cache는 아니다.

**R3D-12CACHE Full4407 완료/PASS — 2026-10-08**.

- 전체 **4,407 studies / 24,371 unique series**.
- 기존 R3D-11CACHE **8,027 series 재사용** + 누락 **16,344 series 신규 생성**.
- ALL usable Series / Crop130 / interpolated D24×96×96 / float16, 총 **160 shards / 10,780,971,008 bytes (~10.04 GiB)**.
- raw decode failures **0**.
- full Study/Series metadata parity PASS.
- 기존 shard SHA equality PASS / 신규 shard readback PASS.
- 기존 Crop130 12-series raw rebuild exact parity PASS (max abs 0).
- runtime **479.195 min (~7h59m)**.
- `series_index.csv` SHA256: `e72c9238c97e0957bb7fccee91489d23847519dd1aaf01e40620411875abe217`.
- `shard_manifest.csv` SHA256: `bf4a008de5fbf9a239066524b38d0b0632891b83ff2781bde07538ff75bd44a0`.
- audit ZIP SHA256: `73d6b93d678f6922cc72b8103961fc6a7baa67cd8fe41f740709ebbf8c69e39c`.
- `study_roles.csv`: report-only train 4,349 / Gold validation 58 exact.
- 학습용 artifact는 audit ZIP이 아니라 `r3d12cache_full/` 전체 Dataset이다.
- **캐시 축은 종료. 재생성하지 않는다.**


---

# 5. Series / geometry 연구의 최종 결정

## Series policy

3-Fold mean Macro AUROC:

- P2: 0.573140
- P3: 0.589716
- **ALL: 0.596226**

결론:

- **ALL 고정**
- P4 / max-N 추가 search 없음

## Physical crop

Crop130 3-Fold confirmation:

| Fold | Full-FOV AUROC | Crop130 AUROC | ΔAUROC |
|---|---:|---:|---:|
| F0 | 0.617594 | 0.622257 | +0.004663 |
| F1 | 0.548407 | 0.542584 | -0.005823 |
| F2 | 0.622678 | 0.656090 | +0.033412 |

3-Fold mean:

- Full-FOV AUROC: **0.596226**
- Crop130 AUROC: **0.606977**
- mean ΔAUROC: **+0.010751**
- mean ΔAUPRC: **+0.003722**

결론:

- **Crop130 채택**
- fold heterogeneity는 있지만 primary AUROC 평균 개선 크기가 의미 있음

## 기각된 geometry/input

추가 탐색하지 않는다.

- Crop150
- Full-FOV 128×128
- simple D32 interpolation
- REAL32 nearest actual-slice
- REAL24 nearest actual-slice
- Full/Crop Dual-FOV feature-token fusion
- Mixed3 Full/Crop/Dual training

---

# 6. R3D-08 / 09 / 10 핵심 결과

## R3D-08C — REAL24 최종

3-Fold mean delta:

- AUROC **+0.000405**
- AUPRC **+0.000842**

자동 sign-only rule은 ADOPT였지만 실제 판정:

- **KEEP interpolated D24**
- gain이 noise 수준
- Fold1/Fold2 AUROC 하락

## R3D-09AB — Crop130 confirmation

3-Fold mean delta:

- AUROC **+0.010751**
- AUPRC **+0.003722**

판정:

- **ADOPT Crop130**
- Main input freeze

## R3D-10AB — Dual-FOV screen

Fold0 frozen:

- Full-FOV: **0.617594 / 0.540314**
- Crop130: **0.622257 / 0.508100**

Always Dual:

- AUROC **0.609809**
- AUPRC **0.494292**
- vs Crop130 ΔAUROC **-0.012448**

Mixed3:

- training modes:
  - Full-only 621
  - Crop-only 645
  - Dual 654
- best Dual AUROC **0.610704**
- best Dual AUPRC **0.483695**
- same checkpoint Full-only AUROC **0.612836**
- Crop-only AUROC **0.604505**
- probability avg AUROC **0.607573**

판정:

- **Dual-FOV / Mixed3 기각**
- Fold1/Fold2 confirmation 없음
- Main R3D = Crop130 single-view 유지

R3D-10 result ZIP SHA256:

`da5dbf79b88bbe4c9d8f1537c322cdc0b761356c70ab6d27d6df2bedee52fbe6`

---

# 7. Target-specific Series 상태

## Medial Meniscus

R3D-06H Fold0 paired binary specialist:

- P2: 0.677083 / 0.591098
- Sag1-only: **0.729167 / 0.756302**
- ΔAUROC **+0.052083**
- ΔAUPRC **+0.165204**

강한 신호다.

R3D-11 재확인은 완료했으며 위 결과가 우선한다. 과거 06H 참고:

- 06H는 현재 final Main input인 Crop130 이전 실험
- visible 06H implementation에는 canonical R34 naming과 다른 부분이 있어
  최종 specialist 근거로 그대로 쓰지 않는다
- Canonical R34 + Crop130 재확인은 R3D-11에서 완료했고 최종 채택은 보류했다.

## Synovitis

R3D-06H:

- P2: **0.680000 / 0.757973**
- Sag1-only: 0.590000 / 0.583247

결론:

- **Sag1-only hard routing 기각**
- 다시 열지 않는다

---

# 8. R3D-11 검토 완료

상세 수치와 검토는 이 문서 2절 및 EXPERIMENT_HISTORY.md 참조. 세 fold 개선이지만 최종 SAG1 채택은 보류.

# 9. 최종 실행 방향

## 확정된 최종 학습 방향

- **단일 Main R3D 모델**, 3-fold 최종 학습 아님. 기존 3-fold는 구조 비교용이었다.
- 학습 범위: **report-only 4,349 studies 전체**. 검증: **공식 Gold58 전원**, 학습에서 제외.
- 신규 라벨에서 supervision이 전혀 없는 study는 손실에 기여할 수 없다. 실제 유효 supervision 수는 audit 후 별도로 기록한다.
- Main: ALL → Crop130 → interpolated D24×96×96 → MedicalNet R34 → GLOB + metadata → Transformer/shared CLS → 12 heads.
- Search best.pt를 이어 학습하지 않고 MedicalNet pretrained에서 새로 시작한다.
- Epoch은 전체 학습 목록 순회를 기준으로 한다. 192 draws/epoch search budget을 최종 학습에 그대로 적용하지 않는다.
- Epoch 종료 시 Gold58 12-target Macro AUROC 우선, Macro AUPRC tie-break로 best.pt 선정. Epoch 수/compute budget/unknown mask 및 loss 정규화의 구체 구현은 아직 확정 전.
- Gold58은 이미 반복 탐색에 사용되었으므로 untouched test가 아니다.
- 먼저 standalone R3D Public LB 확인, 이후 Exp57(0.918)과 ensemble 상보성 검토. SAG1은 보류 후보이며 자동 추가하지 않는다.

## 바로 다음 작업

1. 원본 report 기반 라벨 감사/재구축: 공식 target 정의 확인 → 근거 문장과 상태를 보존하는 소규모 pilot → 애매한 사례 사용자 리뷰.
2. `positive / negative / uncertain / not-mentioned / insufficient`를 구분. 언급 없음·불완전 report를 자동 음성으로 만들지 않는다. LLM 자기 확신을 calibrated probability로 취급하지 않는다.
3. 기존 V4 full-data routing은 CommonGold57을 이용해 reader/target 정책을 골랐다. 이를 그대로 학습하고 Gold58을 독립 검증이라 부르지 않는다. 새 라벨 정책은 Gold 결과에 맞춰 조정하지 않는다.
4. 병행한 R3D-12CACHE 완료 audit 확인 후 새 라벨 manifest, supervision coverage와 최종 loss/budget 확정.
5. 단일 Main full-data 학습 → standalone 제출 → 필요 시 Exp57 blend 평가.

라벨 재생성 자체는 아직 시작하지 않았다. 현재 원본 report/V4 master/method/old audit 자료는 확보했으며 원래 추출 prompt·근거 문장은 제공 자료에 없다.


---

# 10. 더 이상 하지 않는 작업

근거 없이 다시 열지 않는다.

- R50 / R101
- GLOB vs coarse spatial-token 재비교
- anatomy mask current fusion
- lower backbone LR / frozen backbone
- P2 / P3 / Series cap micro-search
- Synovitis Sag1-only
- Crop 130/140/150 micro-search
- Full-FOV 128/160/192/224 resolution search
- simple D32/D40/D48 interpolation
- REAL24 / REAL32 nearest-slice
- R3D-10 Dual-FOV Fold1/2 confirmation

새 evidence가 생기기 전까지 위 항목은 closed다.

---

# 11. Kaggle 운영 핵심

- 새로운 image/cache 생성 = **CPU-only Notebook**
- GPU Notebook = **training-only**
- Save & Run All 전제
- 전체 `/kaggle/input` recursive search 금지
- exact mounted path 우선
- 같은 Dataset의 서로 다른 Version 동시 mount에 의존하지 않음
- mount 단계에서 `Output 0 B / ERRORED_MOUNTING_DATASET`이면 Python code error로 해석하지 않음
- 실패 시 재학습 전에 기존 artifact가 완성됐는지 먼저 확인
- T4×2에서 독립 Fold/variant를 GPU0/GPU1 subprocess로 병렬 실행 가능
- 한 계정에서 input을 공유할 수 있으면 굳이 Account A/B 두 세션으로 분리하지 않아도 됨

---

# 12. 문서 우선순위

새 채팅에서 판단이 충돌하면 다음 순서를 따른다.

1. **CURRENT_HANDOFF.md**
2. **CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md**
3. **3D_RESNET_EXPERIMENT_PLAN.md**
4. **EXPERIMENT_HISTORY.md**
5. AI_AGENT_KAGGLE_NOTEBOOK_RULES.md — 실행 규칙
6. README 및 과거 Specialist 문서 — historical reference

과거 문서에
"NEXT", "현재 다음", "진행 중"이 남아 있어도
이 문서의 2026-10-08 상태와 충돌하면 **과거 기록으로만 해석**한다.

