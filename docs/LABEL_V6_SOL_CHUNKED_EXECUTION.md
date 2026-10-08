# SUPERSEDED — GPT-5.6 Sol package is no longer the current execution plan

Do not use the legacy GPT-5.6 Sol Chat Packs/prompts. Current user-selected GPT-6 plan: [LABEL_V6_GPT6_CHUNKED_EXECUTION.md](LABEL_V6_GPT6_CHUNKED_EXECUTION.md). Original report chunks and frozen competition policy remain unchanged.

---

# LABEL-V6 — GPT-5.6 Sol Chunked Execution Plan

Date: 2026-10-08

## Decision

The previously prepared Kaggle GPU reader plan using Qwen3-8B / Mistral-Nemo-12B is **superseded and must not be executed**.

Reason:
- final training quality depends directly on report-derived supervision quality;
- 8B/12B local readers are weaker than the available GPT-5.6 Sol reasoning reader;
- spending Kaggle T4 resources on weaker primary labelers is not a good trade-off.

The current plan is:
**GPT-5.6 Sol primary labeling in deterministic chunks -> programmatic audit -> GPT-6 Astra adjudication of high-risk cases -> canonical LABEL-V6 release.**

## Fixed source scope

- source train.csv SHA256:
  `8ca2203c0e9d61c080c7a314c7cdb51c1b03a1d9eb4770819f7f34af53ef4e33`
- total studies: 4,407
- Gold58: 58, excluded from report labeling
- report-only: 4,349
- partial-label rows: 0
- empty reports: 0
- 12 targets
- total report decisions: 52,188
- report-only UID manifest SHA256:
  `e675c1cfb8e88b3ec00af4fcba77bfb010e324e3a3473b04089da651af630a94`

## Chunking

Source `train.csv` row order is preserved.

- Chunk 001–086: 50 studies each = 600 target decisions each
- Chunk 087: 49 studies = 588 decisions
- total chunks: 87

Chunk manifest SHA256:
`66179ef419094e6204ea3c39c4696d1da68463320bc9c58168e96d993e5a0cd5`

Policy SHA256:
`e7cf242796b5d63816233a05bfc099f47054014213b2238b0169ebeef6633989`

Master schema SHA256:
`d8cbfeea206d0e59f566c1c07a3e72d0e26357179d41db4dcb2fe1d500067c7e`

## Chat grouping

Default maximum = 5 chunks per GPT-5.6 Sol chat.

- Chat 01: Chunks 001–005
- ...
- Chat 17: Chunks 081–085
- Chat 18: Chunks 086–087

Thus the default plan uses 18 chats rather than 87. A chat may stop earlier than five chunks if context quality becomes a concern. The newest cumulative Master + Handoff is then carried into a fresh chat.

## Per-chunk contract

For every study, GPT-5.6 Sol reads the full current report and assigns all 12 targets under the frozen policy:
- positive -> label1 mask1
- negative -> label0 mask1
- insufficient -> null mask0
- not_mentioned -> null mask0
- uncertain -> null mask0

Every supervised label preserves exact report evidence with Python Unicode zero-based end-exclusive offsets. Insufficient/uncertain items preserve the ambiguity-causing phrase when present. Not-mentioned has no evidence span.

Each chunk must validate:
- exact expected UID set
- no duplicate UID-target
- 12 target rows/study
- criterion id exact
- state/label/mask exact
- report SHA exact
- evidence text == source report[offset_start:offset_end]
- positive/negative evidence non-empty
- normal chunks = exactly 600 decisions; Chunk087 = 588

## Cumulative outputs

After each chunk:
- chunk decision JSONL
- chunk audit JSON
- cumulative Master through current chunk
- cumulative Handoff with hashes, counts, next chunk and unresolved high-review items

Do not relabel completed chunks unless an integrity defect is found.

## Astra final review

After all 4,349 studies:
1. programmatically revalidate 4,349 studies / 52,188 decisions;
2. audit target-wise 5-state distribution, supervised coverage and positive prevalence;
3. extract HIGH-review, inference-used, contradiction, localization/temporal ambiguity, duplicate inconsistency and distribution anomaly cases;
4. GPT-6 Astra independently rereads those cases from original report + frozen policy;
5. adjudicate disagreements;
6. freeze canonical LABEL-V6 + SHA;
7. only then compute training class weights and final masked macro loss.

Gold58 and V4 remain descriptive references. They are not used to tune the frozen report-label policy or chunk reader decisions.
