# highz-accretion-atlas
A standardized, assumption-tracked catalogue of JWST-identified high-redshift
($z \ge 4$) accreting massive-black-hole systems and candidates, and their
possible formation and growth scenarios.

## Background
The James Webb Space Telescope pushes observational cosmology into the first few billion years of cosmic history, and it has revealed massive accreting objects that are hard to explain due to the limited time for them to grow. It follows that one of the biggest questions cosmologists are asking right now is: “How did these objects get so big, so fast?” My research project aims to contribute to this question by creating a standardized cross-paper catalogue of these objects and then testing what scenarios could have theoretically formed each one. Either they started from a sufficiently massive seed, accreted continuously for a long enough time, formed very early, or some combination of these conditions. This is explored and visualized with parameter-space maps and growth tracks based on the analytic black hole growth equation used in [Dayal (2024)](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html).

Across the literature, key quantities are often inferred with different methods and assumptions, even though small shifts in inferred quantities like `M_BH`, `M_*`, or `L_bol` can imply very different growth histories. A standardized, assumption-tracked catalogue would clarify which objects are genuinely challenging for standard formation models rather than artifacts of inference choices.

Overall, this project aims to help determine what objects are the best candidates for follow-up and deeper theory work.

## Theory 
The growth model follows Eq. 1 of [Dayal (2024)](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html):

$M_{BH}(t) = M_{seed}(t_{seed})e^{\frac{4\pi Gm_p f_{Edd}}{c\sigma_T}\frac{1-\epsilon}{\epsilon}(t-t_{seed})}$

The optional merger-assisted case multiplies this smooth-accretion result by
$B_{\rm merge}$. Thus $B_{\rm merge}=2$ adds a fixed
$\log_{10}(2)=0.301$ dex to the predicted mass; it does not double
$f_{\rm Edd}$ or the exponential growth rate. For ideal Kerr thin disks, the
spin cases $a=-1,0,+1$ correspond to $\epsilon=0.038,0.057,0.423$
(rounded), respectively.

The spin-separated $f_{Edd}$-mass maps additionally show an illustrative slim-disk
coupling above Eddington. They retain the spin-dependent thin-disk efficiency
for $f_{Edd}\leq1$ and use
$\epsilon_{\rm eff}=\epsilon_{\rm spin}f_{Edd}/e^{f_{Edd}-1}$ for
$f_{Edd}>1$, representing the decline in effective radiative efficiency from
photon trapping. The growth-track figure continues to show constant-efficiency
reference curves.

Cosmic time in Gyr, derived from the FLRW form with flat $\Lambda$ CDM: 

$t(z) = \frac{2}{3H_0\sqrt{\Omega_{\Lambda}}}{\sinh^{-1}}(\frac{\sqrt{\Omega_{\Lambda}/{\Omega_m}}}{(1+z)^{3/2}})$

All catalogue ages, growth intervals, tables, and figures use a flat Planck
2018-style cosmology with $H_0=67.3\,{\rm km\,s^{-1}\,Mpc^{-1}}$,
$\Omega_m=0.315$, and $\Omega_\Lambda=0.685$.

For each object, the pipeline computes the cosmic time available between $z_{seed}$ and the observed redshift. It then explores a grid of:

- ${M_{seed}}$
- $f_{Edd}$
- $z_{seed}$
- radiative efficiency $\epsilon$



## Manuscript and Paper Products

The complete first manuscript draft is available as
[`paper/highz_accretion_atlas_v3.pdf`](paper/highz_accretion_atlas_v3.pdf),
with its editable LaTeX source beside it. It reflects the frozen 340-object v3
catalogue and the current canonical results.

Main-text products:

- catalogue overview in redshift-mass space — `results/v3/figures/v3_catalogue_growth_landscape.png`
- object ranking by growth pressure — `results/v3/tables/v3_object_point_ranking.csv` and `results/v3/figures/v3_class_aware_growth_pressure.png`
- required $f_{Edd}$ summaries for fixed seed masses — `results/v3/tables/v3_required_fedd_by_seed_mass.csv`
- required seed-mass summaries for fixed accretion histories — `results/v3/tables/v3_required_mseed_by_growth_assumption.csv`
- compatibility heatmap across seed/growth assumptions — `results/v3/figures/v3_compatibility_summary.png` and `results/v3/tables/v3_all_object_compatibility.csv`
- uncertainty and systematics robustness plots — `results/v3/figures/v3_uncertainty_robustness.png`, its presentation-ready top-five crop `results/v3/figures/v3_uncertainty_robustness_top5.png`, `results/v3/figures/v3_monte_carlo_summary.png`, and `results/v3/figures/v3_measurement_sensitivity.png`
- selected object-level $f_{Edd}$-mass maps — `results/v3/parameter_maps/fedd_mass_maps/`
- follow-up priority table or matrix — `results/v3/tables/v3_followup_priority.csv`

Appendix or supplement products:

- full catalogue schema — `docs/reference/admission-schema.md`
- full source registry — `data/source_family_registry.csv`, `data/source_provenance_registry.csv`, and `data/mass_method_registry.csv`
- full processed catalogue tables — `data/processed/v3/` with identity products in `data/crossmatch/v3/`
- full result tables — `results/v3/tables/`
- full per-object $f_{Edd}$-mass map gallery — `results/v3/parameter_maps/fedd_mass_maps/`
- full seed-redshift-mass map gallery — `results/v3/parameter_maps/seedredshift_mass_maps/`
- comprehensive v3 growth-track grid preserving all historical v1 line
  combinations — `results/v3/figures/v3_all_object_growth_tracks_full_assumptions.png`
- validation checks — `results/v3/tables/v3_exclusion_audit.csv`, `results/v3/tables/v3_all_object_visual_coverage.csv`, and `results/v3/tables/v3_science_policy.csv`; executable gate in `scripts/04_verify.ipynb`
- sensitivity tests — `results/v3/tables/v3_alternate_measurement_sensitivity.csv` and `results/v3/figures/v3_measurement_sensitivity.png`
- source-by-source caveats — `results/v3/tables/v3_source_caveat_summary.csv`
- source-level selection/completeness audit — `data/selection_function_registry.csv` and `results/v3/tables/v3_selection_completeness_summary.csv`
- immutable extraction audit — `data/manual_extraction_audit.csv`

The canonical v3 gallery covers all 340 objects with one $f_{Edd}$-mass map in
`results/v3/parameter_maps/fedd_mass_maps/` and one seed-redshift-mass map in
`results/v3/parameter_maps/seedredshift_mass_maps/`. The 237
growth-eligible objects receive numerical panels; the other 103 receive explicit
no-inference status panels. Growth tracks are retained only as combined
catalogue-wide figures under `results/v3/figures/`; the full-assumption v3
companion contains 72 curves spanning three seed masses, three $f_{Edd}$
values, four efficiencies, and two merger boosts. Seed mass is encoded by
color, $f_{Edd}$ by line style, efficiency by line width, and merger boost by
opacity. Catalogue-wide compatibility and Monte
Carlo atlases retain every object label, while class-specific summaries avoid
reporting a heterogeneous pooled demographic fraction. Start with
`results/README.md` or the version manifests under `releases/`.

The main text should showcase the atlas logic and strongest rankings, while
the appendix preserves the comprehensive technical and visual record. This
keeps the project centered on observational triage rather than on claiming that
any single seed or accretion channel is proven.

## Workflow

Dataset versions describe nested scientific datasets, not software releases or
chronological development checkpoints. Every version uses the same latest
applicable corrections, identity rules, cosmology, growth model, uncertainty
propagation, comparison policy, and visual grammar.

| Version | Dataset | Measurements | Objects | Hosts |
| --- | --- | ---: | ---: | ---: |
| v1 | Original Juodzbalis et al. JADES BLAGN catalogue | 23 | 23 | 23 |
| v2 | v1 plus comparable JWST BLAGN sources with canonical masses | 218 | 211 | 210 |
| v3 | v2 plus heterogeneous JWST-identified candidates | 350 | 340 | 339 |

For each version, canonical catalogues are under
`data/processed/<version>/`, identity products are under
`data/crossmatch/<version>/`, and science tables, figures, and per-object
galleries are under `results/<version>/`. Source-specific raw files retain
descriptive publication names because they are immutable extractions.

Run the numbered notebooks in `scripts/` from top to bottom. They call tested
Python modules under `src/internal/`; scientific implementation does not live
only in notebook state. To execute the complete workflow non-interactively:

```bash
mkdir -p /tmp/highz-atlas-notebooks
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/00_process_catalogues.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/01_generate_science.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/02_generate_figures.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/03_generate_atlas.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/04_verify.ipynb
```

Only the historical source-admission builders required for exact reconstruction
remain under `src/internal/compatibility/`; they do not define public dataset
versions or write legacy output trees.

## Getting Started

The project requires Python 3.12. Create a repository-local virtual environment
and install the pinned project requirements:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-notebook-lock.txt
```

Run the complete regression and verification suite:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
.venv/bin/python -m src.internal.verify_manual_extractions
.venv/bin/python -m src.internal.verify_primary_source_values
.venv/bin/python -m src.internal.verify_source_provenance
.venv/bin/python -m src.internal.verify_versions
```

Full dataset generation commands are listed in the workflow above. The source
review cutoff and explicit admission boundary are documented in
`docs/reference/literature-scope.md`; versioning details are in
`docs/guides/versioning.md`.

## Repository map

Folder-level guides keep the data, results, documentation, releases, and code
easy to navigate:

- [`data/`](data/README.md): raw sources, processed catalogues, and identity products
- [`results/`](results/README.md): science tables, figures, galleries, and inventory
- [`docs/`](docs/README.md): contracts, methods, guides, and source notes
- [`releases/`](releases/README.md): exact dataset manifests and hashes
- [`src/`](src/README.md), [`scripts/`](scripts/README.md), and [`tests/`](tests/README.md): implementation, commands, and validation

## References

Catalogue data sources are documented authoritatively in `data/sources.md`.
The following is background and prospective reading, not a list of sources
currently represented by catalogue rows:

1. Dayal, P. 2024, [A&A](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html), 690, A182
2. Ji, X., Maiolino, R., Übler, H., et al. 2025, [MNRAS, 544, 3900](https://doi.org/10.1093/mnras/staf1867)
3. Maiolino, R., Übler, H., D’Eugenio, F., et al. 2025, [arXiv:2505.22567](https://arxiv.org/abs/2505.22567) 
4. Dayal, P. & Maiolino, R. 2025, [arXiv:2506.08116](https://doi.org/10.48550/arXiv.2506.08116)
5. Prole, L. R., Regan, J. A., Mehta, D., et al. 2025, [arXiv:2506.11233](https://arxiv.org/abs/2506.11233)
6. Adamo, A., Atek, Hakim., Bagley, M., et al. 2025, [arXiv:2405.21054](https://arxiv.org/abs/2405.21054)
7. Dayal, P. & Ferrara, A. 2018, [arXiv:1809.09136](https://arxiv.org/abs/1809.09136)
8. Stark, D., Topping, M., Endsley, R., et al. 2025, [arXiv:2501.17078](https://arxiv.org/abs/2501.17078)

Reproduction compares regenerated CSV values and PNG pixels with an independent
baseline before refreshing hashes; see [reproduction and intentional updates](docs/guides/reproducibility.md).
Independent source fixtures cover all 32 families with 2,041 field checks;
all 244 numerical masses and both error bounds are independently checked.
Other observable fields retain representative coverage.
