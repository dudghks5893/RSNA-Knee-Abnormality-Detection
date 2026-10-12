# S1-DINO-CBL2F-01 — 실험 계획·진행 현황 (갱신형 단일 문서)

> **Current as of 2026-10-13:** `DATA_PREPARED_LOCAL / GOLD_SPLIT_VERIFIED_LOCAL / KAGGLE_PREFLIGHT_PENDING`.
> 새 실험마다 계획서를 만들지 않고 **이 파일에서 현황·의존성·다음 한 가지 액션을 수정**한다. 실제 관측 점수는 별도 누적 EXPERIMENT_LOG에만 기록.

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
| S3 | A/B V6 PREFLIGHT Save & Run All | 양 계정 5 Input, SHA, pretrain load, 두 GPU 분리, 최소 2-step 또는 실제 GPU 실험 검증, Loss/gradient, peak VRAM, 처리량 확인 | `NOT_RUN` |
| S4 | 학습 시간·메모리 재평가 | 실측 GPU 처리량, microbatch 18/12/8/4, Study batch4/8 비교 필요성, 전체 예상 세션 비용, Resume 경로 | `BLOCKED_ON_S3` |
| S5 | A와 B Stage1 Fold0/1 TRAIN | 각 Fold best/last checkpoint, 두 fold success, class balance/epoch log, 실패 시 보존 산출물 복구 | `NOT_RUN` |
| S6 | Gold58 pooled OOF58 및 Target별 평가 | 예측 중복0/누락0, Macro AUROC/AUPRC, Recall·F1·Specificity 등; 클래스별 confusion, 근거 포함 | `BLOCKED_ON_S5` |
| S7 | Stage1 네 모델의 full-MRI feature-cache 추출 | 모델 별·Fold 별 서로 다른 가중치, UID/Series/Slice/center, float16 1536d, 해시/용량 budget 검증 | `PLANNED` |
| S8 | Study-level Full-MRI hierarchical MIL | 질환별 Window Attention→Series Attention, 정해진 동일 Fold 분리, Pooling baseline 대비 비교 | `PLANNED` |
| S9 | Top-K Selector / B3A 또는 direct MIL 앙상블 | MIL 중요도 상위 Window 선별, 기존 Exp57(0.918 Public LB) 비교, 독립 제출 성공 여부 구분 | `CONDITIONAL` |

### 즉시 다음 작업 — 한 가지

**S1: 사용자가 새 Gold58 Dataset 5개 파일을 Kaggle에 게시한 뒤, 각 계정에서 정확한 mount와 SHA를 PREFLIGHT로 검증.** 현재 대화에서 데이터셋 ZIP은 만들어졌으나 실제 Kaggle 업로드는 확인되지 않았다. S1 완료 증거가 있어야 S3로 전환.

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
- A PREFLIGHT `S1-STRICT-F01-GOLDV6-PREFLIGHT`; TRAIN `S1-STRICT-F01-GOLDV6-TRAIN`
- B PREFLIGHT `S1-V4-F01-GOLDV6-PREFLIGHT`; TRAIN `S1-V4-F01-GOLDV6-TRAIN`

**Run All 예상(실측 아님)**
- PREFLIGHT: **약 5~20분**, 초기 계획 근거 약함. Input mount/샤드 검증 시간 별도 변동.
- A TRAIN: 4,210 Studies/Fold × 4~12 Epoch. 12 Epoch에서 Study당 0.5~5초 가정 **7.0~70.2시간 이상**(I/O/검증/저장 오버헤드 미포함).
- B TRAIN: 4,378 Studies/Fold × 4~12 Epoch. 동일 가정 **7.3~73.0시간 이상**.
- **중요:** Kaggle 한 세션 제한 초과 위험 큼. 현 V6 노트북에 세션 간 checkpoint resume 없음. PREFLIGHT 처리량 측정 후 TRAIN 진행 여부 재결정. 4를 데이터 규모만으로 확장하지도, 과거 Batch≥124 여유를 무시하고 1로 임의 축소하지도 않는다.

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

[데이터/모델 기준](S1-DINO-CBL2F-01_DATA_MODEL.md) · [실험 누적 로그](S1-DINO-CBL2F-01_EXPERIMENT_LOG.md)
