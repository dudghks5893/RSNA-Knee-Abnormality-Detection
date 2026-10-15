# RMIL-02D 완료 — K16 Mean vs Shared Window Attention; 과거 RMIL 전체 비교

**일자:** 2026-10-10
**상태:** Kaggle 양쪽 T4 GPU 학습 PASS, 결과 ZIP 독립 감사 PASS, Shared Window Attention **성능 개선 실패**, K16 Mean 현 단계 보존.

## 1. 완료된 실험 및 조건

- 데이터: 358명(Train300 / Gold58 개발 검증), 전체 2,006 Series / 66,430 native Slice를 V3 224px 캐시로 전처리; Series별 최대 16개의 인접 3-Slice Window를 선택(총 31,838 Window).
- 정확한 캐시 경로: `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`; HDF5 16 Shard 실제 SHA가 Kaggle 시작 단계에서 전부 PASS.
- 두 Worker 공통: V4 soft+confidence-weighted labels(Train300), Gold58, 의료영상 MedicalNet R34 3D→2D deflation Option-A, full fine-tune, 메타데이터 CLS Transformer(512/2layers/8heads), seed 20261013, AdamW+Cosine, backbone LR1e-5/head5e-5/WD1e-4, FP32, 최대10 Epoch(최소5, Patience3), Window microbatch4/Study accum4.
- GPU0 Mean vs GPU1 Shared Window Attention. Attention은 Series 내 모든 Window에 **하나의 공통 Linear(512→1) 점수**를 사용해 softmax한 후 weighted sum. **12개 질환에 공유**, 질환별 Attention 아님. Attention Linear 가중치를 0으로 초기화해 초기 출력 Mean 동등.
- 두 모델의 공통 초기 가중치 SHA **일치**: `2213f0e06be7e0a5702dcb374d17c6399b19f9bfb476d12fece1b7322786d620`.
- 동일한 RMIL-02C의 K16 Mean과 새로운 RMIL-02D K16 Mean의 **58×12 Gold 예측 CSV 바이트 SHA 동일**, AUROC 0.5778564562010546, AUPRC 0.4322999648458117 및 학습 Epoch별 AUROC 수열 재현. 각 Notebook의 최종 체크포인트 SHA 자체는 다르므로 바이트 동일 체크포인트라는 주장은 하지 않음.

## 2. 역사적 결과 전체 비교

**지표는 AUROC-우선 최적 체크포인트에서 동시 측정한 것**이며 서로 다른 Epoch의 최고 AUROC/AUPRC를 결합하지 않음.

| 실험 | 영상 기준 | K | Pooling | Macro AUROC | Macro AUPRC | Best/Done Epoch | Train 분 |
|---|---|---:|---|---:|---:|---|---:|
| RMIL-01 | **구 캐시** (전처리 상이) | 4 | Mean | 0.576370 | 0.450730 | 4/7 | 9.24 |
| RMIL-01 | **구 캐시** (전처리 상이) | 4 | Shared Attn | 0.544296 | 0.415892 | 3/6 | 8.01 |
| RMIL-02C | **V3** | 4 | Mean | 0.574420 | 0.428417 | 4/7 | 20.92 |
| RMIL-02C | **V3** | 16 | Mean | **0.577856** | **0.432300** | 5/8 | 54.53 |
| RMIL-02C | **V3** | 24 | Mean | 0.577402 | 0.425870 | 3/6 | 55.51 |
| RMIL-02D | **V3** | 16 | Mean (재현) | **0.577856** | **0.432300** | 5/8 | 50.77 |
| RMIL-02D | **V3** | 16 | Shared Attn | 0.564698 | 0.415525 | 9/10 | 63.40 |

**통제 비교:**
- RMIL-01 K4 SharedAttn−Mean = **−0.032074 AUROC, −0.034838 AUPRC** (구 캐시에서만 유효).
- RMIL-02C V3 K16 Mean−K4 Mean = **+0.003437 AUROC**; K24 Mean−K16 Mean = **−0.000454 AUROC**.
- **RMIL-02D V3 K16 SharedAttn−Mean = −0.013157957 AUROC, −0.016775022 AUPRC**; Attention은 Mean보다 총 학습시간 +24.9%(10 vs 8 Epoch), Epoch당 연산·최대 CUDA 할당량은 비슷함.
- RMIL-01과 RMIL-02D에서 Attention의 손실 폭이 다르다고 해서 Window 수가 원인이라는 인과 결론을 내리지 않음(픽셀 전처리·K·실험 환경 상이).

## 3. RMIL-02D 질환별 개별 검증 (ATTN−Mean)

| 타깃 | 양성/58 | Mean AUROC | Attn AUROC | ΔAUROC | Mean AUPRC | Attn AUPRC | ΔAUPRC |
|---|---:|---:|---:|---:|---:|---:|---:|
| ACL | 24 | 0.563725 | 0.542892 | −0.020833 | 0.487028 | 0.436779 | −0.050249 |
| MCL | 9 | 0.512472 | 0.446712 | −0.065760 | 0.172375 | 0.148626 | −0.023749 |
| Medial Meniscus | 26 | 0.735577 | 0.682692 | −0.052885 | 0.725064 | 0.698535 | −0.026529 |
| Lateral Meniscus | 23 | 0.511801 | 0.481988 | −0.029814 | 0.401109 | 0.393460 | −0.007649 |
| Medial OA | 15 | 0.606202 | 0.663566 | +0.057364 | 0.386629 | 0.410188 | +0.023558 |
| Lateral OA | 11 | 0.444874 | 0.520309 | +0.075435 | 0.244097 | 0.238133 | −0.005964 |
| PF OA | 21 | 0.580438 | 0.581725 | +0.001287 | 0.413070 | 0.433275 | +0.020205 |
| Effusion | 35 | 0.750311 | 0.616149 | **−0.134161** | 0.797903 | 0.663232 | **−0.134671** |
| Synovitis | 27 | 0.635603 | 0.636798 | +0.001195 | 0.598949 | 0.599024 | +0.000075 |
| Baker's | 12 | 0.666667 | 0.619565 | −0.047101 | 0.350906 | 0.320570 | −0.030336 |
| Contusion | 19 | 0.421053 | 0.406208 | −0.014845 | 0.295527 | 0.296266 | +0.000739 |
| Fracture | 18 | 0.505556 | 0.577778 | +0.072222 | 0.314943 | 0.348211 | +0.033268 |

AUROC Attention 개선 5/12, 하락 7/12. AUPRC 개선 5/12, 하락 7/12. 개선 타깃은 Medial OA (+0.05736), Lateral OA (+0.07544), PF OA(+0.00129), Synovitis(+0.00120), Fracture(+0.07222). 중요 악화는 Effusion(−0.13416), MCL(−0.06576), Medial Meniscus(−0.05289), Baker's(−0.04710). 특히 Effusion의 악화가 큰 비중을 차지하나 12개 질환 모두 영향이 있는지 개별 평가 필요.

## 4. Attention 집중도 진단

최고 AUROC Epoch9의 Gold58 총 336개 Series에서:
- 유효 Window 수: 평균 **15.7917**개(대부분 K16; 317/336 Series가 16개).
- **실효 Window 수** (1/Σw²): 평균 **12.8882** (중앙값 13.5761). 각 Series 내 상대 유효 Window 비율 평균 **81.81%**.
- 가장 높은 단일 Window 가중치 평균 **0.103947**, 균등 가중치 평균 **0.063667**. 비율을 Series별 계산한 평균 **1.6425배**; 최대 0.4680.
- 정규화 엔트로피 평균 **0.942431** (1=완전 균등, 0=한 Window 독점). 2× 균등 가중치보다 높은 최댓값 Series 비중 약 **19.64%**.
- `window_attention.weight` best 파라미터 L2 norm **0.0169732**, 0은 아님. 따라서 Attention이 학습됐으나 **상대적으로 완만하게 집중했고 예측 성능은 악화**.
- Window 가중치 또는 중심 좌표는 병변 Ground Truth 위치가 아님. 정상/결함 구간 선정이 타당한지 임상적 위치 라벨 없이 판단 불가.

## 5. 검증 및 재현성

- 수령 `RMIL-02D_results_for_review.zip`: **151,880 bytes**, SHA256 `67badca393c11ab7664ca2e8f120e5e93181209a8e96f784bb9bc020377373c8`, **57개 파일 CRC PASS**.
- 각 모델 `artifact_sha256.json` 선언된 **49개 산출물 SHA-256 전부 로컬 독립 재계산 일치**.
- 초기 공통 모델 SHA, 고정 파라미터 계약, 58×12 Gold 예측, 12 타깃 Macro/AUPRC, 최적 Epoch, Attention 진단 Series 336, log/summary **PASS**. K16 Mean 02C→02D 최종 Gold58 예측 CSV 실제 바이트 일치.
- 받지 못한 Kaggle `best.pt` 체크포인트 내용 자체는 로컬 검증하지 않음. Notebook 출력 경로 `RMIL-02D-K16-MEAN/best.pt`, `RMIL-02D-K16-ATTN/best.pt`에 저장된 것으로 로그에 기록; 추후 제출에 재사용할 때 SHA 재검증 필요.
- 모든 점수는 반복 선택에 사용된 작은 **Gold58 개발 검증**. 유의성 검증/독립 시험/실제 Public LB가 아니며, 차이로 완전한 일반화 우열 판단 불가.

## 6. 다음 실험 결정

1. **RMIL-02D 완료·동결.** K16 Shared Scalar Window Attention을 최종 구조에 채택하지 않고, 현 V3 기준 **K16 Mean을 가장 강한 공통 후보로 보존**.
2. **RMIL-03 질환별 Attention**은 독립적으로 실험할 가치가 있으나 대폭 개선을 가정하지 않음. 같은 K16/V3/Train300/Gold58/Backbone/학습 예산을 유지하며 먼저 12개 Target-specific Window Attention, 이어 **Target-specific Window+Series Attention**을 순차 검증. 새 모델에서 질환별 12개 logit aggregation을 명시하고 파라미터/시간 증가 기록.
3. 이미 Gold58을 여러 번 활용했으므로 사후의 질환별 구조/가중치 선택은 과적합 위험. 추후 결과 검증에 반복 Seed·독립 데이터·OOF/전체 4,349학습 등 보강 권장.
4. 이미지 해상도 224→320/384 및 원본 가변 Pixel Spacing 기반 처리 실험은 **별도 변수를 바꾸는 계획**으로 분리하고 RMIL-03 Attention과 동시에 변경하지 않음. 더 고해상도는 원본 DICOM을 다시 디코딩해야 하며 224px 캐시의 단순 업스케일은 원본 정보 복구가 아님.
5. RMIL-04 전체 데이터 학습·공식 Standalone Kaggle 제출 및 필요시 RMIL-05(2D complement), RMIL-06(3D complement) 평가. 기존 Exp57 Public LB 0.918과 Gold58 AUC 0.57 수준은 직접 숫자 비교 금지.

**기록 지침:** 코드성 오류·디버깅 히스토리는 GitHub에 별도 기록하지 않고, 재현 가능한 과학적 결과 및 인수인계만 한국어로 보존.
