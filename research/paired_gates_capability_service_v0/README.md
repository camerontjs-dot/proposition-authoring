# Paired Gates Capability Service V0

This research-infrastructure successor is stacked on exact parent `d9dd911f79c5648b64e8cd84e5045697cef393f4` from Draft PR #34.

Its purpose is capability completeness, not authority promotion.

The runtime now exposes one in-process service surface that returns unchanged ClaimGate authoring output plus Claim Profile V0, Evidence World Profile V0, observational Preflight Compatibility V0, receipts, and a machine-readable feature registry.

Every descriptive field starts at `IMPLEMENTED_SHADOW`. The feature registry and authority firewall prevent those fields from being projected as Evidence Bundler hints unless a later research record explicitly promotes them to `QUALIFIED_HINT`.

Preflight is complete for the V0 contract when it can observe expected/available evidence forms, missing expected forms, temporal scope, jurisdiction, verification world, corpus aperture, declared completeness, and known gaps without steering retrieval or judging support/refutation.

## Nonclaims

This branch does not establish field accuracy, evidence sufficiency, retrieval benefit, production readiness, CAL semantics, Decision policy, or authorization. Individual fields still require separate qualification.
