# RC5 local qualification falsification

The frozen ClaimGate V1 integration candidate at `b3278e960707720f5add10935027a7187725d446` was exercised by the first CAL Pipeline V1 prototype-freeze qualification using the exact public CLI command prescribed by `LOCAL_QUALIFICATION.md`.

Observed on hosted run `camerontjs-dot/research-scaffold-harness` workflow run `35054821028`:

- frozen declared fixture expected `DECLARED`;
- actual public CLI result was `ABSTAINED`;
- reason `NO_UNIQUE_WARRANTED_DECLARATION:ok:none`;
- no authoritative Contract A was emitted.

The failure is preserved in `research-scaffold-harness#34`, artifact `10430556399`, artifact digest `sha256:b1304cceffd2998421c98dfb209e8df627c58e5d4891e833ccd9b3ded65c24c3`.

Live lineage inspection localized the mismatch:

- `proposition-authoring author` invokes `AuthoringEngine()`;
- default `AuthoringEngine()` instantiates `FrozenPredecessorBackend()`;
- RC4b decisive reproduction at `809b2534ffb34efa31c13975da55e65770460b99` explicitly instantiated `AuthoringEngine(CoverageBackend("pooled", vendor_dir=...))`.

Therefore the scientific RC4b pooled result is not itself falsified. The exact integration candidate is falsified because its default executable path is not the semantic subject its frozen smoke expectations assumed.

Do not reinterpret this candidate as RC5-supported. Any successor must be separately preregistered and prove default-runtime equivalence to the exact frozen RC4b pooled subject before rerunning Contract A / Evidence Bundler consumer conformance.
