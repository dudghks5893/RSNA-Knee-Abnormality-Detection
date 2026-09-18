# RSNA Knee Abnormality Detection — Experiment Log

**Competition:** [RSNA Knee Abnormality Detection](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection)

---

## Experiment 01 — 초기 V1.1 Submission

### 구성
- 초기 RSNA Knee 모델 파이프라인
- 단일 모델 제출
- 이후 V2 계열의 비교 기준으로 사용

### 결과
- **Public LB: 0.554**

### 인사이트
- 초기 파이프라인만으로는 경쟁력 있는 성능이 나오지 않았다.
- 이후 실험에서는 MRI series 구성, DICOM 전처리, pseudo-label 품질, pretrained backbone, multi-plane aggregation을 함께 개선했다.

---

## Experiment 02 — Report Pseudo Label v2

### 구성
- Report 기반 pseudo-label 생성
- 대상: report-only train studies
- 12개 target별 `score / confidence / verdict` 생성
- 대표 score mapping:
  - NO: score 0.08 / confidence 0.85
  - UNK: score 0.28 / confidence 0.05
  - YES: severity에 따라 score 0.68 / 0.82 / 0.94, confidence 0.95

### 결과
- 총 train 4,407 studies 중 **4,349 report-only studies**에 pseudo supervision 구성
- Gold overlap을 이용한 내부 검증에서 ACL 등 일부 target은 양호했으나,
  - Lateral OA
  - Synovitis
  - Contusion
  에서는 상대적으로 약한 정합성을 보였다.

### 인사이트
- 하나의 고정 pseudo-label 규칙만 사용하는 것보다 target별 reader 신뢰도를 반영할 필요가 있었다.
- 이 결과가 이후 V4 Consensus pseudo-label 구성으로 이어졌다.

---

## Experiment 03 — V4 Consensus Pseudo Label

### 구성
- 기존 report label과 GPT-5.6 Sol 기반 report label을 활용한 consensus pseudo-label
- target별 reader alignment를 기준으로 routing
- Gold leakage를 막기 위해 fold-aware pseudo-label 파일 생성
- 생성 데이터:
  - broad report-only pseudo labels
  - strict pseudo labels
  - Fold 0~4 leakage-safe pseudo labels
  - Gold fold policy / audit

### 결과
- Full-data reader-alignment 기준 평균 AUC: **약 0.8957**
- Gold studies는 pseudo supervision에서 제외
- 학습 시 Gold source weight는 1.0, pseudo source는 confidence 기반 weight 사용

### 인사이트
- pseudo-label source를 target별로 선택하는 방식이 단일 reader보다 안정적이었다.
- OOF 평가에서는 반드시 fold-aware pseudo-label을 사용해야 leakage를 방지할 수 있었다.

---

## Experiment 04 — V2 DINOv2-S Fold 0 Single Model

### 구성
- Backbone: **DINOv2 Small**
- Input:
  - 6 slots
  - Sagittal / Coronal / Axial
  - fluid-sensitive / non-fluid-sensitive
  - 각 slot 9 slices
  - 3 slices × 3 groups
- Input tensor: `[B, 6, 3, 3, 224, 224]`
- Physical center crop: **130 mm**
- Laterality normalization 적용
- DICOM ordering:
  - ImageOrientationPatient + ImagePositionPatient
  - InstanceNumber fallback
- Label-specific slot attention
- Fold 0:
  - Train: 4,349 pseudo + 47 Gold
  - Validation: 11 Gold
- 3 epochs
- Effective batch size: 4

### Validation 결과

| Epoch | Train Loss | Val Loss | Macro AUC |
|---|---:|---:|---:|
| 1 | 0.820360 | 0.904339 | 0.705556 |
| 2 | 0.763319 | 0.846631 | 0.745007 |
| 3 | 0.718780 | 0.825426 | **0.750099** |

### Fold 0 Target AUC
- ACL: 0.666667
- MCL: 0.722222
- Medial Meniscus: 0.607143
- Lateral Meniscus: 0.750000
- Medial OA: 0.958333
- Lateral OA: 0.611111
- PF OA: 0.642857
- Effusion: 0.821429
- Synovitis: 0.900000
- Baker's: 0.666667
- Contusion: 0.821429
- Fracture: 0.833333

### Submission 결과
- **Public LB: 0.804**

### 인사이트
- V1.1의 0.554에서 **0.804로 크게 상승**했다.
- DINOv2 + multi-plane MRI 구성 + V4 pseudo-label 조합이 유효했다.
- Fold 0 validation은 11명뿐이어서 개별 target AUC 변동성이 매우 컸다.
- Slot attention은 대부분 0.16~0.17 부근으로 비교적 균일해, slot specialization은 강하지 않았다.

---

## Experiment 05 — V2.1 Optimized 5-Fold Training Engine

### 변경 사항
- 고정 5-fold Gold split
- Fold-aware V4 pseudo-label 사용
- 2 × Tesla T4 DataParallel
- Physical batch: 4
- Gradient accumulation: 1
- Effective batch: 4
- Shared DICOM cache
- 각 Fold 독립 checkpoint 저장
- Fold별 best epoch 선택
- 각 Fold의 held-out Gold만 validation으로 사용

### Fold 구성

| Fold | Validation Gold |
|---|---:|
| 0 | 11 |
| 1 | 12 |
| 2 | 11 |
| 3 | 12 |
| 4 | 12 |
| **Total** | **58** |

모든 Fold에서 target class coverage 검증을 통과했다.

### 학습 결과

| Fold | Best Epoch | Best Validation Macro AUC |
|---|---:|---:|
| Fold 0 | 1 | **0.751323** |
| Fold 1 | 3 | **0.835174** |
| Fold 2 | 3 | **0.813294** |
| Fold 3 | 3 | **0.761872** |
| Fold 4 | 3 | **0.858336** |

### 실행 특성
- Trainable parameters: 약 **4.16M**
- Total parameters: 약 **22.66M**
- 각 Fold 학습 시간: 약 **10분**
- 전체 4,407 study DICOM precache:
  - 약 40~43분
  - cache errors: 0
  - 평균 valid slots: 6.0
- GPU VRAM 사용량은 T4 용량 대비 낮아 계산 자원 여유가 확인되었다.

### 인사이트
- Fold별 validation AUC 차이가 상당히 컸다.
- 11~12 Gold validation sample만으로 Fold 자체의 우열을 판단하기 어렵다.
- 동일 architecture와 거의 동일한 학습 데이터라도,
  - held-out Gold 차이
  - fold-aware pseudo-label 차이
  - Fold별 seed 차이
  때문에 서로 다른 예측을 생성했다.

---

## Experiment 06 — V2.1 Fold 0~2 Partial OOF

### 구성
- Fold 0, 1, 2 validation prediction 결합
- 총 **34 Gold studies**
- 각 study는 자신을 학습하지 않은 Fold model prediction만 사용

### 결과
- **Partial OOF Macro AUC: 0.779997**

### Target AUC
- ACL: 0.703571
- MCL: 0.779310
- Medial Meniscus: 0.652632
- Lateral Meniscus: 0.794872
- Medial OA: 0.893333
- Lateral OA: 0.761905
- PF OA: 0.848485
- Effusion: 0.859848
- Synovitis: 0.750865
- Baker's: 0.835979
- Contusion: 0.779167
- Fracture: 0.700000

### 인사이트
- 상대적으로 약했던 target:
  - Medial Meniscus
  - Fracture
  - ACL
  - Synovitis
- 상대적으로 강했던 target:
  - Medial OA
  - Effusion
  - PF OA
  - Baker's
- 34명 기준이므로 target별 AUC는 여전히 표본 변동성이 컸다.

---

## Experiment 07 — V2.1 Fold 3~4 Partial OOF

### 구성
- Fold 3, 4 validation prediction 결합
- 총 **24 Gold studies**

### 결과
- **Partial OOF Macro AUC: 0.805944**

### Target AUC
- ACL: 0.814286
- MCL: 0.625000
- Medial Meniscus: 0.706294
- Lateral Meniscus: 0.671429
- Medial OA: 0.953704
- Lateral OA: 0.912500
- PF OA: 0.629630
- Effusion: 0.888112
- Synovitis: 0.707143
- Baker's: 0.936842
- Contusion: 0.888889
- Fracture: 0.937500

### 인사이트
- Fold 0~2 partial OOF와 약점/강점 패턴이 크게 달랐다.
- 작은 Gold validation subset에서는 target별 AUC가 Fold split에 매우 민감했다.
- Fold3~4에서는 Fracture가 매우 높았지만 MCL/PF OA는 낮아, Fold별 모델이 서로 보완적인 예측을 만들 가능성을 확인했다.

---

## Experiment 08 — V2.1 3-Fold Ensemble Submission

### 구성
- Models:
  - Fold 0 best
  - Fold 1 best
  - Fold 2 best
- 각 checkpoint가 test MRI를 독립적으로 inference
- Ensemble:
  - **Equal-weight arithmetic mean of sigmoid probabilities**
- Rank averaging / validation-AUC weighting 사용하지 않음

### Test inference 진단
- Prediction stack: `(3, 3, 12)`
- Mean model disagreement (prediction std): **0.06988**
- Ensemble probability range: 약 **0.1741 ~ 0.7019**

### Submission 결과
- **Public LB: 0.810**

### 비교
- V2 Fold0 single: 0.804
- V2.1 3-Fold Ensemble: **0.810**
- 변화: **+0.006**

### 인사이트
- 거의 같은 데이터로 학습한 Fold 모델들도 충분한 prediction diversity를 보였다.
- Equal-weight probability ensemble만으로 single model보다 Public LB가 개선되었다.
- Fold validation AUC 기반 가중치를 사용하지 않아도 ensemble 효과가 확인되었다.

---

## Experiment 09 — V2.1 5-Fold Ensemble Submission

### 구성
- Models:
  - Fold 0 best
  - Fold 1 best
  - Fold 2 best
  - Fold 3 best
  - Fold 4 best
- Ensemble:
  - **Equal-weight arithmetic mean of sigmoid probabilities**
- 3-Fold와 동일한 preprocessing / architecture / inference 방식 유지

### Test inference 진단
- Prediction stack: `(5, 3, 12)`
- Mean model disagreement (prediction std): **0.07295**
- Ensemble probability range: 약 **0.1603 ~ 0.7264**

### Submission 결과
- **Public LB: 0.816**

### 비교

| Experiment | Public LB |
|---|---:|
| V1.1 single | 0.554 |
| V2 Fold0 single | 0.804 |
| V2.1 3-Fold Ensemble | 0.810 |
| V2.1 5-Fold Ensemble | **0.816** |

### 인사이트
- Fold 3, 4를 추가한 뒤 Public LB가 **0.810 → 0.816**으로 추가 상승했다.
- single → 3-fold → 5-fold 순서로 Public LB가 일관되게 증가했다.
- Fold 3, 4는 기존 Fold 0~2와 완전히 동일한 예측을 반복하지 않았고, ensemble diversity를 추가했다.
- 현재 완료된 submission 실험 중 **V2.1 5-Fold equal-weight probability ensemble이 최고 점수**다.

---

## Experiment 10 — Full 58-Gold OOF Analysis

### 구성
각 Fold의 held-out validation prediction을 연결했다.

- Fold 0: 11 Gold
- Fold 1: 12 Gold
- Fold 2: 11 Gold
- Fold 3: 12 Gold
- Fold 4: 12 Gold
- Total: **58 unique Gold studies**

각 Gold study는 자신을 학습하지 않은 Fold model에 의해 정확히 한 번 예측되었다.

### Full pooled OOF 결과
- **Macro ROC-AUC: 0.784485**

### Target별 Full OOF AUC

| Target | AUC | Positive / Negative |
|---|---:|---:|
| Medial Meniscus | **0.6707** | 26 / 32 |
| MCL | **0.7075** | 9 / 49 |
| PF OA | **0.7336** | 21 / 37 |
| Lateral Meniscus | **0.7354** | 23 / 35 |
| Synovitis | **0.7407** | 27 / 31 |
| ACL | **0.7561** | 24 / 34 |
| Fracture | **0.8042** | 18 / 40 |
| Contusion | **0.8124** | 19 / 39 |
| Lateral OA | **0.8221** | 11 / 47 |
| Effusion | **0.8621** | 35 / 23 |
| Baker's | **0.8714** | 12 / 46 |
| Medial OA | **0.8977** | 15 / 43 |

### 추가 진단
- 5개 Fold Macro AUC 단순 평균: **약 0.8040**
- Raw pooled OOF Macro AUC: **0.7845**
- Fold 내부 percentile-rank normalization 후 pooled OOF: **약 0.7988**
- Study-level bootstrap 95% 구간: **약 0.737 ~ 0.827**

### 인사이트
- Fold별 raw probability calibration 차이가 pooled ranking을 일부 악화시켰다.
- 다섯 Fold의 Macro AUC 평균과 pooled OOF AUC는 같은 지표가 아니다.
- 내부에서 가장 약한 target:
  - Medial Meniscus
  - MCL
  - PF OA
  - Lateral Meniscus
  - Synovitis
  - ACL
- 내부에서 상대적으로 강한 target:
  - Medial OA
  - Baker's
  - Effusion
- Gold가 총 58명뿐이므로 target별 AUC와 bootstrap 구간의 불확실성이 상당하다.


---

## Experiment 11 — V2.2 Gold / Pseudo Loss Split

### 변경 사항
V2.1의 model, preprocessing, optimizer, learning rate, batch, epoch, fold split은 그대로 유지하고 loss 계산만 변경했다.

- Gold:
  - binary Gold label 사용
  - Gold training subset에서 계산한 `pos_weight` 적용
- Pseudo:
  - V4 soft pseudo-label 유지
  - `pos_weight` 적용 제거
  - 기존 `pseudo_weight × confidence` 유지
- Gold / pseudo 전체 상대 weight와 global normalization 방식은 V2.1과 동일
- Gold oversampling / source balancing은 적용하지 않음

### Loss 검증
실제 학습 전 sanity check에서 loss 분리가 의도대로 동작하는지 확인했다.

```text
LOSS CONTRACT: PASS
Gold loss responds to pos_weight : YES
Pseudo loss responds to pos_weight: NO
```

### 학습 결과

| Fold | Best Epoch | Best Validation Macro AUC |
|---|---:|---:|
| Fold 0 | 3 | 0.722421 |
| Fold 1 | 3 | 0.828822 |
| Fold 2 | 3 | 0.792196 |
| Fold 3 | 3 | 0.770208 |
| Fold 4 | 3 | 0.842416 |

### 실행 특성
- 전체 Fold training time: 약 **63.74분**
- 4,407-study precache: **37.08분**
- Cache files: 4,407
- Cache errors: 0
- 평균 valid slots: 6.0

### Full 58-Gold OOF 결과
- **Macro ROC-AUC: 0.793107**
- V2.1 Full OOF: 0.784485
- 변화: **+0.008622**

### Target별 Full OOF AUC

| Target | V2.1 | V2.2 | 변화 |
|---|---:|---:|---:|
| Medial Meniscus | 0.6707 | **0.6911** | **+0.0204** |
| MCL | 0.7075 | **0.7098** | +0.0023 |
| PF OA | **0.7336** | 0.7284 | -0.0052 |
| Lateral Meniscus | 0.7354 | **0.7391** | +0.0037 |
| ACL | 0.7561 | **0.7684** | **+0.0123** |
| Synovitis | 0.7407 | **0.7969** | **+0.0562** |
| Contusion | **0.8124** | 0.8043 | -0.0081 |
| Fracture | 0.8042 | **0.8083** | +0.0041 |
| Lateral OA | **0.8221** | 0.8143 | -0.0078 |
| Baker's | **0.8714** | 0.8496 | -0.0218 |
| Effusion | 0.8621 | **0.8969** | **+0.0348** |
| Medial OA | 0.8977 | **0.9101** | **+0.0124** |

### Loss 진단
Gold loss와 pseudo loss를 별도로 기록했다.

예: Fold 0 Epoch 3

```text
train_loss  = 0.47412
gold_loss   = 0.78675
pseudo_loss = 0.46633
```

전체 train loss가 pseudo loss에 매우 가까웠고, Gold supervision의 유효 loss 기여 비중은 약 **2~3% 수준**이었다.

### 5-Fold Ensemble Submission

#### 구성
- Fold 0~4 V2.2 best checkpoint 사용
- V2.1과 동일한 inference preprocessing / architecture
- **Equal-weight arithmetic mean of sigmoid probabilities**

#### Test inference 진단
- Prediction stack: `(5, 3, 12)`
- Mean model disagreement: **0.05523**
- Ensemble probability range: 약 **0.0745 ~ 0.7565**

#### Submission 결과
- **Public LB: 0.816**

### 비교

| Version | Full 58-Gold OOF | Public LB |
|---|---:|---:|
| V2.1 5-Fold | 0.784485 | **0.816** |
| V2.2 Loss-Split 5-Fold | **0.793107** | **0.816** |

### 인사이트
- pseudo-label에 Gold-derived `pos_weight`를 제거한 뒤 **Full OOF가 0.784485 → 0.793107로 개선**됐다.
- 특히 Synovitis, Effusion, Medial Meniscus, ACL에서 OOF 개선 폭이 컸다.
- 일부 target은 하락했지만 전체 Macro AUC는 상승했다.
- Public LB는 0.816으로 V2.1과 동일했다.
- visible 3-study test는 sample/example data이며 실제 Public LB scoring은 hidden test set으로 수행된다.
- 내부 OOF는 개선되고 Public LB는 하락하지 않아, loss split 변경은 내부 검증 기준으로 유효했다.
- Gold와 pseudo loss를 분리해보니 Gold supervision의 전체 loss 기여가 여전히 매우 작다는 점도 확인됐다.

---

---

## Experiment 12 — V2.3 Gold Oversampling ×10

### 변경 사항
V2.2 Loss-Split을 그대로 유지하고 **Gold study 노출 빈도만 10배로 강화**했다.

- Pseudo study: epoch마다 1회
- Gold study: epoch마다 10회
- Validation Gold: oversampling하지 않음
- V2.2 Gold / pseudo loss split 유지
- Gold `pos_weight` 유지
- Pseudo confidence weighting 유지
- Model / preprocessing / LR / batch / fold split은 V2.2와 동일
- Gold effective supervision weight share는 약 **20% 수준**으로 증가

### 학습 결과

| Fold | Best Epoch | Best Validation Macro AUC |
|---|---:|---:|
| Fold 0 | 3 | 0.759623 |
| Fold 1 | 3 | 0.829437 |
| Fold 2 | 3 | 0.788955 |
| Fold 3 | 3 | 0.781217 |
| Fold 4 | 2 | 0.804911 |

### Full 58-Gold OOF 결과
- **Macro ROC-AUC: 0.773342**
- V2.2 Full OOF: 0.793107
- 변화: **-0.019765**

### Target별 Full OOF AUC

| Target | V2.2 | V2.3 | 변화 |
|---|---:|---:|---:|
| Medial Meniscus | 0.691106 | 0.627404 | -0.063702 |
| MCL | 0.709751 | **0.766440** | **+0.056689** |
| PF OA | 0.728443 | **0.734878** | +0.006435 |
| Lateral Meniscus | 0.739130 | 0.708075 | -0.031055 |
| ACL | 0.768382 | **0.795343** | **+0.026961** |
| Synovitis | 0.796894 | 0.735962 | -0.060932 |
| Contusion | 0.804318 | 0.762483 | -0.041835 |
| Fracture | 0.808333 | 0.666667 | **-0.141666** |
| Lateral OA | 0.814313 | 0.793037 | -0.021276 |
| Baker's | 0.849638 | **0.914855** | **+0.065217** |
| Effusion | 0.896894 | 0.850932 | -0.045962 |
| Medial OA | 0.910078 | **0.924031** | +0.013953 |

### 인사이트
- Gold signal을 전체적으로 10배 강화하는 방식은 **Full OOF 기준 성능이 하락**했다.
- MCL, ACL, Baker's, Medial OA에서는 상승했지만, Fracture / Meniscus / Synovitis 등 여러 target이 크게 하락했다.
- 모든 target에 동일한 강도로 Gold supervision을 강화하는 방식보다 **target별 특성을 고려한 조정이 필요**하다는 신호를 확인했다.
- Public LB 제출은 진행하지 않았다.

---

## Experiment 13 — V2.4 Batch / Learning-Rate Search

### 목적
V2.2 Loss-Split baseline 위에서 **batch size와 learning rate 범위**를 내부 Gold validation으로 탐색했다.

### Stage A — Throughput / VRAM Benchmark

| Physical Batch | Throughput | Peak Allocated VRAM |
|---:|---:|---:|
| 4 | 22.27 studies/s | 0.54 GB |
| 8 | 24.72 studies/s | 0.94 GB |
| 16 | 24.98 studies/s | 1.71 GB |
| 32 | **28.47 studies/s** | 3.25 GB |

- Batch 32까지 OOM 없이 정상 동작했다.
- Batch 4 대비 Batch 32 throughput은 약 **+28%**였다.
- Batch 32는 이 단계에서 **성능 탐색이 아니라 hardware throughput만 측정**했다.

### Stage B / C — Performance Search

탐색 후보:

```text
Batch 4  : Head LR 5e-5 / 1e-4 / 2e-4
Batch 8  : Head LR 1e-4 / 2e-4 / 4e-4
Batch 16 : Head LR 1e-4 / 2e-4 / 4e-4
```

- Backbone LR은 coarse search에서 Head LR의 `1/10`
- Fold 0 + 4로 23-Gold coarse search
- 상위 후보 + baseline을 Fold 1에 추가
- Fold 0 + 1 + 4, 총 **35 Gold pooled OOF**로 최종 비교

### 최종 Search Winner

| Candidate | Batch | Head LR | Backbone LR | 35-Gold Pooled AUC |
|---|---:|---:|---:|---:|
| **b4_h2e-4** | **4** | **2e-4** | **2e-5** | **0.795854** |
| b4_h1e-4 baseline | 4 | 1e-4 | 1e-5 | 0.794909 |
| b4_h5e-5 | 4 | 5e-5 | 5e-6 | 0.774623 |

- Search winner의 baseline 대비 변화: **+0.000945**
- 차이가 매우 작아 **새 baseline으로 확정하지 않았다.**
- Full 58-Gold 확인 없이 35-Gold search 결과만으로 채택하지 않았다.

### Target별 변화 — 2e-4 / 2e-5 vs baseline

| Target | Baseline | Candidate | 변화 |
|---|---:|---:|---:|
| MCL | 0.591954 | **0.672414** | **+0.080460** |
| Baker's | 0.872449 | **0.933673** | **+0.061224** |
| ACL | 0.785714 | **0.846939** | **+0.061224** |
| Fracture | 0.848485 | **0.890152** | +0.041667 |
| Lateral OA | 0.688776 | **0.719388** | +0.030612 |
| Contusion | 0.821970 | **0.844697** | +0.022727 |
| Medial OA | 0.910256 | **0.927350** | +0.017094 |
| PF OA | 0.751748 | 0.741259 | -0.010490 |
| Effusion | 0.920000 | 0.893333 | -0.026667 |
| Lateral Meniscus | 0.755102 | 0.727891 | -0.027211 |
| Synovitis | 0.815789 | 0.763158 | -0.052632 |
| Medial Meniscus | 0.776667 | 0.590000 | **-0.186667** |

### 인사이트
- **Batch 4가 성능 탐색 상위권을 유지**했다.
- Batch 32는 throughput과 VRAM 측면에서 충분히 실행 가능함을 확인했다.
- Head LR `2e-4` / Backbone LR `2e-5`는 전체 평균에서는 약한 상승 신호가 있었지만 target별 편차가 매우 컸다.
- 특히 Meniscus 계열은 높은 LR 설정에서 하락해, 하나의 LR 조합이 모든 target에 동일하게 유리하지 않음을 확인했다.
- Public LB 제출은 진행하지 않았다.

---

## Experiment 14 — V2.5 Adjacent Slice Triplet 5-Fold

### 변경 사항
V2.2를 baseline으로 유지하고 **slice sampling 방식만 변경**했다.

기존 V2.2:
- 12~88% 구간에서 9 slices를 넓게 equal-spaced sampling
- 넓은 anatomical coverage 확보

V2.5:
- 3 anatomical anchors
- 각 anchor에서 `[center-1, center, center+1]`
- **3 anchors × adjacent 3-slice triplet = 9 slices**
- 각 3-channel group이 실제 인접 MRI slice로 구성되도록 변경

고정 조건:
- DINOv2 Small
- 224 × 224
- 130 mm crop
- V4 fold-aware pseudo labels
- V2.2 Gold / pseudo loss split
- Batch 4 / Grad Accum 1
- Head LR `1e-4`
- Backbone LR `1e-5`
- Max epoch 3
- Gold oversampling 없음

### 학습 결과

| Fold | Best Epoch | Best Validation Macro AUC |
|---|---:|---:|
| Fold 0 | 3 | 0.708796 |
| Fold 1 | 3 | 0.814534 |
| Fold 2 | 3 | 0.784160 |
| Fold 3 | 3 | 0.776866 |
| Fold 4 | 3 | 0.856586 |

### Full 58-Gold OOF 결과
- **Macro ROC-AUC: 0.778191**
- V2.2 baseline: 0.793107
- 변화: **-0.014916**

### Target별 Full OOF AUC

| Target | V2.2 | V2.5 Adjacent | 변화 |
|---|---:|---:|---:|
| **Medial Meniscus** | 0.691106 | **0.731971** | **+0.040865** |
| MCL | 0.709751 | 0.650794 | -0.058957 |
| PF OA | 0.728443 | 0.693694 | -0.034749 |
| **Lateral Meniscus** | 0.739130 | **0.793789** | **+0.054659** |
| ACL | 0.768382 | 0.751225 | -0.017157 |
| Synovitis | 0.796894 | 0.738351 | -0.058543 |
| Contusion | 0.804318 | **0.817814** | +0.013496 |
| Fracture | 0.808333 | 0.798611 | -0.009722 |
| Lateral OA | 0.814313 | **0.831721** | +0.017408 |
| Baker's | 0.849638 | 0.836957 | -0.012681 |
| Effusion | 0.896894 | 0.817391 | **-0.079503** |
| Medial OA | 0.910078 | 0.875969 | -0.034109 |

### 5-Fold Ensemble Submission

#### 구성
- Fold 0~4 V2.5 best checkpoint
- V2.5 adjacent preprocessing 동일 유지
- **Equal-weight arithmetic mean of sigmoid probabilities**

#### Submission 결과
- **Public LB: 0.807**
- V2.2 Public LB: 0.816
- 변화: **-0.009**

### 인사이트
- Adjacent Triplet을 모든 target에 적용하는 방식은 **OOF와 Public LB 모두 하락**했다.
- Full OOF 하락 방향이 Public LB에서도 재현되어, 현재 Full 58-Gold OOF를 실험 선택 기준으로 사용하는 것이 유효하다는 추가 근거를 얻었다.
- 반면 **Medial Meniscus와 Lateral Meniscus는 둘 다 명확하게 상승**했다.
- Meniscus 계열은 넓은 slice coverage보다 **local adjacent context**의 도움을 받을 가능성이 확인됐다.
- 반대로 Effusion, MCL, Synovitis, PF OA 등은 wide context를 잃었을 때 손해가 컸다.
- 따라서 Adjacent sampling은 global replacement보다 **target-specific context로서 가치가 있는 신호**를 남겼다.

---

## Completed Experiment Scoreboard

| ID | Experiment | Internal Metric | Public LB |
|---|---|---:|---:|
| 01 | V1.1 single submission | - | 0.554 |
| 04 | V2 DINOv2-S Fold0 single | Fold0 Val AUC 0.750099 | 0.804 |
| 06 | V2.1 Fold0~2 Partial OOF | 0.779997 | - |
| 07 | V2.1 Fold3~4 Partial OOF | 0.805944 | - |
| 08 | V2.1 3-Fold Ensemble | - | 0.810 |
| 09 | V2.1 5-Fold Ensemble | - | **0.816** |
| 10 | V2.1 Full 58-Gold OOF | 0.784485 | - |
| 11 | V2.2 Loss-Split 5-Fold | **Full OOF 0.793107** | **0.816** |
| 12 | V2.3 Gold Oversampling ×10 | Full OOF 0.773342 | - |
| 13 | V2.4 Batch / LR Search | 35-Gold Search AUC 0.795854 | - |
| 14 | V2.5 Adjacent Triplet 5-Fold | Full OOF 0.778191 | 0.807 |

---

## Current Best Completed Submission

- **Public LB 공동 최고: V2.1 5-Fold / V2.2 Loss-Split 5-Fold**
- **Public LB: 0.816**
- Full 58-Gold OOF:
  - V2.1: 0.784485
  - V2.2 Loss-Split: **0.793107**
  - V2.3 Gold ×10: 0.773342
  - V2.5 Adjacent Triplet: 0.778191
- 현재 완료된 Full 58-Gold 실험 중 **V2.2 Loss-Split이 최고 OOF**
- Backbone: DINOv2-S
- V4 Consensus fold-aware pseudo supervision
- 5-Fold equal-weight probability mean
- V2.5에서 **Medial / Lateral Meniscus에 대한 adjacent local-context 개선 신호** 확인
