# RMIL-04C00 완료 검증 / RMIL-04C01 Full4,349 V4 K16 Mean T4×2 DDP 준비

**2026-10-11. RMIL-04C00 Kaggle CPU 실행 및 사용자 산출물 독립검증 PASS. RMIL-04C01 학습 Notebook 작성·정적/합성 검사 PASS, 실제 Kaggle GPU 학습은 미실행.**

## RMIL-04C00 감사 (제출된 결과 ZIP/로그)

- `RMIL-04C00_results_for_review.zip`: SHA256 **`4a2ada496d44501554f510b4f15f7b40df74d11edf3ac8a39e656019a445c322`**; ZIP CRC PASS. 내부 3개 산출물 SHA256 일치.
- Kaggle 로그 최종 상태 **`PASS_FULL_CACHE_AND_V4_SCHEMA_GATE`**, 5.34분 CPU.
- 실제 마운트된 **5개 Pack / 190개 HDF5 shard** 파일을 약 41GB 순차 실제 SHA-256 읽기로 전부 PASS; 과거 Pack별 픽셀 parity 2,006/2,006는 Producer 기록이며 이번 C00에서 재전처리한 것이 아님.
- 전체 **4,407 Studies, 24,371 Series, 819,078 Slices**, 4,349 Train·Gold58 분리. V4 4,349×12 score/conf 모두 숫자형, finite, 0~1, null 0, Gold 분리. K-count: K4 **97,484**, K16 **387,714**, K24 **553,877**, K32 **649,496**. 04A Study/Series/Part 고정 fingerprint 일치.
- 이 결과는 **전처리·라벨 기본 스키마의 검증이지 성능 평가나 정식 임상 라벨 승인 아님**. V4 report-only pseudo labels이고, LABEL-V6는 `CANDIDATE_NOT_RELEASED`로 사용 금지. Gold58은 여러 실험에서 사용된 개발 검증 세트.

## 다음 실행 Notebook: RMIL-04C01

**`RMIL-04C01_Full4349_V4_K16_Mean_DDP_T4x2_KO.ipynb`**, SHA256 **`59f229e8f566143f36f8e8fe0a47d7c1140b47bd2ac88c21451284386d5e279a`**. 별도 포함 Worker Python 소스 SHA256 **`b096595d9f96b33a03427382d742ef5ce0117360189b2250ae2ee0439e4f0049`**. 현 채팅 artifact로 전달, GitHub에 원본 노트북 전체를 직접 커밋한 것은 아님.

**구조**: RMIL-02D K16 Mean 동일 ResNet34 MedicalNet 3D→2D OptionA, 224×224 실제 인접 3-Slice, Window Mean, 512-dim Series/metadata CLS Transformer (2 layers/8heads), 12개 질환 Head, Backbone full fine-tuning. LABEL-V4 `rsna_knee_pseudolabels_v4_routed_broad.csv` 4,349 보고서 기반 pseudo labels 및 per-target `__conf`, loss `BCEWithLogits * [0.25+0.75*confidence]`의 12-target Mean. **Class pos_weight 별도 사용 안 함**. Gold58은 라벨/source 미혼합의 반복 개발 검증.

**훈련 차이점**: Train300 이전 실험을 늘리는 Full-data Stage이므로 Epoch **4회**(기존 Train300 10회가 아닌 새로운 고정 screening budget), cosine backbone LR1e-5, head LR5e-5, AdamW WD1e-4, Seed20261013, FP32, Frozen BN running stats, effective global batch=4 Studies. PyTorch **DDP NCCL rank2** = Kaggle 계정 하나 **T4×2 두 GPU를 하나의 모델에 동시에 활용**, data-parallel split. 4349는 4로 나누어떨어지지 않으므로 마지막 batch에만 0-loss dummy로 mask: 원본 4,349 실제 환자 모두 학습, 마지막 실제 예제에 맞춰 DDP gradient 정규화. `no_sync` forward+backward 포함, sync/gradient clip/All-Reduce loss/Gold58 rank0 평가. 모든 epoch마다 원자적 `best.pt`, `last.pt`, epoch별 metrics/preds/History; 리뷰 ZIP은 checkpoint/4,349 full soft labels/전체 series UID raw 파일을 제외한다.

**Kaggle Add Input 총 4개(정확한 user-supplied mount)**
1. `yhlucas/rmil-04b-full-mri-native224-v3` (1 Dataset, Pack paths not uniform: `results/RMIL-04B_PACK_00`, `results (1)/RMIL-04B_PACK_01`, ..., `results (4)/RMIL-04B_PACK_04`; root `/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/`)
2. `yhlucas/rsna-knee-v4-consensus-dataset`, `rsna_knee_pseudolabels_v4_routed_broad.csv`, SHA pinned `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`
3. `rsna-knee-wide224-persistent-cache-v1` old canonical Gold58 + 358 allseries4 metadata
4. `yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1` `resnet_34.pth`, SHA `977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`.

**Runtime**: GPU T4×2, Internet OFF, Save & Run All. Version name `RMIL-04C01 Full4349 V4 K16 Mean DDP T4x2` (<60char). 예상 수 시간~10시간 이상 가능 **실측 전**. GPU Notebook 시작 시 C00의 SHA/UID/V4 검사를 다시 실행, 190 HDF5 actual SHA 전수 확인 후에 GPU만 동작. **전체 DICOM 직접 디코드 없음**.

**출력**: `/kaggle/working/RMIL-04C01_FULL4349_V4_K16_MEAN/best.pt`, `last.pt`, `training_history.csv`, `gold58_metrics_best.csv`, `gold58_predictions_best.csv`, `training_summary.json`; `/kaggle/working/RMIL-04C01_results_for_review.zip` (모델 제외). 중단될 경우 Kaggle Save Version이 완료된 Epoch 출력을 실제 보존했는지 확인해야 하며 재실행만으로 자동 이어받지 않음. 평가 모델 / 추론 제출 Notebook은 실제 학습 완료 후 설계. Seed 동일해도 학습 표본과 world-size/budget이 달라 Train300과 완전 동일 최적화 궤적 아님.

**테스트 수준:** `nbformat.validate`, 코드 셀/worker AST PASS, CPU synthetic StudyModel forward+encoder gradient PASS, Gloo CPU 2-rank dummy-last-batch gradient sync 테스트 PASS. 실제 Kaggle T4/NCCL, GPU memory/time 및 최종 Public LB는 미검증. Gold58 macro ≠ Public LB 0.918.

**다음:** Notebook Run All → epoch GPU 로그/checkpoint/ZIP 제출 → 실제 결과 독립 감사 → V6 정식 승인 이후 별도 V6 masked supervision 학습/Standalone 제출 의사결정.
