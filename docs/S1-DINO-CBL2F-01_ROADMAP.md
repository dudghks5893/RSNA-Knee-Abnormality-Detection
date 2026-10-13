# S1-DINO-CBL2F-01 — 실험 계획·진행 현황 (갱신형 단일 문서)

> **Current as of 2026-10-13:** `DATA_PREPARED_LOCAL / GOLD_SPLIT_VERIFIED_LOCAL / KAGGLE_PREFLIGHT_PENDING`.
> 새 실험마다 계획서를 만들지 않고 **이 파일에서 현황·의존성·다음 한 가지 액션을 수정**한다. 실제 관측 점수는 별도 누적 EXPERIMENT_LOG에만 기록.

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
| S0 | Strict/V4 라벨·공통 Native224 cache 계약/원본 SHA | UID, 12 Target, masks, 5 Packs/190 Shards 검증 | `로컬 라벨·명세 확인`; Kaggle mount 확인 전 |
| S1 | Gold58 별도 Kaggle Dataset 게시 | `rsna-knee-gold58-2fold-v1` 5개 파일 게시, 지정 root 마운트, 파일 SHA PASS | `PENDING_USER_UPLOAD/MOUNT` |
| S2 | Gold58 29/29 다중 타깃 분할 검증 | 58 UID 중복0/누락0, 각 Fold×12 Target 모두 positive≥1, negative≥1, A/B 동일 Fold SHA | `LOCAL_PASS`, Kaggle `PENDING` |
| S3 | A/B V7 PREFLIGHT Save & Run All | 양 계정 5 Input, SHA, pretrain load, 두 GPU 분리, 최소 2-step 또는 실제 GPU 실험 검증, Loss/gradient, peak VRAM, 처리량 확인 | `A/B_GPU_PREFLIGHT_PASS` |
| S4 | 학습 시간·메모리 재평가 | 실측 GPU 처리량, microbatch 18/12/8/4, Study batch4/8 비교 필요성, 전체 예상 세션 비용, Resume 경로 | `EPOCH_RUNTIME_MEASURED` |
| S5 | A와 B Stage1 Fold0/1 TRAIN | 각 Fold best/last checkpoint, 두 fold success, class balance/epoch log, 실패 시 보존 산출물 복구 | `A/B_2FOLD_TRAIN_PASS` |
| S6 | Gold58 pooled OOF58 및 Target별 평가 | 예측 중복0/누락0, Macro AUROC/AUPRC, Recall·F1·Specificity 등; 클래스별 confusion, 근거 포함 | `POOLED_OOF58_VERIFIED_DEV` |
| S7 | Stage1 네 모델의 full-MRI feature-cache 추출 | 모델 별·Fold 별 서로 다른 가중치, UID/Series/Slice/center, float16 1536d, 해시/용량 budget 검증 | `BLOCKED_ON_CHECKPOINT_REGISTRATION` |
| S8 | Study-level Full-MRI hierarchical MIL | 질환별 Window Attention→Series Attention, 정해진 동일 Fold 분리, Pooling baseline 대비 비교 | `PLANNED` |
| S9 | Top-K Selector / B3A 또는 direct MIL 앙상블 | MIL 중요도 상위 Window 선별, 기존 Exp57(0.918 Public LB) 비교, 독립 제출 성공 여부 구분 | `CONDITIONAL` |

### 즉시 다음 작업 — 한 가지

**S7 준비: A/B 각각 Fold0·Fold1 `best.pt` 총 4개 파일을 Kaggle Output에서 보존·등록한 뒤, 학습 summary의 SHA256와 실제 체크포인트를 검증한다.** 확인 전 Stage2 특징 추출 작업 착수 금지.

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
| 2026-10-13 | GPU0/1 독립 Fold 및 Full-MRI MIL 후속 | 두 GPU로 한 Fold DDP 대신 2-Fold 동시 학습 | Fold당 batch4, 모델 4개 추후 feature-cache 4종 |\n| 2026-10-13 | A/B Stage1 2-Fold TRAIN 및 OOF 완료, B 우선 후보 | Gold58 pooled macro AUROC B=0.871112 > A=0.811284 (탐색적) | B 우선 Full-MRI MIL, A 유지, checkpoint Add Input 등록 필요 |

[데이터/모델 기준](S1-DINO-CBL2F-01_DATA_MODEL.md) · [실험 누적 로그](S1-DINO-CBL2F-01_EXPERIMENT_LOG.md)
