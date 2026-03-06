# highz-accretion-atlas
The goal of this project is to build a standardized catalogue of JWST-identified accretion candidates at z ≥ 4 that tracks how quantities were inferred and under which assumptions. Using this catalogue, a Python pipeline:  
1. Recomputes key derived quantities (e.g. `M_BH/M_*`) and applies a set of physically motivated interpretation variants (e.g. orientation/beaming on luminosity, non-virial broad-line broadening affecting `M_BH`, AGN contamination affecting `M_*`) 
2. Tests each object against a menu of seed + growth scenarios (e.g. Pop III/light seeds, cluster/intermediate seeds, heavy/DCBH seeds, PBH-like primordial seeds; with Eddington-limited, supercritical/slim-disk-like, merger-assisted, and spin/efficiency-varied growth) by solving for the required seed mass or average accretion intensity given the cosmic time available
3. Summarizes results as per-object requirement tables, robustness bands, and a transparent feasibility score across models, highlighting which objects remain peculiar under reasonable assumption changes

This is helpful because current high-z AGN/BH literature mixes methods and conventions. A reproducible dataset with explicit assumptions and robustness checks makes it clearer which objects are genuinely challenging for standard formation models versus artifacts of inference choices, and helps prioritize the best candidates for follow-up and deeper theory work.

## Background
JWST pushes sensitive spectroscopy and imaging into the first few billion years of cosmic history, where there is not much time for black holes and galaxies to assemble. That makes many z ≥ 4 discoveries natural stress tests. Small shifts in inferred `M_BH`, `M_*`, or `L_bol` can imply very different growth histories, especially since many calibrations were developed at low redshift.

However, key quantities are often inferred with different methods and assumptions across papers, which can move objects in or out of the “peculiar” regime. This project’s motivation is to create a standardized assumption-tracked catalogue so it’s clearer which objects remain genuinely challenging under reasonable alternative interpretations, and therefore best motivate additional formation/growth channels and follow-up observations. 

Testing multiple seed + growth scenarios matters because different origins imply different requirements to reach the observed state by a given redshift. Light seeds may demand extreme accretion histories while heavy seeds reduce that burden but can require special environments. More theoretical ideas like PBH seeding represent a fundamentally earlier “head start.” Studying these earliest accreting systems helps pin down how the first structures formed and grew, refining our picture of cosmic history and testing the physics that underpins modern cosmology.

**JWST surveys (common sources of z ≥ 4 discoveries):** JADES, CEERS, UNCOVER

For the full list of implemented formation, growth, and interpretation models, see `docs/model-menu.md`.

## Workflow
**Phase 1 (CURRENT STAGE): Start with a small dataset** 
- Extract raw data (only from 1 paper) into `data/raw/v1_raw.csv`
- Write data standardizing pipeline into `src/standardize_data.ipynb`
- Standardize into `data/processed/v1_processed.csv` (units, log conventions, derived `M_BH/M_*`, consistent method tags) 

**Phase 2: Implement core pipeline**
- In `src/models.ipynb`, write
 - Interpretation variants (MBH systematics, host `M_*` contamination; `L_bol` scaling if used)
 - Seed + growth feasibility solver (required seed mass or required average accretion intensity)
- Build scoring system in `src/scoring.ipynb` 

**Phase 3: Results**
- Run and generate core plots, saving to `results`: requirement tables, model score tables, and core plots (e.g., `M_BH/M_*` vs z, required average `f_Edd` vs z, feasibility heatmap)

***Call everything up until this point `v1`.***

**Phase 4: Increase dataset (same object class) and repeat**
- Scale by adding additional sources (more papers, same object class) and reconcile duplicates via coordinates + redshift
- Track cross-paper differences explicitly (multiple measurements per object) and propagate them through the same pipeline
- Update outputs to include cross-survey comparisons and “most assumption-sensitive” vs “robust outlier” rankings

**Phase 5: Increase dataset (all object classes) and repeat**
- Scale to more accretion candidates and inferred properties. Add additional object classes: narrow-line AGN, LRDs/compact red AGN candidates, X-ray selected candidates (where available)
- Add discrete interpretation branches where needed (e.g., LRD stellar-break vs non-stellar break affecting `M_*`)
- Add metallicity and ISM diagnostics for the subset with suitable lines and clearly documented calibrations
- Extend scoring to include environment/rarity priors (e.g., DCBH-like special conditions) where relevant

