# RSNA Knee — Specialist Model Roadmap

최종 업데이트: **2026-10-02**

> 상태: **SS07A — Lateral Meniscus DINOv2-Small Specialist Pilot 준비**
>
> 현재 우선순위는 아래 2026-10-02 Current Specialist Roadmap을 따른다.
> 2026-09-30의 LM-only candidate-rule 계획은 역사 기록으로만 유지한다.

완료 기록: [SPECIALIST_EXPERIMENT_LOG.md](SPECIALIST_EXPERIMENT_LOG.md)


<!-- SPECIALIST_2026_10_02_CURRENT_START -->

# 2026-10-02 Current Specialist Roadmap

> **현재 단계: SS06B 완료 -> SS07A Lateral Meniscus Specialist pilot**
>
> 아래 2026-09-30 LM-only candidate-rule 계획은 역사 기록으로 유지한다.
> 실제 진행 우선순위는 이 섹션을 따른다.

## 방향 전환 배경

기존 SS02 pilot은 target마다:

```text
generic frozen DINOv2-Small
-> 전체 single-slice feature extraction
-> target-specific hierarchical MIL
-> target-specific ranking
```

을 독립적으로 수행하도록 설계했다.

SS02A LM에서는 feature extraction만 약 238.7분이 걸렸고,
MIL은 best Fixed Val ROC-AUC **0.685**에서 early stop됐다.
ranking / reliability audit까지 포함하면 target 하나당 5시간 이상이 필요한 구조였고,
12 target selector + 12 final Specialist까지 이어지는 전체 비용이 지나치게 컸다.

따라서 이 구조는 **완료 실험으로 기록하지 않고 중단/폐기**한다.

## 새 전체 파이프라인

```text
SS01  Full MRI Single-Slice Inventory / Manifest     [DONE]
  ↓
SS03  DINOv2-Base single-slice Knee MRI adaptation  [DONE]
  ↓
SS04  Full single-slice feature cache                [DONE]
  ↓
SS05  Shared Hierarchical MIL                       [DONE]
      + 12 target-specific attention/output heads
  ↓
SS06A Top-K reliability audit                     [DONE]
SS06A2 weak-selector extended audit                 [DONE]
SS06B 12 target-specific single-slice manifests     [DONE]
  ↓
SS07A LM DINOv2-Small Specialist pilot               [CURRENT]
  ↓
SS07B~ remaining target-specific Specialists
  ↓
Hidden Test end-to-end inference / submission
```

## SS03 완료 결과

- PASS
- best epoch: **11**
- best SSL Val Loss: **0.1376109371**
- epoch 12 Val Loss: **0.1379058798**
- total: **218.72 min**
- train / val studies: **3,592 / 815**
- checkpoint SHA256: `d60811d7a002d539fcabddfb8f8334a3b6a0a697f521dccc98bf24a124959166`
- collapse signal 없음: val feature std 약 **1.49**
- 최종 feature extractor: best teacher DINOv2-Base backbone

## SS03 확정 계약

- backbone init: generic pretrained **DINOv2-Base**
- 기존 3-slice-window task-tuned checkpoint: **사용하지 않음**
- input unit: **single MRI slice 1장**
- Series sampling range: **20~80%**
- epoch당 Series별 sample: **1장**, epoch마다 위치 변경
- image: **224x224**, 130 mm physical center crop
- training: self-supervised domain adaptation
- disease label: 사용하지 않음
- Fixed Val UID: train에서 완전 제외
- checkpoint: SSL Val Loss 최소 best 1개만 유지
- epochs: **12**
- global batch: **16** on T4 x2
- backbone LR:
  - early **1e-6**
  - mid **3e-6**
  - late **1e-5**
- SSL projector LR: **2e-4**
- 최종 산출물: adapted **teacher DINOv2-Base backbone**

주의:
single-slice는 batch size 1을 뜻하지 않는다.
한 training sample이 MRI 1장이라는 뜻이며 batch에는 여러 single slices를 함께 넣는다.

## SS04 완료 결과

- PASS
- 4,407 studies / 24,371 series / **819,078 true single slices**
- feature: **CLS768 + PatchMean768 = 1536-d float16**
- cache shape: **[819078, 1536]**
- cache size: **2.3434 GiB**
- runtime: **60.87 min**
- throughput: **224.26 slices/s**
- decode errors: **0**
- feature audit: **PASS**
- feature SHA256: `90d1c84a8ecd1d3d49213abf63ed797329057f15341cb5c46b222bf616536879`

## SS04 — Feature cache

SS03 best backbone으로 전체 Train MRI를 한 번만 통과시킨다.

```text
each DICOM slice
-> adapted DINOv2-Base
-> CLS / patch representation
-> persistent feature cache
```

이 cache는 이후 12 target이 공통 사용한다.

## SS05 완료 결과

- PASS
- best epoch: **19**
- Fixed Val Macro ROC-AUC: **0.881247**
- Weak-6 ROC-AUC: **0.856870**
- runtime: **16.14 min**
- train: **3,592 studies**
- Fixed Val union: **815 studies**

Target AUC:
- ACL 0.9400
- MCL 0.7675
- Medial Meniscus 0.9581
- Lateral Meniscus 0.7606
- Medial OA 0.9213
- Lateral OA 0.8613
- PF OA 0.8981
- Effusion 0.9525
- Synovitis 0.9824
- Baker's 0.8831
- Contusion 0.8756
- Fracture 0.7744

Attention coverage:
- Top24: 약 **31~35%**
- Top32: 약 **38~42%**
- Top48: 약 **50~55%**
- Top64: 약 **60~65%**

SS06에서는 Top24를 고정하지 않는다.
K=24/32/48/64를 중심으로 keep/remove/random-K 진단 후 target별 K를 결정한다.

## SS06A 완료 결과

- PASS / runtime **2.11 min**
- K=24/32/48/64, Random-K 5 repeats
- SS05 Full AUC 12 target 정확히 재현

유력 K:
- ACL 24
- MCL 24
- Medial Meniscus 48
- Lateral Meniscus 24
- Medial OA 64
- Synovitis 24
- Baker's 24
- Contusion 48
- Fracture 32

추가 검증 대상:
- **Lateral OA**
- **PF OA**
- **Effusion**

이 3개는 attention Keep-K가 Random-K보다 약한 경우가 많다.
따라서 SS06A2에서 **K=64/96/128 + uniform/random**을 비교한 뒤 최종 policy를 freeze한다.

## SS06B 완료 결과

- PASS
- 4,407 studies × 12 targets = **52,884 target-study rows**
- runtime: **0.84 min**
- selection parquet: **12.19 MiB**
- integrity audit: **PASS**
- attention target padding: **0**
- Uniform K96 padding: **120 / 4,407 = 2.72%**
- padding sentinel: **feature_row = -1**

Artifacts:
- selection index SHA256:
  `7385ed4a353c5fe2b0fd315d7c692d32a46c4470c72d7245f2782c220b40bdef`
- target summary SHA256:
  `aa88ffb4b4ac92b72e6e91bb4640c09d580ae66ab273d74cfd82bbc3af5055d7`
- frozen policy SHA256:
  `927d0c592401f26f1f6a73a510736c0f9f4b686f63e4da51d0274273a936a857`

SS07A pilot:
- target: **Lateral Meniscus**
- selector: **attention K24**
- backbone: **DINOv2-Small**
- aggregator: **metadata-aware set-like Slice Transformer**
- first goal: Fixed Val LM ROC-AUC가 SS05 LM baseline **0.760625**를 개선하는지 확인.

## SS05 — Shared Hierarchical MIL

1차 기본 구조:

```text
Study
 ├─ Series 1 -> slice features -> target-aware slice attention
 ├─ Series 2 -> slice features -> target-aware slice attention
 └─ ...
        ↓
 target-aware series aggregation
        ↓
 12 target predictions
 + 12 target-specific slice importance maps
```

처음부터 12개의 MIL을 독립 학습하지 않는다.

검증:
- 각 target Fixed Val ROC-AUC
- Top-K keep
- Top-K remove
- Random-K
- attention/ranking stability
- plane / series coverage

Shared MIL이 특정 target에서 충분히 약한 경우에만
그 target용 binary MIL을 후속 분리한다.

## SS06 — Target-specific Top-K

MIL이 학습한 **single-slice importance**를 사용한다.

기존 계보의 3-slice-window importance와 구분한다.

```text
ACL importance -> ACL Top-K single slices
LM importance  -> LM Top-K single slices
...
```

K는 고정하지 않고 reliability audit 결과로 결정한다.
초기 후보는 16 / 24 / 32 / 48 / 64 범위에서 비교한다.

## SS07 — Target-specific Final Specialist

각 target:

```text
target Top-K single slices
-> DINOv2-Small
-> slice aggregation / transformer
-> binary head
-> target probability
```

- Positive + Negative 모두 학습
- target별 Fixed Val 사용
- 최종 Specialist는 target마다 독립
- Selector 역할의 SS03/SS05 representation은 공통 재사용

## Hidden Test

```text
Hidden Test raw MRI
-> adapted DINOv2-Base
-> single-slice feature cache in-memory
-> shared MIL
-> target-specific Top-K
-> target-specific DINOv2-Small Specialist
-> 12 probabilities
```

Hidden Test Top-K는 미리 만들 수 없으며
실제 test MRI에서 online으로 selector를 실행한다.

<!-- SPECIALIST_2026_10_02_CURRENT_END -->

---

# 1. 목표

기존 shared 12-label 모델과 별도로, **질환 하나만 Yes / No로 판단하는 binary specialist** 계보를 구축한다.

개념:

```text
Patient MRI
  -> disease-specific input selector
  -> disease-specific Top-K windows
  -> DINOv2-Small
  -> Slice Transformer
  -> binary head
  -> one disease probability
```

12개 질환을 한 번에 모두 만들지 않는다.
먼저 한 질환으로 데이터 선택부터 validation까지 전체 파이프라인을 완성한 뒤 다른 질환으로 확장한다.

Specialist가 모든 target에서 shared model보다 좋아야 할 필요는 없다.
최종 제출에서는 target별로 shared / specialist 중 더 적합한 출력을 사용하는 hybrid도 허용한다.

---

# 2. 확정된 핵심 설계 원칙

## 2.1 Binary classification

각 Specialist는 자기 질환 하나만 예측한다.

예:

```text
MCL Specialist

MCL 있음  -> Positive / YES
MCL 없음  -> Negative / NO
```

실제 학습에는 **Positive와 Negative를 모두 사용**한다.
Positive만 학습하면 NO를 구분할 기준을 배울 수 없기 때문이다.

## 2.2 Positive-only 분석과 실제 학습을 구분

질환 전용 입력 규칙을 찾는 초기 localization audit에서는
**training Positive MRI**를 먼저 분석한다.

목적:

- 어떤 Plane이 반복적으로 중요한지
- 어떤 Series가 중요한지
- slice 위치가 어디에 몰리는지
- 기존 target-specific attention이 어디를 높게 보는지

이 단계는 질환이 잘 보이는 candidate space를 찾기 위한 분석이다.

최종 selector / preprocessing은 label을 알지 못해도 실행 가능해야 한다.
따라서 확정된 질환 전용 candidate rule은 이후 **Positive / Negative / Validation / Test 모두에 동일하게 적용**한다.

## 2.3 Positive Top-K / Negative Top-K를 따로 만들지 않는다

질환마다 selector는 **하나만** 둔다.

```text
Disease-specific candidate rule
        ->
Disease-specific selector
        ->
same Top-K procedure
        ->
Positive study: lesion-relevant windows
Negative study: disease-relevant anatomy but no disease
```

Negative에서는 질환이 있을 법한 위치를 보지만 실제로는 없는 영상을 선택하도록 하여
**hard negative** 역할을 하게 한다.

Positive용 selector와 Negative용 selector를 따로 만들면
추론 전에 label을 알아야 하므로 실제 Test에 사용할 수 없다.

## 2.4 Backbone

Specialist backbone 기본 방향은 **DINOv2-Small**이다.

이 선택은 Small이 Base보다 더 강하다고 가정해서가 아니라:

- disease-specific lightweight specialist
- 여러 specialist의 inference 비용
- Slice Transformer와 결합하는 구조
- 관련 knee MRI 연구 근거

를 고려한 것이다.

DINOv2 Small / Base / Large 크기 비교는 이미 별도 계보에서 충분히 검토했으므로
**Specialist에서 model-size scaling을 다시 실험하지 않는다.**

## 2.5 Gold 58 사용

Official Gold **58명은 모두 Train에 사용**한다.

따라서 Specialist 학습 후 Gold 58을 별도 validation으로 사용하는 단계는 두지 않는다.
학습에 사용한 Gold의 성능은 sanity check 용도로 볼 수는 있지만 일반화 성능 근거로 사용하지 않는다.

## 2.6 Fixed Pseudo Validation

Specialist 개발용 pseudo validation은 target별로 **미리 고정된 크기와 Positive / Negative 수**를 사용한다.

ROC-AUC의 효율적인 비교를 위해 각 target의 Val은 Positive / Negative를 1:1로 구성한다.
다만 고신뢰 학습 샘플을 최대한 남기기 위해 모든 target을 100명으로 강제하지 않는다.

| Target | Val Total | Val Pos | Val Neg | 이유 |
|---|---:|---:|---:|---|
| ACL | 80 | 40 | 40 | Strict P/N 충분 |
| MCL | 80 | 40 | 40 | Strict P/N 충분 |
| Medial Meniscus | 80 | 40 | 40 | Strict P/N 충분 |
| Lateral Meniscus | 80 | 40 | 40 | Strict P/N 충분 |
| Medial OA | 80 | 40 | 40 | Strict P/N 충분 |
| Lateral OA | 80 | 40 | 40 | Strict P/N 충분 |
| PF OA | 80 | 40 | 40 | Strict P/N 충분 |
| Effusion | 80 | 40 | 40 | Strict P/N 충분 |
| Synovitis | 50 | 25 | 25 | Strict Negative가 114뿐이므로 Val을 축소 |
| Baker's | 80 | 40 | 40 | Strict P/N 충분 |
| Contusion | 80 | 40 | 40 | Strict P/N 충분 |
| Fracture | 60 | 30 | 30 | Strict Positive가 246뿐이므로 Val을 축소 |

Val sample 선정 원칙:

1. Official Gold 58은 Val 후보에서 제외하고 전부 Train에 둔다.
2. V4 Strict에서 target별 Positive / Negative pool을 만든다.
3. 각 class 내부 confidence percentile 기준 **50% 이상 90% 미만**을 기본 Val candidate band로 사용한다.
   - threshold 직전의 불확실한 pseudo를 피한다.
   - confidence 최상위 10%는 가능한 한 Train에 남겨 가장 강한 supervision을 보존한다.
4. candidate가 부족한 경우에만 confidence band를 아래쪽으로 순차 확장한다.
5. 고정 random seed **20260930**으로 필요한 수만큼 sampling한다.
6. 한 번 선택한 StudyInstanceUID는 해당 target의 Specialist 계보에서 절대 바꾸지 않는다.
7. 해당 target의 Val UID는 localization audit / selector discovery / Specialist training에서 모두 제외한다.
8. main metric은 target ROC-AUC, secondary metric은 BCE / prediction distribution이다.
9. balanced Val이므로 BCE의 절대값을 실제 population calibration으로 해석하지 않는다.

이 validation은 pseudo-label 기반 development proxy이며 external ground truth validation으로 해석하지 않는다.

---

# 3. V4 pseudo-label 질환별 분포

2026-09-30 Kaggle에서
`rsna_knee_pseudolabels_v4_routed_broad.csv`와
`rsna_knee_pseudolabels_v4_routed_strict.csv`를 직접 집계했다.

Soft target 기준:

- Positive: `target >= 0.5`
- Negative: `target < 0.5`

| Target | Broad Total | Broad Pos | Broad Neg | Broad Pos % | Strict Total | Strict Pos | Strict Neg | Strict Pos % | Strict Removed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ACL | 4349 | 1194 | 3155 | 27.45 | 3975 | 827 | 3148 | 20.81 | 374 |
| MCL | 4349 | 680 | 3669 | 15.64 | 4119 | 522 | 3597 | 12.67 | 230 |
| Medial Meniscus | 4349 | 1758 | 2591 | 40.42 | 3593 | 1561 | 2032 | 43.45 | 756 |
| Lateral Meniscus | 4349 | 651 | 3698 | 14.97 | 3910 | 560 | 3350 | 14.32 | 439 |
| Medial OA | 4349 | 1611 | 2738 | 37.04 | 3992 | 1363 | 2629 | 34.14 | 357 |
| Lateral OA | 4349 | 1161 | 3188 | 26.70 | 4064 | 937 | 3127 | 23.06 | 285 |
| PF OA | 4349 | 1975 | 2374 | 45.41 | 3371 | 1794 | 1577 | 53.22 | 978 |
| Effusion | 4349 | 2616 | 1733 | 60.15 | 3808 | 2508 | 1300 | 65.86 | 541 |
| Synovitis | 4349 | 538 | 3811 | 12.37 | 629 | 515 | 114 | 81.88 | 3720 |
| Baker's | 4349 | 1074 | 3275 | 24.70 | 2310 | 1053 | 1257 | 45.58 | 2039 |
| Contusion | 4349 | 729 | 3620 | 16.76 | 4181 | 599 | 3582 | 14.33 | 168 |
| Fracture | 4349 | 299 | 4050 | 6.88 | 1840 | 246 | 1594 | 13.37 | 2509 |

모든 질환에서 Val 100 자체는 구성 가능하다.
다만 strict filtering이 class balance를 크게 바꾸는 target이 있으므로
**Strict-only를 모든 Specialist에 일괄 적용하지 않는다.**

특히 Synovitis:

```text
Broad  : Positive 538 / Negative 3811
Strict : Positive 515 / Negative 114
```

Strict가 대부분의 Negative를 제거한다.
따라서 Synovitis는 Strict-only Train/Val을 기본값으로 사용하지 않고,
Broad confidence distribution까지 함께 보고 high-confidence Negative 확보 방식을 정한다.

Baker's와 Fracture도 strict filtering 후 class prevalence가 크게 변하므로 같은 점을 확인한다.

---

# 4. Official Gold 58 분포

| Target | Gold Total | Gold Pos | Gold Neg | Gold Pos % |
|---|---:|---:|---:|---:|
| ACL | 58 | 24 | 34 | 41.38 |
| MCL | 58 | 9 | 49 | 15.52 |
| Medial Meniscus | 58 | 26 | 32 | 44.83 |
| Lateral Meniscus | 58 | 23 | 35 | 39.66 |
| Medial OA | 58 | 15 | 43 | 25.86 |
| Lateral OA | 58 | 11 | 47 | 18.97 |
| PF OA | 58 | 21 | 37 | 36.21 |
| Effusion | 58 | 35 | 23 | 60.34 |
| Synovitis | 58 | 27 | 31 | 46.55 |
| Baker's | 58 | 12 | 46 | 20.69 |
| Contusion | 58 | 19 | 39 | 32.76 |
| Fracture | 58 | 18 | 40 | 31.03 |

Gold prevalence와 pseudo prevalence가 크게 다른 target이 있으므로
Gold 58만으로 pseudo 모집단의 prevalence를 교정한다고 가정하지 않는다.

---

# 5. V4 Strict confidence threshold

기존 V4 strict mask 기준:

| Target | confidence threshold |
|---|---:|
| ACL | 0.45 |
| MCL | 0.45 |
| Medial Meniscus | 0.45 |
| Lateral Meniscus | 0.45 |
| Medial OA | 0.45 |
| Lateral OA | 0.35 |
| PF OA | 0.35 |
| Effusion | 0.30 |
| Synovitis | 0.20 |
| Baker's | 0.45 |
| Contusion | 0.35 |
| Fracture | 0.35 |

Strict file은 이 confidence 기준 미달 target/study pair를 NaN / masked 처리한다.

기존 main-line broad 학습은:

```text
pseudo target weight = 0.70 x confidence
```

를 사용했다.

Specialist의 첫 baseline에서 broad weighting을 그대로 유지할지,
일부 high-confidence filtering을 섞을지는 pilot target split을 만든 뒤 최종 확정한다.

---

# 6. Specialist 실행 계획

## S00-1 — Target distribution audit — 완료

Broad / Strict / Gold의 Positive / Negative 수를 확인했다.

목적:
각 target이 별도 binary Specialist 학습과 Fixed Val 100을 구성할 수 있는지 확인한다.

## S00-2 — Target별 Fixed Val 구축

상태: **완료 — 2026-09-30**

실행 코드는 GitHub에 저장하지 않는다.
Specialist 실행은 Kaggle에 notebook을 Import해 Run All 하는 방식으로 진행한다.

12개 target의 Val 크기와 P/N 수를 위 2.6 표대로 먼저 고정한다.

작업:

- V4 Strict에서 target별 Positive / Negative pool 생성
- class별 confidence percentile 50–90% candidate band 생성
- seed 20260930으로 고정 sampling
- target별 Val manifest CSV 생성
- 통합 `specialist_fixed_val_manifest_v1.csv` 생성
- 검증용 `specialist_fixed_val_summary_v1.csv` 생성
- Train / Val UID 완전 분리 검증
- 이후 동일 target의 모든 Specialist 실험에서 같은 manifest 사용

실행 결과:
- 12개 target 모두 계획된 Val P/N 수로 생성 성공
- 모든 target에서 기본 confidence percentile band 50–90%만으로 충분했음
- confidence band 하향 확장 불필요
- Gold overlap 0
- target 내부 UID 중복 0
- confidence 최상위 10% Val 사용 0
- 통합 manifest: 910 target-study rows / 815 unique StudyInstanceUID
- combined manifest SHA256: `4e80375e688b8419b075a97b63508bb4523512fa91bbde1b3b9003a0bde8fe4a`
- summary SHA256: `a553d194a33127bdcdea1a316c982d2d9a59b40873b8af2951bef608b80906f4`
- output ZIP SHA256: `201f723147fffed14aa6171030c6d9a825af80ebb99125e63b710db74f8aacb5`

S00-2 완료. 다음은 S00-3 pilot target Training Positive MRI localization audit이다.

## S00-3 — Training Positive MRI localization audit

상태: **완료 — 2026-09-30**

Pilot target: **Lateral Meniscus**

Audit pool:
- V4 Strict Positive = 560
- Fixed Val Positive 40 제외
- **Training Strict Positive = 520**
- Gold는 이 localization audit에 포함하지 않음

Attention lineage:
- **Exp16B-1 original full-MRI features**
- **Exp16B-2 original Fold2 best hierarchical MIL**
- Lateral Meniscus target-specific window attention × target-specific series attention
- Exp59 / Exp60 refreshed branch는 사용하지 않음

이유:
Exp59/Exp60 이후 K24/K32 재학습은 기존 성공 계보보다 Public LB가 낮았으므로,
더 좋은 localization signal이라는 근거가 없다.
S00-3에서는 Exp16B-2.5 → Exp16B-3A로 이어진 원래 성공 selector 계보를 기준으로 한다.

분석 항목:
- 중요 Plane
- 중요 Series / sequence
- canonical relative slice position
- target-specific joint attention concentration
- diagnostic Top1/4/8/16/24/32 attention mass
- raw Top32 및 same-series NMS gap3 Top32 metadata 분포

목적은 최종 Top-K를 지금 확정하는 것이 아니라,
전체 819,078-window 공간에서 Lateral Meniscus candidate space를 좁힐 근거를 얻는 것이다.

실행 결과:

- Fixed Val 80명 완전 제외 확인
- Training Strict Positive 520명 전부 분석
- 분석된 full-MRI windows = 101,883
- 분석된 Series = 3,051
- target-specific joint attention 합 = study별 1.0 검증
- runtime 약 0.20분
- PASS

Plane 평균 joint-attention mass:

| Plane | Mean attention mass |
|---|---:|
| Axial | 0.362325 |
| Coronal | 0.326014 |
| Sagittal | 0.311661 |

세 Plane 모두 중요하며 Axial이 1위지만 차이가 크지 않다.
따라서 S00-4에서 단일 Plane만 남기는 규칙은 사용하지 않는다.

Raw Top32 plane share:

- Axial 36.05%
- Coronal 34.15%
- Sagittal 29.80%

same-series NMS gap3 Top32 plane share:

- Sagittal 39.68%
- Coronal 34.54%
- Axial 25.78%

NMS 후 Sagittal 비중이 크게 올라간 것은 Axial 상위 attention window가 인접 slice에 더 군집되어 있음을 시사한다.
따라서 실제 Specialist selector에서는 연속 3-slice window 중복 제어가 필요하다.

Raw attention concentration:

| K | Mean cumulative attention mass |
|---:|---:|
| 8 | 0.280396 |
| 16 | 0.447494 |
| 24 | 0.566393 |
| 32 | 0.653829 |

Top32만으로도 평균 attention mass가 약 65.4%이므로 K를 먼저 확정하지 않는다.
S00-4에서 deterministic candidate space를 먼저 줄인 뒤 그 안에서 K를 결정한다.

전체 relative-position attention은 0.3~0.8 구간에 가장 많이 모였지만,
Plane별 peak 위치가 다르다:

- Axial: 0.3~0.7, 특히 0.4~0.6
- Coronal: 0.4~0.9, 특히 0.5~0.8
- Sagittal: 0.6~0.9가 강하고 0.1~0.4에도 secondary mass 존재

따라서 모든 Plane에 동일한 단일 relative-position cutoff를 바로 적용하지 않고
S00-4에서 plane-specific candidate ranges를 정량 비교한다.

S00-3 artifact fingerprint:

```text
lateral_meniscus_localization_audit_summary.json
SHA256 = fa655e94ec00bd9cbf84aac51b91bdec1b5f8e93711dec3917e373b9b5b355f8

lateral_meniscus_attention_concentration.csv
SHA256 = 221930f8943a9ef22e20d4030297977f8c33704d3f7efed46f98f715c8a7bc03

lateral_meniscus_top32_nms_gap3.parquet
SHA256 = 72dc2f88027777be2855449720a5979c37243566a7e4b0f9e33869d1ef919b40

rsna_knee_s00_3_lateral_meniscus_localization_audit_v1.zip
SHA256 = fa70ac6a710df8d123a91d306bed14089d75d324290c98a304e1dfb53b745b1b
```

## S00-4 — Disease-specific candidate rule 확정

상태: **Lateral Meniscus candidate-rule audit notebook 준비 / Kaggle 실행 결과 대기**

S00-3 결과를 바탕으로
label을 알지 못해도 적용할 수 있는 deterministic candidate rule을 정의한다.

이번 단계에서는 하나의 규칙을 미리 정답으로 고정하지 않고
Positive 520명의 101,883 full-MRI windows에서
**candidate-window 감소율 vs Lateral Meniscus attention 보존율**을 비교한다.

비교 후보:

```text
R0 Full MRI
- filter 없음

R1 Broad relative range
- all Plane
- relative 0.2 ~ 0.9

R2 Conservative plane-specific
- Axial    0.2 ~ 0.8
- Coronal  0.3 ~ 0.9
- Sagittal 0.1 ~ 0.9

R3 Focused plane-specific
- Axial    0.2 ~ 0.7
- Coronal  0.4 ~ 0.9
- Sagittal 0.1 ~ 0.4 OR 0.6 ~ 0.9

R4 Focused + low-value sequence pruning
- R3
- Axial non-fluid / non-fat-suppressed 제외
```

평가 항목:

- 전체 candidate window 감소율
- study당 candidate windows mean / median / p10 / min
- study별 attention retention mean / median / p10 / min
- retention >= 95 / 90 / 85 / 80% study 수
- zero-candidate study 수
- Plane / sequence 보존 분포
- 각 rule에서 same-series NMS gap3 + K 8/16/24/32 simulation

중요:
S00-4에서 attention은 rule 성능을 평가하는 근거로만 사용한다.
최종 candidate filter 자체는 Plane / sequence / relative-position 같은
label-blind metadata만 사용해야 한다.

실행 결과를 검토한 뒤 한 rule만 freeze하고 S00-5로 이동한다.
Validation / Test에서도 동일 rule을 사용한다.

## S00-5 — Disease-specific Top-K selector / manifest

동일한 target-specific selector를 모든 study에 적용한다.

- Positive -> 병변을 잘 보여줄 가능성이 높은 Top-K
- Negative -> 같은 해부학적 위치에서 질환이 없는 hard-negative Top-K
- Val/Test -> label을 사용하지 않고 동일 절차

Positive용 / Negative용 selector는 따로 만들지 않는다.

## S00-6 — Specialist persistent cache

선택된 Top-K raw windows를 persistent cache로 저장한다.

목적:

- 반복 DICOM decode 방지
- S01 이후 controlled experiment 속도 향상
- input contract 고정

질환 12개 cache를 미리 만들지 않고 pilot target 하나부터 만든다.

## S01 — Specialist Baseline

기본 구조:

```text
Disease-specific Top-K
 -> DINOv2-Small
 -> window / slice features
 -> lightweight Slice Transformer
 -> binary head
 -> YES / NO
```

S01이 이후 Specialist 실험의 내부 baseline이 된다.
기존 Exp16B-3A Fold2를 S01의 pass/fail 기준으로 사용하지 않는다.

## S02 — Input selection 개선

한 번에 한 변수만 바꿔 확인한다.

후보:

- Top-K 수
- Plane / Series candidate rule
- NMS / slice spacing
- target attention selection 방식

## S03 — Pseudo supervision 개선

후보:

- Broad confidence weighting
- low-confidence masking
- class별 confidence cutoff
- broad + strict mixed policy

architecture 변경과 pseudo 정책 변경을 같은 실험에서 섞지 않는다.

## S04 — Hard Negative 개선

현재 Specialist가 Positive로 잘못 판단하는 Negative study를 분석한다.

질환 관련 해부학적 위치는 맞지만 실제 병변이 없는 어려운 Negative를
학습에 더 효과적으로 반영하는 방법을 검증한다.

## S05 — Specialist architecture 개선

후보:

- DINO feature: CLS only vs CLS + PatchMean
- Slice Transformer layer / head
- hidden dimension
- pooling / aggregation
- positional embedding
- series handling

DINO backbone size scaling은 다시 하지 않는다.

## S06 — Training optimization

구조가 안정된 뒤:

- learning rate
- augmentation
- regularization
- early stopping
- checkpoint metric

을 조정한다.

## S07 — Public LB 검증

해당 target의 Fixed Val에서 충분한 개선이 확인된 중요한 checkpoint만 Kaggle Public LB로 확인한다.

Gold 58은 Train에 포함되므로 별도 Gold validation 단계는 없다.

## S08 — 다른 질환으로 확장

pilot Specialist에서 확립된 pipeline을 다른 target으로 확장한다.

모든 target에 동일 candidate rule / confidence cutoff를 강제하지 않는다.

## S09 — 최종 target-level hybrid

각 target에서 shared model / specialist prediction을 비교하고
최종 12개 output을 구성한다.

Specialist가 더 강한 target만 교체하는 방식도 허용한다.

---

# 7. 현재 남은 핵심 TBD

실제 S01을 실행하기 전에 다음을 확정한다.

- Top-K
- DINO feature token: CLS only / CLS + PatchMean
- Slice Transformer layer / head / hidden dim
- positional embedding
- series 처리 방식
- first baseline의 pseudo supervision policy
- checkpoint / early-stop metric
- augmentation / regularization
- inference runtime contract

---

# 8. Validation leakage 방지

순서는 반드시 다음과 같이 유지한다.

```text
1. Target별 Fixed Val manifest 먼저 확정
2. 해당 target Val UID를 모든 discovery / training pool에서 제외
3. Training Positive만으로 localization audit
4. candidate rule freeze
5. frozen rule을 Train / Val / Test에 동일 적용
6. Specialist Train
7. 해당 target의 Fixed Val 평가
```

기존 shared selector가 이미 일부 pseudo study를 학습에 본 이력이 있을 수 있으므로,
Fixed pseudo Val은 완전한 external ground truth validation으로 해석하지 않는다.
Specialist 계보의 **고정 development proxy**로 사용한다.

---

# 9. 참고 자료

- Medical Slice Transformer, Scientific Reports 2025: https://www.nature.com/articles/s41598-025-09041-8
- WACV 2024 medical foundation model comparison: https://openaccess.thecvf.com/content/WACV2024/html/Huix_Are_Natural_Domain_Foundation_Models_Useful_for_Medical_Image_Classification_WACV_2024_paper.html
- DINOv2 Radiology Benchmarks: https://arxiv.org/abs/2312.02366
- Kaggle single-model discussion: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304

---

# 10. 기록 원칙

- 실제 실행 결과 / checkpoint / Public LB / runtime / 인사이트는 `SPECIALIST_EXPERIMENT_LOG.md`에 기록한다.
- 실험 ID만 적지 않고 설명형 제목을 함께 사용한다.
- S01 이후에는 가능한 한 핵심 변수 하나씩만 바꾼다.
- 기존 dataset / cache / checkpoint를 덮어쓰지 않는다.


---

# 2026-10-01 Architecture Decision — One Target, One Selector, One Specialist

Specialist 기본 구조를 다음과 같이 고정한다.

```text
1 target
  = 1 native single-slice selector
  + 1 final specialist
```

12개 target 전체 기준 기본 checkpoint 수:

```text
12 selectors
+ 12 final specialists
= 24 checkpoints
```

3-Fold ensemble은 기본 설계가 아니다.

우선순위:

1. 각 target마다 selector 1개 + final specialist 1개로 독립 전문가를 완성한다.
2. target별 성능 개선이 한계에 도달했을 때 final specialist 3-Fold를 선택적으로 검토한다.
3. 추가 시간이 충분할 때만 selector Fold ensemble까지 확장한다.
4. 모든 target에 Fold ensemble을 일괄 강제하지 않는다.

목표는 하나의 모델이 하나의 target을 전담하여
해당 질환의 input selection부터 binary prediction까지 독립적으로 최적화되는 구조다.

## Hidden-Test inference 운영

Kaggle hidden Test는 제출 실행 시점에 처음 접근 가능하므로
Test slice ranking / Top-K manifest를 제출 전에 미리 생성해 둘 수 없다.

실제 LB inference는 각 target마다 다음 순서를 모두 실행해야 한다.

```text
Hidden Test Full MRI
  -> Target Selector
  -> target-specific slice ranking / Top-K
  -> Final Specialist
  -> target probability
```

따라서 기본 12-target 제출은 논리적으로
**12 selectors + 12 final specialists**가 모두 hidden-Test inference에 참여한다.

같은 notebook 실행 안에서는 selector가 만든 Top-K intermediate artifact를
즉시 저장해 뒤의 Specialist 단계에서 재사용할 수 있지만,
그 artifact를 다음 hidden-Test 제출 전에 미리 만들어 두는 것은 불가능하다.

Train / Fixed Val처럼 이미 접근 가능한 데이터에서는 ranking cache를 미리 생성해
반복 실험 속도를 줄일 수 있다.

## Single-slice architecture 방향

기존 3-slice S00-3/S00-4 결과는 historical reference로 보존하되,
새 Specialist 기본 lineage는 native single-slice 방향으로 다시 시작한다.

```text
Full MRI single slices
  -> target-specific native selector
  -> target-specific slice ranking / Top-K
  -> DINOv2-Small
  -> adjacent-feature local context
  -> Slice Transformer
  -> binary head
```

기존 3-slice attention 기반 candidate rule은
새 single-slice selector의 입력을 제한하는 hard rule로 사용하지 않는다.
새 selector는 전체 MRI single-slice space에서 해당 target의 중요도를 다시 학습한다.


---

# 2026-10-01 Dual-Target Parallel Execution Contract

현재 Specialist pilot을 단일 Lateral Meniscus에서 **2-target A/B 병렬 pilot**으로 확장한다.

- **A lane = Lateral Meniscus**
- **B lane = ACL**

선정 이유:
- 둘 다 Fixed Val 80 (40P/40N)이 이미 고정되어 있다.
- Strict training pool이 충분하다.
- 서로 다른 해부학적 target을 동시에 검증하여 single-slice pipeline이 특정 질환에만 맞는지 조기에 확인할 수 있다.

공통 작업은 한 번만 수행한다:

```text
SS01 Full MRI Single-Slice Inventory / Manifest
```

그 다음부터:

```text
A: SS02A LM Native Selector -> reliability / Top-K -> LM Final Specialist
B: SS02B ACL Native Selector -> reliability / Top-K -> ACL Final Specialist
```

로 병렬 진행한다.

## Kaggle Notebook 실행 규칙

모든 notebook은:

1. Kaggle Import 후 Run All 1회로 완료
2. 필요한 Input 명시
3. CPU/GPU 설정 명시
4. 예상 Run All 시간 명시
5. 완료 output 공유 후 GitHub log / roadmap 현행화
6. Save Version title은 6~59자, 실험 번호 필수

실행 notebook 소스는 repository에 저장하지 않는다.

## 성능 용어

- Fixed Val 결과 = **Val 성능 / Val ROC-AUC**
- 실제 Kaggle 제출 결과만 = **LB / Public LB / Private LB**

## Single-model first 정책

각 target의 기본은:

```text
1 native selector + 1 final specialist
```

3-Fold Final Specialist와 Selector ensemble은 baseline이 아니다.
먼저 single-model specialist의 성능 한계를 확인한 뒤 선택적으로 추가한다.

## 다음 실험

**SS01 Full MRI Single-Slice Inventory / Manifest**

목적:
- raw MRI 전체에서 native single-slice lineage의 실제 input universe를 처음부터 확정
- Study / Series / Slice 수와 DICOM header / path contract 검증
- 224x224 single-slice image cache와 feature cache의 예상 저장량/throughput 산출
- LM / ACL selector가 공유할 공통 manifest 생성

SS01에는 target label을 이용한 slice selection을 넣지 않는다.


### SS01 notebook 전달 상태 — 2026-10-01

- Kaggle title: `SS01 Full MRI Single-Slice Inventory`
- Artifact: `RSNA_Knee_SS01_Full_MRI_Single_Slice_Inventory_v2.ipynb`
- Input: RSNA Knee Abnormality Detection competition data only
- Accelerator: **CPU**
- Expected Run All: **30~90 min**
- Status: **notebook prepared / execution result pending**
- Result sharing: 마지막 셀 로그 + `rsna_knee_ss01_single_slice_inventory_v1.zip`

SS01 결과를 검토한 직후
`SS02A Lateral Meniscus Native Selector`와
`SS02B ACL Native Selector`를 A/B 병렬로 시작한다.


## SS01 — Full MRI Single-Slice Inventory / Manifest — 완료

실행일: **2026-10-01**  
상태: **PASS**

결과:
- 전체 DICOM: **819,635**
- header 성공: **819,635 / 819,635**
- header failure: **0**
- Train: **4,407 studies / 24,371 series / 819,078 slices**
- Visible test sample: **3 studies / 15 series / 557 slices**
- Train Plane slices:
  - Sagittal **340,843**
  - Coronal **243,374**
  - Axial **234,861**
- unknown Plane: **0**
- path fallback Series: **0**
- duplicate relative path: **0**
- duplicate non-empty SOP UID: **0**
- Series <3 slices: **0**
- Header scan runtime: **66.00 min / CPU 8 workers**

Single-slice cache estimate (Train 819,078 slices):
- 224x224 uint8 grayscale: **38.28 GiB**
- 224x224 float16 grayscale: **76.55 GiB**
- DINOv2-Small CLS384 float16: **0.586 GiB**
- DINOv2-Small CLS+PatchMean768 float16: **1.172 GiB**

결론:
- native single-slice lineage의 Study / Series / Slice 계약이 정상 확인됐다.
- 전체 raw image cache를 무조건 복제하기보다 compact DINO feature cache를 활용하는 selector 경로가 저장공간상 유리하다.
- 다음 단계는 A/B 병렬:
  - **SS02A Lateral Meniscus Native Selector**
  - **SS02B ACL Native Selector**

Artifact fingerprint:
```text
ss01_full_mri_single_slice_manifest.parquet
SHA256 = 315e6443bb2c58d29981b17f92086f35b48a2dfb8bc6ee53bc65000a69bdd1eb

ss01_series_summary.parquet
SHA256 = d88c8e5a1e2e7507de8cfe16523385d8e1bb07c88da82078bdcd0dab8f8c0409

ss01_inventory_summary.json
SHA256 = 4d23f8ab468055217fa30365f2efb07470010c85ede36177174fd638e30fe1a8

ss01_integrity_checks.csv
SHA256 = 0460f4e086ca530b0c52c2b88aef209d6ad69e08633e84d908ef87e4f1db3ec9

ss01_cache_size_estimates.csv
SHA256 = b5a9d3fa3054fca72563a032a2d7e1c12db96041a18180b1b780cb6ca1de6d3a

rsna_knee_ss01_single_slice_inventory_v1.zip
SHA256 = 0e66dd3369bb418037db2d979a40d3191f6a6669e3b9833fc59621bc2482577c
```
