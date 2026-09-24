# RSNA Knee Abnormality Detection — 5-Fold 최종 실험 / A-B 병렬 실행 설계

최종 업데이트: **2026-09-25**

이 문서는 현재 최고 성능 파이프라인을 5-Fold로 확장하고,
환자별 중요 MRI 선택을 더 안정화하기 위한 **최종 실험 설계 기준 문서**다.

계획은 실험 결과에 따라 수정할 수 있다.
수정할 때는 기존 내용을 조용히 덮어쓰기보다
**왜 순서를 바꾸는지 / 어떤 결과 때문에 바꾸는지**를 함께 기록한다.

> 주의: 아래의 **A / B는 병렬 실행 작업 레인**을 뜻한다.
> 기존 모델 이름인 B3A / B3B의 A/B와는 관계없다.

---


# 0. 실험 번호 규칙

앞으로 주요 실행 단위마다 Exp 번호를 붙여 추적한다.

- **Exp51**: B3A 70% + B2 direct 30% 확률 앙상블
- **Exp52A**: Fold0 task-tuned DINOv2-Base + Head768 학습
- **Exp52B**: Fold1 task-tuned DINOv2-Base + Head768 학습

A/B는 같은 단계의 병렬 실험을 뜻한다.
이후 단계도 같은 방식으로 번호를 순차 부여한다.

---


# 1. 현재 기준점

현재 확인된 Public LB:

- 환자별 Top-24 + 기존 무릎 MRI 가중치 이어받기 최종 모델 (B3A): **0.907**
- 전체 MRI 모든 슬라이스 특징 계층적 직접 예측 (B2 direct): **0.904**
- 동일 Top-24 + 일반 pretrained DINOv2 clean-start (B3B): **0.903**

현재 제출 대기:

- **Exp51 — B3A 70% + B2 direct 30% probability ensemble**
- 결과 대기 중

현재 핵심 관찰:

1. 전체 MRI 정보를 계층적으로 통합하는 것 자체가 강하다.
2. 그 위에서 환자별 Top-24를 골라 raw image로 다시 학습하면 추가 이득이 있다.
3. 현재 Top-24는 Fold2 selector 하나가 결정한다.
4. Fold2 Gold validation은 11명뿐이므로 한 Fold의 선택 판단에 과도하게 의존하지 않는다.
5. 다음 큰 목표는 단순히 모델을 더 크게 만드는 것이 아니라
   **여러 독립 Fold가 각자 중요한 MRI를 판단하게 하고,
   최종 예측을 안정화하는 것**이다.

---

# 2. 현재 Top-24의 정확한 의미

Top-24는 **MRI Series 24개**가 아니다.

한 환자의:

- 모든 MRI Series
- 모든 slice center

를 후보로 만들고,
각 후보를 다음 3장의 묶음으로 구성한다.

```text
[previous slice, center slice, next slice]
```

이를 하나의 **3-slice window**라고 한다.

현재 selector는 환자의 전체 후보 window에 중요도를 매긴 뒤
같은 Series의 너무 가까운 후보가 반복되지 않도록 NMS를 적용하고,
환자당 최종 **24개 window**를 선택한다.

최종 이미지 모델 입력:

```text
[Batch, 24, 3, 224, 224]
```

즉 최종 모델은 환자당 24개의 3-slice window를 본다.

---

# 3. 최종적으로 우선 목표로 하는 5-Fold 구조

가장 먼저 완성할 구조는 **Fold별 독립 selector + Fold별 독립 Top-24 + Fold별 독립 최종 모델**이다.

```text
Hidden test 전체 MRI
        │
        ├─ Fold0 backbone → Fold0 full-MRI MIL → Fold0 Top-24 → Fold0 B3A → 예측0
        ├─ Fold1 backbone → Fold1 full-MRI MIL → Fold1 Top-24 → Fold1 B3A → 예측1
        ├─ Fold2 backbone → Fold2 full-MRI MIL → Fold2 Top-24 → Fold2 B3A → 예측2
        ├─ Fold3 backbone → Fold3 full-MRI MIL → Fold3 Top-24 → Fold3 B3A → 예측3
        └─ Fold4 backbone → Fold4 full-MRI MIL → Fold4 Top-24 → Fold4 B3A → 예측4

                              ↓

                       5개 확률 동일 평균

                              ↓

                        submission.csv
```

중요:

- Fold0이 고른 Top-24를 모든 Fold가 공유하지 않는다.
- 각 Fold는 **자기 selector가 고른 Top-24**를 자기 최종 모델에 넣는다.
- 처음 5-Fold ensemble은 **20%씩 동일 가중치**로 시작한다.
- Fold별 가중치를 Public LB에 맞춰 임의 최적화하지 않는다.

이 구조가 현재 가장 중요한 1차 최종 목표다.

---

# 4. 왜 먼저 5-Fold 독립 파이프라인인가

목적은 두 가지다.

## 4.1 예측 안정화

현재 B3A 0.907은 Fold2 단일 모델이다.

Fold마다 학습 데이터 구성이 달라지면:

- 중요하다고 보는 영상
- 질환별 attention
- 최종 오류 환자

가 달라질 수 있다.

5개의 예측을 평균하면
한 Fold의 우연한 편향을 줄일 가능성이 있다.

## 4.2 사진 선택 자체의 안정성 확인

현재는 Fold2 selector 한 명의 판단이다.

5-Fold가 생기면 같은 환자에 대해:

```text
Fold0 중요도
Fold1 중요도
Fold2 중요도
Fold3 중요도
Fold4 중요도
```

를 모두 얻을 수 있다.

이를 이용해:

- Fold끼리 Top-24가 얼마나 겹치는지
- 어떤 영상은 5개 Fold가 모두 중요하게 보는지
- 어떤 영상은 한 Fold만 중요하게 보는지

를 분석할 수 있다.

---

# 5. Fold별 파이프라인의 데이터 누수 방지 원칙

Fold f의 validation Gold는
Fold f의 아래 모든 학습 단계에서 사용하지 않는다.

```text
Fold f용 Wide9 task backbone
→ Fold f용 전체 MRI feature
→ Fold f용 full-MRI MIL / selector
→ Fold f용 Top-24
→ Fold f용 최종 B3A
```

즉 Fold별로 selector까지 독립적이어야 한다.

**Fold2 selector 하나로 Fold0~4 최종 모델의 Top-24를 전부 만들고
이를 5-Fold라고 부르지 않는다.**

그 방식은 selection 단계에서 validation 정보가 섞일 수 있다.

---

# 6. A/B 병렬 실행 전체 계획

## 단계 0 — Exp51 hybrid 검증 완료

현재:

- B3A: **0.907**
- B2 direct: **0.904**
- B3A 70% + B2 direct 30%: **0.913 — 현재 최고**

결론:

- full-MRI direct branch는 보조 실험 수준이 아니라 **최종 파이프라인에 유지할 핵심 branch**다.
- Top-24 branch와 full-MRI branch가 실제 hidden test에서 상보적이라는 근거가 생겼다.
- 따라서 Fold0 / Fold1 구축은 계획대로 즉시 진행한다.
- 3-Fold / 5-Fold에서도 B3A와 direct를 각각 만든 뒤 hybrid를 우선 검증한다.

---

## 단계 1 — Fold0 / Fold1 selector 계보를 병렬 구축

### A 레인 — Fold0

```text
A1. **Exp52A — Fold0용 Exp11B-style DINOv2-Base 학습**
A2. Fold0 backbone으로 전체 MRI 819,078 window feature 생성
A3. Fold0용 fresh full-MRI hierarchical MIL 학습
A4. Fold0 full-MRI direct validation 기록
A5. Fold0 selector importance 생성
A6. 전체 4,407 study에 Fold0 Top-24 생성
A7. Fold0 Top-24로 Fold0 B3A 최종 모델 학습
```

### B 레인 — Fold1

```text
B1. **Exp52B — Fold1용 Exp11B-style DINOv2-Base 학습**
B2. Fold1 backbone으로 전체 MRI 819,078 window feature 생성
B3. Fold1용 fresh full-MRI hierarchical MIL 학습
B4. Fold1 full-MRI direct validation 기록
B5. Fold1 selector importance 생성
B6. 전체 4,407 study에 Fold1 Top-24 생성
B7. Fold1 Top-24로 Fold1 B3A 최종 모델 학습
```

Fold2는 이미 존재하므로,
단계 1이 끝나면 **Fold0 / Fold1 / Fold2 세 selector와 세 최종 B3A 모델**을 비교할 수 있다.

### 단계 1 체크포인트

반드시 확인:

- 각 Fold Macro AUC
- 각 Fold Weak-6 AUC
- target별 AUC
- Top-24 pairwise overlap
  - Fold0 vs Fold1
  - Fold0 vs Fold2
  - Fold1 vs Fold2
- selected Series 수
- attention concentration / coverage
- NMS fallback 수
- visible test 3 studies에서의 Top-24 overlap
- full-MRI inference 시간 / study

주의:

train study에서 여러 selector를 비교하면
일부 selector는 그 study를 학습에서 본 상태다.
따라서 Top-24 overlap은 **선택 다양성 진단용**이지
엄격한 OOF 성능 지표로 해석하지 않는다.

### 단계 1 중간 제출 — 3-Fold 앙상블

Fold0 / Fold1이 완성되는 즉시 Fold2와 묶어
5-Fold 전체가 끝나기 전에 **3-Fold 중간 Public LB**를 확인한다.

#### 3-Fold full-MRI direct ensemble

Fold0 / 1의 full-MRI MIL이 학습되는 순간 가능하다.

```text
Fold0 full-MRI direct
Fold1 full-MRI direct
Fold2 full-MRI direct
        ↓
       1/3 평균
```

목적:

- full-MRI branch가 Fold 확장으로 실제 안정화되는지 빠르게 확인
- Fold3 / 4까지 확장할 가치 판단

#### 3-Fold B3A ensemble

Fold0 / 1의 Top-24 최종 B3A까지 학습되면 제출한다.

```text
Fold0 selector → Fold0 Top-24 → Fold0 B3A ┐
Fold1 selector → Fold1 Top-24 → Fold1 B3A ├→ 1/3 평균
Fold2 selector → Fold2 Top-24 → Fold2 B3A ┘
```

목적:

- 현재 Fold2 단일 B3A **0.907**을
  Fold0 / 1과의 평균이 넘어서는지 조기 확인
- 5-Fold 완성 전에 fold diversity의 실제 Public LB 이득 확인

처음에는 세 Fold를 **동일 가중치 1/3**로 사용한다.

Exp51이 0.913으로 개선됐으므로
**3-Fold B3A + 3-Fold full-MRI direct hybrid는 우선 제출 후보로 승격**한다.

기본 시작점은 Exp51과 동일하게:

```text
3-Fold B3A ensemble × 0.70
+
3-Fold full-MRI direct ensemble × 0.30
```

으로 두고, 단일 비율을 먼저 확인한다.

---

# 7. 단계 1 의사결정

Fold0 / 1 / 2가 거의 같은 사진만 고르더라도
5-Fold prediction ensemble의 가치는 남아 있다.

다만 **Consensus Top-24의 추가 가치**는 낮아질 수 있다.

반대로 Fold마다 선택이 의미 있게 달라지면서
각 Fold full-MRI 모델 성능도 유지된다면
5-Fold selector 구축의 근거가 강해진다.

Top-24 overlap 숫자 하나에 임의의 절대 합격선을 두지 않는다.
다음 요소를 함께 본다.

- overlap
- CV
- target별 변화
- selected Series 다양성
- attention 분포
- hidden-like visible test 선택 차이

---

# 8. 단계 2 — Fold3 / Fold4 selector 계보 병렬 구축

단계 1에서 구조상 문제가 없으면 바로 진행한다.

### A 레인 — Fold3

```text
A7. Fold3용 task backbone 학습
A8. Fold3 전체 MRI feature 생성
A9. Fold3 full-MRI MIL 학습
A10. Fold3 importance / Top-24 생성
```

### B 레인 — Fold4

```text
B7. Fold4용 task backbone 학습
B8. Fold4 전체 MRI feature 생성
B9. Fold4 full-MRI MIL 학습
B10. Fold4 importance / Top-24 생성
```

이 단계가 끝나면:

- 5개 task backbone
- 5개 full-MRI feature space
- 5개 full-MRI MIL
- 5개 selector
- 5개 Top-24 selection

이 준비된다.

---

# 9. 단계 3 — Fold별 최종 B3A 학습

selector가 모두 준비되면
각 Fold의 Top-24를 사용해
현재 B3A와 같은 최종 raw-image 모델을 학습한다.

학습 recipe의 기본 기준은 현재 Fold2 B3A를 유지한다.

- DINOv2-Base
- physical batch = 4
- grad accumulation = 1
- effective batch = 4
- MIL LR = 2e-4
- backbone late LR = 1e-5
- backbone mid LR = 3e-6
- backbone early LR = 1e-6
- weight decay = 1e-4
- warmup ratio = 0.05
- min LR ratio = 0.01
- max epochs = 12
- patience = 4
- validation interval = 275 optimizer updates
- gradient checkpointing = True

초기화도 Fold2 B3A 원칙을 따른다.

```text
Fold f task-tuned backbone
+
Fold f full-MRI MIL
→ Fold f Top-24 end-to-end final model
```

### 병렬 실행

Fold0 / Fold1 B3A는 3-Fold 중간 제출을 위해 단계 1에서 이미 학습한다.

이 단계에서는:

#### A 레인
- Fold3 B3A

#### B 레인
- Fold4 B3A

Fold2 B3A는 기존 모델을 사용한다.

---

# 10. 단계 4 — 5-Fold B3A prediction ensemble

5개 최종 모델을 모두 확보하면
가장 먼저 단순 동일 가중 평균을 제출한다.

```text
Final probability
= (Fold0 + Fold1 + Fold2 + Fold3 + Fold4) / 5
```

이 실험이 1차 최종 성능 기준이다.

이 단계에서는 아직 Consensus Top-24를 사용하지 않는다.

---

# 11. 단계 5 — 5-Fold full-MRI direct ensemble

각 Fold의 full-MRI MIL은 selector일 뿐 아니라
12개 질환을 직접 예측할 수 있다.

따라서 Fold별 모델이 모두 만들어지면
추가 학습 없이 다음도 확인할 수 있다.

```text
Fold0 full-MRI direct
Fold1 full-MRI direct
Fold2 full-MRI direct
Fold3 full-MRI direct
Fold4 full-MRI direct
        ↓
       평균
```

Fold2 단일 direct model이 이미 Public LB **0.904**였으므로
이 branch도 버리지 않는다.

---

# 12. 단계 6 — 최종 두 계열 ensemble

5-Fold B3A와 5-Fold full-MRI direct가 모두 강하면:

```text
5-Fold Top-24 raw-image ensemble
+
5-Fold full-MRI direct ensemble
```

을 섞는다.

현재 70:30 실험 결과를 참고하되,
최종 5-Fold에서 다시 확인한다.

처음에는 단순한 몇 개 비율만 사용하고
Public LB에 과도하게 비율을 맞추지 않는다.

---

# 13. Consensus Top-24의 정확한 목적

Consensus Top-24는
**5개 Fold에서 각각 24개씩 골라 120개를 최종 모델에 넣는 방식이 아니다.**

5개의 selector가 같은 환자의 전체 MRI 후보에 각각 중요도를 매긴 뒤,
그 의견을 합쳐 **최종 24개 window만 다시 선택**하는 방식이다.

```text
Fold0 중요도 ┐
Fold1 중요도 │
Fold2 중요도 ├→ 5개 의견 통합 → NMS → 최종 Consensus Top-24
Fold3 중요도 │
Fold4 중요도 ┘
```

최종 입력 크기는 기존과 동일하다.

```text
[Batch, 24, 3, 224, 224]
```

---

# 14. Consensus 점수의 1차 설계

Fold마다 attention scale이 다를 수 있으므로
raw attention 값을 바로 평균하는 것을 기본안으로 하지 않는다.

각 Fold 안에서 환자별 전체 window를 중요도 순으로 정렬한 뒤
**정규화된 순위(percentile rank)**로 변환한다.

예:

```text
Fold0: window A = 상위 1%
Fold1: window A = 상위 2%
Fold2: window A = 상위 1%
Fold3: window A = 상위 4%
Fold4: window A = 상위 1%
```

이런 영상은 여러 Fold가 안정적으로 중요하게 본 후보이다.

1차 Consensus 기준:

1. 각 Fold에서 기존과 동일한 target-aware importance 계산
   - `max over 12 targets(joint attention)`
2. study 안에서 중요도 순위를 percentile로 정규화
3. 5개 Fold의 normalized rank를 평균
4. 보조 진단으로 median rank와 Top-24 선택 횟수도 기록
5. same-Series NMS center gap >= 3
6. 최종 24개 선택

처음부터 복잡한 가중 합을 만들지 않는다.

---

# 15. Consensus Top-24의 중요한 leakage 주의

**5개 Fold selector를 모두 사용해 training Gold의 Consensus Top-24를 만들고
그것을 그대로 OOF validation에 사용하는 방식은 leakage가 될 수 있다.**

이유:

어떤 Gold study가 Fold2 validation이라면:

- Fold2 selector는 그 study를 학습에서 보지 않음
- Fold0 / 1 / 3 / 4 selector는 그 study를 학습에서 봤을 수 있음

따라서 5개 selector의 consensus를
Fold2 validation 입력 선택에 사용하면
validation study 정보가 selection 단계에 섞일 수 있다.

그래서 Consensus Top-24는 **5-Fold 독립 파이프라인보다 뒤에 있는 별도 연구 실험**으로 둔다.

하지만 Consensus Top-24를 단순 분석으로 끝내지는 않는다.
선택 방식이 유의미하면 **그 24개를 실제 입력으로 사용하는 전용 최종 이미지 모델도 학습한다.**

개념적으로는 현재 B3A와 동일하다.

```text
현재 B3A
Fold2 selector가 고른 Top-24
→ raw-image DINOv2 + hierarchical MIL 재학습

후속 Consensus 모델
5개 selector 의견을 합친 Consensus Top-24
→ raw-image DINOv2 + hierarchical MIL 재학습
```

즉 질문은:

> “한 Fold가 고른 24장보다 여러 Fold가 공통적으로 높게 평가한 24장만 보여주면
> 최종 이미지 모델이 더 강해지는가?”

를 직접 검증한다.

다만 학습용 Consensus Top-24 생성에는 leakage 문제가 있으므로
다음 두 단계로 진행한다.

### 1차 실용 실험 — OOF-selected training + Consensus hidden-test

각 train study는 **자기 study를 보지 않은 held-out Fold selector**가 고른 Top-24를 사용해
OOF Top-24 training cache를 만든다.

```text
Fold0 study → Fold0 selector가 선택
Fold1 study → Fold1 selector가 선택
...
Fold4 study → Fold4 selector가 선택
```

이렇게 만든 4,407 study OOF Top-24로
새 최종 이미지 모델을 학습한다.

hidden test에서는 정답/학습 노출이 없으므로
5개 selector의 normalized-rank consensus로
Consensus Top-24를 만든 뒤 이 최종 모델에 넣는다.

장점:

- train selection은 각 study에 대해 leakage-free
- 기존 5개 selector를 그대로 활용 가능
- 추가 selector 학습 없이 빠르게 검증 가능

주의:

- train은 single OOF selector Top-24,
  hidden test는 5-selector Consensus Top-24이므로
  selection distribution이 완전히 같지는 않다.
- 따라서 첫 실용 검증으로 사용한다.

### 2차 엄격 실험 — Consensus-trained final model

1차 실험에서 신호가 좋으면
각 outer Fold validation을 보지 않은 **여러 selector replica / seed**를 만들어
그 Fold에 대해 leakage-free consensus를 생성한다.

예:

```text
Outer Fold2 validation
→ Fold2 validation을 전혀 보지 않은 selector seed A
→ Fold2 validation을 전혀 보지 않은 selector seed B
→ Fold2 validation을 전혀 보지 않은 selector seed C
→ 세 의견 consensus
→ Fold2 validation Consensus Top-24
```

필요하면 inner-fold / repeated-fold 구조로 확장한다.

이렇게 하면 학습/검증에서도
“여러 독립 selector의 합의로 고른 Top-24”라는 조건을 더 정확하게 재현할 수 있다.

비용이 크므로
**5-Fold 독립 B3A와 1차 Consensus 모델의 결과를 확인한 뒤** 진행한다.

---

# 16. Top-16 / Top-24 / Top-32 비교 순서

Top-K 최적화는 selector 구조가 확정된 후 한다.

순서:

```text
어떤 영상을 고를지 안정화
→ Fold별 selector / 5-Fold 구조 확정
→ 그 다음 몇 장을 고를지 최적화
```

후보:

- Top-16
- Top-24
- Top-32

현재 기준은 Top-24 유지.

---

# 17. 9시간 제출 제한을 위한 inference 설계

최종 제출 Notebook은
Fold마다 DICOM을 처음부터 다시 읽지 않는다.

한 study에서 먼저:

```text
DICOM decode
→ physical sort
→ 130 mm crop
→ 224 resize
→ full-series 1–99 percentile normalize
→ 3-slice windows 생성
```

을 **한 번만** 수행한다.

그 결과 window를 5개 Fold가 공유한다.

그 다음:

```text
같은 raw windows
   ├→ Fold0 backbone / selector / Top-24 / final
   ├→ Fold1 backbone / selector / Top-24 / final
   ├→ Fold2 backbone / selector / Top-24 / final
   ├→ Fold3 backbone / selector / Top-24 / final
   └→ Fold4 backbone / selector / Top-24 / final
```

두 GPU를 이용해 selector backbone을 병렬 처리한다.

예:

```text
Wave 1
GPU0 → Fold0
GPU1 → Fold1

Wave 2
GPU0 → Fold2
GPU1 → Fold3

Wave 3
GPU0 → Fold4
GPU1 → 가능한 final-model 계산
```

정확한 스케줄은 실제 VRAM / throughput benchmark 후 조정한다.

---

# 18. 앞으로 모든 Fold 실험에서 반드시 기록할 시간

성능만 기록하지 않는다.

각 Fold / submission notebook에서:

- DICOM 전처리 sec/study
- full-MRI DINO feature extraction sec/study
- full-MRI MIL importance sec/study
- Top-24 selection sec/study
- final B3A prediction sec/study
- total sec/study
- peak GPU memory
- decode error count

를 기록한다.

최종 목표는 Public LB뿐 아니라
**hidden test 전체가 9시간 제한 안에 안정적으로 완료되는 것**이다.

---

# 19. A/B 병렬 실행 한 줄 버전

```text
[현재]
Exp51: B3A 0.907 + B2 direct 0.904 → 70:30 ensemble = **0.913 현재 최고**

[1차 병렬]
A: Fold0 backbone → full MRI feature → MIL → Top-24 → Fold0 B3A
B: Fold1 backbone → full MRI feature → MIL → Top-24 → Fold1 B3A

[중간 제출]
3-Fold full-MRI direct equal ensemble (Fold0/1/2)
3-Fold B3A equal ensemble (Fold0/1/2)
3-Fold hybrid: B3A 70% + full-MRI direct 30%

[체크]
Fold0 / Fold1 / Fold2 selector 비교
+ CV / direct prediction / 시간 측정

[2차 병렬]
A: Fold3 backbone → full MRI feature → MIL → Top-24 → Fold3 B3A
B: Fold4 backbone → full MRI feature → MIL → Top-24 → Fold4 B3A

[1차 최종 제출]
5-Fold B3A equal ensemble

[추가 저비용 제출]
5-Fold full-MRI direct equal ensemble

[최종 ensemble 후보]
5-Fold B3A + 5-Fold full-MRI direct

[Consensus 실험]
5-Fold importance 분석
→ Consensus Top-24
→ OOF-selected Top-24로 1차 전용 최종 모델 학습
→ hidden test는 5-selector Consensus Top-24 사용
→ 신호가 좋으면 multi-seed / inner-fold 기반 엄격한 Consensus-trained 모델

[마지막]
Top-16 / Top-24 / Top-32
```

---

# 20. 계획 변경 원칙

이 문서는 현재 기준 계획이다.

다음 결과가 나오면 우선순위를 바꿀 수 있다.

예:

- 70:30 ensemble이 크게 개선됨
- Fold0/1에서 full-MRI 성능이 무너짐
- Fold별 selector가 사실상 동일한 Top-24만 선택함
- 5-Fold inference 예상 시간이 9시간을 초과함
- 새로운 selector가 명확하게 더 좋은 evidence를 찾음

계획을 바꿀 때는
**결과 → 해석 → 변경된 순서**를 이 문서에 함께 기록한다.
