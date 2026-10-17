<!-- CONVNEXT_README_STATUS_2026_10_18 -->
## 현재 상태 — 2026-10-18

- **NOT_RUN / DESIGN_REVIEW_ACTIVE**
- 기다리는 S11/Branch-B 결과와 병렬로 C-DESIGN-V2 상세 설계를 진행한다.
- 기존 `latest B soft-label` / `single full-data` 가정은 확정값이 아니다.
- V4 Broad Base → V4 Strict FT와 2-Fold 여부를 재검토한다.
- exact ConvNeXt pretrained / anatomy anchor / cache/view / spatial+MIL 구조를 고정하기 전 실행 Notebook을 만들지 않는다.
- 상세 cold-start: [../RSNA_KNEE_BRANCH_C_START_HANDOFF_2026-10-18.md](../RSNA_KNEE_BRANCH_C_START_HANDOFF_2026-10-18.md)

# Branch-C — ConvNeXt

이 폴더는 **RSNA Knee 최종 앙상블의 선택적 Branch-C(ConvNeXt Anatomy Expert)** 를 관리한다.

Branch-C는 시간이 허락할 때 추가하는 세 번째 독립 전문가다.  
Branch-A의 S8C Top18이나 Branch-B의 96-slot 입력을 재사용하지 않고, **Full-FOV + anatomy-centered local views + spatial attention + window MIL**로 다른 오류 패턴을 만든다.

## 문서 읽는 순서

1. [CONVNEXT_BRANCH_PLAN.md](CONVNEXT_BRANCH_PLAN.md)
2. [CONVNEXT_EXPERIMENT_LOG.md](CONVNEXT_EXPERIMENT_LOG.md)
3. 공통 상태: [../CURRENT_HANDOFF.md](../CURRENT_HANDOFF.md)

## 현재 상태 — 2026-10-17

- 상태: **DESIGN_FROZEN / NOT_RUN**
- 실행 우선순위는 Branch-B 다음.
- Branch-C의 성공 기준은 standalone 절대점수 + A/B와의 낮은 오류 상관 + A+B+C ensemble gain.
- 안전 baseline 목적이 아니다.
