## 2026-10-12 — Stage1 개선안: Wide9 고정 선택 대신 All-Series epoch-rotating 3-Slice Window (DESIGN DRAFT / GPU 미실행)

**사용자 핵심 우려:** Stage1 DINO를 기존 Exp11B `6 slots × 9 selected slices`로만 학습하면, 특징 추출 Encoder가 제외된 다른 Series/전후방 Slice 및 rare sequences에 충분히 task-adapt하지 못할 수 있음. 고정 Wide9 원안은 **권고 취소**. 원래 Exp11B 성공 기록을 무시하는 것이 아니라, 새 Stage1의 목적(전체 MRI 3-slice window Feature Encoder)을 우선한 설계 변경.

**Stage1 신규 권고 (추정 개선 효과, 아직 테스트 없음):**
- Meta 공식 Pretrained DINOv2 Small/Base에서 출발, **전체 Series를 학습 후보**로 두고 Epoch마다 Series당 다양한 물리적 Slice 중심을 재샘플. 윈도우는 실제 인접 `[center-1,center,center+1]`로 만들어 **Stage2 전체 MRI feature 추출/최종 Top24 2.5D와 입력 계약 일치**. 환자 라벨로 supervised 12-target classification, 작은 quality-aware/Series-aware aggregation Head를 Stage1 학습에만 사용; Head는 feature extraction 때 제거하고 Backbone `CLS + patch mean`만 저장.
- 단순 매 Epoch 전체 819,078개 window를 DINO로 **역전파하지 않음**. 제안 시작값: Study당 ~12–18개의 동적 Window, 실제 Series마다 우선 최소 하나를 배정하고 남는 수를 균등 배분. Study Series가 상한 초과 시 Fold·UID·Epoch 기반 회전 선택으로 시리즈 누락을 장기간 방지; **매 Epoch All Series 고정 처리라고 오표현하지 않음**. 위치는 예를 들어 0~100% 범위의 계층화 bins/10~90% 중심 및 양끝 보충으로 설계, epoch간 덜 본 위치 우대; 정해진 단일 20~80% 범위에 고정하지 않음. All-series 사용으로 Scan 품질과 label noise에 민감해질 수 있으니 balanced allocation + fixed deterministic validation, Series별 selected positions/coverage audit 권장.
- 동일 Study/Series/Window 입력 3장에 identical geometric transform 적용(동일 위치 정렬), mild intensity augmentation은 train only / 원본 contrast 보존. 모델 K24 자체는 **Study당 24개**로 Stage2 MIL selector가 선택할 것이며 Stage1의 `12-18`은 성능 실험의 K가 아니라 연산 예산임.

**전처리 제안 — 효율 우선 vs 원본 DICOM:**
- DICOM pixel은 `RescaleSlope+Intercept`, MONOCHROME1 inversion, ImageOrientationPatient+ImagePositionPatient 물리 정렬, 130mm FOV centered crop 및 boundary pad, **Series 단위** robust intensity normalize, resize224, uint8로 먼저 처리. Meta DINO input은 uint8→float [0,1] 및 ImageNet channel normalization. 원본 DICOM을 무전처리로 입력하지 않음.
- **현재 완성된 RMIL-04B Full Native224 V3 5Pack/190Shard**는 전체 `4,407 Studies/24,371 Series/819,078 Slices`를 이미 저장. 현재 V3 원본 실제 규칙은 Series-sampled p0.5/99.5 clipping → full-Series z-score clamp[-5,5] → pad -5 → cv2 INTER_AREA resize224 → uint8, 130mm FOV. 신규 Stage1/FullMRI feature/Top24/hidden inference를 이 **동일 V3 규칙으로 전부 새로 학습**하면 이전 Exp57의 1/99 uint8와 정확히 같을 필요 없음. **과거 Exp57의 가중치/Feature를 V3 pixel cache와 혼용하면 안 됨**. 기존 공개 Hidden code 제출에서 V3 DICOM assertions로 `Notebook Threw Exception` 보고되어, Hidden metadata/decoder fallback을 학습 전 preflight로 정의하고, 정상 DICOM에 대한 preprocessing parity와 decode coverage 검증 필수.
- Old Exp57에는 laterality canonicalization이 있었으나 현재 V3 preprocess 함수에는 해당 transformation이 명시되지 않은 것으로 파악. 새로운 일관된 Laterality 처리 추가는 별도 결정·검증 없는 자동 적용 금지. N4, CLAHE, denoise, gamma contrast 큰 보정은 근거 없는 기본 추가 금지.

**라벨/Fold**
- Strict 2Fold 29/29 Gold split; Stage1, MIL/Selector, final DINO의 각 Fold는 동일 held-out Gold29 supervision/pseudo-derived routing을 침범하면 안 됨. V4/V6 비교 시 Stage1 자체도 각각 동일 공개 pretrained 초기값/같은 Study sampling calendar에서 독립 학습 (V6 canonical release 전에는 GPU 학습 금지). Stage1 dynamics의 epoch sampling position은 seed+StudyUID+epoch 고정해 pair 비교 가능.
- Over-claimed OOF 방지: V4 pseudo 라벨 routing/history Gold 관련 누출 가능성 별도 표기; Gold58 개발 여러 번 사용. 이미 학습된 Exp57 Fold weights는 새 2Fold에 무조건 warmstart 금지.
- Input Study budget 12~18는 **초기 가설**이며 이전 Exp11B 18개의 3채널 group과 유사한 forward량을 의도하지만, 모델·학습 구조/Series Count 가변과 2GPU VRAM이 달라서 실제 T4×2 2–3-step FP32/mixed precision smoke 및 GPU throughput 측정 후 고정. Window Microbatch 1 금지, Batch>=124 과거 모델 경험만으로 새로운 K24 full FT VRAM 단정 금지.
- Stage1 평가: Macro AUROC/AUPRC 외 Gold heldout에서 인식하는 Series/position coverage, Target-wise score, MIL attention 분산, Feature statistics, class distribution 그리고 downstream MIL 최종 score를 함께 평가. Stage1 score가 높다고 최종 좋은 feature 보장 X.

**다음 사용자 합의 필요:** 현재 complete Full Native224 V3 캐시 기반으로 전 단계의 픽셀 전처리를 통일하고, Stage1 All-Series 3-slice Window epoch coverage 변경안을 채택하면 신규 Notebook을 제작한다. 학습 미실행, 초안 변경만 수행.

---

## 2026-10-12 — 설계 논의: 3단계 Task-tuned DINO Feature → MIL Selector+Direct → Top24 DINO (DRAFT, 미실행)

**사용자 질문/방향:** Exp57 계보를 참조한 개선형 모델에서 특징 추출 DINO를 official pretrained 그대로 쓸지 MRI 전체 학습할지 결정. 사용자 파이프라인은 정확히 `DINO feature encoder → hierarchical MIL (12-target window/series importance + direct prediction) → patient-level Top24 3-slice windows → final DINO warm-start predictor → final Top24 70% + MIL direct30%`. 1 Fold에서 2개 DINO checkpoint(초기 task-tuned feature encoder, Top24 end-to-end final) + 1개 MIL, 단 MIL은 Selector이면서 Direct30%의 예측기이므로 별도 세 번째 direct 모델은 불필요. Final DINO는 initial DINO와 MIL pretrained weights를 초기화로 활용하며 서로 독립적 모델 2개를 처음부터 2회 새로 학습하지 않음.

**권고:** 공식 Meta DINOv2 Base/Small (224; Base embedding768/CLS+patchmean1536, Small384/CLS+patchmean768)에서 시작해 **Fold-aware supervised task adaptation** 으로 knee MRI encoder 생성, 그 checkpoint에서 `eval()` freeze feature extraction across all Series/Slices → float16 persistent full MRI cache를 Fold별 1회 생성 → MIL 학습→Top24 cache → final DINO Full Fine-tune warmstart. Exp11B→Exp45 검증된 효율적 방식은 선별된 Wide9(6 slots × 9 raw slices)로 first-stage DINO를 task-tune하고, 이후 전체 3-neighbor-slice windows를 819078 candidate로 특징화하는 방식. 이것은 Exp11B 점수 재현 독립 실험이 아닌 **새 파이프라인에 반드시 필요한 stage1 학습**이다. Slice 선택 및 3채널 구성의 train/inference 분포 차이는 결과에 명시하며, 1차에는 새 변수를 더해 3-slice task-tuning으로 바꾸지 않는다. Full 819078 candidate backbone 훈련은 GPU 시간 낭비; **feature extraction만 전체**를 순회. 과거 Exp53 full cache fold당 200.44/241.14분 실제 기록을 비용 기준으로 참고(동일 실행 시간 보장 X).

**Gold과 라벨:** 2-Fold Gold58 29/29, 각 Fold stage1 DINO/MIL/final predictor **모두 동일 held-out Gold29를 감독 학습에서 제외**. Train pseudo report-only4349 + training-side Gold29(4,378 studies), validation Gold29. "Gold58 전원+4349 학습한 공통 MRI DINO 하나"는 Fold validation leakage. Original Exp57 old weights/Top24 Gold artifacts도 새 split held-out 라벨과 충돌 가능; 직접 OOF 주장 금지. 기존 V4 Gold-derived routing 감사할 때 원본 전체 rerun 필요 없으며, 독립 OOF를 보장할 수 없으면 dev comparison이라는 명칭 유지.

**V4/V6 실험 공정성 대 비용 (둘 다 명시)**:
- **Strict full pipeline paired comparison (final research claim):** 동일 Size×Fold의 Official DINO initial state에서 V4 TaskDINO vs V6 TaskDINO를 독립 supervised fine-tune; 각각의 full feature cache/MIL/Top24/final DINO를 별도로 학습. 2 labels × 2 sizes × 2 folds=8 independent full pipelines (not 8 single training jobs). 동일 optimizer LR/batch/seed/time/Fold, target mask/weights auditing. V6 canonical release 이전에는 V6 run 금지. **이것이 라벨이 encoder에도 미치는 효과까지 평가하는 공정한 실험**.
- **Budget-first conditional screening:** 먼저 Size×Fold 당 common MRI feature extractor 1개를 만든 뒤 DINO frozen cache를 **V4/V6 MIL+final comparator에 재사용**하여 feature cost 2배 절감. 그러나 common encoder를 V4 labels로 학습하면 V4에 편향된 Representation 고정이며 "V6 전체 pipeline이 V4보다 나쁜가"라는 주장 불가; "V4-encoder-fixed downstream label influence"만 평가. Label-neutral unlabeled adaptation은 GPU 비싸며 현 priority 아님. User label-comparison priority면 full pipeline fair path가 기준, 가벼운 screen은 명칭/범위를 엄격 표기.
- 권장 실행은 **Base 우선**: Base V4 Fold0/1 기반 Stage1 backbone → feature+MIL/Direct+Top24+Final까지 실질 성공과 비용 계측. V6 canon release 후 Base V6 identical training paired, Small은 이어서 같은 pipeline으로 2×2. Option to start Small as cheap engineering smoke without model scoring. T4×2 single full fine-tune 1 job/account (또는 1GPU×2 fold 분리는 실제 VRAM/throughput 측정 통과 시). Window microbatch1 금지, preflight forward/backward VRAM/throughput 필수.

**단계별 체크포인트 산출:** `stage1_dino_best.pt`, `full_features_fp16_shards+manifest_sha`, `mil_direct_selector_best.pt`, `top24_manifest+image_cache`, `final_top24_dino_best.pt`, `fold_val_predictions_branchwise`. MIL Direct30%는 동일 MIL 모델의 질환 직접 확률, 최종 Top24 70%는 최종 DINO 모델의 확률. 70:30은 Exp57 검증값으로 출발하지만 새 라벨/Backbone/2-Fold에서는 최종 blend 최적 보장 없음. 관련 실험 기록은 기존 README Exp11B, Exp45-57, Exp62-63을 따름. 신규 실험별 Markdown 금지.

---

## 2026-10-12 — UPDATED DRAFT: Exp57 통찰 기반 개선형 K24 DINO × Label V4/V6 × Small/Base × Gold 2-Fold

**사용자 최신 결정**: Exp57 체크포인트/전처리 재현 실험, 기존 Wide9 재기준선 학습, K32/고해상도 확대 선행 실험 **하지 않는다**. 과거 결과 자체를 연구 근거로 사용하고 **새로운 개선형 Top24 모델 하나**를 사전에 고정하여 라벨 2종 × 모델 크기 2종 × 2-Fold = 총 8개 학습으로 비교한다. 현재는 설계 초안/미실행. LABEL-V6는 `CANDIDATE_NOT_RELEASED`: canon SHA, UID × 12, mask, high-review 최종 승인 후에만 V6 GPU 학습.

### 누적 근거 (과거 결과)
- Exp11B Base vs Exp7A Small: Fold2 AUROC 0.942758 vs 0.900860 (Head width 등도 다르므로 Backbone 크기의 순수 효과라고 단정하지 않음). Exp12B Wide9→Slice15 hidden LB 0.822, Exp13A 224→336 LB 0.861; 이미지 수/해상도 무조건 늘리는 방법은 선행 금지.
- Exp47 patient-level attention Top24(3-slice window) / 평균 선택 Series 5.48, Exp48 Warm-start B3A LB 0.907 vs Exp49 Clean-start 0.903. Selector 자체 강한 신호, 기존 Top24 persisted raw cache와 ranking을 가능한 그대로 재사용하되 provenance/validation leakage 확인은 새 거대 재학습이 아닌 **메타데이터/manifest의 소규모 무결성 점검**으로 수행.
- Exp50 Full-MRI Direct 0.904, Exp51 70:30 0.913, Exp57 3fold 70:30 0.918. B3A 중요 영상과 전체 MRI Direct 상보성은 강한 관측; 추가 Full-MRI feature extraction/branch 재학습은 1차 8회 모델에 포함하지 않고, 승자에 대해 **저장된 Fold별 Direct predictions/weights 활용 가능 시** 후속 평가.
- Exp58 inference-only K32 Fold2 0.969147은 Exp62 K32-trained hidden LB 0.905로 재현되지 않음(다른 조건도 변화), Exp63 no-val all-data 0.897. K24 유지 및 validation-best 선택.

### 고정된 개선형 모델 1종 (안)
- 입력: **Study당 K24**, Exp57 질환별 Attention 기반 Top24 Ranking/Window(실제 인접 slice c-1,c,c+1), 224×224, 원래 130mm physical FOV/원래 normalization/laterality. **Series별 K24가 아님**. **현 Native224 V3는 원래 Exp57 픽셀 전처리와 다르므로 아무 검사 없이 혼용 금지**; 이전 Exp57 Top24 persisted cache를 가능하면 그대로 사용. 기존 Top24 캐시는 재생성보다 재사용 우선.
- DINOv2 Small/Base full fine-tune, CLS+patch mean global, per-target hierarchical Window/Series attention(Exp57 강점). **새 제안**: target-wise attention context와 Top24 전체 mean pooled context를 learnable bounded residual/gate로 결합하는 안정화 Head(기존 hierarchical B3A의 구체 코드 중복 여부 확인 후 설계). Metadata plane/fluid/slice-normalized position은 이미 존재하는 입력과 충돌 없이 적용. 12 Target single shared backbone, 매 실험 전체 구조 동일; Base feature width와 Small feature width 차이 외 가능한 같은 계약. 새 헤드 효과 자체를 독립 검증한 게 아니며 실제 향상 가설일 뿐. Full-MRI Direct는 나중에 blend.
- 이전 검증된 DINO Recipe **Exp7A/Exp11B**: Full FT, physical batch4/gradaccum1, Backbone early/mid/late LR 1e-6/3e-6/1e-5, Head 2e-4, MaxEpoch12, patience4, 5% warmup+linear decay; Base Head768, Small Head384. 위는 구 모델 recipe이며 K24 학습에서는 **물리 VRAM 사전 속도/peak 배치 벤치 필수**; 불가능한 숫자를 억지 적용하거나 WindowMicrobatch=1로 자동 축소하지 않음. V4/V6 동일 run budget/augmentation/optimizer/early stopping. 2-Fold의 Gold 29 train은 과거 Exp57 Gold47 train과 다르므로 절대성능 직접 대조 불가.
- **공통 Model Initialization**: 동일 Size/Fold V4-V6 Pair는 공식 공개 DINO pretrained와 동일한 초기 Head RNG/seed/state SHA에서 출발한다. 기존 Exp57 task-tuned checkpoint를 임의 Warm-start하면 변경된 Gold29 Val에 이미 정답이 포함될 수 있어 비교 결과 오염 가능; matched clean-start가 안전한 기본값. Old Fold checkpoint 재사용은 provenance 증명이 있을 때만 별도 검토.

### Gold split / 8 run
- Gold58 iterative multilabel stratification `29/29` 고정 Manifest, 타깃별 양·음 class 분포 실제 확인. Fold0 train=Pseudo4349+Gold[1]29, val=Gold[0]29; Fold1 train=Pseudo4349+Gold[0]29, val=Gold[1]29. V4/V6 모델/seed/validation IDs/metadata/Top24 입력/augmentation/pixel & checkpoint selection 모두 동일. Gold train에는 Gold truth만; pseudo routing이 Gold-derived일 수 있으므로 "clean independent OOF" 주장 금지.
- RUN ID: `EXP-L01/L02` Small+V4 Fold0/1, `EXP-L03/L04` Base+V4 Fold0/1, `EXP-L05/L06` Small+V6 Fold0/1, `EXP-L07/L08` Base+V6 Fold0/1.
- **주의: 이전 Exp57 Selector/Top24 Gold cached results에 새로운 Gold29 validation 라벨이 학습에 간접 반영됐을 가능성**. 모두 같은 고정 후보를 사용하더라도 누출이 무효화되지는 않음. 가능한 Fold-agnostic/pseudo-only selector 또는 실제 held-out에 대해 fold-safe old selector가 확인되면 그것을 사용; 재생성 비용이 크거나 불명확하면 기존 Cache는 **탐색적 개발 비교**에만 쓰고 'strict clean OOF'라 부르지 않는다. 이미 Gold58을 반복 탐색한 사실도 별도 표기. Full rerun 금지가 이 사실을 삭제하지 않음.
- V4 = 기존 routed soft + confidence (broad/strict 명시); V6 = canon label known-only + mask, not_mentioned/insufficient/uncertain mask0, numerical Baker cyst uncertain mask0. **라벨 값 + 가용 supervision coverage + soft/hard 차이의 결합 효과**임을 명시. 각 Target V4/V6 positive/negative/mask 차이 분석. 우수 Backbone에 대해 `V4 with V6 mask` 조건만 필요시 추가 2-Fold로 coverage-controlled 실험.
- Paired Gold58 OOF macro AUROC/AUPRC 및 disease-level, label count, paired delta/CI, GPU throughput/epoch/runtime. 작은 Gold58이 여러 번 사용돼 통계적 독립 최종 검증 아님; LB 최종 확인.

### 자원과 단계
1. **실행 전에 할 최소 점검(재현 학습 아님)**: 실제 Exp57 cached Top24 완결/경로, Gold UID–Fold/source provenance, V4/V6 범위·canonical 상태, 2-Fold label counts, 1–2 실제 batch forward/backward peak/step-time 예측 (Small/Base 각각). 기존 cache를 재생성하는 Exp57 별도 재현 실험은 하지 않음.
2. V4 4개 Round: Account A T4 GPU0/1 = Small F0/F1, Account B T4 GPU0/1=Base F0/F1 **독립 1GPU batch4가 가능할 때만**. 불가능하면 계정당 2GPU DDP로 Fold 순차 실행하고 Model/Grad semantics 유지. 실행 시 V6용 seed 초기상태 보존; V6 릴리스 뒤 같은 GPU 배치로 L05~L08 실행.
3. 성능 비교 후 우수 라벨/Backbone으로 Exp57 저장 Full-MRI Direct와 보완성 검토. 필요 시 그때만 Full-MRI branch 추가 학습; 새로운 Crop/CLAHE/N4/336/K32 실험은 그 이후에 한 변수씩.
4. Save&RunAll, `best.pt`, `last.pt`, `fold_manifest.csv`, label-mask audit, run config+SHA, metrics/OOF/report artifacts. 결과는 `EXPERIMENT_HISTORY.md`, 진행 상태는 이 문서에만 누적. 새 개별 md 없음.

---

## 2026-10-12 — RMIL-04C02 A/B Kaggle 비공개 제출 오류·안전 추론 V2 준비

**현재 상태:** 사용자 공유 A Kaggle Notebook (`scriptVersionId=357563109`) `Notebook Threw Exception`, B DINOv2 Small도 동일 사용자 보고. 공개 `Save & Run All` 3 Study/12 target 모두 정상, `best.pt` 로딩 성공; **비공개 실제 오류 위치/원인 미확인, Public LB 없음**. `.pt` 확장자는 문제가 아님; 이전 Exp11B `.bin`도 PyTorch `torch.load`. 사용자가 공유한 Exp11B 성공 Notebook은 Series fallback과 slice read failure/결측 복원 등 더 방어적인 방식. RMIL 원래 제출코드의 경직된 DICOM assertions, 의도적인 8h40 경과 예상 `RuntimeError`, 전체 Study Window GPU 일괄 할당은 비공개 대량 데이터에서 위험. 확인 사실과 가설 구분.

**수정본 — 실제 Kaggle GPU/hidden 미실행:**
- A `RMIL-04C02_A_ResNet34_K16_SUBMIT_SAFE_V2.ipynb`, SHA256 `8d4524d4c37a3260c77e5488b87a2ae5f494807631f251702f6208c9ce13959f`.
- B `RMIL-04C02_B_DINOv2Small_K16_SUBMIT_SAFE_V2.ipynb`, SHA256 `6b326bc5df53c2f678af69a3adec1fe46f0206d00e7f4faac90c85f67de97e93`.

**입력 그대로:** A `/kaggle/input/datasets/yhlucas/rsna-knee-rmil04c02-resnet34-v4-k16-best/best.pt`; B `/kaggle/input/datasets/woniyeon/rsna-knee-rmil04c02-dinov2small-v4-k16-best/best.pt`; 각 Notebook은 Competition + 자기 best.pt Dataset 2개. V3 Native224 전처리/선택/12 target/모델 구조 유지. 이상 Series는 기록 후 건너뜀, 모든 Series 불가능한 Study는 0.5 중립 확률로 계속하며 품질 열화 위험을 summary에 기록; CPU에 원본 Study 텐서를 두고 GPU Forward를 Window microbatch로 제한; 사전 예측 시간 초과 RuntimeError 제거.

**다음:** 무료 새 학습 불필요. 사용자가 제출 시도 횟수·자원 예산을 고려해 **A V2 하나**의 Kaggle 공개 Save & Run All / 정상 CSV 먼저 확인, 그다음 필요하면 Code Submit 검증. 실제 hidden 점수·에러 수신하면 `EXPERIMENT_HISTORY.md`에만 누적한다. 실패 시 무작정 반복 제출 금지. Exp57 Public LB 0.918 복귀 개선 방향은 유지.

---

## 2026-10-12 — 사용자 방향 제안: Exp57 기준점 복귀·K16 캐시 실제 범위 확인

**사용자 방향:** 새 RMIL-04C02 A/B 본학습의 비용과 기존 Exp57 Public LB 0.918을 고려해 **최고 성능 Exp 계보로 돌아가 개선**하는 방향 선호. 새 Full4349 DINO Gold58 지표를 기존 Exp57 Public LB와 같은 척도로 비교하면 안 됨. 복귀 전에 기존 Exp57 3-Fold B3A Top24 + Full-MRI Direct 70:30 아티팩트/실험 조건부터 확인하고, 안정적인 단일 변수 개선안을 검토한다. GPU 재학습 자동 시작 금지.

**현재 Native224 V3 캐시 실제 정책 — 원본 `RMIL-04B_PACK00_FullNative224_V3_Cache_CPU_KO.ipynb` centers_nested와 04A 24,371 Series inventory 기준:**
- 4,407 Studies(Train4,349/Gold58), **24,371 Series, 819,078 native slices 모두** 130mm 중심 FOV·224×224 uint8로 HDF5에 저장; 5 Packs, 190 Shards. 모든 Series를 캐시하며, Train은 24,035 Series·808,550 slices.
- **3-Slice Window는 중심 slice 하나와 물리적 양옆 한 장씩 `(c-1,c,c+1)`**, Window 수 3개란 뜻이 아님.
- 유효 중심 `1..n-2`(0-based). K4 초기 anchor `rint(linspace(0.1*(n-1),0.9*(n-1),4))` (~10%, 36.7%, 63.3%, 90%). 이후 기선택 중심들과의 **최소 거리 최대인 유효 중심을 반복 추가**해 K16/K24/K32 중첩. 따라서 Window 중심은 초기 10~90%에만 묶이지 않으며 시작/끝 근처까지 확장한다. K16 중심 위치는 Series 전체에 분산; K16 위의 triplet이 첫/마지막 Slice까지 포함할 수도 있음.
- 위 실제 inventory의 n_slices를 원본 알고리즘으로 계산한 **K16 중심 개수 387,714개**, 3-Slice Triplet의 합집합 고유 Slice **723,689/819,078=88.3541%**, **18,224/24,371 Series=74.78%에서 모든 Slice 적어도 1회 포함**, **23,477/24,371=96.33% Series가 Slice 90% 이상 포함**. 주의: 819,078은 **캐시에 전부 저장된 수**, 723,689는 **K16 Model Input Triplet에 선택된 유니크 Slice**; 중복된 3-Slice Window 호출이 있으므로 실제 연산량은 387,714×3 Slice 사용량 기반. Train만 K16 **382,408 Windows**, Gold58 **5,306 Windows**.
- **Exp57과의 구조 차이:** Exp57은 전체 MRI를 후보로 학습한 질환별 MIL attention에서 환자당 중요 **Top-24 3-Slice Windows**를 선택하고, DINOv2-Base warm-start final B3A 3-fold 70% + 전체 MRI direct MIL 3-fold 30% 확률 앙상블 (Public LB **0.918**). 현행 RMIL-04C02는 전체 Series당 K16 균등 공간분산 Mean pooling+Metadata Transformer, DINOv2-Small/ResNet34 single model; 결과를 Backbone 하나의 우열로 단정 불가.
- 다음 단계: Exp57 기준 재현 가능한 기존 모델/selector/feature cache/Top24를 우선 사용하고, 개선 변수·추론 시간·GPU 자원 예산을 별도 제시할 것. 기존 사용자 실측 Batch≥124 GPU VRAM 여유와 사전 속도 측정 의무 유지.

---

## 2026-10-12 — RMIL-04C02 A/B 독립 V4 Best Kaggle 제출 Notebook 준비 (GPU 미실행)

**현재 작업:** 사용자 제공 Kaggle Best checkpoint Input:
- A ResNet34 `/kaggle/input/datasets/yhlucas/rsna-knee-rmil04c02-resnet34-v4-k16-best/best.pt`; 제출 Notebook: `RMIL-04C02_A_ResNet34_V4_K16_SUBMISSION_T4x2.ipynb`; Notebook SHA256 `0d7dc4c01a76cb21cef370365a578a27acdf478b195503776cb3b0756e3902bf`.
- B DINOv2-Small `/kaggle/input/datasets/woniyeon/rsna-knee-rmil04c02-dinov2small-v4-k16-best/best.pt`; 제출 Notebook: `RMIL-04C02_B_DINOv2Small_V4_K16_SUBMISSION_T4x2.ipynb`; Notebook SHA256 `b7ab9ed270230b9b8e7bf38f26a4e48acaed8bfa8bc710866311b5770a7a79d3`.

**Inference-only:** Official Competition Test Dataset 자동 연동 + 각 자체 Best Dataset **총 두 Inputs씩**. Label/cache/pretrained 별도 Add Input 불필요. 기존 학습 04B V3의 실제 130mm crop, physical Slice ordering, sampled series p0.5/99.5 Zscore→224 uint8, farthest-first K16, 2.5D 인접 3slice, 원래 StudyModel 그대로, checkpoint strict state, 실제 checkpoint config plane_map. T4x2 independent study parallelism; 실제 MRI 첫 Study에서 Window inference 4/8/16/32/64/128 후보 VRAM/속도 계측 후 자동 선택(학습 Microbatch1 재사용 금지). 출력 `/kaggle/working/submission.csv` 12 label; no GPU training. Notebook `nbformat`, Worker/code-cell AST, exact StudyModel AST parity, 04B 전처리 함수 AST parity, CPU A ResNet forward+strict state, synthetic MRI 130mm preprocessing/K16 및 3-row submission CSV execution checks PASS.

**한계/다음 작업:** 사용자가 제공한 원격 Kaggle Best checkpoint의 실제 바이트·구조와 실전 hidden 1300 Study T4 inference는 **아직 테스트하지 않음**. 사용자에게 A/B 각각 Kaggle Save & Run All (Internet OFF, T4×2) 후 성공하면 Competition Submit하도록 안내. 실제 LB 수치와 추론 시간은 제출 이후 `EXPERIMENT_HISTORY.md` 누적; 개별 `.md` 실험 보고서 파일은 만들지 않는다. **대회 Code Submission GPU/CPU <=9h, Internet OFF, submission.csv 필수.**

---

## 2026-10-12 — 단일 누적 기록 체계 복원 / RMIL-04C02 현재 상태 (최신)

**문서 운영 결정 (사용자 의도 복원):** 실험 1개당 GitHub 보고서 파일 1개를 추가하는 방식을 **중단**한다. 실험 결과·수치·변경 근거는 기존 [`EXPERIMENT_HISTORY.md`](EXPERIMENT_HISTORY.md) **하나에 계속 누적**한다. 실험 계획/현재 상태는 **이 파일 하나에 누적**한다. Notebook 규칙과 GPU 운영 절차는 기존 [`AI_AGENT_KAGGLE_NOTEBOOK_RULES.md`](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)에 누적한다. 신규 채팅 인수인계 `CURRENT_HANDOFF.md`에는 이 3개 파일을 어디부터 봐야 하는지만 간결하게 유지한다. README는 진입점, 옛 파일·개별 QA 보고서는 **과거 참고자료**.

**현재 관측:** RMIL-04C02 A ResNet34 / B DINOv2-Small, Full V4 train4349 / Gold58 dev, K16, T4×2 DDP. 현재 사용자 제공 로그 범위: A 7 Epoch 완료/8 진행, B 1 Epoch 완료/2 진행. Epoch 실제 소요: A 46.334분, B 217.147분. Best Gold58 macro AUROC A 0.652246 @ E5, B 0.727655 @ E1 (B는 1 Epoch만 평가). A/B 결과 ZIP·최종 Public LB는 미확인. B의 Microbatch1 배치 전략은 너무 느리고 **GPU 자원 사전 계측 실패**; 사용자는 B 실행 중단 의사 표시했으며 실제 중단/저장 가중치 회수 여부 확인 전.

**다음 방향:** A 완료 산출물이 보존됐는지 먼저 확인한다. B 재실행을 즉시 요구하거나 이전 배치1을 유지하지 않는다. 기존 사용자 실측 **Batch>=124에도 GPU VRAM 여유**를 반드시 고려하면서, 현행 DINO Full Fine-tuning 조건에 맞는 Window Microbatch 후보의 VRAM/실제 처리량을 소규모 테스트한 뒤, 체크포인트 복구와 GPU 세션 예산을 확인하고 사용자에게 사전 보고한다. LAB-V6는 정식 릴리스 전에는 금지(`CANDIDATE_NOT_RELEASED`). V4 각 모델 별도 Public LB 제출 후 V6 정식 릴리스/재학습/재제출 비교 계획은 유지하되, 실행 실패/중단으로 계획 조정 가능.

**문서 분기 금지:** 임시 DDP 오류, Notebook 변경, 사전 Smoke QA, GPU 시간 문제를 별도의 실험당 신규 `.md`로 계속 만들지 말 것. 이 파일에는 **결정·상태만**, `EXPERIMENT_HISTORY.md`에는 **실제 관측 수치·판정만**, `AI_AGENT_KAGGLE_NOTEBOOK_RULES.md`에는 **재사용할 엔지니어링 규칙만** 누적. 각 시점 기존 기록은 삭제하지 않고 이전 상태로 보존하며, 옛 'NEXT'는 최신 블록과 충돌하면 무효.

---

## 2026-10-12 — TOP PRIORITY: 실제 Batch≥124 GPU 여유 기록 / 임의 축소 금지

**사용자 직접 재강조 (네 번 이상 반복된 중요 사실):** 초기 RSNA 실험에서 GPU 메모리를 측정하면서 Batch **124 이상**으로도 메모리 여유가 있었음. **GPU는 한정된 자원이며 임의로 Window Microbatch 1 등으로 축소한 판단을 금지**. RMIL-04C02 B DINO-Small V4 K16 1 Epoch 실측 **217.15분**, A ResNet34 **46.33분**; 원인을 분해하지 않고 모든 차이를 Microbatch 때문이라고 단정하지 말 것. 과거의 Batch 124+는 모델·입력·Global/Window 기준이 이 문서만으로는 특정되지 않았으므로 현행 DINO Full FT에 대한 자동 보증은 아님. 그러나 **작은 배치를 default로 정하는 근거도 아님**. 새 장시간 Notebook 생성 전 최소 여러 Window Microbatch 실제 GPU Forward+Backward 시간·VRAM 측정 및 5~10 epoch 총비용, checkpoint resume 검증 필요. 중요한 설정은 사용자에게 사전 보고하고 승인을 얻는다.

**Required:** [GPU VRAM/Batch 정책](GPU_BATCH_RESOURCE_MANDATORY_POLICY.md) / [root AI coding agent rules](../AGENTS.md). 이 지침이 이전 Notebook의 `microbatch=1` 등의 레거시 설명보다 우선함.

---

## 2026-10-11 — B DINO Small DDP failure diagnosed / V2 two-step smoke fix prepared (Kaggle re-run PENDING)

**User Kaggle failure (B only):** full MRI 190 SHA/V4/Gold58 PASS, pretrained DINOv2 Small strictly loaded, GPU T4x2 one-step Smoke PASS. Then first FULL_TRAIN second forward rank1 `Expected to have finished reduction in prior iteration`, missing-grad parameter index 2. No epoch complete. DDP old `find_unused_parameters=False`; DINO mask token used in masked pretrain but not 2.5D classification. A ResNet not implicated/unchanged.

**Superseding B notebook** `RMIL-04C02_B_DINOv2Small_Full4349_K16_T4x2_DDP_FIX_V2.ipynb`, sha256 `a0d18b42ae006ddbf5cdd43af0ba33033bf572a8f42b3dcd7b2b77634971ceb1`, worker SHA `e2ce001a15b384e1cccc661bb412685a54e5332a609728a5914fe9c8f0e38533`. Before DDP freeze unused `encoder.embeddings.mask_token` if Parameter, enable `find_unused_parameters=True`, named trainable grad audit, smoke **two consecutive full DDP optimizer steps** on largest four TRAIN studies, smoke JSON `smoke_optimizer_steps==2` required, then original Gold test/checkpoint; training config/K16/V4 unchanged. Source notebook and C00 gate verified paths retained.

**QA evidence:** CPU 2-rank Gloo with DINO-like unused mask & nonreentrant activation checkpoint reproduced *old second-forward reducer crash* vs FIXED two-step PASS. Notebook/embedded-worker AST, nbformat PASS, final export mock PASS, 13 unchanged-input and dynamic safety checks PASS. **Actual Kaggle GPU rerun NOT done.** Use new B notebook GPU T4×2 Internet OFF Save&Run All; expect `GPU_SMOKE_DDP_STEP 2/2 PASS` before `FULL_TRAIN`, then `EPOCH_COMPLETED`, `FINAL PASS`. Do not misreport as training completed. [Diagnosis and change log](RMIL-04C02_B_DINO_SMALL_DDP_FIX_V2_2026-10-11.md).

---

## 2026-10-11 — RMIL-04C02 final independent per-model notebooks, end-to-end artifacts audited

**SUPERSEDES** earlier `RMIL-04C02_A_ResNet34_...` and `RMIL-04C02_B_DINOv2Small_...` artifacts. User requires no account A/B instructions *inside* notebooks, numbered add-input sections with file/version and careful code QA.

**Latest files** (all Kaggle GPU execution pending):
- `RMIL-04C02_ResNet34_Full4349_V4_K16_DDP_T4x2_REVIEWED_KO.ipynb` SHA `727e9cc646285bdc183246d20b78cdd2baf6988b4ef27e5764e1022c856d79f7`
- `RMIL-04C02_DINOv2Small_Full4349_V4_K16_DDP_T4x2_REVIEWED_KO.ipynb` SHA `5147ca7377098dff3438f7b1fb64be84a0550b69d946c2e9b2da44b848ac87e3`
- combined ZIP SHA `6950b560aab93c37a43cd0f56a9e2f523e293e3214687931be3f201421c64789`.

Both standalone Notebook Markdown ① Full MRI 5-pack 190-shard cache ② exact V4 broad CSV SHA ③ old `R2D_SHARED224_V1` Gold58/train300/allseries4 metadata + pinned Gold58 SHA ④ exact specific backbone pretrained source/SHA. **Numeric dataset version of `rsna-knee-wide224-persistent-cache-v1` unknown in existing records**: do not guess; replicate version from **successful RMIL-04C00 Input**, verify `R2D_SHARED224_V1/frozen_manifests/gold58_manifest.csv` SHA `a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`, train300_manifest.csv and 358 allseries4 json, old series metadata integrity.

**Enhanced safety:** Before actual training do 190 HDF5 SHA data gate, synthetic final export full dry-run incl checkpoint torch.save/load, Gold58 per-Epoch/target, artifact SHA and review ZIP CRC (actual local mock BOTH PASS); then actual Kaggle 2-rank NCCL Smoke: **largest 4 Train K16 studies** full 2.5D forward/backward, optimizer step, largest Gold58 study inference, checkpoint torch.save/load roundtrip; only then 10-Epoch max/min5/patience3 FULL 4349 train. CPU Gloo 2rank correctness tested incomplete batch n=1,3,4 vs single global mean, diff ≤4.66e-10. After GPU training exact same dry-run-tested finalizer checks real best.pt last.pt SHA/torch.load, epochs and Gold58 metrics, produces review ZIP; **Kaggle GPU RUN NOT YET CONFIRMED**. Initial local QA found an actual UID scoping NameError in newly authored finalizer fixture, corrected and all tests rerun PASS.

[Detailed QA and model-specific input setup](RMIL-04C02_INDEPENDENT_NOTEBOOKS_CODE_QA_2026-10-11.md). Previous A/B notebook filenames and earlier GPU launch instructions below are historical; use latest files above. Gold58 dev reused, LABEL-V6 CANDIDATE_NOT_RELEASED, V4 separate model Public LB after learning then V6 formal release and new training/LB.

---

## 2026-10-11 — FINAL CHANGE: DINOv2 Small FIRST (supersedes RMIL-04C02 B Base) + V4/V6 LB stages

**최종 실험 선택:** A = MedicalNet R34 2.5D, **B = DINOv2-Small 2.5D** (Base/large 확대는 마지막). A 기존 노트북 `RMIL-04C02_A_ResNet34_Full4349_V4_K16_T4x2_KO.ipynb` SHA `433cc79e4da7875d2fd0b25d165e27ea4c75828c11ef8c0ffbf905531ef9f94d` 변경 없음. **새 B Small** `RMIL-04C02_B_DINOv2Small_Full4349_V4_K16_T4x2_KO.ipynb` SHA `6b7fdc59b581cf8f9162845c5e02683612ada196ad2efb41af71cd98c4e1f813`, worker SHA `39c650a857fbeb2dc879c80cd46b8e33503abe5efcb8fe4cdc09d55e4814a41b`. Small official 384-dim, 6 heads, 12 layers, patch14, CLS+patch-mean768; Small pretrain SHA `1051e25b2ed69ddad24f3c41e7b6eed6e7f7d012103ea227e47eb82e87dc2050`, Kaggle Model MetaResearch DINO v2 PyTorch **small v1**, backbone upper LR1e-5/LLRD0.8, head1e-4, fp16. Original B Base Notebook **superseded, do NOT execute**.

A/B new ZIP `RMIL-04C02_AB_ResNet_vs_DINOv2Small_Full4349.zip` SHA `ef610daf58976d2f915731380dbd010893436c9275d3244ed08b5c14925c85b9`. Each Kaggle account T4×2 DDP; full Train4349 Gold58-dev, K16 2.5D, confidence & target-balanced V4 loss, max10/min5/patience3. Notebook nbformat/AST PASS; **Kaggle GPU/strict Small pretrained checkpoint load NOT RUN**. **After training:** independent ResNet V4 LB submission then Small V4 LB submission; obtain exact actual Public LB, no invented 0.94. **Later only when V6 formally released**: audit policy/UID+target masks, do NOT treat `not_mentioned/insufficient/uncertain` as negatives, retrain same A/B backbones and submit V6 LB independently; report delta 4-arm matrix. [Full staged execution protocol](RMIL-04C02_SMALL_FIRST_V4_LB_THEN_V6_LB_PROTOCOL_2026-10-11.md). Previous B Base design section below is **historical/superseded**.

---

## 2026-10-11 — RMIL-04C02 A/B Full4,349 2.5D ResNet vs DINO 준비 (Kaggle GPU 미실행)

사용자 요청으로 기존 `RMIL-04C01` **4-Epoch 고정 ResNet 단독 설계 대신** A계정 MedicalNet R34 2.5D / B계정 **DINOv2-Base 2.5D** 병렬 GPU T4×2 DDP 비교 전환. **최대10, 최소5 Epoch, patience3 Early Stopping**, Gold58 Macro AUROC 기준 두 DDP rank 동일 종료. V4 train4349에서 질환별 soft 양성/음성 비율과 Confidence를 결합해 **양성·음성 질환별 loss weight(.5~2.5 제한, 정규화)** 두 모델 공통 적용. 기존 RMIL-02D는 confidence-only라 **기존 모델과 직접 구조 실험 비교는 confounded**. DINO는 ImageNet 정규화, CLS+Patch Mean1536, Layer-wise ViT LR decay, FP16 activation checkpoint/micro1, ResNet은 기존 -5..5 MedicalNet full FP32/micro4. Gold58 반복 Dev, V6 `CANDIDATE_NOT_RELEASED` 미사용.

준비 파일 SHA:
- `RMIL-04C02_A_ResNet34_Full4349_V4_K16_T4x2_KO.ipynb` `433cc79e4da7875d2fd0b25d165e27ea4c75828c11ef8c0ffbf905531ef9f94d`
- `RMIL-04C02_B_DINOv2Base_Full4349_V4_K16_T4x2_KO.ipynb` `cf7f83c08f7791227083007e2800e8188e35a558ff2d284cd08b8051668fb889`
- ZIP `RMIL-04C02_AB_ResNet_vs_DINO_Full4349_EarlyStop.zip` `202914fde02a7b27bab5376e8d67b708c991a30a0f0dd91411bee8a254168d9c`.
Notebook AST, Worker AST, nbformat + TinyEncoder CPU 2.5D Forward/Backward 확인 (실제 DINO checkpoint, Kaggle T4 CUDA/NCCL, GPU 학습 **미확인**). **DINO Checkpoint** Kaggle Model `metaresearch/dinov2/PyTorch/base/1`, 이전 프로젝트에서 기록된 exact path `/kaggle/input/models/metaresearch/dinov2/pytorch/base/1/pytorch_model.bin`, SHA `014965d9e330e7f4bff8ddcbee9df5e4f2ca032b2f5180942a6edb454783e75d`, input add 여부는 B Kaggle 직접 확인. DINO ViT-B Full-data K16는 **실행시간이 길어 Kaggle 세션 제한 초과 가능성**이 큼. 기존 GPU Notebook 사용하면 이 새 변경은 반영되지 않음. [전용 실험·운영 기록](RMIL-04C02_AB_FULL4349_RESNET_VS_DINO_DESIGN_2026-10-11.md).

---

## 2026-10-11 — RMIL-04C00 verified PASS / RMIL-04C01 4,349-study V4 DDP GPU Notebook prepared (NOT executed)

수령한 `RMIL-04C00_results_for_review.zip` SHA256 `4a2ada496d44501554f510b4f15f7b40df74d11edf3ac8a39e656019a445c322`: CRC, 내부 3개 파일 SHA PASS. Kaggle 실제 로그 상태 `PASS_FULL_CACHE_AND_V4_SCHEMA_GATE`, CPU 5.34분. 5-Pack 4,407 Studies / 24,371 Series /819,078 Slices, Train4,349/Gold58 nonleak UID, **190/190 HDF5 shard 파일 SHA 실제 전수 읽기 PASS**, V4 전체 4,349 × 12 score/conf finite/0..1/누락0, K16 windows 총 387,714. 기존358 V3 픽셀 parity2,006는 04B Producer 보고값이며 C00 재전처리 재검사는 아님. **C00은 GPU 학습 아님**.

**다음 실제 실행 Notebook**: `RMIL-04C01_Full4349_V4_K16_Mean_DDP_T4x2_KO.ipynb` SHA256 `59f229e8f566143f36f8e8fe0a47d7c1140b47bd2ac88c21451284386d5e279a`, Worker SHA `b096595d9f96b33a03427382d742ef5ce0117360189b2250ae2ee0439e4f0049`. Notebook/Worker AST, nbformat, CPU synthetic StudyModel gradient, Gloo 2-rank masked last batch DDP test PASS. **Kaggle T4 실행 미확인**. Kaggle GPU T4×2, Internet OFF, Save & Run All, Seed20261013, Save `RMIL-04C01 Full4349 V4 K16 Mean DDP T4x2`. 4 Add Inputs: (1) `yhlucas/rmil-04b-full-mri-native224-v3` 사용자 확정 `results`/ `results (1)`~`results (4)` 5 pack (2) `yhlucas/rsna-knee-v4-consensus-dataset` (3) `rsna-knee-wide224-persistent-cache-v1` (4) `yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1`. Full preflight 190 SHA 선검사.

RMIL-02D와 동일 ResNet34 MedicalNet OptionA K16 Mean + CLS Transformer + 12-head, Full FT; V4 confidence-floor0.25 BCE; **DDP NCCL 2GPU 하나의 모델 학습** (global 4 Studies, last 1 Study only mask dummy), **4 Epoch 고정 full-data initial training budget** (Train300과 다른 훈련 budget), LR backbone1e-5/head5e-5 WD1e-4 cosine, FP32, frozen BN. 각 Epoch `best.pt`/`last.pt`+Gold58 dev metrics/preds. 리뷰 ZIP은 Checkpoints 및 원본 Train4,349 라벨 제외. 실제 runtime 미측정(수 시간~10시간 이상 가능), Gold58은 반복 사용된 dev set. LABEL-V6 **CANDIDATE_NOT_RELEASED** 계속. [자세한 C00 감사 + GPU 실험 핸드오프](RMIL-04C00_VERIFIED_RMIL-04C01_FULL_GPU_PREPARED_2026-10-11.md). 다음: 학습 로그/검토 ZIP 받아 평가 후 Standalone 제출/정식 V6 계획 결정.

---

## 2026-10-11 — RMIL-04B Pack01~04 independent QA PASS / RMIL-04C00 CPU gate prepared (GPU not run)

사용자가 Pack01~04 `results_for_review.zip` 4개를 제출. ZIP CRC 4/4 PASS, 40개 내부 파일 SHA256 직접 일치, RMIL-04A 동결 Study·Series UID/역할/part/Slice 원본과 전 행 일치, 중복/누락 없음, 4종 K nested center 검증 PASS. Pack01~04 **3,526 Studies (Train3481/Gold45), 19,492 Series, 655,290 Slices, 152 Shards**, 과거 V3 parity 기록 **1600/1600**. Pack00 과거 로그 PASS(881 Studies, 4,879 Series, 163,788 Slices, 38 Shards, V3 parity 406/406) 포함한 **전체 계획 4,407 Studies / 24,371 Series / 819,078 Slices / Train4,349+Gold58 /190 HDF5 / V3 parity 2,006**. 주의: 사용자 리뷰 ZIP에 원본 영상 파일은 없으므로 **190개 HDF5의 실제 바이트 SHA와 현 Kaggle Dataset 마운트는 아직 재검증되지 않음**. V4 4349×12 score/conf 값/NaN/gold leakage 검증 전. LABEL-V6 CANDIDATE_NOT_RELEASED.

**다음 권장 실행:** `RMIL-04C00_Full4407_Cache190SHA_V4_Label_Gate_CPU_KO.ipynb`, SHA256 `a1bf7df011bf17eed8c2c5d3d5b4e2773362025d7f75db4871e2155eab9d668e`, Notebook nbformat/AST PASS, **Kaggle CPU 미실행**. 단일 Dataset의 실물 5개 경로(기존 문서의 `results`, `results (1)`,...`results (4)`) + V4 broad + Gold58 frozen 추가. CPU/Internet OFF/Seed20261013/Run All, HDF5 shard 190개 실제 SHA, 메타 50개 SHA, RMIL-04A full UID inventory fingerprint, nested K, Gold58 제외 및 V4 soft/conf 0..1 검증 후 `RMIL-04C00_results_for_review.zip` 수령. 통과 시 Full4,349 GPU K16 Mean model (02D 구조) 준비. [전체 QA·C00 계획](RMIL-04B_PACK01_04_QA_AND_RMIL-04C00_GATE_2026-10-11.md).

---

## 2026-10-11 — RMIL-04B 실제 통합 Kaggle Dataset 마운트 경로 확보 (RMIL-04C 전용)

**사용자가 Kaggle에 `yhlucas/rmil-04b-full-mri-native224-v3`를 등록하고 다음 5개 실제 마운트 경로를 제공했다.** 파일 존재/SHA/5-pack 통합 상태는 현재 ChatGPT에서 Kaggle mount에 직접 접근할 수 없어 **사용자 진술 기반 경로 확보이며 아직 Kaggle 실측 검증 전**. 다음 RMIL-04C 작업은 이전에 가정한 `RMIL-04B_FULL_NATIVE224_V3/RMIL-04B_PACK_XX` 구조를 **사용하지 말 것**.

```python
from pathlib import Path
PACK_PATHS = [
    Path("/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results/RMIL-04B_PACK_00"),
    Path("/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results (1)/RMIL-04B_PACK_01"),
    Path("/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results (2)/RMIL-04B_PACK_02"),
    Path("/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results (3)/RMIL-04B_PACK_03"),
    Path("/kaggle/input/datasets/yhlucas/rmil-04b-full-mri-native224-v3/results (4)/RMIL-04B_PACK_04"),
]
for i, root in enumerate(PACK_PATHS):
    assert root.is_dir(), f"PACK_{i:02d} 경로 없음: {root}"
    for name in ("series_index.csv", "k_selection.jsonl", "shard_sha256.csv", "cache_contract.json"):
        assert (root/name).is_file(), f"PACK_{i:02d} 파일 없음: {root/name}"
    assert (root/"shards").is_dir(), f"PACK_{i:02d} shards 없음: {root}"
```

- **Kaggle Add Input**: `rmil-04b-full-mri-native224-v3` 하나. 그 안에서 Pack별 `results`, `results (1)`, `results (2)`, `results (3)`, `results (4)`가 **상이하며 공백·괄호를 포함하므로 정확한 문자열 유지**. 디렉터리 `rglob`, 전체 `/kaggle/input` 재귀 탐색 금지.
- Expected metadata from RMIL-04A: Packs 00~04의 studies `881,881,881,882,882`, series `4879,4863,4896,4881,4852`, slices `163788,163788,163788,163860,163854`; 합계 **4,407 Studies /24,371 Series /819,078 Slices**, frozen **Train4,349/Gold58**. **RMIL-04B Pack01~04의 성공 로그·review ZIP을 이번 턴에서 받지 않았으므로 파트별 완료/SHA 확인이 아직 끝난 것으로 주장하지 말 것.**
- 학습 전 **Pack별 실제 HDF5 shard 존재·SHA-256·`series_index.csv`/manifest/metadata·UID coverage·K selection**; 5개 Pack 간 중복 없음; 358명 중첩 기존 V3 2,006 Series 픽셀 SHA parity(각 Pack 산출 메타) 검증; V4 full 4349×12 label schema/score/conf/leakage 별도 승인. LABEL-V6는 `CANDIDATE_NOT_RELEASED`인 동안 학습 금지.
- RMIL-04C baseline 후보 **RMIL-02D V3 K16 Mean**; Seed **20261013**. Gold58은 반복 사용 개발 검증, 별도 standalone 실제 제출 이후에만 LB 보고.

---

## 2026-10-10 — RMIL-04A PASS / RMIL-04B 5개 CPU Pack Notebook 준비 (GPU 미실행)

**RMIL-04A 실제 Kaggle 실행 결과 검증 완료**: 사용자 ZIP SHA256 `121145c51525862672f630d0c6b650602046964151ceb36e53b981a071be3614`, CRC+내부 6개 메타 SHA PASS. 공식 원본 **4,407 Studies /24,371 Series /819,078 Slices**, 누락·중복 0, frozen **Train4,349/Gold58** 분리. V4 broad pseudo-label `rsna_knee_pseudolabels_v4_routed_broad.csv` 전체 4,349 UID 및 12 target+12 confidence 열 커버 PASS; **아직 Full GPU label release 아님**(`UID_COVERAGE_PASS_NEEDS_12_TARGET_CONTRACT`). Train300 분포 재분석 사용자 요청으로 하지 않음.

**RMIL-04B 다음**: 5개 독립 Kaggle CPU Notebook 준비 완료, **실제 픽셀 캐시 미생성**. 04A Study/Series 파트 동결본을 각 Notebook에 해시 고정 압축 내장해 별도 04A Kaggle Dataset 불필요. 전체 224px uint8 원시 저장 41.098GB (14GB/project Output cap), 각 Part ~8.2GB. Pack별 기존 V3 픽셀 SHA 비교 Series: **00:406, 01:419, 02:453, 03:394, 04:334 = 2,006 Series 전체**. RMIL-02B V3 동일 `preprocess_series` 코드 재사용. CPU 합성 padding/no-padding, K 중첩/Notebook nbformat·AST 통과. **Pack00 먼저 CPU Save & Run All을 실행하여 기존 V3 픽셀 SHA 동일 확인 후, Pack01~04 A/B 계정 CPU 병렬**. GPU 없음, Internet OFF, Seed20261013. 세 입력: competition, `yhlucas/rmil-02b-native224-v3`, `rsna-knee-wide224-persistent-cache-v1`. 저장한 8.2GB HDF5 폴더 전체를 각 Kaggle Dataset으로 별도 등록하고 review ZIP만 공유.

**다운로드 전달**: `RMIL-04B_FivePack_CPU_Notebooks_and_Handoff.zip` SHA `3d12212fcd8e467935728452ec91442ce805720317b0a5e69e01f8bdae25c2c3` (노트북 5개 + QA 보고서). 상세 [RMIL-04A 검증·RMIL-04B 실행 준비](RMIL-04A_VERIFIED_RMIL-04B_FIVEPACK_PREPARED_2026-10-10.md). **LABEL-V6 CANDIDATE_NOT_RELEASED**; RMIL-04C 4,349 GPU 학습은 5파트 HDF5 실제 생성/UID·SHA 통합 및 라벨 승인 후에만. 현재 모델 구조는 기존 RMIL-02D K16 Mean이 우선 대조군; Gold58은 반복 사용 개발 검증.

---

## 2026-10-10 — RMIL-04A 전체 데이터·영상 캐시 5파트 사전 검증 Notebook 준비 (Kaggle 미실행)

사용자는 **Train300만 대상으로 하는 class/SoftLabel/confidence 분포 재분석은 진행하지 말고**, 향후 LABEL-V6 완료를 앞두고 **전체 4,349명 Full-data 학습 RMIL-04** 단계로 이동하도록 결정함. RMIL-03 네 모델 완료/동결, 현재 기준 모델 RMIL-02D V3 K16 Mean Gold58 0.577856 유지. RMIL-03B는 탐색 후보, 미검증 대규모 채택 금지.

**사용자 다운로드용으로 작성된 CPU Notebook:** `RMIL-04A_Full4407_5Pack_Source_Label_Preflight_CPU_KO.ipynb`; SHA256 `40720e63afea06bff06b4ec6fa79b51e5c425ee2269ee781dce18c642ae6d24d`. Notebook nbformat 및 각 코드 셀 AST 검증 PASS, **실제 Kaggle Save & Run All 미실행**. 입력 공식 Competition `train.csv`/`train_series.csv`/`train_series/<UID>/<Series>/*.dcm`, 검증 Gold58 dataset `rsna-knee-wide224-persistent-cache-v1`, V4 full dataset `rsna-knee-v4-consensus-dataset` **옵션: UI Mount 실제 검증 전**. GPU 없음, Internet OFF, Seed20261013, Save Version `RMIL-04A Full4407 Cache Partition Preflight CPU`. 전역 /kaggle/input 재귀 탐색 금지, 원본 CSV에 나온 Series 폴더에서만 Slice 파일 개수 검사.

**전체 영상량:** 역사 SS01 기록 4,407 Studies, 24,371 Series, 819,078 DICOM Slices. Raw V3 uint8 224×224 전체 캐시 추정 **41,098,057,728B≈41.10GB**이며 Kaggle Project 저장 cap **14GB**를 넘음. RMIL-04A는 Study 단위 누수없는 **5파트 용량 균형 분할** + `1.3×raw+300MB` 파트별 게이트, V4 라벨의 UID 커버리지 구조적 검증만 수행하고 영상 캐시·GPU 학습은 생성하지 않음. **Train4349/Gold58 분리**. Gold58 반복 개발 데이터, 독립 테스트 아님. V6 후보 `CANDIDATE_NOT_RELEASED` 유지, 원본 영상 캐시는 V4/V6 라벨 변경과 무관하게 재사용 계획.

**다음 실제 단계:** A CPU ZIP 수령·검사 → RMIL-04B 5파트 네이티브224 V3 전처리/358명 픽셀 parity 게이트/sha Dataset 저장 → 라벨 승인 후 RMIL-04C Full4,349 Train (K16 Mean 원형 우선, 필요 시 03B 별도 통제), Gold58 Dev 및 standalone Public LB. 자세한 [RMIL-04 프로토콜](RMIL-04_FULL_DATA_EXECUTION_PROTOCOL_2026-10-10.md). **RMIL-04A/04B/04C 미실행을 완료라고 기록 금지.**

---

## 2026-10-10 — RMIL-03 A/B 2×2 학습 네 모델 완료, 최종 셀 오류 복구 분석 완료

**현재 상태:** A계정 03A/03B, B계정 03D/03C **4개 모델 학습 전부 GPU 종료코드 0**, 각 최고 Epoch `best.pt` Kaggle Output 로그에 저장. 사용자가 직접 ZIP 묶어서 제공. **최종 Notebook 비교 셀 오류:** 동일 초기 SHA에도 최초 `initial_forward_logits`가 FP32로 최대 1.78814e-7 차이인데 `==` 정밀 비교하여 `AssertionError ('설정 불일치','initial_forward_logits')`; **학습 무효 아님**. 후속 코드에서 이 설정 필드 제외 후 `np.allclose(...,atol=2e-5,rtol=0)`로 별도 검사. 학습 재실행 불필요.

| 모델 | Window | Series | Macro AUROC | Macro AUPRC |
|---|---|---|---:|---:|
| RMIL-03A | Mean | Mean | 0.560367 | 0.418299 |
| **RMIL-03B** | Target Window Attn | Mean | **0.562446** | **0.426945** |
| RMIL-03D | Mean | Target Series Attn | 0.550656 | 0.419531 |
| RMIL-03C | Target Window Attn | Target Series Attn | 0.560299 | 0.420671 |

**2×2 비교:** B−A Window 단독 **+0.002079 AUROC/+0.008646 AUPRC**; D−A Series 단독 **−0.009710 AUROC/+0.001232 AUPRC**; C−B Series 추가 **−0.002147 AUROC/−0.006274 AUPRC**; C−D Window 추가 **+0.009643 AUROC/+0.001140 AUPRC**. 03B가 RMIL-03 내부 최고이나 **기존 V3 K16 Mean 02C/02D 0.577856 AUROC/0.432300 AUPRC**는 못 넘었음. 02C/02D와 03은 예측 Head 구조가 달라 인과적 Attention 효과는 **03 내부 Pair로 비교**. 향후 최종 후보는 02D K16 Mean 우선 보존.

**독립 파일 QA:** A/B 수동 ZIP CRC PASS, 네 모델 `artifact_sha256.json` 선언 **총 78개 파일 SHA 일치**, 예측 58×12·12타깃 지표/최적 Epoch/공통 Worker SHA/Seed20261013/전체 초기 State SHA 검증 PASS. 단 Gold58 정답 Manifest와 네 실제 `best.pt`는 ZIP에 없어 원본 정답 대비 재계산 또는 체크포인트 바이트 검증 불가. 자동 Bootstrap CI 및 최종 ZIP은 마지막 셀 실패로 미생성; 보고서에 허위 CI 추가 금지. LABEL-V6 CANDIDATE_NOT_RELEASED 유지.

**상세 보고서:** [RMIL-03 4구조 완료 및 오류 복구 감사](RMIL-03_2X2_ATTENTION_COMPLETED_2026-10-10.md). **후속:** RMIL-03 구조 탐색 동결, 반복 Gold58 모델 선택 중단 또는 축소, 라벨 품질·학습 표본 규모·독립 검증 및 RMIL-04 전체 학습 계획 검토. 원본 픽셀 해상도 시험은 별도 축.

---

## 2026-10-10 — RMIL-03 2×2 통제 실험으로 A/B Notebook 교체 준비 (GPU 미실행)

**설계 변경 이유:** 과거 계정 B의 두 번째 `RMIL-03B Seed20261014` 반복은 재현성 검증에는 유용하지만, GPU4개를 한 번에 쓸 수 있는 상황에서 **새로운 RMIL-03D = Window Mean + 12질환별 Series Attention**을 탐색하는 편이 메커니즘 분리에 더 많은 정보를 줌. 기존 반복형 A/B Notebook **미실행 상태라면 새 2×2 A/B Notebook을 사용**. 이미 실행 중인 학습은 변경된 것처럼 표시하지 말고 그 결과를 별도로 보존.

| 계정/T4 | GPU0 | GPU1 | Seed |
|---|---|---|---|
| A | RMIL-03A: Window Mean / Series Mean | RMIL-03B: Target Window Attn / Series Mean | **20261013** |
| B | **RMIL-03D: Window Mean / Target Series Attn** | RMIL-03C: Target Window Attn / Target Series Attn | **20261013** |

**새 Notebook들 (독립 Kaggle GPU 실행 전; 기존 Notebook과 혼동 금지):**
- A: `RMIL-03_2x2_A_K16_Attention_T4x2_KO.ipynb`, SHA256 `4e87a2a5a4dd9c5827965b15727668ec191d04b08ce78302f99505735aae8556`
- B: `RMIL-03_2x2_B_K16_Attention_T4x2_KO.ipynb`, SHA256 `e768935cdfb8be785302f301c1a77cd5ffee07c2bd4f4b0ea6075b4d504ced0c`
- 두 Notebook 내 **동일한 Worker 소스 SHA256** `f0ec2d32c7d6170041e6de1a62ddcdde98aa721a400f98a6a989c04338502c03`, 동일 Seed/모델 초기 전체 State SHA 및 초기 Forward 동등 검사. 다른 Kaggle 세션 간 비트-동일 최종 재현은 보장하지 않지만 A/B 통제 조건 확인 후 교차 비교.
- Notebook nbformat / 모든 코드 셀 + Worker AST **PASS**, **CPU 합성 모델 테스트:** 4종(03A/03B/03D/03C) 초기 Model 전체 State 동등, Window/Series Attention Softmax 합 1, 12-logit 초기 출력 일치, 03D Series-only 및 03C 이중 Attention 기울기와 Encoder 기울기 전부 PASS. **실제 Kaggle 실험 결과 아직 미수령**.
- **Four-cell factorial:** Window 효과 03B−03A (Series Mean), 03C−03D (Series Attn); Series 효과 03D−03A (Window Mean), 03C−03B (Window Attn). 상호작용 `(03C−03D)−(03B−03A)`. 개발 검증 Gold58을 반복 사용하므로 작은 차이와 변수 선택편향 주의.
- V3 native224 K16 31,838 Windows / Train300 V4 soft-label confidence BCE / Gold58 / 2,006 Series·358명, full FT MedicalNet R34·CLS Transformer 동일. 입력 dataset 3개(캐시 / frozen manifest / pretrained) 모두 고정 경로, **/kaggle/input 전체 재귀 탐색 없음**. T4×2·Internet OFF·Save & Run All를 A/B 각 계정에서 수행. B 계정의 yhlucas 데이터셋 권한 확인. 운영상 Kaggle 계정별 GPU 용량/할당량 제약 확인.
- Save Version A `RMIL-03 2x2 A Window Effect T4x2`, B `RMIL-03 2x2 B Combined Effect T4x2`; 계정당 예상 65–140분 **미측정**. 각 계정 `RMIL-03-A_results_for_review.zip` / `RMIL-03-B_results_for_review.zip` + 실제 독립 `best.pt` 보존. **최종 계정 간 4-way 통합 지표/interaction/Bootstrap은 두 ZIP을 모두 받은 뒤 계산**.
- 기존 RMIL-03 2계정 `Seed 13/14` 반복형 버전은 **2×2 버전이 우선**이며, 두 실행 결과가 혼합되면 강력한 Pair 통제 비교로 주장하지 않음. LABEL-V6 미사용(`CANDIDATE_NOT_RELEASED`), Gold58 독립 테스트 아님.

---

## 2026-10-10 — RMIL-03 A/B 계정 동시 병렬 Notebook 준비 (GPU 실제 학습 전)

사용자가 **Kaggle 팀원 1명 추가로 두 계정(A/B), 계정당 T4×2 = 총 4GPU 동시 학습**이 가능하다고 확인함. A/B에 서로 다른 독립 Notebook 두 개 준비. **모든 기존 RMIL-01~02D 결과 동결.**

| Kaggle 계정 | 물리 GPU0 | 물리 GPU1 | Pair 내부 Seed | 독립 검증 질문 |
|---|---|---|---|---|
| **A** | `RMIL-03A-K16-MEAN`: 질환별 Head, Window Mean/Series Mean | `RMIL-03B-K16-TARGET_ATTN-seed13`: 질환별 Window Attention / Series Mean | **20261013** | Window Attention만 바꾸는 효과 |
| **B** | `RMIL-03B-K16-TARGET_ATTN-seed14`: 질환별 Window Attention / Series Mean | `RMIL-03C-K16-WINDOW_SERIES_ATTN`: 질환별 Window **+** 질환별 Series Attention | **20261014** | Window 구조 고정 후 Series Attention만 추가하는 효과 |

- A `RMIL-03_A_K16_Attention_T4x2_Parallel_KO.ipynb`, SHA-256 `91920eb52b194ab1462f06285370714395881c8c927d64c90c3c5fe3372d76c4`.
- B `RMIL-03_B_K16_Attention_T4x2_Parallel_KO.ipynb`, SHA-256 `9e4805b98fee62c5c7c81168cc6d0287e93e19e47be736854950a8af40573bb0`.
- **A와 B Notebook은 동일 Worker 코드** SHA-256 `a10ec735ee85cf64cebea90c846fd8324d07664ddf04e0f7b8757e6352e94a3d`. 동일 512-d ResNet34+공유 CLS Transformer+12질환 Head, 비교 Pair 안에서는 전체 초기 State SHA/첫 Study 출력 일치 검사. 모든 모델에 `nn.Linear(512,12)` 질환별 Window Attention과 `[12,512]` 질환별 Series Attention 매개변수를 동일하게 0으로 등록하되, 실험마다 필요한 Softmax 경로만 활성화. **A 계정 03A↔03B는 동일 Seed; B 계정 03B↔03C는 동일 Seed. 다른 Seed의 A03B↔B03C를 paired 비교하지 말 것.**
- **실행 전 검증:** Notebook nbformat / 전 코드 셀 AST / 내장 Worker AST / 공통 SHA 검사 통과, CPU 합성 실제 `StudyModel` Forward/Backward 3종(MEAN/TARGET_ATTN/TARGET_WINDOW_SERIES_ATTN), 12개 logit, 초기 3종 출력 일치, Window/Series/Encoder gradient, Attention Softmax 합 1 확인 통과. **실제 Kaggle T4 동작, 데이터셋 접근권 및 학습 완료는 미확인**.
- **입력 3개:** `yhlucas/rmil-02b-native224-v3` (고정 root `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`), `rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1`, `yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1/resnet_34.pth`. **B 계정에서 yhlucas 소유 Dataset을 실제 Add Input으로 읽을 수 있는지 필수 확인**. 비공개 개인 Dataset은 Notebook 팀원 권한과 다를 수 있음. 16 HDF5 shard/manifest/weight SHA 실제 검증.
- **공통:** V3 224px K16 (Train300 V4 soft/conf BCE, Gold58), ResNet34 Full FT, AdamW/Cosine/FP32, Epoch≤10/min5/patience3, T4×2, Internet OFF, Save & Run All. 예상 계정당 65~140분(**미측정**); 동시 가동은 Kaggle GPU 할당량/세션 정책 조건. `LABEL-V6` 후보 데이터 **사용 금지(CANDIDATE_NOT_RELEASED)**.
- **산출:** A `RMIL-03-A_results_for_review.zip`, B `RMIL-03-B_results_for_review.zip`. 4개 `best.pt`는 각 Kaggle Notebook Output에 보존하고 리뷰 ZIP에 미포함. Pair별 12질환 AUROC/AUPRC, 58×12 예측·출력 SHA/Bootstrap/Attention 진단·worker 로그, 03C에는 Series Attention Study×Target 진단 추가.
- 과거 공유한 단일 A 전용 `RMIL-03B_K16_TargetWindowAttention_vs_MatchedMean_T4x2_KO.ipynb`보다 **이번 A/B 공동 Worker 버전을 우선 사용**. 사용자에게 **둘 다 교체된 최종 A/B Notebook으로 실행**하도록 안내.

**후속:** A/B 두 ZIP 및 로그를 함께 받아 무결성/비교 → 조건부 해상도/Full-data 실험. Gold58 반복 개발 검증으로 일반화/임상 위치 입증 아님.

---

## 2026-10-10 — RMIL-03B 질환별 Window Attention Notebook 준비 완료 (GPU 미실행)

**파일:** `RMIL-03B_K16_TargetWindowAttention_vs_MatchedMean_T4x2_KO.ipynb`; SHA-256 `29e4a6b0cebb31ae957d9dcb01718a6503aeaf51478401ed9424b1249a315f60`. **Notebook/Worker 문법, CPU 합성 12질환 Forward·초기 Mean 동등·Encoder/Attention 역전파 테스트 통과. Kaggle GPU 학습 결과는 아직 없음.**

**단계:** RMIL-02D 완료 후 **RMIL-03B (질환별 Window Attention)**를 먼저 검증; **RMIL-03C (질환별 Series Attention)**는 다른 변수를 바꾸지 않는 별도 후속 실험으로 분리. GPU0=`RMIL-03A-K16-MEAN` **신규 matched Mean**, GPU1=`RMIL-03B-K16-TARGET_ATTN` **12개 질환별 Window Attention**. 양쪽에 **동일한 질환별 Target Projection/12개 Head**, **동일한 공유 Series CLS Transformer**, **동일한 균등 Series 집계**, 초기 Attention Linear(512→12) 가중치 전부 0, 전체 모델 초기 State SHA 및 첫 환자 초기 Logit 동등 검사. Attention의 12개 출력은 Window 축에서 별도 softmax되며 모든 질환의 Backbone은 하나로 공유. **과거 RMIL-02C/02D K16 Mean 0.577856은 아키텍처·Head 구성이 달라 1차 통제군으로 사용하지 않음.**

**입력/학습 고정:** 358명(Train300 V4/Gold58), 2006 Series, 66430 원본 Slice, `RMIL-02B-NATIVE224-V3` **공통 224px 캐시**, K16 총 31838 인접 3-Slice Window, MedicalNet-deflated R34 전체 FT, Seed20261013, AdamW cosine LR backbone1e-5/head5e-5, WD1e-4, Epoch≤10,min5,patience3, 4 Window microbatch/4 Study accumulation, T4×2, Internet OFF, Save & Run All. 입력 3개 Kaggle datasets는 RMIL-02D와 동일. Save Version: `RMIL-03B K16 TargetAttn vs Mean T4x2`. 실행 예상 약 65~140분 **미실측**.

**Output:** `RMIL-03A-K16-MEAN/best.pt`, `RMIL-03B-K16-TARGET_ATTN/best.pt`는 Notebook Output에 유지. 검토용 `RMIL-03B_results_for_review.zip`에는 각 Epoch AUROC/AUPRC/예측·12타깃별 메트릭·Target별 집중도·1000회 쌍체 Gold58 Bootstrap CI·콘솔 로그/설정/SHA만 저장. HDF5 16 Shard 실제 SHA, GPU 할당, 모든 질환·Gold 58명, Attention 합계1, 초기 공통 SHA/첫 예측 동등, ZIP CRC를 실제 실행에서 검증. Gold58은 **반복된 개발 검증**, 독립 일반화·Public LB 지표가 아님.

**다음:** Kaggle 실행 후 결과 ZIP·로그 수령 → 독립 검증 → RMIL-03C 진행 여부 판단. LABEL-V6는 현재 사용하지 않으며 `CANDIDATE_NOT_RELEASED` 유지. 원본 해상도 320/384/Native 실험은 Attention 효과와 분리해서 추후 비교.

---

## 2026-10-10 — RMIL-02D 완료·독립 검증: K16 Shared Attention < K16 Mean

**최신 확정 단계: RMIL-02D 두 모델 Kaggle Save & Run All 완료/PASS.** `RMIL-02D_results_for_review.zip` SHA256 `67badca393c11ab7664ca2e8f120e5e93181209a8e96f784bb9bc020377373c8`; ZIP 57파일 CRC PASS, 선언된 **49개 산출물 SHA256 일치**, 58×12 예측·매크로·최적 Epoch·336 GOLD Series Attention 진단 및 공통 초기 가중치 SHA 검증 PASS. K16 Mean의 58×12 예측은 RMIL-02C K16 Mean과 **파일 SHA까지 동일**(정확히 재현).

| V3 동일 캐시·동일 K16 | Macro AUROC | Macro AUPRC(최적 AUROC Epoch) | Best Epoch | 전체 Epoch |
|---|---:|---:|---:|---:|
| **Mean** | **0.577856** | **0.432300** | 5 | 8 |
| Shared Window Attention | 0.564698 | 0.415525 | 9 | 10 |
| Attention − Mean | **−0.013158** | **−0.016775** | | |

Attention은 개선 AUROC 5/12 질환, 악화 7/12. 가장 크게 악화한 Effusion **−0.13416**, 개선한 Fracture **+0.07222**, Lateral OA **+0.07544**, Medial OA **+0.05736**. 실효 Window 평균 **12.888개**, 가중치 엔트로피 **0.94243**, top1 평균 **0.10395**(균등 **0.06367**); Attention은 실제로 학습했으나 전체 성능을 높이지 못함. **일괄 Shared Scalar Attention 승격 보류**.

**다음 실험:** RMIL-03 (K16 V3 동일 조건, 질환별 Window Attention → 질환별 Window+Series Attention) 순차 검증; 개선 효과가 불확실하므로 재현성·샘플 크기 점검. 이후 RMIL-04 전체4,349명 학습 및 Standalone 제출. RMIL-05 2D/MIL 및 RMIL-06 3D 결합은 실제 보완 증거가 있을 때만. 고해상도 320/384/original-varying은 Attention 실험과 분리된 선택적 변수.

**전체 7개 RMIL-01/02C/02D 모델 성능 및 12개 질환별 상세:** [RMIL-02D 완료 통합 보고서](RMIL-02D_K16_MEAN_VS_SHARED_ATTENTION_COMPLETED_2026-10-10.md). **RMIL-01 K4는 다른 픽셀 전처리이므로 V3 순위에 직접 포함 금지.** Gold58 반복 개발 검증으로 통계적 일반화, Public LB 점수 주장 금지. 코드 디버깅 이력은 작성하지 않음.

---

## 2026-10-10 — RMIL-02D K16 Mean vs Shared Window Attention 준비 완료

**현재 단계:** RMIL-02C의 K4/K16/K24 Mean 학습·검증은 모두 완료. K16이 Gold58 Macro AUROC **0.577856**, AUPRC **0.432300**으로 상대적 최고이나 K4 대비 증가는 **+0.003437**이며 개발 검증 Gold58 재사용에 주의.

**다음 RMIL-02D — 실행 전 준비 완료:** 한글 Kaggle Notebook `RMIL-02D_K16_Mean_vs_SharedWindowAttention_T4x2_KO.ipynb` SHA-256 `64e6a086bb4d24c1a449b24c0d3e07a16b0e4db9d8de3eddce073cf604e96d06`. **GPU 학습·검증 결과는 아직 없음**. 새 Mean(K16)과 새 Shared Window Attention(K16)을 **T4×2의 GPU0/GPU1에서 병렬 학습**해 Pooling 효과만 비교. 기존 RMIL-02C K16 체크포인트의 성능은 참고하고 공정한 Pair의 Mean을 이번 실험에서 새로 학습함. Attention은 **Series 내 Window마다 공유 스칼라 Linear→Softmax 가중 평균, 0 초기화**(학습 시작 시 Mean 동일)이며 질환별 Attention이 아님.

**고정 조건:** 새 RMIL-02B V3 이미지 캐시, Train300 V4 soft/conf weighted BCE, Gold58, 동일 K16 선택(전체 31,838 Window), 전체 2,006 Series, MedicalNet3D→ResNet34 deflation Option-A, 512차원/2층/8헤드 메타데이터 Transformer, Backbone full FT, Seed20261013, AdamW, cosine LR, 10 Epoch/최소5/patience3, Window microbatch4, Study accumulation4. 양쪽의 **공통 초기 State SHA**와 16개 HDF5 샤드 SHA/데이터 분리·동일 학습 설정 확인을 강제.

**Kaggle Add Input 3개:** (1) `rmil-02b-native224-v3` → `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`; (2) `rsna-knee-wide224-persistent-cache-v1` → `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1`; (3) `rsna-knee-r3d-medicalnet-pretrained-v1` → `/kaggle/input/datasets/yhlucas/rsna-knee-r3d-medicalnet-pretrained-v1/resnet_34.pth`. **T4×2, Internet OFF, Run All**, Save Version `RMIL-02D K16 Mean vs SharedAttn T4x2`. 예상 소요 55~110분(실측 전).

**출력:** `RMIL-02D-K16-MEAN/`와 `RMIL-02D-K16-ATTN/`의 별도 `best.pt`, 학습곡선·질환별 AUROC/AUPRC·Gold58 예측, Attention 최고 Epoch의 Series별 최대 가중치·엔트로피·실효 K 등 진단. `RMIL-02D_results_for_review.zip`는 메타데이터·로그만 보존, 모델은 Kaggle Output에 유지. Attention 가중치 자체를 병변 위치의 증거로 해석하지 않음.

**Notebook 사전 검사:** nbformat 및 각 코드 셀/내장 Worker 문법 PASS, CPU 합성 네트워크에서 가변 Window 수의 초기 Mean/Attention 출력 일치·초기 공통 가중치 동등·Attention/Encoder 역전파 PASS. 이것은 실제 Kaggle 결과가 아님.

**이후:** RMIL-02D 결과 검증 → 개선이 있더라도 재현성/시간비용 검토 → 필요 시 RMIL-03 질환별 Attention 테스트. 이전 실험 결과를 재판정하거나 수정하지 않으며 단순 코드 오류 이력도 GitHub에 별도 작성하지 않음.

---

## 2026-10-10 — RMIL-02C 완료: K4·K16·K24 Mean 통제 비교

**완료 상태:** T4×2에서 K4·K16·K24 3개 Mean 모델 모두 정상 학습·Gold58 평가·ZIP 산출 완료. 수령 ZIP 70개 항목 CRC 및 60개 산출물 SHA-256 **독립 검증 통과**. 캐시 `rmil-02b-native224-v3`의 HDF5 **16개 실제 SHA-256 Kaggle 재검사 PASS**. 358명(Train300/Gold58), 2,006 Series, 66,430 Slice, seed20261013, MedicalNet-deflated R34 2.5D+Transformer, 동일 학습 설정. 이전 RMIL-01 K4 값은 픽셀 전처리가 달라 직접 비교하지 않음.

| 지표 | K4 | K16 | K24 |
|---|---:|---:|---:|
| Gold58 Macro AUROC | 0.574420 | **0.577856** | 0.577402 |
| Gold58 Macro AUPRC(최적 AUROC Epoch에서) | 0.428417 | **0.432300** | 0.425870 |
| 최고 AUROC Epoch / 전체 Epoch | 4/7 | 5/8 | 3/6 |
| 학습 시간(분) | 20.92 | 54.53 | 55.51 |

K16은 K4보다 AUROC +0.003437, K24보다 +0.000454; K16/24 Window 증가로 큰 전체 성능 개선은 관찰되지 않음. 질환별 최고 AUROC는 K4·K16·K24 각각 4/12개. K16 Effusion +0.052, K24 Medial OA +0.093(모두 K4 대비); Lateral Meniscus와 Fracture는 큰 K에서 약화. **AUPRC의 단독 최고 Epoch는 AUROC 최적 Epoch와 다르므로 지표별 서로 다른 Epoch 점수를 결합하지 않음**. Gold58 반복 소규모 개발 검증으로 유의성·일반화 증명 불가.

**다음:** RMIL-02D는 우선 **K16 Mean vs K16 Shared Window Attention**으로 같은 V3 공통 캐시/윈도우/모델 계약에서 pooling 효과를 격리. K24의 질환별 이점은 탐색적으로 보존하되 전면 채택하지 않음. 실제 GPU 실행 전 Notebook 필요. [질환별 AUROC/AUPRC·Epoch·자원·무결성 전체 결과](RMIL-02C_K4_K16_K24_MEAN_COMPLETED_2026-10-10.md).

---

**RMIL-02C 캐시 입력 경로 확정 (2026-10-10):** 사용자가 Kaggle Dataset `yhlucas/rmil-02b-native224-v3`로 등록했으며 정확한 하위 폴더는 `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`입니다. 후속 K4·K16·K24 학습은 **이 경로 하나만 사용**하고 그 안의 `shards/shard_000.h5`~`shard_015.h5`, `series_index.csv`, `k_selection.jsonl`, `cache_contract.json`, `shard_sha256.csv`를 실행 전에 검사합니다. 경로를 고정한 한글 Notebook은 `RMIL-02C_K4_K16_K24_Mean_T4x2_경로확정.ipynb` (SHA-256 `44c92cac63126c5b477ed0a1864c473587df14a0fc19dce56374930e68898e4d`); 코드 문법 검증 PASS, **Kaggle GPU 실행은 아직 미검증**입니다.

## 2026-10-10 — 최신 결과: RMIL-02B 공통 영상 캐시 생성 완료

**실험 결과:** RMIL-02B V3 Kaggle CPU 전체 실행 **완료** (`PASS_NEW_PREPROCESS_V3`). Train300 + Gold58 **358명**, **2,006 Series**, **66,430 Slice**의 원본 MRI로 공통 224×224 `uint8` 캐시를 생성했습니다. HDF5 **16개 샤드**, 전체 파일 크기 **3,341,400,768 bytes(약 3.34GB)**, 실제 실행 시간 **23.41분**. 개별 샤드는 Kaggle 실행 과정에서 저장 후 읽기·SHA 검증을 수행했습니다.

**독립 감사:** 제공받은 `RMIL-02B_V3_results_for_review.zip` SHA-256 `f21f454542b47c99e3ef4d1503c191a5d1e006387c8d0e5e81e7cd320625fdd8`. ZIP CRC PASS, **메타데이터 7개 파일 SHA 전부 일치**, Study/Series UID 중복 0, 2,006개 Series의 실제 Slice 수·K 중첩/유효 Window·물리 정렬 재검사 오류 0. 단, **영상 HDF5 자체 바이트는 ZIP에 없으므로 독립 SHA 재계산 미완료**. 다음 학습 Notebook은 마운트된 16개 영상 샤드를 다시 SHA 검증합니다.

**K별 실제 Window:** K4 **8,024**, K16 **31,838**, K24 **45,472**, K32 **53,532**(보류). **130mm FOV 바깥 배경 패딩은 24/2,006 Series**, 20% 이상 16개(모두 Axial), 최고 61.14%. 이 패딩 분포는 영상 조건상 확인된 데이터 특성으로 기록하며 임의 제외하지 않습니다.

**다음 단계 — RMIL-02C:** 한글 Notebook `RMIL-02C_K4_K16_K24_Mean_Train300_T4x2_KO.ipynb` (SHA-256 `627aa87ab7327bfdb6eb6be55e6d96503f02aa5f1c03e3dd85e5e8bd708c2c18`) 준비, Kaggle GPU 실행 **전**. Add Input **3개**: 완료된 RMIL-02B V3 Notebook Output 전체(16개 HDF5 샤드 포함), 기존 `rsna-knee-wide224-persistent-cache-v1` frozen Train300/Gold58 메타데이터, `rsna-knee-r3d-medicalnet-pretrained-v1` MedicalNet R34 가중치. **T4×2, Internet OFF, Run All**. GPU0 K4→K16, GPU1 K24, 모두 MedicalNet-deflated R34 2.5D + 메타데이터 Transformer, Train300 V4 soft/conf weighted BCE, Gold58, full fine tune, Mean pooling 및 동일 optimizer/seed 사용. 코드 셀/Worker 문법과 가변 Window HDF5 합성 검사는 PASS이나 **실제 T4 실행 검증 전**이며 성능 결과는 없음. 결과 ZIP `RMIL-02C_results_for_review.zip`에 모델이 아닌 성능·예측·로그를 담고 best.pt는 Output에 각각 보존합니다.

완료 캐시 자세한 검증: [RMIL-02B V3 완료 결과](RMIL-02B_V3_CACHE_COMPLETED_2026-10-10.md). 기존 RMIL-01 K4는 서로 다른 영상 전처리이므로 이번 K4의 비교 기준으로 사용하지 않습니다. 코드 오류 수정 내역은 별도 GitHub 기록으로 만들지 않습니다.

---

## 2026-10-10 — RMIL-02B 현재 진행 상태

**진행 단계:** 358명(Train300 + Gold58), 2,006개 Series, 66,430개 Slice를 대상으로 **공통 224×224 단일 채널 캐시**를 생성하는 단계입니다. 현재 사용할 한글 설명판 Notebook은 `RMIL-02B_V3_Native224_FOVSafe_SharedCache_CPU_KO.ipynb` (SHA-256 `3c73cda26e664eb0fbcbd71c9041c7eea658028c896878e03ffb437e30de7753`)이며, **Kaggle 최종 실행 결과는 아직 검증되지 않았습니다.**

**데이터 처리 조건:** 원본 DICOM의 물리적 Slice 순서, 130mm 기준 Crop과 영상 바깥 영역 패딩, Series 단위 정규화, K4 ⊆ K16 ⊆ K24 선택을 동일하게 적용합니다. 생성 파일은 14GB 내부 출력 한도 이내에서 HDF5 샤드로 관리합니다.

**다음 단계:** 캐시 실행 로그 및 검증용 결과 ZIP 확인 → 새로운 공통 전처리 기준의 K4·K16·K24 Mean 학습 → 동일 K에서 Mean·Attention 비교. 과거 RMIL-01의 K4 점수를 새로운 전처리의 비교 기준으로 사용하지 않습니다.

---

# RSNA Knee — Current Experiment State & Roadmap


## 2026-10-10 — RMIL-02B0 COMPLETED; RMIL-02B New V2 cache prepared (OVERRIDES older K4 parity hard gate)

**Actual artifact audit PASS**, but **K4 image parity FAIL**: ZIP SHA256 `3f7ee4b7a12db3b0297ed3d11eebce31133d4bc87adeb08687df4ece33c06a27`, CRC PASS, all 5 declared output SHA pass. Diagnostic 9 Series across 3 Studies / 144 candidate pixel transformations, ZERO exact entire-Series matches, best mean MAE 8.476386 and byte match fraction ~0.153%. No cache pixel output, no GPU; existing RMIL-01 score unchanged. **[Detailed completed RMIL-02B0 audit](RMIL-02B0_COMPLETED_PARITY_AUDIT_2026-10-10.md).**

**Decision to avoid repeated uncertain cache-builder archaeology:** original R2D-CACHE-01 exact pixel implementation NOT available; freeze newly specified and reproducible **`RMIL-02B-NATIVE224-V2` preprocessing** for the same 358 Study original DICOM source instead. **A fresh `RMIL-02C-K4-NEW` training baseline is MANDATORY** before interpreting K16 and K24 count effect. Old RMIL-01 0.576370 is historical only; cannot substitute as K4 for new V2. Within new V2 cache compare K4 Mean, K16 Mean, K24 Mean (K32 conditional) from nested selected native Slice center windows, then at matched K compare Mean vs shared attention. RMIL-03 later.

**Prepared new CPU notebook (NOT Kaggle-executed)** `RMIL-02B_Native224_SharedCache_CPU.ipynb`, SHA256 `097c72a070114caa53603180f9813ec16c3edf15ab7dc1ff84c30a279cbc080b`, syntax/nbformat PASS, synthetic nested selector 310 source lengths PASS. Accelerator None, Internet OFF, Save & Run All, 2 existing inputs (competition + `rsna-knee-wide224-persistent-cache-v1`); 358 studies / 2006 Series / 66430 real slices. V2 preproc exact contract spelled out in notebook and [audit](RMIL-02B0_COMPLETED_PARITY_AUDIT_2026-10-10.md), **NOT claimed historical image parity**. Output `RMIL-02B_NATIVE224_V2/shards/shard_###.h5` 220MB-target SHA/atomic, manifest and metadata-only ZIP `RMIL-02B_results_for_review.zip`; keep whole Kaggle Notebook output as next model Input. Kaggle saved output all-working total 14.0GB project cap, ≥2GB physical free. Actual pixels not yet created and GPU experiments not run.

---

## 2026-10-10 — RMIL-02A ACTUAL RESULTS VERIFIED (supersedes previous 'unexecuted 02A' below)

**COMPLETED/PASS_METADATA_PREFLIGHT.** Actual user-supplied `RMIL-02A_results_for_review.zip` independently CRC+all 9 declared file SHA PASS; received ZIP SHA256 `fbabf2840be680d62c636f86af5e4bb1cc87a3c6c2619fe875d0dfca6008520f`. Kaggle CPU preflight on frozen **358 Studies/2006 Series/66430 native Slices**, **0 issues**, DICOM sample decode PASS, ~11.254min header survey. Actual K full Series: 4 **2006**, 16 **1924**, 24 **1513**, 32 **516**. Real unique windows K4 **8024**, K16 **31838**, K24 **45472**, K32 **53532**. **Recommended first mean-only K16 vs K24**, K32 conditional: 1490/2006 Series cannot fill K32. Verified legacy K4 centers exactly fit **`round(linspace(.1*(N-1),.9*(N-1),4))` for all 2006 Series** (metadata indices only; orientation/pixel parity still NOT verified).

**Disk:** 66430×224² uint8 single-channel = **3.104277GiB** pixel bytes; projected *future cache peak* **4.633149184GB decimal**, safely under project **14.0GB all-working-files cap** (runtime effective remaining **13.983781468GB**). This is a budget eligibility projection, not actual generated image-cache bytes. **No new pixel cache created; no new GPU/Gold AUROC results.** The original K4 image transform parity is a HARD GATE.

**NEXT = RMIL-02B0 (prepared, not executed),** `RMIL-02B0_K4_Pixel_Parity_Probe_CPU.ipynb`, local SHA256 `0bf941097a3bdd5db04b4093f6dfe7e853127b5704011db5cbe98251a209804c`: same two Kaggle inputs, CPU only, diagnostic sample comparison for physical order, Crop130, percentiles, normalization and quantization. Only after the actual original R2D-CACHE-01 implementation (preferable) / strict K4 parity is verified may RMIL-02B **358-Study native pixel shards** be built. RMIL-01 is completed and immutable; RMIL-03 after higher K data+shared Attention ablation. Details: [RMIL-02A completed metadata and K feasibility audit](RMIL-02A_COMPLETED_METADATA_AUDIT_2026-10-10.md).

---

## 2026-10-10 — MANDATORY RMIL-02 20GB output guard

**RMIL-02A CPU metadata preflight notebook revised with disk budget evaluation:** `RMIL-02A_Native_Slice_Preflight_DiskSafe_CPU.ipynb` SHA256 `1516660b1d413aa384a193122593aad21d057832c4405a64be9d9e9e973204dd`; **not executed**. `disk_budget.json` estimates cache size and checks `/kaggle/working` effective space. Kaggle documents **20GB** saved Notebook output; project caps ALL saved working files at **14.0GB decimal**, reserves free disk margin, stores one channel/native slice, targets 256–512MB atomic shards and metadata-only ZIP, rejects/splits cache when estimated or actual bytes exceed budget. Details in [RMIL-02/03 protocol](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md). RMIL-01 remains completed.

---

## 2026-10-10 — UPDATED RMIL-02/03 K-VS-ATTENTION PROTOCOL (SUPERSEDES PRIOR NEXT BELOW)

**NEXT = RMIL-02A CPU metadata/geometry/asset preflight ONLY** (prepared Notebook, not run), then **RMIL-02B** native Slice cache creation after K4 parity validation, then **RMIL-02C** K-Mean count test and same-K Mean-vs-shared-ATTN test. DICOM input mount must be confirmed; no new high-res full Slice cache already verified. Old `R2D_SHARED224_V1` contains only 4 windows/Series; existing R3D caches are D24×96, and Exp16B full-MRI feature cache does not store source pixels. Use exact competition path candidates and source asset checks, never global `/kaggle/input` recursive search. **[Full approved plan and uncertainty/QA gates](RMIL_02_03_NATIVE_WINDOW_CONTROLLED_PROTOCOL_2026-10-10.md).**

**Two isolated hypotheses:** K effect from K4/16/24/32 with MEAN constant, and Attention effect in matched *same K* MEAN-vs-shared-ATTN (K24/32 conditional on CPU audit). Preserve K4 legacy input parity. No RMIL-01 rerun. RMIL-03 separate target-window then target-window+Series comparison at chosen K; no unseen results claimed. All C1/C2/C3, fold/blend decisions remain pending; best Public LB Exp57 0.918. Older stale NEXT text below is archived.

---

## 2026-10-10 — CURRENT ACTIVE WORK: RMIL-02 CPU coverage preflight (overrides old RMIL-01 NEXT below)

**RMIL-01 COMPLETED / AUDITED:** [actual received ZIP/target metrics audit](RMIL-01_COMPLETED_AUDIT_2026-10-10.md). GPU0 MEAN Gold58 AUROC **0.5763704369**, AUPRC **0.4507296488**, best E4; GPU1 shared 4-window ATTN AUROC **0.5442963023**, AUPRC **0.4158921311**, best E3. Differences **−0.0320741346 AUROC**, **−0.0348375177 AUPRC** (ATTN minus MEAN); 4/12 target AUROC improvements, 8/12 declines. Both workers PASS; review ZIP 43 entries, all 38 declared artifact hashes PASS, source ZIP SHA recorded. Checkpoint bytes/Gold58 label manifest absent from ZIP; this is non-independent Gold development validation only. **MEAN retained as comparator**, shared ATTN not promoted.

**NEXT, UNEXECUTED RMIL-02:** CPU-only actual-Slice 16/24/32 windows-per-Series candidate cache design/preflight, geometry sorting, adjacency, deduplication, window coverage, SHA and persistent storage/runtime budget. Separate window count from selection policy, preserve Train300/Gold58 split and controlled MEAN model optimization for subsequent GPU ablation. Do not launch GPU for raw DICOM decoding; do not falsely claim dataset prepared.

**Unchanged:** RMIL-03 target-specific Window/Series MIL later; RMIL-04 full4349 after pilots; optional RMIL-05 2D and RMIL-06 3D only with repeatable added value. C1/C2/C3 all undecided. No 3/5-Fold or Exp57 automatic blend. Best verified project Public LB Exp57 **0.918**, unchanged. Old 'RMIL-01 immediate next' below superseded.

---

## 2026-10-10 — CURRENT ACTIVE WORK: RMIL-01 Window Pooling (supersedes all older future tasks below)

**Immediate next:** `RMIL-01`, controlled **2.5D R34 MEAN vs learned Window Attention**, Train300/Gold58, frozen shared 224×224 cache, T4×2, Internet OFF. Notebook prepared, **no Kaggle results yet**. Existing `EXP-01` name already occupied. GPU0=MEAN / GPU1=ATTN. Zero-init attention = initial Mean; only pooled feature selection changes. Read [RMIL experiment contract & architecture candidates](RMIL_FINAL_ARCHITECTURE_AND_EXPERIMENT_PLAN.md) FIRST.

**New active research order:** RMIL-01 pooling → RMIL-02 high-coverage actual Slice cache → RMIL-03 target-specific Window+Series Attention → RMIL-04 full4349 single expert and standalone LB → RMIL-05 optional 2D complementary expert → RMIL-06 optional 3D complementary expert.

**Three UNDECIDED final configurations:** C1 **one 2.5D target-aware MIL CNN**, C2 **2D+2.5D**, C3 **2D+2.5D+3D** (3D contingent on independent gain). **No committed 3/5-Fold or Exp57 ensemble**, since >10 models could be inefficient. Exp57 **Public LB 0.918** preserved as benchmark, not mandatory part of final. V6 label candidate not canonical until audited.

**Recently completed and now logged:** R2D-SHARED 4, RDINO-01 4, R3D-15 3 (11 actual results); see [full 11 ZIP SHA audit and metrics](R2D_RDINO_R3D15_COMPLETED_AUDIT_2026-10-10.md). Most favorable Train300/Gold58 score R2D-SHARED-A-25D AUROC **0.57637044**, not comparable to Exp57 Public LB 0.918. R3D-14V4 standalone user-reported Public LB **0.689** also completed; earlier below-text describing R3D-12/R3D-14 as 'NEXT' is historical and superseded.

---

최종 업데이트: **2026-10-10**

이 문서는 **현재 상태와 다음 작업만 기록하는 기준 문서**다.
오래된 계획/상태를 아래에 누적하지 않는다.

- 완료된 실험의 상세 기록: [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md)
- 앞으로의 R3D 실행 계획: [3D_RESNET_EXPERIMENT_PLAN.md](3D_RESNET_EXPERIMENT_PLAN.md)
- Kaggle Notebook 작성/복구 규칙: [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
- 새 채팅 인수인계: [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md)

이 문서와 위 3개 문서가 과거 README / Specialist 문서의 오래된 "현재 다음" 문구보다 우선한다.

## 2026-10-08 — 병렬 작업 결정: 기존 V4로 R3D 선행 학습

**현재 Kaggle/R3D lane의 다음 작업은 V6를 기다리는 것이 아니라 V4 baseline을 먼저 완성하는 것이다.**
새 LABEL-V6 라벨링은 별도 GPT-6 채팅에서 병렬 진행하며, 이 결정은 기존 frozen Main 구조나 R3D-12CACHE 완료 상태를 바꾸지 않는다.

1. **R3D-12V4DATA:** 기존 V4 Routed Broad / official Gold58 / R3D-12CACHE full-volume Kaggle Input 검증 및 label-distribution/loss/runtime preflight (CPU 우선, GPU smoke/profile만 별도).
2. **R3D-13V4:** MedicalNet R34 pretrained에서 단일 Main을 새로 학습. Train=V4 report-only4349 (soft target + confidence), validation=Gold58 (학습 제외).
3. **R3D-14V4:** standalone hidden-test Kaggle LB 제출. Exp57 Public LB 0.918과 비교.
4. **LABEL-V6 canonical release 이후:** 같은 구조/seed/budget/검증으로 R3D-13V6를 처음부터 학습 → R3D-14V6 standalone → V4/V6 target별/전체 비교.
5. 별도의 합의 근거가 생긴 경우에만 Exp57 blend, 선택적 3/5fold 확장. 과거 pseudo-only specialist/구 구조 탐색 반복 금지.

**경계조건:** R3D-12CACHE raw volume 생성+로컬 audit PASS이나 10.04GiB 전체 Kaggle Dataset 등록과 정확한 mount root는 아직 독립 확인되지 않았다. V4 broad all 52,188 target soft scores non-null, strict 39,792 non-null. V4 routing은 과거 Gold57을 사용했으므로 Gold58 validation은 독립 test가 아니다. V4와 V6의 first-run은 가능한 한 라벨 이외 요인을 고정해야 공정하게 비교할 수 있다.

상세 실행·비교 계약: [R3D_V4_V6_CONTROLLED_COMPARISON_PLAN.md](R3D_V4_V6_CONTROLLED_COMPARISON_PLAN.md).


---

# 1. 현재 프로젝트 기준점

## Public Leaderboard

현재 프로젝트 최고 Public LB:

- **0.918**
- **Exp57 — 3-Fold B3A + 3-Fold Full-MRI Direct 70:30 Hybrid**

Exp57은 단순 2D 모델이 아니다.

요약 구조:

~~~text
전체 MRI 모든 Series / 3-slice windows
        ↓
Fold별 task-tuned DINOv2-Base
        ↓
Fold별 Full-MRI Hierarchical MIL
        ├─ Direct probability branch
        └─ attention으로 환자별 Top-24 raw windows 선택
                    ↓
          Fold별 B3A end-to-end model

P_B3A_3F    = mean(F0, F1, F2)
P_DIRECT_3F = mean(F0, F1, F2)

P_FINAL = 0.70 × P_B3A_3F + 0.30 × P_DIRECT_3F
~~~

- Exp57 Public LB = **0.918**
- SS08 Specialist-only Public LB = **0.876**
- 따라서 R3D는 최종적으로 Exp57과 **상보적 ensemble** 가능성까지 확인해야 한다.

---

# 2. 현재 R3D 한 줄 상태

현재 Main R3D:

~~~text
ALL Series
→ 130 mm physical center crop
→ interpolated D24 × 96 × 96
→ MedicalNet R34
→ GLOB
→ metadata embedding
→ Transformer + shared CLS
→ 12 target heads
~~~

현재 고정값:

- Series policy: **ALL**
- physical FOV: **130 mm center crop**
- depth: **interpolated D24**
- in-plane: **96×96**
- Backbone: **MedicalNet R34**
- Representation: **GLOB**
- Anatomy mask: **OFF**
- Aggregator: **Transformer + shared CLS**
- Full fine-tuning
- pure FP32
- BatchNorm running stats frozen
- Backbone LR: **1e-5**
- New-layer LR: **5e-5**
- Weight Decay: **1e-4**

## R3D-11 결과 검토 — 2026-10-08

- 대상: **Medial Meniscus 단일 target**. 아래 AUROC/AUPRC는 12-target Macro 값이 아니다.
- Pipeline / paired contracts: **PASS**. 자동 adoption_status: **REVIEW_REQUIRED**.
- 검토 결론: **SAG1은 유망 후보로 보존하되 최종 specialist 채택·hard routing은 보류**. Main은 ALL 유지. 이번 결과만으로 specialist 추가 학습을 시작하지 않는다.

| Scope | ALL AUROC | SAG1 AUROC | ΔAUROC | ALL AUPRC | SAG1 AUPRC |
|---|---:|---:|---:|---:|---:|
| F0 | 0.531250 | 0.697917 | +0.166667 | 0.426910 | 0.618876 |
| F1 | 0.555556 | 0.777778 | +0.222222 | 0.649439 | 0.823719 |
| F2 | 0.659091 | 0.738636 | +0.079545 | 0.730888 | 0.770433 |
| Pooled Gold58 OOF | 0.582933 | 0.606971 | +0.024038 | 0.553281 | 0.599431 |

해석:

- 세 fold 모두 AUROC/AUPRC 개선. Pooled AUPRC Δ = **+0.046150**.
- Pooled AUROC 차이의 descriptive paired bootstrap 95% 구간: **[-0.193510, +0.238011]**. 선택된 checkpoint에 조건부이며 epoch/구조 선택 및 fold 간 의존성을 보정한 독립 검정이 아니다. 우월성 확정 불가.
- Fold마다 점수 분포가 달라 fold 내부 순위 개선이 pooled 순위 개선으로 그대로 이어지지 않는다. SAG1 F0 확률 범위 **0.44657543–0.44822356**으로 매우 좁다. ALL F1은 전원 0.5 초과. 원인 확정은 하지 않으며 calibration/학습 안정성 점검 대상이다.
- SAG1 pooled threshold 0.5 sensitivity **0.076923**, specificity **1.0**. 높은 fold AUROC만으로 임계값 성능이나 확률 품질을 보장하지 않는다. Gold58에 사후 calibration을 맞춰 개선으로 보고하지 않는다.
- Gold58은 epoch 선택과 반복 실험에 사용된 model-selection validation이다. 독립 최종 test로 부르지 않는다.

재현·검증:

- Gold58 unique UID, 양성26/음성32. 저장 OOF 예측에서 pooled AUROC/AUPRC를 재계산해 metrics.csv와 일치 확인.
- Canonical MedicalNet R34 pretrained matched fraction 1.0; Crop130 interpolated D24×96×96; FP32; BN stats frozen; MASK_OFF.
- 각 fold ALL/SAG1의 초기 모델 SHA, study sampling trace, 공통 SAG1 증강 trace 일치. 세 paired contracts PASS.
- 10 epochs × 192 study draws; fold-specific Pseudo1000 + training Gold; Gold sampling probability .25; accumulation4. 실제 unique sampled studies F0 799/F1 788/F2 788.
- 매 epoch 종료 후 validation. AUROC 우선/AUPRC tie-break. ALL best epoch F0/F1/F2 = **5/3/6**, SAG1 = **6/8/4**.
- ALL runtime 약 **32.3–32.9분/fold**, SAG1 **6.8–7.0분/fold**. 병렬 실행 조건의 관측치이며 최종 full-data 시간 추정으로 직접 쓰지 않는다.
- Historical normalized weighted BCE 유지: 단일 target의 양수 scalar weight는 분자/분모에서 상쇄된다. pseudo .35 및 confidence가 의도한 sample attenuation으로 작동한다고 해석하지 않는다. 최종 학습에서 unknown mask와 loss 정규화를 명시적으로 재설계한다.
- 여섯 best.pt는 search 산출물. 최종 모델 초기화에 재사용하지 않는다.
- 결과 원본: `A_R3D-11_results_no_pt.zip`; SHA256 `b6bd762858cc581b6f025dd9d155292f67c817f554d2f1f2479658a669af8848`.

## 확정된 최종 학습 방향

- **단일 Main R3D 모델**, 3-fold 최종 학습 아님. 기존 3-fold는 구조 비교용이었다.
- 학습 범위: **report-only 4,349 studies 전체**. 검증: **공식 Gold58 전원**, 학습에서 제외.
- 신규 라벨에서 supervision이 전혀 없는 study는 손실에 기여할 수 없다. 실제 유효 supervision 수는 audit 후 별도로 기록한다.
- Main: ALL → Crop130 → interpolated D24×96×96 → MedicalNet R34 → GLOB + metadata → Transformer/shared CLS → 12 heads.
- Search best.pt를 이어 학습하지 않고 MedicalNet pretrained에서 새로 시작한다.
- Epoch은 전체 학습 목록 순회를 기준으로 한다. 192 draws/epoch search budget을 최종 학습에 그대로 적용하지 않는다.
- Epoch 종료 시 Gold58 12-target Macro AUROC 우선, Macro AUPRC tie-break로 best.pt 선정. Epoch 수/compute budget/unknown mask 및 loss 정규화의 구체 구현은 아직 확정 전.
- Gold58은 이미 반복 탐색에 사용되었으므로 untouched test가 아니다.
- 먼저 standalone R3D Public LB 확인, 이후 Exp57(0.918)과 ensemble 상보성 검토. SAG1은 보류 후보이며 자동 추가하지 않는다.

## 바로 다음 작업

1. **Competition-aligned report label policy v2 freeze 완료**: [LABEL_RECONSTRUCTION_POLICY_V2.md](LABEL_RECONSTRUCTION_POLICY_V2.md).
2. Qwen3-8B / Mistral-Nemo-12B Kaggle GPU reader plan은 **폐기/미실행**. 현재 실행 계약: [LABEL_V6_GPT6_CHUNKED_EXECUTION.md](LABEL_V6_GPT6_CHUNKED_EXECUTION.md).
3. report-only 4,349 studies를 원본 `train.csv` 행 순서 그대로 **87 chunks**로 고정:
   - Chunk 001–086 = 50 studies / 600 decisions
   - Chunk 087 = 49 studies / 588 decisions
   - 총 52,188 decisions
   - report-only UID manifest SHA256 = `e675c1cfb8e88b3ec00af4fcba77bfb010e324e3a3473b04089da651af630a94`
   - chunk manifest SHA256 = `66179ef419094e6204ea3c39c4696d1da68463320bc9c58168e96d993e5a0cd5`
4. primary reader는 **GPT-6**. 기본 최대 5 chunks/chat으로 18개 chat에 배치하되, context 품질이 우려되면 더 일찍 끊고 최신 cumulative Master/Handoff로 새 chat에서 계속한다.
5. 각 chunk는 모든 study의 12 targets를 직접 판정하고 exact report evidence + Unicode offset + report SHA를 보존한다. 이전 completed chunk는 integrity defect가 없으면 재판정하지 않는다.
6. 4,349 완료 후 4,349 studies / 52,188 decisions 전체 contract, target별 5-state distribution / supervised coverage / positive prevalence / language·script / duplicate consistency를 감사한다.
7. HIGH-review / inference-used / contradiction / ambiguity / distribution anomaly를 **GPT-6 Astra가 원본 report + frozen policy로 독립 재판정**하고 최종 adjudication 후 canonical LABEL-V6를 freeze한다.
8. canonical release 후에만 target별 N_pos/N_neg/mask coverage로 class weight와 **masked per-target BCE → 12-target macro average** loss를 확정한다.
9. canonical label release → R3D-13 single Main full-data → standalone Public LB → 필요 시 Exp57 complementary blend. 동일 canonical manifest를 Exp57 old-vs-new label 비교에도 사용한다.

중요: 공식 Gold는 MRI image-derived consensus label이다. 새 라벨은 공식 영상 판정 기준을 최대한 모사하는 report-derived supervision이며 새로운 ground truth가 아니다.

### GPT-6 실행·다음 채팅 인수인계 보강 (2026-10-08)

- 사용자용 새 배포본: `RSNA_Knee_LABEL_V6_GPT6_Reviewed_Workbench.zip` (`LABEL_V6_GPT6_Chat01_START.zip`부터 시작).
- 기존 GPT-5.6 Sol 이름의 Chat Pack/프롬프트는 **SUPERSEDED**; 원본 chunk data와 Policy V2 SHA는 변경되지 않음.
- 입력 완전성: 원본 순서 4,349 UID / 87 chunk / 52,188 decision; Source UID index / chunk SHA 검증.
- 실제 Chunk 완료 시 누적 Master(.jsonl.gz) + 감사 JSON + Handoff JSON + 다음 단계 프롬프트를 묶은 `HANDOFF_BUNDLE.zip` 전달.
- 다음 Chat에서는 **다음 Chat Pack + 직전 Handoff Bundle** 두 ZIP을 올려 SHA와 이전 12-target per UID 범위를 검증 후 다음 chunk만 append. 조기 채팅 종료 시에는 동일 Chat Pack으로 재개.
- 단일 GPT-6 reader 결과는 candidate. 코드를 통한 구조적 PASS만으로 임상/대회 의미 정확성은 증명되지 않음. 고위험 및 샘플 감사 후 GPT-6 Astra(이용 가능 시) 검토, canonical release, 분포·class weight 확정.
- 실행 계약: [LABEL_V6_GPT6_CHUNKED_EXECUTION.md](LABEL_V6_GPT6_CHUNKED_EXECUTION.md).


---

# 3. Frozen validation / pseudo contract

## Gold58

- Official Gold: **58 studies**
- deterministic multilabel 3-Fold seed: **20261059**
- Fold sizes:
  - F0 = 20
  - F1 = 19
  - F2 = 19
- 모든 target에서 모든 Fold Positive / Negative coverage 존재
- manifest SHA256:
  `246f252a1ce4faaafa1b7d30e2c75cde6d79951cb780b0b33bf4f4dd12ad7e4b`

주의:

- Gold58은 작다.
- 수천분의 일 수준 차이는 구조적 개선으로 과장하지 않는다.
- Fold0는 많은 architecture search에 사용되어 **untouched validation이 아니다**.
- 현재는 split을 다시 만들지 않는다.

## Fold-specific Pseudo1000

Dataset:

`rsna-knee-r3d-3fold-pseudo-v1`

대표 root:

`/kaggle/input/datasets/yhlucas/rsna-knee-r3d-3fold-pseudo-v1`

Pseudo UID SHA256:

- F0: `e96b07e22aa0e4ac40281ce5709841dbadfa3cb61c882c6f1d10b8dccb4e233c`
- F1: `e3bcab2deb4e4284179fd369a72566e17083eb173750144c55f0c096dee15d98`
- F2: `d2c482ed154c141a9eb2f1ce83e5ca395c57eb30e5e3a331e319a427c333cc4d`

Sample trace SHA:

- F0: `d0c36a537f9868e6d6f484d5852f922a48d08df1ad7d35d9d241c751ed05f7a3`
- F1: `724f4b6e5e8604d8d860e42e4eb006a41419a5bb1c5e8738febf803c0624a096`
- F2: `1e4d28dfce05fb4e364599d59fdd9b691c14734889d2bd9c9d923772c40cb525`

---

# 4. Frozen R3D assets

## MedicalNet

Dataset:

`rsna-knee-r3d-medicalnet-pretrained-v1`

R34 SHA256:

`977a1be79298602fa35980de9c03789229ad36087fb1f4d9bde468aec653c658`

현재 R3D Main에서는 R50 / R101을 다시 비교하지 않는다.

## Full-FOV persistent cache

Dataset:

`rsna-knee-wide224-persistent-cache-v1`

실제 구조는 metadata와 volume shard가 분리되어 있다.

Metadata:

`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d06a_metadata_bundle/series_index.csv`

Volume root:

`/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d06a_all_series_d24_96_v1/`

규모:

- 4,407 studies
- 24,371 series
- 819,078 slices
- 48 shards
- decode failure 0

중요:

R3D-06A raw `series_index.csv`에는
`plane_rank` / `selection_order`가 원래 저장되어 있지 않다.

기존 ALL policy와 동일하게 런타임에서 재구성한다.

~~~text
plane order:
Sagittal → Coronal → Axial

rank =
4 × Fluid_Sensitive × Fat_Suppression
+ 2 × Fluid_Sensitive
+ Fat_Suppression

tie-break:
SeriesInstanceUID ascending
~~~

그 뒤 study/plane별 `plane_rank`,
study별 `selection_order`를 생성한다.

## 현재 Crop130 cache

**R3D-11CACHE 완료/PASS**: 1,446 studies / 8,027 series / 32 float16 shards, 약 3.31 GiB. 기존 cache 통합, raw decode 0.

- 현재 mount: `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/r3d11cache`
- volume/index: `crop130_d24_96/`; Gold와 fold pseudo: `manifests/`.
- Index SHA256: `114bc191102849cc5df8b3f45c3a2b6361446d3e190f5315e13cdf6d002d1ef4`.
- Gold58와 3fold pseudo scope coverage PASS. 최종 4,407명 전체 cache는 아니다.

**R3D-12CACHE Full4407 완료/PASS — 2026-10-08**.

- 전체 **4,407 studies / 24,371 unique series**.
- 기존 R3D-11CACHE **8,027 series 재사용** + 누락 **16,344 series 신규 생성**.
- ALL usable Series / Crop130 / interpolated D24×96×96 / float16, 총 **160 shards / 10,780,971,008 bytes (~10.04 GiB)**.
- raw decode failures **0**.
- full Study/Series metadata parity PASS.
- 기존 shard SHA equality PASS / 신규 shard readback PASS.
- 기존 Crop130 12-series raw rebuild exact parity PASS (max abs 0).
- runtime **479.195 min (~7h59m)**.
- `series_index.csv` SHA256: `e72c9238c97e0957bb7fccee91489d23847519dd1aaf01e40620411875abe217`.
- `shard_manifest.csv` SHA256: `bf4a008de5fbf9a239066524b38d0b0632891b83ff2781bde07538ff75bd44a0`.
- audit ZIP SHA256: `73d6b93d678f6922cc72b8103961fc6a7baa67cd8fe41f740709ebbf8c69e39c`.
- `study_roles.csv`: report-only train 4,349 / Gold validation 58 exact.
- 학습용 artifact는 audit ZIP이 아니라 `r3d12cache_full/` 전체 Dataset이다.
- **캐시 축은 종료. 재생성하지 않는다.**


---

# 5. Series / geometry 연구의 최종 결정

## Series policy

3-Fold mean Macro AUROC:

- P2: 0.573140
- P3: 0.589716
- **ALL: 0.596226**

결론:

- **ALL 고정**
- P4 / max-N 추가 search 없음

## Physical crop

Crop130 3-Fold confirmation:

| Fold | Full-FOV AUROC | Crop130 AUROC | ΔAUROC |
|---|---:|---:|---:|
| F0 | 0.617594 | 0.622257 | +0.004663 |
| F1 | 0.548407 | 0.542584 | -0.005823 |
| F2 | 0.622678 | 0.656090 | +0.033412 |

3-Fold mean:

- Full-FOV AUROC: **0.596226**
- Crop130 AUROC: **0.606977**
- mean ΔAUROC: **+0.010751**
- mean ΔAUPRC: **+0.003722**

결론:

- **Crop130 채택**
- fold heterogeneity는 있지만 primary AUROC 평균 개선 크기가 의미 있음

## 기각된 geometry/input

추가 탐색하지 않는다.

- Crop150
- Full-FOV 128×128
- simple D32 interpolation
- REAL32 nearest actual-slice
- REAL24 nearest actual-slice
- Full/Crop Dual-FOV feature-token fusion
- Mixed3 Full/Crop/Dual training

---

# 6. R3D-08 / 09 / 10 핵심 결과

## R3D-08C — REAL24 최종

3-Fold mean delta:

- AUROC **+0.000405**
- AUPRC **+0.000842**

자동 sign-only rule은 ADOPT였지만 실제 판정:

- **KEEP interpolated D24**
- gain이 noise 수준
- Fold1/Fold2 AUROC 하락

## R3D-09AB — Crop130 confirmation

3-Fold mean delta:

- AUROC **+0.010751**
- AUPRC **+0.003722**

판정:

- **ADOPT Crop130**
- Main input freeze

## R3D-10AB — Dual-FOV screen

Fold0 frozen:

- Full-FOV: **0.617594 / 0.540314**
- Crop130: **0.622257 / 0.508100**

Always Dual:

- AUROC **0.609809**
- AUPRC **0.494292**
- vs Crop130 ΔAUROC **-0.012448**

Mixed3:

- training modes:
  - Full-only 621
  - Crop-only 645
  - Dual 654
- best Dual AUROC **0.610704**
- best Dual AUPRC **0.483695**
- same checkpoint Full-only AUROC **0.612836**
- Crop-only AUROC **0.604505**
- probability avg AUROC **0.607573**

판정:

- **Dual-FOV / Mixed3 기각**
- Fold1/Fold2 confirmation 없음
- Main R3D = Crop130 single-view 유지

R3D-10 result ZIP SHA256:

`da5dbf79b88bbe4c9d8f1537c322cdc0b761356c70ab6d27d6df2bedee52fbe6`

---

# 7. Target-specific Series 상태

## Medial Meniscus

R3D-06H Fold0 paired binary specialist:

- P2: 0.677083 / 0.591098
- Sag1-only: **0.729167 / 0.756302**
- ΔAUROC **+0.052083**
- ΔAUPRC **+0.165204**

강한 신호다.

R3D-11 재확인은 완료했으며 위 결과가 우선한다. 과거 06H 참고:

- 06H는 현재 final Main input인 Crop130 이전 실험
- visible 06H implementation에는 canonical R34 naming과 다른 부분이 있어
  최종 specialist 근거로 그대로 쓰지 않는다
- Canonical R34 + Crop130 재확인은 R3D-11에서 완료했고 최종 채택은 보류했다.

## Synovitis

R3D-06H:

- P2: **0.680000 / 0.757973**
- Sag1-only: 0.590000 / 0.583247

결론:

- **Sag1-only hard routing 기각**
- 다시 열지 않는다

---

# 8. R3D-11 검토 완료

상세 수치와 검토는 이 문서 2절 및 EXPERIMENT_HISTORY.md 참조. 세 fold 개선이지만 최종 SAG1 채택은 보류.

# 9. 최종 실행 방향

## 확정된 최종 학습 방향

- **단일 Main R3D 모델**, 3-fold 최종 학습 아님. 기존 3-fold는 구조 비교용이었다.
- 학습 범위: **report-only 4,349 studies 전체**. 검증: **공식 Gold58 전원**, 학습에서 제외.
- 신규 라벨에서 supervision이 전혀 없는 study는 손실에 기여할 수 없다. 실제 유효 supervision 수는 audit 후 별도로 기록한다.
- Main: ALL → Crop130 → interpolated D24×96×96 → MedicalNet R34 → GLOB + metadata → Transformer/shared CLS → 12 heads.
- Search best.pt를 이어 학습하지 않고 MedicalNet pretrained에서 새로 시작한다.
- Epoch은 전체 학습 목록 순회를 기준으로 한다. 192 draws/epoch search budget을 최종 학습에 그대로 적용하지 않는다.
- Epoch 종료 시 Gold58 12-target Macro AUROC 우선, Macro AUPRC tie-break로 best.pt 선정. Epoch 수/compute budget/unknown mask 및 loss 정규화의 구체 구현은 아직 확정 전.
- Gold58은 이미 반복 탐색에 사용되었으므로 untouched test가 아니다.
- 먼저 standalone R3D Public LB 확인, 이후 Exp57(0.918)과 ensemble 상보성 검토. SAG1은 보류 후보이며 자동 추가하지 않는다.

## 바로 다음 작업

1. 원본 report 기반 라벨 감사/재구축: 공식 target 정의 확인 → 근거 문장과 상태를 보존하는 소규모 pilot → 애매한 사례 사용자 리뷰.
2. `positive / negative / uncertain / not-mentioned / insufficient`를 구분. 언급 없음·불완전 report를 자동 음성으로 만들지 않는다. LLM 자기 확신을 calibrated probability로 취급하지 않는다.
3. 기존 V4 full-data routing은 CommonGold57을 이용해 reader/target 정책을 골랐다. 이를 그대로 학습하고 Gold58을 독립 검증이라 부르지 않는다. 새 라벨 정책은 Gold 결과에 맞춰 조정하지 않는다.
4. 병행한 R3D-12CACHE 완료 audit 확인 후 새 라벨 manifest, supervision coverage와 최종 loss/budget 확정.
5. 단일 Main full-data 학습 → standalone 제출 → 필요 시 Exp57 blend 평가.

라벨 재생성 자체는 아직 시작하지 않았다. 현재 원본 report/V4 master/method/old audit 자료는 확보했으며 원래 추출 prompt·근거 문장은 제공 자료에 없다.


---

# 10. 더 이상 하지 않는 작업

근거 없이 다시 열지 않는다.

- R50 / R101
- GLOB vs coarse spatial-token 재비교
- anatomy mask current fusion
- lower backbone LR / frozen backbone
- P2 / P3 / Series cap micro-search
- Synovitis Sag1-only
- Crop 130/140/150 micro-search
- Full-FOV 128/160/192/224 resolution search
- simple D32/D40/D48 interpolation
- REAL24 / REAL32 nearest-slice
- R3D-10 Dual-FOV Fold1/2 confirmation

새 evidence가 생기기 전까지 위 항목은 closed다.

---

# 11. Kaggle 운영 핵심

- 새로운 image/cache 생성 = **CPU-only Notebook**
- GPU Notebook = **training-only**
- Save & Run All 전제
- 전체 `/kaggle/input` recursive search 금지
- exact mounted path 우선
- 같은 Dataset의 서로 다른 Version 동시 mount에 의존하지 않음
- mount 단계에서 `Output 0 B / ERRORED_MOUNTING_DATASET`이면 Python code error로 해석하지 않음
- 실패 시 재학습 전에 기존 artifact가 완성됐는지 먼저 확인
- T4×2에서 독립 Fold/variant를 GPU0/GPU1 subprocess로 병렬 실행 가능
- 한 계정에서 input을 공유할 수 있으면 굳이 Account A/B 두 세션으로 분리하지 않아도 됨

---

# 12. 문서 우선순위

새 채팅에서 판단이 충돌하면 다음 순서를 따른다.

1. **CURRENT_HANDOFF.md**
2. **CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md**
3. **3D_RESNET_EXPERIMENT_PLAN.md**
4. **EXPERIMENT_HISTORY.md**
5. AI_AGENT_KAGGLE_NOTEBOOK_RULES.md — 실행 규칙
6. README 및 과거 Specialist 문서 — historical reference

과거 문서에
"NEXT", "현재 다음", "진행 중"이 남아 있어도
이 문서의 2026-10-08 상태와 충돌하면 **과거 기록으로만 해석**한다.

