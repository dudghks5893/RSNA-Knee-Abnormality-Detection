# S1-DINO-CBL2F-01 — Stage1~MIL 실험 결과 누적 로그 (Append-Only)

 > **최신 상태 2026-10-13: A/B Stage1 2-Fold TRAIN 완료 및 Gold58 OOF 검증 완료; A/B LB V2 Notebook 준비(공식 제출 미실행).** 초기 등록 항목의 미실행 상태는 작성 당시 기록이다. 노트북 실행 및 모델 평가가 끝날 때마다 **이 파일에 날짜순으로 아래쪽에만 기록**한다. 실험별 `.md` 파일을 새로 만들지 않는다.

## 0. 기록 규칙 (고정)

- 한 기록의 필수 항목: 날짜, 실험/계정/Fold, **실제 실행한** Notebook SHA, RUN_MODE, Kaggle Input 버전 및 실물 SHA, GPU/Batch/Microbatch, 완료된 Epoch/steps, GPU peak VRAM, 실제 Run All 시간, best Epoch, Gold29 또는 OOF58 macro/12 targets, 체크포인트/출력 SHA, 결과 상태(PASS/FAIL/PARTIAL/NOT_RUN), 오류 원인과 조치(과학적·재현성 핵심만).
- **실측**과 **추정**을 표/문장에서 명확하게 분리한다. 과거 Exp57 LB 0.918은 비교 기준이지 본 실험 성과가 아님.
- PRE-FLIGHT PASS는 full TRAIN PASS가 아니다. Gold58 반복 DEV OOF도 독립 Test가 아니다.
- 실패 시 마지막 artifact만 실패했는지 확인하고 기존 best checkpoint를 먼저 복구; GPU 재학습을 자동 지시하지 않는다.
- 각 완료 실험 때마다 결과를 이 파일에 추가하고 `S1-DINO-CBL2F-01_ROADMAP.md`의 완료 상태/다음 작업을 갱신. 입력 스키마나 모델 설정이 달라지면 `S1-DINO-CBL2F-01_DATA_MODEL.md`도 갱신.

## 1. 초기 등록 — 2026-10-13 / Stage1 V6 준비

**실험 이름:** `S1-DINO-CBL2F-01`: Strict V1 vs V4 Confidence/Class-balanced Stage1 DINOv2-Base / independent Gold58 two-Fold / downstream Full-MRI MIL.

**현재 확인된 로컬 산출물**
- A `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V6.ipynb`: SHA256 `bef2684ccc1e114782cf7cc7efc9c27db4cabeffa4e54317917b6898486a79e5`; 실제 Kaggle GPU 미실행.
- B `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V6.ipynb`: SHA256 `ebbd19492b51687e927d1c730197a3c4d7ec1f4e014e11f74b7be770cbac859b`; 실제 Kaggle GPU 미실행.
- Gold58 `gold58_manifest.csv` 사용자 제공 내용의 재구성 SHA256 `a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`, 58 UID×12 Target; 신규 Gold 전용 Dataset local ZIP 제작 **완료**, Kaggle 게시/마운트 **미확인**.
- `gold58_2fold_manifest.csv` SHA256 `6e66444e12a62c3f73670e421b939f1b286e21e496c29040754a72b1d18b4876`, Fold0/1 각29. Fold0·Fold1의 12개 타깃은 양성·음성 모두 있음(예: MCL Fold0 4+/25−, Fold1 5+/24−). **검증은 사용자 제공 로컬 라벨 기준**.
- Strict pseudo 라벨: 4,181 supervised Study, 32,163 유효 타깃, 양성 4,607/음성 27,556, 제외 20,025(전체 4,349×12 대비), 희소 MCL 양성37, Synovitis 음성35.
- V4 pseudo 라벨: 4,349×12 Soft Label+Confidence; 가장 불균형한 Fracture soft positive fraction 약 10% 수준, Synovitis 평균 confidence 약 0.173. 데이터/모델 명세에서 원본/버전 확인.
- A/B V6 예정 프로토콜: 각각 T4×2 물리 GPU를 Fold별 독립 사용, Stage1 supervised encoder, effective Study batch4 per Fold, train max12/patience4, Gold OOF58 검증, 4개 encoder 특징 추출→MIL 예정.

**로컬 준비 vs 실측 상태표**

| 단계 | 상태 | 증거/비고 |
|---|---|---|
| 입력·스키마 분석 | `LOCAL_PASS` | STRICT/V4 사용자 제공 ZIP의 CSV 열/해시 및 분포 확인 |
| Gold58 29/29 split 양·음성 coverage | `LOCAL_PASS` | 24개 Fold×Target 모두 양·음성 존재 |
| Gold58 Dataset Kaggle 등록 | `NOT_CONFIRMED` | 사용자 업로드 확인 전 |
| A/B Notebook Kaggle PREFLIGHT | `NOT_RUN` | CUDA 처리량/VRAM 미측정 |
| A/B Stage1 각 2-Fold TRAIN | `NOT_RUN` | best.pt/last.pt 실측 없음 |
| Gold58 pooled OOF58 | `NOT_RUN` | AUROC/AUPRC/Recall/F1 수치 없음 |
| Full MRI feature cache / MIL | `PLANNED` | 모델 최종 평가 이전 |

**주의/위험:** `CUSTOM_GOLD_2FOLD_TRAIN`은 STRICT 원본 릴리스의 Gold 학습 금지 규칙과 다른 사용자 연구 프로토콜. Gold58 여러 번 개발용으로 사용한 결과는 독립 성능 추정 아님. 현 V6는 Kaggle 세션 간 resume 미구현이므로 GPU 시간 측정 전 장시간 학습 금지.

## 2. 실제 GPU PREFLIGHT / TRAIN 결과 — 아직 없음

새 로그를 받으면 다음 양식을 **반복해서 이 절 아래에 계속 추가**:

```text
### YYYY-MM-DD — <lane/fold/notebook version>
- 상태: PREFLIGHT_PASS | TRAIN_PASS | PARTIAL | FAIL
- Notebook/Input SHA 및 Kaggle Script Version:
- GPU 모델·2GPU isolation·Window microbatch·study batch/accum:
- 측정 peak VRAM / study 처리량 / 실제 runtime:
- Epoch / optimizer steps / best Epoch:
- Validation 12-target AUROC/AUPRC; Recall/F1/Specificity 등:
- Gold58 OOF58 (양 Fold 완료 후):
- best.pt/last.pt/predictions SHA 및 저장 위치:
- 확인된 사실 / 실패 원인 / 후속 결정:
```

## 3. 향후 Stage2 Full-MRI MIL 결과 — 아직 없음

Stage1 Fold checkpoint 4개가 확보되면 fold별 DINO feature extraction SHA와 CLS+PatchMean1536 cache UID/Slice coverage를 검증한 뒤, Window/Series Attention MIL 결과와 Top-K ablation 성적을 이 파일에 순서대로 누적한다. 실험별 새 `.md`는 만들지 않는다.

[데이터/모델 기준](S1-DINO-CBL2F-01_DATA_MODEL.md) · [현재 계획/상태](S1-DINO-CBL2F-01_ROADMAP.md)


### 2026-10-13 — B V4 V7 PREFLIGHT 실측 PASS (TRAIN 미실행)

- **실행 방식/증거:** 사용자 제공 실제 Kaggle 실행 TXT `붙여넣은 텍스트(1)(20261012-191942).txt`, `STAGE1_V4_DUALFOLD_PREFLIGHT_review.zip`. ZIP CRC 전체 PASS; V4 Worker SHA256 `0a2cd180491ad0c91502f40a4287c0739c8b5d108e50867002754dad70d0a2d7`, AST PASS. Notebook 실행은 V7 WorkerFix, `RUN_MODE=PREFLIGHT`.
- **데이터 계약:** common manifest 24,371 Series/4,407 Studies; 5 Packs 각38 Shards; Gold58 전용 데이터셋 및 29/29 UID split SHA PASS; 12타깃 Fold별 positive/negative PASS; V4 pseudo 4,349+각 Fold Gold29 → **4,378 train/Fold**, Gold29 val/Fold; leakage 검사 PASS.
- **Loss:** `LOSS_CONTRACT_PASS Gold3xNoPseudoPrior Conf0.25 MaskedNoGradient 12-target_norm`; V4 pseudo Confidence-weighted tempered positive/negative class BCE; Synovitis 평균 confidence 약0.173 / Fracture weighted soft positive prevalence 약0.1002는 경고로 기록(오류 아님).
- **실제 GPU0 Fold0:** T4 독립 worker exit0; Window microbatch18, peak allocated **2.41 GiB**, synthetic full18 Window F+B **1.32초**, 실제 HDF5 Study F+B **0.239102214초**, loss0.4005183, `GPU_PREFLIGHT_PASS`.
- **실제 GPU1 Fold1:** T4 독립 worker exit0; microbatch18, peak allocated **2.41 GiB**, synthetic full18 Window F+B **1.32초**, 실제 HDF5 Study F+B **0.236578257초**, loss0.4299068, `GPU_PREFLIGHT_PASS`.
- **결과:** `BOTH_GPU_PREFLIGHT_PASS`, `PREFLIGHT COMPLETE`. **아직 optimizer step이나 전체 epoch는 수행되지 않음; best.pt/last.pt 없음; 학습 성능 기록 없음.**
- **12 Epoch GPU F+B만 단순 예상:** Fold0 3.49시간 / Fold1 3.45시간(동시 실행, 합산 금지). HDF5 I/O·Optimizer step·Epoch validation·checkpoint 저장·병렬 I/O 경합 **미반영**, 실제 시간은 더 길 수 있음. 세션 간 resume 미구현이므로 Kaggle 세션 제한 시 중도 결과 위험.
- **결정:** B는 입력/실제 모델 GPU 사전검증을 통과해 `RUN_MODE=TRAIN`으로 변경할 수 있는 단계. 단 과도한 시간·비용 위험을 명시하고 1 Epoch 실측/남은 세션 예산을 모니터링할 것. A STRICT V7 GPU PREFLIGHT는 별도 로그 확인 대기.


### 2026-10-13 — A STRICT V1 V7 실제 GPU PREFLIGHT PASS (TRAIN 미실행)

- **실행/증거:** 사용자 제공 `STAGE1_STRICT_DISTRIBUTION_V3_PREFLIGHT_review.zip`. ZIP 내 27개 파일 CRC PASS; `dual_preflight_summary.json`에 `BOTH_GPU_PREFLIGHT_PASS`; 양 Fold `console.log`, `gpu_preflight_results.json` 대조. `stage1_strict_worker.py` 존재, Worker 파일 생성 문제 V7에서는 해결.
- **데이터 계약:** 입력 manifest 24,371 Series/4,407 Studies, pseudo STRICT supervised 4,181/각 Fold Gold train29 → **4,210 Study/Fold**, held-out Gold29/Fold. 원본 STRICT 희소 클래스 Target-mask가 보존됨. 독립 Fold 프로세스 exit0 (해당 JSON 및 사용자 제출 ZIP 기준).
- **Loss 검증:** 양 Fold `LOSS_CONTRACT_PASS Goldx3 Conf0.25 MaskedNoGradient 12-target_norm`. Fold0/1 공통 `epoch_01_balance_preview.json`의 majority rotation: MCL 3,724 negatives 중 740, Lateral OA 2,490 negatives 중 1,320 매 Epoch 선택. MCL 37 positives·LateralOA 66 positives·Synovitis 35 negatives 전부 보존, rescue0.
- **GPU0 Fold0:** Window Microbatch18, peak allocated **2.41 GiB**, synthetic 18-window F+B **2.60초**, real HDF5 Study F+B **0.270552014초**, loss **0.0366938189**; `GPU_PREFLIGHT_PASS`.
- **GPU1 Fold1:** Window Microbatch18, peak allocated **2.41 GiB**, synthetic F+B **2.59초**, real Study F+B **0.239363503초**, loss **0.0585563257**; `GPU_PREFLIGHT_PASS`.
- **12 Epoch F+B-only 투영:** Fold0 약 **3.80시간**, Fold1 약 **3.36시간**(동시 실행). HDF5 I/O, Optimizer, validation, checkpoint, 두 Fold의 동시 I/O 경합 미포함. 단일 Study 표본 측정으로 전체 Epoch 시간 확정 불가.
- **상태:** 실제 Kaggle GPU 사전검증 PASS. **Optimizer step / 첫 Epoch / 모델 학습 / 성능 지표는 아직 미실행**. Cross-session Resume 기능이 없어 세션 중단 위험을 갖고 있음.
- **다음:** A는 `RUN_MODE=TRAIN` 전환 가능; Save Version `S1-STRICT-F01-WFIXV7-TRAIN`, GPU T4×2 Internet OFF Save & Run All. 첫 Epoch/로그의 실제 시간·남은 세션 한도를 확인해야 함.


### 2026-10-13 — A STRICT V1 vs B V4 Stage1 2-Fold TRAIN 완료 / Gold58 OOF 비교

**상태:** A, B 각각 `BOTH_FOLDS_TRAIN_SUCCESS`, Fold0·Fold1 각 `STAGE1_TRAIN_SUCCESS`; ZIP CRC PASS; Gold58 예측 58 UID 모두 유일하며 양 계정의 UID·Fold·12타깃 Truth가 동일. 유저 제출 TRAIN ZIP의 원본 CSV를 재계산하여 macro 및 타깃별 AUROC·AUPRC 원본 출력과 일치 확인. **best.pt/last.pt 본체는 ZIP에서 제외된 상태**로 SHA/경로는 학습 보고서에서만 확인됨; Kaggle Output 모델 파일을 반드시 별도 보관.

**실행 증거:**
- A: `STAGE1_STRICT_DISTRIBUTION_V3_TRAIN_review.zip` SHA256 `92284f1eaf71a1abbefd0e7f54fab8fbdb5a188fe8feb1413015d144d65c01ee`; `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb`, STRICT 4,181 pseudo + 29 Gold train/Fold = 4,210.
- B: `STAGE1_V4_DUALFOLD_TRAIN_review.zip` SHA256 `650bd27f58b16dfd18a65d021c5535263f11a362439de8f346ee3e7c6dd858d0`; `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb`, V4 4,349 pseudo + 29 Gold train/Fold = 4,378.
- 두 계정 모두 실제 T4×2, Fold0 GPU0 / Fold1 GPU1 독립 병렬, Window microbatch18, effective Study batch4/Fold, 224×224 3-Slice Window×18, DINOv2-Base full fine-tune.

| 계정/Fold | Best Gold29 Macro AUROC | Best Epoch | 학습 Epoch | 각 Fold 실제 시간 | best.pt SHA256 (학습 보고서 기반) |
|---|---:|---:|---:|---:|---|
| A STRICT Fold0 | 0.838365 | 9 | 12 | 630.67 min | `e5ae8a3a2b30d5bf71a19aabc7cfba888bb05d91b152d82931c3d44f3d4387a6` |
| A STRICT Fold1 | 0.785654 | 7 | 11 | 587.92 min | `954d099a0e4274c1ee4581fc8c518fd3f30dcafff39e4d2ed941eb9224704935` |
| B V4 Fold0 | 0.892702 | 8 | 12 | 629.08 min | `15bd9189eac7a7366239a0747e671f0f567a40a2db660e7054e2de26eb01e629` |
| B V4 Fold1 | 0.868232 | 9 | 12 | 630.70 min | `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5` |

**Gold58 pooled OOF — 모델별 Fold best checkpoint에서 나온 58명 통합 예측; threshold-dependent metrics는 0.5 고정**

| Metric | A STRICT | B V4 | B−A |
|---|---:|---:|---:|
| Macro AUROC | 0.811284 | **0.871112** | +0.059828 |
| Macro AUPRC | 0.729597 | **0.800206** | +0.070609 |
| Macro Recall@0.5 | 0.6170 | **0.8223** | +0.2053 |
| Macro Precision@0.5 | **0.7975** | 0.6391 | −0.1584 |
| Macro F1@0.5 | 0.6347 | **0.7053** | +0.0706 |
| Macro Specificity@0.5 | **0.8529** | 0.7389 | −0.1140 |
| Macro Balanced Accuracy@0.5 | 0.7350 | **0.7806** | +0.0456 |

**Gold58 타깃별 A/B AUROC**

| Target | Gold positive | A STRICT | B V4 | B−A |
|---|---:|---:|---:|---:|
| ACL | 24 | 0.8848 | 0.9007 | +0.0159 |
| MCL | 9 | 0.7007 | 0.8639 | +0.1633 |
| Medial Meniscus | 26 | 0.8918 | 0.9423 | +0.0505 |
| Lateral Meniscus | 23 | 0.7739 | 0.8037 | +0.0298 |
| Medial OA | 15 | 0.8233 | 0.9628 | +0.1395 |
| Lateral OA | 11 | 0.7485 | 0.8569 | +0.1083 |
| PF OA | 21 | 0.7786 | 0.8211 | +0.0425 |
| Effusion | 35 | **0.9540** | 0.9329 | −0.0211 |
| Synovitis | 27 | **0.6906** | 0.6762 | −0.0143 |
| Baker's | 12 | 0.8460 | 0.9783 | +0.1322 |
| Contusion | 19 | 0.8070 | 0.8853 | +0.0783 |
| Fracture | 18 | **0.8361** | 0.8292 | −0.0069 |

**통계 참고(탐색적):** 동일 58 UID를 짝지어 Study-level replacement bootstrap 1200회 실시한 V4−STRICT pooled macro AUROC 델타 퍼센타일 2.5–97.5% 약 **+0.014~+0.106**; AUPRC 델타 약 **+0.004~+0.137**. Best Epoch를 같은 Gold58에서 선택했으므로 **독립 검증 CI나 확증적 p-value로 해석 금지**. MCL Gold 양성 9명 등 소표본으로 지표 분산 큼.

**해석 및 결정:** B는 Gold58 개발 OOF ROC 기준 12타깃 중 9개에서 우세. Effusion/Synovitis/Fracture는 A가 소폭 우세. B를 다음 Full-MRI feature-cache/MIL 우선 백본 후보로 선택하되 **A Fold0/1 체크포인트는 보존**, 후속 A/B 또는 앙상블 비교 후보로 유지한다. A/B는 label 분포뿐 아니라 4,181 vs 4,349 Study, target mask, class-balanced loss/Confidence 차이가 있어 B 우위를 단일한 'V4 라벨 품질' 인과효과로 주장 금지. Recall/F1의 임계값 최적화는 58 Gold에서 재튜닝 시 낙관편향 위험.

**차단 사항/다음 작업:** 제출 ZIP에 **모델 가중치 `.pt` 바이너리 없음**. Kaggle 각 실행의 Output `fold0/best.pt` + `fold1/best.pt` 총 4개 파일 보존 여부 및 SHA를 확인하고, 이를 Add Input 모델/데이터셋으로 등록한 뒤 Fold-aware Stage2 특징 추출을 설계해야 한다. Kaggle Public LB 점수는 본 실험에서 측정하지 않음.


### 2026-10-13 — A/B independent 2-Fold LB submission notebooks prepared (NOT submitted)

Experiment S1-DINO-CBL2F-01 Stage1 has A STRICT and B V4 independently trained Fold0/Fold1 best checkpoints. These are **separate LB submissions**, each equal 0.5/0.5 sigmoid probability averaging (not A+B averaging). No model training or Gold58-based calibration during inference.

A notebook: A_S1-DINO-CBL2F-01_STRICT_2FOLD_LB_SUBMISSION_V1.ipynb SHA256 268187b2ab0db2390a008cb627adaa0e8aa731b2ff8f35560cdaf85856d59eb1.
B notebook: B_S1-DINO-CBL2F-01_V4_2FOLD_LB_SUBMISSION_V1.ipynb SHA256 a0c7bd71d50f5e652f49ee1f23398be1eceb8b34b6fcc2b4195e6b60ebe04392.

Source architecture copied verbatim from actual Train ZIP FeatureDINO Worker (identical A/B class SHA b385856a8e5ecfcd81da42c417dc1ba96ca5cb4f3d345a44a162907c32ad0874). Stage1 sampler from Train ZIP SHA 8ce97e7cebf0c75597e6bd8ea8c262bfb6596dfdcbf0975b8d31101fe125052c. Preprocessing follows RMIL-04B Native224 V3 physical slice ordering, 130mm center crop, per-Series percentile 0.5/99.5, Zscore, clamp +/-5, INTER_AREA 224, uint8; 20 Study/360 Window sampler and 12-Slice/3-triplet synthetic byte parity tests PASS.

Required Kaggle Add Input per account: (1) Competition RSNA Knee Abnormality Detection test.csv/test_series.csv/sample_submission.csv/test_series/*.dcm; (2) NEW USER-UPLOADED checkpoint dataset A yhlucas/rsna-knee-stage1-strict-f01-best-v1 or B yhlucas/rsna-knee-stage1-v4-f01-best-v1, files fold0_best.pt/fold1_best.pt in its root (PROPOSED, not yet confirmed created); (3) MetaResearch dinov2 PyTorch Base version1 original pretrained model (SHA pinned). No training HDF5, pseudo label or Gold58 required.

GPU T4x2, GPU0 Fold0/GPU1 Fold1; 2 GPU parallel inference, Internet OFF, Save & Run All. Kaggle GPU code submission max 9 hours. Visible 3 Studies and ~1300 hidden Studies runtime estimate 1-10min / 2-8h+ is speculative, not measured. Per Study corruption logged with neutral fallback, final submission.csv exact schema/UID/finite probability SHA verified.

STATUS: NOTEBOOKS_STATIC_QA_PASS; CHECKPOINT_DATASET_MOUNT_PENDING; REAL_KAGGLE_GPU_UNVERIFIED; OFFICIAL_PUBLIC_LB_NOT_SUBMITTED. Model best.pt binary not contained in TRAIN review ZIP. Register actual checkpoint files from completed Kaggle outputs; only then execute and score. Historical Gold58 OOF STRICT 0.811284 / V4 0.871112 are NOT LB scores.

### 2026-10-13 — LB Submission V2 exact checkpoint paths (user supplied; not yet executed)

- A checkpoint Dataset: `yhlucas/rsna-knee-stage1-strict-f01-best-v1`; exact files:
  - `/kaggle/input/datasets/yhlucas/rsna-knee-stage1-strict-f01-best-v1/fold0/best.pt`
  - `/kaggle/input/datasets/yhlucas/rsna-knee-stage1-strict-f01-best-v1/fold1/best.pt`
- B checkpoint Dataset **owner differs**: `woniyeon/rsna-knee-stage1-v4-f01-best-v1`; exact files:
  - `/kaggle/input/datasets/woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold0/best.pt`
  - `/kaggle/input/datasets/woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold1/best.pt`
- Newly corrected notebooks:
  - A `A_S1-DINO-CBL2F-01_STRICT_2FOLD_LB_SUBMISSION_V2_EXACTPATH.ipynb`, SHA256 `d272241254c8222004a74dbf34def355a6093cc7ef588d5852a22e965a89bdb0`.
  - B `B_S1-DINO-CBL2F-01_V4_2FOLD_LB_SUBMISSION_V2_EXACTPATH.ipynb`, SHA256 `2c7323124de1b5fa3a2de2463618f19b6a342a9c7e060abe8a9a0dcf0ce2cb95`.
- Only checkpoint path owner/subfolder and first Markdown / Save Version metadata changed. Original FeatureDINO architecture, RMIL-04B V3 raw DICOM policy, 18-window sampler, 2GPU Fold probability averaging, SHA-pinned `best.pt` and pretrained weights retained.
- **QA:** Both Notebook JSON/nbformat/6 code-cell AST PASS; exact-path assertions, checkpoint SHA literals verified in source; ZIP CRC PASS. User provided paths but live Kaggle mount and actual `best.pt` bytes are **not yet verified**. Status `NOTEBOOK_V2_STATIC_PASS / KAGGLE_INFERENCE_NOT_RUN / PUBLIC_LB_UNKNOWN`.


### 2026-10-13 — Performance audit: Exp11B 140.50min vs Stage1 V7 ~630min

**Observed source**: historical 2026-09-21 Exp11B complete Kaggle saved code/log (Fold2), repository README Experiment37; new Stage1 user-provided A/B TRAIN review ZIPs, fold console logs and training_history.csv. This is a comparison of *different execution designs*, not a controlled benchmark.

| Item | Exp11B DINOv2-Base | Current S1 A/B V7 |
|---|---|---|
| Backbone/resolution/full FT | DINOv2-Base / 224 / Yes | same |
| DINO calls per Study | 6 slots × (9 slices/3-channel) = 18 | 18 three-slice windows |
| Parallelization | 2×T4 DataParallel **one Fold/model** | GPU0 Fold0 and GPU1 Fold1 **independent models** |
| Batch | physical Study batch 4, grad accum1 | physical Study batch 1/GPU, grad accum4, effective4 per Fold |
| Cache/data loader | Persistent `.npy` `np.load(mmap_mode='r')`; DataLoader num_workers4, prefetch_factor2, pin_memory | 190 HDF5 shards random access, synchronous `train_ds[idx]` in worker (no DataLoader training prefetch), 12-open-file LRU cache |
| Activation checkpoint | absent in retrieved Exp11B training model | `_features` checkpoint `use_reentrant=False` every Study in Train |
| Train studies/Fold | 4,396 | A4,210; B4,378 |
| Epochs executed | 10 (early stop) | A Fold0 12, Fold1 11; B both12 |
| Time per epoch | Exp11B epoch10 13.97min, full mean ~14.05min | A Fold0 52.56min, B Fold0 52.42min |
| Total/Fold | 140.50min | A Fold0 630.67min; B Fold0 629.08min / Fold1 630.70min |
| Throughput | 5.22 studies/sec per model on 2 GPUs | A Fold0 ~1.34 studies/sec per GPU; B Fold0 ~1.39 studies/sec per GPU |

**Quantitative analysis:** B wall time ~4.48× Exp11B (630/140.5); mean epoch time ~3.73× (52.4/14.05) plus 12 vs 10 epochs ×1.2 explains total. The 18 DINO inputs/Study were **the same**; more images per Study is *not* the cause. GPU count allocation 2 GPUs per Fold versus 1 GPU per Fold can explain part; 1-Study sequential forward/backward/4× accumulation, activation checkpoint recomputation, and synchronous HDF5 I/O likely cause the remainder. Neither model-side versus I/O side nor each factor's proportion is separately timed, so no measured causal attribution/percentages.

**Optimization gate (no automatic retraining):** benchmark same Fold+same data+same selected model and 100-200 Study under (1) checkpoint on/off only after actual optimizer VRAM profile, (2) physical Study batch1 vs2/4 with grad accumulation adjusted to preserve effective4 (vectorized forward; never confuse Study with Window microbatch), (3) HDF5 background DataLoader workers 0/2/4 + pinned prefetch, (4) independent Fold vs DP/DDP two GPUs if goal is single-Fold wall time; separately report two-Fold total GPU-hours, preprocessing vs GPU F/B+optimizer time, measured Study/sec, peak allocated/reserved, loss/scientific parity. All these are FUTURE potential fixes, not verified runtime reductions.

### 2026-10-13 — New GPU resource rule: Batch124+ evidence, 30h/week (policy decision)

- User re-confirmed past real observations: simultaneous Batch124+ feasible and approximately 20GB unused VRAM. Exact model, GPU(s), and Batch unit are unconfirmed; do not silently downgrade these observations to speculative OOM concerns.
- User GPU quota is 30 hours per week. The previous A/B Stage1 training taking as much as ~630.7 minutes must not recur because of unnecessarily low Study Batch, lack of HDF5 prefetch, or checkpointing without performance profiling.
- Shared AI_AGENT_KAGGLE_NOTEBOOK_RULES and GPU_BATCH_RESOURCE_MANDATORY_POLICY updated to require 128-256 MRI Study full-step profiling, aggressive larger Batch exploration (including 124+ where available), highest-throughput selection, full GPU time forecast (goal <=4h/run, block >=8h predicted), stop/checkpoint if projected budget breached, weekly quota tracking.
- Existing S1-DINO-CBL2F-01 ROADMAP and DATA_MODEL documents updated in place, not split. Completed training models unchanged; no new GPU experiment was run for this administrative change. Future claims about max current-model Batch will require measurement.
