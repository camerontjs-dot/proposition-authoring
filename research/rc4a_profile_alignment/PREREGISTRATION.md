# RC4a Preregistration — P5 / Semantic-Authority Competence Alignment

## Status

Research experiment only. No production authorization, release, merge, Contract A amendment, Evidence Bundler integration, or semantic-authority widening.

## Trigger

Terminal RC4 #9 / PR #18 was `INCONCLUSIVE_REPRODUCTION_COVERAGE_DIVERGENCE`. Context-free reconstruction mechanics passed, but P5 achieved 6/8 fresh safe cases because two roots containing `rejected` received a P5 proposal that the exact frozen RC1 authority could not warrant.

Revealed RC4 cases C09/C14 are development counterexamples only. They cannot count toward RC4a qualification.

## Question

Can P5 prospectively restrict its advertised proposal surface to the exact intersection between its pre-RC4a embedded-predicate profile and the frozen semantic-authority competence profile, while retaining useful in-profile coverage and preserving fail-closed safety?

## Frozen semantic authority

RC4a may not modify the RC2/RC3 authority boundary. These RC3 target-freeze objects remain authority inputs rather than experimental variables:

- `src/proposition_authoring/ambiguity.py` blob `133de6b2a4cfa7fc58d1f0f38a80b1c9ebb0b19d`
- `src/proposition_authoring/authority.py` blob `1c05f7261171ad5176fbbb19bf164bd10db2b78c`
- `src/proposition_authoring/backend.py` blob `bcc03f1d1ec3e78591cd339d3a8600d020faf643`
- `src/proposition_authoring/conservation.py` blob `dbe69e8bde1d9f485f3f16ba7d50f0bd86dff5a1`
- `src/proposition_authoring/coverage_backend.py` blob `345dee65468e886b2016eb8b8335aabf46b50a02`
- `src/proposition_authoring/engine.py` blob `d122e70d92708e3bef0af465feb7988abca960fa`

## Experimental change

Only the P5 proposal competence declaration changes.

Pre-alignment advertised predicates:

`active, approved, compliant, failed, inactive, passed, ready, rejected, restarted, stopped`

Prospective authority-compatible intersection:

`active, approved, compliant, failed, inactive, passed, ready, restarted, stopped`

`rejected` is prospectively out of profile. The aligned P5 lane must emit no proposal when either embedded clause falls outside the declared intersection.

The pre-alignment ten-token P5 surface is preserved as a weak control.

## Development burden before freeze

1. Every declared aligned token must produce a candidate that the exact frozen authority accepts in a controlled `reported that A and B` construction.
2. Revealed C09/C14 must be suppressed by aligned P5 while the pre-alignment weak control still proposes them.
3. At least one authority-only token outside both P5 profiles must demonstrate that authority can be broader than P5 without automatically expanding P5.
4. Existing inherited tests must remain green.
5. No fresh RC4a cases or gold may exist before target/harness freeze.

## Fresh decisive surface

Author only after freeze. Planned shape: 36 roots.

- 18 `INTERSECTION_SAFE`: two fresh roots for each of the nine aligned predicates/states.
- 6 `PROPOSER_ONLY_BLOCKED`: fresh `rejected` mutations. Aligned P5 must emit no proposal; pre-alignment weak P5 must emit one.
- 6 `AUTHORITY_ONLY_BLOCKED`: predicates the authority can warrant but neither P5 profile declares. Both P5 lanes must abstain; an independent authority probe must establish candidate warrantability.
- 6 `FAIL_CLOSED`: scope/connective/negation/reference hazards that the integrated pooled apparatus must leave non-authoritative.

Gold is sealed after target freeze and removed from the workspace before raw execution.

## Positive gates

A positive RC4a requires all of the following on fresh evidence:

1. zero unsafe pooled authoritative outcomes on `FAIL_CLOSED` roots;
2. aligned P5 emits no proposal outside `INTERSECTION_SAFE`;
3. at least 90% exact P5 finalization on `INTERSECTION_SAFE` roots;
4. 100% aligned-P5 abstention on `PROPOSER_ONLY_BLOCKED` roots;
5. the pre-alignment weak control proposes on all `PROPOSER_ONLY_BLOCKED` roots, demonstrating the misalignment mutation;
6. 100% aligned and pre-alignment P5 abstention on `AUTHORITY_ONLY_BLOCKED` roots while the independent authority probe accepts all of them;
7. all emitted Contract A objects validate against released Contract A 2.0.0;
8. exact raw replay;
9. exact semantic-authority blob identities remain unchanged.

Any unsafe authoritative outcome is an immediate `FALSIFIED` result. Proposal leakage outside the declared aligned profile or semantic-authority byte drift is also `FALSIFIED`.

If safety holds but one of the coverage/control gates misses, disposition is `INCONCLUSIVE`.

If all gates pass, canonical governance disposition is `SUPPORTED FOR PROMOTION` with experiment-specific classification `SUPPORTED_FOR_SUCCESSOR_RC4_REPRODUCTION`. Promotion means only that one successor integrated candidate may enter a new context-free reproduction experiment. RC5 remains ineligible until that successor reproduction passes.
