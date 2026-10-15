# RMIL-04C02 — 독립 ResNet34 / DINOv2-Small Notebook 전면 검수 (2026-10-11)

**상태: Notebook·worker 정적 검사 및 최종 산출물 Dry Run, CPU DDP 수치 테스트 PASS. 실제 Kaggle T4×2 GPU 학습/실가중치 로드는 미실행.**

## 교체 파일 (기존 계정 A/B 표기 Notebook 대신 사용)

- **ResNet34:** `RMIL-04C02_ResNet34_Full4349_V4_K16_DDP_T4x2_REVIEWED_KO.ipynb`, SHA256 `727e9cc646285bdc183246d20b78cdd2baf6988b4ef27e5764e1022c856d79f7`
- **DINOv2-Small:** `RMIL-04C02_DINOv2Small_Full4349_V4_K16_DDP_T4x2_REVIEWED_KO.ipynb`, SHA256 `5147ca7377098dff3438f7b1fb64be84a0550b69d946c2e9b2da44b848ac87e3`
- **ZIP:** `RMIL-04C02_ResNet34_DINOv2Small_INDEPENDENT_REVIEWED.zip`, SHA256 `6950b560aab93c37a43cd0f56a9e2f523e293e3214687931be3f201421c64789`

각 Notebook은 **자기 모델 설명만** 포함하며 계정 A/B 및 다른 모델과의 비교 지시 없음. 독립 Run All, 모델별 결과 경로. Markdown ①~④ 4개 Add Input, 정확한 파일·SHA, 숫자 버전 불확실성 표기.

### Input Version 경고

`rsna-knee-wide224-persistent-cache-v1`은 과거 성공 로그에서 **숫자 버전을 확인할 수 없다**. 숫자 Version을 추측 금지. 이전 RMIL-04C00 PASS Notebook에서 **실제로 사용한 Dataset 입력 버전 그대로 Pin**해야 한다. 필수 `R2D_SHARED224_V1/frozen_manifests/gold58_manifest.csv` SHA256 **`a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`**, `frozen_manifests/train300_manifest.csv`, `allseries4/358 Study JSON` 및 이전 V3 Series 순서/plane embedding 비교 Pass 필요. 조건 만족 시 숫자 버전 무관 동일 입력 계약.

공통: RMIL-04B full MRI 5-Pack single Dataset `yhlucas/rmil-04b-full-mri-native224-v3`, Kaggle real `results`, `results (1)`~`results (4)`, 190 HDF5 shard SHA 전수 검증. V4 broad `rsna_knee_pseudolabels_v4_routed_broad.csv` SHA `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`. ResNet pretrained `yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1/resnet_34.pth` SHA `977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`. DINO pretrained Kaggle Models MetaResearch DINOv2 PyTorch small v1 `pytorch_model.bin` SHA `1051e25b2ed69ddad24f3c41e7b6eed6e7f7d012103ea227e47eb82e87dc2050`.

### Independent safety QA

- `nbformat.validate` and every code cell+embedded worker AST PASS.
- Original post-training assertion/save/export had no prior full mock verification; added **pretraining full finalizer dry-run**: tiny synthetic `best.pt`,`last.pt` saved+reloaded, 5 epochs Gold58 12-target metrics & preds, SHA manifest, review ZIP/CRC/artifact SHA, in a temp directory. Both Notebook extracted finalizer executions **PASS**. During audit discovered & fixed real `NameError: uid` in mock fixture, then re-ran PASS.
- Added **real 2-GPU NCCL smoke BEFORE 10-Epoch training**: load both real pretrained model ranks strictly; real HDF5 2.5D; choose **four largest Train K16 Studies**, spread across ranks (2 each), full forward/backward and optimizer 1 step plus largest Gold58 study inference; `torch.save`/`torch.load(weights_only=True)` checkpoint roundtrip. Fail-fast on GPU OOM/invalid grad/checkpoint mismatch before multi-hour training; smoke itself pending live Kaggle execution.
- CPU Gloo 2-rank DDP math: group sizes **1,3,4** masked dummy batches compared to single-GPU-equivalent optimizer update, max-diff **0..4.66e-10**. `no_sync` spans forward+backward.
- Finalization after training calls **same** dry-run-tested function: training summary schema, epochs5..10, Gold58 predictions/counts/order, best macro AUROC+AUPRC vs target metrics, per-Epoch metrics/preds, both checkpoint SHA & actual `torch.load` and best/last Epoch, full artifact SHA, ZIP CRC and per-file SHA. Checkpoints and Train4,349 raw labels remain OUTSIDE review ZIP.
- Retained Backbone-specific optimizer/normalizers, DDP 2×T4; Full4,349 Train/Gold58 Dev, K16 Mean, max10 min5 patience3, V4 Confidence + train-only per-class clipped loss; **V6 CANDIDATE_NOT_RELEASED** not trained. Runtime or LB are not yet verified. DINO might exceed Kaggle session runtime.

### Execution plan
Notebook each T4×2, Internet OFF, Add Input 4 (listed individually). Run All. New combined output `RMIL-04C02_*_results_for_review.zip` separate per model. Audit each before building separate V4 Public LB inference submission. After LABEL-V6 formal release, retrain masked labels and submit separate Public LB; larger DINO models deferred.
