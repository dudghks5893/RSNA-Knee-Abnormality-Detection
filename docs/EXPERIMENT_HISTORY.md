# RSNA Knee — Experiment History

최종 업데이트: **2026-10-05**

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

## 6. 기록 원칙

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
