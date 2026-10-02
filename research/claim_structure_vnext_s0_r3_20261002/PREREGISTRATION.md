# S0-R3 constrained-format discrimination

S0-R2 produced internally inconsistent rows before completing its frozen review
sequence: U01 and U02 were labeled AMBIGUOUS although the basis described one
atomic assertion and no competing readings were supplied. U04 split a visibility
condition into a fragment child. Preserve every R2 response and its frozen rule.

## Question

Does response-format presentation alter a reviewer's semantic label under the
same prompt, exact root and settings? The heaviest assumption is that an
annotation schema merely serializes a semantic judgment. It is falsified for
this apparatus if changing only constrained format or class-enum order changes
the judged class or preservation of material obligations.

Competing explanations are constrained-decoder/schema effects, model semantic
review failure, and an inadequate annotation prompt. This diagnostic can separate
format sensitivity from format-invariant failures. It cannot prove which
internal model/decoder mechanism caused an observed change.

## Smallest test

Use three explicitly synthetic controls from frozen R2: a qualified atomic
assertion, a local/shared location-scope ambiguity, and a clear disjunction.
Expected classes were constructed before any R2 model execution. They are never
sent to the reviewers. These are reused diagnostic controls, not fresh public
decisive cases or a naturalistic sample.

Reuse each model's original-schema R2 response as the baseline. Do not reroll it.
For each of the two pinned local model families, make one fresh request per
control using JSON-only format and one using the same schema with only the class
enum order reversed. All prompt bytes, model, seed, temperature and other
request settings remain identical. Cache exact request/response bytes.

Wait for R2 to finish; do not overlap provider inference with the predecessor.
Freeze code, prompt, schemas, selector, models and settings before execution.
No retry or post-output repair is allowed. An apparatus failure remains a failed
cell. Compare labels and obligation content, not confidence or majority votes.

## Evaluation and dispositions

Check row identity/schema and consistency mechanically: AMBIGUOUS requires at
least two alternatives and no selected children; ATOMIC has one complete child;
ALL_OF has at least two children; NON_ALL_OF supplies an unsupported operator;
UNRESOLVED_REVIEW must flag unresolved. Preserve basis text for manual semantic
inspection. Mechanical consistency does not establish semantic correctness.

Report per-model/per-format control errors, consistency errors, class changes
and qualifier/role/operator losses. A class change caused by format alone
falsifies format invariance. Any control error or material content loss
falsifies this raw cold-model annotation architecture as a decisive oracle.
No aggregate threshold can override either falsifier.

Allowed dispositions: FALSIFIED_FORMAT_INVARIANCE,
FALSIFIED_COLD_MODEL_ORACLE, SUPPORTED_BOUNDED_FORMAT_INVARIANCE,
FAILED_APPARATUS. More than one negative finding may coexist. Successful
classification of three controls supports only the bounded diagnostic.

If format sensitivity is observed, a separately frozen successor may use a
format supported by the diagnostic, with fresh public review and deterministic
annotation consistency rejection. If errors persist across formats, narrow the
oracle hypothesis to independent content-bearing scope/obligation annotations
whose material alternatives can be checked before assigning a class. Do not
grant raw LLM labels semantic authority.

S1–S6 remain NOT_RUN until the canonical S0 positive burden is met. No production
runtime or Contract A authority is introduced by this experiment.

> Binds: S0-R3 experiment owner and reviewer execution.
> Tier: T0 for semantic judgments; input identity/JSON shape are separately checked.
> Check: none for semantic correctness; run_format.py records mechanical consistency.
> Escape: retain negative/failed cells and keep S0 blocked for decisive S1.
