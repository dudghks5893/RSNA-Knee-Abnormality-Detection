# S8 — Strict-FT Full-MRI MIL A/B Public LB 결과 (2026-10-16)

## 상태 및 증거 구분

- **결과:** 사용자가 Kaggle 제출 후 직접 공유한 Public LB: **S8A Mean 0.918**, **S8B Attention 0.923**.
- 이 문서는 사용자가 보고한 점수를 기록한다. Kaggle Private LB, 숨겨진 전체 테스트의 원시 예측값, 제출 버전 ID 등은 아직 독립적으로 확인하지 않았다.
- V1/V2 제출 시 Hidden-Test `Notebook Threw Exception` 발생. 성공 점수는 Hidden-Test 방어 로더/Series 스트리밍을 추가한 **V3_HIDDENFIX** 재제출 결과다.
- 2026-10-16 기준 연구/제출 기록이며, 리더보드 수치는 제출 시점의 사용자 보고값이다.

## Public LB 비교

| Run | 추론 구조 | Public LB | 이전 B2 대비 |
| --- | --- | ---: | ---: |
| B2 Full-MRI Hierarchical MIL (기존) | Full MRI, hierarchical disease-specific Window/Series Attention, 기존 Fold2 encoder | 0.904 | — |
| **S8A MEAN** | Strict-FT Fold0/1 encoder → all-window CLS+PatchMean → Mean MIL → 2-Fold probability mean | **0.918** | **+0.014** |
| **S8B ATTN** | 동일 encoder/전처리 → disease-specific Window Attention MIL + Series Mean → 2-Fold probability mean | **0.923** | **+0.019** |

- **A 대비 B:** +0.005 Public LB.
- 역사적 Exp57 Public LB 0.918 대비 B +0.005 (비교용 기록, 입력/모델/학습 조건이 통제된 실험은 아님).
- 현재 확인된 이 프로젝트 제출 기록에서 **S8B가 최고 Public LB 0.923**.

## 아키텍처 및 재현 입력

두 실행은 다음 전처리/feature extraction을 공통으로 사용한다.

1. Competition Test의 모든 사용 가능한 MRI Series를 처리. 기본적으로 Series 길이 `n ≥ 3`에 대해 모든 유효 center `1..n-2`에서 인접 3-Slice Window를 생성; Test 장애 대응 fallback은 아래 참조.
2. **RMIL04B_NATIVE224_V3** 계약: 130 mm FOV 물리적 중앙 crop, Series 단위 0.5/99.5-percentile clipping, z-score 및 [-5,5] clip, 224x224 uint8, ImageNet normalization.
3. Strict-FT DINOv2-Base Fold0/1 `last.pt` **각각**으로 1536차원 `CLS(768) + Patch Mean(768)` 특징 추출. 중간 특징은 S7 FP16 캐시 저장 정밀도를 한 번 재현.
4. Fold0 특징은 Fold0 MIL, Fold1 특징은 Fold1 MIL에 입력; Fold 사이의 특징 공간을 직접 결합하지 않음.
5. Fold별 12질환 sigmoid 확률을 평균해 `submission.csv` 생성.

**Strict FT checkpoint root**
`/kaggle/input/datasets/woniyeon/rsna-knee-s1ft02-b-v4strict-2fold-best-v1`

- `fold0/last.pt` SHA-256: `b4e7d29d3ae0e7ff999c3fb0119dc6126ddd5d5a006c69868818bc440c895aa4`
- `fold1/last.pt` SHA-256: `966fdfe174c995bfbd8855b520440c508a6aa8539eee9cb5a5f724402b538d79`
- 원본 DINOv2 Base weights SHA-256: `014965d9e330e7f4bff8ddcbee9df5e4f2ca032b2f5180942a6edb454783e75d`

**S8A Mean MIL**
- checkpoint root: `/kaggle/input/datasets/yhlucas/s8-mil-mean`
- Fold0 `best.pt` SHA-256: `7c5ff6743b1c525f47a9adb9dc8613056eba602315f465675e1b33e97378310b` (epoch 3)
- Fold1 `best.pt` SHA-256: `12cbb9fb2771305fac37c9901afcf04d3faa28de89daf6df9c1de730d4623c9b` (epoch 3)
- pooling: each Series Window Mean → Series Mean → 12-target classifier.

**S8B Attention MIL**
- checkpoint root: `/kaggle/input/datasets/woniyeon/s8-mil-attn`
- Fold0 `best.pt` SHA-256: `0bbe9d1b532cc933ca346e426c612abf7cbf388e991baa0875f14986e3176770` (epoch 1)
- Fold1 `best.pt` SHA-256: `e52b42565c79476ce342c75e76be078077a8c94fa88e31ee361408e6b0fd3615` (epoch 3)
- pooling: disease-specific Window Attention **within each Series** → Series Mean (질환별 Series Attention은 아직 없음) → disease-specific head.

**V3 Kaggle Run settings**

- Accelerator: **T4 x2**, Internet: **OFF**, Save & Run All.
- A Save Version 권장/실험 ID: `S8-MEAN-MIL-LB-2F-V3-HIDDENFIX`
- B Save Version 권장/실험 ID: `S8-ATTN-MIL-LB-2F-V3-HIDDENFIX`
- V3 Hidden-Test 대응: `sample_submission.csv` Study 순서 보존, DICOM `force=True`, IOP/IPP→InstanceNumber→filename 정렬 fallback, 손상 Slice 근접 정상 Slice 대체, 1~2 Slice edge replication, Series 단위 추론으로 RAM 절약, GPU0 Fold0/GPU1 Fold1 parallel feature extraction, 보정/제외 로그. 임의 0.5 대체 제출은 없음.
- Kaggle 공개 Test 3 Studies / 15 Series V3 `SUBMISSION_SUCCESS`; A/B 모두 공개 Test에서 `parallel_feature_fallbacks=0`, `series_failed_total=0`, `decode_errors_total=0`. Hidden Test의 fallback 상세 통계는 제공되지 않음.

## Gold58 연구 지표 — LB와 혼동 금지

| Run | Gold58 pooled Fold29/29 diagnostic Macro AUROC | Public LB |
| --- | ---: | ---: |
| S8A Mean | 0.894883 | 0.918 |
| S8B Attention | 0.877599 | 0.923 |

- Gold58에서는 **A > B**, Public LB에서는 **B > A**였다. 소규모 개발 검증 데이터와 Public LB 간 순위가 뒤집혔음을 기록한다. 이것만으로 어느 쪽이 Private LB에서도 우수하다고 결론 내릴 수 없다.
- Strict FT encoder 자체가 반대편 Gold29를 학습했으며 MIL `best.pt`는 자신의 Fold Gold29로 epoch 선택되었다. 그러므로 pooled Gold58는 MIL head의 OOF 형태이지만 **전체 파이프라인의 독립·편향 없는 holdout 점수는 아니다**.

## 후속

1. **S8B (0.923)** 기준으로 disease-specific attention 활용 가능성을 확인.
2. S8C Hierarchical MIL(Window + Series attention)을 실험하되, S8A/B 공통의 Fold-specific DINO encoder와 전처리 계약을 유지하여 모델 통합 구조만 통제 비교.
3. 질환별 Window/Series importance 추출 시 ranking 신뢰도 및 추출 정책을 별도 검증. Attention weight만으로 실제 병변 위치를 확정하지 않음.
4. Public LB에 대한 반복적인 튜닝은 과적합 위험이 있으므로 고정 검증과 상호 비교를 병행.

## 기록 변경 이력

- **2026-10-16:** 사용자 보고 S8A 0.918 / S8B 0.923 추가. 이전 B2 0.904 및 Gold58 진단과 함께 보존.
