# RMIL-03 — K16 Target Window / Series Attention 2×2 실험 완료 및 후처리 복구

**완료일** 2026-10-10 | **상태** 03A/03B/03D/03C 네 GPU 학습 모두 성공; Kaggle Notebook 마지막 후처리 셀은 **오류(OUTPUT_REVIEW_RECOVERED)**. 이 문서는 업로드된 A/B 수동 ZIP 및 로그를 독립 검사하여 복구한 보고서다.

## 1. 고정 조건과 비교 목적

A계정 T4#0 03A Window Mean+Series Mean, T4#1 03B 질환별 Window Attention+Series Mean. B계정 T4#0 03D Window Mean+질환별 Series Attention, T4#1 03C 질환별 Window+Series Attention. A/B 모두 Seed **20261013**, 동일 **전체 초기 State SHA-256** `3b87a5e969a85ffc40d24f6b423e980241b46545f289841aa32c2bab2143e827`, 동일 Worker SHA `f0ec2d32c7d6170041e6de1a62ddcdde98aa721a400f98a6a989c04338502c03`.

입력 V3 Native224 캐시(K16 인접 3-Slice/Series, Train300 V4 soft/conf BCE, Gold58 반복 개발 검증), 358 Study·2,006 Series·66,430 Slice, MedicalNet R34 3D→2D Option-A full FT, 공통 CLS Transformer + 12 질환별 Head, 최대 Epoch10/min5/patience3, AdamW+Cosine, GPU 4개. **RMIL-02C/02D 기존 모델은 Head 구조가 달라 2×2 단일변수 검증은 03 내부에서만 해야 함.**

## 2. 최고 Macro AUROC 체크포인트에서 AUROC/AUPRC

| 모델 | Window | Series | Macro AUROC | Macro AUPRC | Best / Done Epoch | 학습 분 |
|---|---|---|---:|---:|---|---:|
| **RMIL-03A** | Mean | Mean | 0.560367 | 0.418299 | 9 / 10 | 65.08 |
| **RMIL-03B** | Target Window Attention | Mean | **0.562446** | **0.426945** | 2 / 5 | 33.53 |
| **RMIL-03D** | Mean | Target Series Attention | 0.550656 | 0.419531 | 2 / 5 | 35.12 |
| **RMIL-03C** | Target Window Attention | Target Series Attention | 0.560299 | 0.420671 | 2 / 5 | 35.12 |

과거 V3 K16 Mean(02C/02D)은 AUROC **0.577856**, AUPRC **0.432300**. 현재 가장 우수한 공통 V3 실험으로 보존. 과거 RMIL-01은 영상 픽셀 전처리 달라 직접 우열 비교 제외.

| 통제 비교 | Δ AUROC | Δ AUPRC |
|---|---:|---:|
| 03B−03A Window 효과 (Series Mean) | +0.002079 | +0.008646 |
| 03D−03A Series 효과 (Window Mean) | −0.009710 | +0.001232 |
| 03C−03B Series 추가 (Window Attention) | −0.002147 | −0.006274 |
| 03C−03D Window 추가 (Series Attention) | +0.009643 | +0.001140 |
| **상호작용 (03C−03D)−(03B−03A)** | +0.007563 | −0.007506 |

위 값은 **각 모델이 Gold58에서 개별 선택한 서로 다른 최적 Epoch**에서 나온 탐색적 비교이다. 충분한 통계적 재현성·독립 검증·인과적 상호작용 유의성을 증명하지 않는다. 03B는 새 Head 내부에서 가장 좋은 전체 Macro이나, 기존 RMIL-02D K16 Mean에는 미달. **03C를 최종 구조로 채택하지 않음.**

## 3. 12개 질환별 Gold58 AUROC

| Target | 양성 | 02D K16 Mean | 03A | 03B | 03D | 03C |
|---|---:|---:|---:|---:|---:|---:|
| ACL | 24 | 0.5637 | 0.5147 | 0.4877 | 0.4779 | 0.4779 |
| MCL | 9 | 0.5125 | 0.4376 | 0.3832 | 0.4059 | 0.4286 |
| Medial Meniscus | 26 | 0.7356 | 0.7067 | 0.6815 | 0.7127 | 0.6526 |
| Lateral Meniscus | 23 | 0.5118 | 0.5478 | 0.5602 | 0.4807 | 0.5702 |
| Medial OA | 15 | 0.6062 | 0.4760 | 0.4992 | 0.5473 | 0.5674 |
| Lateral OA | 11 | 0.4449 | 0.5106 | 0.5957 | 0.6054 | 0.5068 |
| PF OA | 21 | 0.5804 | 0.5084 | 0.5598 | 0.4659 | 0.5663 |
| Effusion | 35 | 0.7503 | 0.7056 | 0.7019 | 0.7118 | 0.7205 |
| Synovitis | 27 | 0.6356 | 0.6057 | 0.6583 | 0.6165 | 0.6738 |
| Baker's | 12 | 0.6667 | 0.6322 | 0.5906 | 0.6087 | 0.5996 |
| Contusion | 19 | 0.4211 | 0.4359 | 0.4103 | 0.3819 | 0.4265 |
| Fracture | 18 | 0.5056 | 0.6431 | 0.6208 | 0.5931 | 0.5333 |

일부 타깃에서 03A~C/D가 기존 모델을 이겼으나 **Gold58 기반 사후 모델 선별은 선택편향 위험**. 질환별 특정 최고값만 채택하지 말 것.

## 4. Attention 실제 학습 확인

- 03B Window: GOLD 336 Series×12=4,032 기록, 실효 Window 평균 **11.493**, 최고 가중치 평균 **0.1741**, 평균 Entropy **0.8799**.
- 03D Series: GOLD 58 Study×12=696 기록, 실효 Series 평균 **4.376**, 최고 가중치 **0.3744**, Entropy **0.8553**.
- 03C Window: 4,032기록, 실효 **10.947**, 최고 가중치 **0.1796**, Entropy **0.8765**.
- 03C Series: 696기록, 실효 **4.289**, 최고 가중치 **0.3906**, Entropy **0.8244**.
- 가중치 합·범위·타깃별 개수는 기록 내 무결성 PASS. 가중치 자체가 병변 위치의 정답이라는 의미는 아니다.

## 5. 마지막 Notebook 오류 — 학습 문제 아님

두 계정 모두 최종 후처리 Cell에서:
```python
for key,val in configs[control].items():
    if key not in ('experiment','pooling','attention','series_aggregation'):
        assert val == configs[treatment][key], ('설정 불일치', key)
```
**`initial_forward_logits`**가 허용오차 없이 정확 비교된 것이 문제. 네 모델 공통 초기 State SHA는 일치하며 네 모델 간 최초 12-logit **최대 절댓값 차이 1.78814×10⁻⁷**. 이는 32bit GPU 부동소수점 차이 규모. 수정은 config 정밀 비교에서 `initial_forward_logits`를 **제외**하고 별도:
```python
init_a = np.asarray(configs[control]['initial_forward_logits'], dtype=np.float64)
init_b = np.asarray(configs[treatment]['initial_forward_logits'], dtype=np.float64)
assert init_a.shape == init_b.shape == (12,)
assert np.allclose(init_a, init_b, rtol=0, atol=2e-5)
```
변경 후 **학습 재실행 불필요**, 기존 학습 결과에 대해서만 후처리 다시 하면 됨. 원래 셀 이후 Bootstrap CI·최종 ZIP 자동 출력은 발생하지 않았으며, 사용자가 직접 Output을 다운로드해 만든 ZIP으로 복구 분석함.

## 6. 독립 무결성 감사 및 남는 한계

- A 수동 ZIP **SHA256 `3bdc97da8cf514500b77c7db254bf464353af597e9f127e11cf880319f385721`**, B 수동 ZIP **SHA256 `07468b84b83a91dc390254e8404baf4e99e4f6d8534a0331bd8af478a2c689e6`**. Mac `__MACOSX`/보조파일 제외 실제 주요 파일 **A53/B45**, ZIP CRC PASS.
- 네 `artifact_sha256.json`에서 확인한 모델별 **26 + 17 + 17 + 18 = 78개** 선언 파일 **SHA256 일치**, 누락/불일치 0. 네 모델 최초 State SHA, Seed, 58×12 예측 형식, 최고 Epoch CSV와 최종 CSV 동일성, 최적 Epoch History 및 질환별 지표 평균=Macro 일치.
- **직접 검증하지 못한 것:** 사용자 ZIP에는 `best.pt` 실제 바이트가 없으므로 Kaggle Notebook Output 체크포인트 SHA 실제 검증 불가(Worker 로그에는 성공한 모델 SHA 기록). 독립 Gold58 정답 Manifest도 ZIP에 없어 **실제 골드 라벨에서 AUROC/AP를 원천 재계산하거나 Bootstrap CI를 독립 재생성하지 못함**. 이 제한을 넘어서 PASS라고 선언 금지.
- 기존 예측·Checkpoint는 수정하지 않으며 결과는 **Gold58 반복 개발 검증**, Public LB나 임상적 검증이 아니다. LABEL-V6 **CANDIDATE_NOT_RELEASED** 유지, V4 라벨 사용.

## 7. 후속 계획

**RMIL-03 4개 구조 탐색은 학습 완료로 동결**. 현재 **K16 Mean RMIL-02D를 공통 기준으로 유지**, 03B는 추가 데이터에서 재검증할 탐색 후보. 반복 Gold58 선택을 줄이고 V4/V6 라벨 승인/품질·Train300 규모 개선·독립 평가·이후 RMIL-04 전체 학습 여부를 검토. 해상도/원본 Pixel Spacing 실험은 다른 변수로 별도 진행. 본 문서에 단순 디버깅 사건을 별도의 독립 실험으로 기록하지 않음.
