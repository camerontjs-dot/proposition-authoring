# RC4b terminal disposition

## Disposition

**SUPPORTED FOR PROMOTION**

Experiment classification: **SUPPORTED_FOR_RC5_CONSUMER_CONFORMANCE**.

This result authorizes only RC5, Evidence Bundler Contract A consumer conformance. It does not authorize merge to production semantics, release, tag, pipeline insertion, or production use.

## Exact lineage and freezes

- neutral programme `main`: `a4f018285ffc6d2c5755b2cc02a751799f1511a1`
- RC3 integrated predecessor: `50a943c401f8a09d5bb940472bdad43b54dca5d0`
- terminal RC4 evidence: `c1814952e84bec2f32f8e122c9cde901ed8a9796`
- RC4a scientific source: `f9d0ae9ba81756c51d7f1d433616d699eb9b6fd3`
- RC4a target/harness freeze: `9c76b3d87b4362b79a22c0467a13a48c0a380a16`
- RC4a fresh seal / decisive head: `805bccc7f1ac338c9c8b463c6441cee5ae1e0a37`
- RC4a terminal evidence: `e218f99bdaa67b242d8a077452cbe5f269498208`
- RC4b target freeze: `96c203e1abec02117eb56040149da595f3f8cec7`
- RC4b fresh seal / decisive head: `e29f824c99a85dfda871c5091c0615af38419631`
- Draft research PR: #22, intentionally left unmerged

At RC4b target freeze, no RC4b fresh cases or gold existed. Hosted freeze verification completed successfully before fresh authoring, and no target output was observed before the fresh surface was atomically sealed.

## Hosted evidence

Target-freeze verification:

- run: `34803417338`
- job: `103850452463`
- artifact: `10332281278`
- artifact digest: `sha256:c1a8975ceb903f9c69a1fd5e1b9883dc10db3e96de12829f0f2d29c0d1661086`

Decisive reproduction:

- run: `34803657202`
- job: `103851145236`
- artifact: `10333075196`
- artifact digest: `sha256:013e77edb5d15a0fc99b4f45498e165a2cdc400e37cea061b8521fde61d5b781`

## Decisive observations

The sealed cohort contained 44 fresh roots: 14 aligned P5 safe, 7 P4 safe, 7 baseline safe, 4 single propositions, 4 prospectively out-of-profile P5 roots, and 8 fail-closed adversaries.

Observed decisive results:

- 44/44 exact case correctness
- 36/36 safe-root correctness, 100%
- aligned P5: 14/14 correct, with no missing in-profile proposals
- P4: 7/7 correct, with no missing in-profile proposals
- baseline controls: 7/7 correct
- single propositions: 4/4 correctly `NOT_NEEDED`
- out-of-profile P5: 4/4 correctly non-authoritative; aligned P5 proposed on 0/4
- weak prealignment P5 control proposed on all 4 out-of-profile roots, demonstrating that the competence boundary was capable of failing
- fail-closed adversaries: 8/8 correctly `ABSTAINED`
- unsafe authoritative outcomes: 0
- wrong authoritative decompositions: 0
- P5 competence-envelope leaks: 0
- processing failures: 0
- Contract A authoritative emissions: 32
- Contract A validation failures: 0
- abstention Contract A leaks: 0
- two clean candidate trees identical
- provision receipts byte-identical
- raw outputs byte-identical

The aligned P5 competence declaration remained exactly:

`active, approved, compliant, failed, inactive, passed, ready, restarted, stopped`

`rejected` remained outside P5 competence. No semantic-authority widening occurred.

## Decisive hashes

- fresh cases SHA-256: `0b8d0faaa9cb18d9418f27ec4aa4190e46bec2abb30e0e94b09b83a1fc9c281a`
- hidden gold SHA-256: `166cfbaac811c5147ed479879756a452dfa5af44e6d7527070ada1233b7f5a27`
- candidate tree SHA-256: `840a7e7d22824000bad2333b49fef3df58bee1a96e3fd357bc8ec065d51d470a`
- raw A/B SHA-256: `0cd561395d576190e0237f8a12042d0bdeeae996b567af2e54697e7d1546cc05`
- provision A/B receipt SHA-256: `db899d732029ae4ca15d9b339cee8eb7ec260835fd0478adb9a96da82ef8c7cf`
- replay receipt SHA-256: `6ae4c5e3355cd8ed48cc96a8b04de091db872d8b5748373c964fe4c1dd80735d`
- score SHA-256: `9b42e35662b680dfe87fe8b0c46dcf310c11b736b287e21985d3b86e640867ed`
- task packet SHA-256 observed by both provisions: `0e289bbb36273cc23c8c4f234b59c4c3660231b596c6e788066df09fa67e881b`

Fresh surface Git blobs:

- cases: `c367f9fc46c167ee1e191d66d287542c2dca8c0f`
- gold: `181eb6a6f73c5ef266b2a1c62e52d367f0281167`
- fresh-freeze receipt: `cf16d71667f3b579dd2f34f14f72764b67a42df5`

## Deviations and apparatus record

A pre-freeze repository transport limitation prevented direct local-network cloning and one low-level commit attempt was rejected by connector policy. Repository operations were moved to the authenticated GitHub connection before target freeze; hosted GitHub Actions performed the actual frozen reconstruction and decisive executions. This caused no post-freeze scientific-file change, no fresh-surface repair, and no hosted apparatus failure.

No scientific counterexamples were observed in the sealed cohort.

## Epistemic interpretation

**Observed:** the exact hashes, reconstruction equality, raw replay, per-family scores, competence-boundary behavior, Contract A validator results, and hosted workflow identities above.

**Inference:** under this frozen apparatus and fresh cohort, a context-free executor can reconstruct and execute the exact RC4a-aligned Proposition Authoring candidate while preserving its bounded safety, coverage, competence contract, determinism, and Contract A behavior.

**Hypothesis:** RC5 can now test whether Evidence Bundler conforms as a Contract A consumer of this supported upstream handoff.

**Unknown / non-claims:** RC4b does not establish production fitness, universal semantic correctness, wider proposer competence, an independent semantic reimplementation by another model family, Evidence Bundler consumer conformance, or permission to merge/release/tag/deploy this research branch.

## Terminal routing

Issue #21 is terminal and should be closed completed. RC5 issue #10 becomes eligible. The next research boundary is RC5, but RC5 is not started automatically by this disposition.
