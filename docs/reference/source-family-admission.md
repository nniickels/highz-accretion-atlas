# Source-family admission

Source families are ingested as reviewed batches rather than appended directly
to processed CSVs. Each batch must include:

1. immutable source-native extraction files and archive hashes;
2. a source-registry entry and exact publication/version metadata;
3. a deterministic adapter to the canonical admission schema;
4. reviewed identity overrides where automatic matching is insufficient;
5. source-local observables and caveat tags;
6. regression anchors for source membership and published values;
7. complete regeneration of every affected canonical dataset and manifest.

New literature membership creates a new dataset version rather than mutating
v3. Publication-status and provenance corrections may update metadata without
changing scientific membership. No source family authorizes pooled demographic
claims without an explicit selection/completeness model.

The admitted families and their extraction records are indexed in
[`../source-notes/README.md`](../source-notes/README.md); canonical membership is
defined by [`../guides/versioning.md`](../guides/versioning.md).
