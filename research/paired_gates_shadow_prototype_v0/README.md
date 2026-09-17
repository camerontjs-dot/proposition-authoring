# Paired Gates Shadow Prototype V0

This directory records the executable prototype tracked by issue #28 and Draft PR #29.

The prototype is stacked on the exact ClaimGate successor subject `7daaf3031b405499851b4d3fd946a05c53a25f25`. It does not change existing ClaimGate authoring semantics or Contract A behavior.

## Runtime

Run:

```bash
paired-gates-shadow REQUEST.json --out OUT_DIR
```

The ordinary authoring request fields remain unchanged. Optional shadow metadata may be supplied under a top-level `shadow` object:

```json
{
  "handoff_id": "h1",
  "producer_id": "local",
  "producer_version": "0",
  "work_id": "w1",
  "root_id": "c1",
  "root_text": "Drug A had 20% higher response than Drug B in 2025.",
  "sources": [
    {"source_id": "s1", "media_type": "application/pdf", "content": "..."}
  ],
  "shadow": {
    "claim": {
      "domain": "healthcare",
      "verification_world": "open",
      "jurisdiction": "Canada"
    },
    "evidence_world": {
      "verification_world": "open",
      "corpus_scope": "supplied packet",
      "completeness_state": "not_claimed",
      "known_gaps": []
    },
    "sources": [
      {
        "source_id": "s1",
        "provenance": "named issuer",
        "source_role": "primary_authoritative_record",
        "evidence_form": "document_text",
        "temporal_coverage": "2025",
        "jurisdictional_coverage": "Canada"
      }
    ]
  }
}
```

## Outputs

The wrapper emits the normal ClaimGate receipt and Contract A when present, plus:

- `CLAIM-PROFILE.json`
- `CLAIM-PROFILE-RECEIPT.json`
- `EVIDENCE-WORLD-PROFILE.json`
- `EVIDENCE-WORLD-RECEIPT.json`
- `PREFLIGHT-COMPATIBILITY.json`
- `PREFLIGHT-COMPATIBILITY-RECEIPT.json`

All shadow outputs are content-bound. They are non-authoritative and non-causal.

## Machinery

Claim Profile V0 uses bounded transparent detectors for descriptive claim-family observations and mechanically recoverable temporal scope. Domain, jurisdiction, and verification-world declarations are taken only from explicit task metadata.

EvidenceGate inventories exact supplied source representations, hashes their content, records explicit provenance/source metadata, and mechanically maps only a small known media-type surface to evidence forms. Unknowns remain unknown.

Preflight Compatibility V0 compares claim-side expectations against evidence-world availability for evidence form, temporal scope, jurisdiction, and verification world. It emits only `match`, `mismatch`, `partial`, `unknown`, or `not_applicable` observations.

## Protected boundary

This prototype does not:

- change ClaimGate authoring decisions;
- change Contract A;
- retrieve, rank, retain, or admit evidence;
- change Evidence Bundler or Contract B;
- judge SUPPORTS/REFUTES;
- select CAL semantic families;
- change Decision behavior.

A later causal use of any field requires separate qualification.
