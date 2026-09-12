# Canonical dataset manifests

`v1-dataset-manifest.json`, `v2-dataset-manifest.json`, and
`v3-dataset-manifest.json` define the canonical public artifact sets and exact
SHA-256 hashes. `source-provenance-manifest.json` protects the provenance
registry.

Former software-release manifests are intentionally excluded from the public
tree. Their history remains in Git.
Current contracts are defined in `docs/guides/versioning.md` and checked by
`src.internal.verify_versions`.

The [validation guide](../data/validation/README.md) describes independent
source checks and their coverage. The [manuscript analysis guide](../paper/analysis/README.md)
explains the publication samples and sensitivity results.
