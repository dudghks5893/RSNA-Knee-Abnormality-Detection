# RMIL-04 — 전체 4,349 report-only 데이터 학습 실행 계획 (2026-10-10)

**현재 단계: `RMIL-04A` CPU 사전 검증 Notebook 작성 완료, Kaggle 미실행. `RMIL-04B` 대용량 캐시와 `RMIL-04C` GPU 학습은 아직 생성·실행되지 않음.** LABEL-V6는 후보 `CANDIDATE_NOT_RELEASED`.

## 결정 근거

- 기존 RMIL-02C/02D V3 K16 MEAN: Gold58 개발 검증 Macro AUROC **0.577856**, AUPRC **0.432300**. 기존 V3 K4 0.574420, K24 0.577402. **V3 내부 최고** K16 Mean.
- RMIL-03 질환별 Head 새 구조 2×2: 03A 0.560367, 03B Window-only 0.562446, 03D Series-only 0.550656, 03C Both 0.560299. 03B 새 Head의 matched Mean 대비 +0.002079이지만 기존 02D K16 Mean 대비 낮음. **추가 target Attention을 검증 없이 full-scale 최종 구조로 승격 금지.**
- 300개만 대상으로 한 질환별 class·confidence 분포 재분석을 사용자가 명시적으로 중단했으므로 실행하지 않음; 전체 분포 기록은 과거 V4 자료가 우선.

## RMIL-04A — 지금 실행 가능한 CPU 자산·분할 검증

**Notebook**: `RMIL-04A_Full4407_5Pack_Source_Label_Preflight_CPU_KO.ipynb`
**SHA-256**: `987807dd589440493fafed9d231c3196526b6117d44d0193ae35a01e748acf32`
**설정**: CPU/Internet OFF/Save & Run All/Seed 20261013; Save Version `RMIL-04A Full4407 Cache Partition Preflight CPU`.

**필요한 Kaggle Add Input**
1. Competition `RSNA Knee Abnormality Detection`, source `train.csv`, `train_series.csv`, `train_series/<StudyUID>/<SeriesUID>/*.dcm`. 알려진 root 두 곳 `/kaggle/input/competitions/rsna-knee-abnormality-detection` / `/kaggle/input/rsna-knee-abnormality-detection` 검사.
2. `rsna-knee-wide224-persistent-cache-v1` → `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1/frozen_manifests/gold58_manifest.csv`; **고정 SHA** `a3ca7df32d43ee7c683091162b1839ea8308d802bea3f2b437f4908d9cbcb079`.
3. Optional structural source check `rsna-knee-v4-consensus-dataset`, file `rsna_knee_pseudolabels_v4_routed_broad.csv`. **실제 mounted root/schema를 이번 실행 전엔 검증하지 못함**. Dataset이 없으면 영상 source/pack planning은 가능하지만 `LABEL_NOT_MOUNTED`, **GPU Train 진행 금지**.

Official train.csv expected SHA `8ca2203c0e9d61c080c7a314c7cdb51c1b03a1d9eb4770819f7f34af53ef4e33`. 이전 SS01 full inventory: **4,407 Studies / 24,371 Series / 819,078 Slices**. 현재 원본 파일 개수 재검사(원본 CSV가 나열한 Series 폴더 내부의 이름만 `os.scandir`, 전역 recursive 없음); Gold58 UID·전체 4349 training UID 분리 검증, Series 메타데이터 포함. 클래스/Confidence 분포 계산 금지. V4에서는 4,349명 UID 커버리지만 확인; **12-target score/conf schema, fold-aware leakage, 결측/보류 정책은 RMIL-04C에서 따로 Release Gate**.

**용량:** `819078×224×224=41,098,057,728 bytes≈41.10GB` raw uint8 1-channel. 프로젝트 **14.0GB/Notebook** 보수적 상한을 초과, 직접 Full V3 1회 Notebook 캐시는 금지. RMIL-04A는 Study 단위 split을 유지해 **5개 용량 균형 분할**을 설계. 단순 평균 파트당 raw8.22GB, 안정성 계산 `1.30×raw+300MB≈10.99GB` 추정; 각 파트별 실제 count로 보수적 게이트. `RMIL-04A_results_for_review.zip`은 메타데이터만 포함; 원본 픽셀 생성 안 함.

**CPU preflight output**: `RMIL-04A_full_series_inventory.csv`, `RMIL-04A_study_partitions.csv`, `RMIL-04A_partition_summary.csv`, `RMIL-04A_issues.csv`, `RMIL-04A_label_gate.json`, `RMIL-04A_preflight_summary.json`, 파일별 SHA manifest, `RMIL-04A_results_for_review.zip`.

## RMIL-04B — 검증된 Full Native224 V3 캐시 분할 생성 (준비 다음 단계)

- RMIL-04A verified `part 0..4` 결과를 동결. 5번의 독립 CPU 작업에서 해당 part만 처리하고 SHA 검증, `n_slices×224×224` uint8 단일 Slice 저장. 파트별 14GB 보수적 상한과 물리적 저장 여유 >2GB 유지, 256~512MB 내부 HDF5 shards atomic commit; 저장된 HDF5 직접 읽어 SHA 검증.
- **재사용 전처리:** 현재 358명 캐시 `RMIL-02B-NATIVE224-V3`의 물리 순서, 130mm FOV 원본 바깥 -5 패딩, Series 단위 p005/p995 클리핑·zscore·clip5·INTER_AREA224·uint8. **358명 교집합에서 새 full-data 캐시 vs V3 실제 uint8 픽셀 SHA/수치 동등성 사전 Gate**. 새 코드를 같은 계약 없이 변경 금지.
- K16 selection은 기존 K4 numeric anchor+최대 최소거리 nested 정책 유지, 중복없고 center±1 실제 Slice. Full 24,371 Series에는 short Series가 있을 수 있으므로 파트 생성 전에 short-series policy를 사전 동결·감사.
- 비슷해 보이는 과거 Full-MRI DINO Feature·3D D24×96·일부 TopK 캐시는 V3 source pixels와 다르므로 혼합 금지. 원본 DICOM 전체 픽셀을 1 Notebook Output 41GB로 저장 금지.
- 완료된 각 part를 정확한 Kaggle Dataset으로 등록하고 mount-root·metadata SHA·shard SHA를 기록. Dataset 이름/slug는 **실제 사용자가 생성하기 전엔 정해진 것으로 주장하지 않음**.

## RMIL-04C — 4,349명 Full Train + 독립 평가 (캐시 및 라벨 Release Gate 이후)

- **1순위 모델:** RMIL-02D 구조의 **MedicalNet R34 2.5D K16 Mean + 공유 CLS Series Transformer + 12 outputs**, seed20261013, Full Fine-tuning.
- **A/B 두 계정 T4×2의 활용:** 기존 K16 Mean을 기준으로 같은 label release를 사용하는 통제 실험만 진행. RMIL-03B Window-only는 별도 탐색 후보이고, 03A/03B의 Head 자체가 02D와 달라 섞어 비교하지 않음. Full-data batch/epoch/lr는 300명 실험 값의 최적이라는 보장이 없어 새로운 full-data 프로토콜에 맞춰 사전에 동결, 검증 지표만 보고 사후 임의 변경 금지.
- **V4 실행:** 4,349명에 대해 전체 V4 soft score + target별 confidence weighted BCE (floor0.25). Gold58 훈련 입력 제외, UID 정합·라벨 출처·Gold pseudo leakage 검사. 기존 V4 Gold reader routing이 validation에 미친 영향을 보고서에 명시. **V6 승인 전 V6를 학습에 사용 금지**.
- **V6 실행(조건부):** 완료·Audit·독립 Review·Policy 동결·Release 승인 시 `positive/negative` 등 명시적 확정만 target-wise loss mask 학습, `insufficient/uncertain/not_mentioned`를 0으로 간주 금지. V4 full train과 V6 full train은 라벨 축이 달라 **별도 실험**으로 기록; 영상 캐시는 재사용 가능. V6 release가 매우 임박했다면 GPU full V4를 중복 실행하기보다 동일 영상 캐시 준비 우선.
- **평가:** Gold58 = 반복 개발 검증; 별도 OOF/holdout 누수 통제, Kaggle standalone Public LB (공식 점수는 실제 제출 시에만 주장). 사용자 프로젝트 최고 Public LB Exp57=0.918(다른 평가 표본)과 Gold58 pilot AUROC 숫자를 동일 척도로 직접 비교 금지. **Full preprocessing/inference parity** 확보 후 Kaggle inference Notebook 작성.
- **잠재 GPU 러닝 비용:** Train300 시각 약 50분에서 4349명으로 ~14.5배 규모이나 I/O·캐시 마운트·epochs·순서 영향 커서 실행 시간은 미측정. 단일 GPU 2개/계정, 2계정 총4GPU는 모델 간 병렬에 활용하되 멀티GPU 사용/IO/Quota는 실제 실행에서 확인.

## 후속 자료

- [RMIL-03 완료 감사](RMIL-03_2X2_ATTENTION_COMPLETED_2026-10-10.md)
- [RMIL-02B V3 캐시 결과](RMIL-02B_V3_CACHE_COMPLETED_2026-10-10.md)
- [RMIL 최종 구조 및 탐색 프로토콜](RMIL_FINAL_ARCHITECTURE_AND_EXPERIMENT_PLAN.md)
- [Kaggle Notebook 작성 규칙](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
