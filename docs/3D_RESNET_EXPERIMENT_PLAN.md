# RSNA Knee — 3D ResNet Experiment Plan

최종 업데이트: **2026-10-08**

상태: **R3D-10AB 완료 / Dual-FOV 기각 / Crop130 single-view Main 유지**

이 문서는 **앞으로 무엇을 할지**를 기록한다.
완료 결과는 [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md)에 기록하고,
현재 기준점은 [CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md](CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md)를 따른다.

Kaggle Notebook 작성/복구 규칙:
[AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)

---

# 1. 최종 목표

기존 Exp57 Public LB **0.918**을 기준점으로 유지하면서,
독립적인 3D MRI 계보의 실제 hidden-test 성능과 Exp57과의 상보성을 확인한다.

R3D의 성공 기준은 내부 Gold58 점수만이 아니다.

최종적으로 확인해야 할 것은:

1. R3D standalone Public LB
2. Exp57 대비 차이
3. Exp57 + R3D ensemble의 net gain
4. Medial Meniscus Sag1 specialist가 target-specific 보완에 실제 기여하는지

---

# 2. 현재 확정 Main R3D

~~~text
ALL Series
→ 130 mm physical center crop
→ interpolated D24 × 96 × 96
→ MedicalNet R34
→ GLOB token / series
→ metadata embedding
→ Transformer + shared CLS
→ 12 independent sigmoid heads
~~~

고정:

- Backbone: **MedicalNet R34**
- R50 / R101 재비교 없음
- Full fine-tuning
- pure FP32
- BN running stats frozen
- Series = **ALL**
- Crop = **130 mm**
- Depth = **interpolated D24**
- In-plane = **96×96**
- Representation = **GLOB**
- Anatomy mask = **OFF**
- Backbone LR = **1e-5**
- New-layer LR = **5e-5**
- WD = **1e-4**
- Transformer:
  - d_model 512
  - 2 layers
  - 8 heads
  - FFN 2048
  - dropout 0.10
  - Pre-LN
  - learnable CLS

현재 구조를 다시 흔드는 micro-search는 중단한다.

---

# 3. 완료된 decision gates

## Backbone

- R34 pooled Macro AUROC: 0.567267
- R50: 0.533494
- R101: 0.510364
- **R34 selected**

## Representation

- GLOB: 0.601827
- SPT27: 0.595809
- SPT48: 0.590426
- **GLOB selected**

## Backbone LR

- 1e-5: 0.601827
- 5e-6: 0.591677
- 3e-6: 0.582062
- frozen: 0.579953
- **1e-5 selected**

## Anatomy mask

- MASK_ON: 0.601827
- MASK_OFF: 0.609698
- **MASK_OFF selected**

## Series

3-Fold mean AUROC:
- P2 0.573140
- P3 0.589716
- ALL **0.596226**
- **ALL selected**

## Physical FOV

Crop130 3-Fold:
- mean ΔAUROC vs Full = **+0.010751**
- mean ΔAUPRC = **+0.003722**
- **Crop130 selected**

## Depth / detail

Rejected:
- R128
- simple D32 interpolation
- REAL24 nearest actual-slice
- REAL32 nearest actual-slice

Depth representation:
- **interpolated D24 유지**

## Dual-FOV

R3D-10AB Fold0:
- Frozen Crop130 0.622257
- Frozen Full 0.617594
- Always Dual 0.609809
- Mixed3 Dual 0.610704

결론:
- **Dual-FOV current fusion reject**
- Fold1/Fold2 confirmation 없음
- Crop130 single-view 유지

---

# 4. Cache 실행 상태

## 현재 Crop130 cache

**R3D-11CACHE 완료/PASS**: 1,446 studies / 8,027 series / 32 float16 shards, 약 3.31 GiB. 기존 cache 통합, raw decode 0.

- 현재 mount: `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d11cache`
- volume/index: `crop130_d24_96/`; Gold와 fold pseudo: `manifests/`.
- Index SHA256: `114bc191102849cc5df8b3f45c3a2b6361446d3e190f5315e13cdf6d002d1ef4`.
- Gold58와 3fold pseudo scope coverage PASS. 최종 4,407명 전체 cache는 아니다.

**R3D-12CACHE Full4407 완료/PASS — 2026-10-08**.

- 4,407 studies / 24,371 unique series.
- reused 8,027 + new 16,344.
- ALL + Crop130 + interpolated D24×96×96 + float16.
- 160 shards / 10,780,971,008 bytes (~10.04 GiB).
- decode failure 0.
- metadata parity / reused shard SHA / new shard readback / 12-series Crop130 exact parity 모두 PASS.
- runtime 479.195 min.
- series index SHA256 `e72c9238c97e0957bb7fccee91489d23847519dd1aaf01e40620411875abe217`.
- shard manifest SHA256 `bf4a008de5fbf9a239066524b38d0b0632891b83ff2781bde07538ff75bd44a0`.
- audit ZIP SHA256 `73d6b93d678f6922cc72b8103961fc6a7baa67cd8fe41f740709ebbf8c69e39c`.
- report-only 4,349 / Gold58 role split exact.
- **cache generation closed; do not rerun.**


---

# 5. R3D-11 — 완료/PASS, 최종 채택 보류

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


---

# 6. R3D-12 — 라벨 및 최종 학습 정책

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
2. Qwen3-8B / Mistral-Nemo-12B Kaggle GPU reader plan은 **폐기/미실행**. 현재 실행 계약: [LABEL_V6_SOL_CHUNKED_EXECUTION.md](LABEL_V6_SOL_CHUNKED_EXECUTION.md).
3. report-only 4,349 studies를 원본 `train.csv` 행 순서 그대로 **87 chunks**로 고정:
   - Chunk 001–086 = 50 studies / 600 decisions
   - Chunk 087 = 49 studies / 588 decisions
   - 총 52,188 decisions
   - report-only UID manifest SHA256 = `e675c1cfb8e88b3ec00af4fcba77bfb010e324e3a3473b04089da651af630a94`
   - chunk manifest SHA256 = `66179ef419094e6204ea3c39c4696d1da68463320bc9c58168e96d993e5a0cd5`
4. primary reader는 **GPT-5.6 Sol**. 기본 최대 5 chunks/chat으로 18개 chat에 배치하되, context 품질이 우려되면 더 일찍 끊고 최신 cumulative Master/Handoff로 새 chat에서 계속한다.
5. 각 chunk는 모든 study의 12 targets를 직접 판정하고 exact report evidence + Unicode offset + report SHA를 보존한다. 이전 completed chunk는 integrity defect가 없으면 재판정하지 않는다.
6. 4,349 완료 후 4,349 studies / 52,188 decisions 전체 contract, target별 5-state distribution / supervised coverage / positive prevalence / language·script / duplicate consistency를 감사한다.
7. HIGH-review / inference-used / contradiction / ambiguity / distribution anomaly를 **GPT-6 Astra가 원본 report + frozen policy로 독립 재판정**하고 최종 adjudication 후 canonical LABEL-V6를 freeze한다.
8. canonical release 후에만 target별 N_pos/N_neg/mask coverage로 class weight와 **masked per-target BCE → 12-target macro average** loss를 확정한다.
9. canonical label release → R3D-13 single Main full-data → standalone Public LB → 필요 시 Exp57 complementary blend. 동일 canonical manifest를 Exp57 old-vs-new label 비교에도 사용한다.

중요: 공식 Gold는 MRI image-derived consensus label이다. 새 라벨은 공식 영상 판정 기준을 최대한 모사하는 report-derived supervision이며 새로운 ground truth가 아니다.

---

# 8. R3D-14 — Hidden-Test Standalone Submission

Exp57과 섞기 전에 R3D standalone을 먼저 제출한다.

목적:

- R3D 자체 hidden-test generalization 측정
- internal Gold58 ↔ Public LB gap 확인
- Exp57 complementarity와 standalone 성능을 분리

기본 inference:

~~~text
Hidden Study
→ all usable Series
→ 130 mm physical crop
→ interpolated D24×96×96
→ single final R34
→ 12-target probabilities
→ submission.csv
~~~

최종 단일 모델 best checkpoint를 사용한다.

---

# 9. R3D-15 — Final Ensemble

입력 후보:

1. **Exp57** — Public LB 0.918
2. **R3D final single model**
3. **Medial Meniscus Sag1 specialist** — 현재 보류; pipeline PASS는 채택 PASS가 아님

Exp57은:

- 3-Fold B3A
- 3-Fold Full-MRI Direct
- 70:30

으로 이미 완성된 강한 baseline이다.

R3D는 Exp57과 architecture / representation이 다르므로
standalone이 약간 낮아도 ensemble value가 있을 수 있다.

실행 전 가능하면:

- prediction correlation
- target별 delta
- ranking disagreement
- especially weak target behavior

를 먼저 확인한다.

Public LB에 ratio를 반복적으로 맞추는 식의 micro-search는 하지 않는다.

---

# 10. Closed experiments

새 evidence가 생기기 전에는 재오픈하지 않는다.

- R50 / R101
- spatial token SPT27 / SPT48
- current anatomy mask fusion
- lower LR / frozen R34
- Series cap P2/P3/P4
- Synovitis Sag1-only
- Crop150 / 140 mm micro-search
- R128 이상 단순 resolution search
- simple D32+ interpolation
- REAL24 / REAL32 nearest actual-slice
- Full+Crop Always Dual
- Full/Crop Mixed3
- R3D-10AB Fold1/Fold2

---

# 11. Resource execution plan

## CPU lane

사용:
- DICOM decode
- cache generation
- cache consolidation
- manifest / policy audit
- SHA / parity validation

금지:
- CPU preprocessing 때문에 T4를 예약해 두는 구조

## GPU lane

사용:
- training
- validation
- model inference

새 image/cache generation을 GPU notebook에 넣지 않는다.

## T4×2

한 Kaggle session에서 독립 lane을 병렬 실행할 수 있으면:

~~~text
GPU0 → experiment/fold lane 1
GPU1 → experiment/fold lane 2
~~~

subprocess + `CUDA_VISIBLE_DEVICES` 방식 사용 가능.

두 Kaggle 계정을 쓰는 것보다
같은 Input을 공유해야 하는 경우 한 계정 T4×2가 더 편하면
한 세션 병렬을 우선할 수 있다.

---

# 12. Experiment numbering going forward

- **R3D-11CACHE** — consolidated Crop130 3-Fold cache
- **R3D-11** — Medial Meniscus Sag1 canonical paired confirmation
- **R3D-12** — final-training data/budget decision
- **R3D-13** — final Main single model
- **R3D-14** — standalone hidden-test submission
- **R3D-15** — final Exp57 + R3D ensemble

번호는 실제 실행 결과에 따라 세부 suffix를 추가할 수 있으나,
새 채팅에서 임의로 과거 번호를 재사용하지 않는다.

