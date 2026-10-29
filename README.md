# High-Redshift Black Holes: Catalogue and Growth Constraints

A standardized, assumption-tracked catalogue of JWST-identified high-redshift
($z \ge 4$) black holes and black-hole candidates, with analyses of their growth
requirements under different seed masses, growth onset times, and radiative
efficiencies.

**Draft manuscripts:** [Ap&SS PDF](paper/apss/main.pdf),
[general draft PDF](paper/early_giants_draft.pdf), and
[general draft source ZIP](paper/early_giants_overleaf.zip).

**Posters:** [Portrait PDF](posters/36x48.pdf) ([PowerPoint](posters/36x48.pptx)) and
[landscape PDF](posters/48x36.pdf) ([PowerPoint](posters/48x36.pptx)).

## Catalogue and key results

| Find | Link |
| --- | --- |
| Compact object results, sample flags, and growth requirements | [v3 object results CSV](results/v3/tables/v3_object_results.csv) |
| Full adopted measurements and coordinates, including provisional objects | [Object catalogue CSV](data/processed/v3/v3_accreting_objects.csv) |
| All v3 measurements, including alternatives | [Measurement catalogue CSV](data/processed/v3/v3_accreting_measurements.csv) |
| Required growth rates at adopted central masses | [v3 object ranking CSV](results/v3/tables/v3_object_point_ranking.csv) |
| Growth requirements with reported mass errors | [v3 uncertainty ranking CSV](results/v3/tables/v3_object_uncertainty_ranking.csv) |
| Highest-ranked primary-sample objects and mass-estimator caveats | [Target comparison CSV](results/v3/selected_samples/tables/target_robustness.csv) |
| Primary and expanded sample figures | [Scientific figures](results/v3/selected_samples/figures/) |

See [data guidance](data/README.md) for identifiers, units, and catalogue limits,
and [sample results](results/v3/selected_samples/README.md) for sample definitions
and sensitivity tests.

Start with the compact results table. Select `publication_primary_flag=True`
for the reviewed primary sample or `publication_exploratory_flag=True` for the
expanded sample; both exclude unresolved identities. All 343 archival records
remain available in the full tables.

## Repository guide

- [Data](data/README.md): catalogue tables, source records, identities, and validation.
- [Results](results/README.md): growth calculations, figures, and object maps.
- [Documentation](docs/README.md): methods, assumptions, and source audits.
- [Source code](src/README.md): model and processing modules.
- [Notebooks](scripts/README.md): ordered analysis workflows.
- [Tests](tests/README.md): regression checks and continuous integration (CI).

## Dataset versions

An active galactic nucleus (AGN) is identified by evidence of black-hole
accretion. The broad-line samples use masses estimated from broad emission lines.
v1–v3 are nested catalogue versions; v4 is a separate analysis of four v3 targets.

| Version | Scope | Measurements | Object records | Host systems |
| --- | --- | ---: | ---: | ---: |
| v1 | Original Juodzbalis et al. JADES broad-line AGN sample | 23 | 23 | 23 |
| v2 | v1 plus comparable JWST broad-line AGN measurements | 222 | 215 | 214 |
| v3 | v2 plus systems with other evidence or mass methods | 355 | 343 | 342 |
| v4 | Earlier-onset growth tests using the unchanged v3 catalogue | 355 | 343 | 342 |

The v3 object count is provisional: three identity groups remain unresolved.
The [v4 analysis](docs/reference/pbh-growth-v4.md) tests growth from assumed
seeds, including primordial black-hole scenarios. It does not model seed
formation or population abundance.

## Getting started

Use Python 3.12 and a complete checkout; the Python package does not include
the data or results. Install the pinned Linux/macOS environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --requirement requirements/notebook.txt
.venv/bin/python -m pip check
```

Use `requirements/core.txt` instead if Jupyter is not needed.
Run notebooks 00–04 in [scripts/](scripts/README.md) in numerical order.
Their calculations are implemented in Python modules, so individual notebook
cells do not need to be retained between runs.

Follow [Reproducing results](docs/guides/reproducibility.md) for the complete
procedure, including separate baseline and execution copies, verification
commands, poster checks, and the optional v4 analysis. Review and commit intended
changes before reproducing a revision: `git archive HEAD` excludes uncommitted files.

## Sources and limits

The [source bibliography](data/sources.md) records publications and extraction
limits. [Sample rules](data/publication/README.md) select the primary and expanded
samples; [sample results](results/v3/selected_samples/README.md) contain their
tables and figures. The catalogue workflow does not require LaTeX or local
manuscript sources.

Independent checks cover all 248 numerical mass measurements and both error
bounds, all central redshifts, and all available coordinate pairs. Other fields
have partial coverage. See [validation coverage](data/validation/README.md) and
the [identity audit](docs/source-notes/redshift-identity-audit.md).

Reproducing stored results does not validate every mass estimator or make the
sample statistically complete. Growth requirements depend on the adopted
measurements and assumptions; sample counts do not establish population fractions.
See the [scientific limits](docs/reference/science-policy.md).
