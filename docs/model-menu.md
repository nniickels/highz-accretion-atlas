# Model Menu
(THIS IS A DRAFT)

## v1 Implemented Growth Equation
The v1 science module uses the Dayal-style exponential growth equation:

`M_BH(t_obs) = M_seed * exp[f_Edd * ((1 - epsilon) / epsilon) * Delta_t / t_Edd]`

where `t_Edd = c sigma_T / (4 pi G m_p) ~= 0.45 Gyr`. The pipeline works in
`log10(M/Msun)` for masses, Gyr for cosmic time, dimensionless redshift,
dimensionless average `f_Edd`, and radiative efficiency `0 < epsilon < 1`.

The available growth time is `Delta_t = t(z_obs) - t(z_seed)`, with `z_seed`
required to be greater than `z_obs`. v1 uses the flat Planck 2018-style
Lambda-CDM closed form in the README with `H0 = 67.3 km/s/Mpc`,
`Omega_m = 0.315`, and `Omega_Lambda = 0.685`.

NaN catalogue values are allowed to propagate through science tables. Finite
unphysical inputs, such as negative redshift, negative `f_Edd`, invalid
`epsilon`, or `z_seed <= z_obs`, are validation errors.

## Formation and Growth Models
**A. Seeds**
- Light seeds (Pop III remnants); `M_seed ~ 10–100 Msun`
- Intermediate seeds (dense cluster runaway/nuclear star cluster); `M_seed ~ 1e3–1e4 Msun`
- Heavy seeds (DCBH-like / SMS-like); `M_seed ~ 1e4–1e6 Msun` 
- PBH seeds; `1e2–1e6 Msun`

**B. Growth models**
- Thin-disk Eddington-limited; `f_Edd ≤ 1`, `ε ≈ 0.1`
- Supercritical / slim-disk-like; allow `f_Edd > 1` and/or reduced `ε` (e.g., `ε ∈ [0.03, 0.1]`)
- Duty-cycle / bursty growth; `⟨f_Edd⟩ = D * f_Edd_burst`
- Spin/efficiency scan; `ε ∈ [0.04, 0.3]` 
- Merger-assisted growth; `B_merge ∈ {1, 2, 5, 10}` applied over `Δt` 

**C. Fuel / environment “gating” (plausibility priors)**
- DCBH gate
- Cluster runaway gate
- PBH halo-seeding gate

**D. Cosmology / structure-formation alternatives (population-level module)**
- ΛCDM baseline
- PBH-boosted small-scale fluctuations
- Warm DM / fuzzy DM
- Primordial non-Gaussianity / modified power spectrum

## Interpretation Models
**A. MBH inference interpretations**
- Single-epoch virial systematics
- Non-virial broadening
- Line fitting choices
- Continuum proxy mismatch

**B. Luminosity / accretion interpretations**
- Bolometric correction uncertainty
- Orientation / anisotropy / beaming
- Obscuration / reprocessing
- Variability

**C. Host galaxy interpretations (M\*, SFR, ages)**
- AGN contamination of SED
- Nebular line contamination in broadband photometry
- LRD “fake Balmer break”
- Lensing magnification uncertainty

**D. Metallicity / ISM interpretations (when Z is included)**
- AGN vs star-forming calibration choice
- Ionization parameter / density / Te assumption
- Dust extinction correction for lines
- Shock/outflow contamination

**E. Selection / sample effects (metadata + later corrections)**
- Malmquist/brightness bias
- spectroscopic follow-up bias
- cosmic variance between fields
