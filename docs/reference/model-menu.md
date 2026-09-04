# Model and sensitivity menu

All v1/v2/v3 datasets use the same implemented growth equation:

`M_BH(t_obs) = M_seed * exp[f_Edd * ((1 - epsilon) / epsilon) * Delta_t / t_Edd]`

with `t_Edd ~= 0.45 Gyr`, `Delta_t = t(z_obs) - t(z_seed)`, and the shared
Planck-style flat cosmology (`H0=67.3 km/s/Mpc`, `Omega_m=0.315`,
`Omega_Lambda=0.685`). Calculations use logarithmic solar masses and require
`z_seed > z_obs` and `0 < epsilon < 1`.

Implemented comparisons include:

- light, intermediate, heavy, and PBH-labelled seed-mass ranges;
- fixed average accretion histories and required-`f_Edd` inversion;
- thin/slim-disk effective efficiencies across three spin cases;
- merger boosts of one and two in the visual atlas;
- two-state duty-cycle sensitivities with burst `f_Edd` of 1, 2, or 3;
- source-reported mass uncertainty and separately stated method
  systematics;
- alternate-measurement sensitivity.

These are diagnostic scenarios, not claims that any object uniquely selects a
seed or growth channel. Selection functions, time-resolved feedback, and
population-level non-standard cosmologies are outside the implemented inference
contract.
