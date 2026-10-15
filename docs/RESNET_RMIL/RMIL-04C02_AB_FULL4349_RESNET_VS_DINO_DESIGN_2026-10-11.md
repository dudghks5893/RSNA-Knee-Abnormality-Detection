## 2026-10-11 — FINAL CHANGE: DINOv2 Small FIRST (supersedes RMIL-04C02 B Base) + V4/V6 LB stages

**최종 실험 선택:** A = MedicalNet R34 2.5D, **B = DINOv2-Small 2.5D** (Base/large 확대는 마지막). A 기존 노트북 `RMIL-04C02_A_ResNet34_Full4349_V4_K16_T4x2_KO.ipynb` SHA `433cc79e4da7875d2fd0b25d165e27ea4c75828c11ef8c0ffbf905531ef9f94d` 변경 없음. **새 B Small** `RMIL-04C02_B_DINOv2Small_Full4349_V4_K16_T4x2_KO.ipynb` SHA `6b7fdc59b581cf8f9162845c5e02683612ada196ad2efb41af71cd98c4e1f813`, worker SHA `39c650a857fbeb2dc879c80cd46b8e33503abe5efcb8fe4cdc09d55e4814a41b`. Small official 384-dim, 6 heads, 12 layers, patch14, CLS+patch-mean768; Small pretrain SHA `1051e25b2ed69ddad24f3c41e7b6eed6e7f7d012103ea227e47eb82e87dc2050`, Kaggle Model MetaResearch DINO v2 PyTorch **small v1**, backbone upper LR1e-5/LLRD0.8, head1e-4, fp16. Original B Base Notebook **superseded, do NOT execute**.

A/B new ZIP `RMIL-04C02_AB_ResNet_vs_DINOv2Small_Full4349.zip` SHA `ef610daf58976d2f915731380dbd010893436c9275d3244ed08b5c14925c85b9`. Each Kaggle account T4×2 DDP; full Train4349 Gold58-dev, K16 2.5D, confidence & target-balanced V4 loss, max10/min5/patience3. Notebook nbformat/AST PASS; **Kaggle GPU/strict Small pretrained checkpoint load NOT RUN**. **After training:** independent ResNet V4 LB submission then Small V4 LB submission; obtain exact actual Public LB, no invented 0.94. **Later only when V6 formally released**: audit policy/UID+target masks, do NOT treat `not_mentioned/insufficient/uncertain` as negatives, retrain same A/B backbones and submit V6 LB independently; report delta 4-arm matrix. [Full staged execution protocol](RMIL-04C02_SMALL_FIRST_V4_LB_THEN_V6_LB_PROTOCOL_2026-10-11.md). Previous B Base design section below is **historical/superseded**.

---

# RMIL-04C02 — A/B 동시 Full4,349: ResNet34 2.5D vs DINOv2-Base 2.5D

**2026-10-11. Notebook 2개 생성, Notebook AST/nbformat 및 synthetic encoder forward/backward PASS. Kaggle T4 실제 학습 미실행.**

## 이유
사용자 요청: ResNet/DINO 두 계정(A/B)에서 동시 독립 학습; 최대10 Epoch + EarlyStopping; DINO를 ResNet 설정에 억지로 맞추지 말고 DINO 전용 학습 설정 사용; 전체 4,349명에서 질환 불균형과 V4 Confidence 반영. Train300 질환 분포 추가 감사 중단.

## 제공 파일
- `RMIL-04C02_A_ResNet34_Full4349_V4_K16_T4x2_KO.ipynb` SHA256 `433cc79e4da7875d2fd0b25d165e27ea4c75828c11ef8c0ffbf905531ef9f94d`, worker SHA `63f089252310c19f52b73962399ccf5df393f244e99ac2de383cec803eb9e87d`.
- `RMIL-04C02_B_DINOv2Base_Full4349_V4_K16_T4x2_KO.ipynb` SHA256 `cf7f83c08f7791227083007e2800e8188e35a558ff2d284cd08b8051668fb889`, worker SHA `09906571516f8fd7445a16a423280e3e64267312d17cdc5b35d21bfaa3160eec`.
- `RMIL-04C02_AB_ResNet_vs_DINO_Full4349_EarlyStop.zip` SHA256 `202914fde02a7b27bab5376e8d67b708c991a30a0f0dd91411bee8a254168d9c`.

## Shared protocol and release
- User-supplied Kaggle mount `yhlucas/rmil-04b-full-mri-native224-v3`, Pack00 under `results`, Packs01..04 under `results (1)` etc.; same full 190 HDF5 SHA preflight as independently completed RMIL-04C00. Frozen V4 broad `rsna_knee_pseudolabels_v4_routed_broad.csv` SHA `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`, Train4,349 (Gold58 excluded), same K16 centers/Mean, same shared 512-d 2layer-8head metadata CLS Transformer, same Head12, Seed20261013; Gold58 repeated dev only. LABEL-V6 CANDIDATE_NOT_RELEASED **not used**.
- **Each Kaggle account T4×2 NCCL DDP single model**, NOT 4-way single DDP. Global Batch 4 Studies (2 local per rank), dummy 0-grad masked final incomplete group so 4349 real studies per Epoch, gradient sync.
- **Max10, min5, patience3** by Gold58 Macro AUROC; same stop decision broadcast rank0→rank1. Atomic best.pt, last.pt each Epoch; evaluation 58×12, AUPRC secondary, per-target CSV. If interrupted, Kaggle Save Version checkpoint preservation may not occur, and automatic resume is not promised.
- **Confidence:** baseline formula `conf_weight = 0.25 + 0.75 * per_study_target_confidence`. **New separate target class imbalance weight:** only Train4,349 V4 score/conf, `p_t = sum(c_weight * y_t)/sum(c_weight)`; `w_pos_t=clip(.5/p_t,.5,2.5)`, `w_neg_t=clip(.5/(1-p_t),.5,2.5)`; normalize `norm_t=p_t*w_pos_t+(1-p_t)*w_neg_t`; target soft BCE = `[w_pos_t*y_t*softplus(-z_t)+w_neg_t*(1-y_t)*softplus(z_t)]/norm_t` × conf_weight, mean target/Study. This differs from RMIL-02D's confidence-only loss, so **no direct causal old-baseline vs C02 architecture gain interpretation**. The weights file `target_class_weights.json` is saved in both outputs/metadata review ZIP. V4 uncertain pseudo labels still have floor .25, so class balancing may amplify label noise; capped at 2.5 to reduce risk. This is a proposed balancing policy, not empirically proven optimum.
- Gold58 heavily reused; user may compare A/B relative dev performance but final selection needs separate standalone Public LB or independent holdout. Disease-wise winner cherry-picking is not acceptable.

## A / ResNet
- MedicalNet ResNet34 3D weights deflated to 2D, Option A shortcuts, adjacent-three-Slice `[prev,center,next]`, input `uint8/255*10-5`, 224px, full FT, BN running stats frozen.
- `LR backbone=1e-5, head=5e-5, weight_decay=1e-4`, FP32, Window microbatch4; cosine schedule across10 Epoch. Same ResNet RMIL-02D Mean backbone topology except new positive/negative class balancing and training cohort/budget.

## B / DINO
- Kaggle Add **Model** `metaresearch/dinov2`, PyTorch Base v1, historically verified `/kaggle/input/models/metaresearch/dinov2/pytorch/base/1/pytorch_model.bin`, SHA **`014965d9e330e7f4bff8ddcbee9df5e4f2ca032b2f5180942a6edb454783e75d`**. Requires preinstalled `transformers` and strict `Dinov2Model` compatibility, local config.json or known official embedded architecture 518px pos embedding interpolated to 224px / patch14, no downloads (Internet OFF).
- Adjacent-three-Slice as pseudo-RGB, ImageNet mean `[.485,.456,.406]`, std `[.229,.224,.225]` (not MedicalNet -5..5), full FT ViT-B (12 blocks, hidden768), per Window 1, CLS768 + mean patch768 concat1536 projected512, multi-Series shared CLS Transformer.
- DINO layerwise optimizer: ViT last-block LR5e-6, previous layers decay factor0.8 per depth, embeddings factor0.8^12; Head LR1e-4, AdamW WD0.05 except biases/normalization/pos-token; warmup Epoch1 factor.35 and cosine thereafter, FP16 encoder autocast + GradScaler with fp32 head/loss, activation checkpoint to fit T4. All settings are **DINO-oriented prior**, not claimed optimum; B may be substantially slower than A and may exceed Kaggle session time.

## Kaggle Add Input
**Both**: 1 `yhlucas/rmil-04b-full-mri-native224-v3`, 2 `yhlucas/rsna-knee-v4-consensus-dataset`, 3 `rsna-knee-wide224-persistent-cache-v1`; **A** add 4 `yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1`; **B** add 4 Kaggle Model `metaresearch/dinov2` PyTorch base v1.

Save Versions: `RMIL-04C02 A R34 Full4349 K16 EarlyStop T4x2`, `RMIL-04C02 B DINOv2B Full4349 K16 EarlyStop T4x2`. Accelerator GPU T4x2 on each account, Internet OFF, Save & Run All. No global /kaggle/input recursive scan.

## Important status
Neither notebook has been run on live Kaggle T4/NCCL; the actual published DINO model mount/version, library compatibility and true training runtime must be confirmed in the initial live preflight. CPU synthetic forward/backward with stub image encoder was tested for both ResNet/DINO StudyModel wrappers; it is **not** strict pretrained DINO checkpoint load nor GPU training test. Avoid promising completion within session quota.
