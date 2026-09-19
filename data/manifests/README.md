# Artifact manifests

`v1-dataset-manifest.json`, `v2-dataset-manifest.json`, and
`v3-dataset-manifest.json` record the canonical artifact sets and SHA-256 hashes.
`source-provenance-manifest.json` records provenance inputs and validation fixtures.

Verify with `python -m src.internal.verify_versions` and
`python -m src.internal.verify_source_provenance`.
See the [reproduction guide](../../docs/guides/reproducibility.md) before refreshing hashes.
Publication outputs are checked separately by the independent reproduction gate.
