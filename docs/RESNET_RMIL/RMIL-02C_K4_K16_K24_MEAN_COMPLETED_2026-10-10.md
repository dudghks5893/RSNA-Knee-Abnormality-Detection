# RMIL-02C 완료 — K4·K16·K24 Mean 성능 비교

**실험일:** 2026-10-10  
**최종 상태:** K4·K16·K24 모두 PASS / T4×2 병렬·순차 사용 / Gold58 반복 개발 검증

## 핵심 결론

**K16이 AUROC와 AUROC 최적 체크포인트의 AUPRC에서 모두 최고.** 다만 K4 대비 Macro AUROC 개선은 **+0.003437**에 불과하고 K24가 K16을 앞서지 못함(-0.000454). K4 대비 Window를 4배/6배 늘려도 현재 **Series별 단순 Mean pooling에서는 유의미한 대폭 개선의 근거가 부족**. 질환별 방향은 달라 이후 같은 K에서 Window Attention을 비교할 과학적 근거는 있으나, **Attention이 반드시 개선한다는 주장은 하지 않음**. 골드 검증 58명은 반복 사용한 소규모 개발 검증이고 일반화/독립 테스트/LB가 아님.

## 입력·모델 통제

- 캐시: `rmil-02b-native224-v3`; 정확한 마운트 `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`. 358명/2,006 Series/66,430 Slice, HDF5 영상 샤드 **16개 전체 파일 SHA-256 전부 Kaggle에서 재검증 PASS**. 새 V3 영상 전처리 기준이라 RMIL-01의 K4 점수 0.57637044와 직접 비교 금지.
- V4 Train300 soft label + confidence weighted BCE, Gold58 12타깃, 전체 Series·유효 Slice Triplet; K4 ⊆ K16 ⊆ K24의 중첩 선택으로 Window 수만 변경.
- MedicalNet 3D→2D deflated ResNet34 Option-A, full fine-tuning, 기존 메타데이터 CLS Transformer 512/2layer/8heads, Mean pooling, seed20261013, AdamW, cosine, backbone LR 1e-5, head LR 5e-5, WD 1e-4, 최대10 Epoch / 최소5 Epoch / patience3, Window microbatch4, 4 Studies gradient accumulation, FP32. GPU0 K4→K16, GPU1 K24.
- 제출 자료 `RMIL-02C_results_for_review.zip` 수령 SHA256 `9c9c577a02c7a819171802bed532f893b8778fa9c3e1a39f3a340d8ec478a13f`, **70개 ZIP 항목 CRC PASS**, 각 모델의 manifest에 기재된 **60개 산출물 SHA-256 모두 독립 재계산 일치**, 최적 Epoch·Macro 수치·58×12 예측·조건 계약 자체 검증 PASS.
- Checkpoint `best.pt`는 수령 ZIP에 포함되지 않음. Kaggle Output 개별 모델 폴더에 보존됨을 실행 로그로 확인; 별도 체크포인트 바이트를 로컬 독립 검증했다고 주장하지 않음.

## 주요 수치 — AUROC 최고인 Epoch의 체크포인트 기준

| 지표 | K4 | K16 | K24 |
|---|---:|---:|---:|
| 실제 전체 Window | 8,024 | 31,838 | 45,472 |
| Gold58 Macro AUROC | 0.574420 | **0.577856** | 0.577402 |
| Gold58 Macro AUPRC | 0.428417 | **0.432300** | 0.425870 |
| AUROC 최고 Epoch | 4 | 5 | 3 |
| 학습 완료 Epoch | 7 | 8 | 6 |
| 학습 시간(분) | 20.917 | 54.529 | 55.505 |
| Epoch 평균 시간(분) | 2.988 | 6.816 | 9.251 |
| GPU 최대 할당 메모리(GiB) | 0.689 | 0.767 | 0.823 |
| 학습 마지막 Loss | 0.381633 | 0.381820 | 0.384620 |
| 조기 종료 | YES | YES | YES |

증감: K16-K4 AUROC **+0.0034368393**, AUPRC **+0.0038832013**; K24-K4 AUROC **+0.0029828215**, AUPRC **−0.0025471902**; K24-K16 AUROC **−0.0004540178**, AUPRC **−0.0064303915**. 완주 학습시간은 K4 대비 K16 **2.61배**, K24 **2.65배**이며, Epoch당 비용은 각각 **2.28배, 3.10배**.

**주의 — AUPRC 자체 최대 Epoch와 최고 AUROC Epoch는 다름.** K4는 AUPRC 최대 Epoch3 = **0.432281** (이때 AUROC 0.571835), K16 최대 Epoch6 = **0.436264** (AUROC 0.577483), K24 최대 Epoch6 = **0.436695** (AUROC 0.573134). 공식 best.pt 저장 규칙은 Macro **AUROC 우선**이며, 상단 최적 체크포인트 비교에서 K24 AUPRC 0.425870이 맞다. K24의 Epoch6 AUPRC 0.436695를 Epoch3 AUROC 0.577402와 결합해 가상의 최고 성능을 만들면 안 됨.

## 질환별 AUROC

| 질환 | Gold58 양성수 | K4 | K16 | K24 |
|---|---:|---:|---:|---:|
| ACL | 24 | 0.5686 | 0.5637 | 0.5539 |
| MCL | 9 | 0.5102 | 0.5125 | 0.4717 |
| Medial Meniscus | 26 | 0.7067 | 0.7356 | 0.7284 |
| Lateral Meniscus | 23 | 0.5329 | 0.5118 | 0.4969 |
| Medial OA | 15 | 0.6605 | 0.6062 | 0.7535 |
| Lateral OA | 11 | 0.4178 | 0.4449 | 0.4526 |
| PF OA | 21 | 0.5740 | 0.5804 | 0.5817 |
| Effusion | 35 | 0.6981 | 0.7503 | 0.7230 |
| Synovitis | 27 | 0.6081 | 0.6356 | 0.5914 |
| Baker's | 12 | 0.6649 | 0.6667 | 0.6703 |
| Contusion | 19 | 0.4359 | 0.4211 | 0.4305 |
| Fracture | 18 | 0.5153 | 0.5056 | 0.4750 |

각 K가 12개 중 **4개 질환씩** AUROC 최고. K16 vs K4 상승 7/12; K24 vs K4 상승 6/12; K16 vs K24 상승 7/12. 최대 변화 예시: **K16 Effusion +0.05217**; **K24 Medial OA +0.09302**(K16보다 +0.14729); K24 **Fracture −0.04028**, **Lateral Meniscus −0.03603**(모두 K4 대비). 질환별 유리한 K가 다르고 표본 작음(최소 MCL 양성9, Lateral OA 양성11), 사후 질환별 모델 선택은 과적합 위험.

## 질환별 AUPRC

| 질환 | K4 | K16 | K24 |
|---|---:|---:|---:|
| ACL | 0.4721 | 0.4870 | 0.4776 |
| MCL | 0.1862 | 0.1724 | 0.1572 |
| Medial Meniscus | 0.7023 | 0.7251 | 0.7306 |
| Lateral Meniscus | 0.4250 | 0.4011 | 0.3773 |
| Medial OA | 0.3907 | 0.3866 | 0.4746 |
| Lateral OA | 0.1960 | 0.2441 | 0.1986 |
| PF OA | 0.4127 | 0.4131 | 0.4072 |
| Effusion | 0.7249 | 0.7979 | 0.7462 |
| Synovitis | 0.5843 | 0.5989 | 0.5867 |
| Baker's | 0.3623 | 0.3509 | 0.3706 |
| Contusion | 0.3271 | 0.2955 | 0.2866 |
| Fracture | 0.3573 | 0.3149 | 0.2973 |

AUPRC 최고 질환 수: K4 **4**, K16 **5**, K24 **3**. K16이 K24를 12개 중 **9개 질환에서** AUPRC로 앞섬. 그러나 Medial OA는 K24가 큰 우위.

## 학습 해석

- Train Loss는 모든 K에서 내려갔지만 AUROC는 K4 Epoch4, K16 Epoch5, K24 Epoch3에서 최고를 기록한 뒤 정체/하락. 단순 데이터 증가가 안정적 일반화로 이어진 것은 아님.
- 2.5D Window가 늘면 병변 없는 Window까지 단순 Mean에 포함될 수 있어 국소 질환 신호가 약해지는 **가능한 기전**. 이번 결과만으로 기전의 인과성이 증명된 것은 아님.
- 질환별 표본수와 반복된 Gold58, Epoch별 최적 체크포인트 선택을 고려해 작은 Macro AUROC 차이를 통계적으로 유의하다고 판단할 근거 없음. Public LB / 숨겨진 Test 점수로 환산 금지.

## 후속 결정

1. **RMIL-02C 완료·동결.** 전역 공통 K의 다음 통제 실험 우선 후보는 **K16**: 같은 V3 이미지·선택 기준·MedicalNet R34·Optimizer·Seed에서 K16 Mean vs K16 **shared scalar Window Attention**. K16 Mean의 기존 결과는 기준으로 보존하되 새 ATTENTION 실험과 실행 조건 차이를 엄격히 관리.
2. K24는 Medial OA에서의 특이적 이점을 발견한 탐색적 결과로 보존; K24로 즉시 전면 확대하거나 질환별 모델을 사후 조합해 Gold58에 과적합하지 않음.
3. RMIL-02D 완료 이후 RMIL-03 질환별 Window 및 Series Attention을 계획. 가능하면 반복 seed, 독립 홀드아웃/교차 검증과 더 큰 Train을 통한 안정성 확인.
4. Kaggle Output의 `RMIL-02C-K4/best.pt`, `-K16/best.pt`, `-K24/best.pt`를 유지. 재사용 전 해당 파일 SHA 검증 필요.

