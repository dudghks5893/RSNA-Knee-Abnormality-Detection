# RMIL-04A 검증 완료 / RMIL-04B Full Native224 V3 5-Pack 준비

**기준일 2026-10-10. RMIL-04A는 Kaggle CPU 실행 및 사용자 ZIP 독립검증 완료. RMIL-04B 캐시 구축·GPU Full4,349 학습은 아직 실행되지 않았음. LABEL-V6 = CANDIDATE_NOT_RELEASED.**

## 1. RMIL-04A 사용자 업로드 ZIP 검증 결과

- ZIP `RMIL-04A_results_for_review.zip` SHA256 **`121145c51525862672f630d0c6b650602046964151ceb36e53b981a071be3614`**, 834,322 bytes, CRC PASS, 선언 메타 파일 **6/6 SHA PASS**.
- 4,407 Studies, 24,371 Series, 819,078 native DICOM Slices. Source Series 누락/Study·Series UID 중복 0. Study-level Train4,349/Gold58 분리 PASS.
- 전체 V4 pseudo-label `rsna_knee_pseudolabels_v4_routed_broad.csv` **4,349 rows, 12 target + 12 __conf columns**, 전체 Train UID 커버(누락/extra 0). 실제 파일 SHA `93863c59f99a70e2fd5c2d1674bc91266f3c459d398755911e033dbdac8d381c`; **게이트 상태 `UID_COVERAGE_PASS_NEEDS_12_TARGET_CONTRACT`**. 값·null·class imbalance·leakage·V4/V6 정책 승인은 아직 미검증. 사용자 요청상 Train300 분포 재분석은 진행하지 않음.
- 5 Study-packed, slice-balanced immutable partitions. Raw uint8×224² 전체 **41,098,057,728 bytes ≈41.10GB**, 보수적 Kaggle output 14GB cap 때문에 5개 독립 캐시/Notebook 필요. RMIL-04A elapsed **8.625min**.

| Pack | Studies | Series | Slices | V3 old-358 중첩 Series | Nominal raw |
|---|---:|---:|---:|---:|---:|
|00|881|4879|163788|406|8.218GB|
|01|881|4863|163788|419|8.218GB|
|02|881|4896|163788|453|8.218GB|
|03|882|4881|163860|394|8.222GB|
|04|882|4852|163854|334|8.222GB|
|**총계**|**4407**|**24371**|**819078**|**2006**|**41.098GB**|

## 2. RMIL-04B CPU Notebook 5개 준비 완료 (미실행)

**사용자에게 전달한 Notebook (모두 한글, CPU, Internet OFF, Run All):**

- `RMIL-04B_PACK00_FullNative224_V3_Cache_CPU_KO.ipynb` SHA256 `069442b089bcba392bd657ec43297d0974ff740f003a3fc3d73838e5a6ee62f9`
- `RMIL-04B_PACK01_FullNative224_V3_Cache_CPU_KO.ipynb` SHA256 `f31a2bf3a7b6e18effbf63a7a62df20d1dedc8d00ba89bfc5f3356aaa1a979f6`
- `RMIL-04B_PACK02_FullNative224_V3_Cache_CPU_KO.ipynb` SHA256 `3ce766f428cf59ad5ec4004447f7d88c3bcb0b76f8c2bc85d5711b13baf0e548`
- `RMIL-04B_PACK03_FullNative224_V3_Cache_CPU_KO.ipynb` SHA256 `9552715a71ba324383ff273d5262716fd29b601948737416a09724e4c16554e5`
- `RMIL-04B_PACK04_FullNative224_V3_Cache_CPU_KO.ipynb` SHA256 `f11c1c70f5264a67e88f6e389cd4a7a2d7a111ba7646f357331c2daa908ec591`
- 사용자 전달 묶음 `RMIL-04B_FivePack_CPU_Notebooks_and_Handoff.zip` SHA256 `3d12212fcd8e467935728452ec91442ce805720317b0a5e69e01f8bdae25c2c3`. 파일들은 **채팅 업로드로만 제공**, GitHub에는 실험·자산·실행 규칙을 기록.

**입력 (Kaggle Add Input):** ① Official competition `RSNA Knee Abnormality Detection` `/kaggle/input/competitions/rsna-knee-abnormality-detection`, ② `yhlucas/rmil-02b-native224-v3` `/kaggle/input/datasets/yhlucas/rmil-02b-native224-v3/RMIL-02B_NATIVE224_V3`, ③ `rsna-knee-wide224-persistent-cache-v1` `/kaggle/input/rsna-knee-wide224-persistent-cache-v1/R2D_SHARED224_V1`. B 계정은 dataset 접근권 확인. 04A 원본 파트 CSV는 SHA256 검증된 압축 bytes로 각 Notebook 내장: 새 Kaggle Dataset slug를 가정하지 않음. 전역 /kaggle/input 재귀 탐색 없음.

**구현:** 기존 RMIL-02B V3 **`preprocess_series` 함수 실제 소스와 5개 Notebook의 함수 본문이 byte-for-byte 동일(비교·검증)**. 원본 physical sort, center±1 실제 3-Slice, 130mm crop/외부 Z=-5 패딩, Series sampled p0.5/99.5→z-score→clamp±5→cv2 INTER_AREA224→uint8, numeric K4 anchors ⊂ K16⊂K24⊂K32. 기존 358명 중첩 **2006개 모든 Series 새 픽셀 byte SHA와 02B V3 `pixels_sha256` 전수 대조**; 하나라도 불일치 시 Fail-Fast. 기존 Series 메타 embedding index도 frozen 358 metadata에서 유도·체크. 220MB HDF5 shard, per-series pixel SHA readback, per-shard SHA, output 14GB cap/free 2GB reserve, compact metadata-only review ZIP, 실제 8.2GB HDF5는 output folder에 보관.

**실행 전 코드검증:** nbformat 5/5, AST all Code 5/5 PASS, 함수원본 일치 PASS, 합성 DICOM pixel crop/pad + nested K selector CPU PASS. **실제 Kaggle CPU/pydicom DICOM 전체 decoding·출력 8.2GB×5·픽셀 parity는 아직 수행하지 않음.**

## 3. 권장 실행/연계

1. **Pack00 단독 CPU 먼저 Run All** → 406 Series 기존 V3 Pixel SHA parity 확인 및 Review ZIP 수령.
2. Pack00 통과 후 Pack01~04 병렬 CPU 진행 (A/B 계정, 각각 GPU 없음). 계정별 정책·출력용량 범위에서만 동시 실행.
3. 각 Pack 출력 `/kaggle/working/RMIL-04B_PACK_XX/shards/*.h5` **실픽셀 포함 폴더를 통째로 Kaggle Dataset로 별도 등록**. `RMIL-04B_PACKXX_results_for_review.zip`만 등록하면 실제 학습에 필요한 픽셀이 없음. 등록 Dataset name/root/SHA 확인 후 5개 파트 연결.
4. 5개 part metadata/UID/order/intersection의 통합 SHA Gate → RMIL-04C **Full4,349 GPU**, 우선 RMIL-02D K16 Mean 구조 고정, V4 전체 라벨의 12 target/conf/missing/leakage 계약 확인. V6는 release 후 별도 masked-label 학습. Gold58은 이미 반복 선택에 쓰인 개발 검증, 독립 테스트 아님.
