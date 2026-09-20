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

## Experiment 15 — V2.6A Meniscus Hybrid Controlled 5-Fold

### 목적
V2.5에서 확인된 **Meniscus adjacent-context 개선 신호**를 전체 target에 적용하지 않고, Medial / Lateral Meniscus에만 선택적으로 적용했다.

### 구성
- Shared backbone: **DINOv2 Small**
- Shared `GroupAttention` / `LabelSpecificSlotHead`
- Target routing:
  - Medial Meniscus → Adjacent branch
  - Lateral Meniscus → Adjacent branch
  - 나머지 10 targets → V2.2 Wide branch
- 두 branch는 동일한 backbone / pooling / head parameter를 공유
- Batch 4 / Grad Accum 1 / Effective batch 4
- Head LR `1e-4` / Backbone LR `1e-5`
- Max epoch 3
- V2.2 Gold / pseudo loss split 유지
- Gold oversampling 없음

### 학습 결과

| Fold | Best Epoch | Best Validation Macro AUC |
|---|---:|---:|
| Fold 0 | 3 | 0.731316 |
| Fold 1 | 3 | 0.781917 |
| Fold 2 | 3 | 0.799206 |
| Fold 3 | 3 | 0.762621 |
| Fold 4 | 2 | **0.863803** |

### Full 58-Gold OOF 결과
- **Macro ROC-AUC: 0.784614**
- V2.2 baseline: 0.793107
- 변화: **-0.008493**

### Target별 Full OOF AUC

| Target | V2.2 | V2.6A | 변화 |
|---|---:|---:|---:|
| MCL | 0.709751 | 0.664399 | -0.045352 |
| PF OA | 0.728443 | 0.740026 | +0.011583 |
| **Medial Meniscus** | 0.691106 | **0.751202** | **+0.060096** |
| Contusion | 0.804318 | 0.754386 | -0.049932 |
| **Lateral Meniscus** | 0.739130 | **0.763975** | **+0.024845** |
| Synovitis | 0.796894 | 0.765830 | -0.031064 |
| Fracture | 0.808333 | 0.766667 | -0.041666 |
| ACL | 0.768382 | 0.775735 | +0.007353 |
| Lateral OA | 0.814313 | 0.789168 | -0.025145 |
| Baker's | 0.849638 | 0.858696 | +0.009058 |
| Medial OA | 0.910078 | 0.875969 | -0.034109 |
| Effusion | 0.896894 | 0.909317 | +0.012423 |

### 인사이트
- Hybrid routing을 적용했지만 **전체 Macro AUC는 V2.2보다 하락**했다.
- 반면 Medial Meniscus는 +0.0601, Lateral Meniscus는 +0.0248 상승해 adjacent local-context가 Meniscus 계열에 유효하다는 신호가 다시 확인됐다.
- 두 branch가 backbone / pooling / head를 공유하므로 Meniscus용 adjacent branch의 gradient가 다른 target representation에도 영향을 줄 수 있다.
- 여러 non-Meniscus target이 동시에 하락한 결과는 **shared-gradient interference 가능성과 일치**하지만, Gold 58개 기준 실험만으로 인과관계를 확정할 수는 없다.
- Public LB 제출은 진행하지 않았다.

---

## Experiment 16 — V2.6B Meniscus Hybrid Long-Horizon 5-Fold

### 목적
V2.6A와 동일한 Meniscus hybrid routing을 유지하면서, 더 큰 effective batch와 긴 학습 horizon, step-wise warmup / linear decay를 적용했다.

### 구성
- Target routing:
  - Medial Meniscus / Lateral Meniscus → Adjacent branch
  - 나머지 10 targets → Wide branch
- Shared DINOv2-S backbone / pooling / head
- Physical batch: **32**
- Gradient accumulation: **2**
- Effective batch: **64**
- Peak Head LR: **2e-4**
- Peak Backbone LR: **1e-5**
- Max epoch: **48**
- Early stopping patience: **6**
- Warmup: 전체 optimizer-step budget의 **5%**
- Scheduler: optimizer update 기준 **linear decay**
- V2.2 Gold / pseudo loss split 유지
- Gold oversampling 없음

### 학습 결과

| Fold | Best Epoch | Best Validation Macro AUC |
|---|---:|---:|
| Fold 0 | 15 | 0.773082 |
| Fold 1 | 8 | 0.793510 |
| Fold 2 | 11 | **0.844907** |
| Fold 3 | 12 | 0.810232 |
| Fold 4 | 9 | **0.885863** |

- Best epoch가 모든 Fold에서 **8~15 epoch** 범위에 형성됐다.
- 기존 3-epoch 실험보다 긴 training horizon이 실제 checkpoint 선택에 영향을 주는 것을 확인했다.

### Full 58-Gold OOF 결과
- **Macro ROC-AUC: 0.807992**
- V2.2 baseline: 0.793107
- 변화: **+0.014885**
- 현재 완료된 Full 58-Gold 실험 중 **최고 OOF**

### Target별 Full OOF AUC

| Target | V2.2 | V2.6B | 변화 |
|---|---:|---:|---:|
| MCL | 0.709751 | 0.691610 | -0.018141 |
| Synovitis | 0.796894 | 0.734767 | -0.062127 |
| Lateral Meniscus | 0.739130 | 0.737888 | -0.001242 |
| **Medial Meniscus** | 0.691106 | **0.743990** | **+0.052884** |
| PF OA | 0.728443 | **0.760618** | **+0.032175** |
| Fracture | 0.808333 | 0.776389 | -0.031944 |
| ACL | 0.768382 | **0.818627** | **+0.050245** |
| Lateral OA | 0.814313 | **0.820116** | +0.005803 |
| Contusion | 0.804318 | **0.855601** | **+0.051283** |
| Baker's | 0.849638 | **0.902174** | **+0.052536** |
| Effusion | 0.896894 | **0.906832** | +0.009938 |
| Medial OA | 0.910078 | **0.947287** | **+0.037209** |

### 5-Fold Ensemble Submission
- Fold 0~4 V2.6B best checkpoint
- 학습과 동일한 static target routing 유지
- Fold별 sigmoid probability를 **equal-weight arithmetic mean**

### Submission 결과
- **Public LB: 0.814**
- 기존 Public 최고: 0.816
- 변화: **-0.002**

### 인사이트
- 내부 Full OOF는 **0.807992로 최고 기록**을 갱신했지만, Public LB는 **0.814**로 기존 최고 0.816보다 소폭 낮았다.
- 따라서 58-Gold OOF는 실험 방향을 비교하는 내부 지표로는 유용하지만, 작은 validation population 특성상 Public LB의 절대 점수를 정밀하게 대변하지는 못한다.
- V2.6A에서 Hybrid만 적용했을 때는 전체 OOF가 하락했지만, V2.6B에서는 batch / effective batch / LR / scheduler / training horizon을 함께 변경한 뒤 OOF가 상승했다.
- 따라서 V2.6B의 상승을 **Hybrid 단독 효과로 해석할 수 없으며**, long-horizon optimization package의 영향이 포함된 결과로 해석한다.
- Medial Meniscus는 V2.6A와 V2.6B에서 반복적으로 개선되어 local adjacent-context 활용 가치가 다시 확인됐다.
- 반면 MCL, Synovitis, Fracture 등은 여전히 약하거나 하락해 target별 representation / expert 구조 개선 필요성이 남았다.
---

## Experiment 17 — Exp1A DINOv2 Last4 Layer-wise LR, Fold2 Screening

### 목적
V2.2 Wide-only MRI input과 V2.6B의 long-horizon optimization을 유지하면서, DINOv2-S의 fine-tuning 범위를 Last2에서 **Last4 blocks**로 확장했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Input: V2.2 **Wide-only**
- DINOv2-Small
- Fine-tuning: **Last4**
- Layer-wise LR: 이전 2 blocks `3e-6`, 마지막 2 blocks `1e-5`, Head `2e-4`
- Physical batch: **64**
- Gradient accumulation: **1**
- Effective batch: **64**
- Warmup: optimizer-step budget의 5%
- Scheduler: step-wise linear decay
- Max epoch: 48
- Early stopping patience: 6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Best Macro ROC-AUC: 0.818585**
- Best epoch: **7**
- Weak-6 Macro AUC: **0.753571**
- V2.6B Fold2 reference: 0.844907
- 변화: **-0.026323**
- Training time: 약 **34.58분**

### Target별 Fold2 AUC

| Target | AUC |
|---|---:|
| Fracture | 0.333333 |
| Medial Meniscus | 0.607143 |
| Contusion | 0.750000 |
| PF OA | 0.785714 |
| ACL | 0.833333 |
| Effusion | 0.857143 |
| Synovitis | 0.866667 |
| Medial OA | 0.916667 |
| Lateral Meniscus | 0.928571 |
| Baker's | 0.944444 |
| Lateral OA | 1.000000 |
| MCL | 1.000000 |

### 인사이트
- Last4로 fine-tuning 범위를 확장했지만 기존 V2.6B Fold2 기준보다 성능이 낮았다.
- Best epoch가 7로 형성되어, 3-epoch 제한보다 long-horizon 학습이 유효하다는 신호는 유지됐다.
- Lateral Meniscus / MCL 등 일부 target은 높았지만 Fracture와 Medial Meniscus가 크게 낮아 전체 Macro를 제한했다.
- 이 결과만으로 Last4 자체의 효과를 분리할 수는 없으며, 현재 Fold2 screening 기준에서는 승격하지 않았다.

---

## Experiment 18 — Exp1B DINOv2 Full Fine-tuning + Layer-wise LR, Fold2 Screening

### 목적
동일한 Wide-only input과 long-horizon optimization을 유지하면서, DINOv2-S의 **전체 12 blocks를 fine-tuning**하고 conservative layer-wise LR을 적용했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Input: V2.2 **Wide-only**
- DINOv2-Small
- Fine-tuning: **Full 12 blocks**
- Layer-wise LR: Early third `1e-6`, Middle third `3e-6`, Late third `1e-5`, Head `2e-4`
- Gradient checkpointing: **ON**
- Physical batch: **16**
- Gradient accumulation: **4**
- Effective batch: **64**
- Warmup: optimizer-step budget의 5%
- Scheduler: step-wise linear decay
- Max epoch: 48
- Early stopping patience: 6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Best Macro ROC-AUC: 0.884127**
- Best epoch: **18**
- Weak-6 Macro AUC: **0.839484**
- V2.6B Fold2 reference: 0.844907
- 변화: **+0.039220**
- Exp1A 대비 변화: **+0.065542**
- Training time: 약 **127.96분**
- Early stop: epoch 24

### Target별 Fold2 AUC

| Target | AUC |
|---|---:|
| Fracture | 0.708333 |
| PF OA | 0.714286 |
| Contusion | 0.750000 |
| Medial Meniscus | 0.785714 |
| ACL | 0.900000 |
| Synovitis | 0.900000 |
| Lateral Meniscus | 0.928571 |
| Medial OA | 0.958333 |
| Effusion | 0.964286 |
| MCL | 1.000000 |
| Lateral OA | 1.000000 |
| Baker's | 1.000000 |

### 인사이트
- Full fine-tuning은 Fold2에서 **0.884127**을 기록해 현재 완료된 단일 Fold2 screening 중 최고 성능을 기록했다.
- V2.6B Fold2 0.844907 대비 **+0.039220** 개선됐다.
- Weak-6 Macro도 **0.839484**로 Exp1A보다 크게 개선됐다.
- Best epoch가 18에 형성되어 deeper fine-tuning에서도 long-horizon 학습이 필요했다.
- Full fine-tuning + layer-wise LR 조합은 이후 단일-Fold 구조 실험의 기준 backbone 설정으로 채택할 근거를 제공했다.
- Fold2 validation은 11 Gold에 불과하므로 이 점수는 internal screening metric이며 Public LB와 직접 대응하지 않는다.

---

## Experiment 19 — Exp2A Full FT + Target-specific Patch-token Spatial Attention, Fold2 Screening

### 목적
Exp1B의 Full DINOv2-S fine-tuning + layer-wise LR을 유지하면서, 기존 `CLS + patch_mean` 압축 대신 **target별 patch-token spatial attention**을 적용해 각 target이 서로 다른 spatial evidence를 선택하도록 했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Persistent Wide224 cache 사용
- DINOv2-Small **Full fine-tuning**
- Target-specific patch-token spatial attention
- Physical batch: **64**
- Gradient accumulation: **1**
- Effective batch: **64**
- Layer-wise LR: Early `1e-6` / Middle `3e-6` / Late `1e-5`
- Head LR: `2e-4`
- Gradient checkpointing: ON
- Max epoch: 48
- Early stopping patience: 6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Best Macro ROC-AUC: 0.889120**
- Best epoch: **14**
- Early stop: epoch **20**
- Weak-6 Macro AUC: **0.847421**
- Exp1B Fold2: 0.884127
- 변화: **+0.004993**
- Weak-6 변화: **+0.007937**
- Training time: 약 **105.75분**
- Persistent cache contract: PASS
- Runtime DICOM precache: 없음
- T4 ×2에서 Batch64 정상 실행

### Target별 Fold2 AUC

| Target | AUC | Exp1B 대비 |
|---|---:|---:|
| Lateral Meniscus | 0.607143 | -0.321428 |
| Fracture | 0.791667 | +0.083334 |
| PF OA | 0.857143 | +0.142857 |
| ACL | 0.866667 | -0.033333 |
| Effusion | 0.892857 | -0.071429 |
| MCL | 0.900000 | -0.100000 |
| Medial OA | 0.916667 | -0.041666 |
| Medial Meniscus | 0.928571 | +0.142857 |
| Lateral OA | 0.944444 | -0.055556 |
| Contusion | 0.964286 | +0.214286 |
| Baker's | 1.000000 | 0.000000 |
| Synovitis | 1.000000 | +0.100000 |

### 인사이트
- 전체 Fold2 Macro는 Exp1B 대비 **+0.004993** 상승해 현재 완료된 단일 Fold2 screening 최고 기록을 갱신했다.
- Weak-6 Macro도 **0.847421**로 상승했다.
- Fracture / PF OA / Medial Meniscus / Contusion / Synovitis는 개선되어 patch-level spatial evidence 활용 가치가 확인됐다.
- 반면 Lateral Meniscus가 0.928571 → 0.607143으로 크게 하락했고, 여러 강한 target도 함께 낮아졌다.
- 따라서 patch-token spatial attention을 기존 global feature의 완전한 대체로 사용하는 방식보다는, **global representation을 보존하면서 spatial context를 residual/gated 형태로 추가하는 구조**가 더 적합할 가능성을 시사한다.
- Fold2 Gold가 11명뿐이므로 target별 변화와 +0.004993 차이는 불확실성이 크며, Public LB 향상을 의미하지 않는다.

---

## Experiment 20 — Exp2B Full FT + Target-specific Low-rank Expert Head, Fold2 Screening

### 목적
Exp1B의 global image representation을 유지하고 upper head에 **12개 target-specific low-rank residual experts**를 추가해 target 간 representation interference를 줄일 수 있는지 확인했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Persistent Wide224 cache 사용
- DINOv2-Small **Full fine-tuning**
- 기존 `CLS + patch_mean` 유지
- Target-specific low-rank residual expert head
- Expert rank: **64**
- Expert up-projection zero initialization
- Physical batch: **64**
- Gradient accumulation: **1**
- Effective batch: **64**
- Layer-wise LR: Early `1e-6` / Middle `3e-6` / Late `1e-5`
- Head LR: `2e-4`
- Gradient checkpointing: ON
- Max epoch: 48
- Early stopping patience: 6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Best Macro ROC-AUC: 0.862765**
- Best epoch: **5**
- Early stop: epoch **11**
- Weak-6 Macro AUC: **0.847222**
- Exp1B Fold2: 0.884127
- 변화: **-0.021362**
- Weak-6 변화: **+0.007738**
- Training time: 약 **55.33분**
- Persistent cache contract: PASS
- Runtime DICOM precache: 없음
- T4 ×2에서 Batch64 정상 실행

### Target별 Fold2 AUC

| Target | AUC | Exp1B 대비 |
|---|---:|---:|
| Fracture | 0.583333 | -0.125000 |
| Medial Meniscus | 0.678571 | -0.107143 |
| Effusion | 0.821429 | -0.142857 |
| Medial OA | 0.833333 | -0.125000 |
| ACL | 0.833333 | -0.066667 |
| Baker's | 0.888889 | -0.111111 |
| PF OA | 0.892857 | +0.178571 |
| Contusion | 0.892857 | +0.142857 |
| Lateral Meniscus | 0.928571 | 0.000000 |
| MCL | 1.000000 | 0.000000 |
| Lateral OA | 1.000000 | 0.000000 |
| Synovitis | 1.000000 | +0.100000 |

### 인사이트
- Weak-6 Macro는 Exp1B보다 상승했지만 전체 Macro는 **-0.021362** 하락해 현재 구조는 승격하지 않았다.
- PF OA / Contusion / Synovitis는 개선됐지만 Fracture / Medial Meniscus / Effusion / Medial OA / ACL / Baker's가 하락했다.
- target-specific expert를 추가하는 것만으로는 전체 representation interference 문제가 해결되지 않았고, 일부 target 개선과 다른 target 하락이 동시에 나타났다.
- Best epoch가 5로 비교적 이르게 형성돼 Exp1B/Exp2A보다 빠르게 peak에 도달했다.
- Fold2 Gold가 11명뿐이므로 target별 변화의 인과는 확정할 수 없지만, 현재 screening 기준에서는 Exp2B를 다음 기준 구조로 채택하지 않는다.



---

## Experiment 21 — Exp3A Full FT + Global/Spatial Gated Residual, Fold2 Screening

### 목적
Exp1B의 안정적인 `CLS + patch_mean` global representation을 유지하면서, Exp2A의 target-specific patch attention을 **zero-initialized gated residual**로 추가했다.

Exp2A에서 spatial information 자체는 유효했지만 global representation을 완전히 대체하면서 Lateral Meniscus 등 일부 강한 target이 크게 하락했기 때문에, 이번 실험은 global path를 보존한 상태에서 spatial evidence를 보조 신호로 사용하는 구조를 검증했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Persistent Wide224 cache 사용
- DINOv2-Small **Full fine-tuning**
- Global path: `CLS + patch_mean`
- Spatial path: target당 patch query **1개**
- Fusion: `global + tanh(spatial_scale) × spatial_delta`
- Spatial scale initialization: **0.0**
- Global group-attention weight를 spatial branch에도 재사용
- Physical batch: **64**
- Gradient accumulation: **1**
- Effective batch: **64**
- Layer-wise LR: Early `1e-6` / Middle `3e-6` / Late `1e-5`
- Head LR: `2e-4`
- Gradient checkpointing: ON
- Max epoch: 48
- Early stopping patience: 6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Best Macro ROC-AUC: 0.895437**
- Best epoch: **12**
- Early stop: epoch **18**
- Weak-6 Macro AUC: **0.873810**
- Exp2A Fold2: 0.889120
- Macro 변화: **+0.006316**
- Weak-6 변화: **+0.026389**
- Training time: 약 **96.44분**

### Target별 Fold2 AUC

| Target | AUC | Exp2A 대비 | Learned Spatial Scale |
|---|---:|---:|---:|
| Fracture | 0.666667 | -0.125000 | -0.028865 |
| ACL | 0.800000 | -0.066667 | -0.024719 |
| PF OA | 0.821429 | -0.035714 | +0.016051 |
| Medial Meniscus | 0.821429 | -0.107142 | +0.009690 |
| Contusion | 0.821429 | -0.142857 | -0.011182 |
| Medial OA | 0.916667 | 0.000000 | +0.028468 |
| Synovitis | 0.933333 | -0.066667 | -0.018021 |
| Effusion | 0.964286 | +0.071429 | -0.032652 |
| Lateral OA | 1.000000 | +0.055556 | +0.028285 |
| Lateral Meniscus | 1.000000 | +0.392857 | -0.006233 |
| MCL | 1.000000 | +0.100000 | +0.017506 |
| Baker's | 1.000000 | 0.000000 | +0.012386 |

### 인사이트
- Global representation을 보존하고 spatial context를 residual로 추가하자 Fold2 Macro가 **0.895437**로 다시 상승했다.
- Exp2A에서 크게 무너졌던 Lateral Meniscus가 **0.607143 → 1.000000**으로 회복됐고, MCL / Effusion / Lateral OA도 개선됐다.
- 반면 Exp2A에서 높았던 Fracture / Medial Meniscus / Contusion은 다시 하락했다.
- Learned spatial scale은 target별로 서로 다른 부호와 크기를 학습해 spatial branch를 target-specific residual로 실제 사용했다.
- 현재 결과는 global-only와 spatial-only의 장점이 서로 보완적일 가능성을 보여주지만, Fold2 Gold 11명 기준이므로 target별 수치의 불확실성은 크다.

---

## Experiment 22 — Exp3B Full FT + Multi-query Global/Spatial Residual, Fold2 Screening

### 목적
Exp3A의 global-preserving residual fusion을 유지하면서, target당 spatial query를 **1개 → 4개**로 확장했다. 하나의 target이 서로 다른 위치/형태의 병변 evidence를 여러 spatial prototype으로 표현할 수 있는지 확인했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Persistent Wide224 cache 사용
- DINOv2-Small **Full fine-tuning**
- Global path: `CLS + patch_mean`
- Spatial path: target당 patch query **4개**
- 4개 spatial context를 target-specific learned softmax로 혼합
- Fusion: `global + tanh(spatial_scale) × spatial_delta`
- Spatial scale initialization: **0.0**
- Global group-attention weight를 spatial branch에도 재사용
- Physical batch: **64**
- Gradient accumulation: **1**
- Effective batch: **64**
- Layer-wise LR: Early `1e-6` / Middle `3e-6` / Late `1e-5`
- Head LR: `2e-4`
- Gradient checkpointing: ON
- Max epoch: 48
- Early stopping patience: 6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Best Macro ROC-AUC: 0.898710**
- Best epoch: **12**
- Early stop: epoch **18**
- Weak-6 Macro AUC: **0.867857**
- Exp2A Fold2: 0.889120
- Macro 변화: **+0.009590**
- Weak-6 변화: **+0.020437**
- Exp3A 대비 Macro: **+0.003274**
- Exp3A 대비 Weak-6: **-0.005952**
- Training time: 약 **94.84분**
- 0.900 marker까지 차이: **0.001290**

### Target별 Fold2 AUC

| Target | AUC | Exp2A 대비 | Learned Spatial Scale |
|---|---:|---:|---:|
| Fracture | 0.666667 | -0.125000 | -0.029620 |
| Medial Meniscus | 0.750000 | -0.178571 | +0.009878 |
| Contusion | 0.821429 | -0.142857 | -0.011205 |
| ACL | 0.833333 | -0.033334 | -0.023650 |
| PF OA | 0.892857 | +0.035714 | +0.016199 |
| Synovitis | 0.933333 | -0.066667 | -0.016917 |
| Medial OA | 0.958333 | +0.041666 | +0.028135 |
| Effusion | 0.964286 | +0.071429 | -0.030756 |
| Lateral Meniscus | 0.964286 | +0.357143 | -0.006041 |
| MCL | 1.000000 | +0.100000 | +0.016207 |
| Lateral OA | 1.000000 | +0.055556 | +0.028305 |
| Baker's | 1.000000 | 0.000000 | +0.011656 |

### 인사이트
- Multi-query residual은 Fold2 Macro를 **0.898710**까지 높여 현재 완료된 single-Fold screening 최고 기록을 갱신했다.
- Exp3A 대비 Macro는 +0.003274 개선됐지만 Weak-6는 -0.005952 낮아졌다.
- Exp3A와 비교하면 ACL / PF OA / Medial OA가 개선됐고, Medial / Lateral Meniscus는 낮아졌다.
- Exp3A와 Exp3B의 learned spatial scale 패턴이 매우 유사해, query 수 증가가 residual 사용량 자체보다 spatial context의 세부 표현을 변화시킨 것으로 보인다.
- 0.900 marker까지 차이는 약 0.00129로 매우 작지만, validation이 11 Gold에 불과하므로 이 차이를 절대적인 threshold로 해석해서는 안 된다.
- 현재 구조 탐색 결과는 **Full FT + global representation + gated spatial residual** 계열이 가장 일관된 개선 방향임을 지지한다.



---

## Experiment 23 — Exp3B Fold2 Single-Model Public LB Check

### 목적
Fold2 내부 validation에서 최고 성능을 기록한 **Exp3B Multi-query Global/Spatial Residual** checkpoint를 재학습하지 않고 그대로 hidden test에 inference하여, 단일 Fold 모델의 실제 Public LB 일반화 성능을 확인했다.

### 구성
- 사용 checkpoint: **Exp3B Fold2 best**
- Fold2 internal Macro ROC-AUC: **0.898710**
- Best epoch: **12**
- Training studies:
  - report-only pseudo: 4,349
  - Gold train: 47
  - Fold2 validation Gold: 11 제외
  - 총 train: **4,396 studies**
- DINOv2-Small Full fine-tuning
- Global path: `CLS + patch_mean`
- Spatial path: target당 query 4개
- Gated residual fusion
- Hidden test preprocessing: Wide224 / 130mm / 9 slices / 6 slots
- Submission: **Fold2 단일 모델 1개**, ensemble 없음

### Submission 결과
- **Public LB: 0.824**
- 기존 Public 최고: **0.816**
- 변화: **+0.008**
- 기존 최고는 V2.1 / V2.2의 **5-Fold ensemble**이었음
- 이번 결과는 **단일 Fold Exp3B 모델 하나가 기존 5-Fold 최고 기록을 넘어선 첫 결과**

### 인사이트
- Fold2 내부 성능 상승이 Public LB에서도 실제 개선으로 이어졌다.
- Exp3B의 Full FT + global representation + multi-query gated spatial residual 구조가 hidden test에서도 유효하다는 강한 근거를 확보했다.
- 단일 Fold 모델만으로 0.824를 기록했기 때문에, 이후 Fold ensemble에는 추가 상승 여지가 있을 수 있으나 상승 폭은 사전에 확정할 수 없다.
- 현재 단계에서는 5-Fold 전체 학습보다 단일 Fold screening + 선택적 LB 확인을 계속 사용하고, 최종 후보가 좁혀진 뒤 5-Fold ensemble을 수행하는 것이 계산 효율이 높다.
- Fold2 internal AUC 0.898710과 Public LB 0.824는 서로 다른 population / metric sample에 대한 값이므로 수치 자체를 직접 변환해 해석하지 않는다.



---

## Experiment 24 — Exp4A Target-specific Spatial Group Attention, Fold2 Screening

### 목적
Exp3B의 global path와 4-query spatial residual 구조는 유지하면서, spatial branch가 3개 slice group을 합칠 때 target별로 서로 다른 group weighting을 학습할 수 있는지 확인했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Persistent Wide224 cache 사용
- DINOv2-Small Full fine-tuning
- Global path: `CLS + patch_mean`
- Spatial queries: target당 4개
- 기존 target-level zero-init spatial residual gate 유지
- **추가:** global group-attention을 기준으로 target-specific group correction 학습
- target-specific correction은 0으로 초기화
- Batch64 / Accum1 / Effective64
- Max48 / Patience6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Best Macro ROC-AUC: 0.864021**
- Best epoch: **8**
- Early stop: epoch **14**
- Weak-6 Macro AUC: **0.857540**
- Exp3B Fold2: 0.898710
- Macro 변화: **-0.034689**
- Exp3B Weak-6: 0.867857
- Weak-6 변화: **-0.010317**
- Training time: 약 **67.83분**

### Target별 변화 vs Exp3B
- 개선:
  - Medial Meniscus: 0.750000 → **0.857143**
  - Synovitis: 0.933333 → **0.966667**
  - Lateral Meniscus: 0.964286 → **1.000000**
- 주요 하락:
  - Fracture: 0.666667 → **0.500000**
  - Medial OA: 0.958333 → **0.833333**
  - PF OA: 0.892857 → **0.821429**
  - ACL: 0.833333 → **0.766667**

### Group-routing 진단
Validation 평균 target-specific spatial group attention은 대부분 target에서 거의 동일한 패턴을 보였다.

- Group 1: 약 **0.159**
- Group 2: 약 **0.475~0.479**
- Group 3: 약 **0.360~0.366**

Target-specific group-query norm은 target마다 달랐지만, 최종 group attention 분포는 크게 분리되지 않았다.

### 인사이트
- target별 slice-group correction을 추가했지만 전체 Macro와 Weak-6 모두 Exp3B보다 하락했다.
- target별 group routing이 실제로 크게 분화되지 않아, 현재 방식은 유의미한 specialization을 만들지 못했다.
- Meniscus 계열 일부는 개선됐으므로 local expert 아이디어로는 참고할 수 있으나, 전체 baseline으로는 승격하지 않는다.
- Public LB 제출은 진행하지 않는다.

---

## Experiment 25 — Exp4B Target × MRI-Slot Spatial Gate, Fold2 Screening

### 목적
Exp3B의 spatial residual gate를 target당 1개에서 **target × MRI-slot 12×6**으로 세분화해, 질병별로 Sagittal / Coronal / Axial 및 fluid / non-fluid slot별 spatial residual 사용량을 다르게 학습할 수 있는지 확인했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Persistent Wide224 cache 사용
- DINOv2-Small Full fine-tuning
- Global path: `CLS + patch_mean`
- Spatial queries: target당 4개
- Exp3B spatial group routing 유지
- Spatial residual gate:
  - Exp3B: target당 1개
  - Exp4B: **12 targets × 6 MRI slots = 72개**
- 모든 target-slot gate는 0으로 초기화
- Batch64 / Accum1 / Effective64
- Max48 / Patience6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Best Macro ROC-AUC: 0.896726**
- Best epoch: **16**
- Early stop: epoch **22**
- Weak-6 Macro AUC: **0.868056**
- Exp3B Fold2: 0.898710
- Macro 변화: **-0.001984**
- Exp3B Weak-6: 0.867857
- Weak-6 변화: **+0.000198**
- Training time: 약 **104.23분**

### Target별 변화 vs Exp3B
- 개선:
  - ACL: 0.833333 → **0.933333**
  - Medial Meniscus: 0.750000 → **0.821429**
  - Synovitis: 0.933333 → **1.000000**
  - Fracture: 0.666667 → **0.708333**
- 유지:
  - MCL: 1.000000
  - Lateral Meniscus: 0.964286
  - Lateral OA: 1.000000
  - Effusion: 0.964286
  - Baker's: 1.000000
  - Contusion: 0.821429
- 주요 하락:
  - PF OA: 0.892857 → **0.714286**
  - Medial OA: 0.958333 → **0.833333**

### Target × MRI-slot gate 진단
- ACL은 Sagittal fluid에서 가장 큰 음의 gate를 학습: 약 **-0.0739**
- MCL은 Coronal / Axial 계열에서 양의 gate가 상대적으로 큼
- Effusion은 Sagittal fluid에서 약 **-0.0803**
- Fracture는 전반적으로 음의 gate를 학습
- gate 사용량(mean absolute scale)이 큰 target:
  - MCL: **0.03796**
  - Fracture: **0.03583**
  - Lateral OA: **0.03233**
  - ACL: **0.03007**

### 인사이트
- 전체 Macro는 Exp3B보다 아주 소폭 낮았지만 **-0.001984** 차이로 사실상 근접했다.
- Weak-6는 **+0.000198**로 거의 동일하다.
- A와 달리 target별/slot별 gate가 실제로 서로 다른 부호와 크기를 학습해 specialization 신호는 확인됐다.
- ACL / Medial Meniscus / Synovitis / Fracture가 동시에 개선됐다는 점은 약한 target 보완 관점에서 의미가 있다.
- 그러나 PF OA와 Medial OA가 크게 하락해 전체 Macro는 Exp3B를 넘지 못했다.
- 현재 기준에서는 Exp3B를 baseline으로 유지하고, Exp4B의 slot-specific gate 아이디어는 선택적으로 제한 적용하는 후속 실험 후보로 남긴다.
- Public LB 제출은 진행하지 않는다.


---

## Experiment 26 — Exp5A Hierarchical Target + MRI-Slot Gate (alpha=0.50), Fold2 Screening

### 목적
Exp4B의 target × MRI-slot specialization 신호는 유지하되, 72개 free gate의 자유도를 줄이기 위해 **target-level base gate + zero-mean slot correction** 구조를 적용했다. Exp5A는 slot correction strength를 **0.50**으로 설정했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Persistent Wide224 cache
- DINOv2-Small Full fine-tuning
- Global path: `CLS + patch_mean`
- Spatial queries: target당 4개
- Hierarchical spatial gate:
  - target-level base gate
  - 6개 MRI-slot zero-mean correction
  - correction strength: **0.50**
- Batch64 / Accum1 / Effective64
- Max48 / Patience6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Macro ROC-AUC: 0.877778**
- Weak-6 Macro AUC: **0.850992**
- Best epoch: **12**
- Early stop: epoch **18**
- Training time: 약 **82.29분**
- Exp3B 대비:
  - Macro: **-0.020933**
  - Weak-6: **-0.016865**
- Exp4B 대비:
  - Macro: **-0.018948**
  - Weak-6: **-0.017063**

### Target별 주요 변화 vs Exp3B
- 개선:
  - Fracture: 0.666667 → **0.708333**
  - Medial Meniscus: 0.750000 → **0.785714**
- 주요 하락:
  - PF OA: 0.892857 → **0.750000**
  - Medial OA: 0.958333 → **0.875000**
  - ACL: 0.833333 → **0.766667**
  - Lateral Meniscus: 0.964286 → **0.928571**

### 인사이트
- alpha=0.50은 correction 자유도를 충분히 제한하지 못했고 전체 Macro와 Weak-6가 모두 하락했다.
- Hierarchical decomposition 자체가 Exp4B의 약점을 자동으로 해결하지는 못했다.
- Public LB 제출 없이 종료한다.

---

## Experiment 27 — Exp5B Hierarchical Target + MRI-Slot Gate (alpha=0.25), Fold2 Screening

### 목적
Exp5A와 동일한 hierarchical gate를 사용하되 slot correction strength를 **0.25**로 낮춰 더 보수적인 slot specialization을 검증했다.

### 구성
- Validation: **Fold 2 Gold 11 studies**
- Persistent Wide224 cache
- DINOv2-Small Full fine-tuning
- Global path: `CLS + patch_mean`
- Spatial queries: target당 4개
- Hierarchical spatial gate:
  - target-level base gate
  - 6개 MRI-slot zero-mean correction
  - correction strength: **0.25**
- Batch64 / Accum1 / Effective64
- Max48 / Patience6
- V2.2 Gold / pseudo loss split 유지

### Fold2 결과
- **Macro ROC-AUC: 0.894742**
- Weak-6 Macro AUC: **0.879365**
- Best epoch: **12**
- Early stop: epoch **18**
- Training time: 약 **84.44분**
- Exp3B 대비:
  - Macro: **-0.003968**
  - Weak-6: **+0.011508**
- Exp4B 대비:
  - Macro: **-0.001984**
  - Weak-6: **+0.011310**

### Target별 주요 변화 vs Exp3B
- 개선:
  - Medial Meniscus: 0.750000 → **0.821429**
  - Synovitis: 0.933333 → **0.966667**
- 유지:
  - MCL: 1.000000
  - Lateral Meniscus: 0.964286
  - Lateral OA: 1.000000
  - Effusion: 0.964286
  - Baker's: 1.000000
  - Contusion: 0.821429
  - Fracture: 약 0.666667
- 하락:
  - Medial OA: 0.958333 → **0.875000**
  - PF OA: 0.892857 → **0.857143**
  - ACL: 0.833333 → **0.800000**

### 인사이트
- alpha를 0.50 → 0.25로 줄이자 Exp5A보다 크게 회복됐고 Exp3B Macro에 다시 근접했다.
- **Weak-6 0.879365는 현재 완료된 Fold2 실험 중 최고 Weak-6 기록**이다.
- 개선은 특히 Medial Meniscus / Synovitis에서 나타났으며, Macro 손실은 주로 Medial OA / ACL / PF OA에서 발생했다.
- 따라서 slot correction을 모든 target에 동일하게 허용하기보다, 기존에 약한 target에만 제한적으로 적용하는 후속 실험이 더 적합하다.
- 전체 Macro가 Exp3B를 넘지 못했으므로 현재 baseline은 Exp3B를 유지하고 Public LB 제출은 보류한다.

---

## Completed Experiment Scoreboard

| ID | Experiment | Internal Metric | Public LB |
|---|---|---:|---:|
| 01 | V1.1 single submission | - | 0.554 |
| 04 | V2 DINOv2-S Fold0 single | Fold0 Val AUC 0.750099 | 0.804 |
| 06 | V2.1 Fold0~2 Partial OOF | 0.779997 | - |
| 07 | V2.1 Fold3~4 Partial OOF | 0.805944 | - |
| 08 | V2.1 3-Fold Ensemble | - | 0.810 |
| 09 | V2.1 5-Fold Ensemble | - | 0.816 |
| 10 | V2.1 Full 58-Gold OOF | 0.784485 | - |
| 11 | V2.2 Loss-Split 5-Fold | Full OOF 0.793107 | 0.816 |
| 12 | V2.3 Gold Oversampling ×10 | Full OOF 0.773342 | - |
| 13 | V2.4 Batch / LR Search | 35-Gold Search AUC 0.795854 | - |
| 14 | V2.5 Adjacent Triplet 5-Fold | Full OOF 0.778191 | 0.807 |
| 15 | V2.6A Meniscus Hybrid Controlled | Full OOF 0.784614 | - |
| 16 | V2.6B Meniscus Hybrid Long-Horizon | Full OOF 0.807992 | 0.814 |
| 17 | Exp1A Last4 Layer-wise LR | Fold2 AUC 0.818585 | - |
| 18 | Exp1B Full Fine-tuning + Layer-wise LR | Fold2 AUC 0.884127 | - |
| 19 | Exp2A Full FT + Target Spatial Attention | Fold2 AUC 0.889120 | - |
| 20 | Exp2B Full FT + Target Expert Head | Fold2 AUC 0.862765 | - |
| 21 | Exp3A Global/Spatial Gated Residual | Fold2 AUC 0.895437 | - |
| 22 | Exp3B Multi-query Global/Spatial Residual | **Fold2 AUC 0.898710** | - |
| 23 | Exp3B Fold2 Single-Model LB Check | Fold2 AUC 0.898710 | **0.824** |
| 24 | Exp4A Target-specific Spatial Group Attention | Fold2 AUC 0.864021 | - |
| 25 | Exp4B Target × MRI-Slot Spatial Gate | Fold2 AUC 0.896726 | - |
| 26 | Exp5A Hierarchical Target+Slot Gate α0.50 | Fold2 AUC 0.877778 | - |
| 27 | Exp5B Hierarchical Target+Slot Gate α0.25 | Fold2 AUC 0.894742 | - |

---

## Current Best Completed Results

- **Public LB 최고: Exp3B Fold2 Single Model — 0.824**
  - 이전 최고 0.816 대비 **+0.008**
  - 기존 0.816은 V2.1 / V2.2 5-Fold ensemble
- **Full 58-Gold OOF 최고: V2.6B — 0.807992**
- **Single Fold2 screening 최고: Exp3B Multi-query Spatial Residual — 0.898710**
- **Single Fold2 Weak-6 최고: Exp5B Hierarchical Target+Slot Gate α0.25 — 0.879365**
- 최근 Fold2 screening:
  - Exp1A Last4: 0.818585
  - Exp1B Full fine-tuning: 0.884127
  - Exp2A Spatial Attention: 0.889120
  - Exp2B Target Expert: 0.862765
  - Exp3A Global/Spatial Residual: 0.895437
  - **Exp3B Multi-query Spatial Residual: 0.898710**
  - Exp4A Target-specific Group Attention: 0.864021
  - Exp4B Target × MRI-Slot Gate: 0.896726
  - Exp5A Hierarchical Gate α0.50: 0.877778
  - Exp5B Hierarchical Gate α0.25: 0.894742
- Public LB 흐름:
  - V2 Fold0 single: 0.804
  - V2.1 3-Fold: 0.810
  - V2.1 / V2.2 5-Fold: 0.816
  - V2.6B 5-Fold: 0.814
  - **Exp3B Fold2 single: 0.824**
- Exp3B는 현재 처음으로 **단일 Fold 모델이 이전 5-Fold Public 최고를 넘어선 구조**다.
- Fold2 validation은 11 Gold에 불과하므로 구조 탐색용으로 사용하고, Public LB는 선택된 후보의 실제 일반화 확인용으로 사용한다.
- Exp4A는 Macro -0.034689 / Weak-6 -0.010317로 승격하지 않는다.
- Exp4B는 Macro -0.001984 / Weak-6 +0.000198로 Exp3B에 매우 근접했고, 일부 약한 target이 개선되어 slot-specific gating 아이디어는 후속 제한 적용 후보로 유지한다.
- Exp5A α0.50은 Macro/Weak-6 모두 하락해 승격하지 않는다.
- Exp5B α0.25는 Macro 0.894742로 Exp3B보다 낮지만 **Weak-6 0.879365로 새 최고 기록**을 만들었다. 다음 단계에서는 slot correction을 모든 target에 주기보다 약한 target에 선택적으로 제한하는 방향을 검증한다.
- 5-Fold 전체 학습은 최종 후보가 좁혀진 뒤 수행한다.
