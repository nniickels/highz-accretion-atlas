# Notebook workflows

`scripts/` contains the public, ordered Jupyter workflows:

1. `00_process_catalogues.ipynb`
2. `01_generate_science.ipynb`
3. `02_generate_figures.ipynb`
4. `03_generate_atlas.ipynb`
5. `04_verify.ipynb`

Run them from top to bottom. Each notebook is a thin, inspectable driver for
tested Python modules under `src/internal/`; catalogue and scientific logic is
kept in `.py` files rather than hidden in notebook state.

Historical exploratory notebooks are not part of the public workflow; their
history remains recoverable from Git.
