# S1-DINO-CBL2F-01 — Stage1~MIL 실험 결과 누적 로그 (Append-Only)

> **2026-10-13 상태: 실측 Kaggle Stage1 GPU 학습 결과 0건.** 아래의 로컬 파일 검사와 구성 설계는 **실험 완료가 아님**. 노트북 실행 및 모델 평가가 끝날 때마다 **이 파일에 날짜순으로 아래쪽에만 기록**한다. 실험별 `.md` 파일을 새로 만들지 않는다.

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
