# Source Package Guide

The `src` package is organized by responsibility and release rather than by
nested packages so established imports and frozen reproduction remain stable.

## Shared foundations

- `models.py`: cosmology and black-hole growth equations
- `scoring.py`: model compatibility and ranking scores
- `standardize_data.py`: original standardization and validation
- `identity.py`: stable object identity and match candidates
- `object_taxonomy.py`: controlled evidence, class, phenotype, and eligibility terms
- `mass_systematics.py`: source-method systematic registry
- `source_provenance.py`: provenance-registry validation

## Catalogue and science releases

- `v3_catalogue.py` through `v6_catalogue.py`: frozen BLAGN catalogue builders
- `v3_science.py` through `v6_science.py`: frozen BLAGN science builders
- `v7_catalogue.py`, `v7_admission.py`, and `v7_batch.py`: generalized v7 framework
- `v7_1_catalogue.py` through `v7_5_catalogue.py`: successive catalogue layers
- `v7_2_science.py` and `v7_5_science.py`: class-aware science layers

## Source-family adapters

- `v7_ren.py`: ALPINE–CRISTAL–JWST candidates
- `v7_xqr30.py`: XQR-30 luminous quasars
- `v7_shen19.py`: GNIRS-50 luminous quasars
- `v7_3_uhz1.py`: UHZ1 evidence history
- `v7_4_scholtz.py`: JADES narrow/high-ionization candidates

Release-numbered modules are intentionally retained. Consolidating them would
make frozen reconstruction less transparent and risks changing historical
behavior.

