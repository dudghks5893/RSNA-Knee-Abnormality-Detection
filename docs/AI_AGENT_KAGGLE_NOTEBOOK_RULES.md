# AI Agent Rules — Kaggle Notebook Delivery

최종 업데이트: **2026-10-05**

이 문서는 RSNA Knee 프로젝트에서 AI Agent가 사용자에게 Kaggle Notebook을 설계/작성/수정해서 전달할 때 반드시 따라야 하는 규칙이다.

이 규칙은 실험 내용과 별개로 **모든 Kaggle Notebook 작업에 공통 적용**한다.

---

# 1. 기본 원칙

Notebook은 사용자가 Kaggle에 Import한 뒤 **위에서부터 Run All / Save Version만 하면 재현 가능**해야 한다.

금지:

- 중간 셀 수동 수정 요구
- 이전 세션 변수/메모리에 의존
- 사용자가 셀을 특정 순서로 수동 실행해야만 동작하는 구조
- 임시 경로를 사람이 직접 바꾸어야 하는 구조
- output 파일을 사람이 중간에 옮겨야 하는 구조
- 전체 /kaggle/input 재귀 탐색

필수:

- clean session에서 Run All 가능
- deterministic input resolution
- seed 고정
- 모든 계약 검증
- output 자동 저장
- 오류 시 초기에 명확하게 fail-fast

---

# 2. Notebook 첫 Markdown Cell 필수 정보

모든 Notebook 첫 부분에 아래를 반드시 적는다.

1. **Experiment ID / 실험명**
2. **실험 목적**
3. **이번 실험에서 변경하는 변수**
4. **고정 조건**
5. **Required Kaggle Inputs**
6. **Kaggle Runtime 설정**
7. **예상 실행 시간**
8. **추천 Save Version 이름**
9. **예상 Output**
10. **성공 기준 / 비교 기준**

---

# 3. Experiment ID

모든 Notebook은 명확한 실험 번호를 가진다.

신규 3D ResNet 계보 예:

- R3D-00
- R3D-01
- R3D-02
- R3D-03A
- R3D-03B
- R3D-03C
- R3D-04

Notebook 파일명, Markdown title, output artifact에 Experiment ID를 포함한다.

예:

~~~text
R3D-03A_ResNet34_Transformer_Fold0.ipynb
r3d03a_r34t_fold0_best.pt
r3d03a_r34t_fold0_epoch_log.csv
~~~

---

# 4. Save Version / Notebook 이름

사용자가 Kaggle에서 바로 사용할 수 있도록 매번 **추천 Save Version 이름**을 제공한다.

규칙:

- **60자 이내**
- 실험 번호 포함
- 핵심 변경점 포함
- 너무 긴 설명 금지
- Final이라는 단어는 정말 최종 제출일 때만 사용

예:

~~~text
R3D-03A R34T Fold0 Baseline
R3D-03B R50T Fold1 Baseline
R3D-01 Anatomical Segmentation
~~~

Notebook 전달 답변에도 추천 이름을 명시한다.

---

# 5. Kaggle Runtime 설정

매 Notebook마다 반드시 명시한다.

예:

~~~text
Accelerator: T4 x2
Internet: Off
Run mode: Save & Run All
Expected runtime: 45~60 min
~~~

CPU-only 작업이면:

~~~text
Accelerator: None (CPU)
~~~

GPU가 필요한지 애매하게 적지 않는다.

GPU를 사용한다면 실제 코드가 GPU를 사용하는지 확인한다.

T4 x2를 지정하면:

- DataParallel / DDP 등 실제 2 GPU 사용 여부 명시
- physical batch / effective batch 명시
- VRAM 사용을 실제 로그로 확인

과거 작은 batch를 사용했다는 이유만으로 새 모델의 batch를 임의로 낮추지 않는다.
GPU headroom을 먼저 확인한 뒤 결정한다.

---

# 6. Required Kaggle Inputs — 가장 중요한 규칙

사용자가 Kaggle Add Input에서 **검색해서 바로 찾을 수 있는 정확한 이름**을 제공해야 한다.

반드시 다음 형식을 사용한다.

~~~text
[Experiment # / experiment name]
→ Kaggle Dataset / Competition / Model name
→ actual required filename(s)
~~~

예:

~~~text
[R3D-00 / Data Audit]
→ RSNA Knee Abnormality Detection
→ train.csv, train_series.csv, train_series/

[R3D-00 / Data Audit]
→ rsna-knee-v4-consensus-dataset
→ rsna_knee_pseudolabels_v4_routed_broad.csv
~~~

Model도 동일하다.

~~~text
[R3D-03A / ResNet34 Transformer]
→ <verified Kaggle Model name>
→ <verified actual weight filename>
~~~

중요:

- Kaggle UI에서 검색할 **표시 이름**을 명시
- 가능하면 owner / slug도 함께 기록
- 실제 Notebook에서 읽는 **정확한 filename** 명시
- Dataset root / expected path 명시
- 존재 여부를 코드에서 assert
- 아직 실제 이름을 확인하지 못한 Dataset/Model 이름은 **절대 만들어내지 않는다**
- 이름을 모르면 먼저 검색/확인하고 Notebook을 작성한다

이 동일한 Input 설명을:
1. 사용자에게 보내는 답변
2. Notebook 첫 Markdown
두 곳 모두 넣는다.

---

# 7. Input Path Resolution 규칙

금지:

~~~text
Path("/kaggle/input").rglob(...)
Path("/kaggle/input").glob("**/*")
~~~

처럼 전체 Kaggle Input을 재귀 탐색하는 방식.

과거 global recursive search가 10분 이상 걸린 적이 있으므로 사용하지 않는다.

우선순위:

1. **검증된 exact path**
2. Path.exists() 확인
3. 필요할 경우 **알려진 Dataset root 내부에서만** 제한 탐색

예:

~~~text
/kaggle/input/competitions/rsna-knee-abnormality-detection/
/kaggle/input/datasets/yhlucas/rsna-knee-v4-consensus-dataset/
~~~

fallback search가 필요해도 해당 root 바깥으로 나가지 않는다.

---

# 8. Run All 보장

Notebook은 처음 셀부터 마지막 셀까지 한 번의 실행으로 끝나야 한다.

필수:

- import
- config
- input validation
- data load
- preprocessing/cache
- model load/build
- training
- validation
- checkpoint
- inference
- output save
- final artifact check

필요한 단계가 모두 연결되어 있어야 한다.

중간 산출물이 이미 존재한다고 가정하지 않는다.
외부 Input이 필요하면 Required Inputs에 명확히 적는다.

---

# 9. Config / Reproducibility

Notebook 상단에 config를 모은다.

최소 기록:

- experiment_id
- seed
- input size
- batch size
- gradient accumulation
- effective batch
- learning rate
- weight decay
- epochs
- patience
- scheduler
- model name
- pretrained source
- fold
- target list
- segmentation version
- data manifest/version

seed는 Python / NumPy / PyTorch 모두 설정한다.

determinism을 완전히 보장할 수 없는 CUDA 연산이 있으면
bitwise reproducibility를 과장하지 않는다.

---

# 10. Controlled Experiment 규칙

A/B 실험에서는 무엇을 바꾸는지 명확하게 적는다.

예:

~~~text
Changed:
3D ResNet34 → 3D ResNet50

Fixed:
Gold Fold split
Pseudo UID manifest
Segmentation mask
Transformer
Loss
Epoch
Checkpoint rule
Evaluation
~~~

여러 변수를 동시에 바꾸고 한 변수의 효과라고 해석하지 않는다.

모델 크기별 hyperparameter 최적화가 필요한 경우:

- 각 모델에 같은 값 강제 금지
- 동일한 HPO budget 제공
- 각 모델의 최적 설정을 기록

---

# 11. Validation Leakage 규칙

Gold58 OOF를 사용할 경우:

- held-out Gold는 그 Fold model의 학습에 절대 사용하지 않음
- held-out Gold를 이용해 만든 pseudo routing / feature / selector도 금지
- pseudo labels가 Gold-derived라면 Fold-aware leakage-safe version 사용
- preprocessing statistics도 필요하면 training side에서만 계산
- segmentation fitting이 competition Gold annotation을 이용한다면 Fold 분리 적용

OOF 조건:

- 58 Gold study 모두 정확히 한 번 held-out prediction
- duplicate UID 금지
- missing UID 금지

마지막 셀에서 반드시 contract check한다.

---

# 12. Checkpoint 규칙

현재 R3D 기본:

1. Validation Macro AUROC 최대
2. 사실상 동률이면 Macro AUPRC 최대

checkpoint 저장 시 metadata에 포함:

- Experiment ID
- epoch
- model config
- hyperparameters
- Fold
- train/val study count
- train/val manifest SHA
- segmentation config/version
- best Macro AUROC
- best Macro AUPRC
- seed

학습 종료 후 checkpoint SHA256을 출력한다.

---

# 13. 평가 출력 규칙

Classification notebook은 최소 아래를 출력한다.

- Train loss by epoch
- Validation loss
- Macro AUROC
- Macro AUPRC
- target별 AUROC
- target별 AUPRC
- Sensitivity
- Specificity
- F1
- Balanced Accuracy
- best epoch
- runtime
- GPU memory summary

3-Fold 완료 후 별도 OOF evaluation에서:

- 58 study pooled OOF Macro AUROC
- pooled OOF Macro AUPRC
- target metrics
- Fold metrics
- prediction CSV

Segmentation notebook은 최소:

- Dice
- IoU
- class/structure별 metric
- macro metric
- sample visualization 가능하면 포함

---

# 14. Output 규칙

모든 산출물은 기본적으로:

~~~text
/kaggle/working/
~~~

에 저장한다.

예:

~~~text
/kaggle/working/r3d03a_r34t_fold0_best.pt
/kaggle/working/r3d03a_r34t_fold0_epoch_log.csv
/kaggle/working/r3d03a_r34t_fold0_val_predictions.csv
/kaggle/working/r3d03a_r34t_fold0_manifest.json
~~~

마지막 셀에서:

- expected output 전부 존재하는지 검사
- file size
- SHA256
- key contract
- success/fail

을 출력한다.

submission notebook은 추가로:

- submission.csv 존재
- row count
- column count
- StudyInstanceUID uniqueness
- required 12 target columns
- NaN 없음
- probability finite
- probability range
- SHA256

을 검증한다.

---

# 15. 예상 실행 시간

Notebook 전달 전에 예상 소요 시간을 반드시 적는다.

예:

~~~text
Expected Run All:
- preprocessing/cache: 15~25 min
- training: 40~55 min
- validation/output: 5 min
- total: 60~85 min
~~~

근거가 약하면 범위로 적는다.
실제 실행 후에는 measured runtime으로 기록을 교체한다.

---

# 16. Notebook 전달 전 Agent 자체 검증

사용자에게 파일을 주기 전에 반드시 확인:

- ipynb JSON / nbformat 정상
- 모든 Python cell syntax compile 가능
- undefined variable 없음
- Required Input과 코드 path 일치
- output path 일치
- experiment ID 일치
- Save Version 60자 이내
- Accelerator 설명과 코드가 일치
- Internet On/Off 요구와 코드가 일치
- global /kaggle/input recursive search 없음
- Run All 순서 의존성 문제 없음

Notebook 파일을 생성했다면 실제 생성된 파일 경로를 확인한 뒤 사용자에게 전달한다.

---

# 17. 사용자에게 Notebook을 전달할 때 답변 형식

길게 설명하지 않는다.

최소 아래 형식으로 전달한다.

~~~text
Experiment:
R3D-03A — 3D ResNet34 + Transformer Fold0

Kaggle Settings:
- Accelerator: T4 x2
- Internet: Off
- Save Version: R3D-03A R34T Fold0 Baseline
- Expected Run All: 약 XX~YY분

Inputs:
[R3D-03A / R34T Fold0]
→ RSNA Knee Abnormality Detection
→ ...

[R3D-03A / R34T Fold0]
→ ...
→ ...

Outputs:
- ...
- ...

Notebook:
[Download ...]
~~~

필요한 실행 후 공유 항목도 마지막에 짧게 적는다.

예:

~~~text
실행 후 공유:
- 마지막 summary cell
- epoch log
- best checkpoint 정보
- 오류가 있으면 전체 traceback
~~~

---

# 18. 실험 결과를 받은 뒤 Agent 규칙

사용자가 Kaggle 실행 로그 / 결과를 공유하면:

1. 실제 로그를 먼저 읽는다.
2. 추정이나 기억보다 실행 결과를 우선한다.
3. success contract 확인
4. best epoch / metric 추출
5. 이전 실험과 동일 조건인지 확인
6. 바뀐 변수만 기준으로 해석
7. 다음 실험 필요 여부 결정
8. 완료된 결과를 Git Experiment History에 기록
9. Plan 문서의 진행 상태 업데이트

Public LB를 받으면:

- 정확한 score
- submission 구조
- project best 대비 delta
- 내부 Val과 LB gap
- 해석
을 기록한다.

---

# 19. 현재 R3D 계보의 특별 규칙

- DINOv2는 현재 R3D 비교 후보에서 제외
- Backbone은 3D ResNet34 / 50 / 101
- Full Fine-tuning
- LoRA 사용 안 함
- 모든 backbone candidate에 Transformer 포함
- ROI는 BBox가 아니라 Anatomical Segmentation Mask
- Gold58 3-Fold pooled OOF
- initial backbone selection은 fold별 pseudo 약 1,000
- 같은 Fold 안에서 세 backbone은 동일 pseudo UID manifest 사용
- pseudo가 Gold-derived이면 반드시 Fold-aware leakage-safe version 사용
- primary = pooled Macro AUROC
- secondary = pooled Macro AUPRC


---

# 20. A/B Account Lane Naming Rule

사용자는 Kaggle 계정 A / B를 동시에 사용할 수 있으므로,
병렬 실행 Notebook은 **실행 계정이 파일명과 화면에서 즉시 구분되어야 한다.**

필수:

- Notebook filename 맨 앞에 `A_` 또는 `B_`
- 첫 Markdown title에 `[Account A]` 또는 `[Account B]`
- 추천 Save Version 맨 앞에 `A ` 또는 `B `
- 사용자 전달 답변에서 반드시 `계정 A` / `계정 B`를 분리해서 표시
- 같은 wave에서 A/B가 바뀌지 않도록 experiment-to-account mapping을 명시
- Experiment ID 자체는 R3D-xx를 유지하고 Account tag는 실행 lane tag로 별도 표기

예:

~~~text
A_R3D-06I_P3_Fold12_Confirmation_DualT4.ipynb
B_R3D-06H_Sag1_TargetPolicy_Confirmation_Fold0_DualT4.ipynb

A R3D-06I P3 F12 Confirm
B R3D-06H Sag1 Target F0
~~~

병렬 실험이 아닌 단독 실행 Notebook에는 A/B tag를 강제하지 않는다.
