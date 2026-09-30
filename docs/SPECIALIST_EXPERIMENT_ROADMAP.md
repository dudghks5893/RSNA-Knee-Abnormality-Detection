# RSNA Knee — Specialist Model Roadmap

최종 업데이트: **2026-09-30**

> 상태: **실험 전 설계 확정 단계**
>
> Specialist의 큰 구조와 데이터/검증 원칙은 확정했다.
> 아직 남은 핵심 TBD는 pilot target, target-specific candidate rule, Top-K, Slice Transformer 세부 구조, pseudo supervision 세부 정책이다.
> 실제 학습 실험은 이 항목들을 고정한 뒤 시작한다.

완료 기록: [SPECIALIST_EXPERIMENT_LOG.md](SPECIALIST_EXPERIMENT_LOG.md)

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

Specialist 개발용으로 질환별 **Fixed Val 100 studies**를 만든다.

원칙:

- pseudo pool에서 Train과 완전히 분리
- Positive와 Negative를 모두 포함
- 가능한 한 label confidence가 높은 사례 우선
- 한 번 정한 100명은 해당 Specialist 계보에서 계속 고정
- selector rule 발견 / Specialist 학습에서 해당 Val 100을 사용하지 않음
- main metric: target-specific ROC-AUC
- secondary metric: BCE / prediction distribution
- P/N 비율은 모든 질환에 기계적으로 50:50 또는 40:60을 강제하지 않고, 질환별 confidence / class 수를 확인한 뒤 고정

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

## S00-2 — Fixed Val 100 구축

pilot target에 대해 pseudo pool에서 **100 studies**를 완전히 holdout한다.

작업:

- high-confidence Positive 후보 확인
- high-confidence Negative 후보 확인
- class 수와 confidence distribution을 보고 P/N 비율 확정
- Train과 UID 완전 분리
- 이후 모든 Specialist 실험에서 동일 Val 고정

## S00-3 — Training Positive MRI localization audit

Val 100을 제외한 **training Positive studies**를 사용한다.

기존 target-specific full-MRI attention을 참고해:

- 중요 Plane
- 중요 Series / sequence
- slice position
- attention concentration

을 분석한다.

목적은 전체 819,078-window 공간을 매번 모두 탐색하지 않고
질환별 candidate space를 좁히는 것이다.

## S00-4 — Disease-specific candidate rule 확정

S00-3 결과를 바탕으로
label을 알지 못해도 적용할 수 있는 deterministic candidate rule을 정의한다.

예:

```text
All MRI
 -> target-relevant Plane / Series
 -> target-relevant window candidate pool
```

Validation / Test에서도 동일 규칙을 사용한다.

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

Fixed Val 100에서 충분한 개선이 확인된 중요한 checkpoint만 Kaggle Public LB로 확인한다.

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

- **Pilot target**
- Fixed Val 100의 정확한 Positive / Negative 구성
- candidate rule discovery에 사용할 Positive subset
- target-specific candidate Plane / Series 규칙
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
1. Fixed Val 100 먼저 확정
2. Val 100을 모든 discovery / training pool에서 제외
3. Training Positive만으로 localization audit
4. candidate rule freeze
5. frozen rule을 Train / Val / Test에 동일 적용
6. Specialist Train
7. Fixed Val 100 평가
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
