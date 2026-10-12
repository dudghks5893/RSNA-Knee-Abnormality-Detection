# S1-DINO-CBL2F-01 — 데이터·모델 기준 명세 (누적 관리)

- **실험 ID:** `S1-DINO-CBL2F-01` (2026-10-13 신규; 기존 GitHub 파일명/코드 검색에서 중복 미발견)
- **목표:** DINOv2-Base Stage1 지도 Fine-tuning을 STRICT V1과 V4 라벨 정책으로 비교하고, 이후 Full-MRI 특징 캐시·질환별 MIL·Top-K Selector로 확장.
- **운영:** 이 실험군의 Markdown은 본 문서(DATA_MODEL), ROADMAP, EXPERIMENT_LOG **3개만** 만들고 계속 편집한다. 실험·버그·노트북 버전마다 .md 신설 금지.
- **실행 상태(2026-10-13):** Kaggle 학습 **미실행/미검증**. 아래는 준비된 입력의 로컬 감사와 V6 노트북 설정이다. 데이터셋이 Kaggle에 업로드·마운트되었다는 의미가 아니다.
- **출처:** 로컬 공개된 A/B V6 노트북, 사용자 제공 STRICT/V4 원본 ZIP, Gold58 사용자 제공 정답, 기존 GitHub cache 명세. 최신 노트북 설정이 바뀌면 해당 변경 이력과 SHA를 이 문서에 갱신.

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

- A: `A_S1_STRICT_DINOBASE_F01_GOLDDEDICATED_V6.ipynb`; 파일 SHA256 `bef2684ccc1e114782cf7cc7efc9c27db4cabeffa4e54317917b6898486a79e5`
- B: `B_S1_V4_DINOBASE_F01_GOLDDEDICATED_V6.ipynb`; 파일 SHA256 `ebbd19492b51687e927d1c730197a3c4d7ec1f4e014e11f74b7be770cbac859b`
- 두 파일은 대화 산출물이며 **현재 GitHub에 노트북 바이너리를 커밋했다는 뜻이 아님**. 최신 구현으로 교체 시 파일명·SHA·설정을 본 문서에서 갱신.
- **Add Input 5개/계정:** 공통 ① Native224 cache ② shared manifest ③ 전용 Gold58 ④ official DINOv2 Base 모델, 개별 ⑤ STRICT/V4 라벨.
- 구 R2D `rsna-knee-wide224-persistent-cache-v1`은 이 Stage1 Gold Input에서 **사용하지 않음**.

## 6. 변경·감사 원칙

각 데이터셋의 Kaggle 게시 버전, 실제 mounted path, SHA, UID 교집합, mask, 라벨 정합성은 실측 때 이 문서에 갱신한다. QA 'PASS'와 GPU 학습 'COMPLETE'를 혼동하지 않는다. 모델 설정 변경은 이유/영향과 이전 값까지 남긴다.

- [계획 및 현재 단계](S1-DINO-CBL2F-01_ROADMAP.md)
- [실제 실행 결과 누적 로그](S1-DINO-CBL2F-01_EXPERIMENT_LOG.md)
- [프로젝트 공통 Kaggle Notebook 규칙](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
