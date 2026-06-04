# highz-accretion-atlas

This project builds a standardized, source-tracked catalogue of JWST-identified black holes at z ≥ 4 and uses it to test what combinations of seed mass, average Eddington fractions, seed redshifts, and radiative efficiencies can produce it given an observed black hole mass at redshift z. 

The project produces parameter-space maps and growth tracks based on the analytic black hole growth equation used in [Dayal (2024)](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html). The main output is a set of transparent figures showing where each observed object lies relative to physically interpretable seed and growth scenarios.

This is helpful because current high-z AGN/BH literature mixes methods and conventions. A reproducible dataset with explicit assumptions and robustness checks makes it clearer which objects are genuinely challenging for standard formation models versus artifacts of inference choices, and helps prioritize the best candidates for follow-up and deeper theory work.

## Background
JWST pushes sensitive spectroscopy and imaging into the first few billion years of cosmic history, where there is not much time for black holes and galaxies to assemble. That makes many z ≥ 4 discoveries natural stress tests. Small shifts in inferred `M_BH`, `M_*`, or `L_bol` can imply very different growth histories, especially since many calibrations were developed at low redshift.

However, key quantities are often inferred with different methods and assumptions across papers, which can move objects in or out of the “peculiar” regime. This project’s motivation is to create a standardized assumption-tracked catalogue so it’s clearer which objects remain genuinely challenging under reasonable alternative interpretations, and therefore best motivate additional formation/growth channels and follow-up observations. 

Testing multiple seed + growth scenarios matters because different origins imply different requirements to reach the observed state by a given redshift. Light seeds may demand extreme accretion histories while heavy seeds reduce that burden but can require special environments. More theoretical ideas like PBH seeding represent a fundamentally earlier “head start.” Studying these earliest accreting systems helps pin down how the first structures formed and grew, refining our picture of cosmic history and testing the physics that underpins modern cosmology.

The growth model follows Eq. 1 of [Dayal (2024)](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html):

$M_{BH}(t) = M_{seed}(t_{seed})e^{\frac{4\pi Gm \rho f_{Edd}}{c\sigma T}\frac{1-\epsilon}{\epsilon}(t-t_{seed})}$

Cosmic time in Gyr, derived from the FLRW form with flat $\Lambda$ CDM: 

$t(z) = \frac{2}{3H_0\sqrt{\Omega_{\Lambda}}}\operatorname{asinh}(\frac{\sqrt{\Omega_{\Lambda}/{\Omega_m}}}{(1+z)^{3/2}})$

For each object, the pipeline computes the cosmic time available between `z_seed` and the observed redshift. It then explores a grid of:

- `M_seed`
- `f_Edd`
- `z_seed`
- radiative efficiency `epsilon`

The main figures are 2D parameter maps with:

- x-axis: `log10(M_seed / Msun)`
- y-axis: `f_Edd`
- colour: predicted `log10(M_BH / Msun)`
- contours or markers: observed `M_BH` for catalogue objects

The project also makes [Dayal (2024)](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html) Fig. 1-style growth-track plots using the compiled catalogue.

## Workflow
### v1: Start Easy

Use one clean object class from one paper.

1. Ingest one source catalogue into `data/raw/v1_raw.csv`.
2. Standardize it into `data/processed/v1_processed.csv`.
3. Validate the catalogue schema, missing values, methods, and provenance.
4. Implement the Dayal growth equation in a dedicated growth module.
5. Make one-object parameter maps first.
6. Scale to all v1 objects.
7. Produce:
   - `M_BH` vs redshift growth-track plot
   - per-object `f_Edd` vs `M_seed` maps
   - sample-level map summaries
   - table of required `f_Edd` for chosen seed masses
   - table of required `M_seed` for chosen accretion assumptions

No feasibility scores are used. Interpretability comes from physical thresholds such as `f_Edd <= 1`, `M_seed = 100 Msun`, `10^4 Msun`, `10^5 Msun`, and uncertainty bands.

### v2: Same Object Class, More Papers

Add more broad-line AGN catalogues.

1. Add new raw source files or source-specific ingestion scripts.
2. Track duplicate objects across papers using coordinates, aliases, and redshift.
3. Preserve multiple measurements for the same physical object.
4. Compare how different papers move objects in parameter space.
5. Add uncertainty propagation using Monte Carlo sampling of reported errors.

### v3: More Object Classes

Add other early accretion candidate classes.

Possible additions:

- LRDs / compact red AGN candidates
- X-ray-selected high-z black holes
- high-ionization-line candidates
- lensed candidates
- narrow-line AGN candidates

Each class should have required metadata fields and clearly documented caveats.

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
