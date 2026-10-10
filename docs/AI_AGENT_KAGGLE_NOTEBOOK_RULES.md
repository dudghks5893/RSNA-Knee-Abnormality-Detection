# AI Agent Rules — Kaggle Notebook Delivery

최종 업데이트: **2026-10-10**

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

2026-10-08 기준 현재 R3D Main은 아래로 고정한다.

- Backbone: **MedicalNet R34**
- Full Fine-tuning
- pure FP32
- BatchNorm running stats frozen
- Series policy: **ALL**
- physical center crop: **130 mm**
- tensor: **interpolated D24×96×96**
- representation: **GLOB**
- anatomy mask: **OFF**
- aggregator: **Transformer + shared CLS**
- output: 12 independent sigmoid heads
- backbone LR: **1e-5**
- new-layer LR: **5e-5**
- WD: **1e-4**
- Gold58 deterministic 3-Fold 유지
- Fold-specific Pseudo1000 사용

현재 closed:

- R50 / R101
- coarse spatial token
- current anatomy mask fusion
- lower LR / frozen backbone
- P2/P3 series cap search
- Crop150
- simple R128 / D32
- REAL24 / REAL32
- Full/Crop Dual-FOV / Mixed3

새 evidence가 없으면 위 항목을 임의로 재오픈하지 않는다.

DINOv2 / Exp57은 R3D 내부 backbone 후보가 아니라
**외부 strong baseline / final ensemble source**로 취급한다.

---

# 20. Account tag와 Variant 이름 규칙

매우 중요:

**파일명 맨 앞의 `A_` / `B_`는 Kaggle 실행 계정 tag로 예약한다.**

예:

~~~text
A_R3D-11_...
B_R3D-11_...
~~~

의미:

- A_ = Kaggle Account A에서 실행
- B_ = Kaggle Account B에서 실행

Experiment suffix의 A/B와 혼동하지 않는다.

## 한 Account의 T4×2에서 두 lane을 돌릴 때

가능하면 Variant를 A/B라고 부르지 않고
설명형 이름을 사용한다.

권장:

~~~text
GPU0 → ALWAYS_DUAL
GPU1 → MIXED_3MODE
~~~

비권장:

~~~text
GPU0 → Variant A
GPU1 → Variant B
~~~

이유:
Account A/B와 화면에서 혼동되기 쉽다.

### Historical exception

`R3D-10AB`는 이미 완료된 historical experiment ID다.

- 실행 계정: **Account A**
- GPU0: ALWAYS_DUAL
- GPU1: MIXED_3MODE

여기서 `10AB`의 AB는 두 비교 variant를 뜻했으며
Account B 실행을 뜻하지 않는다.

이 naming pattern은 앞으로 반복하지 않는다.

## 한 계정 T4×2 vs 두 계정 A/B

입력 Dataset을 공유해야 하고
두 작업이 한 T4×2 session에서 독립적으로 실행 가능하면
굳이 두 Kaggle 계정으로 분리하지 않아도 된다.

한 session:

~~~text
GPU0 → lane 1
GPU1 → lane 2
~~~

가 더 단순하면 이를 우선할 수 있다.

두 계정을 분리하는 경우는:

- 서로 다른 Notebook을 완전히 독립 실행하는 것이 더 편함
- Dataset 공유가 이미 완료됨
- runtime/session limit 분리가 유리함
- 한 T4×2 notebook에서 orchestration complexity가 지나치게 큼

일 때 사용한다.

---

# 21. CPU preprocessing / GPU training 분리 규칙

새 MRI image/cache 생성은 **CPU-only preprocessing Notebook**에서 수행한다.

예:

- raw DICOM decode
- physical crop
- resize
- actual-slice selection
- persistent volume cache
- metadata manifest
- cache consolidation

설정:

~~~text
Accelerator: None / CPU
~~~

그 결과를 persisted Kaggle Input으로 만든 뒤
GPU Notebook은 training-only로 사용한다.

GPU Notebook 금지:

- raw DICOM 대규모 decode
- 수십 분짜리 cache generation
- CPU preprocessing 동안 T4 idle reservation

예외:
아주 작은 sanity-check decode가 model 실행 contract 확인에 꼭 필요한 경우만 허용하고,
대규모 cache generation으로 확장하지 않는다.

---

# 22. Kaggle Dataset Version / Mount 규칙

Kaggle에서 같은 Dataset의 서로 다른 Version을
동시에 독립 Input처럼 사용할 수 있다고 가정하지 않는다.

특히 base cache와 delta cache가
같은 Dataset의 다른 Version에만 존재하도록 설계하지 않는다.

권장:

1. 필요한 cache를 **한 canonical Dataset / active Version**에 합침
2. 또는 서로 다른 Dataset slug로 분리
3. 최종 Notebook에서는 exact mounted path를 사용

Dataset 재등록 후 실제 Kaggle mount path가 바뀌면
사용자가 공유한 **실제 path를 기준**으로 Notebook을 수정한다.

Dataset 이름을 기억만으로 추정하지 않는다.

---

# 23. Mount 실패와 Python 실행 실패 구분

아래 로그:

~~~text
Output 0 B
ERRORED_MOUNTING_DATASET
retry budget exhausted
dataset loading failed
~~~

이면 Notebook Python 코드가 실행되기 전이다.

판정:

- Python bug 아님
- model training 시작 안 됨
- GPU experiment result 없음

조치:

1. 어떤 Dataset이 mount 실패했는지 확인
2. 같은 Dataset 재시도만 반복하지 않음
3. 필요하면 new slug / saved Notebook Output / consolidated Dataset으로 우회
4. Notebook 코드를 무작정 수정하지 않음

반대로 traceback에:

~~~text
Exception encountered at "In [x]"
~~~

가 있고 Python line이 나오면
실제 Notebook code failure로 분석한다.

---

# 24. 실패 후 artifact recovery 우선 규칙

Notebook이 마지막 aggregation / SHA check / zip 단계에서 실패했다고 해서
곧바로 GPU training을 다시 하지 않는다.

반드시 먼저 확인:

- epochs가 이미 완료됐는가
- best checkpoint가 존재하는가
- prediction CSV가 존재하는가
- target metric CSV가 존재하는가
- history/log가 존재하는가
- 실패가 post-training contract bug인가

저장된 artifact로 결과 복구 가능하면
**로컬/CPU posthoc recovery**를 우선한다.

Fresh Save & Run All 재학습은
필수 artifact가 부족하거나 결과 신뢰성을 회복할 수 없을 때만 한다.

사용자는 Save & Run All workflow를 사용한다.
같은 세션에서 "그 셀만 다시 실행"을 기본 해결책으로 제안하지 않는다.

---

# 25. Raw metadata와 derived policy column 규칙

cache의 metadata 파일에 downstream policy column이
항상 저장되어 있다고 가정하지 않는다.

실제 사례:

R3D-06A raw `series_index.csv`에는:

- StudyInstanceUID
- SeriesInstanceUID
- Anatomical_Plane
- Fluid_Sensitive
- Fat_Suppression
- volume_file
- row_in_shard

등 primitive metadata가 있지만,
`plane_rank` / `selection_order`는 downstream ALL policy에서 생성했다.

Canonical ALL policy:

~~~text
plane order:
Sagittal → Coronal → Axial

rank =
4 × Fluid_Sensitive × Fat_Suppression
+ 2 × Fluid_Sensitive
+ Fat_Suppression

sort:
StudyInstanceUID
→ plane order
→ rank descending
→ SeriesInstanceUID ascending

plane_rank:
Study + plane 내 cumcount + 1

selection_order:
Study 내 cumcount
~~~

새 Notebook이 Full cache와 derived cache를 pair할 때는
primitive metadata에서 동일 policy를 재구성한 뒤 parity를 검사한다.

없는 derived column을 곧바로 assert해서
실험을 중단시키지 않는다.

단,
과거 실험의 실제 policy 공식을 확인할 수 없으면
임의로 재구성하지 말고 먼저 기록/코드를 확인한다.

---

# 26. T4×2 independent subprocess 규칙

한 Notebook에서 두 독립 training lane을 실행할 때:

~~~text
physical GPU0 → subprocess 1
physical GPU1 → subprocess 2
~~~

각 subprocess environment:

~~~text
CUDA_VISIBLE_DEVICES=0
CUDA_VISIBLE_DEVICES=1
~~~

처럼 물리 GPU를 분리한다.

각 worker 내부에서는 자기에게 보이는 GPU가 `cuda:0`이어도 정상이다.

필수:

- `torch.cuda.device_count() >= 2` preflight
- lane별 log 분리
- lane별 returncode 확인
- 한 lane 실패 시 다른 lane artifact 보존
- main aggregation은 두 returncode / summary를 확인한 뒤 실행

---

# 27. 문서 업데이트 / 새 채팅 인수인계 규칙

실험이 완료되면 최소 다음을 갱신한다.

1. `EXPERIMENT_HISTORY.md`
   - 완료 결과
   - artifact SHA
   - 실제 판정
2. `CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md`
   - 현재 Main
   - closed/open 축
   - 다음 액션
3. `3D_RESNET_EXPERIMENT_PLAN.md`
   - NEXT / dependency / gate
4. 필요 시 `AI_AGENT_KAGGLE_NOTEBOOK_RULES.md`
   - 새로 발견된 운영 실수 방지 규칙
5. `CURRENT_HANDOFF.md`
   - 새 채팅 cold-start 기준

오래된 "현재 다음", "NEXT", "진행 중"이
새 상태와 충돌하게 방치하지 않는다.

README에 current status가 있으면
그 상단 status도 같이 최신화한다.


---

# 28. RMIL-02/03 native-Slice CPU→GPU QA extension (2026-10-10)

- RMIL-01 is completed; do not rerun to fill or guess missing results. RMIL-02A `CPU` metadata-only preflight is a separately numbered **planned** step; RMIL-02B image-cache construction must not silently masquerade as completed.
- K4 historical cache with Series×4 windows is **not a full-native-Slice cache**. Existing resized 3D D24×96 volumes and DINO feature embeddings are not reconstructible 224px source pixels. The new cached pixel source must be independently identified and verified.
- Exact Kaggle display names and `train_series.csv` and `train_series/<Study>/<Series>/*.dcm` under named competition source must be stated. Check known candidate competition roots with `Path.exists()` only. Do not invent a source Dataset slug, do not search entire Kaggle Input recursively.
- CPU preflight: physically sort original DICOM geometry; verify Slice orientation, duplicate position, Series UID/Study UID mapping, valid non-padding window counts; distinguish **expected** from **verified** mount and stored image bytes.
- **Hard K4 parity gate:** retain original selected Slice center-index mapping, physical cropping, clipping/normalization ordering and 224px resizing; require old cache-builder code/contract for byte-level comparison. Rebuilding K4 with a different normalization is not a fair K effect.
- For K16/24/32 store actual unique usable valid centers and mask; do not mark repeated / padded positions as native Window evidence. Track short Series, plane/position coverage and source provenance.
- For controlled trials, separate **MEAN K variation** from **MEAN vs shared Attention at the same K**; only after that, separate shared Attention vs disease-specific Window Attention vs disease-specific Window+Series Attention. Use common train300/Gold58 source manifests (Gold development only), pretraining SHA, seed/budget, and target metrics.
- CPU only for DICOM extraction/cache building; GPU T4×2 only for model training on released, auditable persisted cache. If preprocessing/runtime data are not verifiable, fail-fast or explicitly mark `BLOCKED`; do not claim completion.
- Approved detailed procedure: [RMIL-02/03 native Window protocol](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md).

---

# 29. Kaggle saved Output 20GB limit and RMIL cache safety (2026-10-10)

- Kaggle docs: `/kaggle/working` **up to 20GB preserved output**. Project rule: do not let the **sum of all files in `/kaggle/working` exceed 14.0GB decimal**. The remaining ~6GB is safety margin; it is NOT permitted unused scratch from which to save additional multi-GB data.
- Count existing output before preprocessing/training; check physical free space independently with at least 2GB reserve. Use the minimum of both budgets. File system `disk_usage.free` alone is insufficient to enforce Kaggle output quota.
- Estimate actual Slice count × 224×224 uint8 × 1 channel, add +30% overhead and 300MB for staging/metadata. Do not rely on compression to fit. If estimate exceeds capacity, fail early and split output across separately versioned notebook outputs / datasets (respecting Kaggle dataset version/mount rules) or reduce representation.
- Cache in 256–512MB independent validated shards; **recheck available output bytes immediately before every shard**; write temp, SHA-check, atomically rename. Preserve completed shards and a useful status manifest if write must stop.
- Do not create K16/K24/K32 duplicate pixel caches or copy a large cache into a results ZIP in the same `/kaggle/working`. Save metadata-only review ZIP; persist canonical compressed or uncompressed shards directly with manifest/SHA. `/kaggle/tmp` is ephemeral; output intended for reuse must be under persistent output or a registered input Dataset.
- RMIL-02A records `disk_budget.json` and **does not construct new 224px image pixels**. Prepared disk-safe `RMIL-02A_Native_Slice_Preflight_DiskSafe_CPU.ipynb`, SHA256 `1516660b1d413aa384a193122593aad21d057832c4405a64be9d9e9e973204dd`; Kaggle runtime verification pending.
- Detailed [RMIL-02/03 disk/output policy](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md).

---

# 30. RMIL-02A verified geometry / legacy K4 pixel parity blocker (2026-10-10)

- RMIL-02A actually completed CPU metadata preflight, verified 358 Studies / 2006 Series / 66430 DICOM Slices, zero geometry errors; [full audit](RMIL-02A_COMPLETED_METADATA_AUDIT_2026-10-10.md).
- Old K4 `series_centers` index formula was independently reproduced across all 2006: `np.rint(np.linspace(.1*(N-1),.9*(N-1),4)).astype(int)`; **do not equate numeric centers with pixel and orientation parity**. New RMIL-02A `uniform_spaced_valid_centers_v1` is a separate policy and cannot substitute for original K4 without an explicit control.
- RMIL-02B0 CPU **K4 pixel parity diagnostic Notebook** prepared, not executed: `RMIL-02B0_K4_Pixel_Parity_Probe_CPU.ipynb`, SHA256 `0bf941097a3bdd5db04b4093f6dfe7e853127b5704011db5cbe98251a209804c`. It only analyzes plausible interpolation/crop/normalization combinations on a few Series; even full matching on this set does NOT release the entire 358-study cache.
- The preferred next source is the original R2D-CACHE-01 cache-builder Python/Notebook, if obtainable; require comprehensive K4 byte parity to the SHA-pinned `R2D_SHARED224_V1`, not just sample MAE. If missing, keep the pixel pipeline blocked/diagnostic; never invent a PASS.
- RMIL-02B new pixel cache must be built from 358-study **original DICOM**, without reusing unrelated old DINO/EXP image caches (user preference). Actual output feasibility: 3.104277GiB raw single-channel data plus overhead estimated peak 4.633149184GB decimal < 14GB safety cap, but recompute per shard before write.
- At controlled GPU stage compare K16 vs K24 **Mean** first (high K full coverage 95.91% vs 75.42%), then same-K shared Window ATTENTION. K32 optional conditional; K32 full coverage only 25.72%, not automatic. RMIL-03 target-specific later.

---

# 31. RMIL-02 K size comparisons require nested center policy

- RMIL-02A `native_k_candidates.jsonl` generated K4/16/24/32 by *independent* uniform linspace; **these lists are nonnested** and therefore not a clean count-only comparison.
- Before GPU experiments, emit a versioned nested policy `NESTED_LEGACY_ANCHORED_FARTHEST_POINT_V2`: four original K4 indices (subject to physical/pixel parity gate) then successively append valid center furthest from existing centers, lowest-index tie break, and take K prefixes. Freeze SHA, unique center count, Study/Series UIDs, no synthetic padding. Compare K16 Mean vs K24 Mean on exactly nested indices, then same-K Mean vs Attention.
- If old K4 physical orientation/pixel equality cannot be proven, explicitly STOP rather than claiming a controlled K effect.

---

# 32. RMIL-02B0 evidence: new V2 input / new K4 rebaseline supersedes old-parity gate (2026-10-10)

- Completed RMIL-02B0 K4 pixel parity diagnostic: actual uploaded ZIP SHA256 `3f7ee4b7a12db3b0297ed3d11eebce31133d4bc87adeb08687df4ece33c06a27`; CRC plus 5 SHA entries PASS, but **0/144 trial candidates** matched all tested original bytes. Never claim original RMIL-01 pixel parity. [Full audit](RMIL-02B0_COMPLETED_PARITY_AUDIT_2026-10-10.md).
- To avoid indefinitely blocking the K ablation on missing original preprocessing code, an **explicit, alternative experimental lane** is authorized: a NEW reproducibly defined 224px native Single-Slice Series V2 CPU cache, from original DICOM for 358 frozen subjects; train a **NEW K4 baseline** on that same V2 cache, then K16 and K24 under exactly the same V2 image preprocessing, model/hyperparameter/seed split, before same-K Mean-vs-Attention. This V2 rebaseline is not the historical RMIL-01 and must not reuse RMIL-01 K4 AUROC for causal delta.
- **V2 branch overrides the old obligatory pixel-perfect comparison to RMIL-01** for within-V2 count/attention tests ONLY. Do not say it reproduces the historical K4. Historical K4 parity requirement still applies if asserting numerical reproducibility of RMIL-01 specifically.
- Prepared CPU notebook `RMIL-02B_Native224_SharedCache_CPU.ipynb`, SHA256 `097c72a070114caa53603180f9813ec16c3edf15ab7dc1ff84c30a279cbc080b`, syntactically validated and nested K selector tested against Slice-length N=11..320; **NOT YET run on Kaggle**. Accelerator None, Internet OFF, Save & Run All; use original competition + pinned K4 study manifest Input, no old DINO cache reuse; preserve all HDF5 shards, manifest and metadata-only review ZIP. Project saved output cap 14.0GB, ≥2GB physical reserve, per-shard SHA and atomic replacement.
- Require user-supplied Kaggle full-run log and `RMIL-02B_results_for_review.zip` artifact SHA validation before treating V2 cache as completed. Do not train GPU until cache dataset is persisted and manifest confirmed.

---

# 32. Crop physical FOV < 130mm — RMIL-02B V3 requirement

- Actual V2 `RMIL-02B_Native224_SharedCache_CPU.ipynb` Kaggle run FAILED on centered crop assertion `hh<=h and ww<=w` after 358/2006/66430 source audit passed. No verified completed HDF5 shard shown. **V2 must not be marked PASS**. [Audit / V3 handoff](RMIL-02B_V2_FAILED_CROP130_V3_FOV_SAFE_2026-10-10.md).
- V3 `RMIL-02B_V3_Native224_FOVSafe_SharedCache_CPU.ipynb` SHA256 `0089f337ff1a8bffb8a58169f6915b7b706a45ebd4875fd48a1ee68689cf6ebf`. Run All on Kaggle still pending. Keep **physical 130mm crop FOV**; source-image-absent margins get constant normalized -5 padding BEFORE resize, not reflected anatomy; statistics computed from real pixels, not padding. Every Series needs `fov_crop_audit.csv` and pad fraction; warn >=20%.
- New V3 pixel SHA/preprocessing lineage means new on-cache K4 comparator mandatory. Confirm all Shard and metadata manifests before GPU training. Existing V2 partial files are invalid.
