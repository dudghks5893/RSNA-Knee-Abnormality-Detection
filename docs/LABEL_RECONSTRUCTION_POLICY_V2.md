# RSNA Knee — Report Label Policy v2 (competition-aligned freeze)

Date: 2026-10-08

## Source of truth

The label definition is frozen from the RSNA/Kaggle competition host description. The competition score is the unweighted mean of the 12 per-target ROC AUCs. Existing V4 pseudo labels, Gold-based reader routing, previous model scores, and public leaderboard outcomes are not allowed to change this report-to-label policy.

## Official target criteria — operational paraphrase

- ACL: high-grade partial (>50% fiber disruption) or complete tear. Mild signal change/degeneration/thickening without discontinuity is negative.
- MCL: acute high-grade partial or complete tear with fiber disruption; low-grade sprain and chronic/remote stress change are negative.
- Medial/Lateral Meniscus: definite surface-reaching tear or tear morphology. Intrasubstance degeneration not reaching the articular surface is negative. A definitive report diagnosis of tear can serve as report-derived proxy evidence even when the report does not document the two-image criterion.
- Medial/Lateral/PF OA: >50% cartilage-thickness loss over a moderate/large area (roughly >=1 cm), compartment-specific. Small focal high-grade defects do not automatically satisfy the label.
- Effusion: moderate or large joint fluid. Trace/small/minimal/physiologic fluid is negative.
- Synovitis: synovial inflammation/thickening. Do not infer from effusion alone.
- Baker's: moderate or large Baker/popliteal cyst in the characteristic location. Small/trace cyst is negative.
- Contusion: impact-related bone marrow edema/bone bruise without a discrete fracture line at that lesion. Degenerative/reactive/nonspecific edema is not automatically a contusion.
- Fracture: acute fracture line or cortical break. Chronic/healed/remote osseous change is negative.

The host states that borderline/on-the-fence imaging findings were graded negative to favor specificity.

## Five semantic states

### positive -> label=1, mask=1
The report provides current-exam evidence that satisfies the competition criterion. Strong direct diagnostic wording can be used as report-derived proxy evidence; do not claim image-level verification.

### negative -> label=0, mask=1
Use when the target is explicitly absent/normal, explicitly below the competition threshold, or a genuinely borderline/equivocal finding that the host criterion says is graded negative. Examples: low-grade ligament sprain, meniscal degeneration not reaching surface, small effusion, trace Baker cyst.

### insufficient -> label=null, mask=0
The report discusses the target but omits an attribute required to map it to the competition threshold. Examples: `effusion` with no amount, `Baker cyst` with no size category, `cartilage thinning` without depth/extent, generic partial ACL tear without enough information to know whether >50% fibers are disrupted. This is not a negative label.

### not_mentioned -> label=null, mask=0
No target-specific finding is provided in an otherwise usable report. Absence of mention is never a negative.

### uncertain -> label=null, mask=0
Reserve for uncommon cases that cannot be safely mapped even after applying the rules: internally contradictory findings/impression, unclear laterality/current-vs-history, corrupted/ambiguous terminology, or examination limitation preventing interpretation. Do not use `uncertain` merely because the finding is below threshold or described as borderline.

## Assertion-strength rules

- Definitive diagnosis / explicit morphology meeting threshold -> positive.
- Explicit normal / absent / below-threshold -> negative.
- `possible`, `suspicious`, `equivocal`, `cannot exclude` without threshold-confirming morphology -> negative if it is an on-the-fence finding under the official criterion; use insufficient instead if the real problem is missing required severity/extent information.
- `likely/probable/consistent with` is not automatically positive. It can support positive only when independent morphology/severity in the same report already meets the target criterion; otherwise withhold or grade negative according to the criterion.
- Clinical history, indication, prior study statements, and surgery history are not current positive findings unless the current findings/impression confirms them.

## Target-specific edge rules

- ACL/MCL: `sprain` alone is not a high-grade tear. Generic `partial tear` with no high-grade/>50% evidence is insufficient or negative when explicitly low-grade/borderline.
- Meniscus: a definitive `tear` diagnosis is positive. `degeneration`, `grade-2-like intrasubstance signal`, or `no surface contact` is negative. A suspected/possible tear without confirming morphology is negative under the host borderline rule.
- OA: do not translate an unknown grading system into the competition threshold. `bone-on-bone`, diffuse/extensive high-grade loss, or severe compartment-specific cartilage loss can satisfy the proxy criterion. Focal full-thickness defect with unknown/small extent is not automatically positive.
- Effusion: unspecified amount -> insufficient.
- Baker's: unspecified size or ambiguous Baker-vs-ganglion identity -> insufficient/negative according to whether the issue is missing size or true diagnostic ambiguity. Do not invent a cm cutoff because the host did not publish one.
- Contusion: marrow edema explicitly attributed to fracture, OA, stress, degeneration, meniscal pathology, or another non-impact cause is negative for contusion. Nonspecific marrow edema with no etiology is insufficient.
- Fracture: explicit current/acute fracture is positive. Chronic/remote fracture is negative. A different bone lesion (AVN, cyst, sclerosis, reactive edema) is not fracture evidence.

## Evidence contract

Every positive/negative must retain exact original report evidence. Evidence must be literal text from the source report with zero-based Python Unicode offsets. No fabricated translation may be stored as evidence. Translation/explanation is secondary metadata only.

## Gold and V4 isolation

- Official Gold58 x 12 labels are immutable.
- Do not show Gold outcomes or V4 labels to the readers.
- V4 is historical distribution/comparison evidence only.
- After the policy is frozen, a blind one-time Gold audit may be used descriptively; do not iteratively alter the policy to improve Gold agreement and then call Gold independent validation.
