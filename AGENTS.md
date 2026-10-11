# RSNA Knee — Rules for AI coding agents

**Read first:** [GPU resource and Batch policy](docs/GPU_BATCH_RESOURCE_MANDATORY_POLICY.md), [current handoff](docs/CURRENT_HANDOFF.md), [current experiments roadmap](docs/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md).

## Highest priority: limited Kaggle GPU budget

The user reports **previous GPU memory profiling found substantial VRAM headroom even at Batch Size >=124** in early experiments (exact historic model/microbatch semantics not established). This repeated user-reported result **MUST NOT BE FORGOTTEN**. Never presume T4 GPUs necessarily require Window Microbatch=1 or 4. The RMIL-04C02 DINOv2-Small microbatch=1 choice without profiling incurred **217.15 minutes/epoch** (compare R34 46.33 min/epoch) and consumed limited GPU budget. Avoid repeating.

**Important:** Historic Batch>=124 is **not** a blanket guarantee for DINOv2 Full Fine-tuning K16. Test actual memory and end-to-end throughput of *this* model/input/backward before claiming a batch is safe. Keep Study Global Batch and Window Microbatch separately documented. Report choices that affect runtime/VRAM; do not silently lower batches. Profile Window microbatches upward from realistic sizes, record measured peak VRAM and steps/sec, estimate 5–10 Epoch total vs Kaggle session/time budget, verify checkpoint resumption before lengthy training. Request user review of material changes.

## Documentation source-of-truth (2026-10-12: MUST FOLLOW)

**Do not create one new `.md` per experiment, Notebook revision, DDP bug, or QA audit.** User explicitly prefers their original cumulative history. Always update three **existing** documents:

- `docs/EXPERIMENT_HISTORY.md`: cumulative actual experiment observations, metrics, completed/failed/interrupted runs, independent QA results.
- `docs/CURRENT_EXPERIMENT_STATE_AND_ROADMAP.md`: cumulative latest decisions, active state, next experiment and priorities.
- `docs/AI_AGENT_KAGGLE_NOTEBOOK_RULES.md`: cumulative notebook-delivery, testing, GPU resource and documentation rules.

`docs/CURRENT_HANDOFF.md` and `README.md` are short navigation/current-state pointers. Older per-experiment QA/design Markdown documents are archived reference, **not the primary source of truth**. Create a separate document only when the user explicitly requests a standalone artifact or an unavoidable technical reason is stated and approved. Do not rely on assistant memory to choose a document: these fixed paths are authoritative. Historic Batch>=124 VRAM-headroom evidence remains mandatory.

## Reproducibility and safety

- Always keep input exact Kaggle dataset/model paths, pinned hashes, data split and Gold58 handling; never mix Gold58 into train labels.
- LABEL-V6 is `CANDIDATE_NOT_RELEASED` until explicit release.
- All Kaggle notebooks: Korean cell descriptions, unambiguous numbered Add Input, Internet OFF, GPU/CPU settings, Save & Run All execution, experiment ID, save name <60 characters, runtime/budget assumptions, full code & output structural QA.
- DDP smoke needs **2+ consecutive optimizer steps**, plus actual full pipeline forward/backward/optimizer, output package dry-run, and a tested resume path.
- Do not claim Kaggle GPU tests or Kaggle LB submissions unless actual logs/artifacts confirm.
