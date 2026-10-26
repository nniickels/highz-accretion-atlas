# Notebook workflows

Run these notebooks in numerical order after [setup](../README.md#getting-started):

| Notebook | Purpose |
| --- | --- |
| `00_process_catalogues.ipynb` | Build the v1–v3 catalogues and identity tables. |
| `01_generate_science.ipynb` | Calculate growth requirements, uncertainties, publication tables, and the four extended v3 tables. |
| `02_generate_figures.ipynb` | Generate catalogue and manuscript figures. |
| `03_generate_atlas.ipynb` | Generate object maps and compare outputs with the independent baseline. |
| `04_verify.ipynb` | Verify data, sample membership, numerical results, and figures. |

The notebooks call Python modules in `src/internal/`; they contain no separate
implementation of the scientific calculations. Follow the
[reproduction guide](../docs/guides/reproducibility.md) to run the committed
revision in a separate workspace with `HIGHZ_BASELINE_ROOT` set to an unchanged
baseline.

The [v3 result guide](../docs/reference/catalogue-results.md) lists the compact
object summary, assumption comparisons, field availability, and minimum seeds.

Publication samples use the [evidence and identity rules](../data/publication/README.md).
Their figures remain separate from the full-catalogue figures. Manuscript editing,
LaTeX compilation, and upload packaging are outside the notebook workflow.
Draft manuscripts: Coming soon.

## Optional v4 analysis

`05_pbh_growth_v4.ipynb` runs the four-target primordial black-hole growth
comparison after its v3 inputs are available. It writes `results/v4/`, updates
the results inventory, and verifies the generated tables and figures.
It is separate from the 00–04 loop and does not rebuild manuscripts or posters.
See [v4 outputs and commands](../results/v4/README.md).
