# ClaimGate Claim Profile V0

## Purpose

ClaimGate may eventually describe useful characteristics of an incoming claim in addition to authoring its proposition structure. This sidecar defines the first observation surface for that idea without expanding ClaimGate's current semantic authority.

The sidecar is **shadow-only, non-authoritative, and non-causal** during V1 qualification.

It is not Contract A. It must not be embedded into Contract A objects. It must not affect whether ClaimGate returns `NOT_NEEDED`, `DECLARED`, `ABSTAINED`, or `FAILED`.

## Candidate characterization fields

A future observation may include:

- `domain`: coarse subject/industry such as healthcare, finance, software, scientific, regulatory, legal, operations, or `unknown`;
- `claim_family`: one or more descriptive families such as empirical, comparative, temporal, causal, attributional, numeric, definitional, existence, status/state, compliance, or `unknown`;
- `verification_world`: `open`, `closed`, `hybrid`, or `unknown`;
- `verification_world_basis`: explicit task/source authority supporting the world assumption, or `unknown`;
- `evidence_expectations`: descriptive expected evidence forms such as document/text, database record, measurement, event record, authoritative declaration, or `unknown`;
- `jurisdiction`: only when explicitly supplied or mechanically recoverable from authoritative context; otherwise `unknown`;
- `temporal_scope`: only when explicitly supplied or mechanically recoverable; otherwise `unknown`;
- `notes`: receipt-visible observations that do not carry authority.

## Open-world / closed-world rule

Open versus closed world is usually a property of the verification task, not a property of sentence wording alone.

ClaimGate must not infer a causal verification regime merely because a claim sounds domain-specific.

Examples:

- `closed`: the task explicitly limits truth determination to a named database, dossier, corpus, register, or other bounded evidence universe;
- `open`: the task explicitly permits relevant evidence beyond a bounded supplied corpus;
- `hybrid`: the task explicitly combines bounded authoritative records with permitted external evidence;
- `unknown`: no adequate authority establishes the regime.

For V0 shadow observations, uncertain classification remains `unknown` rather than being forced.

## Causal boundary

Until separately qualified, Claim Profile fields may not:

- change Contract A content or validity;
- grant or deny decomposition authority;
- choose Evidence Bundler sources, queries, ranks, retention, or admission;
- select or rewrite CAL semantic families;
- alter Decision Engine policy or effects;
- substitute for explicit task authority.

If later testing shows a field is reliably useful, promotion of that field into a causal role requires its own evidence and explicit ownership boundary.

## V1 testing use

Naturalistic shadow qualification may record these fields beside authoritative ClaimGate receipts to answer observational questions such as:

- Which domains and claim families are common in intended use?
- Where does ClaimGate safely resolve versus abstain?
- Would domain or evidence-form classification have helped retrieval?
- Does an explicitly supplied verification-world regime matter downstream?
- Which candidate labels are unstable, ambiguous, or unhelpful?

No downstream component should read this sidecar during the first V1 pipeline smoke.
