# RSNA Knee — Public Research / Performance Roadmap

최종 업데이트: **2026-10-07**

목적:
- 현재 공개된 competition host 자료, Kaggle discussion / notebook, peer-reviewed 자료 중
  재현 가능하거나 근거가 비교적 강한 내용만 정리한다.
- 공개 아이디어를 그대로 복사하는 것이 아니라 현재 R3D 계보에서
  **어떤 실험이 실제 성능 향상 가능성이 높은지 우선순위를 정한다.**
- Public LB만 쫓지 않고 private/generalization 위험을 같이 관리한다.

현재 사용자가 확인한 Public LB 1위는 **0.964**.
이 값은 사용자 제공 최신 관측값이며, 아래 research source의 검색 인덱스에서는
동일 시점의 leaderboard row를 독립적으로 확인하지 못했다.

---

## 1. 공식 Competition 사실

공식 평가지표:
- 12 target 각각의 ROC-AUC를 계산
- 최종 score = 12개 AUC의 macro average

공식 test:
- 약 1,300 studies
- Public leaderboard는 test의 약 30%
- Final standings는 나머지 약 70% private test

공식 일정:
- Entry / Team Merger deadline: 2026-10-15
- Final submission: 2026-10-22

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/overview
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/leaderboard
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/data

---

## 2. 가장 강한 공개 인사이트 — Input Geometry가 매우 중요

### 2.1 DICOM slice physical ordering

공개 controlled audit에서:
- DICOM filename은 SOPInstanceUID이므로 anatomical order가 아님
- physical position / orientation으로 정렬해야 함
- filename 순서가 실제 anatomical order와 맞는 비율이 약 5% 수준이라는 공개 측정도 있음

권장:
- ImageOrientationPatient의 row/column 방향에서 normal 계산
- ImagePositionPatient를 normal에 projection하여 정렬
- fallback: SliceLocation → InstanceNumber → filename

현재 프로젝트:
- Full Manifest v2 / SimpleITK 기반 volume ordering parity는 이미 확인됨
- 따라서 현재 R3D의 강점이며 유지

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735154
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/734105

### 2.2 Fixed-mm physical crop / physical scale normalization

공개 ablation:
- 단순 resize보다 일정한 physical field-of-view를 mm 단위로 crop 후 resize하는 방식이 반복적으로 강조됨
- 130~150 mm crop이 여러 강한 public pipeline에서 사용됨
- 한 공개 pipeline은 140 mm crop이 원본상 398~896 pixels에 해당해 scanner마다 2.3배 차이가 난다고 측정
- 고정 pixel crop은 scanner별 anatomy scale을 다르게 보여줄 수 있음

현재 R3D:
- D24×96×96 full-volume resize가 search pipeline
- **physical FOV normalization은 아직 핵심 실험으로 분리하지 않음**

판정:
- R3D-07에서 단순 96→128보다 먼저 physical crop / spacing normalization audit를 넣을 가치가 높음

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/734105
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304
- https://www.kaggle.com/code/kozykappa/rsna-knee-v600-lb-score-0-942/log

### 2.3 Slice 위치 / 인접성

공개 controlled ablation:
- 288px / 140mm crop 조건에서 slice geometry 변화가 resolution 자체보다 큰 효과
- center-adjacent sampling이 equal-spaced sampling보다 Fold0 OOF 약 +0.018 사례
- 다른 공개 측정에서는 24→32 cached slices가 큰 개선이었다는 보고
- meniscus tear처럼 1~3 mm의 작은 신호는 sparse sampling에서 놓칠 수 있음

현재 R3D:
- 각 Series를 D24로 interpolation/resample
- depth 24 자체와 원본 실제 slice 선택 방식은 아직 별도 최적화 전

판정:
- D24→D32는 단순 숫자 증가가 아니라
  **원본 slice geometry 보존 / adjacency / spacing-aware depth 처리**와 함께 검토

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/737597
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/743148

---

## 3. 현재 R3D의 96×96은 성능 병목 후보

Competition host 설명:
- meniscal tear는 표면에 닿는 비정상 신호가 둘 이상의 image에서 확인되는 subtle finding
- OA는 high-grade cartilage loss를 봐야 함
- fluid-sensitive / fat-suppressed sequence는 edema, effusion, tear 등에 중요

공개 고득점 사례:
- 224px small ResNet single model 0.936 public 보고
- 224px 5-fold 계열 0.943 public 보고
- 288px single model 0.942 raw / 0.943 TTA 보고
- 392px / 150mm crop / 32 slices 사용 사례
- 224/288이 효율-성능 sweet spot이라는 상위권 참가자 의견

주의:
- 큰 resolution이 무조건 답이라는 뜻은 아님
- 288→384에서 차이가 작았다는 공개 보고도 있음
- 핵심은 **해상도 + physical scale + slice geometry**

현재 R3D D24×96×96은 search용으로는 합리적이지만,
최종 0.96대 목표에서는 in-plane detail loss가 강한 병목 후보.

출처:
- Host clinical overview:
  https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/733343
- Best single model discussion:
  https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304
- Controlled ablation:
  https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/737597

---

## 4. Label quality는 중요하지만 Gold58만으로 최적화하면 위험

공식 label 기준:
- borderline / ambiguous는 negative
- ACL: >50% fiber disruption 또는 complete tear 중심
- MCL: high-grade partial / complete acute tear
- meniscus: surface contact on >=2 images 또는 morphology abnormality
- OA: roughly >=1 cm, >50% cartilage-thickness loss
- Effusion: moderate/large
- Baker cyst: moderate/large
- Contusion vs fracture 별도

즉 report에서 'mild', 'minimal', 'sprain', 'degeneration' 등을
모두 positive로 처리하면 공식 label과 어긋날 수 있음.

공개 자료:
- report와 Gold label contradiction 사례가 존재
- soft target이 hard target보다 3/3 paired seeds에서 방향상 우세한 실험이 있었으나
  Gold58 bootstrap CI는 zero를 포함해 확정적이지 않았음
- 한 참가자는 label work + public label combination으로 LB +0.015 보고
- 반대로 상위권 일부는 label extraction 개선이 더 이상 LB에 거의 반영되지 않았다고 보고

판정:
- label은 중요하지만 **Gold58 자체가 너무 작아 0.002~0.01 차이를 안정적으로 판별하기 어려움**
- 현재 leakage-safe pseudo 계보 유지
- official severity criteria로 current pseudo label audit
- public label source와 disagreement map을 만드는 것은 가치 있음
- 단 Gold58을 prompt / route tuning에 과도하게 사용하지 않음

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/733343
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/733826
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/734105
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304

---

## 5. Validation이 현재 큰 병목 후보

공개 상위권 조언:
- Gold58만으로 0.002~0.003 개선을 판단하기 어려움
- report-derived / silver labels로 더 큰 OOF를 만들고 LB와 correlation을 확인하는 접근이 사용됨
- 동일 report text duplicate grouping 필요
- scanner/site grouping을 고려해야 함

DICOM metadata probe:
- metadata-only random fold AUROC 약 0.6515
- unseen-scanner GroupKFold 약 0.5981
- 약 0.053 gap은 site memorization 가능성을 보여줌

현재 R3D:
- Gold58 3-Fold는 엄격한 최종 audit에는 좋음
- 하지만 n=19~20/fold라 micro improvement 판단에는 noise가 큼

권장 dual-validation:
1. **Large Silver CV**
   - report/pseudo-labeled 4k급 study
   - duplicate report grouping
   - scanner/site-aware group
   - 빠른 모델 선택 / 작은 delta 평가
2. **Gold58**
   - final audit / leakage-safe sanity
   - Gold에 맞춘 micro-tuning 금지

출처:
- https://www.kaggle.com/tuckerarrants/discussion
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/733517
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/744495

---

## 6. 모델 크기보다 데이터/입력 설계가 우선

공개 controlled experiment:
- DINOv2 Small → Base
- params 약 4배
- CV +0.0011
- 측정 noise floor 0.0020 안쪽
- 즉 capacity 증가 효과 없음

공개 상위 사례:
- small ResNet / EfficientNet 계열에서도 0.93~0.94대 public score 보고
- 224 / 288 resolution에서 강한 결과 존재

현재 R3D:
- R34 > R50 > R101을 직접 확인
- 이 공개 결과와 방향이 일치
- 따라서 R34 유지가 합리적
- 당분간 더 큰 3D backbone에 GPU를 쓰지 않음

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735154
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304

---

## 7. Medical pretraining / decorrelated 2.5D arm은 가치가 높음

Peer-reviewed RadImageNet:
- 1.35M radiologic images
- small-data transfer에서 ImageNet 대비
  - ACL MRI AUC +4.8%
  - meniscus MRI AUC +4.5%
- medical-source pretraining이 small radiology task에서 유리

Competition discussion:
- Synovitis에서 ImageNet pretrained 계열보다 RadImageNet 계열이 크게 높았다는 participant report 존재

현재 R3D:
- MedicalNet 3D pretrained를 이미 사용
- 따라서 'medical pretraining을 안 쓴다'는 문제가 아님

하지만 ensemble 관점:
- **2.5D RadImageNet CNN**
- **3D MedicalNet R34**
- 기존 **DINO/Exp57**
는 representation family가 달라 decorrelation 가능성이 있음

판정:
- R3D를 버리고 RadImageNet으로 교체하는 것이 아니라
- 최종 ensemble용 독립 arm 후보로 2.5D RadImageNet을 별도로 검증할 가치가 큼

출처:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9530758/
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/737566

---

## 8. Sequence metadata를 더 정확하게 복구할 가치

공식 train_series:
- Anatomical_Plane
- Fluid_Sensitive
- Fat_Suppression

공식 설명상 Fluid_Sensitive와 Fat_Suppression은 항상 같은 개념이 아님.

하지만 train 24,371 rows에서 두 flag가 동일하다는 공개 audit가 있음.

현재 R3D:
- 두 flag를 metadata embedding / ranking에 사용
- train에서는 사실상 duplicate signal

권장:
- SeriesDescription
- ProtocolName
- TE / TR
- ScanOptions
- fat-sat 관련 DICOM field

을 이용해 실제 sequence class를 복구하는 audit.

가능한 slot:
- Sag FS
- Sag non-FS / T1-like
- Cor FS
- Cor non-FS
- Ax FS
- Ax non-FS

이는 P3/ALL 이후에도 Series **개수**가 아니라 Series **종류**를 구분하는 새로운 축.

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/data
- https://www.kaggle.com/code/mattiaangeli/bend-the-knee-to-dinov3-ensembled/comments

---

## 9. Ensemble은 '많은 모델'보다 '다른 모델'이 중요

최근 공개 discussion:
- 서로 동의하는 모델보다 서로 다른 오류를 내는 모델이 ensemble에서 더 가치 있다는 반복 조언
- 한 팀은 correlation 0.83인 외부 arm 하나가 public +0.004였다고 보고
- high-score public ensemble은 DINO, RadImageNet, 기타 CNN family를 섞음
- AUC는 rank metric이라 rank-average가 실용적인 선택

현재 자산:
- Exp57 Public LB 0.918 — DINO/2-stage 계보
- R3D — 3D MedicalNet 계보
- Specialist 계보
- 향후 2.5D RadImageNet 가능

권장:
- 각 family의 OOF prediction correlation matrix 저장
- target별 correlation과 target별 AUC 동시 확인
- correlation이 낮고 성능이 충분한 arm만 blend
- public LB weight tuning 금지
- OOF 기반 rank blend / conservative weight 사용

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/742926
- https://www.kaggle.com/code/kozykappa/rsna-knee-v600-lb-score-0-942/log

---

## 10. TTA / 과도한 Training Trick은 후순위

공개:
- strong single model 0.942 raw → 0.943 TTA
- TTA는 유효하지만 gain은 약 +0.001 사례
- EMA / Mixup / longer cosine는 한 controlled setup에서 noise 수준
- Asymmetric loss는 큰 악화 사례

현재:
- BCE / simple schedule을 유지하는 것이 합리적
- geometry / validation / series / depth보다 먼저 복잡한 loss로 가지 않음
- TTA는 final model 안정화 후 마지막 +alpha 단계

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/737597

---

## 11. 외부 데이터는 규칙 / license 위험이 큼

Competition rule:
- notebook submission
- Internet Off
- freely/publicly available external data / pretrained model allowed

Host clarification:
- OAI처럼 institutional sign-off가 필요한 데이터는
  generally accessible 조건을 만족하는지 문제가 됨
- 공개 discussion에서 실제 사용 가능 여부가 모호하거나 부정적인 dataset이 많음

따라서:
- external MRI dataset을 최우선 성능축으로 잡지 않음
- Kaggle에서 모두 접근 가능한 public artifacts / permissive pretrained weights를 우선
- 외부 데이터는 host clarification + license 확인 후만 사용

출처:
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/overview
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/741819

---

# 12. 현재 프로젝트에 적용할 성능 우선순위

## Priority 0 — 현재 실행 중
- R3D-06I: P3 Fold1/2
- R3D-06H FIXED: Sag1 specialist confirmation

## Priority 1 — Input Geometry Audit
Series policy 확정 직후:
- physical slice order 재검증
- spacing / FOV 분포
- fixed-mm crop 후보 130 / 140 / 150 mm
- left/right orientation / bilateral-knee edge cases audit
- raw slice vs resampled D24 정보 손실 정량화

GPU 없이 가능한 audit를 먼저 한다.

## Priority 2 — Physical Crop A/B
현재 full-frame input과 fixed-mm crop만 비교.
Resolution / depth는 동일하게 고정하여 crop 효과만 분리한다.

## Priority 3 — Resolution
선택된 crop에서:
- 96 → 128
- 필요 시 160/192 또는 224 equivalent 검토

현재 public evidence상 최종 96은 낮을 가능성이 높다.

## Priority 4 — Depth / real-slice geometry
- D24 vs D32
- real-slice adjacency 보존
- spacing-aware interpolation / sampling 비교

## Priority 5 — Large Silver CV
- report duplicate group
- scanner-aware group
- large silver validation
- Gold58 final audit와 역할 분리

## Priority 6 — Label policy audit
- official severity 기준과 현재 pseudo 비교
- public report-label sources와 disagreement matrix
- low-confidence target / report-missing signal 별도 처리

## Priority 7 — Decorrelated model family
- 2.5D RadImageNet CNN
- current 3D R34와 OOF correlation 측정
- Exp57 DINO 계보와도 correlation 측정

## Priority 8 — Final ensemble
- strong family만 사용
- target별 OOF AUC + prediction correlation
- rank averaging / conservative OOF weight
- 5-fold final candidate 고려
- TTA는 마지막

---

# 13. 당장 피해야 할 GPU 낭비

- R50 / R101 재시도
- TargetQuery 재시도
- Mask ON 재시도
- 단순히 Transformer token 수만 늘리기
- Gold58 Fold0에서 0.002~0.005 차이를 과해석
- public LB만 보고 blend weight 미세조정
- external dataset license 확인 전 대규모 pretraining
- physical scale 문제를 해결하지 않은 상태에서 무작정 256/384로 resolution만 상승

---

# 14. 핵심 결론

현재 0.964 수준의 상위권과 격차를 줄이려면
'더 큰 모델'보다 다음 순서가 더 근거가 강하다.

**정확한 MRI geometry → 더 많은 유효 spatial detail → 안정적인 large CV → label noise 관리 → 서로 다른 강한 model family → OOF 기반 ensemble**

현재 R3D는 backbone / mask / LR / series policy를 매우 많이 정리했다.
다음 가장 큰 미개척 영역은 **physical crop + spatial/depth detail + validation 규모**다.
