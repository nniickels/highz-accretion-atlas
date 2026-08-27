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

The spin-separated parameter maps additionally show an illustrative slim-disk
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



## Intended Paper Products

Main-text products:

- catalogue overview in redshift-mass space
- object ranking by growth pressure
- required $f_{Edd}$ summaries for fixed seed masses
- required seed-mass summaries for fixed accretion histories
- compatibility heatmap across seed/growth assumptions
- uncertainty and systematics robustness plots
- selected object-level parameter maps
- follow-up priority table or matrix

Appendix or supplement products:

- full catalogue schema
- full source registry
- full processed catalogue tables
- full result tables
- full per-object parameter-map gallery
- full seed-redshift map gallery
- validation checks
- sensitivity tests
- source-by-source caveats

The complete per-object map collections are also available as seven lossless
high-resolution grids under `results/compiled_object_grids/`: six fixed
spin/merger parameter-space cases and one seed-redshift compilation. Each grid
is 6048 by 5648 pixels at 300 dpi and contains all 23 v1 objects. Start with
`results/README.md` or the machine-readable `results/results_inventory.csv` to
navigate the full results tree without moving immutable release artifacts.

The main text should showcase the atlas logic and strongest rankings, while
the appendix preserves the comprehensive technical and visual record. This
keeps the project centered on observational triage rather than on claiming that
any single seed or accretion channel is proven.

## Workflow

Project release numbers describe reproducible catalogue/science milestones, not
paper versions. The current catalogue layer is **v7.4**, the current science
layer is **v7.2**, and v5 remains the deliberate paper-figure release. v7.4
adds the JADES narrow-line/high-ionization family without changing frozen v7.2
science products:

| Release | Meaning | Canonical products |
| --- | --- | --- |
| v1 | Original 23-row JADES BLAGN catalogue and baseline evaluation | `v1_raw.csv`, `v1_processed.csv`, `v1_evaluation_*` |
| v2 | Ranking, uncertainty propagation, and figure prototypes evaluated on the frozen v1 catalogue | `v2_object_ranking_table.csv`, `v2_uncertainty_*`, `v2_main_text_*` |
| v3 | Combined JADES + Taylor CEERS/RUBIES BLAGN catalogue and measurement/object science workflow | `v3_blagn_*` |
| v4 | Generalized identity, Matthee EIGER/FRESCO and Lin ASPIRE BLAGN, corrected confidence semantics, duplicate sensitivity, and final figures | `v4_blagn_*`, `v4_main_text_*` |
| v5 | Harikane NIRSpec BLAGN measurement layer, class-aware taxonomy, and two-state accretion-history diagnostics | `v5_blagn_*` |
| v6 | Davis/THRILS same-class BLAGN consolidation and source-specific virial sensitivity | `v6_blagn_*` |
| v7.0 catalogue | Frozen v6 plus admitted Ren ALPINE--CRISTAL candidate nuclei and explicit host systems | `v7_accreting_*`, `v7_host_systems.csv` |
| v7.1 catalogue | Frozen v7.0 plus all 42 E-XQR-30 luminous quasars as a separate comparison stratum | `v7_1_accreting_*`, `v7_1_host_systems.csv` |
| v7.2 catalogue | Frozen v7.1 plus all 50 Shen et al. GNIRS quasars, including six reviewed XQR repeats | `v7_2_accreting_*`, `v7_2_host_systems.csv` |
| v7.2 science | Class-aware growth-pressure rankings on frozen v7.2 with separate mass-method strata and uncertainty boundaries | `v7_2_class_aware_*` |
| v7.3 catalogue | Frozen v7.2 plus the original and reanalysed UHZ1 X-ray evidence versions as one disputed physical object | `v7_3_accreting_*`, `v7_3_host_systems.csv` |
| v7.4 catalogue | Frozen v7.3 plus all 20 tabulated Scholtz et al. candidates at z >= 4, including one reviewed JADES 8083 repeat | `v7_4_accreting_*`, `v7_4_host_systems.csv` |

Source-specific raw files retain descriptive names because they are immutable
paper extractions, while `source_paper_version` records the publication/arXiv
version independently. See `docs/release-versioning.md` for the full mapping.
The shared pinned v4.0.1--v7.4 core environment is in `requirements-lock.txt`; verify
every frozen v4 CSV without writing outputs with
`python -m scripts.verify_v4_release --reproduce`. The frozen v5 catalogue and
science tables have an equivalent non-writing gate:
`python -m scripts.verify_v5_release --reproduce`.
The v6 catalogue and science tables add the corresponding gate:
`python -m scripts.verify_v6_release --reproduce`. The frozen catalogue-only
v7.0 layer is checked by `python -m scripts.verify_v7_catalogue --reproduce`.
The frozen v7.1 layer is checked independently by
`python -m scripts.verify_v7_1_catalogue --reproduce`; frozen v7.2 is checked by
`python -m scripts.verify_v7_2_catalogue --reproduce`; the class-aware science
layer is checked by `python -m scripts.verify_v7_2_science --reproduce`.
Frozen v7.3 is checked by `python -m scripts.verify_v7_3_catalogue --reproduce`;
current v7.4 is checked by `python -m scripts.verify_v7_4_catalogue --reproduce`.

All release gates verify exact artifact membership and checked-in bytes against
SHA-256 manifests.
Independent reconstruction is then compared with exact schema, row order,
text, booleans, and missingness plus a tight floating-point tolerance, avoiding
false failures from final-bit differences between macOS/ARM and Linux/x86.
### v1: Pilot Broad-Line AGN Atlas

Start with one clean object class from one source paper.

1. Ingest the JADES broad-line AGN catalogue into `data/raw/v1_raw.csv`.
2. Standardize it into `data/processed/v1_processed.csv`.
3. Validate schema, required values, missing fields, methods, and provenance.
4. Compute cosmic ages and growth intervals.
5. Implement baseline growth diagnostics:
   - predicted black-hole mass
   - required average $f_{Edd}$
   - required seed mass
   - seed-redshift dependence
6. Produce first v1 outputs:
   - $M_{BH}$ vs redshift growth tracks
   - per-object seed/accretion maps
   - required $f_{Edd}$ tables
   - required seed-mass tables
   - sample compatibility summaries

### v2: Ranking, Uncertainty, and Figure Prototypes

Turn the pilot catalogue into an observational triage tool.

1. Define ranking metrics:
   - required $f_{Edd}$ for fixed seed masses
   - required seed mass for fixed accretion histories
   - $M_{BH}/M_*$ tension
   - robustness to black-hole mass shifts
   - object quality and method caveats
   - follow-up priority
2. Generate ranked object tables.
3. Add uncertainty propagation using reported errors.
4. Add systematic mass-shift tests, such as $M_{BH}\pm0.3$ dex.
5. Report percentile ranges and threshold probabilities instead of only point estimates.
6. Create final-style figure prototypes and maintain a living final-paper draft.

### v3: Expanded Broad-Line AGN Atlas

Add more broad-line AGN catalogues while keeping the object class relatively consistent.

1. Add source-specific raw files or ingestion scripts. The first expansion is
   Taylor CEERS/RUBIES in `data/raw/taylor24_ceers_rubies_blagn_table1.csv`.
2. Preserve source-paper measurements rather than overwriting them. Expanded
   products are separate from all v1 and v2 raw, processed, result, and figure files.
3. Track duplicate objects using coordinates, aliases, and redshift. The
   v3 release already uses stable physical-object IDs and retains both
   CEERS-2782 and RUBIES-EGS-50052 measurements.
4. Compare how different papers move objects through growth-parameter space.
5. Recompute rankings and uncertainty-aware diagnostics. Measurement- and
   physical-object-level expanded products now live under
   `results/v3_blagn_*.csv` and are documented in
   `docs/v3-blagn-science-workflow.md`.
6. Update final-style figures and tables. The frozen v3 catalogue now has its own
   final-style overview and ranking figures under `results/v3_main_text_figures/`.

### v4: Measurement Versioning and Same-Class Expansion

This completed release generalizes the physical-object/literature-measurement
split introduced by the Taylor expansion. It contains 96 measurements and 94
physical objects.

1. Extend stable physical object IDs across further overlapping sources.
2. Keep `measurement_id` as the row-level source-paper measurement ID.
3. Add aliases and cross-match metadata.
4. Build measurement-level and object-level ranking tables.
5. Preserve explicit default-measurement rules. One-at-a-time
   alternate-measurement rank sensitivity is complete for every nondefault row.
6. Add the Matthee EIGER/FRESCO and Lin ASPIRE broad-Halpha samples without
   changing v1--v3 artifacts or pooling their unlike selection functions.

### v5: Harikane Measurement Version and Taxonomy Foundation

This completed release adds all ten Harikane et al. broad-Halpha measurements,
links five to existing physical objects, creates five new physical objects, and
retains every prior default measurement. The result is 106 measurements / 99
physical objects. It also separates evidence status, spectroscopic type,
selection channel, phenotype, lensing status, and growth-ranking eligibility.

### v5 science extension: Accretion-History Diagnostics

This completed, non-catalogue-bumping layer moves beyond constant-average
growth tracks while leaving v1--v4 products unchanged.

1. It compares reported current $f_{Edd}$ with required lifetime-average
   $f_{Edd}$ without treating them as the same quantity.
2. It evaluates effective two-state histories with zero quiescent accretion and
   burst $f_{Edd}=1,2,3$.
3. It computes required duty-cycle point estimates and asymmetric-error Monte
   Carlo intervals for a $100\,M_\odot$ seed under the baseline assumptions.
4. It retains duty cycles above one as an explicit sign that the fixed burst
   scenario is insufficient; it does not clip them into apparent feasibility.
5. It retains source-inconsistent reported values for audit but excludes them
   from current-versus-lifetime ratio comparisons.

### v6: Final Same-Class BLAGN Consolidation

This completed release adds the full seven-row Davis/THRILS Appendix Table 5,
retains the one `z<4` repeat in raw storage, and adds six new `z>=4` physical
objects. The combined release has 112 measurements / 105 objects. It preserves
all v5 defaults and artifacts, adds a separately labelled THRILS `+/-0.5 dex`
virial-calibration sensitivity, and leaves unreported LRD, host, luminosity,
Eddington-ratio, and FWHM values blank.

### v7: Multi-Class High-z Accreting BH Atlas

The source-independent admission schema and validator are implemented in
`src/v7_admission.py` under
`docs/multiclass-eligibility-and-mass-comparability.md`. The catalogue-only v7
layer now copies frozen v6 through the explicit vocabulary adapter and appends
the authoritative Ren et al. ALPINE--CRISTAL--JWST Tables 1--2 admission. It has
119 measurements, 112 physical objects, and 111 host systems. All seven Ren
nuclei remain available in the exploratory tier; only `DC_536534` enters the
primary tier. See `docs/v7-catalogue-schema.md`.

Evidence classes and comparison groups tracked by the schema include:

- X-ray-selected high-z black-hole candidates
- high-ionization-line candidates
- narrow-line AGN candidates
- photometric AGN candidates
- luminous high-redshift quasars as comparison anchors

LRD/compact/red designations are phenotypes, and lensing is a separate
measurement property; neither is an accretion-evidence class.

For each class:

1. Validate required metadata and measurement/object/host-system identity.
2. Track mass method and selection caveats.
3. Keep object classes visually and statistically distinct.
4. Recompute atlas rankings with class-aware caveats.

Catalogue-only v7.2 reproduction:

```powershell
python -m scripts.process_v7_2_catalogue
python -m scripts.verify_v7_2_catalogue --reproduce
```

Class-aware science reproduction:

```powershell
python -m scripts.generate_v7_2_class_aware_science --n-samples 10000 --seed 20260808
python -m scripts.verify_v7_2_science --reproduce
```

The science release ranks the 209 eligible measurements and 196 eligible
preferred objects within explicit object-class and mass-comparability scopes.
Its global rank is labelled for navigation only, and its policy product forbids
pooled demographic inference. See `docs/v7.2-class-aware-science-workflow.md`.

Future additions are assembled in coherent source-family batches through
`src/v7_batch.py`; see `docs/v7-source-family-batches.md`. XQR-30 and GNIRS-50
are separately provenance-tracked luminous-quasar batches and are not pooled
with the faint JWST populations.

Catalogue-only v7.3 reproduction:

```powershell
python -m scripts.process_v7_3_catalogue
python -m scripts.verify_v7_3_catalogue --reproduce
```

The UHZ1 addition retains the original candidate X-ray interpretation and the
preferred disputed reanalysis as two versions of one object. It preserves the
published assumption-dependent mass range as bounds, not a canonical point
mass, so the v7.3 growth-eligible population is unchanged. See
`docs/uhz1-xray-evidence-history-extraction-notes.md`.

Catalogue-only v7.4 reproduction:

```powershell
python -m scripts.process_v7_4_catalogue
python -m scripts.verify_v7_4_catalogue --reproduce
```

This adds 20 tabulated `z >= 4` JADES candidates (three source-tentative),
seven high-ionization line fluxes, and one reviewed link to existing JADES
8083. No numeric black-hole mass is inferred, so growth eligibility is
unchanged; the conservative all-measurements evidence aggregate removes JADES
8083 from the catalogue-level primary-object subset. See
`docs/scholtz25-jades-narrow-line-extraction-notes.md`.

## Getting Started

Requirements and full run instructions are documented in
`docs/getting-started.md`.

The project requires Python 3.12. On macOS/Linux, use the repository-local
interpreter explicitly after following the setup instructions:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
```

Plain `python3` on macOS may select Apple Python 3.9 without NumPy or pandas;
that is an environment failure, not a test result from the supported runtime.

Minimal current-v6 reproduction path from the repository root, using the frozen
v5 measurement catalogue as input:

```powershell
.\.venv\Scripts\python.exe -m scripts.process_v6_blagn
.\.venv\Scripts\python.exe -m scripts.generate_v6_blagn_science --n-samples 10000 --seed 20260808
.\.venv\Scripts\python.exe -m scripts.verify_v6_release --reproduce
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m unittest discover -s tests
```

Expected current products include:

- `data/processed/v6_blagn_measurements.csv` (112 measurements)
- `data/processed/v6_blagn_objects.csv` (105 physical objects)
- `data/crossmatch/v6_measurement_object_links.csv`
- measurement- and object-level `results/v6_blagn_*.csv` products
- 336-row measurement and 315-row physical-object accretion-history tables
- a 105-row full-versus-primary ranking comparison
- four deliberate v5 paper figures under `results/v5_main_text_figures/`

The v6 ranking and uncertainty products use the documented baseline
`z_seed=30`, `epsilon=0.1`, `merger_boost=1` reference unless a scenario column
says otherwise. Outputs are observational triage products under stated
assumptions; they do not prove a single seed or accretion channel. Candidate
interpretations remain in the complete diagnostic tables, while
separate primary-rank columns contain only secure/probable evidence statuses.
Object-level LRD summaries preserve an explicit not-reported state. Full
from-raw reproduction instructions for v1--v6 and the frozen earlier figure
sets are in `docs/getting-started.md`.

The Python package version follows the current implemented science milestone
(`7.2.0`). It is distinct from immutable source-paper versions,
catalogue labels such as `v7.2-accreting-atlas-catalogue`, and maintenance
anchors such as v4.0.1.

## References
Sources of data documented in `data/sources.md`

(Draft/rough list:)
1. Dayal, P. 2024, [A&A](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html), 690, A182
2. Ji, X., Maiolino, R., Übler, H., et al. 2025, [MNRAS, 544, 3900](https://doi.org/10.1093/mnras/staf1867)
3. Maiolino, R., Übler, H., D’Eugenio, F., et al. 2025, [arXiv:2505.22567](https://arxiv.org/abs/2505.22567) 
4. Dayal, P. & Maiolino, R. 2025, [arXiv:2506.08116](https://doi.org/10.48550/arXiv.2506.08116)
5. Prole, L. R., Regan, J. A., Mehta, D., et al. 2025, [arXiv:2506.11233](https://arxiv.org/abs/2506.11233)
6. Adamo, A., Atek, Hakim., Bagley, M., et al. 2025, [arXiv:2405.21054](https://arxiv.org/abs/2405.21054)
7. Dayal, P. & Ferrara, A. 2018, [arXiv:1809.09136](https://arxiv.org/abs/1809.09136)
8. Stark, D., Topping, M., Endsley, R., et al. 2025, [arXiv:2501.17078](https://arxiv.org/abs/2501.17078)
