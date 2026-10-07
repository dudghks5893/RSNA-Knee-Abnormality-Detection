# RSNA Knee — Experiment History

최종 업데이트: **2026-10-07**

이 문서는 **완료된 실험과 그 결과만 기록하는 기준 문서**다.
진행 예정 작업과 현재 계획은 [3D_RESNET_EXPERIMENT_PLAN.md](3D_RESNET_EXPERIMENT_PLAN.md)를 따른다.
Kaggle Notebook 작성 규칙은 [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)를 따른다.

---

## 1. 현재 프로젝트 기준점

- Competition: RSNA Knee Abnormality Detection
- Target: 12-label knee MRI multi-label classification
- 현재 최고 Public LB: **0.918**
- 현재 최고 제출: **Exp57 — 3-Fold B3A + 3-Fold Full-MRI Direct 70:30 Hybrid**
- 기존 DINOv2 / MIL / Specialist 계보는 삭제하지 않고 역사 기록으로 보존한다.
- 2026-10-05부터 **3D ResNet + Anatomical Segmentation + Transformer**를 별도 신규 계보로 시작한다.

---

## 2. Exp57 — 현재 Public LB Best

### 구조

- B3A branch: 3-Fold ensemble
- Full-MRI Direct branch: 3-Fold ensemble
- 최종 probability:
  - 0.70 × B3A 3-Fold mean
  - 0.30 × Direct 3-Fold mean

### 결과

- **Public LB = 0.918**
- 현재 프로젝트의 외부 성능 기준점으로 유지한다.

### 의미

향후 신규 구조는 내부 Validation 점수만으로 성공을 판단하지 않는다.
최종적으로 Exp57의 Public LB 0.918을 넘는지가 핵심 외부 기준이다.

---

## 3. Specialist 계보 — First-pass 완료

12개 target별 독립 Specialist의 first-pass 학습은 12 / 12 완료했다.

### Fixed Val best

| Target | Best AUC | Status |
|---|---:|---|
| Medial Meniscus | 0.9937500 | PASS |
| Synovitis | 0.9816000 | PASS |
| Baker's | 0.9750000 | PASS |
| ACL | 0.9609375 | PASS |
| Effusion | 0.9593750 | PASS |
| Contusion | 0.9540625 | PASS |
| Medial OA | 0.9200000 | PASS |
| MCL | 0.9043750 | PASS |
| Lateral OA | 0.8946875 | NOT YET |
| Lateral Meniscus | 0.8940625 | NOT YET |
| PF OA | 0.8925000 | NOT YET |
| Fracture | 0.8788889 | NOT YET |

- Gate PASS: **8 / 12**
- First-pass coverage: **12 / 12**
- target-best Fixed Val simple macro: **0.93410324**

주의:
이 0.9341은 target별로 반복적으로 best checkpoint를 선택한 pseudo 기반 development score다.
Public LB 예상치로 사용하지 않는다.

---

## 4. SS08 — First 12-Specialist Submission

### 구조

- SS03 DINOv2-Base + SS05 Shared MIL: slice selection 용도
- 최종 disease probability에 SS05 MIL direct logits는 사용하지 않음
- Fold ensemble 없음
- Exp57 direct branch 없음
- Exp57 70:30 blend 없음
- 최종 submission은 12개 Specialist sigmoid probability만 사용

### 결과

- **Public LB = 0.876**
- Exp57 대비: **-0.042**
- project best는 **0.918** 유지

### 해석

- pure Specialist-only submission은 현재 hidden test에서 Exp57보다 약했다.
- Fixed Val target-best macro 0.9341과 Public LB 0.876 사이에 큰 generalization gap이 확인됐다.
- Specialist 자체의 문제만으로 원인을 단정하지 않는다.
  - Fold ensemble 제거
  - Full-MRI Direct branch 제거
  - pseudo 기반 반복 model selection
  - hidden-test distribution 차이
  가 동시에 섞여 있다.

---

## 5. 2026-10-05 — 신규 R3D 계보 결정

2026년 knee MRI 최신 연구 방향을 별도로 검토한 뒤,
기존 DINOv2 계보를 즉시 더 튜닝하기보다 **완전히 새로운 3D ResNet 계보**를 시작하기로 결정했다.

### 신규 계보 핵심

- Input: Knee MRI 3D volume
- ROI: **Anatomical Segmentation Mask**
- Backbone candidates:
  - pretrained 3D ResNet34
  - pretrained 3D ResNet50
  - pretrained 3D ResNet101
- Backbone: **Full Fine-tuning**
- LoRA: 현재 신규 계보에 사용하지 않음
- Attention: Backbone 뒤 Transformer Self-Attention 사용
- Output: shared representation + 12 label-specific sigmoid heads
- Validation: Official Gold58 기반 3-Fold OOF
- 초기 빠른 비교 Train data: fold별 약 1,000 report-only pseudo studies + training-side Gold
- 최종 backbone 선택: Gold58 pooled OOF Macro AUROC 우선

### DINOv2 처리

DINOv2는 현재 신규 계보에서 비교 대상에서 제외한다.
기존에 충분히 실험했으며, 3D ResNet 최종 제출이 기대 이하일 경우에만 다시 비교 후보로 복귀한다.


---

## 6. R3D-00A — Gold58 3-Fold + V4 Routing Reproduction Audit

### 목적

- Official Gold58 deterministic multilabel-stratified 3-Fold manifest 생성
- Fold별 12 target Positive / Negative coverage 확인
- 기존 V4 Target-Routed Consensus reader skill / weight / route 공식 재현 감사

### 결과

Gold / split:

- Gold studies: **58**
- Report-only studies: **4,349**
- selected split seed: **20261059**
- Fold sizes:
  - Fold 0: **20**
  - Fold 1: **19**
  - Fold 2: **19**
- 12 target 모두 모든 Fold에서 Positive / Negative 존재: **PASS**
- manifest SHA256:
  - `246f252a1ce4faaafa1b7d30e2c75cde6d79951cb780b0b33bf4f4dd12ad7e4b`

V4 reproduction:

- V2 AUC reproduction: **exact**
- GPT AUC reproduction: **FAIL**
- reader skill / squared weight reproduction: **FAIL**
- route AUC reproduction: **FAIL**
- overall contract: **REVIEW**

주요 max absolute error:

- GPT AUC: **0.0440263**
- V2 AUC: **0.0**
- GPT skill: **0.0880526**
- V2 skill: **0.0**
- GPT/V2 reader weight: **0.0797840**
- simple blend AUC: **0.0286765**

### 원인 분석

기존 V4 method artifact의 `n_gold_used`는 target별 **57**이었다.

현재 source 구조:

- `report_labels_gpt56sol.csv`: Gold 58건 존재
- `report_labels_v2.csv`: Gold overlap 57건

R3D-00A는 GPT를 Gold58 전체에서 평가하고 V2를 57건에서 평가했다.
따라서 두 reader를 같은 calibration population에서 비교하지 못했고,
GPT AUC → reader skill → squared reader weight → blend AUC까지 연쇄적으로 달라졌다.

반면 V2는 기존 V4와 정확히 일치했기 때문에
Gold label / V2 source / AUC code 자체의 문제는 아니다.

### 판정

- **Gold58 3-Fold manifest는 채택**
- **V4 routing reproduction은 미채택**
- 새 3-Fold pseudo 생성은 보류
- 후속: **R3D-00A2 — Common57 V4 Exact Reproduction + Formula Oracle Audit**

R3D-00A2는 GPT와 V2가 모두 존재하는 동일한 Common Gold57에서
기존 reader skill / squared weight / simple / availability-aware routing을 재현하고,
기존 routed-broad 4,349건을 oracle로 label/confidence 공식을 직접 대조한다.


---

## 7. R3D-00A2 — Common57 V4 Exact Reproduction + Formula Oracle Audit

### 결과

- R3D-00A manifest SHA256 exact match: **PASS**
- Common Gold overlap: **57**
- V2 AUC: **12 target 모두 exact**
- GPT AUC / skill / squared reader weight: **FAIL**
- routing math max error: **0.0997151**
- broad label oracle max error: **0.58**
- confidence formula exact reproduction: **FAIL**
- overall status: **REVIEW**

### 해석

Common57로 calibration population을 맞춰도 GPT reference AUC가 재현되지 않았다.
따라서 기존 V4는 report_labels_gpt56sol.csv target 값을 그대로 routing score로 사용한 것이 아니다.
반면 V2 AUC는 계속 exact이므로 Gold / V2 source / AUROC 계산식은 정상이다.

기존 V4 method의 GPT confidence softening 원칙과 master 내부 reader signal을 기준으로
reader preprocessing → route score → final pseudo label/confidence 수학을 추가 복구해야 한다.

### 판정

- Gold58 3-Fold manifest: **최종 채택**
- R3D-00A2 routing / final pseudo formula: **미채택**
- 새 3-Fold pseudo 생성: **계속 보류**
- 후속: **R3D-00A3 — V4 Formula Forensic Audit**

R3D-00A3는 master의 route-independent reader 내부 신호와 기존 V4 fold0~4 / fold policies를
dynamic-route oracle로 사용해 reader preprocessing, route score, label, confidence 수학을 복구한다.

---

## 8. R3D-03A/B/C — MedicalNet R34/R50/R101 + Transformer Backbone Search

### 실행 조건

- Gold58 deterministic 3-Fold: 20 / 19 / 19
- Fold별 leakage-safe Pseudo1000
- canonical MRI cache: **1,446 studies**
- anatomy mask cache: **154 studies**
- input: study당 최대 3 series — Sagittal / Coronal / Axial 각 1개
- tensor: D24 × 96 × 96
- Transformer: d_model=512, 2 layers, 8 heads, FFN 2048, dropout 0.10, Pre-LN, CLS
- Full fine-tuning
- segmentation fusion: global MRI token + mask-weighted anatomy token
- Fold0 LR/WD screening: S1/S2/S3 × 10 epoch
- selected setting full 3-Fold: max20 / min8 / early stopping patience5
- checkpoint: Macro AUROC primary, Macro AUPRC tie-break
- dual-T4 job parallel execution
- validation: FP32
- estimate type: **screened OOF / model-selection estimate**
  - Fold0에서 LR/WD를 선택한 뒤 같은 Gold58의 3-Fold를 평가했으므로 clean/unbiased OOF로 해석하지 않는다.

### Backbone 결과

| Backbone | Selected | Fold0 | Fold1 | Fold2 | Pooled Macro AUROC | Pooled Macro AUPRC |
|---|---|---:|---:|---:|---:|---:|
| **MedicalNet R34** | **S1** | 0.596915 | 0.598180 | 0.582570 | **0.567267** | **0.430502** |
| MedicalNet R50 | S2 | 0.593977 | 0.515280 | 0.510895 | 0.533494 | 0.418787 |
| MedicalNet R101 | S2 | 0.533543 | 0.490685 | 0.583687 | 0.510364 | 0.385794 |

R34 selected config:
- backbone LR: 1e-5
- new-layer LR: 5e-5
- weight decay: 1e-4

R50 / R101 selected config:
- backbone LR: 3e-5
- new-layer LR: 1.5e-4
- weight decay: 1e-4

### R34 target-level pooled OOF

| Target | AUROC | AUPRC |
|---|---:|---:|
| ACL | 0.651961 | 0.653357 |
| MCL | 0.478458 | 0.159523 |
| Medial Meniscus | 0.562500 | 0.561090 |
| Lateral Meniscus | 0.680745 | 0.582810 |
| Medial OA | 0.451163 | 0.272705 |
| Lateral OA | 0.535783 | 0.226810 |
| PF OA | 0.563707 | 0.413502 |
| Effusion | 0.710559 | 0.807573 |
| Synovitis | 0.480287 | 0.464323 |
| Baker's | 0.565217 | 0.244326 |
| Contusion | 0.651822 | 0.423598 |
| Fracture | 0.475000 | 0.356408 |

### Numerical stability finding

MedicalNet full-model FP16 AMP는 안정적이지 않았다.

- R34 screening S1: FP32 forward fallback 1860 / 1920, scaler skip 1, 최종 FP32
- R50 screening S2: FP32 forward fallback 1916 / 1920, scaler skip 1, 최종 FP32
- R101 screening S1/S2/S3: 각 1920 / 1920 forward가 FP32 fallback
- FP32 validation prediction은 finite contract PASS

따라서 후속 R34 실험은 **pure FP32 training / validation**을 기본으로 사용한다.
불필요한 AMP 실패-forward를 반복하지 않는다.

### R34 checkpoints

| Fold | Best epoch | Macro AUROC | SHA256 |
|---|---:|---:|---|
| 0 | 3 | 0.596915 | 90ee978c4110f495327d4077f80b6b56f31228796d920de0cdbe86c3095177fc |
| 1 | 12 | 0.598180 | 205c627d747cefbb18862e6fa189bbb0aaac231329caa3984733f5662526905c |
| 2 | 8 | 0.582570 | 1980717f08cf03c1ca5fbfa3f4f45a7e42af6b8907c9636b6853ae73fa0b215b |

Result ZIP:
- A/R34+R50: r3d03A34B50_dualgpu_results.zip — SHA256 544b30605b3e5e9fbec8da9d0160ee67e4feab30e2bd3a5c38f6f8c3f73b0ac7
- B/R101: r3d03C101_dualgpu_results.zip — SHA256 223ec8ab4201bdaf21a1a9c4f89343e88599448b5402c45af1b02b8ab22acfcd

### 판정

- **Backbone = MedicalNet R34 채택**
- R50 / R101 추가 depth 비교는 중단
- 단, R34 pooled OOF 0.5673은 절대 성능으로는 낮다.
- 현재 architecture에서 final 3D feature map을 즉시 global average pooling하여 series당 MRI token을 1개만 만드는 것이 spatial information bottleneck일 가능성이 높다.
- 대부분의 training studies는 anatomy mask가 없으므로 실제 입력이 최대 3개의 global series token에 크게 의존했다.

---

## 9. R3D-04 — Backbone Selection Decision

### 결론

**MedicalNet R34를 후속 R3D backbone으로 고정한다.**

선택 이유:
1. pooled Macro AUROC 0.567267로 세 후보 중 최고
2. pooled Macro AUPRC 0.430502로 세 후보 중 최고
3. Fold AUROC가 0.5969 / 0.5982 / 0.5826으로 가장 안정적
4. R50 / R101은 depth 증가에도 성능 개선이 없었고 fold 변동이 더 컸다
5. 더 큰 backbone을 유지할 계산비용 근거가 없다

다음 실험은 backbone size가 아니라 **representation 구조**를 바꾼다.

후속: **R3D-05A — R34 Global Token vs Spatial Token Fold0 Screen**

초기 후보:
- GLOB: 기존 global token baseline
- SPT27: global + 3×3×3 = 27 spatial tokens / series
- SPT48: global + 3×4×4 = 48 spatial tokens / series

고정:
- MedicalNet R34
- S1 optimizer setting
- Fold0
- same Pseudo1000 / Gold Train / Gold Val
- pure FP32
- anatomy token policy 유지
- 10 epochs fixed / no early stopping
- primary: best Fold0 Macro AUROC
- tie-break: Macro AUPRC


---

## 10. R3D-05A — R34 Global Token vs Spatial Token Fold0 Screen

### 목적

MedicalNet R34를 고정하고 final 3D feature map의 spatial information을 Transformer에 직접 전달하면
기존 global-average-only representation보다 성능이 좋아지는지 Fold0에서 비교했다.

### 고정 조건

- Backbone: MedicalNet R34
- Fold: Gold Fold0
- Fold0 pseudo: 동일 1,000 studies
- input: D24×96×96, 최대 3 canonical series
- Transformer: d_model512 / 2L / 8H / FFN2048 / dropout0.10
- optimizer: S1 — backbone LR 1e-5 / new-layer LR 5e-5 / WD 1e-4
- pure FP32 training / validation
- 192 samples/epoch × 10 epochs
- no early stopping
- same study sampling / augmentation seed
- anatomy token policy 유지

### 비교

| Variant | Representation | Best epoch | Macro AUROC | Macro AUPRC | Runtime |
|---|---|---:|---:|---:|---:|
| **GLOB** | global token 1개/series | **9** | **0.601827** | 0.499933 | 7.14 min |
| SPT27 | global + 3×3×3 spatial tokens | 8 | 0.595809 | 0.520108 | 10.08 min |
| SPT48 | global + 3×4×4 spatial tokens | 8 | 0.590426 | **0.524856** | 11.55 min |

Spatial vs GLOB:
- SPT27: AUROC -0.006017 / AUPRC +0.020175
- SPT48: AUROC -0.011401 / AUPRC +0.024923

### Target-level 관찰

두 spatial variant에서 공통적으로 AUROC가 좋아진 target:
- Medial OA
- Synovitis
- Baker's

두 spatial variant에서 공통적으로 AUROC가 크게 나빠진 target:
- MCL
- Lateral OA
- Contusion
- PF OA

대표 delta:
- SPT27 Medial OA +0.1200 / Synovitis +0.0900 / Baker's +0.1719
- SPT27 MCL -0.1373 / Lateral OA -0.1250 / Contusion -0.0833
- SPT48 Medial OA +0.1067 / Synovitis +0.0800 / Baker's +0.1094
- SPT48 Lateral OA -0.1563 / Contusion -0.1354 / MCL -0.1176

Gold Fold0가 20 studies뿐이므로 target별 delta는 확정 결론으로 사용하지 않는다.
다만 두 spatial granularity에서 같은 방향이 반복된 target은 후속 label-specific routing 후보로 보존한다.

### 판정

- Primary metric 기준 winner: **GLOB**
- coarse spatial tokens를 모든 label에 공통으로 추가하는 방식은 채택하지 않는다.
- token 수가 늘수록 runtime 증가: SPT27 약 +41%, SPT48 약 +62% vs GLOB
- AUPRC는 spatial에서 상승했지만 primary Macro AUROC가 하락했으므로 3-Fold spatial confirmation은 진행하지 않는다.
- 현재 R34 representation은 GLOB로 유지한다.

### Pure FP32 확인

이전 R34 S1 Fold0 screen reference AUROC는 0.605866이었고, 이번 pure FP32 GLOB는 0.601827이었다.
차이는 -0.004039로 작았으며, pure FP32에서는 AMP 실패-forward 재시도가 없어 Fold0 10 epoch가 약 7.1분에 완료됐다.
후속 R34 screen은 pure FP32를 유지한다.

### 다음 실험

**R3D-05B — R34 Backbone LR Fine-tune Strength Fold0 Screen**

S1이 기존 LR 탐색의 가장 낮은 backbone LR 경계에서 우승했으므로,
representation을 GLOB로 고정한 뒤 backbone fine-tuning 강도를 더 낮은 구간에서 확인한다.

후보:
- FRZ: backbone frozen / new LR 5e-5
- LR3: backbone LR 3e-6 / new LR 5e-5
- LR5: backbone LR 5e-6 / new LR 5e-5
- LR10: backbone LR 1e-5 / new LR 5e-5 baseline

WD는 모두 1e-4로 고정한다.

Result ZIP:
- r3d05a_results.zip
- SHA256 8fbe5d483082999fa68da7e4f8daaf4335e22959f98dfcc22453269d1e7745d7

---

## 11. R3D-05B — R34 Backbone LR Fine-tune Strength Fold0 Screen

### 목적

R3D-05A에서 선택된 MedicalNet R34 + GLOB를 고정하고 pretrained backbone fine-tuning 강도만 비교했다.
기존 R34 screening에서 가장 낮은 경계인 1e-5가 우승했기 때문에 freeze / 3e-6 / 5e-6 / 1e-5를 재비교했다.

### 고정 조건

- MedicalNet R34
- GLOB representation
- Fold0 / 동일 Gold Train-Val / 동일 Fold0 Pseudo1000
- new-layer LR 5e-5
- WD 1e-4
- pure FP32
- BatchNorm running stats frozen
- 192 samples/epoch × 10 epochs
- same seed / study sampling / augmentation

### 결과

| Variant | Backbone LR | Best epoch | Macro AUROC | Macro AUPRC | Runtime |
|---|---:|---:|---:|---:|---:|
| **LR10** | **1e-5** | **9** | **0.601827** | 0.499933 | 7.63 min |
| LR5 | 5e-6 | 8 | 0.591677 | 0.492868 | 7.17 min |
| LR3 | 3e-6 | 8 | 0.582062 | 0.484103 | 7.36 min |
| FRZ | frozen | 9 | 0.579953 | **0.505985** | **3.77 min** |

LR10 대비:
- LR5: AUROC -0.010150 / AUPRC -0.007065
- LR3: AUROC -0.019765 / AUPRC -0.015830
- FRZ: AUROC -0.021874 / AUPRC +0.006052

### 해석

- lower-LR 방향은 성능을 개선하지 않았다.
- backbone을 완전히 freeze하면 runtime은 약 절반으로 줄지만 primary AUROC가 가장 낮았다.
- 1e-5가 lower-bound 우승이었던 이전 결과를 다시 확인했으며, 현재 R34 backbone LR은 **1e-5로 고정**한다.
- LR10의 epoch8 AUROC 0.601744 / AUPRC 0.506908과 epoch9 AUROC 0.601827 / AUPRC 0.499933은 AUROC가 사실상 매우 가깝다.
  다만 사전 정의 primary checkpoint rule에 따라 epoch9가 선택됐다.

### 판정

- **Backbone LR = 1e-5 채택**
- new-layer LR = 5e-5 유지
- WD = 1e-4 유지
- 추가 lower-LR 탐색 중단
- 다음: **R3D-05C — Mask ON vs OFF paired Fold0 ablation**

Result ZIP:
- r3d05b_results.zip
- SHA256 12dd6e311d5ff33b78caab17fd2732cd41033a0276423e84a2caadc8ec0f5026

---

## 12. R3D-05C — R34 Mask ON vs OFF Paired Fold0 Ablation

### 목적

MedicalNet R34 + GLOB + backbone LR 1e-5를 고정하고,
현재 nnU-Net anatomy mask-weighted anatomy token이 classification에 실제로 기여하는지 paired comparison으로 확인했다.

### Paired contract

- MASK_ON / MASK_OFF initial model SHA256 identical: PASS
- sample UID trace SHA256 identical: PASS
- same Fold0 validation UID order: PASS
- pure FP32 forward/backward: PASS
- same optimizer / scheduler / data / augmentation RNG
- contract: PASS

### Mask coverage

- search cache: 1,446 studies
- masks: 154 studies = 10.65%
- Fold0 Gold Train: 38 studies / masked 36
- Fold0 Gold Val: 20 studies / masked 20
- Fold0 Pseudo1000: 1,000 studies / masked 97

Mask availability가 Gold와 pseudo 사이에서 매우 비대칭적이다.
따라서 anatomy token을 사용하면 anatomy content뿐 아니라 mask availability / sample-source 차이도 함께 모델에 들어갈 수 있다.

### 결과

| Variant | Best epoch | Macro AUROC | Macro AUPRC | Runtime |
|---|---:|---:|---:|---:|
| MASK_ON | 9 | 0.601827 | 0.499933 | 8.47 min |
| **MASK_OFF** | **5** | **0.609698** | **0.521793** | 8.47 min |

MASK_ON - MASK_OFF:
- Macro AUROC: **-0.007871**
- Macro AUPRC: **-0.021860**

Target AUROC delta (ON - OFF):
- MCL +0.0784
- Baker's +0.0625
- PF OA +0.0440
- Medial Meniscus +0.0313
- Lateral OA +0.0313
- ACL 0.0000
- Contusion 0.0000
- Lateral Meniscus -0.0104
- Effusion -0.0300
- Medial OA -0.0667
- Synovitis -0.0800
- Fracture -0.1548

### 해석 / 판정

- Primary AUROC와 secondary AUPRC가 모두 MASK_OFF에서 더 높았다.
- 따라서 **현재 154-mask coverage + 현재 mask-weighted anatomy-token fusion은 채택하지 않는다.**
- MASK_ON이 이기지 않았으므로 shuffled-mask / availability-only control은 현재 우선순위에서 제외한다.
- segmentation model 자체의 품질이 나쁘다고 결론 내리는 것은 아니다.
  이번 결론은 현재 coverage와 현재 fusion 방식이 classification에 순이득을 주지 못했다는 뜻이다.
- 후속 R3D 기본 classifier는 **MASK_OFF**로 진행한다.

MASK_ON 결과 0.6018266874 / 0.4999329622는 R3D-05A GLOB 및 R3D-05B LR10과 정확히 재현됐다.
동일 seed/data pipeline의 재현성도 다시 확인됐다.

Result ZIP:
- r3d05c_results.zip
- SHA256 `9ebc077f05572c1b647eff35125db4ae651d17068e512794f95393b0b90620d2`

---

## 13. 기록 원칙

이 문서에는 **실행이 끝난 실험만 추가**한다.

각 완료 실험은 최소한 아래를 기록한다.

- Experiment ID / 이름
- 변경한 변수
- Train / Validation 데이터
- 모델 구조
- 주요 hyperparameter
- Best checkpoint 기준
- 주요 평가 지표
- 실행 시간
- output artifact / checkpoint 이름
- 가능하면 SHA256
- Public LB 제출 시 submission 이름 / Public LB
- 다음 실험에 영향을 주는 해석

계획과 미실행 가정은 이 문서가 아니라 3D_RESNET_EXPERIMENT_PLAN.md에 기록한다.

---

## 13. R3D-06A — All-Series Neutral D24×96 Search Cache

### 목적

기존 Full Manifest v2 inventory를 재생성하지 않고 전체 4,407 studies / 24,371 MRI series를
series selection 없이 기존 R3D preprocessing으로 D24×96×96 float16 search cache로 변환했다.

### 결과

- studies: 4,407 exact
- series: 24,371 exact
- slice manifest rows: 819,078 exact
- pixel decode failures: **0**
- shards: **48**
- cache bytes: **10,780,956,672**
- cache size: **10.04055 GiB**
- build runtime: **2.553 h**
- SeriesInstanceUID unique: PASS
- shard row sum 24,371 exact
- all shard SHA256 present: PASS

### Existing R3D cache parity

- old cache studies: 1,446
- old cache series compared: 4,338
- missing series: 0
- volume mismatch: 0
- metadata mismatch: 0
- **float16 volume exact parity: PASS**
- **plane / Fluid / Fat metadata exact parity: PASS**

따라서 R3D-03~05 계보의 canonical input과 새 all-series cache는 동일 preprocessing 계보로 직접 연결할 수 있다.

### Frozen artifact

- recommended Dataset: `rsna-knee-r3d-all-series-d24-96-v1`
- metadata bundle: `r3d06a_metadata_bundle.zip`
- metadata bundle SHA256: `0aacfaa0e0e19f4ddd541a99b82a00ad547e31e037ee441f9f5599be487d5586`
- series_index.csv SHA256: `6d2ec1d6b8d92455d5a1cfa814fd5aea716c2e24e228738fb84c6e2b073dc8c2`
- shard_manifest.csv SHA256: `940015dc76d55bdbec776630bde640f488ab7538dc41400f635e993821b9ace2`

### 판정

- **R3D-06A PASS**
- Series Composition GPU screen 실행 gate 충족
- 다음 paired screen: **C3 vs P2**

---
## 14. R3D-06B — Series Policy Audit

### 목적

Full Manifest v2의 Series-level metadata만 사용해 실제 MRI Series 분포와
Series Composition GPU screen 후보의 입력량을 정량화했다.

### Contract

- studies: 4,407 exact
- series: 24,371 exact
- slice rows: 819,078 exact
- header errors: 0
- SeriesInstanceUID unique: PASS
- C3 / P2 / ALL study coverage: 4,407 / 4,407
- duplicate Study/Series pairs: 0
- overall: **PASS**

Result ZIP:
- r3d06b_results.zip
- SHA256 `799d6946460a8f08bd7b29ea582f03b741d8f713837df83400e104f3a4dacce5`

### 전체 Series 분포

- Series/study: min 3 / mean 5.5301 / median 5 / p90 7 / p95 9 / max 14
- 3 series 초과 study: 4,406 / 4,407
- 6 series 초과 study: 734
- 8 series 초과 study: 279
- Sagittal / Coronal / Axial missing study: 각각 0

Full Manifest v2의 Fluid_Sensitive / Fat_Suppression 조합은 실제로
`(0,0)` 또는 `(1,1)` 두 종류만 존재했다.

### 정책 규모

| Policy | Selected Series | All 대비 | Mean / Study | Max / Study |
|---|---:|---:|---:|---:|
| C3 | 13,221 | 54.25% | 3.000 | 3 |
| P2 | 21,886 | 89.80% | 4.966 | 6 |
| ALL | 24,371 | 100% | 5.530 | 14 |

C3 → P2:
- +8,665 series
- 추가 series 중 F1/FS1 비율 13.46%
- 즉 86.54%는 F0/FS0

P2 → ALL:
- +2,485 series
- 추가 series 중 F1/FS1 비율 1.57%
- 즉 98.43%는 F0/FS0

### 판정

- 다음 GPU screen의 첫 paired comparison은 **C3 vs P2**로 한다.
- P2는 최대 6 series로 제한하면서 전체 series의 89.8%를 커버해,
  series coverage 증가 효과를 비교하기에 계산량/coverage 균형이 가장 좋다.
- ALL은 P2보다 series 수가 약 11.35%만 더 많지만 max sequence length가 14까지 늘고,
  추가분 대부분이 F0/FS0이므로 첫 screen에서는 보류한다.
- P2가 C3보다 명확히 개선될 때만 ALL을 saturation 확인 후보로 연다.
- R3D-06A all-series cache의 volume/metadata parity PASS 전에는 GPU screen을 실행하지 않는다.

---

## 15. R3D-06C — C3 vs P2 Series Composition Paired Fold0 Screen

### 목적

MedicalNet R34 + GLOB + MASK_OFF classifier를 고정하고,
Study당 canonical 3 series(C3)와 plane별 Top-2 최대6 series(P2)를 paired Fold0 screen으로 비교했다.

### Fairness / contract

- GPU T4 x2
- Gold manifest SHA exact: PASS
- Fold0 Pseudo1000 UID SHA exact: PASS
- R34 pretrained SHA exact: PASS
- R3D-06A series index / shard manifest SHA exact: PASS
- R3D-06A volume / metadata parity: PASS
- old cache C3 selected-Series set/order parity: PASS
- C3 / P2 initial model SHA identical: PASS
- initial model SHA = R3D-05C MASK_OFF reference: PASS
- same training Study UID trace: PASS
- canonical C3-overlap augmentation exact: PASS
- same Fold0 20 validation UID order: PASS
- variants complete: PASS
- overall contract: **PASS**

Result ZIP:
- r3d06c_results.zip
- SHA256 `811dac72ee528eef3a27843c090538641b38b972884708787987b48db7321628`

### 결과

| Policy | Best epoch | Macro AUROC | Macro AUPRC | Runtime | Mean Series/Study | Max |
|---|---:|---:|---:|---:|---:|---:|
| C3 | 5 | 0.609698 | 0.521793 | 7.67 min | 3.000 | 3 |
| **P2** | **1** | **0.613282** | **0.534338** | **11.00 min** | **4.996** | **6** |

P2 - C3:
- Macro AUROC **+0.003584**
- Macro AUPRC **+0.012546**
- runtime 약 **+43.3%**

C3는 R3D-05C MASK_OFF reference 0.6096981725 / 0.5217925010을 **exact 재현**했다.
따라서 새 all-series cache와 기존 R3D classification pipeline 연결은 재현성 관점에서도 확인됐다.

### Target-level delta — P2 minus C3

| Target | Δ AUROC | Δ AUPRC |
|---|---:|---:|
| ACL | -0.375000 | -0.255368 |
| MCL | +0.215686 | +0.281551 |
| Medial Meniscus | -0.052083 | -0.086405 |
| Lateral Meniscus | -0.187500 | -0.079914 |
| Medial OA | -0.133333 | -0.193687 |
| Lateral OA | +0.359375 | +0.387605 |
| PF OA | +0.043956 | +0.034792 |
| Effusion | -0.270000 | -0.155784 |
| Synovitis | +0.180000 | +0.151377 |
| Baker's | +0.375000 | +0.168998 |
| Contusion | +0.041667 | -0.008188 |
| Fracture | -0.154762 | -0.094428 |

AUROC는 6 target 상승 / 6 target 하락, AUPRC는 5 상승 / 7 하락이었다.
즉 macro는 소폭 개선됐지만 label별 반응은 매우 이질적이다.

### 해석 / 판정

- 사전 정의 primary metric 기준 winner는 **P2**다.
- 그러나 Fold0 validation이 20 studies뿐이고 P2 best가 epoch1이라, P2를 최종 series policy로 바로 확정하지 않는다.
- target별로 큰 양/음 delta가 동시에 발생했으므로 label-specific series routing을 이 결과 하나로 도입하지 않는다.
- R3D-05A spatial, R3D-05C mask, R3D-06C series에서 반복되는 target-level 반응은 참고 신호로 누적하되 3-Fold 확인 전까지 routing 근거로 사용하지 않는다.
- 반복 baseline 재학습은 중단한다. C3/P2 계보의 reproducibility가 충분히 확인됐으므로 이후에는 Frozen Reference와 비교한다.
- 다음은 **R3D-06D — Target-Aware Series + Depth Relevance Audit**.
- P2 입력을 유지하되 12개 target query를 새로 학습하고, held-out Gold에서 Series/Depth occlusion으로 target별 유효 Series와 depth 구간을 분석한다.
- Fold0/1을 병렬 실행하고, Fold2는 relevance가 반복될 때만 confirmation으로 사용한다.

---

## 16. R3D-06D — Target-Aware Series + Depth Relevance Audit

### 목적

기존 C3/P2 baseline을 다시 학습하지 않고, P2 input에 target query를 추가해
target별 Series slot 및 D24 depth-bin relevance를 Fold0/1에서 탐색했다.

Primary relevance는 held-out Gold leave-one-Series-out / depth-bin occlusion이며,
attention은 secondary diagnostic으로만 사용했다.

### Contract

- baseline retrained: **False**
- Fold0/1 leakage-safe Pseudo1000: PASS
- R34 / all-series cache SHA contract: PASS
- Fold0 complete: PASS
- Fold1 complete: PASS
- series relevance rows: 144
- depth relevance rows: 864
- overall: **PASS**
- result ZIP SHA256: `c3b044295b143778417724262f6a7f3147fc5e9dfab794f75fb39e7c14af34bf`

### Classifier 성능

| Fold | Best epoch | Macro AUROC | Macro AUPRC |
|---|---:|---:|---:|
| Fold0 TargetQuery-P2 | 10 | 0.586461 | 0.510576 |
| Fold1 TargetQuery-P2 | 1 | 0.527435 | 0.470353 |

Fold0 Frozen P2 Shared-CLS reference:
- AUROC 0.613282
- AUPRC 0.534338

따라서 TargetQuery-P2 Fold0는 frozen P2 대비:
- AUROC **-0.026820**
- AUPRC **-0.023763**

TargetQuery architecture 자체를 최종 classifier 후보로 채택하지 않는다.

### 2-Fold exploratory Series signals

자동 summary는 두 Fold AUROC delta가 양수이고 평균 signed contribution이 양수이면 helpful로 분류했다.
다만 원래 판정 원칙보다 느슨하므로 후속 해석에서는 두 Fold signed contribution까지 같은 방향인지 수동 재검증했다.

더 엄격한 조건에서 남은 exploratory helpful signal:
- ACL → Cor2
- Baker's → Ax1
- Contusion → Cor1
- Lateral Meniscus → Sag1
- Lateral OA → Sag1
- Synovitis → Sag1

단, TargetQuery target별 Full AUROC가 여러 target에서 0.5 미만이었다.
따라서 위 신호를 hard routing에 직접 사용하지 않는다.

특히 상대적으로 해석 신뢰도가 더 높은 target은 Fold0/1 Full AUROC가 모두 0.5 이상이었던
Contusion / Synovitis 쪽이다.

### Depth signals

2-Fold에서 비교적 반복된 normalized D24 후보는:
- Fracture Cor2 D2/D3 (33~67%)
- Lateral OA Sag1 D2/D3 및 Ax1 D3

하지만 해당 TargetQuery classifier의 fold별 target 성능이 불안정하므로 이 역시 exploratory evidence로만 보존한다.

### 판정

- **R3D-06D execution PASS**
- **TargetQuery architecture는 성능상 미채택**
- 06D relevance는 secondary evidence로만 보존
- 같은 약한 TargetQuery를 Fold2에 그대로 반복하지 않는다.
- 다음은 아직 실행하지 않은 P2 Shared-CLS Fold1/2를 새로 학습해,
  실제 P2 classifier에서 직접 Series/Depth occlusion relevance를 측정한다.
- 후속: **R3D-06E — P2 Shared-CLS Fold1/2 + Target-wise Occlusion**

---

## 17. R3D-06E — P2 Shared-CLS Fold1/2 + Target-wise Occlusion

### 목적

Fold0 P2를 다시 학습하지 않고, 아직 실행하지 않았던 P2 Shared-CLS Fold1/2를 새로 학습한 뒤
실제 P2 classifier에서 target별 Series / D24 depth-bin occlusion relevance를 측정했다.

### 실행 / 복구

- GPU0: P2 Shared-CLS Fold1
- GPU1: P2 Shared-CLS Fold2
- Fold1/2 worker returncode: 0 / 0
- training + occlusion 완료
- 최초 Notebook은 aggregation cell에서 sklearn metric top-level import 누락으로 NameError 발생
- GPU artifact는 이미 완성되어 있었으므로 **재학습하지 않고 저장된 output으로 aggregation을 복구**
- recovered result ZIP SHA256: `9c43a7b998f4100725c8cec2d5783a4d2fb41407d800ac44543a0366a29ed230`

### 성능

| Fold | Best epoch | Macro AUROC | Macro AUPRC |
|---|---:|---:|---:|
| Fold1 P2 | 3 | 0.517551 | 0.479572 |
| Fold2 P2 | 6 | 0.588586 | 0.528448 |

Fold1+2 38-study pooled diagnostic:
- Macro AUROC **0.548300**
- Macro AUPRC **0.450897**

주의: 위 pooled 값은 Fold0를 포함하지 않은 Fold1+2 diagnostic이다.

### Strict Series relevance

Fold1/2 모두에서:
- target Full AUROC >= 0.50
- slot present >= 10
- Full-Drop AUROC > +0.005
- Full-Drop AUPRC > 0
- signed logit contribution > 0

를 만족한 Series는 2개였다.

| Target | Series | Mean ΔAUROC | Mean ΔAUPRC | 06D corroboration |
|---|---|---:|---:|---|
| Medial Meniscus | Sag1 | +0.056439 | +0.061633 | No |
| Synovitis | Sag1 | +0.044949 | +0.056513 | Yes |

### Strict Depth relevance

10개 target×series×depth 후보가 strict gate를 통과했다.

대표:
- Medial Meniscus Sag1 D2 [8:12] — mean ΔAUROC +0.056187
- Medial OA Cor1 D2 [8:12] — +0.050000
- Synovitis Cor1 D4 [16:20] — +0.033586
- PF OA Cor1 D4 [16:20] — +0.023810

단 PF OA Fold1 Full AUROC는 0.500이므로 약한 후보로 본다.

### 판정

- target-specific Series relevance는 **Medial Meniscus→Sag1, Synovitis→Sag1** 두 후보만 유지한다.
- occlusion에서 Sag1이 필요하다는 것과 Sag1-only가 최적인 것은 다르므로 별도 paired confirmation이 필요하다.
- baseline 재학습 없이 후속 target-specific input confirmation을 설계한다.

---

## 18. R3D-06F — ALL-Series Saturation Fold0/1

### 목적

P2가 전체 Series의 89.8%를 사용하는 상태에서 남은 Series까지 모두 넣었을 때
classification primary AUROC가 추가 개선되는지 확인했다.

### Contract

- P2 baseline 재학습: **False**
- ALL Fold0 / Fold1만 새로 학습
- initial model SHA = R3D-06C exact
- Fold0 sample UID trace = R3D-06C exact
- Gold / pseudo / R34 / all-series cache contract PASS
- overall: **PASS**
- result ZIP SHA256: `42f6994555a914e9b1389c08b86ab0e9638db2763bca6057291b4a3521b7b6d5`

### 결과

| Fold | Policy | Best epoch | Macro AUROC | Macro AUPRC |
|---|---|---:|---:|---:|
| Fold0 | P2 Frozen | 1 | 0.613282 | 0.534338 |
| Fold0 | **ALL** | **2** | **0.617594** | **0.540314** |
| Fold1 | P2 | 3 | 0.517551 | **0.479572** |
| Fold1 | **ALL** | **1** | **0.548407** | 0.453375 |

Delta:
- Fold0 ALL-P2 AUROC **+0.004312**, AUPRC **+0.005976**
- Fold1 ALL-P2 AUROC **+0.030856**, AUPRC **-0.026197**

Primary Macro AUROC는 Fold0/1 모두 ALL이 높았다.
AUPRC는 Fold1에서 P2가 높아 metric trade-off가 존재한다.

### Target-level Fold1 ALL-P2 AUROC

ALL 개선:
- MCL +0.0625
- Lateral Meniscus +0.1818
- Medial OA +0.0429
- Lateral OA +0.1000
- Effusion +0.0476
- Baker's +0.1000
- Fracture +0.1795

P2 개선:
- ACL +0.0341
- Medial Meniscus +0.0444
- PF OA +0.0119
- Synovitis +0.1250
- Contusion +0.1286

### 판정

- primary AUROC 기준 ALL이 Fold0/1에서 같은 방향으로 우세하다.
- ALL Fold2를 추가해 3-Fold 방향 일치 여부를 확인한다.
- 동시에 P2/ALL 사이의 cap 후보 P3(top3/plane, max9)를 Fold0에서만 먼저 screen한다.
- target-specific Sag1-only는 Medial Meniscus / Synovitis에 대해 별도 fair specialist pair로 확인한다.


---

## 19. R3D-06A~06F — Series / Target Relevance 중간 결론

이 절은 R3D-06A~06F에서 완료된 결과를 한 번에 이해하기 위한 누적 결론이다.

### 데이터 구조

- Study = 한 무릎 검사 단위
- Study 안에 여러 MRI Series가 존재
- Series 안에 여러 Slice가 존재
- 현재 search tensor는 Series 전체를 D24×96×96으로 resample
- 따라서 현재 Series 실험과 Slice/Depth 실험은 서로 다른 축이다.

Series policy:
- C3 = Sagittal / Coronal / Axial 각 Top1 → 정확히 3 Series
- P2 = 각 plane Top2 → 3~6 Series
- ALL = usable Series 전부 → 3~14 Series
- 다음 확인 후보 P3 = 각 plane Top3 → 3~9 Series

### 누적 결과

1. All-Series cache
- 4,407 studies / 24,371 series / 819,078 slices
- decode failure 0
- 기존 cache 4,338 series와 volume / metadata exact parity PASS
- 따라서 이후 series composition 실험은 동일한 MRI preprocessing 위에서 비교 가능

2. C3 vs P2
- Fold0 C3: AUROC 0.609698 / AUPRC 0.521793
- Fold0 P2: AUROC 0.613282 / AUPRC 0.534338
- P2가 macro 기준 소폭 우세
- 그러나 target별 AUROC는 6개 상승 / 6개 하락으로 반응이 크게 갈림

3. TargetQuery 시도
- target별로 다른 Series를 자동 선택하게 하려는 구조를 시험
- Fold0 AUROC 0.586461로 기존 P2 0.613282보다 낮음
- 따라서 TargetQuery architecture는 미채택
- 해당 relevance는 secondary evidence로만 보존

4. 실제 P2 Shared-CLS에서 직접 occlusion
- Fold1 P2: 0.517551 / 0.479572
- Fold2 P2: 0.588586 / 0.528448
- Fold1/2 strict Series 후보:
  - Medial Meniscus → Sag1
  - Synovitis → Sag1
- Synovitis → Sag1은 06D에서도 같은 방향
- Series를 제거했을 때 성능이 반복적으로 나빠졌다는 뜻이며, Sag1-only가 최적이라는 뜻은 아직 아님

5. Depth / Slice-region relevance
- 현재 D24를 6개 구간으로 가려서 검사
- 대표 반복 후보:
  - Medial Meniscus Sag1 D2 [8:12] — 약 33~50%
  - Medial OA Cor1 D2 [8:12] — 약 33~50%
  - Synovitis Cor1 D4 [16:20] — 약 67~83%
- 아직 원본 DICOM slice 번호 확정 단계는 아니며 normalized depth 후보 단계

6. P2 vs ALL
- Fold0: P2 0.613282 → ALL 0.617594, AUROC +0.004312
- Fold1: P2 0.517551 → ALL 0.548407, AUROC +0.030856
- primary Macro AUROC는 현재 2/2 Fold에서 ALL 우세
- 다만 Fold1 AUPRC는 P2 0.479572 > ALL 0.453375로 metric trade-off 존재

### 현재 인사이트

- 단순히 적은 Series만 고르는 것이 항상 유리하지 않다.
- 전체 Series를 더 보여주는 방향이 현재 primary AUROC에서는 유리한 신호를 보인다.
- 동시에 질환마다 유효한 Series가 다르다는 신호도 존재한다.
- 따라서 최종 방향은 다음 두 축을 분리해서 확인한다.
  1. 전체 모델 입력: P2 / P3 / ALL 중 어디가 최적인가
  2. 특정 질환: Sag1 같은 일부 Series만 쓰는 별도 policy가 실제로 이득인가
- relevance 분석만 보고 hard routing을 넣지 않고 실제 학습 비교로 확인한다.
- 이미 재현성이 확보된 baseline은 반복 학습하지 않고 Frozen Reference를 사용한다.
- 서로 독립적인 실험은 두 Kaggle 계정 A/B에서 병렬 실행한다.

### 다음 실행

R3D-06G — Account A:
- GPU0: P3 Fold0
- GPU1: ALL Fold2
- 목적: ALL의 3-Fold 방향 일치와 P3 중간 cap 가치 확인

R3D-06H — Account B:
- Medial Meniscus / Synovitis
- P2 binary specialist vs Sag1-only binary specialist
- 목적: Sag1이 중요하다는 관찰이 Sag1-only 학습 이득으로 실제 이어지는지 확인

R3D-06G / 06H 결과 후 Series policy를 고정하고 R3D-07 Resolution / Depth screen으로 이동한다.


---

## 20. R3D-06G — ALL Fold2 + P3 Fold0

### 목적

R3D-06F에서 ALL-Series가 P2보다 Fold0/1 primary Macro AUROC에서 모두 우세했으므로,
다음 두 질문을 동시에 확인했다.

- ALL Fold2가 P2 Fold2보다도 좋은가?
- P2(max6)와 ALL(max14)의 중간인 P3(plane별 Top3, max9)가 Fold0에서 가치가 있는가?

GPU 병렬:
- GPU0 → P3 Fold0
- GPU1 → ALL Fold2

### Contract

- P2 / 기존 ALL baseline 재학습 없음
- P3 series: 23,915
- P3 mean series/study: 5.4266
- P3 max series/study: 9
- P2 ⊂ P3 ⊂ ALL: PASS
- initial model SHA contract: PASS
- sample UID trace contract: PASS
- overall: **PASS**
- result ZIP SHA256: `b0641481e3d4a8cad2279bcc3ccdc2fc4a5f687d1c32f3b431d66eafa87481b7`

### 결과

P3 Fold0:
- best epoch: 10
- Macro AUROC: **0.624242**
- Macro AUPRC: **0.511143**

비교:
- P3 - P2 Fold0 AUROC: **+0.010960**
- P3 - ALL Fold0 AUROC: **+0.006649**
- 단 AUPRC는 P2/ALL보다 낮음

ALL Fold2:
- best epoch: 3
- Macro AUROC: **0.622678**
- Macro AUPRC: **0.521740**

P2 Fold2 Frozen:
- AUROC 0.588586
- AUPRC 0.528448

ALL - P2 Fold2:
- AUROC **+0.034092**
- AUPRC **-0.006709**

### 누적 Series-policy 해석

Primary Macro AUROC 기준:
- Fold0: ALL > P2
- Fold1: ALL > P2
- Fold2: ALL > P2

즉 **ALL은 P2보다 3/3 Fold에서 AUROC가 높았다.**

동시에 P3 Fold0는:
- P2보다 높음
- ALL보다도 높음

따라서 현재 최종 Series policy를 바로 ALL로 확정하지 않고,
**P3 Fold1/2 확인 가치가 생겼다.**

AUPRC에서는 Fold별 trade-off가 있으므로 최종 선택은
사전 정의 primary AUROC를 우선하되 AUPRC 하락 크기도 같이 기록한다.

### 판정

- ALL-Series의 추가 Series는 단순 noise라고 보기 어렵다.
- P2 확장은 성공적인 방향이었다.
- P3가 Fold0에서 가장 높은 AUROC를 기록했으므로 P3 Fold1/2 confirmation을 진행할 가치가 있다.
- Series policy는 현재 **P3 vs ALL** 최종 경쟁 단계다.
