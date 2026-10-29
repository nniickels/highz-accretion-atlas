# Model and sensitivity menu

All v1/v2/v3 datasets use the same implemented growth equation:

`M_BH(t_obs) = M_seed * exp[f_Edd * ((1 - epsilon) / epsilon) * Delta_t / t_Edd]`

with `t_Edd ~= 0.45 Gyr` and `Delta_t = t(z_obs) - t(z_seed)`. Baseline
calculations use the flat cosmology (`H0=67.3 km/s/Mpc`, `Omega_m=0.315`,
`Omega_Lambda=0.685`). Calculations use logarithmic solar masses and require
`z_seed > z_obs` and `0 < epsilon < 1`.

Implemented comparisons include:

- light, intermediate, heavy, and PBH-labelled seed-mass ranges;
- fixed average accretion histories and required-`f_Edd` inversion;
- thin-disk efficiencies across three spin cases, with an illustrative
  photon-trapping adjustment above the Eddington limit;
- merger boosts of one and two in the catalogue figures;
- two-state duty-cycle sensitivities with burst `f_Edd` of 1, 2, or 3;
- source-reported mass uncertainty and separately stated method
  systematics;
- alternate-measurement sensitivity.

The [extended v3 tables](catalogue-results.md) compare assumptions for every
usable mass. Their minimum-seed calculations include radiation in cosmic ages;
the reference rate comparisons retain the baseline cosmology.

These scenarios compare growth requirements under specified assumptions.
Identifying a seed-formation channel requires additional evidence. The analysis
omits selection functions, time-resolved feedback, and population models with
non-standard cosmologies.

The separate [v4 PBH growth extension](pbh-growth-v4.md) distinguishes
formation from accretion onset, uses radiation-inclusive ages, and excludes
seeds that already overpredict a target mass. It tests a specified published
growth benchmark and delayed-onset sensitivities; a PBH-labelled mass range
alone remains insufficient to establish primordial formation or viability.
