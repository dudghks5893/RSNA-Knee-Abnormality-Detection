# RMIL-02B — 358명 전체 Native224 공통 캐시 생성 결과

**검증 날짜:** 2026-10-10  
**상태:** 캐시 생성 **완료** · 전달된 결과 ZIP 무결성 검증 **통과** · 대용량 HDF5 원본 파일은 별도 Kaggle Output 보존 필요

## 1. 실험 목적과 확정 설정

원본 무릎 MRI DICOM을 공통 조건으로 전처리한 뒤, K4·K16·K24를 별도의 이미지 중복 저장 없이 동일한 단일 채널 캐시로 학습하기 위한 준비 단계.

- 데이터: **Train300 + Gold58 = 358명**, 전체 **2,006 Series / 66,430 Slice**
- 전처리: 물리적 Slice 정렬 → 원본 130mm Crop → Series 단위 정규화 → 224×224 `uint8`
- 실제 촬영 범위가 130mm보다 좁으면 영역 외부를 일정한 배경값(z=-5)으로 처리하고, 실제 영상 부분만으로 정규화 통계를 산출
- 선택 방식: 동일한 유효 3-Slice 인접 Window에서 **K4 ⊆ K16 ⊆ K24 ⊆ K32**; 패딩으로 가짜 Slice를 만들지 않음
- 실제 저장 형식: Slice당 단일 채널 224×224 `uint8`을 HDF5로 저장, K별로 이미지 중복 생성하지 않음
- 출력: `/kaggle/working/RMIL-02B_NATIVE224_V3/shards/` 및 `RMIL-02B_V3_results_for_review.zip`(검증용 메타데이터만 포함)

## 2. 수령한 Kaggle 결과

| 검증 항목 | 결과 |
|---|---:|
| 완료 상태 | `PASS_NEW_PREPROCESS_V3` |
| Train Studies | 300 |
| Gold Studies | 58 |
| 전체 Series | 2,006 |
| 전체 실제 Slice | 66,430 |
| 완료된 HDF5 Shard | **16/16** |
| HDF5 샤드 크기 합계 | **3,341,400,768 bytes** (= **3.3414 GB / 약 3.112 GiB**) |
| 실험 총 소요 시간 | **23.4082분** |
| 프로젝트 Notebook Output 내부 운영 상한 | **14.0 GB** |

Kaggle 로그에는 샤드 16개 모두 `SHARD VERIFIED`가 기록돼 있으며, 실행 시 각 파일의 실제 픽셀을 재읽어 인덱스별 SHA를 검사한 뒤 완성 샤드 파일 SHA를 기록한 것으로 확인됨.

**중요한 검증 범위:** 수령한 ZIP에는 HDF5 영상 파일이 없음. 독립 검증은 **ZIP 8개 항목 CRC + 기록된 메타데이터 7개 파일 SHA-256 + 모든 UID, 인덱스, 원본 Slice 순서, FOV 통계**에 대해 수행. HDF5 바이트 자체 SHA 재계산은 **실제 Kaggle Notebook Output 또는 등록된 Dataset 파일 접근 시에만 가능**하므로 이 문서에서 독립 HDF5 무결성까지 확정했다고 주장하지 않음.

수령 ZIP SHA-256: `f21f454542b47c99e3ef4d1503c191a5d1e006387c8d0e5e81e7cd320625fdd8`; ZIP CRC 검사 PASS, 7개 메타데이터 SHA-256 전부 일치.

## 3. 실제 K별 윈도우 수

| K | 실제 전체 Window | Series당 평균 | K를 모두 채우는 Series |
|---:|---:|---:|---:|
| 4 | **8,024** | 4.00 | 2,006 |
| 16 | **31,838** | 15.87 | 1,924 |
| 24 | **45,472** | 22.67 | 1,513 |
| 32 | **53,532** | 26.69 | 516 |

`k_selection.jsonl`의 2,006개 항목에 대해 **Study/Series UID 고유성**, SOP UID 수와 Slice 수, 물리적 좌표의 단조 증가, 3-Slice 유효 중심 범위, K별 고유성 및 중첩성을 별도로 확인한 결과 **오류 0건**.

## 4. FOV 패딩 현황 — 모델 해석 시 참고

- 패딩 없는 Series: **1,982개 (98.80%)**
- 패딩 있는 Series: **24개 (1.20%)**
- 영상 면적 중 패딩 비율 20% 이상: **16개 (0.80%)**; 모두 **Axial** 영상
- 50% 이상 패딩: **9개**
- 최대 패딩 면적 비율: **61.14%**
- 패딩 Series의 소속: Train **19개**, Gold **5개**

패딩은 원래 존재하지 않는 해부학적 영역을 생성하지 않기 위한 고정 배경 처리임. 비율이 큰 Series는 이후 모델 분석에서 층별 편향/정보량 저하를 확인할 후보이며, **이 결과만으로 임의 제외하거나 평가 분포를 바꾸지 않음**.

## 5. 다음 단계

1. **Kaggle Save & Run All이 생성한 전체 Notebook Output을 다음 실험의 Add Input으로 첨부**. 파일 `RMIL-02B_NATIVE224_V3/shards/shard_000.h5`~`shard_015.h5` 및 `series_index.csv`, `k_selection.jsonl`, `cache_contract.json`, `shard_sha256.csv` 필요.
2. GPU 학습 시작 전에 실제 마운트된 샤드 **16개 모두 존재 및 전체 파일 SHA 재검증**. 이전 출력에서 작성된 SHA 목록과 일치해야 함.
3. 새 공통 V3 전처리에서 **K4·K16·K24 Mean**을 동일한 MedicalNet3D-deflated ResNet34, Train300 V4 soft/conf weighted BCE, Gold58, seed 및 최적화 계약으로 비교. 기존 RMIL-01 K4 AUROC 0.5763704369는 **다른 픽셀 전처리이므로 직접 비교 기준 아님**.
4. K별 Mean 실험이 완료되고 품질·연산 비용을 확인한 다음, 선택된 동일 K·동일 픽셀 조건에서 Mean과 Shared Window Attention을 비교.
5. Gold58은 반복 사용된 작은 개발용 검증 데이터이므로 높은 내부 점수를 외부 리더보드 성능으로 간주하지 않음.

**실험 기록 원칙:** 일반적인 코드 수정 과정이나 임시 오류 연대기는 기록하지 않고 검증된 결과와 중요한 데이터 특성만 남긴다.
