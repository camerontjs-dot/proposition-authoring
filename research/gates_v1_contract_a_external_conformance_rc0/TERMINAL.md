# Gate V1.0.0 → released Contract A 2.0.0 external conformance RC0 — Terminal

**Disposition:** `FALSIFIED_GATE_V1_RELEASED_CONTRACT_A_PRODUCER_CONFORMANCE`

## Exact subject

Gate V1.0.0 frozen compatibility tree:

`c0da10e2e3b9aada5f66af9859cf27964fd3c5fc`

Released Contract A 2.0.0 validator authority:

`529c92b49a34d5c610618551a8737f019f9fa332`

Research apparatus head:

`a9abccca946a55520c84f44d89f44a09e5f2207b`

## Decisive run

- workflow run: `35299488386`
- job: `105458929065`
- conclusion: `success`
- artifact: `10529148309`
- artifact digest: `sha256:a095447e39396d37953b6fb7c9b97295d548ef6b7cc355f5a5e25d740246c0e1`
- artifact expiry currently reported: `2026-12-17T02:28:53Z`

## Primary observation

The unmodified frozen Health Canada specimen uses `text/html` for both supplied sources.

Exact Gate V1.0.0:

- completed the authoring run;
- emitted Contract A;
- accepted the bundle under its maintained Gate bundle verifier.

The exact released Contract A 2.0.0 validator then rejected the emitted object:

`$.sources[0].media_type must be one of ['text/markdown; charset=utf-8', 'text/plain; charset=utf-8']`

## Control

The control changed only both source media types to:

`text/plain; charset=utf-8`

The same Gate subject completed, and the same exact released Contract A 2.0.0 validator accepted the emitted Contract A.

## Interpretation

The defect is isolated to Gate / Proposition Authoring producer conformance at the Contract A source-representation boundary.

This result does not justify widening Contract A or Evidence Bundler. The released Contract A validator and frozen Evidence Bundler are behaving consistently with the released Contract A vocabulary.

The current in-repo Gate bundle verifier is insufficient as a substitute for exact released Contract A producer validation because it checks Contract A structure/integrity but does not enforce the released media-type vocabulary.

## Governance consequence

The frozen Gate V1.0.0 compatibility tree remains valuable evidence and should not be rewritten.

However, immutable V1.0.0 publication/tagging should not claim released Contract A producer conformance from this exact tree unless a bounded successor corrects the producer boundary and requalifies the affected release gate.

No Gate semantic widening, Contract A widening, EB change, CAL change, Decision change, Authorization, or release is authorized by this record.
