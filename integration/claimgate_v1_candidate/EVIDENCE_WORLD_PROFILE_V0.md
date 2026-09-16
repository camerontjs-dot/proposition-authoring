# Evidence World Profile V0

## Purpose

EvidenceGate characterizes the supplied evidence world before Evidence Bundler retrieval. V0 is shadow-only, non-authoritative, and non-causal.

The subject is the available corpus / packet / source universe itself, not the retrieved candidate passages.

V0 must not change Evidence Bundler queries, source routing, ranking, retention, admission, Contract B content, CAL semantic-family selection, CAL judgments, Decision policy, or effects.

## Candidate characterization fields

A future Evidence World Profile observation may include:

- `verification_world`: `open`, `closed`, `hybrid`, or `unknown`;
- `verification_world_basis`: explicit task or source authority establishing that regime, or `unknown`;
- `corpus_scope`: human-readable description of the supplied evidence universe;
- `corpus_scope_basis`: explicit task/corpus declaration or `unknown`;
- `completeness_state`: `complete_for_declared_scope`, `known_incomplete`, `not_claimed`, or `unknown`;
- `completeness_basis`: inspectable authority supporting any completeness claim, or `unknown`;
- `source_inventory`: content-bound source identities and provenance observations;
- `source_roles`: task-designated or provenance-supported roles such as primary_authoritative_record, secondary_reference, interested_party_statement, measurement_record, event_record, or `unknown`;
- `evidence_forms`: forms available in the supplied world, such as document/text, database record, measurement, event record, authoritative declaration, registry entry, or `unknown`;
- `temporal_coverage`: only when explicitly supplied or mechanically recoverable;
- `jurisdictional_coverage`: only when explicitly supplied or mechanically recoverable;
- `known_gaps`: expected or declared sources known to be absent, unavailable, stale, or otherwise outside the supplied world;
- `notes`: receipt-visible observations that carry no authority.

## Authority rule

EvidenceGate does not create authority from persuasive wording, document appearance, semantic similarity, or model confidence.

Any authority or source-role field must be grounded in inspectable evidence such as:

- explicit verification-task declarations;
- source identity;
- provenance / chain of custody;
- issuer identity;
- corpus membership;
- document / record type;
- jurisdiction;
- version / effective date;
- an explicit maintained rule.

If that basis is unavailable or ambiguous, the field remains `unknown`.

## Relation to Claim Profile V0

Claim Profile V0 describes the epistemic problem. Evidence World Profile V0 describes the epistemic resources supplied to investigate it.

Examples of paired observations include:

- claim expects a named closed corpus; evidence world records whether that exact corpus is present and complete;
- claim has a temporal scope; evidence world records available temporal coverage;
- claim has a jurisdiction; evidence world records available jurisdictional coverage;
- claim expects measurements or event records; evidence world records which evidence forms are actually available.

In V0 these comparisons are observational only. They do not alter retrieval or CAL.

## Causal boundary

Evidence World Profile fields may not, during V0:

- judge whether any source or passage SUPPORTS or REFUTES a proposition;
- decide CAL categorical relations;
- infer source truth from prose quality;
- change Contract A or Contract B;
- choose Evidence Bundler queries, ranks, retention, or admission;
- choose or rewrite CAL semantic families;
- alter Decision Engine policy or effects.

## V0 testing use

Naturalistic shadow qualification may record this profile beside Claim Profile V0 to answer questions such as:

- Did the supplied evidence world actually match the declared verification regime?
- Was the corpus known incomplete before retrieval began?
- Were expected evidence forms present?
- Were temporal or jurisdictional mismatches visible before retrieval?
- Would explicit source-role / provenance observations have explained later retrieval or CAL failures?
- Which fields remain unstable, ambiguous, or unhelpful?

Candidate-level evidence characterization and typed reranking are out of scope for this profile and are deferred to Evidence Bundler issue #80 / Draft PR #81.