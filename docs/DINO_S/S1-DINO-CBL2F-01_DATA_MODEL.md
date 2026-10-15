## 2026-10-16 — S7/S8 최신 Fold별 모델·영상 입력 계약

- **Stage1 Strict-FT DINOv2-Base**: Train Pseudo4,349 + Gold29 각 Fold, 다른 Gold29 검증. Study당 **18×(3 인접 Slice) Window**, 사용 가능한 모든 Series에 분산, 중심 20~80% 후보. 
- **S7**: 고정된 Stage1 Fold별 Encoder로 전체 4,407 Studies, 24,371 Series, 819,078 원본 Slice 중 유효 center 1..n−2에서 770,336개 3-Slice Window를 Fold별 1536-d (CLS768 + PatchMean768, fp16) 특징으로 추출.
- **S8A**: 전체 Window→Series 내 Mean→Series Mean MIL→Fold별 sigmoid 확률 평균, Public LB **0.918**.
- **S8B**: 전체 Window→질환별 Window Attention→Series Mean MIL→Fold별 sigmoid 확률 평균, Public LB **0.923**. **질환별 Series Attention은 미사용**.
- **Strict FT checkpoints:** `/kaggle/input/datasets/woniyeon/rsna-knee-s1ft02-b-v4strict-2fold-best-v1/fold{0,1}/last.pt`; Fold0 SHA256 `b4e7d29d3ae0e7ff999c3fb0119dc6126ddd5d5a006c69868818bc440c895aa4`, Fold1 `966fdfe174c995bfbd8855b520440c508a6aa8539eee9cb5a5f724402b538d79`.
- **S8A MIL** `/kaggle/input/datasets/yhlucas/s8-mil-mean/fold{0,1}/best.pt`; Fold0 SHA `7c5ff6743b1c525f47a9adb9dc8613056eba602315f465675e1b33e97378310b`; Fold1 `12cbb9fb2771305fac37c9901afcf04d3faa28de89daf6df9c1de730d4623c9b`.
- **S8B MIL** `/kaggle/input/datasets/woniyeon/s8-mil-attn/fold{0,1}/best.pt`; Fold0 SHA `0bbe9d1b532cc933ca346e426c612abf7cbf388e991baa0875f14986e3176770`; Fold1 `e52b42565c79476ce342c75e76be078077a8c94fa88e31ee361408e6b0fd3615`.
- Kaggle T4×2, Internet OFF, V3_HIDDENFIX 일반 공개 Test 3 Studies/15 Series `SUBMISSION_SUCCESS`; 점수는 사용자 보고. Gold58 반복 개발 검증 자료이지 독립 Test가 아님.

---

# S1-DINO-CBL2F-01 — 데이터·모델 기준 명세 (누적 관리)

- **실험 ID:** `S1-DINO-CBL2F-01` (2026-10-13 신규; 기존 GitHub 파일명/코드 검색에서 중복 미발견)
- **목표:** DINOv2-Base Stage1 지도 Fine-tuning을 STRICT V1과 V4 라벨 정책으로 비교하고, 이후 Full-MRI 특징 캐시·질환별 MIL·Top-K Selector로 확장.
- **운영:** 이 실험군의 Markdown은 본 문서(DATA_MODEL), ROADMAP, EXPERIMENT_LOG **3개만** 만들고 계속 편집한다. 실험·버그·노트북 버전마다 .md 신설 금지.
- **최신 실행 상태(2026-10-13):** A/B Stage1 2-Fold TRAIN 완료 및 Gold58 OOF 재계산 확인. LB V2 Notebook 정적 QA 완료 후 사용자 보고 Public LB A=0.861/B=0.910 수신(실제 제출 스크립트 독립 감사 미완료). 이후 섹션의 V6/V7 미검증 문구는 당시 이력이다.
- **출처:** 로컬 공개된 A/B V6 노트북, 사용자 제공 STRICT/V4 원본 ZIP, Gold58 사용자 제공 정답, 기존 GitHub cache 명세. 최신 노트북 설정이 바뀌면 해당 변경 이력과 SHA를 이 문서에 갱신.

## 2026-10-13 — 실제 PREFLIGHT 오류 수정: V7 WorkerFix

- **새 노트북:** A `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb` (SHA256 `e603978948c0d6d378385105b1b3d8088e8771b3f40e5f53b66d838d1f31e1c0`), B `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb` (SHA256 `5e99513024329483cacc114fb814f83b35b06dfd924705b744451d18c458a84c`).
- V6에서 `worker_path` 미정의로 `subprocess.Popen` 이전에 `NameError` 발생. V7은 Worker 문자열을 `/kaggle/working/STAGE1_DINO_<LABEL>_DUALFOLD/stage1_<label>_worker.py`에 기록하고, 파일 존재·크기·AST를 검증 후 Fold0/1 실행.
- 양쪽 V7은 notebook nbformat/AST, embedded Worker AST, 파일 생성/읽기, 독립 2-프로세스 **CPU mock-launch PASS**. 실제 Kaggle T4×2 PREFLIGHT / TRAIN 아직 미검증.
- **그 외 Label, Loss, Class Balancing, Gold, 모델, Batch 및 Hyperparameters 모두 V6과 동일.** B에도 동일한 V6 결함이 있어 B 노트북도 교체해야 한다.
- V6 파일은 과거 입력 버전 참조용이며 현재 실행 추천 파일은 **V7**이다.

## 1. 공통 데이터 파이프라인

```text
공통 MRI cache: 4,407 Studies = pseudo train 4,349 + Gold58
24,371 Series / 819,078 Slice (총 5 Pack, 190 HDF5 shards)
  -> 물리 위치에 따라 Slice 정렬, 130mm 중심 Crop, Series별 정규화
  -> Native224 V3 uint8 224×224 슬라이스
  -> 이웃 Slice [center-1, center, center+1] 3채널 Window
  -> 1 Study당 18 Window/epoch, 각 Series 포함, center 대략 20~80% 범위 순환 선택
  -> Meta DINOv2-Base CLS768 + PatchMean768 = 1536차원
  -> Stage1 학습용 Projection256 + 타깃별 Window Attention + 12 logits
  -> Study 단위 BCE Loss (Window별 환자 라벨 복제 학습 금지)
```

- **공통 캐시:** `yhlucas/rmil-04b-full-mri-native224-v3`
  - `/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results/RMIL-04B_PACK_00`
  - `/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results (1)/RMIL-04B_PACK_01` ... `results (4)/RMIL-04B_PACK_04`
  - 각 Pack의 `series_index.csv`, `shard_sha256.csv`, `run_status.json`, `shards/*.h5` 등. 기존 RMIL-04C00 190/190 SHA 확인 이력은 존재하지만 **이번 A/B 원격 마운트 검증은 별도**.
- **공통 Series/Sampler:** `yhlucas/stage1-dino-shared-input-manifest-v1`
  - `common_series_manifest.csv`: 24,371 Series; SHA256 `e77023a00103f38dd53f6eb62fb142cf3358e0fc4acfe0b85d908c2c190939ea`.
  - `sampler_reference.py`: SHA256 `8ce97e7cebf0c75597e6bd8ea8c262bfb6596dfdcbf0975b8d31101fe125052c`.
  - 중앙 유효 Center 후보 483,096개; Stage1 18개/Study/Epoch는 **전체 Slice나 전체 Window를 모두 역전파하지 않는다**.
- **공통 Gold58 메타데이터 — 기존 R2D Input 대체:** `yhlucas/rsna-knee-gold58-2fold-v1`, 예상 root `/kaggle/input/datasets/yhlucas/rsna-knee-gold58-2fold-v1`.
  - `gold58_manifest.csv`: 58×12 binary Gold; SHA256 `a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`.
  - `gold58_2fold_manifest.csv`: UID→gold_fold(0/1), SHA256 `6e66444e12a62c3f73670e421b939f1b286e21e496c29040754a72b1d18b4876`.
  - `gold58_fold_class_coverage.csv`, `dataset_contract.json`, `README.md`.
  - **주의:** 로컬 ZIP 패키지 제작 완료, **사용자의 실제 Kaggle Dataset 등록/마운트는 미확인**. `gold58_fold_class_coverage.csv`는 학습 라벨이 아니라 검증 통계.
- **공통 pretrained Model:** MetaResearch DINOv2 PyTorch `base/1`, `pytorch_model.bin`; 후보 `/kaggle/input/models/metaresearch/dinov2/pytorch/base/1/pytorch_model.bin`; SHA256 `014965d9e330e7f4bff8ddcbee9df5e4f2ca032b2f5180942a6edb454783e75d`.

## 2. 라벨 데이터 계정별 구성

| 구분 | A: STRICT V1 | B: V4 |
|---|---|---|
| Kaggle Add Input | `yhlucas/rsna-knee-version-a-strict-v1` | `yhlucas/rsna-knee-v4-consensus-dataset` |
| 파일 | `STRICT_V1/STRICT_V1_TRAIN_LABELS_12_TARGETS.csv` | `rsna_knee_pseudolabels_v4_routed_broad.csv` |
| SHA256 (사용자 원본 ZIP 추출 파일) | `c66810ed4bf35a3fffe35d404aa7eceac860e5f28a013ee2ae7fdf0032497168` | `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c` |
| 의사라벨 Study | 4,181 (168 fully-masked Study 제외) | 4,349 |
| 타깃별 유효성 | 32,163 / 52,188, 나머지 20,025 mask=0 (전체 4,349 기준) | 4,349×12 Soft Label+Confidence |
| Fold별 Train | pseudo 4,181 + Gold train29 = 4,210 | pseudo 4,349 + Gold train29 = 4,378 |
| Fold별 Validation | held-out Gold29 | 같은 held-out Gold29 |

STRICT V1 분포는 **전체 4,349 후보 기준**, pseudo supervised train 4,181개의 유효 라벨 수는 동일하다.

| Target | STRICT Positive | STRICT Negative | Masked / excluded |
|---|---:|---:|---:|
| ACL | 339 | 3,366 | 644 |
| MCL | 37 | 3,724 | 588 |
| Medial Meniscus | 1,525 | 2,446 | 378 |
| Lateral Meniscus | 542 | 3,266 | 541 |
| Medial OA | 212 | 2,398 | 1,739 |
| Lateral OA | 66 | 2,490 | 1,793 |
| PF OA | 204 | 2,268 | 1,877 |
| Effusion | 542 | 2,679 | 1,128 |
| Synovitis | 511 | 35 | 3,803 |
| Baker's | 100 | 1,568 | 2,681 |
| Contusion | 364 | 2,367 | 1,618 |
| Fracture | 165 | 949 | 3,235 |

V4 Soft Label은 단순 0/1로 전환하거나 다수 클래스를 일괄 삭제하지 않는다. 원본 컬럼은 12개 score + 각 `__conf`이며 `confidence_floor=0.25`를 적용한다. 평균 Confidence가 매우 낮은 Synovitis 등에는 label noise 경고를 남긴다.

## 3. 확정된 Gold58 2-Fold

- Seed `20261013`; Fold0 held-out29, Fold1 held-out29. 각 UID는 validation으로 **정확히 한 번** 등장.
- 각각의 12개 타깃에 양성/음성 최소 1명 이상이 존재하여 **Fold×Target AUROC 24개가 계산 가능**. 예시 MCL: Fold0 4+/25−, Fold1 5+/24−.
- **Fold0:** Gold Group1(반대 29)로 학습, Fold0 29로 검증. **Fold1:** Gold Group0로 학습, Fold1 29로 검증. A/B 동일 UID Fold 매핑.
- Gold 반복 사용으로 인해 결과는 개발/교차검증 성능이며 독립 테스트가 아니다.
- **정책 차이:** 원본 STRICT V1 Release README는 Gold58 튜닝/학습을 제한한다. 현 노트북의 `CUSTOM_GOLD_2FOLD_TRAIN`은 **별도의 사용자 승인 연구 프로토콜**이므로 STRICT 공식 릴리스 준수 결과라고 표기하지 않는다. Stage1 이후 MIL/Selector에서도 같은 Fold의 held-out Gold 라벨·예측/선택 정보를 누설하면 안 된다.

## 4. Stage1 모델과 학습 설정 (V6 노트북 실물 기준)

| 항목 | 설정 |
|---|---|
| Backbone | Meta DINOv2-Base, ViT-B/14, full fine-tuning, CLS+PatchMean 1536d |
| Input | `[18, 3, 224, 224]` / Study; Window=인접 3 Slice |
| Head | LayerNorm1536→Linear256→GELU→Dropout0.10, 타깃별 Window Attention, 12 logits, Mean residual 0.1 |
| Runtime | 각 계정 Kaggle T4×2, GPU0→Fold0, GPU1→Fold1 **완전 독립 1-GPU subprocess 2개**, DDP 아님 |
| Study batch | physical 1/GPU, Gradient Accumulation 4, effective 4/**Fold** (양 Fold 합산 batch8로 해석 금지) |
| Window microbatch | PREFLIGHT에서 18→12→8→4를 GPU 시간/VRAM으로 시험 후 선정. 과거 Batch≥124의 여유와 동일한 연산 단위라고 가정하지 않음 |
| Optimizer | AdamW β=(0.9,0.999), eps=1e−8, weight decay 0.05(편향/정규화 등 제외) |
| Backbone LR | early layer 1e−6, middle 3e−6, late 1e−5 (그 외 encoder 1e−6) |
| Head LR | 2e−4 |
| Scheduler | warmup 5% optimizer steps → linear decay |
| Numeric | FP16 AMP + GradScaler, activation checkpoint, gradient clipping 1.0 |
| Epoch / stopping | max12, patience4, 최소 4 Epoch 조건 |
| Best checkpoint | held-out Gold29 Macro AUROC 최대 |
| 보조 지표 | Macro AUPRC, 12 target AUROC/AUPRC, Recall/Precision/F1/Specificity/Balanced Accuracy @ threshold0.5, confusion matrix |
| 저장 | Fold별 `best.pt`, `last.pt`, epoch history, predictions, class weights, logs, integrity report; 종료 후 OOF58 결합 |

**A/STRICT 전용 Loss:** mask=0인 타깃은 gradient=0. 유효 pseudo 라벨로만 class balancing; 양성/음성 양쪽 빈도 보정 power0.70, ratio>20일 때 다수 타깃 loss만 Epoch마다 회전 감소(cap20×희소 클래스), target count correction power0.35. 희소 클래스 사례는 매 Epoch 유지. Study 자체나 타깃 외 다른 질환 정보 삭제 금지.

**B/V4 전용 Loss:** soft BCE의 양성·음성 항 별도 보정 power0.70, 가중치 [0.5,2.5], 정규화; per-target confidence weight `0.25+0.75×conf`, 모든 4,349 Study 유지. 양·음 soft mass 기준; 0.5로 hard threshold하여 삭제하지 않음.

**Gold 학습 행:** pseudo-derived class weights 적용하지 않는 neutral BCE ×3. Loss denominator는 12개 타깃으로 고정하여 Gold×3/Confidence가 분자분모 상쇄되지 않음.

**비교 해석:** A/B는 라벨 구성뿐 아니라 실제 유효 타깃 수·Loss 보정 방식도 다르다. 결과가 달라져도 '라벨 정확도 효과' 단독 원인으로 결론 내리지 말 것. 필요 시 공통 UID/타깃 마스크와 동일 Loss의 추가 통제 실험.

## 5. Notebook 및 Input 운용 상태

- A: `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb`; 파일 SHA256 `e603978948c0d6d378385105b1b3d8088e8771b3f40e5f53b66d838d1f31e1c0`
- B: `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V7_WORKERFIX.ipynb`; 파일 SHA256 `5e99513024329483cacc114fb814f83b35b06dfd924705b744451d18c458a84c`
- 두 파일은 대화 산출물이며 **현재 GitHub에 노트북 바이너리를 커밋했다는 뜻이 아님**. 최신 구현으로 교체 시 파일명·SHA·설정을 본 문서에서 갱신.
- **Add Input 5개/계정:** 공통 ① Native224 cache ② shared manifest ③ 전용 Gold58 ④ official DINOv2 Base 모델, 개별 ⑤ STRICT/V4 라벨.
- 구 R2D `rsna-knee-wide224-persistent-cache-v1`은 이 Stage1 Gold Input에서 **사용하지 않음**.

## 2026-10-13 — Stage1 학습 완료 체크포인트 계약

- **B V4 우선 Stage2 후보:** Fold0 best.pt SHA256 `15bd9189eac7a7366239a0747e671f0f567a40a2db660e7054e2de26eb01e629` (Best Epoch8, Gold29 AUC0.892702); Fold1 `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5` (Epoch9, AUC0.868232).
- **A STRICT 보존 후보:** Fold0 best.pt `e5ae8a3a2b30d5bf71a19aabc7cfba888bb05d91b152d82931c3d44f3d4387a6` (Epoch9, AUC0.838365); Fold1 `954d099a0e4274c1ee4581fc8c518fd3f30dcafff39e4d2ed941eb9224704935` (Epoch7, AUC0.785654).
- **모델 아키텍처·입력·학습 Loss 계약은 본 문서의 V7 설정과 동일**. Fold0 validation Gold29와 Fold1 validation Gold29의 모델을 혼동하지 않는다. 두 Fold 각각 독립 encoder+head 전체 checkpoint이며 1536d feature는 **DINO Encoder의 CLS768+PatchMean768 출력**을 사용한다. 저장된 best.pt는 `model`, `epoch`, `fold`, `label_mode`, `config` 및 `metric_auc`가 포함된 torch checkpoint.
- **실물 확보 상태:** 사용자 공유 review ZIP은 `.pt` 바이너리를 제외하므로 보고된 SHA값은 `training_summary.json`에 대한 신뢰이며 **실제 `.pt` 파일 바이트 검증은 미완료**. Kaggle Output에서 추출해 별도 Dataset Add Input으로 등록한 뒤 일치 확인 필요. 모델 파일을 새 GitHub 문서에 넣는 게 아니라 기존 본 데이터·모델 문서에서 registry 업데이트.
- **성과 참조:** Gold58 DEV OOF Macro AUROC A=0.811284, B=0.871112. 세부 Target/F1/Recall 및 해석은 동일 실험 ID의 `EXPERIMENT_LOG.md` 참조.

## 2026-10-13 — 2-Fold LB Test Data and Checkpoint Input contract

- A Strict and B V4 are distinct Code Competition notebook submissions. For each, Fold0 and Fold1 best weights must be loaded strict, output sigmoid probabilities and then average 50:50. Gold58 is never a scoring inference input.
- Proposed (not published/verified) checkpoint datasets: yhlucas/rsna-knee-stage1-strict-f01-best-v1 and yhlucas/rsna-knee-stage1-v4-f01-best-v1, root filenames fold0_best.pt and fold1_best.pt. The four exact SHAs are in previous Stage1 checkpoint contract section. Do not use TRAIN review ZIP as weights.
- Raw test data is sourced from competition RSNA Knee Abnormality Detection, test.csv/test_series.csv/sample_submission.csv and test_series/<Study>/<Series>/*.dcm. Existing HDF5 Native224 V3 training cache contains only 4,407 train/Gold subjects; it cannot supply hidden test studies.
- Preprocessing reproduces RMIL-04B Native224 V3: DICOM physical slice sort by normal dot ImagePositionPatient; 130mm center crop (pad outside -5 after normalization); MONOCHROME1 inversion; per-Series 0.5/99.5 percentile clip sampled at <=200k pixel stride; Series mean/std Zscore; clip +-5; resize OpenCV INTER_AREA (224x224); uint8 np.rint((z+5)*25.5). Use 18 Window sampler SHA 8ce97e7cebf0c75597e6bd8ea8c262bfb6596dfdcbf0975b8d31101fe125052c, epoch0, [center-1,center,center+1].
- Original FeatureDINO model class source SHA256 b385856a8e5ecfcd81da42c417dc1ba96ca5cb4f3d345a44a162907c32ad0874 is identical in A/B training ZIPs; notebook preserves it. MetaResearch Dinov2 PyTorch Base v1 original model pinned via SHA is also needed to reconstruct the exact encoder init/config.
- Notebook SHA A 268187b2ab0db2390a008cb627adaa0e8aa731b2ff8f35560cdaf85856d59eb1; B a0c7bd71d50f5e652f49ee1f23398be1eceb8b34b6fcc2b4195e6b60ebe04392. Static AST, nbformat, sampler parity 20 Studies/360 Windows, synthetic pixel byte parity 12 Slices/3 Triplets PASS. Full Kaggle inference and official LB UNVERIFIED.
- T4x2 two full models running parallel GPU inference; Internet OFF; Kaggle Submission Code runtime <=9h. Output submission.csv strict shape/range/Study UID/12 columns/SHA. If a Study has corrupt DICOM, neutral fallback is logged; high fallback rate invalidates quality claims.

## 2026-10-13 — V2 LB Checkpoint path correction (current)

- **A STRICT:** `/kaggle/input/datasets/yhlucas/rsna-knee-stage1-strict-f01-best-v1/fold0/best.pt` and `/fold1/best.pt` under the same root. User-provided exact structure. V2 Notebook SHA `d272241254c8222004a74dbf34def355a6093cc7ef588d5852a22e965a89bdb0`.
- **B V4:** `/kaggle/input/datasets/woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold0/best.pt` and `/fold1/best.pt` under the same root. **Owner `woniyeon` (not `yhlucas`).** V2 Notebook SHA `2c7323124de1b5fa3a2de2463618f19b6a342a9c7e060abe8a9a0dcf0ce2cb95`.
- Supersedes V1 **checkpoint root-level `fold0_best.pt`, `fold1_best.pt` assumptions**; model SHA and scientific configuration unchanged. Actual Kaggle mount and model file bytes not independently tested; notebook validates file presence and SHA before inference.

## 2026-10-13 — Historical Batch vs future throughput policy

- V7 Stage1 physical StudyBatch1/GPU, gradaccum4, Window microbatch18, HDF5 synchronous and activation checkpoint ON were the **completed run settings**; they must not be reused without profiling as next-stage defaults.
- User reports older Batch124+ simultaneous operation and ~20GB spare VRAM; user weekly GPU allocation 30h. Which device(s) owned that spare VRAM and whether Batch124 refers to Study/Window are unknown, but speculative OOM avoidance is not an acceptable reason to force small batches.
- Next study benchmarks actual 128-256 MRI studies, optimizer steps, Study batch 1/2/4/8+, Window microbatch 18/32/64/96/124/128+, checkpoint ON/OFF, HDF5 prefetch, and 2GPU mode; selects measured max throughput. Full TRAIN aims <=4h, >=8h estimated blocks, weekly 30h quota is mandatory. No pretrained/label/input semantics change under this policy update.
- References: [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md), [GPU_BATCH_RESOURCE_MANDATORY_POLICY.md](GPU_BATCH_RESOURCE_MANDATORY_POLICY.md).

## 2026-10-13 — 제출 모델 공식 Public LB 사용자 보고 (결과와 출처)

- 두 V2 Notebook의 A STRICT 2-Fold 및 B V4 2-Fold sigmoid probability equal-mean 제출에 대한 **사용자 보고 Public LB**: **A=0.861**, **B=0.910**. 제출 스크립트/CSV 및 숨겨진 Test 실패 UID 감사 자료는 별도로 수신하지 않았으므로 그 실행 세부 정보를 PASS로 단정하지 않는다.
- 개발 Gold58 OOF Macro AUROC: **A=0.811284**, **B=0.871112**. External Public LB 우위(B−A=+0.049)는 별도 test 결과이고 OOF/Both are not directly paired distribution metrics.
- 기존 프로젝트 최고 Exp57 Public LB **0.918** (3-fold selector + full MRI direct 70:30) 대비 **B=−0.008**, **A=−0.057**. B는 next full-MRI encoder candidate; stage1 checkpoints preserved.
- 모델 아키텍처/전처리/생성된 checkpoint hash는 V7 학습 및 V2 추론 명세에서 **변경 없음**. 이번 업데이트는 결과 기록이며 새 GPU 추론/학습 실행이 아님.

## 6. 변경·감사 원칙

각 데이터셋의 Kaggle 게시 버전, 실제 mounted path, SHA, UID 교집합, mask, 라벨 정합성은 실측 때 이 문서에 갱신한다. QA 'PASS'와 GPU 학습 'COMPLETE'를 혼동하지 않는다. 모델 설정 변경은 이유/영향과 이전 값까지 남긴다.

- [계획 및 현재 단계](S1-DINO-CBL2F-01_ROADMAP.md)
- [실제 실행 결과 누적 로그](S1-DINO-CBL2F-01_EXPERIMENT_LOG.md)
- [프로젝트 공통 Kaggle Notebook 규칙](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)


## 2026-10-14 — S1FT02 Broad→Strict 재학습 입력/클래스 가중치 계약 (계획)

- Common warm-start checkpoint B V4 Broad: `/kaggle/input/datasets/woniyeon/rsna-knee-stage1-v4-f01-best-v1/fold0/best.pt` SHA `15bd9189eac7a7366239a0747e671f0f567a40a2db660e7054e2de26eb01e629`, Fold1 `/fold1/best.pt` SHA `0c3939d93d3f37daacf2625711fe751586ea354e5a64b19eb9911ed5f0eb28a5`.
- A source: `yhlucas/rsna-knee-version-a-strict-v1/STRICT_V1/STRICT_V1_TRAIN_LABELS_12_TARGETS.csv`, SHA `c66810ed4bf35a3fffe35d404aa7eceac860e5f28a013ee2ae7fdf0032497168`. B source: `yhlucas/rsna-knee-v4-consensus-dataset/rsna_knee_pseudolabels_v4_routed_strict.csv`, SHA `bfca4993e5c985d9318d732bf2a0970dd7af9b3beff1d6ff619822042bf7a2c0`.
- Other inputs same Stage1: 5Pack Native224 V3, Shared Series Manifest/Sampler SHA, Gold58 frozen 29/29 split, MetaResearch DINOv2 Base/1 pretrained. No competition input for cached training, Competition required for later LB inference.
- Pseudo-only target loss: A hard binary + Mask + majority-rotation cap20:1 + inverse-frequency power0.7 + coverage power0.35; B routed strict Soft + Confidence + Mask + soft pos/neg weighted prevalence inverse power0.7 cap0.5..2.5 + coverage power0.35. Gold29 neutral BCE×3, no pseudo class priors. Unmentioned Mask=0 never converted to negative.
- New model datasets for submission are **proposed only**, not yet registered: A `yhlucas/s1ft02-a-strictv1-f01-v1`, B `woniyeon/s1ft02-b-v4strict-f01-v1`; require `fold0/best.pt`, `fold1/best.pt`, `fold0/training_summary.json`, `fold1/training_summary.json`. Submission notebooks fail-fast on missing files, audit checkpoint SHA from training summary. Both Fold models initialized from same V4 Broad; previously trained A Strict model is not used.
- The training notebooks alter Study physical batching/DataLoader and turn checkpointing into a performance-tested switch while preserving architecture StateDict key names. Model checkpoint actual GPU load/Baseline Val parity not confirmed until Kaggle GPU preflight.
