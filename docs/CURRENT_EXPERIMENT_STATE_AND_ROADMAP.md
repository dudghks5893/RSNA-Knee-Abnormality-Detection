# RSNA Knee — Current Experiment State & Roadmap

최종 업데이트: **2026-10-08**

이 문서는 **현재 상태와 다음 작업만 기록하는 기준 문서**다.
오래된 계획/상태를 아래에 누적하지 않는다.

- 완료된 실험의 상세 기록: [EXPERIMENT_HISTORY.md](EXPERIMENT_HISTORY.md)
- 앞으로의 R3D 실행 계획: [3D_RESNET_EXPERIMENT_PLAN.md](3D_RESNET_EXPERIMENT_PLAN.md)
- Kaggle Notebook 작성/복구 규칙: [AI_AGENT_KAGGLE_NOTEBOOK_RULES.md](AI_AGENT_KAGGLE_NOTEBOOK_RULES.md)
- 새 채팅 인수인계: [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md)

이 문서와 위 3개 문서가 과거 README / Specialist 문서의 오래된 "현재 다음" 문구보다 우선한다.

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

가장 최근 완료 실험:

- **R3D-10AB — Always Dual vs Mixed 3-Mode Fold0**
- 결과: **Dual-FOV 계열 기각**
- 따라서 Main R3D는 **Crop130 single-view** 유지

현재 즉시 다음:

1. **R3D-11CACHE — Crop130 3-Fold search cache 정리/통합**
2. **R3D-11 — Medial Meniscus Sag1-only canonical confirmation**
3. Final Main R3D training policy 확정
4. Hidden-test standalone R3D submission
5. Exp57 + R3D (+ validated Medial Meniscus specialist) ensemble

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

## Crop130 cache — 현재 stable mount

현재 R3D-10에서 정상 사용한 root:

`/kaggle/input/datasets/yhlucas/rsna-knee-r3d-crop130-search-cache-v3/crop130_d24_96`

R3D-10 실행 시 확인된 coverage:

- **1,058 studies**
- Fold0 Gold + Fold0 Pseudo1000 search scope
- paired Series = 5,882

매우 중요:

**이 v3 root 하나만으로 Fold1/Fold2 training을 커버한다고 가정하면 안 된다.**

R3D-09 Fold1/Fold2 confirmation에서는
기존 Fold0 Crop130 base cache와 Fold1/Fold2 missing-study delta cache를 함께 사용했다.

다음 3-Fold 작업 전에:
- 기존 base + delta를 하나의 canonical Crop130 search cache로 합치거나
- missing studies만 CPU-only로 보완해
- 한 Dataset / 한 mounted version으로 Fold0/1/2 coverage를 보장한다.

같은 Kaggle Dataset의 서로 다른 Version을 동시에 mount하는 설계는 사용하지 않는다.

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

하지만 주의:

- 06H는 현재 final Main input인 Crop130 이전 실험
- visible 06H implementation에는 canonical R34 naming과 다른 부분이 있어
  최종 specialist 근거로 그대로 쓰지 않는다
- 따라서 **canonical R34 + Crop130에서 재확인**해야 한다

## Synovitis

R3D-06H:

- P2: **0.680000 / 0.757973**
- Sag1-only: 0.590000 / 0.583247

결론:

- **Sag1-only hard routing 기각**
- 다시 열지 않는다

---

# 8. 다음 작업 — R3D-11

## R3D-11CACHE — 먼저 해결할 prerequisite

목표:

- Crop130 base + Fold1/Fold2 missing-study cache를
  **한 canonical mounted Dataset**으로 정리
- Fold0/1/2의 Gold + fold-specific Pseudo1000을 모두 커버
- 가능하면 기존 cache artifact를 합쳐 재사용하고 raw DICOM 재decode를 피한다
- 기존 artifact로 합칠 수 없을 때만 missing-study CPU cache를 생성

Runtime 원칙:

- **CPU only**
- GPU 예약 금지
- output contract에 Fold0/1/2 coverage를 각각 assert
- exact Study/Series parity를 Full-FOV metadata와 확인

## R3D-11 — Medial Meniscus Sag1 canonical confirmation

이 실험은 아직 실행하지 않았다.

권장 paired design:

~~~text
Control:
Crop130 + ALL Series
→ canonical MedicalNet R34
→ binary Medial Meniscus

Candidate:
Crop130 + Sagittal plane_rank=1 only
→ same canonical MedicalNet R34
→ binary Medial Meniscus
~~~

공정성:

- fixed Gold58 3-Fold
- fold-specific Pseudo1000
- same train Study sampling
- same initial model state within pair
- same optimizer / augmentation / epochs
- only Series policy changes
- Full/Crop Dual-FOV 사용 안 함

가능하면 **3-Fold paired confirmation**으로 마무리한다.
Fold0만 또 반복해서 고르는 방식은 피한다.

Primary:

- pooled Gold58 OOF Medial Meniscus AUROC

Secondary:

- pooled AUPRC
- Fold별 AUROC/AUPRC
- fold stability

Gate:

- Sag1-only가 pooled AUROC에서 분명히 우세하고
  fold-level catastrophic failure가 없으면 final target-specific candidate 유지
- 그렇지 않으면 specialist routing 폐기

---

# 9. R3D-11 이후

## Step 1 — Main R3D final-training policy 확정

아직 명시적으로 결정해야 하는 항목:

- final train에서 Pseudo1000 유지 여부
- report-only pseudo를 더 확장할지 여부
- final epoch / sample budget
- checkpoint selection / fold training budget

중요:

**Search 때 쓴 Pseudo1000을 임의로 4,349 전체로 늘리지 않는다.**
data scope 변경은 별도 실험 변수이므로 사용자와 먼저 결정한다.

## Step 2 — Final Main R3D 3-Fold

확정 구조:

- Crop130
- ALL
- interpolated D24×96×96
- R34 GLOB MASK_OFF
- Transformer + shared CLS

Fold-specific final checkpoints와 SHA를 저장한다.

## Step 3 — Hidden-test standalone R3D

먼저 R3D만 단독 제출해 Public LB를 확인한다.

이 단계가 중요하다.

Exp57과 바로 섞으면:
- R3D 자체 성능
- ensemble complementarity
를 분리할 수 없기 때문이다.

## Step 4 — Final ensemble

후보:

1. Exp57
2. R3D 3-Fold
3. validated Medial Meniscus Sag1 specialist — 통과 시 해당 target에만 제한

Ensemble weight는 Public LB에 반복 과적합하지 않는다.
가능하면 prediction correlation / target-level behavior를 먼저 확인한다.

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
