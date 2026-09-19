# Gate V1 Contract A media-boundary successor RC1 — preregistration

**Status:** frozen before successor implementation

## Objective / decision

Determine whether the smallest fail-closed producer-boundary correction can make the paired ClaimGate + EvidenceGate V1 surface safe to compose with released Contract A 2.0.0 without changing qualified claim semantics, EvidenceGate representation semantics, or valid Contract A bytes.

If supported, the result may justify a minimal production-slice candidate and a later PATCH promotion. It does not itself authorize merge, release, Evidence Bundler changes, CAL changes, Decision changes, or Authorization.

## Authority

Frozen predecessor:

- tag: `v1.0.0`
- release commit: `c0da10e2e3b9aada5f66af9859cf27964fd3c5fc`
- release tree: `4ea9d0fa5ab9d926e0bf960da2103be8c202d400`

Maintained-base convergence subject:

- PR #51 head: `a66b23b413bb5e51626c32694261a71c7b69d5ea`
- tree: exactly `4ea9d0fa5ab9d926e0bf960da2103be8c202d400`

Preserved falsifier:

- PR #50 terminal disposition: `FALSIFIED_GATE_V1_RELEASED_CONTRACT_A_PRODUCER_CONFORMANCE`
- terminal head: `656d95d9c9ba03a7f785322cdba1f29149df04bd`
- confirmation run: `35299554178`
- artifact digest: `sha256:e5e5f5d5fd42c131c23603eb10227d97fa1ec5375e3a9b4a9da32c0be39308fb`

Released downstream authority:

- repository: `camerontjs-dot/apparatus-contracts`
- Contract A 2.0.0 release commit: `529c92b49a34d5c610618551a8737f019f9fa332`
- accepted source media types:
  - `text/plain; charset=utf-8`
  - `text/markdown; charset=utf-8`

## Boundary

In scope:

- the paired Gate V1 production-shaped path only;
- preventing that path from emitting a Contract A object that released Contract A 2.0.0 rejects solely because of source representation media type;
- explicit fail-closed behavior when the supplied representation cannot be carried by Contract A 2.0.0.

Allowed successor mutations:

- the minimum runtime boundary check;
- focused tests;
- one qualification workflow/evaluator;
- research/result records.

Protected / prohibited changes:

- do not move or rewrite `v1.0.0`;
- do not widen Contract A;
- do not change Evidence Bundler;
- do not relabel unchanged bytes as a different media representation;
- do not transform HTML/other representations in this successor;
- do not change ClaimGate decomposition/classification semantics;
- do not change EvidenceGate identity, source provenance, representation identity, or descriptive authority semantics;
- do not add retrieval, CAL, Decision, or Authorization authority;
- do not repair an observed decisive result by changing this preregistration after exposure.

The intended correction uses the existing `FAILED` authoring state and absent Contract-A binding. No new public Gate state or schema field is authorized.

## Candidate behavior under test

For a supplied source representation outside the exact released Contract A 2.0.0 media vocabulary:

- the paired Gate V1 run must fail closed before downstream Contract A use;
- ClaimGate must report `FAILED` with reason `CONTRACT_A_SOURCE_REPRESENTATION_UNSUPPORTED`;
- ClaimGate `contract_a_binding` must be absent;
- the standardization receipt must set `contract_a_state=absent`, null Contract-A hash, and `evidence_bundler_may_consume_contract_a=false`;
- EvidenceGate must still describe the actual supplied representation, including the actual media type and its resulting representation/evidence-world identity;
- no Contract A object may be emitted.

For inputs whose source representations are already valid Contract A 2.0.0 representations:

- the successor must preserve predecessor authoring, ClaimGate, EvidenceGate, receipt, authoring receipt, and Contract A bytes for the same fixed implementation identity;
- emitted Contract A must pass the exact released Contract A 2.0.0 validator.

## Controls

### Preserved negative / weak predecessor control

Exact `v1.0.0` on the frozen Health Canada `text/html` specimen must reproduce the PR #50 failure: Gate-local verification accepts the emitted object while the exact released Contract A validator rejects it for media type.

This demonstrates that the external conformance gate discriminates the successor from the known-defective predecessor.

### Candidate negative control

The same unchanged `text/html` representation must remain `text/html` in EvidenceGate and must produce no Contract A.

### Positive controls

At minimum:

- exact `text/plain; charset=utf-8`;
- exact `text/markdown; charset=utf-8`.

Both must preserve the predecessor valid path and pass the exact released Contract A validator.

### Mutation / anti-laundering control

Changing only an unsupported representation label to an allowed label without changing the bytes must not be introduced by the successor itself. The implementation may accept an already-supplied allowed representation, but it may not rewrite the request to manufacture conformance.

## Acceptance condition

Support requires all of the following on one exact successor head:

1. predecessor control reproduces the known external-conformance failure;
2. candidate unsupported-representation case fails closed with no Contract A;
3. EvidenceGate preserves the actual unsupported representation and remains reconstructable;
4. exact plain and Markdown positives emit Contract A accepted by released Contract A 2.0.0;
5. valid-path outputs remain byte-identical to `v1.0.0` for fixed inputs/implementation identity;
6. affected maintained Gate tests and release/RC3 regressions remain green except tests whose only purpose was to encode the now-falsified producer behavior;
7. deterministic replay holds;
8. no downstream contract or apparatus is modified.

## Falsifiers

The successor is falsified if any of the following occurs:

- it emits a Contract A rejected by the exact released Contract A 2.0.0 validator;
- it silently relabels or transforms the unsupported source representation;
- EvidenceGate loses or changes the actual representation identity as a side effect;
- valid Contract-A-representable inputs change behavior/bytes beyond the bounded correction;
- the correction requires a new Gate state/schema, Contract A widening, representation transformation, or downstream adapter;
- the external evaluator cannot discriminate the successor from the known-defective predecessor.

## Stop / disposition

Stop on the first decisive falsifier or when the acceptance burden is complete.

Allowed research dispositions:

- `SUPPORTED FOR PROMOTION`
- `FALSIFIED`
- `INCONCLUSIVE`
- `SUPERSEDED`

If a new representation-transformation mechanism is required, stop this successor and open a separate research question rather than widening RC1 after exposure.
