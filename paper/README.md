# Manuscript draft

**Conservative manuscript scope:** all six records linked to the three open
identity groups are excluded from manuscript inference. The primary sample has
224 objects; the exploratory numerical sample has 234. Headline threshold
counts and top-five ordering are unchanged in the tested scenarios.
This addresses the analysis dependency, not physical identity resolution or a
final unique-object census. The strict identity gate remains open.

The explicit policy is `identity_exclusions.json`. Reproduce the stored selection
and inclusion/exclusion sensitivity tables with:

```bash
.venv/bin/python -m src.internal.publication_selection --write
.venv/bin/python -m src.internal.publication_selection
```

The second command verifies without rewriting; it is also part of notebook 04.
The six publication-sample figures in `paper/figures/` use the conservative publication
samples. Notebook 02 regenerates them and notebook 04 compares regenerated
pixels (maximum channel difference 3, identical dimensions). The original
full-catalogue figures remain in `results/v3/figures/`.


The `paper/` folder contains the current working manuscript draft and is kept
for reference while the catalogue and analysis continue to evolve.
`highz_accretion_atlas_v3.tex` is the editable LaTeX source. It references the
publication-sample figures in `paper/figures/`.
The manuscript appendix contains the full compatibility grid and its efficiency
prescription. `supplementary_material.tex` contains the illustrative early-start
calculation. Six figures appear in the manuscript and one in the supplement.

```bash
cd paper
SOURCE_DATE_EPOCH=1788393600 pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
SOURCE_DATE_EPOCH=1788393600 pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
SOURCE_DATE_EPOCH=1788393600 pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
```

Tectonic is an equivalent local option when `pdflatex` is unavailable:

```bash
SOURCE_DATE_EPOCH=1788393600 tectonic --keep-logs highz_accretion_atlas_v3.tex
SOURCE_DATE_EPOCH=1788393600 tectonic --keep-logs supplementary_material.tex
```

The compiled files are `highz_accretion_atlas_v3.pdf` and
`supplementary_material.pdf`. With pdflatex, also run the three passes above
for `supplementary_material.tex`. LaTeX intermediate files
are ignored. The fixed epoch is 2026-09-03 00:00:00 UTC and makes repeat builds
with the same compiler byte-reproducible.

## Bibliography

The bibliography follows the [AAS reference instructions](https://journals.aas.org/references/):
author–year citations with initials, alphabetical references, all authors for
papers with up to five authors, and the first three plus *et al.* otherwise.
Article titles remain in `references.bib` but are hidden in the default short
bibliography. Journal metadata and preprint versions were checked on 2026-09-10
against publisher-deposited Crossref records and arXiv; each BibTeX entry records
its metadata source. Stable citation keys can differ from publication years.
Updating a reference does not change the versioned measurements used in the analysis.

To regenerate the embedded bibliography after editing `references.bib`, run:

```bash
.venv/bin/python -m src.internal.update_bibliography
```

This uses Tectonic and the [official AAS v7.1 style](https://journals.aas.org/wp-content/uploads/2026/06/aasjournalv7.1.bst).
The vendored style has one documented correction: clear the suffix state before
its reverse pass to prevent an isolated reference receiving an orphan `a` suffix.
The generated bibliography is embedded in each `.tex` for portability;
normal manuscript builds do not require BibTeX or an Overleaf recompile to sync edits.

The supplement's comparison of growth starting at redshifts 30 and 3400 is
reproduced with `.venv/bin/python -m src.internal.check_early_start`. It uses the
existing matter-plus-Lambda age relation and explicitly treats the high-redshift
extension as an extrapolation, without changing any catalogue inference.
Regenerate the corresponding supplementary figure with
`.venv/bin/python -m src.internal.plot_early_start`. The generated
`figures/early_start_comparison.pdf` is pre-rendered with Matplotlib and the
same serif font family as the other paper figures. Its coordinates come directly
from `src.models`; both panels use matched masses, rates and efficiencies.
All seven figures are embedded as vector PDFs, so normal manuscript builds
require neither PGFPlots nor plot rendering. PNG exports remain for previews
and pixel-based reproduction checks. PDF timestamps are omitted for deterministic
exports. The reproduction gate compares decoded PDF object graphs exactly,
including drawing commands, fonts, image samples and page geometry; compression
and object numbering may differ between rendering environments.

The [scientific/editorial pass record](scientific-editorial-review.md) lists
checked claims, corrections, and remaining submission work.

## Scientific revision following manuscript assessment

The revised draft foregrounds the twelve primary reference-threshold objects,
source-specific estimator caveats and proposed observations. Generated LaTeX
fragments under `analysis/` keep manuscript tables synchronized with the numerical
outputs. The four-object Dayal input comparison and A2744-QSO1 dynamical-mass
comparison are external manuscript analyses; neither admits a new canonical
measurement nor changes frozen v3 membership. Inputs and locators are in
`review_inputs.json`. The direct estimate places A2744-QSO1 near unity with
an interval crossing the threshold, rather than securely below it.

The reference catalogue is identified by Git commit
`a40a0d28c6c8d0b7e0c98aea089629903c34f7be`; this manuscript revision is recorded
by its own Git commit. No archival DOI has been assigned. Journal formatting,
affiliation, acknowledgements and archival deposition remain submission tasks.

Notebook 03 compares the generated manuscript CSVs, LaTeX fragments and six
figures against the independent baseline before refreshing dataset manifests.
Notebook 04 additionally checks internal consistency. CI deletes generated
products in its disposable workspace before reproduction and compiles this
manuscript from the regenerated inputs, not the baseline checkout.

## Supporting documentation

- [Catalogue navigation score](../docs/guides/catalogue-navigation-score.md)
- [Catalogue admission and measurement decisions](../docs/source-notes/manuscript-catalogue-bookkeeping.md)

These details accompany the release; the manuscript retains the source inventory,
sample counts and unresolved identity exclusions.
