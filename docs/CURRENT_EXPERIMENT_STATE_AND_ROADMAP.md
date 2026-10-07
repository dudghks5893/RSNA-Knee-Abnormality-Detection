# RSNA Knee Abnormality Detection — 현재 실험 상태 / 데이터 계보 / 다음 로드맵

최종 업데이트: **2026-10-06**

이 문서는 채팅이 바뀌어도 실험을 그대로 이어갈 수 있도록,
현재까지의 데이터 생성 방식, 모델 계보, 정확한 설정값, 결과, 해석,
현재 진행 위치, 다음 실험 순서를 한 곳에 고정해 두는 문서다.

내부 추적용 ID(Exp16B-2, B3A 등)는 보조적으로만 사용한다.
실험 기록 제목은 가능한 한 **누가 봐도 무엇을 바꿨는지 바로 이해할 수 있는 설명형 이름**을 사용한다.


## 2026-10-07 — Current R3D State / R3D-06F Complete

이 섹션이 아래의 오래된 R3D 계획/상태보다 우선한다.

### 현재 확정 classifier

- Backbone: **MedicalNet ResNet34**
- Representation: **GLOB — global MRI token 1개/series**
- Anatomy token / segmentation fusion: **OFF**
- Backbone LR: **1e-5**
- New-layer LR: **5e-5**
- Weight Decay: **1e-4**
- Precision: **pure FP32**
- BatchNorm running stats frozen
- Current search resolution: **D24×96×96**

### R3D-06A — All-Series Neutral Cache

- 4,407 studies / 24,371 series / 819,078 slices exact
- decode failure 0
- 48 shards / 10.04055 GiB
- build 2.553 h
- old R3D cache 1,446 studies / 4,338 series compared
- missing 0 / volume mismatch 0 / metadata mismatch 0
- **volume exact parity PASS**
- **metadata exact parity PASS**
- metadata bundle SHA256: `0aacfaa0e0e19f4ddd541a99b82a00ad547e31e037ee441f9f5599be487d5586`

### R3D-06B — Series Policy Audit

- Series/study mean 5.53 / median5 / p90 7 / max14
- C3: 13,221 series = 54.25%, max3
- P2: 21,886 series = 89.80%, max6
- ALL: 24,371 series = 100%, max14
- 첫 GPU screen은 **C3 vs P2**
- ALL은 P2가 C3보다 개선될 때만 saturation test

### R3D-06C — C3 vs P2 Series Composition Screen

상태: **COMPLETED — PASS**

공정성:
- old-cache C3 selected-Series UID/order exact parity PASS
- same initial model SHA PASS
- same training Study UID trace PASS
- canonical-overlap augmentation exact PASS
- C3는 R3D-05C MASK_OFF metric exact 재현

결과:
- C3: AUROC 0.609698 / AUPRC 0.521793 / best epoch5 / 7.67 min
- P2: AUROC 0.613282 / AUPRC 0.534338 / best epoch1 / 11.00 min
- P2-C3: AUROC +0.003584 / AUPRC +0.012546
- runtime: P2 약 +43.3%
- Result ZIP SHA256: 811dac72ee528eef3a27843c090538641b38b972884708787987b48db7321628

Target-level:
- AUROC 상승 6 / 하락 6
- AUPRC 상승 5 / 하락 7
- 큰 개선: MCL, Lateral OA, Synovitis, Baker's
- 큰 하락: ACL, Lateral Meniscus, Medial OA, Effusion, Fracture
- Fold0 n=20이므로 label-specific routing 근거로 직접 사용하지 않음

### R3D-06D — Target-Aware Series + Depth Relevance Audit

상태: **COMPLETED — PASS / ARCHITECTURE NOT SELECTED**

실행:
- 기존 C3/P2 baseline 재학습 없음
- GPU0 Fold0 TargetQuery-P2
- GPU1 Fold1 TargetQuery-P2
- Series occlusion 144 rows
- Depth occlusion 864 rows
- result ZIP SHA256: c3b044295b143778417724262f6a7f3147fc5e9dfab794f75fb39e7c14af34bf

Classifier:
- Fold0: AUROC 0.586461 / AUPRC 0.510576 / best epoch10
- Fold1: AUROC 0.527435 / AUPRC 0.470353 / best epoch1
- Fold0 frozen P2 Shared-CLS 대비: AUROC -0.026820 / AUPRC -0.023763

판정:
- TargetQuery architecture는 최종 classifier 후보로 채택하지 않음
- 06D relevance는 exploratory / secondary evidence로만 보존
- 자동 helpful gate가 평균 signed contribution을 사용해 원래 의도보다 느슨했음
- stricter manual review에서 Series 후보:
  - ACL Cor2
  - Baker's Ax1
  - Contusion Cor1
  - Lateral Meniscus Sag1
  - Lateral OA Sag1
  - Synovitis Sag1
- 여러 target에서 TargetQuery Full AUROC < 0.5이므로 hard routing 금지

### R3D-06E — P2 Shared-CLS Fold1/2 + Target-wise Occlusion

상태: **COMPLETED — PASS (artifact recovery, no retraining)**

결과:
- Fold1: AUROC 0.517551 / AUPRC 0.479572 / best epoch3
- Fold2: AUROC 0.588586 / AUPRC 0.528448 / best epoch6
- Fold1+2 pooled diagnostic: AUROC 0.548300 / AUPRC 0.450897
- training / occlusion worker는 모두 정상 종료
- aggregation import 누락은 저장된 output으로 posthoc 복구
- recovered ZIP SHA256: 9c43a7b998f4100725c8cec2d5783a4d2fb41407d800ac44543a0366a29ed230

Strict Series candidate:
- Medial Meniscus → Sag1
- Synovitis → Sag1
- Synovitis Sag1은 06D secondary signal과도 일치

Strict Depth candidate는 10개였으나 Series hard routing 후보는 위 2개만 유지.

### R3D-06F — ALL-Series Saturation Fold0/1

상태: **COMPLETED — PASS**

결과:
- Fold0 P2 Frozen: 0.613282 / 0.534338
- Fold0 ALL: 0.617594 / 0.540314
- Fold1 P2: 0.517551 / 0.479572
- Fold1 ALL: 0.548407 / 0.453375

Primary AUROC:
- Fold0 ALL-P2 +0.004312
- Fold1 ALL-P2 +0.030856

따라서 ALL이 AUROC 기준 두 Fold 모두 우세.
Fold1 AUPRC는 P2가 +0.026197 높아 trade-off 존재.

### 현재 A/B 병렬 wave

계정 A — **R3D-06G**
- GPU0: P3 Fold0
- GPU1: ALL Fold2
- 목적:
  - ALL 3-Fold 방향 일치 확인
  - P3(top3/plane, max9)가 ALL에 근접하는지 Fold0 gate

계정 B — **R3D-06H**
- Medial Meniscus / Synovitis에 대해 P2 binary specialist vs Sag1-only binary specialist
- GPU0: P2 control lane
- GPU1: Sag1-only lane
- discovery는 Fold1/2에서 했고 confirmation은 Fold0에서 수행
- pair별 initial SHA / sample trace exact pairing

실행 원칙:
- 이미 존재하는 baseline은 재학습하지 않음
- 새 Fold / 새 policy / fair control이 필요한 architecture change만 학습

<!-- SPECIALIST_2026_10_02_CURRENT_START -->

## 2026-10-04 — Current Specialist State / First-pass Complete

### 1. 목표 / 평가 규칙

- Public LB best: **0.918 — Exp57**
- independent Specialist first-pass: **12 / 12 완료**
- 내부 Gate: target별 **Fixed Val ROC-AUC >= 0.900000**
- Fixed Val은 pseudo 기반 development proxy이며 Public LB가 아니다.
- shared SS05 결과가 0.90을 넘더라도 independent Specialist Gate PASS로 세지 않는다.

### 2. 현재 independent Specialist best

| Target | Best Fixed Val AUC | SS05 ref | Delta vs SS05 | Status | Best experiment |
|---|---:|---:|---:|---|---|
| Medial Meniscus | **0.9937500** | 0.958125 | +0.0356250 | **PASS** | SS07B-G |
| Synovitis | **0.9816000** | 0.982400 | -0.0008000 | **PASS** | SS07B-H |
| Baker's | **0.9750000** | 0.883125 | +0.0918750 | **PASS** | SS07B-F |
| ACL | **0.9609375** | 0.940000 | +0.0209375 | **PASS** | SS07B-E |
| Effusion | **0.9593750** | 0.952500 | +0.0068750 | **PASS** | SS07B-M |
| Contusion | **0.9540625** | 0.875625 | +0.0784375 | **PASS** | SS07B-I2 |
| Medial OA | **0.9200000** | 0.921250 | -0.0012500 | **PASS** | SS07B-J |
| MCL | **0.9043750** | 0.767500 | +0.1368750 | **PASS** | SS07B-A |
| Lateral OA | **0.8946875** | 0.861250 | +0.0334375 | freeze / NOT YET | SS07B-L |
| Lateral Meniscus | **0.8940625** | 0.760625 | +0.1334375 | freeze / NOT YET | SS07A-X1 |
| PF OA | **0.8925000** | 0.898125 | -0.0056250 | freeze / NOT YET | SS07B-K |
| Fracture | **0.8788889** | 0.774444 | +0.1044449 | freeze / NOT YET | SS07B-C |

Independent Gate PASS = **8 / 12**.
NOT YET = **4 / 12**.
Untrained = **0 / 12**.

### 3. Current target-best macro

12개 best Fixed Val AUC 단순 평균:

- **0.93410324**
- 100점 환산: **93.41 / 100**
- SS05 target macro: **0.88124745**
- delta vs SS05 macro: **+0.05285579 = +5.29 points**

주의:
- target마다 별도 Specialist와 best checkpoint를 선택한 결과의 macro다.
- 반복 model selection이 포함된 development score이므로 Public LB 예상치로 해석하지 않는다.

### 4. 마지막 first-pass — SS07B-L Lateral OA

- selector: SS06B uniform K96
- cache: lossless HDF5
- valid_mask -> Transformer src_key_padding_mask
- padding: 120 studies / 763 entries
- Broad class-wise Top-75%
- Fixed Val: 80 = 40P / 40N
- best epoch: **4**
- best AUC: **0.8946875**
- SS05: 0.861250
- delta: **+0.0334375**
- Gate: **NOT YET**
- runtime: **118.54 min**
- checkpoint: ss07b_l_lateral_oa_k96_h5_broad_top75_best.bin
- checkpoint SHA256: ac7e1b690463ddd1a2106773d7d058d6e19f13da147e3dd761db0dbe96786621

Validation trajectory:
- e1 0.833125
- e2 0.870625
- e3 0.876562
- e4 0.894688 BEST
- e5 0.845938
- e6 0.825000
- e7 0.869375
- e8 0.815000

Interpretation:
- SS05보다 의미 있게 상승했지만 0.90 Gate에는 0.0053125 부족했다.
- e4 이후 train loss는 계속 하락하면서 validation AUC가 크게 흔들려 train-validation divergence가 보인다.
- first-pass checkpoint를 보존하고 post-LB 개선 대상으로 이동한다.

### 5. 마지막 first-pass — SS07B-M Effusion

- selector: SS06B uniform K96
- cache: lossless HDF5
- valid_mask -> Transformer src_key_padding_mask
- padding: 120 studies / 763 entries
- Broad class-wise Top-75%
- Fixed Val: 80 = 40P / 40N
- best epoch: **5**
- best AUC: **0.959375**
- SS05: 0.952500
- delta: **+0.006875**
- Gate: **PASS**
- runtime: **140.55 min**
- checkpoint: ss07b_m_effusion_k96_h5_broad_top75_best.bin
- checkpoint SHA256: 47cc7ccc6d66f480f06fd260cb25307e0857fd72c67c615e058178d9b033e002

Validation trajectory:
- e1 0.939375
- e2 0.948750
- e3 0.957500
- e4 0.958125
- e5 0.959375 BEST
- e6 0.949688
- e7 0.950000
- e8 0.926250
- e9 0.926563

Interpretation:
- SS05보다 소폭 개선했고 independent Specialist Gate를 통과했다.
- K96 HDF5 / padding-mask pipeline이 세 uniform target에서 모두 안정적으로 실행됐다.

### 6. Final selected Specialist checkpoints

| Target | Checkpoint SHA256 |
|---|---|
| ACL | d9765e83c2048910a1ba688677014cea4545089c5246ac11af6e85f2c96dda4d |
| MCL | 891f124dc4ee7cb50b506e88308a0a2040a60647f9f7fb2fd08aeef6d1e3ea5c |
| Medial Meniscus | e67161eec0a206d9bc15c813e7034ab6069cf92a1e67916871901d8177b96d45 |
| Lateral Meniscus | 12c4044de1e04e83168f17eb4dea0e5ca4df98ac99ebda6e62dfb3614bfe846a |
| Medial OA | f90fdf5e1ba886c05de8075c83828d57ec70cc13b6937dc56ae1a694e4e13c19 |
| Lateral OA | ac7e1b690463ddd1a2106773d7d058d6e19f13da147e3dd761db0dbe96786621 |
| PF OA | b83b16ab42d43d8b741969136d7c1681a1ba5a84b549aff269b572c9b5677719 |
| Effusion | 47cc7ccc6d66f480f06fd260cb25307e0857fd72c67c615e058178d9b033e002 |
| Synovitis | d4820ee535f1d54e72e1775d47b996e1a6aee4a64c9e115f7f766e8615a64aae |
| Baker's | 853ee3e042d26f388756b65b6b090ef311a47fd1aadf4f01e60acd92e268bf97 |
| Contusion | 6854595836eff585dde5acd8cb20e92817d83fc68c442c77392363d8763c6805 |
| Fracture | c52285d2e2bc536b4ee667bdbb45663c62f630ab75c4abf81a32a038351392d6 |

### 7. SS08 final submission contract

SS08 final notebook status: **RUN COMPLETE / Public LB 0.876**.

Hidden Test inference:

1. DICOM physical ordering / SS04-equivalent single-slice preprocessing
2. SS03 adapted DINOv2-Base -> single-slice feature
3. SS05 Shared Hierarchical MIL -> attention selector for attention-policy targets
4. SS06B frozen target policy -> target-specific K selection
5. selected raw MRI slices -> target-specific DINOv2-Small Specialist
6. each Specialist sigmoid probability -> submission.csv

Critical distinction:
- **SS05 MIL prediction logits are NOT used in final submission.**
- SS05 MIL is used only to obtain target-aware attention for selector targets.
- Lateral OA / PF OA / Effusion use deterministic uniform K96 selection.
- **No Exp57-style 70:30 blend.**
- **No shared-MIL direct prediction branch.**
- Final 12 columns are **12 independent Specialist probabilities only**.

### 8. Post-LB revisit priority

1. Fixed Val < 0.90
   - Fracture 0.8788889
   - PF OA 0.8925000
   - Lateral Meniscus 0.8940625
   - Lateral OA 0.8946875
2. PASS but below SS05
   - Medial OA 0.9200000 vs 0.921250
   - Synovitis 0.9816000 vs 0.982400
3. SS08 Public LB 0.876 원인 분리: Exp57 대비 single-model / no-direct-branch / Specialist 효과 분리

### 9. Operating rules

- exact input root 우선, 전체 /kaggle/input recursive search 금지
- K96 valid_mask를 Transformer padding mask로 반드시 사용
- first-pass best checkpoint 보존
- 같은 Fixed Val에 대한 반복 micro-search 제한
- SS08 Public LB = 0.876; project best는 Exp57 = 0.918 유지

<!-- SPECIALIST_2026_10_02_CURRENT_END -->

---

# 1. 현재 가장 중요한 결론

현재 Public LB 최고 기록은:

- **0.918**
- 내부 추적 ID: **Exp57**
- 구성:
  - Fold0 / Fold1 / Fold2 B3A prediction equal mean
  - Fold0 / Fold1 / Fold2 full-MRI direct prediction equal mean
  - 최종 `0.70 x B3A_3F + 0.30 x DIRECT_3F`

기존 주요 기준:

- Exp16B-3A Fold2 Top-24 raw: **0.907**
- Exp16B-2 full-MRI direct: **0.904**
- Exp51 Fold2 70:30 hybrid: **0.913**
- Exp57 3-Fold 70:30 hybrid: **0.918**

2026-09-30 최신 K24 / K32 재검증:

| Model | K | Fold2 Macro | Fold2 Weak-6 | Public LB |
|---|---:|---:|---:|---:|
| Exp62A-F2-B2Warm | 24 | 0.933333 | 0.911508 | **0.905** |
| Exp62B-F2-B2Warm | 32 | 0.932837 | 0.884127 | **0.905** |

현재 해석:

1. Exp58A에서 K32 inference-only screening은 강한 신호를 보였지만, K32-trained final model의 Public LB 개선으로 재현되지 않았다.
2. K24 / K32 모두 0.905로 동일해 이번 warm-start branch는 기존 B3A raw 0.907에도 미치지 못했다.
3. 이전 all-data / no-validation branch는 K24/K32 70:30 hybrid 모두 0.897로 실패했다. train loss 기반 checkpoint 선택은 일반화 기준으로 부적절했다.
4. clean Fold2 warm-start selector 자체는 Macro 0.954266 / Weak-6 0.933929로 안정적으로 복구됐지만, 그 selector에서 재학습한 final K24/K32는 hidden LB 상승으로 이어지지 않았다.
5. Fold2 Gold11 validation은 여전히 매우 작아 절대값 및 작은 차이를 과신하지 않는다.
6. 현재 최고 0.918과 새 A/B 0.905의 차이를 고려해, A/B 70:30 추가 제출은 우선순위에서 제외한다.

### 새 연구 축 — disease-specific binary specialist

shared 12-label 모델을 계속 미세 조정하는 것과 별도로, **각 질환을 Yes / No로 판단하는 질환별 specialist**를 독립 실험 계보로 분리한다.

- Specialist 완료 기록: [SPECIALIST_EXPERIMENT_LOG.md](SPECIALIST_EXPERIMENT_LOG.md)
- Specialist 계획 초안: [SPECIALIST_EXPERIMENT_ROADMAP.md](SPECIALIST_EXPERIMENT_ROADMAP.md)

현재는 문서 틀과 참고 근거만 생성한다.
architecture / pilot target / pseudo filtering / validation 정책은 사용자와 추가 논의 후 확정하며, 확정 전에는 실제 Specialist experiment 번호를 부여하지 않는다.

### 로드맵 문서 해석 주의

이 문서 아래쪽에 남아 있는 과거의 `현재 다음 실험`, `즉시 다음 액션` 표현은 당시 시점의 역사 기록이다.
**2026-09-30 이후의 실제 우선순위는 이 섹션과 Specialist 전용 로드맵을 우선한다.**

---
# 2. 절대 바꾸지 말아야 할 기본 데이터 / 전처리 계약

## 전체 train 규모

- Study: **4,407**
- MRI Series: **24,371**
- 전체 3-slice window 중심 후보: **819,078**

## DICOM 정렬

우선순위:

1. `ImageOrientationPatient` + `ImagePositionPatient`
2. 위 값으로 physical slice position 계산
3. 불가능하면 `InstanceNumber`
4. 마지막 fallback은 filename natural sort

## 픽셀 전처리

각 DICOM:

- `RescaleSlope`
- `RescaleIntercept`
- `MONOCHROME1`이면 intensity invert
- **130 mm physical center crop**
- **224 × 224 resize**

Series 전체:

- 전체 Series 기준 **1–99 percentile normalization**
- 결과는 **uint8**

## Laterality 정규화

판단 우선순위:

1. `ImageLaterality`
2. `Laterality`
3. DICOM geometric center fallback

오른쪽 무릎:

- Coronal / Axial: horizontal flip
- Sagittal: slice order reverse
- Sagittal reverse 시 metadata row order도 함께 reverse

## 3-slice window

각 center slice마다:

`[previous, center, next]`

를 3채널 입력처럼 구성한다.

경계에서는 nearest valid index를 사용한다.

---

# 3. Supervision 계약

현재 주력 supervision은 **V4 pseudo labels**이다.

Fold2 기준:

- Train total: **4,396**
- Gold: **47**
- Pseudo: **4,349**
- Validation Gold: **11**
- Validation Fold: **2**
- pseudo weight: **0.70 × confidence**

Master Label v2는 이미지 모델 실험에서 성능이 떨어졌으므로
현재 주력 supervision으로 사용하지 않는다.

---

# 4. 모델 계보

## 4.1 기존 강한 고정 위치 이미지 모델

설명형 이름:

**고정된 6개 MRI 구역에서 각 9개 슬라이스를 보는 DINOv2-Base 모델**

내부 ID: **Exp11B**

입력:

- 6 MRI slots
- Sagittal / Coronal / Axial
- fluid-sensitive / non-fluid-sensitive
- slot당 Wide9
- 기존 54 slice 구성

Backbone:

- DINOv2-Base
- hidden 768
- 12 blocks

학습:

- physical batch = **4**
- grad accumulation = **1**
- effective batch = **4**

Fold2:

- Macro AUC: **0.9427579365**
- Weak-6 AUC: **0.9053571429**

Public LB:

- **0.872**

Checkpoint:

`rsna_knee_exp11b_dinov2_base_head768_fold2_fold2_best.bin`

이 checkpoint의 backbone이 이후 전체 MRI feature 생성의 출발점이 되었다.

---

# 5. 전체 MRI feature 생성 — 1세대

설명형 이름:

**전체 MRI의 모든 Series와 모든 slice를 기존 무릎 MRI DINOv2-Base로 특징 추출**

내부 ID: **Exp16B-1**

전체 train:

- 4,407 studies
- 24,371 series
- 819,078 windows

Feature extractor:

- Exp11B에서 task-tuned 된 DINOv2-Base backbone
- 각 window feature:
  - CLS token
  - patch mean
  - concat
- feature dim = **1536**

저장:

- feature dtype = **float16**
- 이후 MIL 학습 시 float32로 로드

relative position:

- float16 저장

실행 결과:

- 전체 처리 완료
- decode error = **0**
- 약 **223.23분**

중요:

- 전체 Series 기준 1–99 percentile normalization을 사용한다.
- 원래 Wide9 모델의 선택된 9장 기준 normalization과는 다르다.
- 이후 full-MRI 계열 실험은 이 B1 전처리 계약을 따라야 한다.

---

# 6. 전체 MRI 특징을 계층적으로 통합해 직접 예측

설명형 이름:

**전체 MRI 모든 슬라이스 특징을 질환별로 계층적으로 통합해 12개 질환을 직접 예측**

내부 ID: **Exp16B-2**

입력:

- Exp16B-1 전체 feature cache

구조:

- feature projection
- plane embedding
- fluid embedding
- fat suppression embedding
- relative position MLP
- target-specific window attention
- target-specific series attention
- 12개 target classifier

즉 이 모델은 단순 selector가 아니라
**그 자체로 최종 12개 질환을 예측할 수 있는 full-MRI prediction model**이다.

Fold2 best:

- Best epoch: **10**
- Macro AUC: **0.9541666667**
- Weak-6 AUC: **0.9152777778**

Target별 AUC:

- ACL: 1.000000
- MCL: 1.000000
- Medial Meniscus: 1.000000
- Lateral Meniscus: 0.8571428571
- Medial OA: 0.9583333333
- Lateral OA: 1.000000
- PF OA: 0.8928571429
- Effusion: 1.000000
- Synovitis: 0.8666666667
- Baker's: 1.000000
- Contusion: 1.000000
- Fracture: 0.875000

Checkpoint:

`exp16b2_full_data_hierarchical_target_mil_fold2_v2_best.bin`

Standalone hidden-test 직접 예측 Public LB:

- **0.904**

비교:

- 기존 Exp11B 고정 Wide9 모델: 0.872
- 전체 MRI 직접 예측: **0.904**
- Top-24 clean-start 최종 모델: 0.903
- Top-24 warm-start 최종 모델: **0.907**

해석:

- 전체 MRI feature를 계층적으로 통합하는 모델 자체가 이미 매우 강하다.
- Top-24 raw-image 재학습은 이 강한 full-MRI 표현 위에서 추가로 약 **+0.003** Public LB 이득을 만들었다.
- 따라서 이후에는 full-MRI 모델과 Top-24 최종 모델을 서로 대체 관계로 보기보다
  서로 다른 표현을 사용하는 두 강한 예측기로 보고 앙상블 가능성을 먼저 확인한다.

---

# 7. 환자별 Top-24 선택

설명형 이름:

**전체 MRI에서 질환별 중요도를 계산해 환자마다 중요한 24개 3-slice window 선택**

내부 ID: **Exp16B-2.5**

중요도 계산:

- Exp11B task-tuned DINO feature
- Exp16B-2 hierarchical MIL의
  - window attention
  - series attention
- joint attention 사용
- 12개 target 중 최대값:
  `target_aware_score = max over 12 targets(joint_attention)`

중복 억제:

- 같은 Series
- center index 차이 **3 이상**
- same-series NMS
- Top-24가 채워지지 않으면 남은 후보를 NMS 없이 fallback

전체 결과:

- 4,407 studies 모두 Top-24 생성
- 평균 선택 Series 수: **5.478103**
- median: 5
- min: 3
- max: 13
- NMS fallback total: **9**
- 평균 expanded attention coverage: **0.821140**
- median: **0.835358**
- min: **0.442223**
- max: **0.978820**
- decode errors: **0**

최종 image cache:

- shape: **[4407, 24, 3, 224, 224]**
- dtype: **uint8**
- 약 **15.92 GB**

---

# 8. 현재 최고 모델 — 기존 무릎 MRI 가중치를 이어받은 Top-24 end-to-end 모델

설명형 이름:

**환자별 중요 영상 24개 + 기존 무릎 MRI 학습 가중치를 이어받아 전체 모델 재학습**

내부 ID: **Exp16B-3A**

입력:

- Exp16B-2.5 Top-24 raw windows

초기화:

- DINOv2-Base backbone:
  **Exp11B task-tuned backbone**
- Hierarchical MIL head:
  **Exp16B-2 trained MIL**

학습:

- physical batch = **4**
- grad accumulation = **1**
- effective batch = **4**
- T4 ×2
- full layer-wise fine-tuning
- gradient checkpointing = True
- max epochs = 12
- early stopping patience = 4
- validation interval = 275 optimizer updates

Learning rate:

- MIL head: **2e-4**
- backbone late: **1e-5**
- backbone mid: **3e-6**
- backbone early: **1e-6**
- weight decay: **1e-4**
- warmup ratio: **0.05**
- min LR ratio: **0.01**

Optimizer groups:

- early: 28.358M
- mid: 28.358M
- late: 28.358M
- norm: 0.002M
- misc: 1.506M
- MIL: 0.761M

전체 trainable params:

- 약 **87.34M**

Best checkpoint:

- epoch: **4**
- step: **828 / 1099**
- validation event: **18**
- optimizer updates total: **4,125**
- Macro AUC: **0.9534722222**
- Weak-6 AUC: **0.9327380952**

Target별 AUC:

- ACL: 1.000000
- MCL: 1.000000
- Medial Meniscus: 0.964286
- Lateral Meniscus: 0.928571
- Medial OA: 0.916667
- Lateral OA: 1.000000
- PF OA: 0.928571
- Effusion: 0.928571
- Synovitis: 0.900000
- Baker's: 1.000000
- Contusion: 1.000000
- Fracture: 0.875000

Checkpoint:

`rsna_knee_exp16b3a_top24_warmstart_dinov2_base_hierarchical_mil_fold2_fold2_best.bin`

Public LB:

- **0.907**

Hidden-test inference:

```text
hidden test 전체 MRI
→ Exp11B task-tuned DINOv2로 모든 slice feature 추출
→ Exp16B-2가 환자별 중요도 계산
→ Top-24 선택
→ Exp16B-3A가 최종 12개 질환 예측
```

중요:

- B3A 자체는 full MRI에서 Top-24를 찾는 모델이 아니다.
- B3A는 이미 선택된 Top-24를 입력으로 받는다.
- hidden test에서는 Top-24가 미리 없으므로
  selector 단계가 반드시 필요하다.

---

# 9. Clean-start 비교 모델

설명형 이름:

**동일한 환자별 중요 영상 24개를 사용하되 일반 pretrained DINOv2부터 새로 학습**

내부 ID: **Exp16B-3B**

B3A와 동일:

- 같은 Top-24
- 같은 DINOv2-Base architecture
- 같은 Hierarchical MIL architecture
- 같은 Fold2 split
- 같은 V4 pseudo labels
- 같은 optimizer / LR / scheduler
- 같은 augmentation
- physical batch 4
- grad accumulation 1

차이:

- backbone:
  generic pretrained DINOv2-Base
- MIL:
  fresh random initialization
- Exp11B / Exp16B-2 학습 가중치를 초기화에 사용하지 않음

Best:

- epoch: **6**
- step: **1099 / 1099**
- validation event: **29**
- optimizer updates: **6,594**
- Macro AUC: **0.9247023810**
- Weak-6 AUC: **0.8799603175**

Public LB:

- **0.903**

해석:

- Top-24 자체의 효과가 매우 크다.
- warm-start가 추가로 +0.004 LB 이득.
- CV에서 A/B 차이는 크게 보였지만 Public LB 차이는 작다.
- Fold2 Gold 11명의 변동성을 다시 확인했다.

---

# 10. 전체 MRI 모든 슬라이스 특징 통합 직접 예측 — Public LB 검증 완료

## 상태: 완료

설명형 이름:

**전체 MRI 모든 슬라이스 특징을 계층적으로 통합하는 모델 자체를 hidden test 최종 예측으로 사용**

목적:

Top-24로 압축하지 않고
Exp16B-2 full-MRI model 자체가 hidden test에서 얼마나 강한지 확인.

추론:

```text
hidden test 전체 MRI
→ 모든 Series / 모든 slice
→ Exp11B task-tuned DINOv2 feature 추출
→ Exp16B-1과 동일하게 feature float16 저장 정밀도 재현
→ Exp16B-2 hierarchical MIL
→ 12개 질환 직접 예측
```

현재 Notebook:

`rsna_knee_full_mri_all_slice_feature_hierarchical_mil_fold2_public_lb_submission_v2.ipynb`

v1 오류:

- stale variable `B2_FILENAME / B2_PATH`가 남아
  `NameError` 발생
- 모델 / inference 논리 문제는 아니었음

v2 수정 및 실행 결과:

- stale variable 제거
- syntax validation 통과
- Exp11B task-tuned feature extractor 정상 로드
- Exp16B-2 hierarchical prediction model 정상 로드
- visible test 3 studies 전체 추론 완료
- window 수: **284 / 135 / 138**
- decode errors: **0 / 0 / 0**
- 최종 submission contract PASS

필요 Inputs:

1. Competition:
   `rsna-knee-abnormality-detection`
2. Kaggle Model:
   Meta Research / DINOv2 / PyTorch / Base / 1
3. Exp11B checkpoint:
   `rsna_knee_exp11b_dinov2_base_head768_fold2_fold2_best.bin`
4. Exp16B-2 checkpoint:
   `exp16b2_full_data_hierarchical_target_mil_fold2_v2_best.bin`

Runtime:

- T4 ×2
- Internet Off
- Notebook submission 방식
- 직접 submission.csv 수동 업로드 방식으로 설명하지 말 것

Public LB 결과:

- **0.904**

비교:

- Exp11B 고정 Wide9: 0.872
- Exp16B-3B 동일 Top-24 clean-start: 0.903
- **Exp16B-2 전체 MRI 직접 예측: 0.904**
- **Exp16B-3A Top-24 warm-start: 0.907**

핵심 해석:

- Top-24 최종 이미지 모델이 아니어도 전체 MRI 모델 자체가 0.904까지 도달했다.
- 즉 성능 상승의 핵심은 “24장으로 줄였기 때문”만이 아니라,
  **전체 MRI에서 질환별 중요도를 학습하고 정보를 계층적으로 통합한 것**에 있다.
- B3A가 0.003 더 높으므로 Top-24 raw-image end-to-end refinement의 추가 효과는 남아 있다.
- 두 모델의 구조와 정보 사용 방식이 다르므로 다음 단계의 저비용 앙상블 실험 가치가 더 커졌다.

---


## Exp51 — Top-24 최종 모델 70% + 전체 MRI 직접 예측 30% 확률 앙상블

설명형 이름:

**환자별 중요 Top-24를 보는 최종 이미지 모델과 전체 MRI 모든 슬라이스를 보는 직접 예측 모델을 70:30으로 확률 앙상블**

구성:

- B3A Top-24 warm-start branch: **0.907**
- B2 full-MRI direct branch: **0.904**
- 최종 확률:
  `0.70 × B3A + 0.30 × B2 direct`

Public LB:

- **0.913 — 현재 최고**

개선폭:

- B3A 단독 0.907 대비 **+0.006**
- B2 direct 단독 0.904 대비 **+0.009**
- Exp11B 고정 Wide9 0.872 대비 **+0.041**

핵심 해석:

- Top-24에 집중하는 branch와 전체 MRI 정보를 유지하는 branch가 hidden test에서 실제로 상보적이다.
- “MIL이 중요하다”는 방향은 맞지만, 더 정확히는 **full-MRI hierarchical MIL이 보존한 정보가 Top-24 raw-image 모델에 추가적인 유효 신호를 제공한다**는 결과다.
- B3A 자체도 hierarchical MIL을 사용하므로, 이번 +0.006을 단순히 “MIL 유무” 차이로 해석하지 않는다.
- 이후 3-Fold / 5-Fold에서도
  **Top-24 B3A ensemble + full-MRI direct ensemble의 hybrid**를 핵심 제출 후보로 유지한다.

---


## Exp52A / Exp52B — Fold0 / Fold1 task-tuned DINOv2-Base backbone 구축

목적:

- 기존 Fold2 Exp11B recipe를 그대로 유지하고 validation Fold만 바꿔
  Fold0 / Fold1의 독립적인 task-tuned backbone 계보를 만든다.
- 이후 각 Fold backbone으로 전체 MRI 819,078 window feature를 생성하고
  Fold별 full-MRI MIL / Top-24 / B3A로 이어간다.

공통 설정:

- DINOv2-Base + Head768
- Wide224 / Wide9 / 6 MRI slots
- physical batch 4
- grad accumulation 1
- effective batch 4
- V4 pseudo labels
- pseudo weight = 0.70 × confidence
- deterministic 5-Fold split, seed 2026

### Exp52A — Fold0

- Validation Gold: **11**
- Best: **epoch 9 / epoch-end / step 1099**
- Macro AUC: **0.830886243**
- Weak-6 AUC: **0.788029101**
- Wall time: **183.18 min**
- Checkpoint:
  `rsna_knee_exp52a_fold0_tasktuned_dinov2_base_head768_fold0_best.bin`

Target AUC:

- ACL 0.966667
- MCL 0.555556
- Medial Meniscus 0.928571
- Lateral Meniscus 0.785714
- Medial OA 0.875000
- Lateral OA 0.777778
- PF OA 0.750000
- Effusion 0.821429
- Synovitis 0.833333
- Baker's 0.944444
- Contusion 0.857143
- Fracture 0.875000

### Exp52B — Fold1

- Validation Gold: **12**
- Best checkpoint: **epoch 7 / step 6 / intra-epoch**
- Best epoch fraction: **6.005**
- Macro AUC: **0.885819004**
- Weak-6 AUC: **0.902926587**
- Early stop: epoch 10
- Wall time: **138.56 min**
- Checkpoint:
  `rsna_knee_exp52b_fold1_tasktuned_dinov2_base_head768_fold1_best.bin`

Target AUC:

- ACL 0.843750
- MCL 1.000000
- Medial Meniscus 1.000000
- Lateral Meniscus 0.657143
- Medial OA 1.000000
- Lateral OA 0.555556
- PF OA 1.000000
- Effusion 1.000000
- Synovitis 0.916667
- Baker's 0.962963
- Contusion 0.850000
- Fracture 0.843750

해석:

- 두 실험 모두 checkpoint / prediction / log 저장과 output contract를 통과했다.
- Fold0의 Wide9 Macro / Weak-6는 Fold2보다 낮고,
  Fold1은 Macro는 낮지만 Weak-6는 Fold2와 비슷하다.
- 각 Fold validation은 11~12명뿐이므로 이 단계의 Wide9 AUC만으로
  Fold0/1 계보를 중단하지 않는다.
- 현재 목적은 동일 recipe에서 **Fold별 독립 backbone을 확보**하는 것이다.
- 다음 단계에서 실제 핵심인
  **전체 MRI feature → fresh full-MRI MIL → direct prediction / importance / Top-24**
  성능을 확인한 뒤 Fold별 selector 품질을 판단한다.

다음:

- **Exp53A:** Fold0 backbone으로 전체 MRI 819,078 window feature 생성
- **Exp53B:** Fold1 backbone으로 전체 MRI 819,078 window feature 생성

---


## Exp53A / Exp53B — Fold0 / Fold1 전체 MRI feature cache 생성 완료

### Exp53A — Fold0
- Source backbone: Exp52A Fold0
- Studies: **4,407**
- Series: **24,371**
- 3-slice windows: **819,078**
- Feature: **CLS 768 + PatchMean 768 = 1536**
- dtype: **float16**
- Decode errors: **0**
- Runtime: **200.44 min**
- Seconds/study: **2.729**
- Output size: **2.546 GiB**
- 상태: **PASS**

### Exp53B — Fold1
- Source backbone: Exp52B Fold1
- Studies: **4,407**
- Series: **24,371**
- 3-slice windows: **819,078**
- Feature: **CLS 768 + PatchMean 768 = 1536**
- dtype: **float16**
- Decode errors: **0**
- Runtime: **241.14 min**
- Seconds/study: **3.283**
- Output size: **2.546 GiB**
- 상태: **PASS**

두 Fold 모두 동일한 full-series 전처리 계약을 유지했고,
Fold별 feature space를 서로 섞지 않는다.

다음:
- **Exp54A:** Fold0 fresh full-MRI hierarchical MIL
- **Exp54B:** Fold1 fresh full-MRI hierarchical MIL

---


## Exp54A / Exp54B — Fold0 / Fold1 fresh full-MRI hierarchical MIL 완료

공통:

- 입력: 각 Fold의 Exp53 full-MRI 819,078-window feature cache
- 모델: FullDataHierarchicalMIL
- MIL은 random initialization부터 새로 학습
- pseudo weight: 0.70 × confidence
- 다른 Fold MIL checkpoint warm-start 없음
- checkpoint / validation prediction / attention export / summary contract PASS

### Exp54A — Fold0

- Validation Gold: **11**
- Best epoch: **4**
- Macro AUC: **0.797552910**
- Weak-6 AUC: **0.737433862**
- Same-fold Wide9 Exp52A:
  - Macro **0.830886243**
  - Weak-6 **0.788029101**
- 변화:
  - Macro **-0.033333333**
  - Weak-6 **-0.050595238**
- Training: **8.08 min**
- Checkpoint:
  `exp54a_fold0_full_data_hierarchical_target_mil_v1_best.bin`

### Exp54B — Fold1

- Validation Gold: **12**
- Best epoch: **13**
- Macro AUC: **0.872472994**
- Weak-6 AUC: **0.861805556**
- Same-fold Wide9 Exp52B:
  - Macro **0.885819004**
  - Weak-6 **0.902926587**
- 변화:
  - Macro **-0.013346010**
  - Weak-6 **-0.041121032**
- Training: **14.17 min**
- Checkpoint:
  `exp54b_fold1_full_data_hierarchical_target_mil_v1_best.bin`

해석:

- Fold0/1에서는 Fold2 Exp16B-2와 달리 full-MRI direct validation이 같은 Fold Wide9보다 상승하지 않았다.
- 따라서 **full-MRI direct 성능 향상이 모든 Fold에서 자동으로 재현되는 것은 아니다.**
- 다만 validation은 11~12명으로 매우 작고, direct AUC와 selector 유용성은 완전히 같은 질문이 아니다.
- 현재 5-Fold 설계의 핵심은 독립 selector가 고르는 Top-24의 다양성과 최종 B3A 성능을 확인하는 것이므로,
  Exp54A/B를 즉시 폐기하지 않고 다음 Top-24 생성 단계로 진행한다.
- 3-Fold direct ensemble은 Fold0/1/2 결과를 모두 확보한 뒤 실제 OOF / hidden inference 구조에서 다시 판단하며,
  Fold별 direct branch 가중치를 지금 validation 11~12명만으로 조정하지 않는다.

다음:

- **Exp55A:** Fold0 MIL → 전체 4,407명 중요도 → Fold0 전용 Top-24 cache
- **Exp55B:** Fold1 MIL → 전체 4,407명 중요도 → Fold1 전용 Top-24 cache

---


## Exp55A / Exp55B — Fold별 Top-24 선택 + Persistent Image Cache 완료

### Exp55A — Fold0

- selector: Exp54A Fold0 full-MRI MIL
- 후보 window: 819,078
- study: 4,407
- Top-K: 24
- NMS: same-series center gap >= 3
- selected series mean / median: **5.4786 / 5**
- NMS fallback total: **12**
- expanded attention coverage mean / median: **0.8060 / 0.8230**
- cache shape: **[4407, 24, 3, 224, 224] uint8**
- decode errors: **0**
- cache build: **107.51 min**
- output size: **14.839 GiB**
- status: **PASS**

### Exp55B — Fold1

- selector: Exp54B Fold1 full-MRI MIL
- 후보 window: 819,078
- study: 4,407
- Top-K: 24
- NMS: same-series center gap >= 3
- selected series mean / median: **5.5022 / 5**
- NMS fallback total: **19**
- expanded attention coverage mean / median: **0.8436 / 0.8572**
- cache shape: **[4407, 24, 3, 224, 224] uint8**
- decode errors: **0**
- cache build: **105.29 min**
- output size: **14.839 GiB**
- status: **PASS**

해석:

- Fold0/1 모두 각자의 backbone → full-MRI feature → MIL → Top-24로 독립 lineage를 유지했다.
- selected-series 분포는 기존 Fold2와 유사하지만 attention coverage는 Fold별 차이가 있다.
- selector validation AUC가 Fold2보다 낮았어도 Top-24 final model 성능과 동일한 의미는 아니므로
  다음 단계에서 raw-image end-to-end B3A 성능을 확인한다.

다음:

- **Exp56A:** Fold0 Top-24 + Fold0 backbone/MIL warm-start 최종 모델
- **Exp56B:** Fold1 Top-24 + Fold1 backbone/MIL warm-start 최종 모델

---

# 10.5. 2026-09-25 최종 5-Fold / A-B 병렬 실행 설계 확정

상세 설계는 다음 문서를 우선 기준으로 사용한다.

`docs/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md`

현재 중요한 변경점:

- 단일 Fold2 B3A backbone으로 전체 MRI feature를 다시 만드는 실험은 **즉시 최우선에서 제외**한다.
- 다음 큰 검증은 Fold0 / Fold1을 A/B 병렬로 새로 구축해
  Fold2와 함께 **selector가 실제로 다른 사진을 고르는지** 확인하는 것이다.
- Exp51 70:30 hybrid가 **0.913**으로 새 최고를 기록했으므로,
  Fold 확장 후에도 **B3A 계열과 full-MRI direct 계열을 둘 다 유지하고 hybrid를 우선 검증**한다.
- 신호가 유지되면 Fold3 / Fold4도 A/B 병렬로 확장한다.
- 1차 최종 구조는
  **Fold별 독립 selector → Fold별 Top-24 → Fold별 B3A → 5개 예측 평균**이다.
- Consensus Top-24는 5개 selector의 의견을 합쳐 최종 24개 window를 고르는 별도 후속 연구 실험이다.
- Consensus는 train/validation leakage 문제가 있으므로
  5-Fold 독립 파이프라인보다 먼저 주력 모델로 사용하지 않는다.
- 최종 제출은 9시간 제한을 고려해
  study당 DICOM decode / crop / normalization / 3-slice window 생성을 한 번만 수행하고
  5개 Fold가 같은 raw window를 공유하도록 설계한다.
- 모든 Fold 실험에서 sec/study와 GPU memory를 함께 기록한다.

현재 A/B 병렬 요약:

```text
A: Fold0 backbone → full MRI feature → MIL → Top-24
B: Fold1 backbone → full MRI feature → MIL → Top-24
          ↓
Fold0 / Fold1 / Fold2 selector 비교
          ↓
A: Fold3 pipeline
B: Fold4 pipeline
          ↓
A: Fold0 B3A → Fold3 B3A
B: Fold1 B3A → Fold4 B3A
Fold2 B3A는 기존 모델 사용
          ↓
5-Fold B3A equal ensemble
          ↓
5-Fold full-MRI direct ensemble
          ↓
두 계열 ensemble
          ↓
Consensus Top-24 연구
          ↓
Top-16 / 24 / 32
```

---

# 11. 현재 확정 로드맵

아래 기존 순서는 당시 기준 기록으로 유지한다.
**2026-09-25 이후 실행 우선순위는 `docs/FINAL_5FOLD_PARALLEL_EXPERIMENT_PLAN.md`를 우선한다.**
새 결과가 나오면 근거를 기록한 뒤 변경한다.

## 1. 전체 MRI B2 직접 예측 Public LB — 완료

결과: **0.904**

목적:

- full-MRI prediction model 자체의 hidden-test 일반화 확인
- Top-24 최종 이미지 모델이 왜 좋아졌는지 분해
- 이후 ensemble 기준점 확보

---

## 2. 현재 최고 Top-24 모델 + 전체 MRI 직접 예측 모델 앙상블 — 현재 다음 실험

조건:

- 1번 Public LB **0.904 확인 완료**
- B3A Public LB **0.907**

후보:

- Exp16B-3A 예측
- Exp16B-2 직접 예측

처음에는 단순 probability blend 위주로 비교.

예시 후보:

- A 0.8 + B2 0.2
- A 0.7 + B2 0.3
- A 0.6 + B2 0.4
- 0.5 + 0.5

정확한 비율은 1번 Public LB와 prediction distribution 확인 후 결정한다.

목적:

- Top-24 raw image model과
- full-MRI feature model의 서로 다른 정보 사용 여부 확인

새 학습 비용이 거의 없으므로 우선순위가 높다.

---

## 3. 현재 최고 B3A backbone으로 전체 MRI feature 재생성

설명형 이름:

**현재 최고 Top-24 이미지 모델에서 학습된 DINOv2 backbone으로 전체 MRI 모든 슬라이스 특징을 다시 생성**

핵심 가설:

B3A는 Public LB 0.907까지 성능이 향상됐으므로
Exp11B backbone과 다른, 더 질환 판별에 적합한 feature space를 배웠을 가능성이 있다.

절대 주의:

- B3A의 MIL을 그대로 전체 100~500+ windows에 바로 적용하지 않는다.
- B3A는 학습 당시 Top-24만 입력받았다.
- 24개 attention 환경과 수백 개 full-MRI attention 환경은 다르다.

따라서 B3A에서 사용하는 것은 우선 **DINOv2 backbone**이다.

전체 data contract는 Exp16B-1과 동일하게 유지:

- 4,407 studies
- 24,371 series
- 819,078 windows
- same DICOM sort
- same 130 mm crop
- same 224 resize
- same full-series 1–99 percentile normalization
- same laterality canonicalization
- same 3-slice windows
- CLS + patch mean
- feature dim 1536
- feature 저장 dtype float16
- relative position float16

B3A backbone checkpoint source:

`rsna_knee_exp16b3a_top24_warmstart_dinov2_base_hierarchical_mil_fold2_fold2_best.bin`

checkpoint에서 backbone state만 정확히 추출해 사용한다.

---

## 4. B3A backbone feature로 새로운 full-MRI selector 재학습

설명형 이름:

**현재 최고 이미지 모델의 feature 공간에서 전체 MRI 중요 영상 선택 모델을 새로 학습**

중요:

기존 Exp16B-2 MIL weights를 그대로 붙이지 않는다.

이유:

- 기존 B2 MIL은 Exp11B feature space에서 학습됨
- B3A backbone은 end-to-end fine-tuning 후 feature distribution이 달라졌을 수 있음
- 기존 B2 MIL을 그대로 쓰면 feature-space mismatch가 생긴다

기본 실험:

- architecture는 Exp16B-2와 동일한 Hierarchical MIL
- feature input만 B3A backbone 기반 새 full-MRI feature로 교체
- MIL은 **fresh initialization**
- Fold2 split 동일
- V4 supervision 동일
- 가능한 한 B2와 동일한 optimizer/training recipe 유지
- 비교 변수는 feature source가 되도록 통제

검증:

- Fold2 Macro AUC
- Weak-6 AUC
- target별 AUC

기존 기준:

- B2 Macro: 0.954167
- B2 Weak-6: 0.915278
- B2 standalone Public LB: **0.904**

추가 검증 원칙:

- 새 B3A-backbone feature로 학습한 full-MRI MIL은 selector 역할뿐 아니라
  **그 자체로 12개 질환을 직접 예측할 수 있는 모델**이다.
- 따라서 새 MIL이 Fold2에서 기존 B2와 동등하거나 개선되면,
  새 Top-24 전체 재생성에 들어가기 전에 **standalone Public LB를 먼저 확인**한다.
- 이유는 기존 B2 direct prediction이 이미 0.904로 강했기 때문에,
  B3A feature 공간이 full-MRI 직접 예측 자체를 개선하는지 분리해서 볼 가치가 크다.

---

## 5. 기존 selector와 새 selector 비교

반드시 아래를 함께 본다.

### 예측 성능

- Fold2 Macro
- Fold2 Weak-6
- target별 AUC

### 선택 변화

- 기존 Top-24 vs 새 Top-24 overlap
- study별 overlap 분포
- 평균 / median overlap
- 최소 / 최대 overlap

예시 해석:

- overlap 22~24 수준:
  거의 동일한 영상을 선택
  → selector 재생성의 실익이 작을 수 있음

- overlap 10~15 수준:
  중요 영상 판단이 크게 달라짐
  → 새 feature space가 evidence selection을 바꾼다는 신호

### 추가 진단

- selected series count
- target별 attention concentration
- Top-K cumulative attention coverage
- expanded ±1 slice coverage
- NMS fallback count

---

## 6. 새 selector로 전체 4,407 study Top-24 재생성

조건:

5번에서 새 selector가 충분한 근거를 보였을 때 진행.

정책 기본값:

- target-aware score = max over 12 target joint attention
- same-Series NMS center gap >= 3
- Top-24
- 부족하면 fallback fill

새 cache는 기존 cache와 별도 이름으로 저장한다.

기존 cache를 덮어쓰지 않는다.

---

## 7. 새 Top-24로 최종 이미지 모델 재학습

목적:

2세대 patient-specific selection pipeline 완성.

개념:

```text
1세대
Exp11B backbone
→ B2 selector
→ Top-24
→ B3A
→ Public LB 0.907

2세대 후보
B3A backbone
→ 새 full-MRI selector
→ 새 Top-24
→ 새 end-to-end final model
→ Public LB ?
```

초기 비교에서는
기존 B3A와 가능한 한 동일한 학습 recipe를 유지한다.

변수:

- 새 selector가 만든 Top-24

필요 시 이후 초기화 전략을 별도 ablation 한다.

---

## 8. Top-16 / Top-24 / Top-32 비교

이 실험은 selector 개선 뒤에 한다.

이유:

현재 selector를 기준으로 K를 먼저 최적화하면
새 selector가 만들어졌을 때 다시 반복해야 할 수 있다.

순서:

1. 어떤 영상을 고를지 개선
2. 몇 장을 고를지 최적화

기본 후보:

- Top-16
- Top-24
- Top-32

나머지 조건은 최대한 동일하게 유지.

---

## 9. 최종 구조 확정 후 5-Fold 학습 + ensemble

가장 마지막에 진행.

이유:

현재 구조가 아직 변경될 가능성이 있다.
지금 5-Fold를 먼저 하면
새 selector 성공 시 전체를 다시 반복해야 한다.

중요한 leakage 원칙:

각 Fold는 반드시 Fold-specific이어야 한다.

즉 Fold f에서는:

- Fold f Gold validation을 encoder / selector / final model 학습에 사용하지 않음
- Fold별 backbone
- Fold별 full-MRI feature
- Fold별 selector
- Fold별 Top-K
- Fold별 final model

hidden test에서도
각 Fold 파이프라인이 자기 selector로 Top-K를 다시 고른 뒤 예측하고,
마지막에 Fold prediction을 평균한다.

---

# 12. 현재 로드맵 한 줄 버전

```text
[완료]
1. 전체 MRI B2 직접 예측 Public LB = 0.904

[현재 다음]
2. B3A 0.907 + B2 직접예측 0.904 앙상블

[다음 핵심 실험]
3. B3A backbone으로 전체 MRI feature 재생성
4. 그 feature로 새로운 전체 MRI selector 재학습
5. 기존 selector와 새 selector 비교
   - Fold2 Macro / Weak6
   - Top-24 overlap
   - 선택 Series 수
   - attention coverage
6. 새 selector로 전체 4,407 study Top-24 재생성
7. 새 Top-24로 최종 이미지 모델 재학습

[그 다음]
8. Top-16 / Top-24 / Top-32 비교

[구조 확정 후]
9. 최종 방식 5-Fold 학습 + ensemble
```

---

# 13. 실험 기록 원칙

앞으로 README / 문서 / 커밋에는
`B3A`, `B2.5` 같은 내부 ID만 적지 않는다.

권장:

- “전체 MRI 모든 슬라이스 특징을 질환별로 통합해 직접 예측”
- “환자별 중요 영상 24개 + 기존 무릎 MRI 학습 가중치를 이어받아 재학습”
- “현재 최고 이미지 모델의 backbone으로 전체 MRI 특징을 재생성”
- “새 feature 공간에서 환자별 중요 영상 선택 모델을 재학습”

내부 ID는 괄호 보조 표기로만 사용한다.

예:

**환자별 중요 영상 24개 + 기존 무릎 MRI 가중치 이어받기 (Exp16B-3A)**

---

# 14. 실수 방지 체크리스트

새 notebook을 만들기 전에 반드시 확인한다.

1. Competition submission은 **Notebook submission**
   - `/kaggle/working/submission.csv` 생성
   - Save Version / Run All
   - Notebook output을 Competition Submission으로 제출
   - 사용자에게 “submission.csv를 직접 업로드”라고 안내하지 않는다.

2. physical batch / grad accumulation을 임의로 바꾸지 않는다.
   - B3 계열 기준: **4 / 1 / effective 4**

3. DICOM preprocessing을 임의 변경하지 않는다.

4. full-MRI B1 계열은
   **Series 전체 1–99 percentile normalization**을 사용한다.

5. right Sagittal은
   volume과 metadata order를 함께 reverse한다.

6. B3A 기반 새 full-MRI selector 실험에서
   **기존 B2 MIL을 그대로 재사용하지 않는다.**
   우선 fresh MIL로 feature-source effect를 검증한다.

7. B3A 자체를 수백 개 full-MRI window에 바로 넣어
   selector처럼 쓰지 않는다.

8. Fold2는 Gold 11명뿐이다.
   작은 AUC 차이를 확정적 결론으로 표현하지 않는다.

9. Public LB가 크게 움직이면
   CV와 LB의 관계를 함께 기록한다.

10. 기존 dataset / cache / checkpoint를 덮어쓰지 않는다.
    새 실험은 새 slug / filename을 사용한다.

---

# 15. 현재 즉시 다음 액션

현재 해야 할 일은:

**B3A Top-24 warm-start 모델과 전체 MRI 직접 예측 모델의 확률 앙상블을 검증한다.**

확정된 Public LB:

- B3A Top-24 warm-start: **0.907**
- 전체 MRI 직접 예측: **0.904**

우선 비교할 blend 후보:

- B3A 0.8 + Full-MRI 0.2
- B3A 0.7 + Full-MRI 0.3
- B3A 0.6 + Full-MRI 0.4
- B3A 0.5 + Full-MRI 0.5

가능하면 단순 LB 제출 전에 두 모델의 visible-test prediction correlation / target별 차이도 확인한다.

앙상블 확인 후에는 로드맵 **3번:
B3A backbone으로 전체 MRI feature 재생성**으로 넘어간다.


---


## Exp56A / Exp56B — Fold0 / Fold1 전용 Top-24 최종 B3A 완료

### Exp56A — Fold0
- Top-24: Exp55A Fold0 selector
- Backbone init: Exp52A Fold0
- MIL init: Exp54A Fold0
- Best: epoch 2 / step 826 / validation event 8
- Macro AUC: **0.824735**
- Weak-6 AUC: **0.738095**
- 상태: PASS

### Exp56B — Fold1
- Top-24: Exp55B Fold1 selector
- Backbone init: Exp52B Fold1
- MIL init: Exp54B Fold1
- Best: epoch 7 / step 6 / validation event 30
- Macro AUC: **0.897401**
- Weak-6 AUC: **0.914054**
- 상태: PASS

해석:
- Fold1은 Top-24 end-to-end refinement에서 Exp52B / Exp54B보다 개선됐다.
- Fold0은 여전히 낮은 validation을 보이지만 Gold validation이 11명뿐이므로 3-Fold hidden-test ensemble에서 실제 일반화를 확인한다.
- Fold0/1/2 모두 각자 독립 backbone → full-MRI MIL → Top-24 → final B3A 계보를 확보했다.

## Exp57 — 3-Fold B3A + 3-Fold Full-MRI Direct 70:30 Hybrid

별도 3-Fold direct / 3-Fold B3A 제출을 먼저 하지 않고,
Fold2에서 Public LB 0.913을 만든 70:30 구조를 바로 3-Fold로 확장한다.

```text
P_B3A_3F   = mean(Fold0 B3A, Fold1 B3A, Fold2 B3A)
P_DIRECT_3F = mean(Fold0 direct, Fold1 direct, Fold2 direct)

P_FINAL = 0.70 × P_B3A_3F + 0.30 × P_DIRECT_3F
```

구현 원칙:
- study DICOM decode / sort / crop / normalize 1회
- 각 Fold task-backbone feature 1회
- 같은 Fold feature를 direct branch와 selector branch가 공유
- Fold별 Top-24는 각 Fold selector가 독립적으로 선택
- branch prediction을 별도 저장해 이후 ratio 변경을 재추론 없이 할 수 있게 유지

## Exp58A — Fold2 Top-K 빠른 스크리닝

대규모 Top-K 재학습 전에 Fold2 Gold 11명에서
기존 K24-trained B3A를 이용해 **K16 / 20 / 24 / 28 / 32** inference sensitivity를 비교한다.

목적:
- K24보다 낮은 K가 비슷한 성능이면 계산량 절감 후보
- K28/32가 개선 신호면 새 K cache + final model 재학습 후보
- 이 단계는 inference-only screen이므로 최종 결론이 아니라 재학습 후보 결정용



---

# 2026-10-01 Specialist 최신 실행 상태 — 다음 채팅 우선 기준

기존 3-slice window Specialist 실험 S00-3/S00-4는 historical reference로 유지한다.
현재부터의 주력 계보는 **native single-slice specialist**이다.

## 병렬 Pilot

- **Lane A: Lateral Meniscus**
- **Lane B: ACL**

두 target은 첫 class-specific 단계부터 A/B 병렬로 진행한다.
공통 raw-data inventory / manifest처럼 두 target이 완전히 공유하는 작업은 중복 실행하지 않고 한 번만 수행한다.

## 기본 모델 단위

```text
1 target
= 1 native single-slice Selector
+ 1 Final Specialist
```

기본 전체 구성은 12 selectors + 12 final specialists = 24 checkpoints.
3-Fold는 baseline이 아니며, single-model 성능 개선이 막힌 target부터 선택적으로 적용한다.

Hidden Test에서는 target별로 반드시:

```text
Hidden Test Full MRI
-> target-specific Selector
-> target-specific Top-K single slices
-> target-specific Final Specialist
-> probability
```

를 실행한다.

## 용어

- **Val ROC-AUC / Val 성능**: Fixed Val에서 측정한 내부 개발 지표
- **LB / Public LB / Private LB**: 실제 Kaggle submission 후 Leaderboard에서 받은 점수

Val 결과를 LB라고 부르지 않는다.

## Notebook 운영 계약

앞으로 모든 Kaggle 실행 notebook은 아래를 지킨다.

1. Import 후 **Run All 한 번으로 전체 실행 가능**해야 한다.
2. 답변에 필요한 **Kaggle Input 설정과 필요한 파일/데이터셋**을 명시한다.
3. **GPU / CPU 중 무엇을 선택할지** 명시한다. GPU가 필요하지 않은 단계는 CPU를 사용한다.
4. **Run All 예상 소요시간**을 대략 제시한다.
5. 사용자가 완료 output을 공유하면 결과를 분석한 뒤 GitHub에
   - 실험 결과
   - artifact fingerprint
   - 현재 진행 상태
   - 다음 액션
   을 기록한다.
6. Kaggle Save Version용 notebook 제목은 **6~59자**이며 **실험 번호를 반드시 포함**한다.

실행 코드는 GitHub에 저장하지 않고 Kaggle-importable `.ipynb` artifact로 전달한다.

## 현재 다음 순서

```text
SS01  Full MRI Single-Slice Inventory / Manifest      [NEXT, shared]
      ↓
SS02A Lateral Meniscus Native Selector                [A]
SS02B ACL Native Selector                             [B]
      ↓
각 lane Selector reliability / Top-K audit
      ↓
SS03A LM Final Specialist
SS03B ACL Final Specialist
      ↓
Fixed Val 평가
      ↓
구조가 통과하면 나머지 10 targets를 A/B 병렬 확장
      ↓
12-target hidden-Test inference
      ↓
실제 Kaggle submission -> LB 확인
```

SS01은 두 target 공통 prerequisite이므로 한 번만 실행한다.
SS01에서는 500GB raw MRI를 바로 대규모 이미지 cache로 복제하지 않고,
전체 single-slice 수 / Series / Study / 경로 / DICOM header 구조와
cache 예상 크기를 먼저 확정하여 이후 A/B selector의 I/O 전략을 결정한다.


---

# 2026-10-01 Specialist 최신 완료 상태



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


현재 즉시 다음:
```text
A: SS02A Lateral Meniscus Native Selector
B: SS02B ACL Native Selector
```
