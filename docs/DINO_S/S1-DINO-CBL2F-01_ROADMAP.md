# DINO·S — S1FT02 → S7 → S8 누적 Roadmap

**2026-10-16 최신 확인**: S7 4,407 Studies/24,371 Series/770,336개 Full MRI Window 특징 추출 완료. S8A Mean **Public LB 0.918**, S8B 질환별 Window Attention **Public LB 0.923**(사용자 보고). 현재 프로젝트 최고 기록은 S8B.

**다음 후보(미실행)**: S8C 질환별 Window + Series Attention을 같은 S7/Strict-FT Fold별 특징으로 통제 비교. Stage1 DINO가 18 Window/Study로 Fine-tuning됐다는 점과 S7 전체 Window 특징 추출을 구분. 별도 18 vs 32 vs 64 Window Fine-tuning 실험은 S8C 효과 비교와 혼합하지 않는다. Kaggle T4x2/Internet OFF·GPU 예산 사전검증 및 Gold58 반복 DEV 주의.

### 이전 통합 Roadmap에서 이관한 S8·Stage1 계획 및 기록 (작성 당시 상태 주의)

## 2026-10-16 — S8 A/B LB 확정 기록과 S8C 다음 단계

- **최신 Public LB (사용자 보고)**: S8A Mean MIL **0.918**, S8B 질환별 Window Attention MIL **0.923**. 기존 B2 Full-MRI MIL **0.904**, Exp57 **0.918**. 현재 확인된 최고는 **S8B 0.923**.
- **완료:** S7 전체 4,407 Studies / 24,371 Series / 770,336개 유효 Window에 대한 Fold0·Fold1 특징 추출. S8A 및 S8B MIL 학습, 각 2-Fold V3_HIDDENFIX 공개 Kaggle 3-Study 실행 성공, 이후 사용자가 각각의 Public LB 보고.
- **중요 구조 차이:** Stage1 Strict-FT DINO 자체는 Study당 18 Window(Series 전체에 분산, 중심 20–80%)로 Fine-tuning. S7 전체 Window **특징 추출**과 S8 전체 특징 **MIL 학습**은 DINO를 전체 Slice로 재학습했다는 뜻이 아니다.
- **Gold58 주의:** S8A 개발 Macro 0.894883, S8B 0.877599로 Gold 순위와 Public LB 순위가 반대. Gold58는 기존 Stage1 Fold별 학습 및 MIL 모델 선택에 쓰인 반복 DEV 데이터이지 독립 최종 평가가 아니다.
- **다음 한 가지 실험(계획/NOT RUN):** `S8C` — S8B 질환별 Window Attention을 기준으로 **질환별 Series Attention**을 추가한 계층 구조를 같은 Fold별 인코더·S7 특징·학습/평가 계약에서 통제 비교. 가능하면 Mean residual 및 질환별 attention 분포를 기록하고, Public LB/Gold58/추론 자원 비용을 구분한다. S8A/B는 수정 없이 재현 가능한 기준선으로 보존.
- **추가 독립 실험 후보(아직 아님):** DINOv2 Stage1의 18-Window 입력 한계를 검증하기 위한 18 vs 32 vs 64-Window Fine-tuning; 이 변화는 MIL 구조 비교와 혼합하지 말 것.
- **기록 경로 고정:** 실제 수치는 `EXPERIMENT_HISTORY.md`, 현재 진척·다음 작업은 이 파일, 노트북·GPU·기록 규칙은 `AI_AGENT_KAGGLE_NOTEBOOK_RULES.md`만 업데이트. 실험별 새로운 `.md` 파일 작성 금지. 앞서 생성했던 S8 개별 결과 문서는 삭제함.

---

## 2026-10-13 — Kaggle Stage1 Notebook 1MB Source Limit 오류 및 LITE 수정본

**사용자 실행 오류**: `An error occurred while committing kernel: The kernel source must be less than 1 megabytes in size.` 실제 원본 4개 `S1_*T4x2.ipynb` 각 1,142,399~1,142,419 bytes, 코드 Cell5 압축+Base64 inline `COMMON_SERIES_ZLIB_B64` 1,031,218 chars 포함; **Kaggle 노트북 소스 한도 초과 원인 확정**. 이 오류는 GPU/DDP나 V4/Strict 라벨 문제가 아니며 원본 Kaggle Kernel이 저장/커밋되지 않음.

**수정 산출물**: `STAGE1_DINO_V4_STRICT_2FOLD_LITE_FIX.zip` SHA256 `4473c9775be8f9f59ad3016292471614607c0ac55df90cd37f52c0499bec95ac`. 소스 인라인 압축 CSV를 제거하고 기존 경량 공통 입력 `STAGE1_DINO_SHARED_INPUT_MANIFEST_V1.zip` (770,712 bytes)을 **별도 Kaggle Dataset**으로 Add Input하여 `/kaggle/input` 재귀 탐색, SHA 검사 후 read. ZIP 첨부 그대로나 `common_series_manifest.csv`+`sampler_reference.py` 풀어서 등록해도 자동 탐색 가능.
- A V4 Fold0 `S1_V4_DINOBase_F0_T4x2_LITE.ipynb` **37,582 bytes**, SHA `c9e9ebe8a9e8ff734b2456d25f4a5c8680c92cd168c44a4ce660729d63dfc710`
- A V4 Fold1 `S1_V4_DINOBase_F1_T4x2_LITE.ipynb` **37,582 bytes**, SHA `a3fe17c016508b70a3dcc073aa4dabd2e198b53da7c4b34a37ca607da2dc4190`
- B Strict Fold0 `S1_STRICT_DINOBase_F0_T4x2_LITE.ipynb` **37,602 bytes**, SHA `733dfdc6c12a4683d725db81b6180e531672f8558a7d168cc98dd72099c1d6e5`
- B Strict Fold1 `S1_STRICT_DINOBase_F1_T4x2_LITE.ipynb` **37,602 bytes**, SHA `77d6cc8077fbe367b1eaa5b795ca5fe4df3186860c99e9386c611c0bcc9636f9`
**검증**: 4×nbformat validate, 전체 Code AST, DDP embedded worker AST, notebook embed 데이터 잔존 검사, Zip-only 및 raw CSV+PY 가상 dataset path load+SHA 통과. 실제 Kaggle 원격 마운트/2×T4 GPU 본학습은 **아직 미실행**.

**실행**: A Fold0 LITE / B Fold0 LITE 각각 새 노트북 업로드, 기존 4종 Input 유지하면서 **5번째 공통 Manifest Dataset** 추가, Internet OFF T4×2, `RUN_MODE=PREFLIGHT` Save & Run All. `SHARED_KIT_PASS`, `INPUT_PREFLIGHT_PASS`, `GPU_PREFLIGHT_PASS`, `PREFLIGHT_COMPLETE` 로그 확인 후 `RUN_MODE=TRAIN` 변경해 별도로 본학습. Gold29 custom 2fold vs Strict release policy 차이 유지, 원본 라벨/이미지 전처리 변경 없음. 사용자에게 최종 실행 결과 수령 후 EXPERIMENT_HISTORY.md에 실제 관측 추가.

---

## 2026-10-12 — Stage1 DINOv2 Base V4/Strict 2-Fold Kaggle Notebook 4종 제작 (코드 생성/로컬 정적·합성 QA 통과, Kaggle GPU 미실행)

**새 사용자 입력**: Strict A Kaggle Dataset 경로 **`/kaggle/input/datasets/yhlucas/rsna-knee-version-a-strict-v1/STRICT_V1`**, 사용하는 CSV `STRICT_V1_TRAIN_LABELS_12_TARGETS.csv`. 이 경로를 B계정 Notebook에 고정 후보로 반영.

**실제 Notebook 4개, ZIP 한 개 생성:** `STAGE1_DINO_V4_STRICT_BASE_2FOLD_NOTEBOOKS.zip` (SHA256 `4456c684e441f78ea9a5b76b713c3e53de91d89490f88069cfc8a432c2ac9d1c`). 파일 목록 및 SHA:
- `S1_V4_DINOBase_F0_T4x2.ipynb` SHA `75c6363d36b203cd4d4b9efbb13992655c01cc9a58dd29bd25808443527326e1`
- `S1_V4_DINOBase_F1_T4x2.ipynb` SHA `9a9779bbc05d16fec2e2c2efc4d7646d1fb5e422c8628ec44453fc66590011dc`
- `S1_STRICT_DINOBase_F0_T4x2.ipynb` SHA `8c9e0d980ebd588ab1f8bbfba31dde6c36a22e360638c0f6a85463ecdc7f47e7`
- `S1_STRICT_DINOBase_F1_T4x2.ipynb` SHA `5ed9becdcfd71b4935ec63d954743fffae73c20c3f8bea387b99b659b071271d`.

**운영**: A계정 V4 F0 / B계정 Strict F0 동시, 이후 각각 F1. 한 Notebook은 T4×2 DDP로 **Fold 하나**의 DINOv2 Base 학습. Kaggle `Internet OFF`, 4개 Add Input: `rmil-04b-full-mri-native224-v3` 5pack/190 shards, account-specific V4 vs Strict label CSV, MetaResearch DINOv2 PyTorch Base 1, `rsna-knee-wide224-persistent-cache-v1` frozen Gold58 manifest. 경로는 현재 과거 Notebook 기록 기반; 실제 사용 계정 mount 존재 및 모델 패키지 버전은 **Kaggle에서 확인해야 함**.

**실행 2단계**: `RUN_MODE=PREFLIGHT` default로 2GPU 모델 Weight load, 실제 HDF5 Study read/Masked BCE Forward+Backward, VRAM peak Window Microbatch 후보 18/12/8/4 확인 → `GPU_PREFLIGHT_PASS` 또는 실패. 통과 후 사용자가 `RUN_MODE=TRAIN`으로 편집하여 Save & Run All. Max Epoch12, patience4, global study batch4(2 ranks x 1 Study with gradient accumulation2), Backbone layer bands LR1e-6/3e-6/1e-5, HeadLR2e-4, mixed precision + gradient checkpoint (no forced Window MB=1), same Seed20261013 and sampler, 18 central20-80% study-window/epoch; all series candidate each epoch. 기존 HDF5 픽셀은 재생성하지 않음. Stage1 학습/Pred Summary/Best·Last checkpoint 저장, `review.zip` includes logs/metadata only. 모델 직접 Kaggle LB 제출 Notebook 및 downstream full MRI Feature Cache Notebook은 **이번 패키지 범위 아님**.

**명시적 Protocol override:** Notebook은 사용자 이전 Gold29 train + Gold29 val 요구대로 `CUSTOM_GOLD_2FOLD_TRAIN`. 원본 Strict Release README는 Gold58 최적화/검증 **금지**하므로 이것은 원본 Strict 릴리스 규칙 준수 실험이 아니라 **별도 Gold 연구용 교차검증 실험**이다. 원본 라벨 ZIP/CSV 불변. Gold58 재사용 및 V4 routing provenance 때문에 independent holdout이라 주장하지 않음. 사용자에게 이 차이 명시할 것. Strict pseudo 4181 + Gold29 train =4210, V4 pseudo4349 + Gold29=4378 (각 Fold). Gold29 held out val. Both A/B same Fold split.

**로컬 QA**: 4× Notebook nbformat validate + Code cells/worker AST parse, Notebook 내 embedded Series CSV·sampler reference exact parity, 합성 HDF5 인접 three slice (epoch0/1), all-series 18 unique centers, mask=0 BCE gradient 0 PASS. NO Kaggle GPU/remote pretrained/190-HDF5 complete real execution. Unit-test result should not be presented as actual training success. Because real performance unknown, user should **run PRE-FLIGHT only first** and share GPU logs before full training.

---

## 2026-10-12 — Stage1 A=V4 / B=Strict: 공통 RMIL-04B 이미지 캐시 재사용 결정 (CPU 입력 manifest 준비 완료 / GPU 학습 미실행)

**결정**: A계정 = V4 라벨, B계정 = Strict V1 라벨. MRI 픽셀 전처리·Slice/Series UID·학습 샘플러 동일. **각 라벨별 영상 캐시 2벌 생성 금지**. 기존 RMIL-04B Full Native224 V3 HDF5 5 Packs / 190 Shards (4407 UID, 24371 Series, 819078 uint8 Slice, 원시 uint8 pixel bytes 41.1GB) 단일 공통 Input으로 사용. 기존 RMIL-04C00 Kaggle Audit `PASS_FULL_CACHE_AND_V4_SCHEMA_GATE`, 190 Shard SHA 검증 보고; B계정이 A소유 Kaggle Dataset에 실제 접근 가능한지는 별도 mount 체크 필요(미검증). 이 대화 컨테이너에는 원격 HDF5 본문 41GB 없음; **재처리/업로드를 이미 수행한 것으로 주장 금지**.

**정확한 원래 `RMIL-04B_PACK00_FullNative224_V3_Cache_CPU_KO.ipynb` 전처리 확인**:
1. Pixel array float32, RescaleSlope/Intercept, MONOCHROME1 `frame=-frame`, geometry physical slice ordering;
2. PixelSpacing 130mm centered FOV, 부족한 외부는 Z=-5 Padding;
3. Series 전체의 crop pixels에서 stride-sampled percentile p0.5/p99.5 Clip;
4. 해당 Series cropped pixels mean/std Z-score `clip(z,-5,5)`;
5. 부족한 FOV 영역 Constant -5 pad → `cv2.INTER_AREA` 224×224 resize;
6. `uint8 = rint(clip((z+5)*25.5,0,255))`, HDF5 저장 `[n_slices,224,224] uint8` 및 exact SHA/Series metadata;
7. DINO pipeline에서는 `[c-1,c,c+1]` 인접 물리 Slice를 3-channel로 stack, `uint8/255`, ImageNet mean/std (`0.485,.456,.406`/`0.229,.224,.225`)로 양쪽 모델 **완전히 동일**하게 변환. 새 N4/CLAHE/denoise/gamma·다른 FOV·Crop 적용 금지; train-only mild augmentation 추후 별도 동결. Gold/V4/Strict label 불문 pixels 동일.

**새로 생성한 경량 메타데이터 ZIP**: `STAGE1_DINO_SHARED_INPUT_MANIFEST_V1.zip` (현재 대화 배포, 770712 Bytes). 내부 `common_series_manifest.csv` 24371 rows(UID/SUID/n_slices/role/cache_part/center20_start/center80_end/central_valid_centers), `sampler_reference.py` (Seed20261013, all-series mandatory 1+ windows, Study 18 windows/epoch, central [20,80] physical center, 3-adjacent slice, label-independent deterministic), `config.json`, `strict_distribution.csv`, `README.txt`. CPU 검증: 4407 Studies × Epoch0/1, Study마다 18 unique (Series,center), 모든 해당 Study Series가 적어도 한 번 포함. 후보 483096 centers, Train 476882/Gold 6214; original full valid centers 770336. 샘플링 manifest **픽셀 HDF5 자체 아님**, 추가 이미지 전처리 불필요.

**학습 입력**:
- Account A: common 5pack HDF5 + common metadata ZIP + V4 broad label CSV + DINO official Base pretrained + official Gold split artifacts (Gold 사용 허용된 custom protocol 선택 시).
- Account B: **정확히 같은** 5pack HDF5/metadata + `RSNA_KNEE_VERSION_A_STRICT_V1_TRAIN_READY.zip`의 `STRICT_V1_TRAIN_LABELS_12_TARGETS.csv` + 같은 DINO official Base pretrained. Strict 4181 trainable (168 fully masked), 32163 valid masks. Missing = mask0, 절대 음성화 금지.
- V4 4349 vs Strict 4181 supervised train counts mismatch expected; primary label-recipe comparison retains actual coverage, controlled label-value-only comparison requires shared-UID + shared-target mask ablation. Same UID/Fold group and deterministic sampler regardless of labels.
- Strict ZIP README prohibits Gold58 optimisation/tuning/repeated evaluation. Gold29 train/29 val previous proposal is **별도 custom protocol** as already logged; this run cannot simultaneously claim Strict release README compliant. Held-out Gold29 cannot be used by Stage1/MIL/Final if custom 2Fold chosen. Gold-separated supervised and evaluation policies to be fixed before training; not yet final.
- DINO feature cache (float16 CLS+PatchMean) **라벨별/모델별 Stage1 가중치가 다르므로 추후 MIL 단계에서 서로 달라짐**: image pixel HDF5 cache only is shared, *model-generated feature HDF5 cache is NOT shared* across A/B. Each Fold task-tuned DINO has unique weight/hash and independent feature cache.
- GPU job before preflight includes account-specific Mount check 190 shard existence + data SHA or trusted RMIL-04C00 summary, one Study real input parity SHA(A/B), 2–3 Batch forward/backward VRAM and study batch vs window microbatch throughput. A/B T4×2, no arbitrary microbatch1.
- New experiments results only when actual GPU execution; only this current roadmap gets the plan. No new per-experiment md docs.

---

## 2026-10-12 — Label A Strict V1 ZIP 실물 검증 및 Stage1 DINO 학습 판단 (설계 / GPU 미실행)

**첨부 릴리스** `RSNA_KNEE_VERSION_A_STRICT_V1_TRAIN_READY.zip`: ZIP CRC 전체 PASS, 내부 17개 파일 SHA256 목록 항목 전부 PASS(0 mismatches), `README.md` 상태 **`TRAIN_READY_RESEARCH_ONLY`** (전문 MRI Ground Truth 아님). `STRICT_V1_FINAL_GATE_REPORT.json`의 patch replay 414 PASS 및 Gold58 UID 분리 주장 확인. 내부 Label CSV와 NPZ를 읽어 다음 수치 검증: 후보 Report 4349×12=52188, train-ready UID 4181, fully masked UID 168; 유효 target-mask 32163 (61.6291%), excluded 20025 (38.3709%), positives 4607, negatives 27556, Gold58 UID collision 0, NPZ masks sum 32163, masked zeros storage representation only. Target별 P/N/valid/excluded:
- ACL 339/3366/3705/644; MCL **37/3724/3761/588**; Medial Meniscus 1525/2446/3971/378; Lateral Meniscus 542/3266/3808/541; Medial OA 212/2398/2610/1739; Lateral OA **66/2490/2556/1793**; PF OA 204/2268/2472/1877; Effusion 542/2679/3221/1128; Synovitis **511/35/546/3803**; Baker's 100/1568/1668/2681; Contusion 364/2367/2731/1618; Fracture 165/949/1114/3235.
- State `Version B/Evidence Extended` **아직 릴리스 없음**; 제작 과정인 새 버전을 `A_STRICT_V1`과 섞지 않는다. `SCHEMA.json` 및 `FROZEN_LABEL_RECONSTRUCTION_POLICY_V2.md` 고정 규칙: `not_mentioned/insufficient/uncertain`는 `mask=0`이며 음성 취급 불허; numerical borderline Baker's 제외 유지.
- 12개 타깃 정답은 Study 수준이므로 Stage1 All-Series central preference (3-slice) Window마다 환자 라벨을 복제하여 BCE 하지 말 것. DINO features를 Study-level aggregation(head)해 **Study별 12 logits × per-target masked BCE**로 Task-tune. Loss `((BCE(logits,y)*mask*weights).sum()/weighted-mask.sum().clamp(min=1))` (weights 선택하면 같은 부분에 적용). 168개 fully masked는 supervised Stage1 loss에 포함하지 않음; optional self-supervised/unlabeled DINO 특징 추출 단계에는 사용 가능.
- **질문에 대한 결정:** 공식 DINOv2 self-supervised pretrained는 라벨이 없어도 *특징 추출* 가능. 그러나 Exp11B 계보의 무릎 질환 지도 Fine-tuning된 `stage1 task-tuned DINO`를 만들려면 V4/A-Strict/B-Extended 같은 **라벨이 필요**. A Strict은 4181 supervised study 기반의 독립 Stage1 학습 가능. Mask 38.37% 및 일부 클래스 부족(MCL positive37, Synovitis negative35, LateralOA positive66) 때문에 품질을 자동으로 더 높다고 주장 못함. class imbalance 및 target-wise performance watch.
- 연구 단계 비용 최소화: 먼저 **DINOv2-Base / Stage1 / V4와 A Strict 같은 Fold0/1, 공식 pretrained weight, 동일 224px Native V3/All-Series sampled windows/hyperparams/seed** 직접 학습하여 held-out Gold OOF + 필요시 standalone LB로 확인. A Strict을 fine-tune하면 라벨 이용; Version B 나오면 동일 조건을 후속 제3군으로 추가(Strict vs Extended). DINO Small은 Base에서 개선 신호 확인 이후 우선순위 결정. `Stage1 supervised` 성능으로 full-MRI MIL feature quality 보장 X; MIL 직접 모델 성능까지 확인해 성능 판정. All-Series 전체 Feature cache를 모든 후보에 미리 생성하지 않고 먼저 task-adapted encoder validation으로 선별 비용 관리.
- **릴리스 규칙 충돌 주의**: Strict V1 ZIP의 README Critical rule 4는 Gold58 전원을 최적화/하이퍼파라미터 튜닝/의사라벨 판정/반복 평가에서 제외하도록 명시한다. 기존 사용자가 계획한 `Gold29 train + Gold29 val` 2-Fold는 이 규칙을 그대로 따르는 실행이 아님. **Strict 패키지 원칙에 따른 기본 학습은 Pseudo4181만 train, Gold58 정답은 Strict 생성·학습에 미사용**. 사용자가 Gold29 supervised 2-Fold를 선택한다면 `CUSTOM_GOLD_2FOLD_TRAIN` 별도 학습 프로토콜로 명시하고 Strict 원본 라벨/README는 불변 보존; Holdout Gold29는 각 모델/MIL/Selector/final에 완전 제외한다. ZIP은 Gold58 UID만 포함, 실제 정답은 별도 공식 train.csv 필요. Gold 반복 개발 사용 이력 때문에 독립 최종 test 아님.
- 실험별 별도 md 생성하지 않음. A Strict source ZIP 바이트는 사용자 첨부물로 별도 보존. `EXPERIMENT_HISTORY.md`에는 실제 GPU 실행 수치가 생긴 뒤에만 성능 기입.

---

## 2026-10-12 — Stage1 후보: ALL Series + 20~80% 중앙 Slice 고빈도 순환 학습 (사용자 제안 반영 / 설계 후보 / GPU 미실행)

**핵심:** 고정 6 Wide9 Slot 대신 **Study 내 모든 Series**를 sampling inventory에 포함하고, 각 Series의 물리적 Slice 순서 기준 **중앙 20~80%의 3-slice Window 중심**을 높은 빈도로 **epoch-rotating coverage** 학습한다. 원본 각 .dcm는 2차원 Slice이며 기존 Native224 V3 cache는 이를 224×224로 전처리한 영상. "모든 Series"는 "모든 Slice"와 다름. **Host가 20~80%가 선명하다고 발언했다는 원문 근거는 2026-10-12 검색에서 확정되지 않음; 공식 주최자 지침으로 표기 금지.** 중앙부가 항상 pathology-optimal도 아니며 가장자리 위치의 임상 정보 보존 필요.

**실제 04A Series inventory 24,371 rows로 계산:** 4,407 Studies, 819,078 Slice (Train4349 808,550, Gold58 10,528). 인접 3-slice를 위해 valid center 1..n-2만 허용하면 총 770,336 full-coverage centers. 중앙부 범위를 `ceil(.2*(n-1))..floor(.8*(n-1))`로 잡으면 **483,096 center windows (mean Study 109.62, 전체 valid 중심의 62.7124%)**, Train4349만 476,882 / Gold58 6,214. 중앙부 중심에서 구성된 triplets는 ±1 때문에 일부 범위 밖 slice를 이웃 채널로 포함할 수도 있다. 중앙부 60%는 Slice 100%가 아니므로 "전부 학습" 주장 금지.

**효율 제안:** 모든 중앙 center를 모든 epoch DINO로 역전파하면 483,096 windows/epoch, 12 epochs≈5.80M windows 처리(수량 근사, 이미지 decoding/GPU wall-time 아님). Stage1은 환자당 **18~24 Window/epoch**를 예산 시작값으로 두고, 각 실제 Series에 적어도 1개 중앙 Window를 배정한 뒤 가변 Series count(3~14)에서 나머지를 coverage fair scheduling, FoldUID+Epoch deterministic 순환. 18 사용시 전체 4407에서 79,326 Window/epoch, 12 epochs 951,912 window presentations; 483,096 전부 매번 학습의 약 1/6 Window 제시량. 실제 Study 학습 4378명이므로 per-fold 학습 epoch는 78,804 (18/Study). **매 epoch 전체 Series 최소 1개 보장**; 같은 center를 자주 중복하지 않고 12 epoch 동안 중앙 후보의 넓은 범위를 순환. 3-slice window(c-1,c,c+1), 224px, DINO input/normalization과 Series metadata consistent. Center near 20/80 edges면 neighbor 20% 밖에서 약간 사용 가능.

**주의점:** Stage1 supervised label은 Study-level이고 Slice-level label이 아님. Positive Study에서 every Window를 positive로 학습하는 직접 Window BCE는 심각한 weak label noise. Stage1에서 light masked attention/mean+gated Study aggregator를 통해 **Study당 하나의 12-target loss**만 주고 Backbone을 공동 FT. Stage2 more expressive disease-specific hierarchical MIL을 full MRI cached DINO features로 학습. 20~80% strict center-only는 outside morphology and some findings 놓치므로 실행안은 중앙 샘플을 85~90%, 외곽 0~20/80~100의 일부(10~15%)는 optional strata/rotating sampling으로 보존하는 방안을 권고. 첫 고정 실험에서 두 band를 다 실험해 GPU 낭비하지 않고 데이터 coverage log를 수집하여 위험만 확인.

**전체 downstream:** Stage1만 central preference, **Stage2 full MRI Feature extraction / MIL / Top24 Selector는 전체 Slice 위치 0~100%를 후보로 유지**, 실제 DICOM edge windows replicate padding/valid centers 정책 명시. 전체 이미지 cache Native224 V3 이미 존재하므로 새 DICOM decode/crop cache 만들지 않음. V4/V6×Small/Base×2Fold 모두 fixed split, same sampler schedule, same preprocessing, Stage1 MRI DINO from same official pretrained init; V6 release 전 GPU 실험 금지. Age of Gold58 repeated development/label routing leakage warnings 유지. Single T4 batch VRAM vs T4×2 DDP preflight profile 후 GPU 배치 확정.

**선행 작업:** Current Full Native224 V3 cache from RMIL-04B/04A manifests, 24,371 Series inventory로 deterministic `center_band_index` manifest/SHA를 CPU에서 매우 저비용으로 생성. Main Gold split/fold-safe semantics, Stage1 sampler coverage quality and full Stage2 generalization 계획 정리. 새로운 Exp57 재현 학습 불필요.

---

## 2026-10-12 — Stage1 개선안: Wide9 고정 선택 대신 All-Series epoch-rotating 3-Slice Window (DESIGN DRAFT / GPU 미실행)

**사용자 핵심 우려:** Stage1 DINO를 기존 Exp11B `6 slots × 9 selected slices`로만 학습하면, 특징 추출 Encoder가 제외된 다른 Series/전후방 Slice 및 rare sequences에 충분히 task-adapt하지 못할 수 있음. 고정 Wide9 원안은 **권고 취소**. 원래 Exp11B 성공 기록을 무시하는 것이 아니라, 새 Stage1의 목적(전체 MRI 3-slice window Feature Encoder)을 우선한 설계 변경.

**Stage1 신규 권고 (추정 개선 효과, 아직 테스트 없음):**
- Meta 공식 Pretrained DINOv2 Small/Base에서 출발, **전체 Series를 학습 후보**로 두고 Epoch마다 Series당 다양한 물리적 Slice 중심을 재샘플. 윈도우는 실제 인접 `[center-1,center,center+1]`로 만들어 **Stage2 전체 MRI feature 추출/최종 Top24 2.5D와 입력 계약 일치**. 환자 라벨로 supervised 12-target classification, 작은 quality-aware/Series-aware aggregation Head를 Stage1 학습에만 사용; Head는 feature extraction 때 제거하고 Backbone `CLS + patch mean`만 저장.
- 단순 매 Epoch 전체 819,078개 window를 DINO로 **역전파하지 않음**. 제안 시작값: Study당 ~12–18개의 동적 Window, 실제 Series마다 우선 최소 하나를 배정하고 남는 수를 균등 배분. Study Series가 상한 초과 시 Fold·UID·Epoch 기반 회전 선택으로 시리즈 누락을 장기간 방지; **매 Epoch All Series 고정 처리라고 오표현하지 않음**. 위치는 예를 들어 0~100% 범위의 계층화 bins/10~90% 중심 및 양끝 보충으로 설계, epoch간 덜 본 위치 우대; 정해진 단일 20~80% 범위에 고정하지 않음. All-series 사용으로 Scan 품질과 label noise에 민감해질 수 있으니 balanced allocation + fixed deterministic validation, Series별 selected positions/coverage audit 권장.
- 동일 Study/Series/Window 입력 3장에 identical geometric transform 적용(동일 위치 정렬), mild intensity augmentation은 train only / 원본 contrast 보존. 모델 K24 자체는 **Study당 24개**로 Stage2 MIL selector가 선택할 것이며 Stage1의 `12-18`은 성능 실험의 K가 아니라 연산 예산임.

**전처리 제안 — 효율 우선 vs 원본 DICOM:**
- DICOM pixel은 `RescaleSlope+Intercept`, MONOCHROME1 inversion, ImageOrientationPatient+ImagePositionPatient 물리 정렬, 130mm FOV centered crop 및 boundary pad, **Series 단위** robust intensity normalize, resize224, uint8로 먼저 처리. Meta DINO input은 uint8→float [0,1] 및 ImageNet channel normalization. 원본 DICOM을 무전처리로 입력하지 않음.
- **현재 완성된 RMIL-04B Full Native224 V3 5Pack/190Shard**는 전체 `4,407 Studies/24,371 Series/819,078 Slices`를 이미 저장. 현재 V3 원본 실제 규칙은 Series-sampled p0.5/99.5 clipping → full-Series z-score clamp[-5,5] → pad -5 → cv2 INTER_AREA resize224 → uint8, 130mm FOV. 신규 Stage1/FullMRI feature/Top24/hidden inference를 이 **동일 V3 규칙으로 전부 새로 학습**하면 이전 Exp57의 1/99 uint8와 정확히 같을 필요 없음. **과거 Exp57의 가중치/Feature를 V3 pixel cache와 혼용하면 안 됨**. 기존 공개 Hidden code 제출에서 V3 DICOM assertions로 `Notebook Threw Exception` 보고되어, Hidden metadata/decoder fallback을 학습 전 preflight로 정의하고, 정상 DICOM에 대한 preprocessing parity와 decode coverage 검증 필수.
- Old Exp57에는 laterality canonicalization이 있었으나 현재 V3 preprocess 함수에는 해당 transformation이 명시되지 않은 것으로 파악. 새로운 일관된 Laterality 처리 추가는 별도 결정·검증 없는 자동 적용 금지. N4, CLAHE, denoise, gamma contrast 큰 보정은 근거 없는 기본 추가 금지.

**라벨/Fold**
- Strict 2Fold 29/29 Gold split; Stage1, MIL/Selector, final DINO의 각 Fold는 동일 held-out Gold29 supervision/pseudo-derived routing을 침범하면 안 됨. V4/V6 비교 시 Stage1 자체도 각각 동일 공개 pretrained 초기값/같은 Study sampling calendar에서 독립 학습 (V6 canonical release 전에는 GPU 학습 금지). Stage1 dynamics의 epoch sampling position은 seed+StudyUID+epoch 고정해 pair 비교 가능.
- Over-claimed OOF 방지: V4 pseudo 라벨 routing/history Gold 관련 누출 가능성 별도 표기; Gold58 개발 여러 번 사용. 이미 학습된 Exp57 Fold weights는 새 2Fold에 무조건 warmstart 금지.
- Input Study budget 12~18는 **초기 가설**이며 이전 Exp11B 18개의 3채널 group과 유사한 forward량을 의도하지만, 모델·학습 구조/Series Count 가변과 2GPU VRAM이 달라서 실제 T4×2 2–3-step FP32/mixed precision smoke 및 GPU throughput 측정 후 고정. Window Microbatch 1 금지, Batch>=124 과거 모델 경험만으로 새로운 K24 full FT VRAM 단정 금지.
- Stage1 평가: Macro AUROC/AUPRC 외 Gold heldout에서 인식하는 Series/position coverage, Target-wise score, MIL attention 분산, Feature statistics, class distribution 그리고 downstream MIL 최종 score를 함께 평가. Stage1 score가 높다고 최종 좋은 feature 보장 X.

**다음 사용자 합의 필요:** 현재 complete Full Native224 V3 캐시 기반으로 전 단계의 픽셀 전처리를 통일하고, Stage1 All-Series 3-slice Window epoch coverage 변경안을 채택하면 신규 Notebook을 제작한다. 학습 미실행, 초안 변경만 수행.

---

## 2026-10-12 — 설계 논의: 3단계 Task-tuned DINO Feature → MIL Selector+Direct → Top24 DINO (DRAFT, 미실행)

**사용자 질문/방향:** Exp57 계보를 참조한 개선형 모델에서 특징 추출 DINO를 official pretrained 그대로 쓸지 MRI 전체 학습할지 결정. 사용자 파이프라인은 정확히 `DINO feature encoder → hierarchical MIL (12-target window/series importance + direct prediction) → patient-level Top24 3-slice windows → final DINO warm-start predictor → final Top24 70% + MIL direct30%`. 1 Fold에서 2개 DINO checkpoint(초기 task-tuned feature encoder, Top24 end-to-end final) + 1개 MIL, 단 MIL은 Selector이면서 Direct30%의 예측기이므로 별도 세 번째 direct 모델은 불필요. Final DINO는 initial DINO와 MIL pretrained weights를 초기화로 활용하며 서로 독립적 모델 2개를 처음부터 2회 새로 학습하지 않음.

**권고:** 공식 Meta DINOv2 Base/Small (224; Base embedding768/CLS+patchmean1536, Small384/CLS+patchmean768)에서 시작해 **Fold-aware supervised task adaptation** 으로 knee MRI encoder 생성, 그 checkpoint에서 `eval()` freeze feature extraction across all Series/Slices → float16 persistent full MRI cache를 Fold별 1회 생성 → MIL 학습→Top24 cache → final DINO Full Fine-tune warmstart. Exp11B→Exp45 검증된 효율적 방식은 선별된 Wide9(6 slots × 9 raw slices)로 first-stage DINO를 task-tune하고, 이후 전체 3-neighbor-slice windows를 819078 candidate로 특징화하는 방식. 이것은 Exp11B 점수 재현 독립 실험이 아닌 **새 파이프라인에 반드시 필요한 stage1 학습**이다. Slice 선택 및 3채널 구성의 train/inference 분포 차이는 결과에 명시하며, 1차에는 새 변수를 더해 3-slice task-tuning으로 바꾸지 않는다. Full 819078 candidate backbone 훈련은 GPU 시간 낭비; **feature extraction만 전체**를 순회. 과거 Exp53 full cache fold당 200.44/241.14분 실제 기록을 비용 기준으로 참고(동일 실행 시간 보장 X).

**Gold과 라벨:** 2-Fold Gold58 29/29, 각 Fold stage1 DINO/MIL/final predictor **모두 동일 held-out Gold29를 감독 학습에서 제외**. Train pseudo report-only4349 + training-side Gold29(4,378 studies), validation Gold29. "Gold58 전원+4349 학습한 공통 MRI DINO 하나"는 Fold validation leakage. Original Exp57 old weights/Top24 Gold artifacts도 새 split held-out 라벨과 충돌 가능; 직접 OOF 주장 금지. 기존 V4 Gold-derived routing 감사할 때 원본 전체 rerun 필요 없으며, 독립 OOF를 보장할 수 없으면 dev comparison이라는 명칭 유지.

**V4/V6 실험 공정성 대 비용 (둘 다 명시)**:
- **Strict full pipeline paired comparison (final research claim):** 동일 Size×Fold의 Official DINO initial state에서 V4 TaskDINO vs V6 TaskDINO를 독립 supervised fine-tune; 각각의 full feature cache/MIL/Top24/final DINO를 별도로 학습. 2 labels × 2 sizes × 2 folds=8 independent full pipelines (not 8 single training jobs). 동일 optimizer LR/batch/seed/time/Fold, target mask/weights auditing. V6 canonical release 이전에는 V6 run 금지. **이것이 라벨이 encoder에도 미치는 효과까지 평가하는 공정한 실험**.
- **Budget-first conditional screening:** 먼저 Size×Fold 당 common MRI feature extractor 1개를 만든 뒤 DINO frozen cache를 **V4/V6 MIL+final comparator에 재사용**하여 feature cost 2배 절감. 그러나 common encoder를 V4 labels로 학습하면 V4에 편향된 Representation 고정이며 "V6 전체 pipeline이 V4보다 나쁜가"라는 주장 불가; "V4-encoder-fixed downstream label influence"만 평가. Label-neutral unlabeled adaptation은 GPU 비싸며 현 priority 아님. User label-comparison priority면 full pipeline fair path가 기준, 가벼운 screen은 명칭/범위를 엄격 표기.
- 권장 실행은 **Base 우선**: Base V4 Fold0/1 기반 Stage1 backbone → feature+MIL/Direct+Top24+Final까지 실질 성공과 비용 계측. V6 canon release 후 Base V6 identical training paired, Small은 이어서 같은 pipeline으로 2×2. Option to start Small as cheap engineering smoke without model scoring. T4×2 single full fine-tune 1 job/account (또는 1GPU×2 fold 분리는 실제 VRAM/throughput 측정 통과 시). Window microbatch1 금지, preflight forward/backward VRAM/throughput 필수.

**단계별 체크포인트 산출:** `stage1_dino_best.pt`, `full_features_fp16_shards+manifest_sha`, `mil_direct_selector_best.pt`, `top24_manifest+image_cache`, `final_top24_dino_best.pt`, `fold_val_predictions_branchwise`. MIL Direct30%는 동일 MIL 모델의 질환 직접 확률, 최종 Top24 70%는 최종 DINO 모델의 확률. 70:30은 Exp57 검증값으로 출발하지만 새 라벨/Backbone/2-Fold에서는 최종 blend 최적 보장 없음. 관련 실험 기록은 기존 README Exp11B, Exp45-57, Exp62-63을 따름. 신규 실험별 Markdown 금지.

---

## 2026-10-12 — UPDATED DRAFT: Exp57 통찰 기반 개선형 K24 DINO × Label V4/V6 × Small/Base × Gold 2-Fold

**사용자 최신 결정**: Exp57 체크포인트/전처리 재현 실험, 기존 Wide9 재기준선 학습, K32/고해상도 확대 선행 실험 **하지 않는다**. 과거 결과 자체를 연구 근거로 사용하고 **새로운 개선형 Top24 모델 하나**를 사전에 고정하여 라벨 2종 × 모델 크기 2종 × 2-Fold = 총 8개 학습으로 비교한다. 현재는 설계 초안/미실행. LABEL-V6는 `CANDIDATE_NOT_RELEASED`: canon SHA, UID × 12, mask, high-review 최종 승인 후에만 V6 GPU 학습.

### 누적 근거 (과거 결과)
- Exp11B Base vs Exp7A Small: Fold2 AUROC 0.942758 vs 0.900860 (Head width 등도 다르므로 Backbone 크기의 순수 효과라고 단정하지 않음). Exp12B Wide9→Slice15 hidden LB 0.822, Exp13A 224→336 LB 0.861; 이미지 수/해상도 무조건 늘리는 방법은 선행 금지.
- Exp47 patient-level attention Top24(3-slice window) / 평균 선택 Series 5.48, Exp48 Warm-start B3A LB 0.907 vs Exp49 Clean-start 0.903. Selector 자체 강한 신호, 기존 Top24 persisted raw cache와 ranking을 가능한 그대로 재사용하되 provenance/validation leakage 확인은 새 거대 재학습이 아닌 **메타데이터/manifest의 소규모 무결성 점검**으로 수행.
- Exp50 Full-MRI Direct 0.904, Exp51 70:30 0.913, Exp57 3fold 70:30 0.918. B3A 중요 영상과 전체 MRI Direct 상보성은 강한 관측; 추가 Full-MRI feature extraction/branch 재학습은 1차 8회 모델에 포함하지 않고, 승자에 대해 **저장된 Fold별 Direct predictions/weights 활용 가능 시** 후속 평가.
- Exp58 inference-only K32 Fold2 0.969147은 Exp62 K32-trained hidden LB 0.905로 재현되지 않음(다른 조건도 변화), Exp63 no-val all-data 0.897. K24 유지 및 validation-best 선택.

### 고정된 개선형 모델 1종 (안)
- 입력: **Study당 K24**, Exp57 질환별 Attention 기반 Top24 Ranking/Window(실제 인접 slice c-1,c,c+1), 224×224, 원래 130mm physical FOV/원래 normalization/laterality. **Series별 K24가 아님**. **현 Native224 V3는 원래 Exp57 픽셀 전처리와 다르므로 아무 검사 없이 혼용 금지**; 이전 Exp57 Top24 persisted cache를 가능하면 그대로 사용. 기존 Top24 캐시는 재생성보다 재사용 우선.
- DINOv2 Small/Base full fine-tune, CLS+patch mean global, per-target hierarchical Window/Series attention(Exp57 강점). **새 제안**: target-wise attention context와 Top24 전체 mean pooled context를 learnable bounded residual/gate로 결합하는 안정화 Head(기존 hierarchical B3A의 구체 코드 중복 여부 확인 후 설계). Metadata plane/fluid/slice-normalized position은 이미 존재하는 입력과 충돌 없이 적용. 12 Target single shared backbone, 매 실험 전체 구조 동일; Base feature width와 Small feature width 차이 외 가능한 같은 계약. 새 헤드 효과 자체를 독립 검증한 게 아니며 실제 향상 가설일 뿐. Full-MRI Direct는 나중에 blend.
- 이전 검증된 DINO Recipe **Exp7A/Exp11B**: Full FT, physical batch4/gradaccum1, Backbone early/mid/late LR 1e-6/3e-6/1e-5, Head 2e-4, MaxEpoch12, patience4, 5% warmup+linear decay; Base Head768, Small Head384. 위는 구 모델 recipe이며 K24 학습에서는 **물리 VRAM 사전 속도/peak 배치 벤치 필수**; 불가능한 숫자를 억지 적용하거나 WindowMicrobatch=1로 자동 축소하지 않음. V4/V6 동일 run budget/augmentation/optimizer/early stopping. 2-Fold의 Gold 29 train은 과거 Exp57 Gold47 train과 다르므로 절대성능 직접 대조 불가.
- **공통 Model Initialization**: 동일 Size/Fold V4-V6 Pair는 공식 공개 DINO pretrained와 동일한 초기 Head RNG/seed/state SHA에서 출발한다. 기존 Exp57 task-tuned checkpoint를 임의 Warm-start하면 변경된 Gold29 Val에 이미 정답이 포함될 수 있어 비교 결과 오염 가능; matched clean-start가 안전한 기본값. Old Fold checkpoint 재사용은 provenance 증명이 있을 때만 별도 검토.

### Gold split / 8 run
- Gold58 iterative multilabel stratification `29/29` 고정 Manifest, 타깃별 양·음 class 분포 실제 확인. Fold0 train=Pseudo4349+Gold[1]29, val=Gold[0]29; Fold1 train=Pseudo4349+Gold[0]29, val=Gold[1]29. V4/V6 모델/seed/validation IDs/metadata/Top24 입력/augmentation/pixel & checkpoint selection 모두 동일. Gold train에는 Gold truth만; pseudo routing이 Gold-derived일 수 있으므로 "clean independent OOF" 주장 금지.
- RUN ID: `EXP-L01/L02` Small+V4 Fold0/1, `EXP-L03/L04` Base+V4 Fold0/1, `EXP-L05/L06` Small+V6 Fold0/1, `EXP-L07/L08` Base+V6 Fold0/1.
- **주의: 이전 Exp57 Selector/Top24 Gold cached results에 새로운 Gold29 validation 라벨이 학습에 간접 반영됐을 가능성**. 모두 같은 고정 후보를 사용하더라도 누출이 무효화되지는 않음. 가능한 Fold-agnostic/pseudo-only selector 또는 실제 held-out에 대해 fold-safe old selector가 확인되면 그것을 사용; 재생성 비용이 크거나 불명확하면 기존 Cache는 **탐색적 개발 비교**에만 쓰고 'strict clean OOF'라 부르지 않는다. 이미 Gold58을 반복 탐색한 사실도 별도 표기. Full rerun 금지가 이 사실을 삭제하지 않음.
- V4 = 기존 routed soft + confidence (broad/strict 명시); V6 = canon label known-only + mask, not_mentioned/insufficient/uncertain mask0, numerical Baker cyst uncertain mask0. **라벨 값 + 가용 supervision coverage + soft/hard 차이의 결합 효과**임을 명시. 각 Target V4/V6 positive/negative/mask 차이 분석. 우수 Backbone에 대해 `V4 with V6 mask` 조건만 필요시 추가 2-Fold로 coverage-controlled 실험.
- Paired Gold58 OOF macro AUROC/AUPRC 및 disease-level, label count, paired delta/CI, GPU throughput/epoch/runtime. 작은 Gold58이 여러 번 사용돼 통계적 독립 최종 검증 아님; LB 최종 확인.

### 자원과 단계
1. **실행 전에 할 최소 점검(재현 학습 아님)**: 실제 Exp57 cached Top24 완결/경로, Gold UID–Fold/source provenance, V4/V6 범위·canonical 상태, 2-Fold label counts, 1–2 실제 batch forward/backward peak/step-time 예측 (Small/Base 각각). 기존 cache를 재생성하는 Exp57 별도 재현 실험은 하지 않음.
2. V4 4개 Round: Account A T4 GPU0/1 = Small F0/F1, Account B T4 GPU0/1=Base F0/F1 **독립 1GPU batch4가 가능할 때만**. 불가능하면 계정당 2GPU DDP로 Fold 순차 실행하고 Model/Grad semantics 유지. 실행 시 V6용 seed 초기상태 보존; V6 릴리스 뒤 같은 GPU 배치로 L05~L08 실행.
3. 성능 비교 후 우수 라벨/Backbone으로 Exp57 저장 Full-MRI Direct와 보완성 검토. 필요 시 그때만 Full-MRI branch 추가 학습; 새로운 Crop/CLAHE/N4/336/K32 실험은 그 이후에 한 변수씩.
4. Save&RunAll, `best.pt`, `last.pt`, `fold_manifest.csv`, label-mask audit, run config+SHA, metrics/OOF/report artifacts. 결과는 `EXPERIMENT_HISTORY.md`, 진행 상태는 이 문서에만 누적. 새 개별 md 없음.

---



---

### 기존 S1-DINO 전용 Roadmap

# S1-DINO-CBL2F-01 — 실험 계획·진행 현황 (갱신형 단일 문서)

> **Current as of 2026-10-13 (최신):** `A_B_STAGE1_TRAIN_SUCCESS / GOLD58_OOF_VERIFIED / A_B_PUBLIC_LB_USER_REPORTED_0.861_0.910 / STAGE2_PLANNING_PENDING`.
> 새 실험마다 계획서를 만들지 않고 **이 파일에서 현황·의존성·다음 한 가지 액션을 수정**한다. 상세 실측 결과는 누적 EXPERIMENT_LOG에서 관리한다. 아래 2026-10-13 중간 단계 기록의 과거형 '미실행/대기'는 당시 스냅샷이며, 현황은 상단 최신 상태와 단계별 표를 따른다.

### 2026-10-13 — PREFLIGHT 결함 보정 후 상태

- 실제 A 계정 `RUN_MODE=PREFLIGHT` 로그: 공통 Series 24,371, Pack 5개, Gold58 29/29 분할 SHA, STRICT 4,181 입력, Gold/타깃 leakage 검사와 Class Balancing 계산 **CPU 입력 Gate PASS**.
- V6은 CUDA 학습 시작 이전 `NameError: name 'worker_path' is not defined` 발생. **GPU Worker는 시작되지 않았으므로 GPU 처리량/학습 결과 없음.** B도 동일 코드 결함을 갖고 있어 V7로 동시 수정.
- 새 A/B `GOLDDEDICATED_V7_WORKERFIX` 로컬 AST·Worker 파일 생성·2 독립 프로세스 mock-launch PASS. **Kaggle GPU 아직 미실행**; S3 상태는 `PENDING_V7_KAGGLE_PREFLIGHT`.
- V7 Save 이름: A `S1-STRICT-F01-WFIXV7-PREFLIGHT` / B `S1-V4-F01-WFIXV7-PREFLIGHT`. 먼저 PREFLIGHT를 Save & Run All 후 GPU 2개 `GPU_PREFLIGHT_PASS` 확인.


### 2026-10-13 — B V4 V7 실제 GPU PREFLIGHT 통과 (A 별도 대기)

- **B**: `BOTH_GPU_PREFLIGHT_PASS` 실제 Kaggle T4×2; 두 독립 Fold 정상 종료, each train4,378+val29, Window microbatch18, peak GPU allocated2.41GiB, real one-study F+B 0.2391/0.2366초. 참조: `S1-DINO-CBL2F-01_EXPERIMENT_LOG.md` 최신 항목.
- **B RUN_MODE=TRAIN** 전환 가능(사전 GPU·입력 계약 Gate 통과). 단 실제 Optimizer step과 전체 Epoch 시간은 미측정이고 세션 간 Resume가 없어 운영상 중단 위험 존재. 12 Epoch 단순 GPU F+B 3.49/3.45h + 실제 추가 오버헤드. 첫 Epoch와 Kaggle 세션 잔여 시간을 보고 계속 여부 판단. 중간 재시작하면 이전 학습 자동 복원되지 않음.
- **A STRICT**: 이 기록 시점까지 V7 GPU PREFLIGHT 실제 완료 증거 없음. B 결과로 A의 성공을 대신 주장하지 않음.
- S3 상태 `B_GPU_PREFLIGHT_PASS / A_PENDING`, S4 상태 `B_ONE_STUDY_GPU_PROFILED / OPTIMIZER_AND_EPOCH_UNMEASURED`, S5 `NOT_RUN`.


### 2026-10-13 — A/B 양쪽 GPU PREFLIGHT PASS (TRAIN 대기)

- A STRICT: 실제 `BOTH_GPU_PREFLIGHT_PASS`, Fold0/1 microbatch18, GPU allocated peak2.41GiB, real Study F+B 0.2706/0.2394초, train4,210/fold, Gold29 validation/fold. Epoch1 target-mask 미리보기 희소 클래스 보존과 majority rotation PASS.
- B V4: 이미 `BOTH_GPU_PREFLIGHT_PASS`, 18 Window, peak2.41GiB, train4,378/fold, HDF5 Study F+B 0.2391/0.2366초.
- S3 상태 **`A_PASS / B_PASS`**. S5 TRAIN **`NOT_RUN`**. 두 계정의 V7 노트북 `RUN_MODE=TRAIN` 전환 가능하지만 **정상 전체 Epoch 완료/Optimizer step/세션 간 Resume는 아직 검증하지 않았음**.
- A Save Version: `S1-STRICT-F01-WFIXV7-TRAIN`. B Save Version: `S1-V4-F01-WFIXV7-TRAIN`. 둘 다 T4×2, Internet OFF, Save & Run All.
- 12 Epoch GPU F+B만 단순 투영 A Fold0 **3.80h**, Fold1 **3.36h**, B Fold0 **3.49h**, Fold1 **3.45h** (Fold 동시 병렬). I/O, optimizer, validation, checkpoint 제외, 실제 첫 Epoch 실측 필수.

### 2026-10-13 — Stage1 TRAIN 완료 / 다음: checkpoint 실물 등록

- A STRICT Fold0 best AUROC **0.838365** at epoch9/12, Fold1 **0.785654** at epoch7/11; pooled Gold58 Macro AUROC **0.811284**, AUPRC **0.729597**.
- B V4 Fold0 best **0.892702** at epoch8/12, Fold1 **0.868232** at epoch9/12; pooled Macro AUROC **0.871112**, AUPRC **0.800206**. **B 우선 Stage2 후보**, A 보존. 전체 Fold 별 소요 9.8~10.5h, 병렬 동시.
- ZIP CRC·58 UID, 29/29 Fold, Gold truth 동일성·AUROC/AUPRC 재계산 PASS. 실제 `best.pt`는 review ZIP에 포함되지 않음; SHA는 학습 summary 기록에서 확보. **모델 체크포인트 실물 등록 검증이 Stage2의 다음 차단 조건**.
- 상태 S3/S4/S5/S6 완료(개발 Gold58), S7 **`BLOCKED_ON_CHECKPOINT_REGISTRATION`**; 다음 작업: Kaggle A/B Output의 Fold0/1 `best.pt` 4개 보존·Add Input 등록·실제 SHA 검증.
- Gold58은 Epoch 선택에 사용되어 독립 테스트가 아니며, A/B는 라벨과 Loss 설계가 함께 달라지는 비통제 실험. Full-MRI 특징 추출/MIL의 성능과 Kaggle Public LB 점수는 아직 없음.

### 2026-10-13 — A/B Kaggle LB 2-Fold notebooks READY (NOT SUBMITTED)

- A STRICT and B V4 independent 2-Fold submissions: two prepared Kaggle Run All notebooks with exact original FeatureDINO and RMIL-04B native224 V3 DICOM preprocess. Final sigmoid probability equal averaging per account. No combined A+B inference.
- State: NOTEBOOKS_PREPARED_STATIC_QA_PASS / WEIGHTS_DATASETS_NOT_VERIFIED / KAGGLE_SUBMISSION_NOT_RUN / PUBLIC_LB_UNKNOWN.
- Proposed dataset A: yhlucas/rsna-knee-stage1-strict-f01-best-v1; B: yhlucas/rsna-knee-stage1-v4-f01-best-v1. Each root requires fold0_best.pt and fold1_best.pt, copied from Kaggle Train outputs. Registered mount and checkpoint actual SHA gate MUST pass.
- Then Add Input Competition test DICOM + checkpoint dataset + MetaResearch dinov2 base/1. T4x2 Internet OFF, Save & Run All. Official submission runtime <=9h; hidden decoding estimate highly uncertain. Examine neutral fallbacks and official LB.
- Next single action: preserve 4 checkpoint binaries and publish A/B checkpoint datasets; after SHA gate submit each 2-Fold notebook and add official LB scores to cumulative experiment log.

### 2026-10-13 — User-confirmed A/B exact checkpoint paths / V2 submission notebooks

- A owner `yhlucas`: `rsna-knee-stage1-strict-f01-best-v1/fold0/best.pt`, `fold1/best.pt`. B owner **`woniyeon`**: `rsna-knee-stage1-v4-f01-best-v1/fold0/best.pt`, `fold1/best.pt`.
- Revised both A/B Submission V2 notebooks, preserving Full DICOM V3 preprocessing, SHA guards, and Fold0+Fold1 probability 50:50 ensemble. Notebook SHA A `d272241254c8222004a74dbf34def355a6093cc7ef588d5852a22e965a89bdb0`; B `2c7323124de1b5fa3a2de2463618f19b6a342a9c7e060abe8a9a0dcf0ce2cb95`. Both static Python AST/nbformat PASS.
- Current gate: actual Kaggle Add Input mount, real checkpoint SHA and two-GPU inference **not yet executed/confirmed**, Official Public LB unknown. NEXT: A/B each Save & Run All with T4×2 Internet OFF; inspect `SUBMISSION_SUCCESS`, `submission_audit.json`, fallback count, submit each version to competition, then append scores to EXPERIMENT_LOG.

### 2026-10-13 — GPU 30h/week / Batch124+ optimization gate

- User-reported prior observation: Batch124+ simultaneous computation was possible with about 20GB VRAM headroom; per-GPU/total and Study/Window units not identified. Preserve evidence, and do not assume OOM merely because of a larger batch.
- GPU budget 30h/week: check account A/B remaining quota and actual T4x2 billing rate. Include GPU preflight, training, inference and retries in estimate.
- New training must NOT inherit physical StudyBatch1, grad accumulation4, synchronous HDF5, always-on activation checkpointing without benchmarks. Compare StudyBatch 1/2/4/8+, Window Microbatch 18/32/64/96/124/128+, checkpoint on/off, DataLoader prefetch and GPU parallel modes; use full optimizer, 128–256 real MRI studies, and select highest throughput.
- Full TRAIN time gate: target <=4h per run; predicted >4h requires optimization first; predicted >=8h blocked. Reproject at 200–500 Study and checkpoint+exit if budget breached. Avoid any repeat of an unplanned >=10h run.
- Historic Exp11B DINOv2-Base 140.50m/10 epochs (2GPU DataParallel, physical batch4, numpy mmap+prefetch) versus Stage1 up to630.70m/12 epochs (2 independent 1GPU Folds, StudyBatch1, accum4, HDF5 sync, activation checkpoint). 18 DINO Windows/Study for both.
- State: user decision/plan change, not new GPU profiling. Existing trained A/B best checkpoints retained.

### 2026-10-13 — A/B 2-Fold Public LB 결과 확인(사용자 보고)

- A STRICT 2-Fold Public LB **0.861**, B V4 2-Fold Public LB **0.910** (**사용자 직접 보고**, 독립 제출 ZIP/Script ID 미수신); B−A **+0.049**.
- 프로젝트 최고 Exp57 **0.918** 유지; B와 격차는 **−0.008**. Gold58 pooled development OOF A0.811284 vs B0.871112 결과 방향이 LB에서도 유지됐지만 서로 다른 평가 집합이며, A/B의 라벨과 Loss가 모두 달라 순수 라벨 품질 비교는 아니다.
- S7-LB = **`LB_SCORES_USER_REPORTED_A_0.861_B_0.910`**. Code submission Script Version, 실제 `submission.csv` SHA, hidden DICOM fallback count, 사용 GPU quota는 미확인 상태.
- **다음 한 가지 작업:** B V4 Fold0/1 encoder로 Full Native224 V3 특징 추출 및 MIL 설계에 진입하기 전에 128–256 Study 정확한 Encoder 추론/학습 비용과 30h/week GPU 예산을 측정하고, 중복 특징 추출·저장 비용을 비교해 선택. A 체크포인트는 폐기하지 않는다.
- GPU 정책: Batch124+ / 약20GB 여유 실측 이력 우선, 무근거 안전 Batch 축소 금지, 전체 GPU 학습 실행 목표 <=4h, 예측 >=8h 본학습 금지. **Stage1 재학습은 수행하지 않음.**

## 1. 목적과 비교 축

목적: 공통 Native224 MRI/Gold58 2-Fold에서 STRICT V1(엄격한 mask, 희소 클래스 보정)과 V4(soft/confidence 보정) DINOv2-Base Stage1을 비교, 품질이 확인된 Fold encoder로 전체 MRI 특징 추출 후 질환별 MIL을 학습한다. 단일 Fold 결과로 성능 단정하지 않으며 Stage1 AUROC 향상이 MIL AUROC 향상을 보장하지 않는다.

**현재 고정 변수:** 백본, 사전학습 가중치, MRI cache, manifest/sampler, Gold UID split, input 224×224, Study당18 Window, 12타깃, epoch12/patience4, Seed20261013, optimizer/LR, Study effective batch4 per Fold. **의도된 변경 변수:** 라벨 정책+타깃 mask/soft/confidence/class-balancing. 라벨 정책과 Loss 정책이 함께 변하는 비교라는 한계를 명시.

**현재 비교 Lane**
- `A_STRICT_V1_F0` GPU0 / `A_STRICT_V1_F1` GPU1, 각 독립 encoder.
- `B_V4_F0` GPU0 / `B_V4_F1` GPU1, 각 독립 encoder.
- A와 B는 **서로 다른 Kaggle 계정**으로 병렬 실행 가능하나, 원격 mount 접근 권한·GPU 예산 확인 필요.

## 2. 현재 단계별 계획표

| 단계 | 작업 | 필수 완료조건 | 상태 |
|---|---|---|---|
| S0 | Strict/V4 라벨·공통 Native224 cache 계약/원본 SHA | UID, 12 Target, masks, 5 Packs/190 Shards 검증 | `INPUT_MOUNT_METADATA_PASS` (190 Shard 전수 SHA는 과거 RMIL-04C00 별도 Audit 참조) |
| S1 | Gold58 별도 Kaggle Dataset 게시 | `rsna-knee-gold58-2fold-v1` 5개 파일 게시, 지정 root 마운트, 파일 SHA PASS | `A_B_KAGGLE_MOUNT_SHA_PASS` |
| S2 | Gold58 29/29 다중 타깃 분할 검증 | 58 UID 중복0/누락0, 각 Fold×12 Target 모두 positive≥1, negative≥1, A/B 동일 Fold SHA | `A_B_KAGGLE_SHA_AND_COVERAGE_PASS` |
| S3 | A/B V7 PREFLIGHT Save & Run All | 양 계정 5 Input, SHA, pretrain load, 두 GPU 분리, 최소 2-step 또는 실제 GPU 실험 검증, Loss/gradient, peak VRAM, 처리량 확인 | `A/B_GPU_PREFLIGHT_PASS` |
| S4 | 학습 시간·메모리 재평가 | 실측 GPU 처리량, microbatch 18/12/8/4, Study batch4/8 비교 필요성, 전체 예상 세션 비용, Resume 경로 | `EPOCH_RUNTIME_MEASURED` |
| S5 | A와 B Stage1 Fold0/1 TRAIN | 각 Fold best/last checkpoint, 두 fold success, class balance/epoch log, 실패 시 보존 산출물 복구 | `A/B_2FOLD_TRAIN_PASS` |
| S6 | Gold58 pooled OOF58 및 Target별 평가 | 예측 중복0/누락0, Macro AUROC/AUPRC, Recall·F1·Specificity 등; 클래스별 confusion, 근거 포함 | `POOLED_OOF58_VERIFIED_DEV` |
| S7 | Stage1 B V4 Fold0/1 우선 Full-MRI feature-cache 추출 (A 선택 보존) | B 모델 Dataset 경로 제공/사용자 LB 결과 수신; 기존 4개 모델의 정확한 SHA 및 실물 기반 feature provenance 검증, UID/Series/Slice/center, float16 1536d 해시·용량·GPU 시간 예산 | `READY_FOR_PERFORMANCE_PREFLIGHT / FILE_SHA_AUDIT_PENDING` |
| S7-LB | A/B independent 2-Fold Public LB submissions | User-reported A0.861/B0.910, check scriptVersion/CSV/hash when logs provided | `USER_REPORTED_A_0.861_B_0.910` |
| S9 | Top-K Selector / B3A 또는 direct MIL 앙상블 | MIL 중요도 상위 Window 선별, 기존 Exp57(0.918 Public LB) 비교, 독립 제출 성공 여부 구분 | `CONDITIONAL` |

### 즉시 다음 작업 — 한 가지

**S7/STAGE2 GPU 효율 사전 점검:** B V4 Fold0/1 `best.pt`를 Kaggle 제출 Dataset에서 사용 가능하다는 사용자 제공 경로를 기준으로, 실제 Full Native224 특징 추출의 I/O·추론 시간과 저장 예산을 소규모 대표 Study로 먼저 측정한다. 신규 학습이 수반되면 공통 주30시간 GPU quota·4시간 목표·8시간 차단 Gate를 통과해야 한다. A 보존.

## 3. 필수 Kaggle Input / 실행 정보

| Kaggle Add Input 표시명 | 목적 | A | B |
|---|---|:---:|:---:|
| `yhlucas/rmil-04b-full-mri-native224-v3` | 5 Pack Native224 MRI | ✓ | ✓ |
| `yhlucas/stage1-dino-shared-input-manifest-v1` | `common_series_manifest.csv`, `sampler_reference.py` | ✓ | ✓ |
| `yhlucas/rsna-knee-gold58-2fold-v1` | `gold58_manifest.csv`, `gold58_2fold_manifest.csv`, coverage/contract | ✓ | ✓ |
| MetaResearch `dinov2` PyTorch `base/1` | `pytorch_model.bin` | ✓ | ✓ |
| `yhlucas/rsna-knee-version-a-strict-v1` | `STRICT_V1/STRICT_V1_TRAIN_LABELS_12_TARGETS.csv` | ✓ | — |
| `yhlucas/rsna-knee-v4-consensus-dataset` | `rsna_knee_pseudolabels_v4_routed_broad.csv` | — | ✓ |

**Runtime:** T4×2 / Internet OFF / `RUN_MODE=PREFLIGHT`에서 Save & Run All. GPU0는 Fold0, GPU1는 Fold1. 두 독립 single-GPU processes, DDP 아님. Study physical batch1, gradaccum4 → effective4 per Fold. Window microbatch18/12/8/4를 실측하여 결정.

**Save Version 이름(각 60자 미만)**
- A PREFLIGHT `S1-STRICT-F01-WFIXV7-PREFLIGHT`; TRAIN `S1-STRICT-F01-WFIXV7-TRAIN`
- B PREFLIGHT `S1-V4-F01-WFIXV7-PREFLIGHT`; TRAIN `S1-V4-F01-WFIXV7-TRAIN`

**Run All 예상(실측 아님)**
- PREFLIGHT: **약 5~20분**, 초기 계획 근거 약함. Input mount/샤드 검증 시간 별도 변동.
- A TRAIN: 4,210 Studies/Fold × 4~12 Epoch. 12 Epoch에서 Study당 0.5~5초 가정 **7.0~70.2시간 이상**(I/O/검증/저장 오버헤드 미포함).
- B TRAIN: 4,378 Studies/Fold × 4~12 Epoch. 동일 가정 **7.3~73.0시간 이상**.
- **중요:** Kaggle 한 세션 제한 초과 위험 큼. V7 세션 간 checkpoint resume 미지원; 이번 학습은 실제 2-Fold 완료. 차기 Stage2는 checkpoint 별도 등록이 필요. 4를 데이터 규모만으로 확장하지도, 과거 Batch≥124 여유를 무시하고 1로 임의 축소하지도 않는다.

## 4. Gold58 및 실험 신뢰성 Gate

1. 전용 Dataset 내 Gold CSV SHA= `a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`, Fold CSV SHA=`6e66444e12a62c3f73670e421b939f1b286e21e496c29040754a72b1d18b4876`.
2. Fold0/Fold1 validation 각29, 합쳐 UID 58 전부 1회. Target 12×2 Fold에서 양성과 음성 모두 존재.
3. Fold held-out Gold는 그 Fold의 Stage1·MIL·Selector 및 tune에 유출 금지. 원본 STRICT 릴리스 Gold 금지와 본 **Custom Gold-Train 2Fold 연구**는 다른 프로토콜.
4. Gold58은 이미 반복 사용된 DEV 데이터. Model selection과 보고된 Gold58 OOF는 독립 test 점수로 주장 불가.
5. Loss class weights는 pseudo train only에서 산출. STRICT mask0→음성 변환 금지. V4 Soft Label의 Confidence 보존.
6. **실제 리더보드/제출/학습 완료 결과는 별도 GPU 로그·체크포인트·공식 점수로 확인한 뒤 기록.**

## 5. 운영·업데이트 규칙

- 계획 변경 시 이 파일의 고정/변경 조건·표·차단 이유·다음 한 가지 작업을 **수정**.
- 배치, Loss, Gold protocol 등 중요한 변경은 날짜와 이유를 이 파일의 '결정 이력'에 계속 누적.
- 실행 완료·부분 성공·실패·실측 시간/점수는 오직 `S1-DINO-CBL2F-01_EXPERIMENT_LOG.md`에 추가.
- 모델·라벨 스키마/경로/입력 버전 변경은 `S1-DINO-CBL2F-01_DATA_MODEL.md`에 갱신.
- 신규 Notebook/폴드/버그 하나마다 GitHub `.md` 신설하지 않는다. 공통 규칙은 [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md) 참조.

## 6. 결정 이력 (누적)

| 날짜 | 변경/결정 | 사유 | 영향 |
|---|---|---|---|
| 2026-10-13 | `S1-DINO-CBL2F-01`로 명명, 이 실험군의 GitHub 문서 3개 고정 | 중복 회피·누적 관리 요청 | 새 버전은 본 3개 파일 갱신 |
| 2026-10-13 | Gold58을 R2D cache에서 전용 `rsna-knee-gold58-2fold-v1`로 분리 | 데이터셋 용도 혼란 방지 | 두 계정의 Gold Input 교체, 실제 게시 확인 대기 |
| 2026-10-13 | A=STRICT distribution V3, B=V4 soft/conf balanced, Gold29×2 | 희소 양/음성 클래스와 Soft Label 특성 반영 | 두 실험은 라벨+Loss 차이가 동시에 존재, 통제 비교 필요 |
| 2026-10-13 | GPU0/1 독립 Fold 및 Full-MRI MIL 후속 | 두 GPU로 한 Fold DDP 대신 2-Fold 동시 학습 | Fold당 batch4, 모델 4개 추후 feature-cache 4종 |
| 2026-10-13 | A/B Stage1 2-Fold TRAIN 및 OOF 완료, B 우선 후보 | Gold58 pooled macro AUROC B=0.871112 > A=0.811284 (탐색적) | B 우선 Full-MRI MIL, A 유지, checkpoint Add Input 등록 필요 |

[데이터/모델 기준](S1-DINO-CBL2F-01_DATA_MODEL.md) · [실험 누적 로그](S1-DINO-CBL2F-01_EXPERIMENT_LOG.md)


### 2026-10-14 — S1-DINO-CBL2F-02 A/B Broad→Strict Fine-tune 노트북 준비 (미실행)

- **변경 이유:** Stage1 V4 Broad 2-Fold Public LB **0.910** 기반으로 MIL 이전에 2종 Strict 추가 Fine-tuning 비교. **공통 초기값은 B V4 Broad Fold0+Fold1 체크포인트**. 구 A Strict 0.861 초기 가중치는 사용하지 않는다.
- A 새 STRICT V1: pseudo 4,181 Studies / 유효 Binary Label 32,163. Target mask, pseudo-only 양/음성 imbalance power .70, 극심한 불균형에서 다수 Target만 순환 mask cap 20:1, target coverage weight power .35; Gold29는 중립 BCE×3.
- B V4 Routed Strict: pseudo 4,349 Studies / 유효 Soft Label 39,792. Mask 유효만 Confidence(.25+.75×conf) 가중, pseudo-only soft prevalence balance power .70 cap .5..2.5 및 target coverage weight power .35; Gold29는 중립 BCE×3.
- A/B 둘 다 DINOv2-Base full fine-tuning, 18 Windows/Study, native224 V3, 같은 Gold58 29/29 folds, backbone LR 1e-7/3e-7/1e-6, head LR 2e-5, AdamW WD .05, warmup5% linear, max3 Epoch, patience1(min2). Epoch0 Broad checkpoint score를 baseline으로 보존하고 향상 없으면 기존 가중치를 best로 유지.
- **신규 GPU batch gate:** Study physical batch 8/4/2/1, Window microbatch 124/72/36/18, activation checkpoint ON/OFF, HDF5 DataLoader workers2/Prefetch2, 128 Study full AdamW throughput profile; 예측 4시간 초과면 본학습 Fail-fast. 사용자 경험 Batch124+ / VRAM 약20GB 여유 / GPU 30h/week 우선 규칙 적용; 실제 허용 Batch는 GPU에서 계측.
- 준비한 Kaggle 노트북 A `S1FT02_A_BROAD_TO_STRICTV1_DUALFOLD_E3.ipynb` SHA256 `cabea26653a1c0c34b6983093461b467cef8e4b1a2aacad8a8ebb7b6aadf2232`, B `S1FT02_B_BROAD_TO_V4STRICT_DUALFOLD_E3.ipynb` SHA256 `dd98d379846c9602474772ac87c1c8fc11c7c6c2db5458421fba82bfadec38c6`.
- 추가로 두 개의 Submission 템플릿 마련. 훈련 Output에서 각 Fold `best.pt`와 `training_summary.json` 등록한 뒤 제출 가능. **실제 Kaggle GPU 학습·새 Public LB 점수는 아직 없음.** 현재 최고 Exp57 Public LB 0.918 유지. 다음 액션: A/B 학습 노트북 각각 Kaggle Input 6개 연결 및 Save & Run All → 로그/Review ZIP 확인 → 체크포인트 등록 후 LB 제출.
