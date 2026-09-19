# Gate V1 production slice → Evidence Bundler V1 consumer conformance

**Status:** frozen before cross-repository execution

## Decision

Determine whether the exact qualified Gate production-slice candidate can hand its valid Contract A output to the current Evidence Bundler V1 local-pipeline slice without hidden translation, while the unsupported-representation path still stops before Evidence Bundler.

This is a next-consumer conformance check under the minimal-production-slice convention. It does not re-open Gate semantics, Evidence Bundler retrieval policy, Contract B semantics, or CAL semantics.

## Exact subjects

Gate candidate:

- repository: `camerontjs-dot/proposition-authoring`
- exact candidate commit: `c3d04eadfc74c6614836533c24476252e3dd74f6`
- predecessor release: `c0da10e2e3b9aada5f66af9859cf27964fd3c5fc`
- Gate qualification run: `35419559454`
- Gate qualification artifact: `10576936659`
- artifact digest: `sha256:7b960025eee635e4d4c56330361df084ce8f8bfe58d277e486990796d09ceb6b`

Evidence Bundler consumer:

- repository: `camerontjs-dot/evidence-bundler`
- Draft PR: #120
- exact consumer head: `e8fe42b8f58099885a5530665e9047be5f531b6a`
- input authority: released Contract A 2.0.0 at `529c92b49a34d5c610618551a8737f019f9fa332`
- output authority: Contract B 1.2 production lock `c314e53bd91c0736aa4370a364673b069aceb43e`

The consumer PR's Contract-B/CAL conformance job has already passed on this exact head. Its overall promotion qualification is not green because maintained format checks currently reject copied files. This test does not reinterpret that separate blocker.

## Boundary

Allowed:

- execute exact pinned subjects;
- derive a valid plain-text control from the frozen Health Canada packet by changing only supplied media declarations before Gate execution;
- compare outputs mechanically;
- invoke the exact EB consumer with Gate-emitted Contract A.

Forbidden:

- edit either subject during the run;
- transform or relabel Gate output between Gate and EB;
- supply private adapter state;
- change retrieval, admission, Contract B, or CAL semantics;
- treat EB's separate format-only promotion blocker as cleared by this test.

## Controls and acceptance

### Valid-path control

1. Build one packet using exact `text/plain; charset=utf-8` source representations.
2. Run exact released Gate V1.0.0 and exact Gate successor with the same fixed implementation identity.
3. Require complete Gate output directories to be byte-identical.
4. Feed each emitted `CONTRACT-A.json` directly to the exact EB consumer, using the exact PR #120 compatibility carrier and no special admission override.
5. Require both EB invocations to complete.
6. Require the complete EB output directories to be byte-identical.

This establishes that the bounded Gate correction does not perturb the already-valid downstream path.

### Unsupported-representation stop control

1. Run the exact Gate successor on the unchanged frozen `text/html` packet.
2. Require no `CONTRACT-A.json`.
3. Require the existing fail-closed ClaimGate/receipt state.
4. Do not invoke EB because there is no valid handoff.

### Hostile predecessor control

1. Run exact V1.0.0 on the same unchanged HTML packet.
2. Require it to emit the known-invalid Contract A.
3. Present that object directly to the exact EB consumer.
4. Require EB to reject it at Contract A intake.

This demonstrates that the consumer does not merely tolerate the defect the successor is intended to block.

## Dispositions

- `SUPPORTED FOR PROMOTION`: all three controls behave exactly as specified.
- `FALSIFIED`: Gate successor perturbs the valid EB path, leaks an unsupported A, or EB accepts the hostile predecessor object.
- `INCONCLUSIVE`: the apparatus cannot execute the exact pinned subjects or failure cannot be localized.
- `SUPERSEDED`: an authority changes before execution such that the pinned consumer is no longer the intended slice subject.

A green Gate-local run alone is not sufficient.
