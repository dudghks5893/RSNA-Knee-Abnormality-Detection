# RMIL-04B Pack01~04 검증 완료, RMIL-04C00 실제 데이터 검사 준비

**2026-10-11. 상태:** 사용자가 2026-10-11 업로드한 Pack01,02,03,04 review ZIP **메타데이터 독립 QA PASS**. Pack00은 이전 실행 로그 **PASS**. **통합 Kaggle Dataset의 실제 HDF5 190개 직접 SHA 재검증 및 RMIL-04C GPU 학습은 아직 미실행**.

| Pack | Train | Gold | Study | Series | Slices | Shards | V3 old parity (실행 메타 보고) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00 (이전 로그) | 868 | 13 | 881 | 4,879 | 163,788 | 38 | 406/406 |
| 01 (독립 ZIP QA) | 869 | 12 | 881 | 4,863 | 163,788 | 38 | 419/419 |
| 02 (독립 ZIP QA) | 863 | 18 | 881 | 4,896 | 163,788 | 38 | 453/453 |
| 03 (독립 ZIP QA) | 874 | 8 | 882 | 4,881 | 163,860 | 38 | 394/394 |
| 04 (독립 ZIP QA) | 875 | 7 | 882 | 4,852 | 163,854 | 38 | 334/334 |
| **전체 계획** | **4349** | **58** | **4407** | **24371** | **819078** | **190** | **2006/2006** |

## 독립 QA 실제 범위

- Pack01~04 ZIP CRC 4/4 PASS. `metadata_sha256.json`에 선언된 **40개 내부 산출물의 실제 SHA256 전부 일치**.
- 각 ZIP의 `study_partition.csv`, `source_series_inventory.csv` Study/Series UID/role/partition/n_slices를 RMIL-04A 원본 전체와 **행 단위 비교 PASS**; Pak01~04 상호 중복 0. RMIL-04A 전체에서 01~04를 제외한 잔여 881 Study/4,879 Series/163,788 Slice가 Pack00과 일치.
- 각각의 `series_index.csv`, `shard_sha256.csv`, 4,852~4,896 `k_selection.jsonl`에서 UID 수량, HDF5 Series/Slice 집계, 모든 K의 중첩(K4⊆K16⊆K24⊆K32), 물리 center±1 경계 및 SOP 수량 QA 통과.
- **검증 한계:** 원본 HDF5 픽셀은 사용자 review ZIP에 포함되지 않아 실제 152 shard SHA 및 1,600 old V3 overlap byte parity는 사용자 Notebook에서 생성된 **메타데이터 결과**만 확인. Pack00 review ZIP은 이번 업로드에 없고 이전 **콘솔 로그**만 확인. 합산된 190개 실제 HDF5가 현재 통합 Dataset에 존재하며 일치하는지는 아직 직접 확인되지 않음.
- V4 full 4,349 UID + 12-target·confidence 열 존재 이전 04A 확인; **soft score/conf 실제 값·범위·null·Gold leakage 검증은 미완료**. V6는 `CANDIDATE_NOT_RELEASED`.

## 수령 ZIP SHA256

- Pack01 `6b529c3eb184e23c6c55e6a0c689fbe52a61595c90b6db73d69934a6802718f4`
- Pack02 `cfe93b0fef793154caacb8685269772144a485af1603d568b0b49c3dd45d5c52`
- Pack03 `ab6711b0edbc0d86376c9f133a9182cc7b5ca23a9a6190a3d663e10e925ec5ac`
- Pack04 `f42d30fff34db361efc05c4ec5b29019a1b0cda447f390783edb02a98f649a49`
- 동결 04A ZIP `121145c51525862672f630d0c6b650602046964151ceb36e53b981a071be3614`

## 다음: RMIL-04C00 CPU full-cache & label gate

**준비한 Notebook `RMIL-04C00_Full4407_Cache190SHA_V4_Label_Gate_CPU_KO.ipynb`, SHA256 `b468235ac9797d40abdfe65d0103bf97c67592cddc1cf8f4065b65f047e81bbe`.** `nbformat.validate` 및 전체 Python code AST 통과; **실제 Kaggle CPU 미실행**. 3 Input: `yhlucas/rmil-04b-full-mri-native224-v3` (사용자 실제 경로 다섯 Pack), `yhlucas/rsna-knee-v4-consensus-dataset` (V4 broad 4349), `rsna-knee-wide224-persistent-cache-v1` (Gold58). CPU/Internet OFF/Run All/Seed20261013. Notebook은 해당 5개 Pack의 50개 메타 SHA + 동결 04A 전체 UID/Series/Role/Part fingerprint + 24,371 Series의 K 중첩 + 190개 실제 HDF5 shard 파일 SHA 직접 읽기 + V4 4349×12 soft score/conf numeric finite [0,1] 및 Gold leakage 없는지 검사. `RMIL-04C00_results_for_review.zip` 메타데이터만 저장. **Kaggle 실행 후 로그 및 ZIP을 검증한 다음** Full4,349 GPU 모델 RMIL-02D K16 Mean 학습 단계로 진입. Gold58은 반복 개발 검증, Public LB 아님. V6 정식 릴리스 전 학습에 혼입 금지.
