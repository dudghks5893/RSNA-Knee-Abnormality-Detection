# RSNA Knee — Specialist Model Roadmap

최종 업데이트: **2026-09-30**

> 상태: **초안 / 실험 계약 미확정**
>
> 현재는 Specialist 방향을 논의하는 단계다.
> architecture, validation, pilot target, pseudo-label filtering 정책을 사용자와 상세히 확정한 뒤 실제 실험 순서를 이 문서에 추가한다.

완료 기록: [SPECIALIST_EXPERIMENT_LOG.md](SPECIALIST_EXPERIMENT_LOG.md)

---

# 1. 확정된 목표

기존 shared 12-label 모델과 별도로, **질환 하나만 Yes / No로 판단하는 binary specialist** 구조의 가능성을 검증한다.

최종 개념:

```text
Patient MRI
  -> disease-specific specialist
  -> one probability

12 specialists
  -> 12 probabilities
  -> submission
```

모든 질환을 처음부터 동시에 확장하지 않고, 실제 실험 계약이 정해진 뒤 작은 pilot부터 검증하는 방향을 우선한다.

---

# 2. 현재 유력하지만 아직 확정하지 않은 architecture

현재 가장 근거가 강한 후보:

```text
multiple 2D MRI slices / windows
        ->
DINOv2-Small image encoder
        ->
slice feature sequence
        ->
lightweight Slice Transformer
        ->
binary head
        ->
Target Yes / No
```

근거는 Scientific Reports 2025의 Medical Slice Transformer 연구다.
다만 우리 competition의 multi-series / pseudo-label / Top-K selection 조건은 해당 논문과 다르므로 그대로 복제하지 않고 controlled experiment로 검증한다.

---

# 3. 실험 시작 전에 결정할 항목

아래 항목은 아직 TBD이며, 대화 후 확정한다.

- **Pilot target**: 어떤 질환부터 specialist를 만들지
- **Input unit**: Top24 / Top32 / 특정 Series / 전체 Series 중 무엇을 쓸지
- **DINO feature**: CLS only / CLS + patch mean 등
- **Slice Transformer**: layer 수, attention head 수, hidden dim
- **Series 처리**: slice transformer 하나로 합칠지, series-level aggregation을 별도로 둘지
- **Pseudo supervision**: broad confidence weighting vs low-confidence target masking
- **Low-confidence threshold**: V4 strict threshold를 그대로 쓸지 새로 정할지
- **Validation**: Gold11 유지 / pseudo holdout 추가 / 기타 개발 split
- **Checkpoint selection metric**: Macro AUC / target AUC / BCE 등
- **Augmentation / regularization**
- **Inference runtime contract**

이 항목들이 확정되기 전에는 `S01`, `S02` 같은 실제 실험 번호를 만들지 않는다.

---

# 4. 현재 유지할 원칙

1. 한 번에 여러 핵심 변수를 바꾸지 않는다.
2. 첫 specialist 실험에서는 기존 main-line 결과와 비교 가능한 input / preprocessing 계약을 최대한 유지한다.
3. 모델 크기 확대 자체를 목표로 하지 않는다.
4. low-confidence pseudo 제거 효과를 보려면 architecture 효과와 별도 실험으로 분리한다.
5. 58 Gold가 작기 때문에 작은 validation 차이를 확정적 결론으로 해석하지 않는다.
6. single model이 충분히 강해진 뒤에만 multi-fold 확장을 검토한다.
7. Specialist가 일부 target에서만 강하면 12개 전부 교체하지 않고 shared model과 target별 hybrid도 허용한다.

---

# 5. 참고 자료

- Medical Slice Transformer, Scientific Reports 2025: https://www.nature.com/articles/s41598-025-09041-8
- WACV 2024 medical foundation model comparison: https://openaccess.thecvf.com/content/WACV2024/html/Huix_Are_Natural_Domain_Foundation_Models_Useful_for_Medical_Image_Classification_WACV_2024_paper.html
- DINOv2 Radiology Benchmarks: https://arxiv.org/abs/2312.02366
- Kaggle single-model discussion: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/735304

---

# 6. 다음 문서 업데이트 조건

사용자와 다음 사항을 완전히 확정한 뒤 이 문서를 실제 순차 실험 계획으로 변경한다.

```text
Backbone
+ input/slice policy
+ specialist pilot targets
+ pseudo confidence policy
+ validation/checkpoint policy
+ controlled comparison baseline
```

그 뒤 각 실험 완료 시 결과 / checkpoint / Public LB / 인사이트는 `SPECIALIST_EXPERIMENT_LOG.md`에 기록한다.
