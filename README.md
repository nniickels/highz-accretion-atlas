# highz-accretion-atlas

This project builds a standardized, source-tracked catalogue of JWST-identified black holes at z ≥ 4 and uses it to test what combinations of seed mass, average Eddington fractions, seed redshifts, and radiative efficiencies can produce it given an observed black hole mass at redshift z. 

This is helpful because current high-z AGN/BH literature mixes methods and conventions. A reproducible dataset with explicit assumptions and robustness checks makes it clearer which objects are genuinely challenging for standard formation models versus artifacts of inference choices, and helps prioritize the best candidates for follow-up and deeper theory work.

The project produces parameter-space maps and growth tracks based on the analytic black hole growth equation used in [Dayal (2024)](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html).

## Background
JWST pushes sensitive spectroscopy and imaging into the first few billion years of cosmic history, where there is not much time for black holes and galaxies to assemble. That makes many z ≥ 4 discoveries natural stress tests. Small shifts in inferred `M_BH`, `M_*`, or `L_bol` can imply very different growth histories, especially since many calibrations were developed at low redshift.

However, key quantities are often inferred with different methods and assumptions across papers, which can move objects in or out of the “peculiar” regime. This project’s motivation is to create a standardized assumption-tracked catalogue so it’s clearer which objects remain genuinely challenging under reasonable alternative interpretations, and therefore best motivate additional formation/growth channels and follow-up observations. 

Testing multiple seed + growth scenarios matters because different origins imply different requirements to reach the observed state by a given redshift. Light seeds may demand extreme accretion histories while heavy seeds reduce that burden but can require special environments. More theoretical ideas like PBH seeding represent a fundamentally earlier “head start.” Studying these earliest accreting systems helps pin down how the first structures formed and grew, refining our picture of cosmic history and testing the physics that underpins modern cosmology.

The growth model follows Eq. 1 of [Dayal (2024)](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html):

$M_{BH}(t) = M_{seed}(t_{seed})e^{\frac{4\pi Gm \rho f_{Edd}}{c\sigma T}\frac{1-\epsilon}{\epsilon}(t-t_{seed})}$

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

The main figures are 2D parameter maps with:

- x-axis: $\log_{10}(M_{seed} / M_\odot)$
- y-axis: $f_{Edd}$
- colour: predicted $\log_{10}(M_{BH} / M_\odot)$
- contours or markers: observed $M_{BH}$ for catalogue objects

The project also makes [Dayal (2024)](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html) Fig. 1-style growth-track plots using the compiled catalogue.

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

The main text should showcase the atlas logic and strongest rankings, while
the appendix preserves the comprehensive technical and visual record. This
keeps the project centered on observational triage rather than on claiming that
any single seed or accretion channel is proven.

## Workflow
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

1. Add source-specific raw files or ingestion scripts.
2. Preserve source-paper measurements rather than overwriting them.
3. Track duplicate objects using coordinates, aliases, and redshift.
4. Compare how different papers move objects through growth-parameter space.
5. Recompute rankings and uncertainty-aware diagnostics.
6. Update final-style figures and tables.

### v4: Measurement Versioning

Separate physical objects from literature measurements.

1. Add stable physical object IDs.
2. Keep `measurement_id` as the row-level source-paper measurement ID.
3. Add aliases and cross-match metadata.
4. Build measurement-level and object-level ranking tables.
5. Flag objects whose interpretation depends strongly on measurement choice.

### v5: Multi-Class High-z Accreting BH Atlas

Expand beyond broad-line AGN.

Possible classes:

- LRDs / compact red AGN candidates
- X-ray-selected high-z black-hole candidates
- lensed candidates
- high-ionization-line candidates
- narrow-line AGN candidates
- luminous high-redshift quasars as comparison anchors

For each class:

1. Define required metadata fields.
2. Track mass method and selection caveats.
3. Keep object classes visually and statistically distinct.
4. Recompute atlas rankings with class-aware caveats.

### v6: Accretion-History Diagnostics

Move beyond constant-average growth tracks.

1. Compare reported current $f_{Edd}$ with required lifetime-average $f_{Edd}$.
2. Add duty-cycle models.
3. Add bursty-accretion scenarios.
4. Compute required duty cycle for fixed seed and burst assumptions.
5. Identify objects that require unusually early, sustained, or efficient growth.

## Getting Started 
Requirements and instructions documented in `docs/getting-started.md`

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
