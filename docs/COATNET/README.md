# Branch-B — CoAtNet

이 폴더는 **RSNA Knee 최종 앙상블의 독립 Branch-B(CoAtNet Wide-MRI Expert)** 를 관리한다.

Branch-B는 DINO Stage1→S8C→S10/S11 뒤에 이어 붙는 Stage4가 아니다.  
**Branch-A(DINO Core)와 독립적으로 원본 MRI를 넓게 읽는 두 번째 전문가**다.

## 문서 읽는 순서

새 채팅에서는 아래 두 문서만 먼저 읽으면 된다.

1. [COATNET_BRANCH_PLAN.md](COATNET_BRANCH_PLAN.md) — 목적, 데이터 입력, 전처리, 모델, loss, class imbalance, augmentation, 학습/추론/제출 설계, 실행 순서
2. [COATNET_EXPERIMENT_LOG.md](COATNET_EXPERIMENT_LOG.md) — 실제 실행 결과, checkpoint, SHA, Kaggle 경로, Public LB 누적 기록

공통 프로젝트 상태는 [../CURRENT_HANDOFF.md](../CURRENT_HANDOFF.md)를 본다.

## 현재 상태 — 2026-10-17

- 상태: **TRAIN_READY_V4 / NOT_RUN**
- Branch-A 현재 최고: **S10 LAST 70% + S8C Full-MRI Direct 30% = Public LB 0.926**
- Branch-B 목표: DINO selector와 독립적인 Wide-MRI CoAtNet 전문가를 만들고, standalone 성능뿐 아니라 Branch-A와의 **오류 다양성 / ensemble gain**을 확보한다.
- 안전 실행용 baseline이 목적이 아니다. 처음부터 고득점 가설을 사용한다.
- Wide96 Native384 cache: **4,407 Studies / 4 Pack / full-readback PASS**
- 실제 HDF5 경로와 SHA는 `COATNET_BRANCH_PLAN.md` 최상단에 고정
- supervision: **V4 Routed Broad 고정** (`93863c59...381c`)
- pretrained: user-mounted `coatnet_rmlp_2_rw_384_sw_in12k_ft_in1k.pth`
- authoritative notebook: **B_COATNET_WIDE96_2F_BASE_V4.ipynb** (`45f77cd9...f649f`)
- training mode: **Fold0/GPU0 + Fold1/GPU1 independent, No DDP**
- checkpoint: **Fold별 best.pt만 유지**
- Study batch: **4→2→1 실제 benchmark, effective batch/Fold 16**
- 우선순위: **V4 audited independent 2F Base train → 2F standalone LB → mirror TTA → A+B rank blend**

- V4 execution gate: **actual HDF5 resource probe + 128 real Study throughput projection; >4h blocks before training**
- activation checkpoint: **BN-safe recomputation; BN is not globally frozen**
- V1/V2/V3: **DO_NOT_RUN**
