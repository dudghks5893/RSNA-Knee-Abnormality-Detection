# RSNA Knee Abnormality Detection — Final Competition Summary

최종 업데이트: **2026-10-23**

> **COMPETITION CLOSED / PROJECT ARCHIVED**
>
> 이 문서는 대회 종료 후 확정된 최종 결과의 authoritative summary다.
> 기존 문서의 `NEXT`, `CURRENT`, `RUNNING` 표기는 작성 당시의 역사적 상태이며 더 이상 실행 지시가 아니다.

## 1. 최종 결과

| 항목 | 결과 |
|---|---:|
| 최종 MAIN 제출 Public LB | **0.958** |
| 최종 MAIN 제출 Private LB | **0.941** |
| 최종 순위 | **949위** |
| 대회 중 Public leaderboard 최고 위치 | **약 240위** |
| 자체 제출 중 확인된 더 높은 Private 점수 | **0.942** |
| 해당 제출 | 기존 **70:30 비율 변경 제출** |

마지막 제출 세트에서는 **MAIN 버전만 정상 제출에 성공**했고 Public LB는 기존 최고와 동일한 **0.958**이었다.

대회 종료 후 Private leaderboard가 공개되면서 최종 MAIN 제출은 **Private 0.941**로 확정되었다.
그보다 앞서 제출했던 **70:30 비율 변경 버전이 Private 0.942**로 0.001 더 높았다.

공식 최종 순위는 **949위**다.

## 2. Public과 Private의 차이

대회 진행 중에는 Public LB **0.958**까지 올라갔고 Public leaderboard에서 약 **240위**까지 도달했다.

그러나 최종 평가는 Private leaderboard로 결정되었으며:

```text
Final MAIN
Public  = 0.958
Private = 0.941

Earlier 70:30 ratio submission
Private = 0.942
```

로 마무리되었다.

따라서 이 프로젝트를 회고하거나 포트폴리오에 기재할 때는 다음을 구분한다.

- **Public best:** 0.958
- **Public peak rank:** 약 240위
- **Final Private score:** 0.941
- **Final official rank:** 949위
- **Best known Private among our submissions:** 0.942 (70:30 ratio submission)

Public 0.958만을 최종 대회 성적으로 표현하지 않는다.

## 3. 최종 단계 직전의 주요 계보

### 3.1 자체 0.955 계보

핵심 baseline은 공개 CoAtNet reader와 S6F0 계열을 이용한 per-target percentile-rank ensemble이었다.

자체 제출에서:

```text
CoAt384 + S6F0
50:50 percentile-rank blend
Public LB = 0.955
```

를 확보했다.

이후 target-wise 비율 조정에서도 Public **0.955**가 유지되었다.

### 3.2 Weak2 specialist

기존 ensemble에서 상대적으로 약한:

- Synovitis
- Lateral OA

두 target을 보강하기 위해 RadImageNet ResNet50 기반 Weak2 Direct Specialist를 별도로 실험했다.

W2D-00:
- 1,075 studies
- 6,014 Series
- Strict V1 hard-label 기반 all-Series cache
- Gold58 train overlap 0
- cache PASS

W2D-01 계열에서는 resume loader, remote HDF5 I/O, orchestration, AMP full-FT transition 문제를 순차적으로 수정했다.

후속 **W2D-03**에서는 과적합/score saturation 완화를 위해 label smoothing과 regularization을 적용했다.

Gold58 diagnostic:

| Checkpoint | 2-target Macro AUROC | Synovitis AUROC | Lateral OA AUROC |
|---|---:|---:|---:|
| EMA E6 | **0.779490** | **0.756272** | **0.802708** |
| RAW E6 | 0.771753 | 0.756272 | 0.787234 |

W2D-03을 기존 CoAt384 + S6 계보의 Synovitis/Lateral OA에만 추가한 제출은 **Public LB 0.955**로, 기존 0.955 계보 대비 leaderboard 상승은 확인되지 않았다.

## 4. Submission robustness에서 확정된 원칙

프로젝트 후반 hidden-test 오류 대응 과정에서 아래 원칙을 확정했다.

1. DICOM 정렬은 가능한 경우 physical position을 우선한다.
2. 개별 slice decode 실패는 deterministic nearest-valid rescue를 허용한다.
3. bad Series 하나가 전체 Study failure로 확대되지 않게 한다.
4. Fold/branch 일부 실패 시 살아 있는 **실제 MRI prediction**으로 rescue한다.
5. Study-level 고정 `0.5` placeholder로 inference failure를 숨기지 않는다.
6. 실제 이미지 기반 prediction branch가 하나도 남지 않으면 fail-fast한다.
7. submission 생성 성공 여부만 보지 않고 rescue/failure audit를 함께 확인한다.

마지막 정상 MAIN 제출에서도 이 방향의 robustness를 유지했다.

## 5. 프로젝트에서 얻은 핵심 결론

### 모델 성능

- 단일 Branch를 계속 깊게 확장하는 것보다 서로 다른 reader/representation의 ensemble이 Public LB 개선에 더 효과적이었다.
- 자체 DINO/CoAtNet/ConvNeXt branch 실험은 모델·입력 다양성에 대한 근거를 제공했지만, 최종 leaderboard 최고점은 강한 공개 reader 계보와 앙상블 조정에서 나왔다.
- 타깃별 specialist가 Gold58에서 좋아 보여도 hidden leaderboard에서 ensemble marginal gain으로 이어진다는 보장은 없었다.

### 검증

- 작은 Gold58 validation은 방향성 확인에는 유용하지만 leaderboard generalization을 완전히 대변하지 못했다.
- Public leaderboard에서의 미세한 개선 또는 동일 점수도 Private에서 순서가 바뀔 수 있었다.
- 실제로 최종 MAIN은 Public **0.958 / Private 0.941**, 이전 70:30 제출은 Private **0.942**였다.
- 따라서 future competition에서는 Public LB 최적화보다 OOF/holdout robustness와 단순한 ensemble의 재현성을 더 강하게 우선한다.

### 엔지니어링

- T4×2 환경에서 실제 HDF5 I/O, AMP transition, checkpoint resume, subprocess GPU context 정리까지 모두 성능과 안정성에 영향을 줬다.
- profiler는 GPU compute뿐 아니라 DataLoader/I/O까지 포함해서 판단해야 한다.
- hidden inference robustness는 학습 성능과 별개의 제품 수준 문제로 관리해야 한다.

## 6. 프로젝트 종료 상태

```text
Competition: CLOSED
Further Kaggle submission: NONE
Active training experiment: NONE
Active leaderboard tuning: NONE
Project state: ARCHIVED / DOCUMENTATION ONLY
```

기존 checkpoint, cache, notebook, SHA, 실험 로그는 재현성과 포트폴리오 회고를 위해 보존한다.

새로운 실험을 이 대회의 `NEXT`로 이어서 실행하지 않는다.
향후 코드를 재사용할 경우 별도의 후속 프로젝트/대회로 분리한다.

## 7. 문서 읽기 순서

대회 종료 이후에는 다음 순서로 읽는다.

1. **이 문서 — `FINAL_COMPETITION_SUMMARY.md`**
2. `CURRENT_HANDOFF.md` — 종료 상태와 과거 주요 단계
3. 각 Branch의 Experiment Log — 세부 실험 이력
4. 각 Branch의 Roadmap / Data Model — 당시 설계 근거
5. `AI_AGENT_KAGGLE_NOTEBOOK_RULES.md` — 재사용 가능한 실행 규칙

---

**Final official record**

```text
Public best / final MAIN Public : 0.958
Public peak position            : ~240
Final MAIN Private              : 0.941
Best known Private submission   : 0.942 (earlier 70:30 ratio)
Official final rank             : 949
Competition status              : CLOSED
```
