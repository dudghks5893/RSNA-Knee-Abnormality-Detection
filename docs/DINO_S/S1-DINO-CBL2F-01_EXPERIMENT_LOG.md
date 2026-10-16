## 2026-10-17 — Public LB 업데이트: S10+S8C 70:30 = 0.926 / DINOv2-Small = 0.899

### 새 Public LB 결과

- **S10 LAST 2F 70% + S8C Full-MRI Direct 2F 30%**
  - Public LB: **0.926**
  - 이전 S10 standalone: **0.923**
  - 이전 S8C standalone: **0.923**
  - Blend 개선: **+0.003**
  - 구조:
    ```text
    P_S10 = 0.5 * S10_F0_last + 0.5 * S10_F1_last
    P_S8C_DIRECT = 0.5 * S8C_F0_direct + 0.5 * S8C_F1_direct
    P_FINAL = 0.70 * P_S10 + 0.30 * P_S8C_DIRECT
    ```
  - 해석: S8C가 selector와 Full-MRI direct predictor를 동시에 담당하고, S8C가 고른 Top18을 S10이 정밀 재판독하는 Exp57-style 구조가 현재 계보에서도 실제 LB 개선으로 확인됨.
  - 현재 프로젝트 최고 Public LB: **0.926**.

- **DINOv2-Small V4 Broad 2-Fold standalone**
  - Public LB: **0.899**
  - Gold58 pooled DEV Macro AUROC: **0.868824**
  - 비교 대상인 Stage1 V4 Broad DINOv2-Base Public LB **0.910** 대비 **-0.011**.
  - 결론: 현재 데이터/학습 계약에서 Small은 Base보다 명확히 낮음. Small vs Base 재실험 우선순위는 낮추고, S11은 Base 계보를 유지.

### 현재 Public LB 순위

| 모델/제출 | Public LB |
|---|---:|
| **S10 LAST 70% + S8C Direct 30%** | **0.926** |
| S8B Window-Attn MIL | 0.923 |
| S8C Window+Series-Attn MIL | 0.923 |
| S10 Top18 Strict FT last 2F | 0.923 |
| S8A Mean MIL | 0.918 |
| Stage1 V4 Strict FT last | 0.914 |
| Stage1 V4 Broad Base | 0.910 |
| DINOv2-Small V4 Broad 2F | 0.899 |
| V54A Stage1 | 0.873 |

### 다음 결정

- 현재 최종 기준 제출은 **0.926 hybrid**.
- S11 Multi-View는 이 0.926을 넘어서는 것이 목표.
- S11 standalone이 개선되면 다음 1순위 hybrid는 `70% S11 + 30% S8C Direct`.
- Small 계보는 당분간 중단. Base에서 데이터/FOV/augmentation 개선에 집중.

---

## 2026-10-17 — S10 Public LB 0.923 확정 · Small DEV 결과 · S10+S8C 70:30 제출 준비 · S11 Multi-View 계획

### 확인된 결과

- **S10 `S10-BASE-TOP18-STRICT-FT-V1`**
  - Stage1-B Fold0/1 `last.pt`에서 시작, S9 S8C-only selector의 고정 Top18로 V4 Strict 추가 FT.
  - Gold58 pooled epoch0/reference Macro AUROC **0.894507**.
  - Fold별 epoch0 reference: Fold0 **0.923770**, Fold1 **0.882726**.
  - 실제 학습 last(epoch2) pooled Macro AUROC **0.893824**로 reference 대비 **-0.000683**.
  - last checkpoint SHA: Fold0 `e30d268a039dbf64a6ba082d4c85cdb1e1ed2090c70e59d9165b3cfe83083908`, Fold1 `02232b0bdcf8062564d04feda43f9fe6ea09edd1553a7025caaf19ac701ee1b3`.
  - **사용자 보고 Public LB: 0.923.**
  - 결론: Gold58의 미세 하락만으로 last를 실패 처리하면 안 됨. Stage1-B에서도 last의 local val이 더 낮았으나 Public LB가 더 높았던 전례가 있으며, S10도 실제 Public LB 0.923으로 확인됨.

- **DINOv2-Small V4 Broad 2-Fold `S1-DINO-SMALL-V4-2F-V1`**
  - Fold0 best epoch6 Macro AUROC **0.878770**.
  - Fold1 best epoch10 Macro AUROC **0.862916**.
  - Gold58 pooled DEV Macro AUROC **0.868824**, Macro AUPRC **0.797062**.
  - checkpoint: `/kaggle/input/datasets/yhlucas/rsna-knee-checkpoint-models/S1_DINO_SMALL_V4_DUALFOLD/fold0/best.pt`, `fold1/best.pt`.
  - standalone Public LB는 아직 본 기록 시점에 **미확정**. DEV만으로 Base 대비 최종 우열을 확정하지 않음.

- 현재 사용자 보고 Public LB:
  - Stage1 V4 Broad Base **0.910**
  - Stage1 Broad→V4 Strict FT **0.914**
  - S8A **0.918**
  - S8B **0.923**
  - S8C **0.923**
  - V54A Stage1 **0.873**
  - **S10 Top18 last 2F 0.923**
  - Historical Exp57 70:30 **0.918**

### Final blend 현재 판단

과거 Exp57의 최고 hybrid 구조는 **Top-K final branch 70% + 같은 selector MIL의 Full-MRI direct branch 30%**였다. 따라서 현재 계보에서 구조적으로 가장 직접 대응되는 첫 blend는:

```text
P_S10 = mean(sigmoid(S10 Fold0 last), sigmoid(S10 Fold1 last))
P_S8C_DIRECT = mean(sigmoid(S8C Fold0 direct), sigmoid(S8C Fold1 direct))
P_FINAL = 0.70 * P_S10 + 0.30 * P_S8C_DIRECT
```

S8C는 이 제출에서 **Top18 selector + Full-MRI direct predictor** 두 역할을 함께 수행한다. S8B는 이 첫 제출에는 사용하지 않는다. `S10_LAST_70_S8C_DIRECT_30_2F_LB_SUBMISSION_V1.ipynb` 준비 완료, Public LB **대기**.

### S11 계획 — `S11-TOP18-MULTIVIEW-AUG-FT-V1`

목적은 S10의 Top18 선택/라벨/모델 계보를 유지하면서 **선택된 같은 center를 서로 다른 physical FOV와 resolution으로 표현**해 질환별로 필요한 공간 범위를 다르게 제공하는 것. 처음부터 재학습하지 않고 **S10 Fold0/1 last.pt에서 추가 FT**한다.

고정:
- S9 S8C-only V2 Top18 center.
- Fold0/1, V4 Strict + opposite Gold29, class balance/loss.
- DINOv2-Base shared weights, target attention/head 계열.
- 18 Window/Study.
- selector/label/Top-K는 변경하지 않음.

변경:
- 같은 Top18 center마다 3개 View 생성.
  - ANCHOR: 130mm / 224, **S10 기존 Native224 V3와 exact parity**. 기존 padding 정책까지 유지.
  - DETAIL: 110mm / 280. 원본 FOV가 110mm보다 작으면 가짜 padding을 만들지 않고 available FOV 전체를 사용 후 280 resize.
  - CONTEXT: 160mm / 224. 원본 FOV가 160mm보다 작으면 available FOV 전체를 사용 후 224 resize.
- DETAIL/CONTEXT는 requested FOV coverage를 기록. 기존 130mm/224 cache에서는 160mm 바깥 정보를 복원할 수 없으므로 **원본 DICOM에서 전용 S11 Top18 Multi-View cache를 새로 생성**.
- 세 View가 parameter를 따로 갖지 않고 **동일 DINOv2-Base weights를 공유**. View별 12 logits를 만든 뒤 target별 fixed routing weight로 logit 결합.
- learned router는 Gold58 과적합 위험 때문에 S11에서는 사용하지 않음.
- augmentation은 3-slice channel에 동일 transform을 적용. horizontal flip/Cutout/MixUp/strong blur 제외.
- Gold29는 진단값으로 저장하지만 **early-stop 판단을 강제하지 않음**. 2 epochs 고정 실행, epoch1/epoch2(last) 모두 저장.

Target routing prior (DETAIL / ANCHOR / CONTEXT):
- ACL 0.65 / 0.30 / 0.05
- MCL 0.05 / 0.30 / 0.65
- Medial Meniscus 0.60 / 0.35 / 0.05
- Lateral Meniscus 0.55 / 0.40 / 0.05
- Medial OA 0.65 / 0.30 / 0.05
- Lateral OA 0.60 / 0.35 / 0.05
- PF OA 0.50 / 0.40 / 0.10
- Effusion 0.05 / 0.30 / 0.65
- Synovitis 0.10 / 0.40 / 0.50
- Baker's 0.00 / 0.15 / 0.85
- Contusion 0.15 / 0.45 / 0.40
- Fracture 0.40 / 0.45 / 0.15

View별 augmentation prior:
- DETAIL: rot±4°, translate±2%, scale 0.98–1.02, gamma 0.96–1.04, gain±4%.
- ANCHOR: rot±6°, translate±3%, scale 0.96–1.04, gamma 0.94–1.06, gain±6%.
- CONTEXT: rot±8°, translate±4%, scale 0.94–1.06, gamma 0.92–1.08, gain±8%.
- 같은 3-slice Window의 세 channel에는 동일한 augmentation parameter 적용.
- seed는 UID/Series/center/view/epoch 기반 deterministic.

S11의 1차 질문은 “S8C가 고른 같은 Top18을 하나의 130mm/224 표현으로만 보는 것보다 target-specific multi-scale view + mild augmentation이 Public LB를 올리는가?”이다. Plane/sequence routing, Top-K 재선정, K32, learned gating은 S11에 섞지 않는다.

---
## 2026-10-16 — Stage1→Stage2→Top-K→Stage3→70:30 최종 파이프라인 설계 동결 (설계 결정 / 미실행 단계 포함)

사용자와 다음 DINO·S 계보를 **향후 기본 루트**로 확정했다. 이 항목은 실행 결과가 아니라 이후 실험을 같은 구조로 재현하기 위한 설계 결정이다.

1. **Stage1-A Broad 2-Fold DINO**: V4 Routed Broad + Gold29/29 2-Fold로 DINO를 task-tune. Study당 18개의 3-Slice Window, 기존 central 20–80% sampler 사용.
2. **Stage1-B High-confidence FT**: 각 Fold Stage1-A checkpoint에서 V4 Routed Strict 고신뢰 supervision으로 저 LR 추가 FT. 이후 Stage2의 feature extractor 및 Stage3 초기값으로 사용.
3. **Stage2 Full-MRI feature + MIL**: Stage1-B Fold별 encoder를 고정해 모든 valid center(1..n-2)를 특징으로 추출. Base 기준 4,407 Studies / 24,371 Series / 770,336 Windows. 이 특징으로 MIL 학습.
4. **Stage2 Predictor / Selector 역할 분리**: Public LB가 S8B=S8C=0.923인 현재 기준에서 **S8B(Window Attention→Series Mean)**를 단순한 최종 MIL predictor로, **S8C(Window Attention→Series Attention)**를 Full-MRI selector로 사용.
5. **Top-K selection**: S8C의 exact per-window target contribution을 이용해 전체 Window 순위를 만들고 diversity/NMS를 적용. Top18/24/32/48/64 nested manifest를 생성하되 최초 Stage3 실험은 **K=18**로 고정하여 기존 Stage1의 18 Window와 compute를 맞춘다.
6. **Stage3 Top-K FT**: Stage1-B Fold별 checkpoint에서 시작하여 Stage2가 고른 Top18 Window만 사용해 V4 Strict supervision으로 재-FT. 이후 K32 등은 Top18 개선 확인 후 별도 ablation.
7. **Final inference**: Fold 내부 확률을 먼저 50:50 평균한 뒤 **Stage3 probability 70% + Stage2 S8B MIL probability 30%**로 최종 제출. 첫 canonical blend는 target별 별도 weight나 logit blend를 사용하지 않는다.

**Selector 배포 정합성 수정:** 실제 Top-K 선택 점수에는 V4/Gold 정답 방향을 사용하지 않는다. Hidden Test에는 정답이 없으므로 selection은 label-free여야 한다. 기본 score는 S8C의
`series_attention × window_attention × |dot(projected_window, target_head_weight)|`
를 target별 Study 내 percentile로 정규화한 뒤 target max(동률 시 mean)를 사용한다. Train label은 selector 품질 진단에만 사용할 수 있고 최종 selection rule에는 넣지 않는다.

**현재 즉시 실행 우선순위:** 위 Top-K/Stage3 실험은 일단 보류. 다음 한 가지 실험은 **Stage1-A의 backbone만 DINOv2-Small로 바꾸는 통제 실험**이다. V4 Broad label, Gold58 split, 18-window sampler, loss, seed, optimizer/scheduler, max epoch, best-checkpoint 기준은 Base와 동일하게 유지한다. Small은 CLS384+PatchMean384=768-d이므로 입력 projection만 768→256으로 바뀐다. 물리 Study batch/Window microbatch는 속도 최적화를 위해 실측 benchmark로 선택하되 effective Study batch=4는 고정한다.

---
## 2026-10-16 — V54A 최적화 Stage1 DINO 2-Fold · Public LB 0.873 확정

**실험:** `S1-V54A-DINO-2F-OPT-V1` — 기존 Stage1 DINOv2-Base/Native224 V3/18 Window/Gold58 2-Fold 구조를 유지하고 V54A soft/mask/weight에 맞춘 directional soft-mass class balancing을 적용.

**학습 결과**
- Fold0: best epoch **5**, Gold29 Macro AUROC **0.845536**, 9 epochs, **246.18 min**, best SHA256 `786b5851cd57bacfe6bad1f94043f68ac477aadacf870bd51d742f12ccdd4743`.
- Fold1: best epoch **9**, Gold29 Macro AUROC **0.839794**, 12 epochs, **302.72 min**, best SHA256 `73a9006f24c1b84e993ae39a4d46e36a8da8b586f698c1d4a6ff6a1e248317ad`.
- Gold58 pooled DEV Macro AUROC **0.843255**, Macro AUPRC **0.772313**.
- 기존 V4 Broad Stage1 Gold58 pooled Macro AUROC **0.871112** 대비 **-0.027857**. 따라서 Gold58 개발 지표만 보면 V54A가 V4 Broad보다 낮음. 다만 Gold58는 반복 DEV이므로 Public LB 확인 전 최종 판단하지 않음.

**속도 개선**
- 자동 benchmark가 두 Fold 모두 `study_batch=4 / window_microbatch=72 / activation_checkpoint=False / AdamW_fused`를 선택.
- Fold0 128-Study profile 예상 12 epoch **5.83h**, Fold1 **5.76h**.
- 실제 wall time은 두 Fold 병렬 실행에서 느린 Fold1 기준 약 **302.7분(5.05h)**. 기존 V4 Stage1 약 629–631분 대비 대략 절반 수준으로 단축.
- Peak allocated VRAM 약 **8.42 GiB**.

**Checkpoint Dataset**
- Fold0: `/kaggle/input/datasets/woniyeon/rsna-knee-checkpoint-models/S1_V54A_DINO_DUALFOLD/fold0/best.pt`
- Fold1: `/kaggle/input/datasets/woniyeon/rsna-knee-checkpoint-models/S1_V54A_DINO_DUALFOLD/fold1/best.pt`
- 제출 Notebook: `S1_V54A_DINO_2FOLD_PUBLIC_LB_SUBMIT_V1.ipynb`.
- **사용자 제공 Kaggle Public LB: 0.873**.
- 비교: V4 Broad Stage1 **0.910** 대비 **-0.037**, V4 Broad→Strict FT **0.914** 대비 **-0.041**.
- 결론: V54A 맞춤 Stage1 단독 모델은 현재 V4 계열을 대체하지 못함. V54A checkpoint는 실험 기록으로 보존.

---
## 2026-10-16 — S8C Kaggle Public LB 확정: 0.923

**사용자 제공 Kaggle 제출 결과:** `S8C-HIER-ATTN-LB-2F-V1` Public LB **0.923**.

- S8C 구조: 질환별 Window Attention → **질환별 Series Attention** → 질환별 Linear.
- Gold58 pooled diagnostic Macro AUROC: **0.875728**.
- S8B Gold58 diagnostic: **0.877599**. S8C는 개발 지표에서 **-0.001871** 낮았음.
- Public LB: **S8B 0.923 = S8C 0.923**. Series Attention 추가로 Public LB 개선은 확인되지 않음.
- S8C는 S8B보다 구조가 복잡하지만 동일한 Public LB를 기록했으므로, **현 시점 기준 Public-LB 대표 모델은 더 단순한 S8B 0.923을 유지**하고 S8C는 동률 실험으로 보존.
- 중요한 관찰: Gold58에서는 S8C가 소폭 하락했지만 Public LB에서는 S8B와 동률. Gold58 반복 DEV와 Public LB의 순위가 일치하지 않을 수 있다는 기존 관찰을 다시 확인.
- 다음 연구 우선순위는 MIL 구조 추가 확장이 아니라 **V54A 맞춤 Stage1 DINO 2-Fold 학습**으로 이동.

---
## 2026-10-16 — S8C Hierarchical Target Attention MIL 학습 완료 · Public LB 제출 대기

**구조:** S8B의 질환별 Window Attention → Series Mean에서 Series pooling만 변경해 **질환별 Window Attention → 질환별 Series Attention → 질환별 Linear**로 확장. S7 Fold0/1 Full-MRI 1536-d feature cache, V4 Routed Strict supervision, Gold58 29/29, AdamW LR 2e-4, weight decay 0.01, 8 epoch, seed 등은 S8B 조건을 유지. 새 `series_query`는 0으로 초기화해 학습 시작 시 Series Mean과 동일하도록 parity gate를 통과함.

**학습/검증 결과**
- Fold0 best: epoch 1, Gold29 Macro AUROC **0.915085**
- Fold1 best: epoch 3, Gold29 Macro AUROC **0.863470**
- Gold58 pooled MIL diagnostic Macro AUROC: **0.875728**
- S8B Gold58 diagnostic 0.877599 대비 **-0.001871**
- S8B Public LB 0.923은 비교 기준이며 S8C Public LB는 아직 제출 전.
- Gold58 per-target에서 개선: Lateral Meniscus +0.024845, PF OA +0.005148, Medial OA +0.003100, ACL +0.001225. 하락이 큰 target: Effusion -0.011180, Fracture -0.011111, Synovitis -0.009558, MCL -0.009070.
- Series Attention은 median Series=5에서 평균 max weight가 대체로 약 0.20~0.26, normalized entropy 약 0.972~0.998로 **대체로 uniform mean에 가까움**. 따라서 Gold58 기준으로는 Series Attention이 강하게 특정 Series를 선택한 증거가 약함.
- 다만 S8A/S8B에서도 Gold58 순위와 Public LB 순위가 뒤집힌 전례가 있어, S8C는 한 번 Public LB 제출로 확인한다.

**Checkpoint**
- Fold0 `best.pt` SHA256: `1b16bd88d3a5a13d93bbfb45ac12561e516a17cbf8d34fab50204bf09a67cfa8`
- Fold1 `best.pt` SHA256: `506e73b7462195b3091b60508aa8781200f1d72c8c0469d8cea57a8b11771155`
- Kaggle Dataset: `/kaggle/input/datasets/yhlucas/s8c-hier-attn-mil/fold{0,1}/best.pt`
- 제출 Notebook 준비: `S8C_HIER_ATTN_2FOLD_PUBLIC_LB_SUBMIT_V1.ipynb` (Kaggle 실행 전)

---
# S1-DINO/S1FT02/S7/S8 — 최신 실험 결과 (2026-10-16)

**사용자 보고 Public LB:** S8A Mean MIL **0.918**, S8B disease-specific Window Attention MIL **0.923**. S8B가 현재 프로젝트 최고 기록. 기존 B2 Full-MRI 0.904 대비 S8B +0.019, 과거 Exp57 0.918 대비 +0.005.

**Stage1과 S7의 입력 범위:** Stage1 Strict-FT DINO는 Fold별 Train 4,349 Pseudo+Gold29, Study당 18개의 3-Slice Window를 모든 이용 가능 Series에 분배해 중심 20~80%에서 Fine-tuning. S7은 *해당 encoder를 고정*해 Train4,349+Gold58=4,407 Studies, 24,371 Series의 **770,336개 전체 유효 Window 특징**을 Fold별 추출했다. S8 MIL이 이 전체 특징으로 학습되었다는 것이 Stage1 인코더를 전체 Slice로 재학습했다는 뜻은 아니다.

**Gold58 개발 Macro:** S8A 0.894883, S8B 0.877599. Gold와 Public LB 우세가 뒤집혔으며 Gold58는 반복 DEV이므로 독립 시험 성능을 주장하지 않는다.

### 기존 공통 History에서 이관한 S8 실제 제출·체크포인트 기록

## 2026-10-16 — S8 Full-MRI MIL A/B Kaggle Public LB 0.918 / 0.923

**결과 상태 — 사용자 제공 Kaggle 제출 점수:** S8A Mean MIL **Public LB 0.918**, S8B 질환별 Window Attention MIL **Public LB 0.923**. 사용자 보고값을 기록하며 원격 제출 ID/Private LB는 별도 확인되지 않았다. S8B가 현재 이 프로젝트에서 확인된 최고 Public LB다. 기존 B2 Full-MRI Hierarchical MIL 0.904 대비 각각 +0.014 / +0.019, 이전 최고 Exp57 0.918 대비 S8B +0.005.

| 항목 | S8A Mean | S8B Attention |
|---|---:|---:|
| **Kaggle Public LB (사용자 보고)** | **0.918** | **0.923** |
| Gold58 pooled diagnostic macro AUROC (개발 검증) | 0.894883 | 0.877599 |
| MIL Fold0 best epoch | 3 | 1 |
| MIL Fold1 best epoch | 3 | 3 |
| V3 공개 3 Studies / 15 Series 실행 | SUBMISSION_SUCCESS | SUBMISSION_SUCCESS |
| V3 공개 실행 Series 실패 / Decode 실패 / fallback | 0 / 0 / 0 | 0 / 0 / 0 |
| V3 공개 Test submission SHA256 | `2658128987db319fb2bb376235e74a74240bc4a5d742223ffc1a10286052ef06` | `b7aeba1b24f91f74e107d95e61d26dc5a7294e41f02e7953c492b2352c576c55` |

**입력 및 모델 계약:** A/B 모두 130mm Native224 V3 전처리, 모든 정상 Series의 center 1..n−2에서 3-Slice Window, Strict FT DINOv2-Base Fold0/1별 CLS768+PatchMean768(1536-d) 특징 추출, Fold별 별도 S8 MIL 예측 sigmoid 후 2-Fold 확률 평균. **A**는 Window Mean → Series Mean; **B**는 질환별 Window Attention → Series Mean. B에 질환별 Series Attention은 **아직 없음**. V3 개선은 DICOM fallback, Series streaming, sample_submission 순서 고정 및 2GPU 병렬 특징 추출에 관한 것으로 정상 공개 Test 예측 CSV의 SHA는 V2와 동일했다. V1/V2 Hidden 재실행은 `Notebook Threw Exception`; 실제 비공개 traceback이 없으므로 실패 원인 단정 금지. V3의 Kaggle Public LB 수신은 실제 제출 점수 확인을 뜻하지만 Hidden 상세 처리 통계는 확인하지 못했다.

**Stage1 vs S7의 Slice 범위 구분:** Strict FT 원 모델은 Fold별 학습 Study 4,378(Train 4,349 + Gold train 29; 나머지 Gold29 validation)에 대해 **Study당 18 Window, Series마다 최소 1개, 중심 20–80% 후보를 Epoch별 변화시키는 샘플러**로 Full Fine-tuning. 모든 슬라이스로 DINO를 fine-tune하지는 않았다. 이후 S7은 동일한 Fold별 Strict-FT Encoder의 가중치를 **고정**하고 Train4,349+Gold58 = 4,407 Studies, 24,371 Series, 원본 819,078 Slice에 대해 **770,336개 전체 유효 3-Slice Window 특징을 Fold별로 추출**했다. 따라서 S8이 전체 MRI 특징으로 MIL을 학습했어도 DINO의 Stage1 학습 입력은 18 Window였다.

**검증 해석:** Gold58 개발 평가에서는 A(0.894883) > B(0.877599)였으나 Public LB에서는 B(0.923) > A(0.918). Gold58는 Strict FT Fold별 다른 Gold29 활용 및 MIL best epoch 선택에 반복 사용된 연구 데이터이므로 전체 파이프라인의 독립 홀드아웃으로 주장하지 않는다. Public LB 우위를 Private LB 우위로 확정하지 않는다.

**재현 경로 / SHA256**
- Strict FT encoders: `/kaggle/input/datasets/woniyeon/rsna-knee-s1ft02-b-v4strict-2fold-best-v1/fold{0,1}/last.pt`; Fold0 `b4e7d29d3ae0e7ff999c3fb0119dc6126ddd5d5a006c69868818bc440c895aa4`, Fold1 `966fdfe174c995bfbd8855b520440c508a6aa8539eee9cb5a5f724402b538d79`.
- S8A MIL: `/kaggle/input/datasets/yhlucas/s8-mil-mean/fold{0,1}/best.pt`; Fold0 `7c5ff6743b1c525f47a9adb9dc8613056eba602315f465675e1b33e97378310b`, Fold1 `12cbb9fb2771305fac37c9901afcf04d3faa28de89daf6df9c1de730d4623c9b`.
- S8B MIL: `/kaggle/input/datasets/woniyeon/s8-mil-attn/fold{0,1}/best.pt`; Fold0 `0bbe9d1b532cc933ca346e426c612abf7cbf388e991baa0875f14986e3176770`, Fold1 `e52b42565c79476ce342c75e76be078077a8c94fa88e31ee361408e6b0fd3615`.
- V3 Kaggle Save & Run All (T4×2, Internet OFF) 이름: `S8-MEAN-MIL-LB-2F-V3-HIDDENFIX`, `S8-ATTN-MIL-LB-2F-V3-HIDDENFIX`.

**실험 판단:** S8B(0.923)를 현재 Public LB 기준 모델로 보존. 다음 S8C의 질환별 **Window + Series Attention** 구조는 아직 **계획**이며 실제 학습/제출 결과가 아니다. 공개 LB에 대한 반복 튜닝 과적합에 주의.

---



---

# S1-DINO-CBL2F-01 — Stage1~MIL 실험 결과 누적 로그 (Append-Only)

 > **최신 상태 2026-10-13: A/B Stage1 2-Fold TRAIN 완료, Gold58 OOF 검증 완료, 2-Fold Public LB 사용자 보고 A=0.861 / B=0.910 (제출 스크립트/산출물 독립 감사 미완료).** 초기 등록 항목의 미실행 상태는 작성 당시 기록이다. 노트북 실행 및 모델 평가가 끝날 때마다 **이 파일에 날짜순으로 아래쪽에만 기록**한다. 실험별 `.md` 파일을 새로 만들지 않는다.

## 0. 기록 규칙 (고정)

- 한 기록의 필수 항목: 날짜, 실험/계정/Fold, **실제 실행한** Notebook SHA, RUN_MODE, Kaggle Input 버전 및 실물 SHA, GPU/Batch/Microbatch, 완료된 Epoch/steps, GPU peak VRAM, 실제 Run All 시간, best Epoch, Gold29 또는 OOF58 macro/12 targets, 체크포인트/출력 SHA, 결과 상태(PASS/FAIL/PARTIAL/NOT_RUN), 오류 원인과 조치(과학적·재현성 핵심만).
- **실측**과 **추정**을 표/문장에서 명확하게 분리한다. 과거 Exp57 LB 0.918은 비교 기준이지 본 실험 성과가 아님.
- PRE-FLIGHT PASS는 full TRAIN PASS가 아니다. Gold58 반복 DEV OOF도 독립 Test가 아니다.
- 실패 시 마지막 artifact만 실패했는지 확인하고 기존 best checkpoint를 먼저 복구; GPU 재학습을 자동 지시하지 않는다.
- 각 완료 실험 때마다 결과를 이 파일에 추가하고 `S1-DINO-CBL2F-01_ROADMAP.md`의 완료 상태/다음 작업을 갱신. 입력 스키마나 모델 설정이 달라지면 `S1-DINO-CBL2F-01_DATA_MODEL.md`도 갱신.

## 1. 초기 등록 — 2026-10-13 / Stage1 V6 준비

**실험 이름:** `S1-DINO-CBL2F-01`: Strict V1 vs V4 Confidence/Class-balanced Stage1 DINOv2-Base / independent Gold58 two-Fold / downstream Full-MRI MIL.

**현재 확인된 로컬 산출물**
- A `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V6.ipynb`: SHA256 `bef2684ccc1e114782cf7cc7efc9c27db4cabeffa4e54317917b6898486a79e5`; 실제 Kaggle GPU 미실행.
- B `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V6.ipynb`: SHA256 `ebbd19492b51687e927d1c730197a3c4d7ec1f4e014e11f74b7be770cbac859b`; 실제 Kaggle GPU 미실행.
- Gold58 `gold58_manifest.csv` 사용자 제공 내용의 재구성 SHA256 `a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`, 58 UID×12 Target; 신규 Gold 전용 Dataset local ZIP 제작 **완료**, Kaggle 게시/마운트 **미확인**.
- `gold58_2fold_manifest.csv` SHA256 `6e66444e12a62c3f73670e421b939f1b286e21e496c29040754a72b1d18b4876`, Fold0/1 각29. Fold0·Fold1의 12개 타깃은 양성·음성 모두 있음(예: MCL Fold0 4+/25−, Fold1 5+/24−). **검증은 사용자 제공 로컬 라벨 기준**.
- Strict pseudo 라벨: 4,181 supervised Study, 32,163 유효 타깃, 양성 4,607/음성 27,556, 제외 20,025(전체 4,349×12 대비), 희소 MCL 양성37, Synovitis 음성35.
- V4 pseudo 라벨: 4,349×12 Soft Label+Confidence; 가장 불균형한 Fracture soft positive fraction 약 10% 수준, Synovitis 평균 confidence 약 0.173. 데이터/모델 명세에서 원본/버전 확인.
- A/B V6 예정 프로토콜: 각각 T4×2 물리 GPU를 Fold별 독립 사용, Stage1 supervised encoder, effective Study batch4 per Fold, train max12/patience4, Gold OOF58 검증, 4개 encoder 특징 추출→MIL 예정.

**로컬 준비 vs 실측 상태표**

| 단계 | 상태 | 증거/비고 |
|---|---|---|
| 입력·스키마 분석 | `LOCAL_PASS` | STRICT/V4 사용자 제공 ZIP의 CSV 열/해시 및 분포 확인 |
| Gold58 29/29 split 양·음성 coverage | `LOCAL_PASS` | 24개 Fold×Target 모두 양·음성 존재 |
| Gold58 Dataset Kaggle 등록 | `NOT_CONFIRMED` | 사용자 업로드 확인 전 |
| A/B Notebook Kaggle PREFLIGHT | `NOT_RUN` | CUDA 처리량/VRAM 미측정 |
| A/B Stage1 각 2-Fold TRAIN | `NOT_RUN` | best.pt/last.pt 실측 없음 |
| Gold58 pooled OOF58 | `NOT_RUN` | AUROC/AUPRC/Recall/F1 수치 없음 |
| Full MRI feature cache / MIL | `PLANNED` | 모델 최종 평가 이전 |

**주의/위험:** `CUSTOM_GOLD_2FOLD_TRAIN`은 STRICT 원본 릴리스의 Gold 학습 금지 규칙과 다른 사용자 연구 프로토콜. Gold58 여러 번 개발용으로 사용한 결과는 독립 성능 추정 아님. 현 V6는 Kaggle 세션 간 resume 미구현이므로 GPU 시간 측정 전 장시간 학습 금지.

## 2. 실제 GPU PREFLIGHT / TRAIN 결과 — 아직 없음

새 로그를 받으면 다음 양식을 **반복해서 이 절 아래에 계속 추가**:

```text
### YYYY-MM-DD — <lane/fold/notebook version>
- 상태: PREFLIGHT_PASS | TRAIN_PASS | PARTIAL | FAIL
- Notebook/Input SHA 및 Kaggle Script Version:
- GPU 모델·2GPU isolation·Window microbatch·study batch/accum:
- 측정 peak VRAM / study 처리량 / 실제 runtime:
- Epoch / optimizer steps / best Epoch:
- Validation 12-target AUROC/AUPRC; Recall/F1/Specificity 등:
- Gold58 OOF58 (양 Fold 완료 후):
- best.pt/last.pt/predictions SHA 및 저장 위치:
- 확인된 사실 / 실패 원인 / 후속 결정:
```

## 3. 향후 Stage2 Full-MRI MIL 결과 — 아직 없음

Stage1 Fold checkpoint 4개가 확보되면 fold별 DINO feature extraction SHA와 CLS+PatchMean1536 cache UID/Slice coverage를 검증한 뒤, Window/Series Attention MIL 결과와 Top-K ablation 성적을 이 파일에 순서대로 누적한다. 실험별 새 `.md`는 만들지 않는다.

[데이터/모델 기준](S1-DINO-CBL2F-01_DATA_MODEL.md) · [현재 계획/상태](S1-DINO-CBL2F-01_ROADMAP.md)


### 2026-10-13 — B V4 V7 PREFLIGHT 실측 PASS (TRAIN 미실행)

- **실행 방식/증거:** 사용자 제공 실제 Kaggle 실행 TXT `붙여넣은 텍스트(1)(20261012-191942).txt`, `STAGE1_V4_DUALFOLD_PREFLIGHT_review.zip`. ZIP CRC 전체 PASS; V4 Worker SHA256 `0a2cd180491ad0c91502f40a4287c0739c8b5d108e50867002754dad70d0a2d7`, AST PASS. Notebook 실행은 V7 WorkerFix, `RUN_MODE=PREFLIGHT`.
- **데이터 계약:** common manifest 24,371 Series/4,407 Studies; 5 Packs 각38 Shards; Gold58 전용 데이터셋 및 29/29 UID split SHA PASS; 12타깃 Fold별 positive/negative PASS; V4 pseudo 4,349+각 Fold Gold29 → **4,378 train/Fold**, Gold29 val/Fold; leakage 검사 PASS.
- **Loss:** `LOSS_CONTRACT_PASS Gold3xNoPseudoPrior Conf0.25 MaskedNoGradient 12-target_norm`; V4 pseudo Confidence-weighted tempered positive/negative class BCE; Synovitis 평균 confidence 약0.173 / Fracture weighted soft positive prevalence 약0.1002는 경고로 기록(오류 아님).
- **실제 GPU0 Fold0:** T4 독립 worker exit0; Window microbatch18, peak allocated **2.41 GiB**, synthetic full18 Window F+B **1.32초**, 실제 HDF5 Study F+B **0.239102214초**, loss0.4005183, `GPU_PREFLIGHT_PASS`.
- **실제 GPU1 Fold1:** T4 독립 worker exit0; microbatch18, peak allocated **2.41 GiB**, synthetic full18 Window F+B **1.32초**, 실제 HDF5 Study F+B **0.236578257초**, loss0.4299068, `GPU_PREFLIGHT_PASS`.
- **결과:** `BOTH_GPU_PREFLIGHT_PASS`, `PREFLIGHT COMPLETE`. **아직 optimizer step이나 전체 epoch는 수행되지 않음; best.pt/last.pt 없음; 학습 성능 기록 없음.**
- **12 Epoch GPU F+B만 단순 예상:** Fold0 3.49시간 / Fold1 3.45시간(동시 실행, 합산 금지). HDF5 I/O·Optimizer step·Epoch validation·checkpoint 저장·병렬 I/O 경합 **미반영**, 실제 시간은 더 길 수 있음. 세션 간 resume 미구현이므로 Kaggle 세션 제한 시 중도 결과 위험.
- **결정:** B는 입력/실제 모델 GPU 사전검증을 통과해 `RUN_MODE=TRAIN`으로 변경할 수 있는 단계. 단 과도한 시간·비용 위험을 명시하고 1 Epoch 실측/남은 세션 예산을 모니터링할 것. A STRICT V7 GPU PREFLIGHT는 별도 로그 확인 대기.


### 2026-10-13 — A STRICT V1 V7 실제 GPU PREFLIGHT PASS (TRAIN 미실행)

- **실행/증거:** 사용자 제공 `STAGE1_STRICT_DISTRIBUTION_V3_PREFLIGHT_review.zip`. ZIP 내 27개 파일 CRC PASS; `dual_preflight_summary.json`에 `BOTH_GPU_PREFLIGHT_PASS`; 양 Fold `console.log`, `gpu_preflight_results.json` 대조. `stage1_strict_worker.py` 존재, Worker 파일 생성 문제 V7에서는 해결.
- **데이터 계약:** 입력 manifest 24,371 Series/4,407 Studies, pseudo STRICT supervised 4,181/각 Fold Gold train29 → **4,210 Study/Fold**, held-out Gold29/Fold. 원본 STRICT 희소 클래스 Target-mask가 보존됨. 독립 Fold 프로세스 exit0 (해당 JSON 및 사용자 제출 ZIP 기준).
- **Loss 검증:** 양 Fold `LOSS_CONTRACT_PASS Goldx3 Conf0.25 MaskedNoGradient 12-target_norm`. Fold0/1 공통 `epoch_01_balance_preview.json`의 majority rotation: MCL 3,724 negatives 중 740, Lateral OA 2,490 negatives 중 1,320 매 Epoch 선택. MCL 37 positives·LateralOA 66 positives·Synovitis 35 negatives 전부 보존, rescue0.
- **GPU0 Fold0:** Window Microbatch18, peak allocated **2.41 GiB**, synthetic 18-window F+B **2.60초**, real HDF5 Study F+B **0.270552014초**, loss **0.0366938189**; `GPU_PREFLIGHT_PASS`.
- **GPU1 Fold1:** Window Microbatch18, peak allocated **2.41 GiB**, synthetic F+B **2.59초**, real Study F+B **0.239363503초**, loss **0.0585563257**; `GPU_PREFLIGHT_PASS`.
- **12 Epoch F+B-only 투영:** Fold0 약 **3.80시간**, Fold1 약 **3.36시간**(동시 실행). HDF5 I/O, Optimizer, validation, checkpoint, 두 Fold의 동시 I/O 경합 미포함. 단일 Study 표본 측정으로 전체 Epoch 시간 확정 불가.
- **상태:** 실제 Kaggle GPU 사전검증 PASS. **Optimizer step / 첫 Epoch / 모델 학습 / 성능 지표는 아직 미실행**. Cross-session Resume 기능이 없어 세션 중단 위험을 갖고 있음.
- **다음:** A는 `RUN_MODE=TRAIN` 전환 가능; Save Version `S1-STRICT-F01-WFIXV7-TRAIN`, GPU T4×2 Internet OFF Save & Run All. 첫 Epoch/로그의 실제 시간·남은 세션 한도를 확인해야 함.


### 2026-10-13 — A STRICT V1 vs B V4 Stage1 2-Fold TRAIN 완료 / Gold58 OOF 비교

**상태:** A, B 각각 `BOTH_FOLDS_TRAIN_SUCCESS`, Fold0·Fold1 각 `STAGE1_TRAIN_SUCCESS`; ZIP CRC PASS; Gold58 예측 58 UID 모두 유일하며 양 계정의 UID·Fold·12타깃 Truth가 동일. 유저 제출 TRAIN ZIP의 원본 CSV를 재계산하여 macro 및 타깃별 AUROC·AUPRC 원본 출력과 일치 확인. **best.pt/last.pt 본체는 ZIP에서 제외된 상태**로 SHA/경로는 학습 보고서에서만 확인됨; Kaggle Output 모델 파일을 반드시 별도 보관.

**실행 증거:**
- A: `STAGE1_STRICT_DISTRIBUTION_V3_TRAIN_review.zip` SHA256 `92284f1eaf71a1abbefd0e7f54fab8fbdb5a188fe8feb1413015d144d65c01ee`; `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb`, STRICT 4,181 pseudo + 29 Gold train/Fold = 4,210.
- B: `STAGE1_V4_DUALFOLD_TRAIN_review.zip` SHA256 `650bd27f58b16dfd18a65d021c5535263f11a362439de8f346ee3e7c6dd858d0`; `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb`, V4 4,349 pseudo + 29 Gold train/Fold = 4,378.
- 두 계정 모두 실제 T4×2, Fold0 GPU0 / Fold1 GPU1 독립 병렬, Window microbatch18, effective Study batch4/Fold, 224×224 3-Slice Window×18, DINOv2-Base full fine-tune.

| 계정/Fold | Best Gold29 Macro AUROC | Best Epoch | 학습 Epoch | 각 Fold 실제 시간 | best.pt SHA256 (학습 보고서 기반) |
|---|---:|---:|---:|---:|---|
| A STRICT Fold0 | 0.838365 | 9 | 12 | 630.67 min | `e5ae8a3a2b30d5bf71a19aabc7cfba888bb05d91b152d82931c3d44f3d4387a6` |
| A STRICT Fold1 | 0.785654 | 7 | 11 | 587.92 min | `954d099a0e4274c1ee4581fc8c518fd3f30dcafff39e4d2ed941eb9224704935` |
| B V4 Fold0 | 0.892702 | 8 | 12 | 629.08 min | `15bd9189eac7a7366239a0747e671f0f567a40a2db660e7054e2de26eb01e629` |
| B V4 Fold1 | 0.868232 | 9 | 12 | 630.70 min | `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5` |

**Gold58 pooled OOF — 모델별 Fold best checkpoint에서 나온 58명 통합 예측; threshold-dependent metrics는 0.5 고정**

| Metric | A STRICT | B V4 | B−A |
|---|---:|---:|---:|
| Macro AUROC | 0.811284 | **0.871112** | +0.059828 |
| Macro AUPRC | 0.729597 | **0.800206** | +0.070609 |
| Macro Recall@0.5 | 0.6170 | **0.8223** | +0.2053 |
| Macro Precision@0.5 | **0.7975** | 0.6391 | −0.1584 |
| Macro F1@0.5 | 0.6347 | **0.7053** | +0.0706 |
| Macro Specificity@0.5 | **0.8529** | 0.7389 | −0.1140 |
| Macro Balanced Accuracy@0.5 | 0.7350 | **0.7806** | +0.0456 |

**Gold58 타깃별 A/B AUROC**

| Target | Gold positive | A STRICT | B V4 | B−A |
|---|---:|---:|---:|---:|
| ACL | 24 | 0.8848 | 0.9007 | +0.0159 |
| MCL | 9 | 0.7007 | 0.8639 | +0.1633 |
| Medial Meniscus | 26 | 0.8918 | 0.9423 | +0.0505 |
| Lateral Meniscus | 23 | 0.7739 | 0.8037 | +0.0298 |
| Medial OA | 15 | 0.8233 | 0.9628 | +0.1395 |
| Lateral OA | 11 | 0.7485 | 0.8569 | +0.1083 |
| PF OA | 21 | 0.7786 | 0.8211 | +0.0425 |
| Effusion | 35 | **0.9540** | 0.9329 | −0.0211 |
| Synovitis | 27 | **0.6906** | 0.6762 | −0.0143 |
| Baker's | 12 | 0.8460 | 0.9783 | +0.1322 |
| Contusion | 19 | 0.8070 | 0.8853 | +0.0783 |
| Fracture | 18 | **0.8361** | 0.8292 | −0.0069 |

**통계 참고(탐색적):** 동일 58 UID를 짝지어 Study-level replacement bootstrap 1200회 실시한 V4−STRICT pooled macro AUROC 델타 퍼센타일 2.5–97.5% 약 **+0.014~+0.106**; AUPRC 델타 약 **+0.004~+0.137**. Best Epoch를 같은 Gold58에서 선택했으므로 **독립 검증 CI나 확증적 p-value로 해석 금지**. MCL Gold 양성 9명 등 소표본으로 지표 분산 큼.

**해석 및 결정:** B는 Gold58 개발 OOF ROC 기준 12타깃 중 9개에서 우세. Effusion/Synovitis/Fracture는 A가 소폭 우세. B를 다음 Full-MRI feature-cache/MIL 우선 백본 후보로 선택하되 **A Fold0/1 체크포인트는 보존**, 후속 A/B 또는 앙상블 비교 후보로 유지한다. A/B는 label 분포뿐 아니라 4,181 vs 4,349 Study, target mask, class-balanced loss/Confidence 차이가 있어 B 우위를 단일한 'V4 라벨 품질' 인과효과로 주장 금지. Recall/F1의 임계값 최적화는 58 Gold에서 재튜닝 시 낙관편향 위험.

**차단 사항/다음 작업:** 제출 ZIP에 **모델 가중치 `.pt` 바이너리 없음**. Kaggle 각 실행의 Output `fold0/best.pt` + `fold1/best.pt` 총 4개 파일 보존 여부 및 SHA를 확인하고, 이를 Add Input 모델/데이터셋으로 등록한 뒤 Fold-aware Stage2 특징 추출을 설계해야 한다. Kaggle Public LB 점수는 본 실험에서 측정하지 않음.


### 2026-10-13 — A/B independent 2-Fold LB submission notebooks prepared (NOT submitted)

Experiment S1-DINO-CBL2F-01 Stage1 has A STRICT and B V4 independently trained Fold0/Fold1 best checkpoints. These are **separate LB submissions**, each equal 0.5/0.5 sigmoid probability averaging (not A+B averaging). No model training or Gold58-based calibration during inference.

A notebook: A_S1-DINO-CBL2F-01_STRICT_2FOLD_LB_SUBMISSION_V1.ipynb SHA256 268187b2ab0db2390a008cb627adaa0e8aa731b2ff8f35560cdaf85856d59eb1.
B notebook: B_S1-DINO-CBL2F-01_V4_2FOLD_LB_SUBMISSION_V1.ipynb SHA256 a0c7bd71d50f5e652f49ee1f23398be1eceb8b34b6fcc2b4195e6b60ebe04392.

Source architecture copied verbatim from actual Train ZIP FeatureDINO Worker (identical A/B class SHA b385856a8e5ecfcd81da42c417dc1ba96ca5cb4f3d345a44a162907c32ad0874). Stage1 sampler from Train ZIP SHA 8ce97e7cebf0c75597e6bd8ea8c262bfb6596dfdcbf0975b8d31101fe125052c. Preprocessing follows RMIL-04B Native224 V3 physical slice ordering, 130mm center crop, per-Series percentile 0.5/99.5, Zscore, clamp +/-5, INTER_AREA 224, uint8; 20 Study/360 Window sampler and 12-Slice/3-triplet synthetic byte parity tests PASS.

Required Kaggle Add Input per account: (1) Competition RSNA Knee Abnormality Detection test.csv/test_series.csv/sample_submission.csv/test_series/*.dcm; (2) NEW USER-UPLOADED checkpoint dataset A yhlucas/rsna-knee-stage1-strict-f01-best-v1 or B yhlucas/rsna-knee-stage1-v4-f01-best-v1, files fold0_best.pt/fold1_best.pt in its root (PROPOSED, not yet confirmed created); (3) MetaResearch dinov2 PyTorch Base version1 original pretrained model (SHA pinned). No training HDF5, pseudo label or Gold58 required.

GPU T4x2, GPU0 Fold0/GPU1 Fold1; 2 GPU parallel inference, Internet OFF, Save & Run All. Kaggle GPU code submission max 9 hours. Visible 3 Studies and ~1300 hidden Studies runtime estimate 1-10min / 2-8h+ is speculative, not measured. Per Study corruption logged with neutral fallback, final submission.csv exact schema/UID/finite probability SHA verified.

STATUS: NOTEBOOKS_STATIC_QA_PASS; CHECKPOINT_DATASET_MOUNT_PENDING; REAL_KAGGLE_GPU_UNVERIFIED; OFFICIAL_PUBLIC_LB_NOT_SUBMITTED. Model best.pt binary not contained in TRAIN review ZIP. Register actual checkpoint files from completed Kaggle outputs; only then execute and score. Historical Gold58 OOF STRICT 0.811284 / V4 0.871112 are NOT LB scores.

### 2026-10-13 — LB Submission V2 exact checkpoint paths (user supplied; not yet executed)

- A checkpoint Dataset: `yhlucas/rsna-knee-stage1-strict-f01-best-v1`; exact files:
  - `/kaggle/input/datasets/yhlucas/rsna-knee-stage1-strict-f01-best-v1/fold0/best.pt`
  - `/kaggle/input/datasets/yhlucas/rsna-knee-stage1-strict-f01-best-v1/fold1/best.pt`
- B checkpoint Dataset **owner differs**: `woniyeon/rsna-knee-stage1-v4-f01-best-v1`; exact files:
  - `/kaggle/input/datasets/woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold0/best.pt`
  - `/kaggle/input/datasets/woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold1/best.pt`
- Newly corrected notebooks:
  - A `A_S1-DINO-CBL2F-01_STRICT_2FOLD_LB_SUBMISSION_V2_EXACTPATH.ipynb`, SHA256 `d272241254c8222004a74dbf34def355a6093cc7ef588d5852a22e965a89bdb0`.
  - B `B_S1-DINO-CBL2F-01_V4_2FOLD_LB_SUBMISSION_V2_EXACTPATH.ipynb`, SHA256 `2c7323124de1b5fa3a2de2463618f19b6a342a9c7e060abe8a9a0dcf0ce2cb95`.
- Only checkpoint path owner/subfolder and first Markdown / Save Version metadata changed. Original FeatureDINO architecture, RMIL-04B V3 raw DICOM policy, 18-window sampler, 2GPU Fold probability averaging, SHA-pinned `best.pt` and pretrained weights retained.
- **QA:** Both Notebook JSON/nbformat/6 code-cell AST PASS; exact-path assertions, checkpoint SHA literals verified in source; ZIP CRC PASS. User provided paths but live Kaggle mount and actual `best.pt` bytes are **not yet verified**. Status `NOTEBOOK_V2_STATIC_PASS / KAGGLE_INFERENCE_NOT_RUN / PUBLIC_LB_UNKNOWN`.


### 2026-10-13 — Performance audit: Exp11B 140.50min vs Stage1 V7 ~630min

**Observed source**: historical 2026-09-21 Exp11B complete Kaggle saved code/log (Fold2), repository README Experiment37; new Stage1 user-provided A/B TRAIN review ZIPs, fold console logs and training_history.csv. This is a comparison of *different execution designs*, not a controlled benchmark.

| Item | Exp11B DINOv2-Base | Current S1 A/B V7 |
|---|---|---|
| Backbone/resolution/full FT | DINOv2-Base / 224 / Yes | same |
| DINO calls per Study | 6 slots × (9 slices/3-channel) = 18 | 18 three-slice windows |
| Parallelization | 2×T4 DataParallel **one Fold/model** | GPU0 Fold0 and GPU1 Fold1 **independent models** |
| Batch | physical Study batch 4, grad accum1 | physical Study batch 1/GPU, grad accum4, effective4 per Fold |
| Cache/data loader | Persistent `.npy` `np.load(mmap_mode='r')`; DataLoader num_workers4, prefetch_factor2, pin_memory | 190 HDF5 shards random access, synchronous `train_ds[idx]` in worker (no DataLoader training prefetch), 12-open-file LRU cache |
| Activation checkpoint | absent in retrieved Exp11B training model | `_features` checkpoint `use_reentrant=False` every Study in Train |
| Train studies/Fold | 4,396 | A4,210; B4,378 |
| Epochs executed | 10 (early stop) | A Fold0 12, Fold1 11; B both12 |
| Time per epoch | Exp11B epoch10 13.97min, full mean ~14.05min | A Fold0 52.56min, B Fold0 52.42min |
| Total/Fold | 140.50min | A Fold0 630.67min; B Fold0 629.08min / Fold1 630.70min |
| Throughput | 5.22 studies/sec per model on 2 GPUs | A Fold0 ~1.34 studies/sec per GPU; B Fold0 ~1.39 studies/sec per GPU |

**Quantitative analysis:** B wall time ~4.48× Exp11B (630/140.5); mean epoch time ~3.73× (52.4/14.05) plus 12 vs 10 epochs ×1.2 explains total. The 18 DINO inputs/Study were **the same**; more images per Study is *not* the cause. GPU count allocation 2 GPUs per Fold versus 1 GPU per Fold can explain part; 1-Study sequential forward/backward/4× accumulation, activation checkpoint recomputation, and synchronous HDF5 I/O likely cause the remainder. Neither model-side versus I/O side nor each factor's proportion is separately timed, so no measured causal attribution/percentages.

**Optimization gate (no automatic retraining):** benchmark same Fold+same data+same selected model and 100-200 Study under (1) checkpoint on/off only after actual optimizer VRAM profile, (2) physical Study batch1 vs2/4 with grad accumulation adjusted to preserve effective4 (vectorized forward; never confuse Study with Window microbatch), (3) HDF5 background DataLoader workers 0/2/4 + pinned prefetch, (4) independent Fold vs DP/DDP two GPUs if goal is single-Fold wall time; separately report two-Fold total GPU-hours, preprocessing vs GPU F/B+optimizer time, measured Study/sec, peak allocated/reserved, loss/scientific parity. All these are FUTURE potential fixes, not verified runtime reductions.

### 2026-10-13 — New GPU resource rule: Batch124+ evidence, 30h/week (policy decision)

- User re-confirmed past real observations: simultaneous Batch124+ feasible and approximately 20GB unused VRAM. Exact model, GPU(s), and Batch unit are unconfirmed; do not silently downgrade these observations to speculative OOM concerns.
- User GPU quota is 30 hours per week. The previous A/B Stage1 training taking as much as ~630.7 minutes must not recur because of unnecessarily low Study Batch, lack of HDF5 prefetch, or checkpointing without performance profiling.
- Shared AI_AGENT_KAGGLE_NOTEBOOK_RULES and GPU_BATCH_RESOURCE_MANDATORY_POLICY updated to require 128-256 MRI Study full-step profiling, aggressive larger Batch exploration (including 124+ where available), highest-throughput selection, full GPU time forecast (goal <=4h/run, block >=8h predicted), stop/checkpoint if projected budget breached, weekly quota tracking.
- Existing S1-DINO-CBL2F-01 ROADMAP and DATA_MODEL documents updated in place, not split. Completed training models unchanged; no new GPU experiment was run for this administrative change. Future claims about max current-model Batch will require measurement.


### 2026-10-13 — A/B independent 2-Fold Kaggle Public LB (user-reported)

**Evidence/status:** User directly reported the Kaggle Public LB scores in this chat: **A STRICT V1 = 0.861**, **B V4 = 0.910**. This is user-reported official scoreboard observation; no submission Screenshot / scriptVersionId / official score JSON / `submission_audit.json` has been attached for independent verification. Treat the scores as user-reported and do **not** invent Script Version, timestamp or hidden-test metrics.

| Pipeline | Gold58 pooled OOF Macro AUROC (DEV) | Public LB (USER-REPORTED) | Same-metric LB gap versus Exp57 | Notes |
|---|---:|---:|---:|---|
| A STRICT V1 DINOv2-Base, Fold0+Fold1 sigmoid mean 50:50 | 0.811284 | **0.861** | **-0.057** | Custom Gold-train 2-fold STRICT, mask/class balance |
| B V4 DINOv2-Base, Fold0+Fold1 sigmoid mean 50:50 | 0.871112 | **0.910** | **-0.008** | V4 soft/conf-balanced |
| Historical Exp57, 3-fold B3A Top-K + full-MRI direct 70:30 | not same development evaluation | **0.918** | **0** | Historical project best remains unchanged |

**Deltas:** Public LB B−A = **+0.049**; Gold58 OOF development AUROC B−A = **+0.059828** (different evaluation datasets, not statistically interchangeable). Relative to historical project best 0.918, B is only 0.008 lower. A trails B by 0.049. B/A are *separate 2-Fold* ensembles, **not** a combined A+B ensemble.

**Interpretation:** The direction of the Gold58 preference for B over A is corroborated by the reported external Public LB gap (+0.049), which is useful despite repeated Gold58 DEV usage. However A/B differ simultaneously in label coverage, masks, confidence and class-balanced loss, so this result does not isolate label correctness as a causal factor. Exp57 uses another architecture/protocol and 3 folds, so direct architecture superiority is not proven. No new model training, MIL, feature extraction, blending or A+B ensemble was executed in this LB report.

**Decision:** Promote **B V4 2-Fold Stage1** as a strong standalone baseline and priority encoder candidate for Stage2 full-MRI feature extraction / hierarchical MIL; keep both A Fold checkpoints for future diversity tests only if performance-gated. Preserve Exp57 0.918 as project best; do not retrain Stage1 now. Next Stage2 expensive GPU run **blocked on 30h/week resource plan and same-hardware 128–256 Study full-optimizer speed profiling** (batch124+ evidence, target <=4h/run, reject predicted >=8h). First verify B submission fallback count and script/notebook provenance when those logs are available.

**Submission artifact status:** Scores reported by user; exact Kaggle Script Version, `submission.csv` SHA, fallback studies/hidden decoding, checkpoint byte hashes as mounted by the submission kernel, and actual submission runtime **not independently audited**; do not mark those audit gates PASS without evidence.


### 2026-10-14 — S1-DINO-CBL2F-02 A/B Fine-tuning + Submission notebooks STATIC QA only

- **Purpose**: A new Strict V1 hard/masked vs B V4 Routed Strict soft/confidence, both warmstart **the same prior B V4 Broad Fold0/1** weights (prior 2Fold Public LB 0.910). Max3 Epoch low-LR FT, Gold29 heldout Fold-wise; no MIL yet.
- Notebook SHA A `cabea26653a1c0c34b6983093461b467cef8e4b1a2aacad8a8ebb7b6aadf2232` B `dd98d379846c9602474772ac87c1c8fc11c7c6c2db5458421fba82bfadec38c6`. Submissions templates A `b448d25f70e79241111ab7c129d51ad83759939029a5ee7e01021fcbbe6efe18` / B `68d5355a25eac7acdaba0646b68a98899d31c0b31f7c71224973129549175b69`.
- SHA of original source label CSV verified from user-supplied ZIP: A STRICT V1 `c66810ed4bf35a3fffe35d404aa7eceac860e5f28a013ee2ae7fdf0032497168`, 4181 rows/32163 valid; B V4 Routed Strict `bfca4993e5c985d9318d732bf2a0970dd7af9b3beff1d6ff619822042bf7a2c0`, 4349 rows/39792 valid.
- Static checks: both notebook 9 cells AST PASS; extracted Worker Python compile PASS; lightweight CPU mock 2-Study batched-vs-per-Study forward equivalence PASS; label coverage and archive ZIP CRC PASS. **Real Kaggle T4 Optimizer/128 Study benchmark, 2Fold training, public test inference and Public LB NOT RUN.**
- GPU resource gate: attempted Window microbatch124 and Physical Study8 among candidates, Select observed highest Study/sec on real optimizer, HDF5 prefetch workers2, projected 3Epoch >4h triggers pre-train block. Strict class balancing preserves Gold neutral weight3 and masks invalid target loss; A rare class rotation, B soft/confidence weighted imbalance, both pseudo-only.
- Historical Exp57 LB0.918 and V4 Broad LB0.910 unchanged. No claim of new improvement or official competition score.

### 2026-10-14 — S1FT02 A/B failed before train (missing shutil in subprocess), V2 static fix

- User-supplied Kaggle A/B execution logs show CUDA T4x2, checkpoint SHA, label, class balance and Gold58 Fold checks PASS; both Fold0/Fold1 fail after `EPOCH0_BROAD_BASELINE_PASS` with `NameError: name 'shutil' is not defined` at `shutil.copyfile(...,best.pt)` in independent worker. **NO fine-tuning Epoch, optimizer training checkpoint or new LB**. Missing import in worker script, though parent notebook imports shutil.
- Actual benchmark: 8 Study/Window chunk124 yielded **real GPU OOM** per T4 (~14.56GiB available/device), benchmark picked physical Study batch2/window chunk36/checkpoint OFF. Full 128 Study optimizer profile: Fold0 62.04sec (2.06 studies/s; projected 3Epoch2.04h), Fold1 60.93sec (2.10 studies/s; projected2.00h). Baseline Fold0 AUC0.892702, Fold1 AUC0.868232 reproduced. These are **A-log numbers**; verify B separately before treating as B measurements.
- Produced local V2 training notebook with worker `import shutil` explicitly added, preserving labels, loss/balancing, model, LR/seed and benchmark. A `S1FT02_A_BROAD_TO_STRICTV1_DUALFOLD_E3_V2_IMPORTFIX.ipynb` SHA256 `6cdc6ceae0b2e23212b74a825264cbf1953c95dfc2a4d97cdfa1ad5cf1d0cafe`; B `S1FT02_B_BROAD_TO_V4STRICT_DUALFOLD_E3_V2_IMPORTFIX.ipynb` SHA256 `9a77ed87b941577d6e32244bee627d8c2b8f9689f6458a9782392ef50d464ffb`. Both AST/Notebook checks and new ZIP CRC PASS; **live Kaggle V2 NOT_RUN**. Submission templates unchanged.

### 2026-10-14 — FT02 A V2 Epoch1 completed then Fold1 config KeyError, V3 fix

- User A Kaggle V2 log: both Folds passed real full optimizer bench and Stage1 Broad baseline. Fold0 selected StudyBatch2/WindowMicrobatch36/checkpoint OFF, Fold1 StudyBatch4/WindowMicrobatch36/checkpoint OFF (A/B comparison must report unequal effective-batch caveat). Each completed 4,210-study Epoch1 ~28min. Fold0 Gold29 AUROC fell from baseline **0.892702** to **0.876060**, so baseline `best.pt` retained and `last.pt` probably saved. Fold1 improved above baseline 0.868232, then `save_derived()` raised **`KeyError: 'label_mode'`** because per-Fold `run_config.json` omitted that field. Fail-fast then SIGTERM Fold0 (code -15). Fold1 newly improved model was NOT saved; its Epoch1 exact AUROC absent in logs. No completed A 2Fold run, no A LB.
- V3 patch adds `label_mode=LABEL_MODE` to Fold config writer and fail-fast required-config assertions before GPU Worker spawning. A V3 notebook SHA `07a7fe8523eff38d1c270c783850fd91c43e796e968d6f964e225ad678d7e5db`, B V3 SHA `b52e9156d4496815418bed00fc9ee70c39958bf1b59af46857d06a90742b640e`. Python AST + nbformat + worker extraction compile + ZIP CRC verified; real Kaggle V3 NOT RUN. V3 unchanged labels/loss/balance/LR/optimizer other than config bug.
- Kaggle V2 Output persists in failed version if retained; fold0 `last.pt` and `best.pt` may exist. The new V3 Run All does NOT auto-resume from these artifacts. Preserve failed-version Output before replacement; do not claim Fold1 improved best weights exist if save failed.

### 2026-10-14 — S1FT02 V3 A/B completed and reviewed

- User provided A and B V3 console logs and `S1_FT02_A_review.zip`/`S1_FT02_B_review.zip`. Both status **BOTH_FOLDS_FINETUNE_SUCCESS**, both ZIP CRC PASS, each contains Gold58 OOF 58 unique rows, class audits and fold histories. Checkpoint `.pt` files deliberately NOT included in review ZIP; SHA claimed by training summary must be verified against retained Kaggle Output models before submission.
- Original common B-V4-Broad (LB **0.910**, Gold58 OOF **0.8711117400**) fold0 AUROC **0.8927021378**, fold1 **0.8682316866**.
- A STRICT V1: Fold0 best Epoch1 **0.8931986923** (delta **+0.0004965544**, study batch 4), Fold1 best Epoch0 unchanged **0.8682316866** (study batch 2). Two Epochs each, Gold58 pooled macro AUROC **0.8616997625**, delta vs original **−0.0094119775**, macro AUPRC **0.8072076579**. Fold0 improved local AUROC while pooled 58 declined, due to pooled vs within-fold ranking differences. F0 best SHA `72a443d9d69f56aa082f1504a9e878796a35bcfec96f0f23d3225730f21ca474`, F1 original SHA `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5`. A candidate for optional independent public LB test (no new LB yet).
- B V4 Routed Strict: both fold best Epoch0 (NO improvement), pretrained original hashes Fold0 `15bd9189eac7a7366239a0747e671f0f567a40a2db660e7054e2de26eb01e629`, Fold1 `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5`; two Epochs each, study batch 2; pooled OOF **0.8711117400** identical to original; AUPRC **0.8002062131**. Redundant B public LB rerun under identical inference.
- A vs original B per-target strongest deterioration Baker's −0.070652, Lateral OA −0.052225, Synovitis −0.035843; gains PF OA +0.020592, Fracture +0.020833, Medial OA +0.012403. A/B differ in class balancing, sample coverage and physical batch (A F0=4, others=2): NOT a perfectly controlled pure-label isolation.
- Original Exp57 public LB **0.918**, B Broad current public LB **0.910** remain historical bests. FT02 neither shows Gold58 OOF improvement; no new Public LB values yet. Next action: preserve Kaggle A output; optionally submit A 2Fold to obtain independent LB, skip redundant B submission; then proceed to MIL.
