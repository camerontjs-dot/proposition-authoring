# Admission rules

A certificate is admitted only when all of the following hold:

1. The frozen mechanical validator returns no errors for that certificate and its external requirements.
2. Every eligible reviewer returns `ACCEPT_COMPLETE` for the reviewer-facing certificate.
3. Every material objection is answered by an adjudication that cites the frozen root or the cited published analysis.
4. No material objection remains unresolved.

Reviewer agreement is not semantic authority. A reviewer acceptance does not repair a validator error. A validator pass does not repair a material objection.

If reviewers disagree and the source does not resolve the disagreement, the certificate is not decisive gold.

A hostile copy is rejected when the validator returns an error, or when an eligible reviewer returns a verdict other than `ACCEPT_COMPLETE`. The admitted original is not edited to produce the copy.

Accepting a hostile copy that the validator also accepts falsifies the protocol.

The only terminal dispositions are:

- `SUPPORTED_CERTIFICATE_SURFACE_FOR_S0_PACKET`
- `FALSIFIED_CERTIFICATE_SURFACE`
- `INCONCLUSIVE_CERTIFICATE_SURFACE`
- `BLOCKED_CERTIFICATE_SURFACE`

A supported result authorizes only a later targeted S0 packet. It does not authorize a proposer, model, verifier, resolver, production ClaimGate change, or Contract A change.
