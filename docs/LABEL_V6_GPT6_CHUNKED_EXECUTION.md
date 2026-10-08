# LABEL-V6 GPT-6 Chunked Reader / Cross-Chat Handoff (2026-10-08)

**CURRENT EXECUTION DOCUMENT.** Supersedes [LABEL_V6_SOL_CHUNKED_EXECUTION.md](LABEL_V6_SOL_CHUNKED_EXECUTION.md) and abandoned Qwen3/Mistral Kaggle GPU reader notebooks.

## Source and isolation

- Original train.csv SHA256 `8ca2203c0e9d61c080c7a314c7cdb51c1b03a1d9eb4770819f7f34af53ef4e33`.
- Gold58 rows are excluded; exactly 4,349 report-only studies are read.
- Original CSV row order / report bytes / chunk sources are unchanged.
- 87 chunks: 001–086 have 50 studies, 087 has 49. Total 52,188 target decisions.
- Report-only UID index SHA256 `e675c1cfb8e88b3ec00af4fcba77bfb010e324e3a3473b04089da651af630a94`.
- Chunk manifest SHA256 `66179ef419094e6204ea3c39c4696d1da68463320bc9c58168e96d993e5a0cd5`.
- Frozen competition policy: [LABEL_RECONSTRUCTION_POLICY_V2.md](LABEL_RECONSTRUCTION_POLICY_V2.md). **No Gold/V4/predictions available to reader.**
- Primary reader = **user-selected GPT-6 in ChatGPT**, preferably higher reasoning effort when available. Do not assume a specific internal model/backend revision. The reader is a candidate labeler, not clinical ground truth.
- Target schema: state positive/negative supervised; insufficient/not_mentioned/uncertain masked.

## User execution

- User downloads `RSNA_Knee_LABEL_V6_GPT6_Reviewed_Workbench.zip` from the ChatGPT artifact response.
- For Chat 01: upload `LABEL_V6_GPT6_chat_01_chunks_001_005.zip`, paste `COMMON_CHAT_START_PROMPT.md`, ask `Chunk 001 진행해`.
- Subsequent chunks in the same chat: `다음 청크 진행해`.
- **At the actual completion of every chunk**, deliver standalone chunk labels, structural audit, latest cumulative compressed Master `.jsonl.gz`, Handoff JSON, NEXT_STEP markdown, and a Handoff Bundle ZIP containing these plus the common next-chat prompt.
- At the final chunk of one chat, give the user the **exact next Chat Pack filename** and latest Handoff Bundle. For the next chat, the user uploads **both files**, uses `NEXT_CHAT_START_PROMPT.md` (included inside the pack/bundle), and the new reader validates the previous SHA/UID prefix before appending.
- The planned 18 chats process 5 chunks each except Chat18 (86–87). If context limits occur before 5 chunks, stop safely with a PARTIAL/COMPLETED record and reopen a fresh chat with the **same** assigned pack plus latest Handoff Bundle.
- No invisible background execution. Do not claim a chunk complete until actual 12-target per-study annotation and structural validation finishes.

## Programmatic validation

A self-contained `validate_and_merge.py` is included with each Chat Pack. Its checks cover:
- Exact source report SHA / global index / source CSV row / chunk ID / chat ID / Study UID
- Exactly 12 targets and correct criterion IDs for every UID, with no missing/extra/duplicate pairs
- Five-state mapping, mask, reason, review priority/flags
- Literal report evidence and Unicode codepoint offsets for new chunk
- Version tags `LABEL-V6-GPT6-chat-v2`
- Prior Master SHA agreement with prior handoff and contiguous prefix coverage in the 4,349-source UID index
- Candidate output and next handoff file creation after checks pass

**Structural PASS does not establish semantic or clinical correctness.** Synthetic test data used to validate the code must never be offered as a label result.

## Final release gate

After Chunk087, audit 4,349/52,188 coverage, target-level positive/negative/masked and all five-state distribution, exact duplicates, multilingual behavior, HIGH/flagged/inference-used cases, and stratified LOW/MEDIUM samples. Use GPT-6 Astra for final adjudication if available; otherwise flag for suitable further review. Freeze canonical labels with SHA only after those checks. Only then calculate positive class weights and begin R3D-13 / Exp57 comparisons. Gold58 validation remains non-independent because it has been repeatedly used for prior development.

## Confidentiality

Do not upload raw report text, patient identifiers, per-study labels, or workbench packs to the **public** GitHub repo. This file is process metadata only.
