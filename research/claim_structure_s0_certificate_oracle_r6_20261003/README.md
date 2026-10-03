# S0-R6 source-bound scope/obligation certificate successor

Tracking: issue #63.

Frozen predecessor: Draft PR #62 at `45607c923d03c36299f0a6cea29be287d538fcff`.

Predecessor disposition: `FALSIFIED_EVALUATION_SURFACE`.

## Why this successor exists

R1-R5 showed that raw local model classifications and free-form witness generation are not sufficient decisive gold for proposition-structure research. The failure was not just disagreement. The models could:

- call a clear composite atomic;
- silently resolve material ambiguity;
- change `or` to `and`;
- omit a location-qualified reading;
- drop predicate subjects;
- change class under an identical seeded request.

This successor changes the evaluation object rather than retrying the same oracle.

## Hypothesis

A usable S0 evaluation surface may be possible if semantic expectations are encoded as **source-bound certificates** whose obligations are inspectable rather than inferred from reviewer confidence.

A certificate binds:

- exact root bytes;
- exact predicate spans;
- explicit semantic-role bindings;
- explicit operator identity;
- explicit scope attachment;
- explicit material qualifiers;
- every materially live reading when ambiguous;
- a completeness ledger accounting for every material semantic obligation;
- external provenance for the analysis where public annotated examples exist.

Reviewers verify a frozen certificate against the root/source. They do not freehand a scalar class from memory.

Agreement remains reproducibility evidence only.

## External design basis

The certificate shape borrows useful ideas from several established annotation/evaluation traditions:

- PropBank / semantic-role labeling: explicit predicate-argument roles.
- QA-SRL: natural-language role annotation and the importance of coverage/completeness.
- Controlled QA-SRL annotation: independent review/consolidation because superficially valid annotations can omit semantic roles.
- UMR / scope-aware meaning representation: explicit treatment of negation, modality and quantifier/scope structure.
- FactLens: decomposition quality requires context preservation and semantic equivalence.
- DnDScore: decomposition/decontextualization can lose or inject verification-relevant context.

References are recorded in `RESEARCH-BASIS.md`.

## Boundary

This experiment qualifies only the **evaluation packet**.

It does not:

- qualify an LLM proposer;
- qualify an NLI/verifier;
- authorize S1 or S2 automatically;
- modify frozen V1;
- modify Contract A;
- emit production proposition authority.

## Required terminal outcomes

Allowed dispositions:

- `SUPPORTED_CERTIFICATE_SURFACE_FOR_S0_PACKET`
- `FALSIFIED_CERTIFICATE_SURFACE`
- `INCONCLUSIVE_CERTIFICATE_SURFACE`
- `BLOCKED_CERTIFICATE_SURFACE`

A supported result authorizes creation of a fresh targeted S0 packet and nothing more.
