# RSNA Knee — Specialist Model Experiment Log

최종 업데이트: **2026-09-30**

> 이 문서는 12개 질환을 하나의 shared multi-label 모델로 동시에 예측하는 기존 계보와 분리하여,
> **질환별 binary specialist (Yes / No) 모델** 계보만 기록한다.
>
> 아직 Specialist 학습 실험은 시작하지 않았다. 현재 문서는 실험 시작 전 기준선, 확정된 사실, 참고 연구를 고정하는 초기 틀이다.

---

# 1. 현재 상태

- **Specialist 완료 실험: 없음**
- 상세 architecture / pilot target / validation 방식 / pseudo-label filtering 정책은 아직 확정하지 않는다.
- 논의가 끝나고 실험 계약이 확정되면 이 문서에 `Specialist Exp S01`부터 결과를 순서대로 추가한다.

현재 전체 프로젝트 기준 최고 Public LB:

- **0.918 — Exp57: 3-Fold Top-24 B3A + 3-Fold Full-MRI Direct 70:30 Hybrid**

가장 최근 K24 / K32 재검증:

| 실험 | K | Fold2 Macro | Fold2 Weak-6 | Public LB |
|---|---:|---:|---:|---:|
| Exp62A-F2-B2Warm | 24 | 0.933333 | 0.911508 | **0.905** |
| Exp62B-F2-B2Warm | 32 | 0.932837 | 0.884127 | **0.905** |

해석:

- 최근 K24/K32 warm-start 계보는 기존 B3A raw 0.907 및 최고 hybrid 0.918을 넘지 못했다.
- K32는 K24 대비 Public LB 개선을 만들지 못했다.
- 따라서 현재는 같은 shared multi-label 계보를 미세 조정하는 것과 별도로, **질환별 전담 binary specialist**라는 독립 축을 검토한다.

---

# 2. Specialist에서 검증하려는 핵심 가설

한 MRI study에는 여러 질환이 동시에 존재할 수 있지만, 각 specialist는 자기 질환의 binary label만 사용한다.

예:

```text
ACL specialist
Study MRI -> ACL Yes / No

MCL specialist
Study MRI -> MCL Yes / No

...

Fracture specialist
Study MRI -> Fracture Yes / No
```

동반 질환은 해당 specialist의 label을 바꾸지 않는다.
예를 들어 ACL=1, Effusion=1인 study는 ACL specialist에서는 ACL positive sample이며, Effusion은 별도 target 정보일 뿐이다.

현재 검토 중인 장점:

- target 간 gradient 간섭을 줄일 수 있음
- 질환별 pseudo-label confidence / masking 정책을 독립적으로 적용 가능
- 질환마다 중요한 slice / sequence / plane이 다른 경우 target-specific input 설계 가능
- 가벼운 backbone을 사용하면 여러 specialist를 순차 inference하는 구조가 가능

현재 검토 중인 위험:

- shared multi-label 학습에서 얻는 공통 representation 이득을 잃을 수 있음
- Gold 58개로 각 binary task의 validation이 여전히 작음
- 특정 질환과 동반 질환의 상관관계를 shortcut으로 학습할 수 있음
- pseudo-label noise가 target별 specialist에 직접 전달될 수 있음

---

# 3. 현재 pseudo supervision 기준

기존 main-line Fold2 학습은 report-only 4,349 study의 pseudo target을 모두 사용하고, 각 target loss에 다음 weight를 적용했다.

```text
pseudo target weight = 0.70 x confidence
```

즉 low-confidence target도 완전히 제외하지 않고 작은 weight로 학습에 남아 있다.

V4 dataset에는 별도로 `rsna_knee_pseudolabels_v4_routed_strict.csv`가 있으며, 이는 low-confidence target/study pair를 NaN/masked 처리해 loss에서 제외하도록 설계한 자료다.

Specialist에서 broad confidence weighting을 유지할지, strict target masking을 사용할지는 **아직 확정하지 않는다.**

---

# 4. 참고 연구

## 4.1 Medical Slice Transformer — knee MRI와 가장 직접적인 근거

- Gustav Müller-Franzes et al., **Medical slice transformer for improved diagnosis and explainability on 3D medical images with DINOv2**, Scientific Reports, 2025
- Link: https://www.nature.com/articles/s41598-025-09041-8
- Knee MRI cohort: 1,199 patients / meniscus tear binary diagnosis
- 구조: 2D DINOv2 image encoder -> slice feature sequence -> 1-layer Slice Transformer -> binary classifier
- 입력은 knee MRI에서 224 x 224 x 32로 표준화
- Knee MRI AUC: MST-DINOv2 **0.85 ± 0.04** vs 3D ResNet **0.69 ± 0.05**, P=0.001
- 전체 MST 약 23M parameters: DINOv2 약 22M + Slice Transformer 약 1M

이 연구는 현재 검토 중인 **가벼운 DINOv2 + slice-level attention + 질환 Yes/No specialist** 구조와 직접적으로 연결된다.

## 4.2 Natural-domain foundation model의 medical classification transfer

- Joana Palés Huix et al., **Are Natural Domain Foundation Models Useful for Medical Image Classification?**, WACV 2024
- Link: https://openaccess.thecvf.com/content/WACV2024/html/Huix_Are_Natural_Domain_Foundation_Models_Useful_for_Medical_Image_Classification_WACV_2024_paper.html
- SAM / SEEM / DINOv2 / BLIP / OpenCLIP을 4개 medical classification dataset에서 비교
- 논문에서는 DINOv2가 standard ImageNet-pretraining baseline을 일관되게 능가했다고 보고

## 4.3 DINOv2 radiology benchmark

- Mohammed Baharoon et al., **Evaluating General Purpose Vision Foundation Models for Medical Image Analysis: An Experimental Study of DINOv2 on Radiology Benchmarks**
- Link: https://arxiv.org/abs/2312.02366
- X-ray / CT / MRI를 포함해 200개 이상의 평가 설정에서 DINOv2 representation을 검증
- disease classification, segmentation, few-shot, linear probing, end-to-end fine-tuning 등을 폭넓게 비교

## 4.4 Competition 참고 — 작은 모델 / single-fold 성능

- Kaggle discussion: **Best single-model score**
- Link: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304
- 공개 사례 중 small ResNet 224 single-fold Public LB 0.936, single-fold 0.938 등의 사례가 공유됨
- 이 자료는 논문이 아니라 competition participant report이므로 재현 가능한 공식 benchmark로 취급하지 않는다.

---

# 5. 기록 형식

실험이 시작되면 각 Specialist 실험은 아래 형식으로 기록한다.

```text
## Specialist Exp Sxx — 설명형 이름

### 목적
무엇을 한 변수로 검증하는지

### 고정 조건
input / split / augmentation / supervision 등

### 변경 변수
이번 실험에서 실제로 바꾼 것

### 결과
Validation / Public LB / target AUC / runtime

### 인사이트
무엇이 확인됐고 다음 실험에 무엇을 남기는지
```

실험 ID만으로 설명하지 않고, 항상 설명형 제목을 함께 사용한다.
