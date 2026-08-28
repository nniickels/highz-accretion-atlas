# Script Guide

Run modules from the repository root with the supported Python 3.12 environment:

```bash
.venv/bin/python -m scripts.<module>
```

## Processing

- `process_data.py`: original v1 standardization
- `process_v3_blagn.py` through `process_v6_blagn.py`: frozen BLAGN catalogue layers
- `process_v7_catalogue.py` through `process_v7_5_catalogue.py`: heterogeneous catalogue layers

## Science and figures

- `generate_v2_*`: v2 rankings, uncertainties, and figure prototypes
- `generate_v3_*` through `generate_v6_*`: frozen BLAGN science and figures
- `generate_v7_2_class_aware_science.py`: first frozen class-aware science layer
- `generate_v7_4_growth_products.py`: complete eligible-object growth gallery
- `generate_v7_5_class_aware_science.py` and `generate_v7_5_figures.py`: current products

## Verification and inventories

- `verify_source_provenance.py`: current source registry gate
- `verify_v*_release.py`, `verify_v*_catalogue.py`, and `verify_v*_science.py`:
  release-specific hashes and reproduction
- `verify_v7_5_figures.py` and `verify_v7_5_publication.py`: current visual/publication gates
- `release_verification.py` and `reproduction.py`: shared verification utilities
- `build_results_inventory.py`: deterministic global results index

## Source extraction utilities

`extract_xqr30_arxiv_tables.py` and `extract_shen19_cds_tables.py` preserve
source-specific extraction logic. Raw source files are never silently rewritten
by a later release.

Exact end-to-end commands are maintained in
[`../docs/getting-started.md`](../docs/getting-started.md).

