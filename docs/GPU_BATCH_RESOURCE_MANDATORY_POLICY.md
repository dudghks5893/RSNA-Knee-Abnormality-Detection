# 필수 규칙 — GPU 메모리·배치 크기·시간 예산 (최신 2026-10-13)

## 2026-10-13 최신 우선 정책 — 주 30시간 / Batch 124+ / 10시간 학습 방지

사용자가 **실제로 Batch 124개 이상 동시 처리**와 **VRAM 약 20GB 여유**를 경험했다고 재확인했다. 이 값은 우선 보존할 실측 이력이다. 개별 T4의 용량과 2GPU 합산 여유를 혼동하거나 Study Batch와 Window Microbatch를 같은 단위라고 가정하지 않는다. 그러나 **OOM을 단순히 우려한다는 이유만으로 작업량을 작게 쪼개는 보수적 선택은 금지**한다.

1. **VRAM 사용률 자체는 벌점이 아니다.** 목표는 실제 학습 처리량(Study/s, Window/s) 최대화 및 GPU시간 절약. 잠재적인 124+ 배치를 적극 탐색한다.
2. 동일 입력/모델/학습 모드에서 실측 Window Microbatch 후보 **18/32/64/96/124/128+**, 실제 Study Physical Batch **1/2/4/8+**를 가능한 범위에서 비교한다. 일반적인 Checkpointing ON 고정·Batch1/GradientAcc4 고정 금지. 메모리/속도 최적화 때문에 배치를 줄이려면 **실제 OOM 또는 처리량 악화 기록**을 제시해야 한다. 불필요한 실패 반복은 피하되 OOM 공포로 실측 탐색을 포기하지 않는다.
3. **PREFLIGHT 측정 범위:** 대표 MRI 128~256 Study, Warmup, 2회 이상 실제 Optimizer Step(AdamW state 포함), full F+B, 데이터 읽기, 검증, Checkpoint 저장. Study×Window 실측 throughput, peak allocated/reserved, I/O%, 2GPU 방식/누적 gradient의 호출 횟수 별도 기록. 단일 Study F+B 측정값만으로 전체 시간을 추정하지 않는다.
4. **GPU weekly quota 30시간(사용자 제한):** A/B 계정의 사용/잔여 시간을 기록하고 이번 주 GPU 사전실험·TRAIN·Submit/추론·재시도 예정 시간을 함께 산출한다. Kaggle에서 T4×2 시간을 어떻게 차감하는지는 각 계정 UI 실제 자료로 확인한다.
5. **Full TRAIN 사전 통제:** 목표는 1회 실행 4시간 이내. 4시간 예상 초과 → 본학습 대신 병렬화/Study batch/HDF5 prefetch/Activation Checkpoint 최적화 후 재계측. 8시간 이상 예상되는 신규 본학습 **실행 불가**. 10시간 이상의 무계획 자원 소모는 반복하지 않는다.
6. **자동 조기 종료와 Resume:** 128~256 Study 및 첫 200~500 Study 실측으로 전 Epoch 예상 시간을 재계산한다. 예산/시간 상한을 초과하는 계획이면 신속히 종료하고 `best.pt`, `last.pt`를 보존한다. 중단-재개 과정은 장시간 학습 전 Smoke Test. Kaggle 세션 끝나서 모델 전체를 잃는 상황도 방지.
7. **과거-현재 비교 근거:** Exp11B DINOv2-Base는 2GPU DataParallel/physical StudyBatch4/GradientAccum1/`.npy` prefetch/No activation checkpoint에서 10 Epoch 총 140.50분 (약14.05분/Epoch). S1-DINO-CBL2F-01은 GPU마다 1 Fold, physical StudyBatch1/Accum4/HDF5 sync/activation checkpoint에서 각 12 Epoch 약630분(약52.4분/Epoch). 모두 Study당 DINO 입력 18개. 원인별 상대 기여율은 실제 profile 전까지 확정 금지.
8. Notebook을 인도할 때 **실측으로 검증한 batch 범위, throughput, 예상 wall/GPU quota, 사용자가 요청한 30시간 잔여예산 및 이 Gate의 PASS/FAIL**을 첫 Markdown과 실행 로그에 기록한다.

**이 섹션이 아래 2026-10-12 기록 중 '작은 배치 보수 설계', '시간 예측을 단일 Study F+B에서 외삽' 등의 권장과 충돌하면 최신 2026-10-13 규칙을 우선한다.** 사용자 제공 20GB 여유가 GPU별/전체 합산 어느 쪽인지 증거 없이 GPU 개별 할당에 대입하지 않는다.

---

> **CRITICAL / 반드시 먼저 읽기**: 사용자 직접 지시. 이 문서는 이후 모든 Kaggle RSNA Knee 실험 설계, 인수인계, Notebook 생성 및 변경 검토에 우선 적용한다. GPU 크레딧/할당량은 유한하며, 이전에 검증한 메모리 여유를 무시하는 보수적 추측은 금지한다.

## 1. 사용자 보고 실측 기록 — 잊거나 무시하지 말 것

- **초기 실험에서 실제 GPU 메모리 사용량을 측정했고, Batch Size 124 이상으로 설정해도 GPU VRAM 여유가 있었다.**
- 이 사실은 사용자가 여러 차례(이번 메시지 기준 네 번 이상) 반복 전달한 **중요한 기존 실험 근거**다.
- **VRAM이 넉넉했음에도** RMIL-04C02 DINOv2-Small Full4,349/K16 Notebook에 **`MICROBATCH_WINDOWS=1`**을 근거 있는 성능/속도 벤치마크 및 사용자 승인 없이 선택해, 불필요한 매우 잦은 DINO Forward 호출과 장시간 GPU 사용을 초래했다.
- 실제 RMIL-04C02 Kaggle 로그: DINOv2-Small K16 **Epoch 1 = 217.14696분** (약 3시간 37분), ResNet34 K16 **Epoch 1 = 46.33401분**. **차이의 전부를 Microbatch 원인이라고 단정하면 안 되지만** 원인을 벤치마크하지 않고 `1`로 고정한 것은 설계 실패.
- **정확성 경계**: 사용자 보고의 "124 이상 Batch"가 어떤 모델/영상 해상도/Full Fine-tuning 여부/Global Batch인지 Window Microbatch인지의 실험 조건은 이 문서만으로 확인되지 않는다. 따라서 "지금 DINOv2-Small K16 Full FT도 무조건 124 장 가능"이라는 주장은 금지. **반대로 VRAM 부족을 아무 근거 없이 가정하는 것도 금지.**

## 2. 절대 금지

1. **성능·시간·메모리를 벤치마크하지 않고 `Microbatch = 1` 또는 임의의 작은 값을 안전하다는 이유만으로 고정하지 않는다.**
2. 기존 배치/메모리 실측 기록을 확인하지 않고 `T4 16GB라서 batch 1일 수밖에 없다`고 단정하지 않는다.
3. `Window Microbatch`(한 번에 Encoder에 넣는 MRI 이미지/Window 수)와 `Study Global Batch`(DDP Gradient 평균 단위)를 혼용하지 않는다.
4. 속도·VRAM·총 예상 실행 시간에 중요한 설정 변경을 사용자에게 알리지 않고 확정하지 않는다.
5. **실측 1 Epoch 추정/실행 시간으로 세션 예산 내 완료 불가**가 예상되는데, GPU를 자동으로 전 Epoch 돌리거나 성능 보장/시간 보장 문구를 쓰지 않는다.
6. 긴 본학습을 시작한 뒤에야 체크포인트 복구 또는 최종 산출물 오류를 발견하게 방치하지 않는다.

## 3. 모든 신규 모델/입력 조합에서 반드시 수행할 사전검사

1. **과거 실험 및 사용자 보고 실측 확인**: 최소한 이 문서의 Batch **124+ VRAM 여유** 기록을 검토. 동등/비동등 실험 조건은 구분해서 적기.
2. **현재 모델의 실제 메모리/속도 탐색**: 동일 데이터 K, 입력 해상도, AMP/FP32, Full FT, DDP, checkpointing 조건으로 대표적인 실제 MRI Studies에서 Window microbatch를 점진 확대하며 **Forward+Backward+Optimizer Step**을 실행. **후보 범위 예시** 4→8→16→32→64→128 이상(메모리 상황이 허용하는 범위에서); 이전 테스트 124+는 탐색을 작게 끝내지 않을 동기이지만 **상한 보증 아님**. 모든 값을 반드시 시험해야 한다는 뜻도 아니며, 무리한 OOM 반복으로 GPU 낭비 금지.
3. **최대 안전 배치 + 처리량 보고**: 각 시험의 실제 VRAM peak allocated/reserved, 필요 시 장치 전체 사용률, seconds/Window, Windows/s, Studies/s, DDP 전체 평균, Activation Checkpoint 비용을 기록. 데이터 HDF5 읽기와 Encoder 병목 분리.
4. **시간 예산 게이트**: 예상 전체 4,349명 × Epoch(5~10) + Gold58 + 최초 검증/Save·ZIP 작업을 GPU 세션 한도와 비교하고, **한도 초과 위험이 있으면 전체 실행을 기본 중단**하고 최적화·복구·계정 예산 계획을 제안.
5. **체크포인트/재개**: 최소 매 Epoch best/last checkpoint 저장 검증, Kaggle 종료/Save Version 뒤 파일 보존 가능성 확인, 실제 resume 시험. 초기에 기능 검증하기.
6. **사용자 확인**: 모델/데이터/유효 Global Batch/메모리 전략/총 시간이 달라지는 중요한 선택은 결과 근거와 함께 사용자에게 명시하고 승인받은 후 장시간 학습 설계 확정.

## 4. Notebook 필수 표기

GPU Notebook 첫 화면 및 최종 인수인계에서 다음을 표기:
- 입력 Dataset·모델·K·학습 인원·마운트 경로.
- **Study Global Batch (DDP)**, GPU당 Study Batch, **Window Microbatch**, AMP, Activation Checkpointing, Grad Accumulation 각각 별도 표기.
- 후보 배치별 벤치마크 결과, 가장 큰 **실제로 검증된 안전 Batch**, VRAM peak, 초/Window, Epoch 예상, 최소/최대 Epoch·총 예상 시간, Kaggle 세션 및 GPU 크레딧 위험.
- Batch를 줄인 경우 **실측 OOM 또는 속도/정확성 근거** 및 사용자에게 보고한 결정 기록.
- 오랜 학습 후 최종 검증 오류를 방지하기 위한 사전 Smoke 2+ Steps, 최종 패키징 dry-run, resume 시험 결과.

## 5. 현재 우선 적용

- RMIL-04C02 **B DINOv2-Small**: 현행 `MICROBATCH_WINDOWS=1`은 **다음 재실행의 합리적인 기본값으로 인정하지 않는다**. 별도 실측 Batch/throughput 비교 없이 그대로 새 장시간 작업을 제안하지 말 것.
- RMIL-04C02 **A ResNet34**: 현행 Window Microbatch=4도 최적값이라고 가정하지 않는다. **이미 정상 진행 중인 GPU 학습은 임의 중단시키지 말고** 다음 실험부터 자원 최적화 반영.
- 라벨 V6는 공식 릴리스 전 `CANDIDATE_NOT_RELEASED` 유지. GPU 설정 최적화는 라벨 승인과 독립적인 문제.

## 6. 인수인계 규칙

새 채팅/코드 작성 에이전트는 **이 문서를 먼저 읽고** 작업해야 한다. 프로젝트가 바뀌거나 모델 크기가 달라져도 **"과거 Batch 124 이상 + 여유 VRAM"**이라는 사용자 보고 기록을 삭제·상쇄하지 말 것. 다만 신규 모델에 동일 Batch 적용 가능 여부는 **반드시 다시 실측**한다.

이 문서는 장기 GPU 자원 운영 정책으로, 특정 Notebook 파일명이나 임시 실험보다 우선한다.
