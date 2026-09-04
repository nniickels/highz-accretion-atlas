# Selection and completeness contract

`data/selection_function_registry.csv` records what each admitted source
publishes about its parent sample, area, thresholds, and completeness. The
generated `results/<version>/tables/<version>_selection_completeness_summary.csv`
joins those declarations to the catalogue counts for that version.

No current source supplies an object-level inclusion probability that is valid
across the union of surveys, instruments, targeting programs, evidence types,
and mass methods. Consequently every catalogue inverse-probability weight is
missing and `pooled_demographic_inference_allowed` is false. Published fractions
or luminosity functions may be discussed only within the source-local scope
named in the registry. This is an executable analysis gate, not an estimate of
unknown completeness.

The strongest current source-local constraints are:

- Scholtz: 42 candidates from a 209-galaxy JADES parent over z=2-10; the atlas
  retains the audited z>=4 subset.
- Skyfire: 73% spectroscopic completeness for the paper's specified CEERS LRD
  phenotype subset.
- Mascia: a 4,145-object DJA parent and a stated broad-Halpha completeness
  threshold, followed by colour and compactness cuts.
- MEOW and SMILES: source-local selection and luminosity-function analyses that
  are not transferable as weights for the heterogeneous atlas union.

Any future demographic analysis must add a validated per-object or per-cell
inclusion model, preserve each source's parent population and footprint, model
overlap between surveys, and pass the registry validation before enabling
weights.
