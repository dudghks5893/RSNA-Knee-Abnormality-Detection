# RMIL-04C02 — Small First, V4→Public LB→V6→Public LB (2026-10-11)

**최신 사용자 확정 의사결정:** A계정 ResNet34 2.5D, B계정 **DINOv2-Small 2.5D**. 기존 B DINOv2-Base Notebook은 **폐기/실행하지 않음**. 모델 크기(Base/Large/Giant) 증대는 레이블·전처리·학습 설정 개선을 시도한 후 최후순위. A/B V4 전체 학습 후 **각각 별도 Kaggle Public LB 제출**, LABEL-V6가 정식 릴리스되면 **그 라벨로 별도 재학습 후 각 모델 별도 Public LB 재제출**, V4 vs V6 비교.

## 1. 실제 준비 파일 (미실행)

- **A계정 변경 없음:** `RMIL-04C02_A_ResNet34_Full4349_V4_K16_T4x2_KO.ipynb`, SHA256 `433cc79e4da7875d2fd0b25d165e27ea4c75828c11ef8c0ffbf905531ef9f94d`.
- **B계정 Small 신설/기존 Base 대체:** `RMIL-04C02_B_DINOv2Small_Full4349_V4_K16_T4x2_KO.ipynb`, SHA256 `6b7fdc59b581cf8f9162845c5e02683612ada196ad2efb41af71cd98c4e1f813`; embedded worker SHA256 `39c650a857fbeb2dc879c80cd46b8e33503abe5efcb8fe4cdc09d55e4814a41b`.
- A+B Small 및 실행 README ZIP: `RMIL-04C02_AB_ResNet_vs_DINOv2Small_Full4349.zip`, SHA256 `ef610daf58976d2f915731380dbd010893436c9275d3244ed08b5c14925c85b9`.
- Notebook JSON `nbformat.validate` 및 모든 Python cell/embedded worker AST 검증 통과, ZIP CRC/내용 확인. **실제 Kaggle DINO Small checkpoint load, T4×2/NCCL 학습 또는 LB 제출은 아직 실행되지 않았음.**
- Superseded file: `RMIL-04C02_B_DINOv2Base_Full4349_V4_K16_T4x2_KO.ipynb`; **실행 금지**.

## 2. A/B 공통 실험

Full RMIL-04B native 224px 5Pack 한 Kaggle Dataset (`results/RMIL-04B_PACK_00`, `results (1)/RMIL-04B_PACK_01` ... `results (4)/RMIL-04B_PACK_04`). 4,349 Train V4 broad pseudolabels, Gold58 개발 검증 분리, K16 2.5D physical adjacent 3-slice Mean/CLS-Transformer 12 diseases, Confidence BCE floor 0.25 + 질환별 V4 train-only soft-pos/neg capped 0.5~2.5 Loss, max10/min5/patience3, Seed20261013, 각 계정 T4×2 DDP, Internet OFF, Save & Run All. 190 HDF5 files were Kaggle CPU sha-validated in RMIL-04C00, but both new GPU notebook preflights recheck. Gold58은 반복 사용한 dev set, Public LB와 직접 비교 금지.

**B Small specifics (official Meta model config):** 12 encoder layers, hidden **384**, 6 attention heads, patch14, pretrained image size518 interpolated to input224, CLS384 + mean patch384 = **768** feature projection to512; ImageNet normalizer, full finetune ViT, FP16 encoder checkpoint/micro-windows1, backbone top LR **1e-5** layerwise decay factor0.8, head LR1e-4, weight_decay0.05. Verified historical RDINO Small checkpoint SHA256 `1051e25b2ed69ddad24f3c41e7b6eed6e7f7d012103ea227e47eb82e87dc2050`, expected Kaggle Model `metaresearch/dinov2/PyTorch/small/1`, preferred `/kaggle/input/models/metaresearch/dinov2/pytorch/small/1/pytorch_model.bin`, or official alternate `/kaggle/input/dinov2/pytorch/small/1/pytorch_model.bin`, strict hash and strict model state load. Meta Kaggle Small page: `https://www.kaggle.com/models/metaresearch/dinov2/PyTorch/small`. Official HF configuration `https://huggingface.co/facebook/dinov2-small/blob/main/config.json`.

**A-specific Input:** `yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1`. **B-specific Input:** Kaggle Models DINOv2 Small (not Base). **Common 3 Inputs:** RMIL-04B Full MRI cache, V4 pseudo consensus Dataset, old wide224 frozen Gold58 metadata. Each account GPU T4×2 DDP single model.

## 3. Stage plan and strict separation

1. **Stage V4-A/B train:** run A-ResNet and B-DINO Small simultaneously. Keep each `best.pt`, `last.pt` and `results_for_review.zip`, independent integrity+Gold58 AUDIT. Actual T4 training feasibility/time and AUROC not known before live run.
2. **Stage V4-A/B standalone inference + LB:** construct **separate** Kaggle Internet-OFF inference notebooks consuming each saved trained checkpoint and official held-out test DICOM; preserve exactly training's 130mm FOV, Series physical slice order, p0.5/p99.5, 224px uint8, same 2.5D adjacent3+K16 selection, per-backbone normalization/metadata and output 12 target column order. Inspect competition official submission schema/test availability before creating. Submit A and B **separately**, record Public LB each, notebook SHA/checkpoint SHA/Train label version and dev epoch. **Do not assert Public LB 0.94+ until an actual submission**. Any cited Small `0.94+` public example is an external benchmark, not yet reproduced here.
3. **Stage LABEL-V6 formal release gate:** Label V6 remains `CANDIDATE_NOT_RELEASED`. Require explicit official master release, audit/adjudication closure, label-field coverage, data leakage guard and per-study-target label masks/confidence semantics. `not_mentioned`, `insufficient`, `uncertain` do **not** become 0. Construct *masked loss* for known labels only, Gold58 excluded. Confirm what fraction of 4,349 and each target is actually trainable; do not silently convert V6 to V4 format.
4. **Stage V6-A/B retrain+LB:** same model sizes, K16 cache, fixed dataset split, seed/optimizer, training/earlystop policy where meaningful; change supervision to formally released V6 and masked loss. **Report changes in target effective counts/loss policy** because V4 soft scores and V6 categorical/masked judgments are not interchangeable. Submit A and B individually, record Public LB, compare V4/V6 and standalone historical Exp57 Public LB **0.918** using actual common LB metric only, not Gold58 AUROC.
5. If performance plateaus, investigate preprocessing/selection/label quality and well-controlled single variables; **model expansion last**, do not assume larger backbone necessarily improves.

## 4. Caution

Competition test/hidden labels are never to be used as training labels. Multiple LB looks may overfit; preserve transparent sequence and all runs, avoid leaderboard-driven per-target cherry picking. Public LB is not equivalent to independent private-test performance. DDP Global Batch4 same mathematical gradient intent but two model families use different valid backbone-specific hyperparameters, so A/B is end-to-end pipeline comparison, not model-family-only controlled causal effect.
