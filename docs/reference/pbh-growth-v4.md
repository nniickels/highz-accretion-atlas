# v4: conditional PBH-seed growth compatibility

v4 is an analysis extension of the frozen v3 catalogue, not a fourth catalogue
or a new source-admission release. Its claim is **compatibility with a specified
post-onset growth prescription**. It does not establish PBH formation,
population viability, or a need for primordial seeds.

## Published benchmark and adaptations

The benchmark is the growth component of
[Dayal (2024), A&A, 690, A182](https://doi.org/10.1051/0004-6361/202451481),
[versioned text](https://arxiv.org/html/2407.07162v2), Equation 1 and Section 2
(reviewed 2026-10-01). That calculation infers PBH masses at matter–radiation
equality, `z=3400`, by reversing exponential Eddington-limited growth with
constant `epsilon=0.1`. v4 implements this inversion and sensitivity tests;
it does **not** implement the gas-limited halo assembly and feedback model in
Section 3, or reproduce the paper's inferred PBH mass function.

Our equality-onset case is an **optimistic formal growth benchmark**. PBHs are
assumed to exist before equality, but their formation time is not calculated.
Accretion onset is an independent parameter. Holding the seed mass constant
before onset is an approximation, not a survival or gas-supply calculation.
Delaying onset tests how much the timing advantage depends on access to fuel.
None of the chosen onset redshifts is asserted to be physically guaranteed.

The configured anchors are `z_accretion=20,25,30,60,100,300,1100,3400`, augmented
by a logarithmic grid. These distinguish galaxy-era, earlier, approximately
recombination-era, and equality-era starts. A stellar-remnant control at `z=30`
is a starting-time assumption, not a hard first-star boundary. A heavy
astrophysical control also starts at `z=30`; neither control includes formation
probabilities, stellar lifetimes, or a gas supply model.

## Targets and inputs

The three highest reference-growth-pressure **publication-primary** objects
are selected by recalculating their required ratio with the unchanged v3
matter+Lambda reference cosmology. GN-z11 is added as an expanded-sample
high-redshift comparator. Current targets are UNCOVER-20466,
COSMOS3D-13852, RUBIES-EGS-55604, and GN-z11. GN-z11's UV virial mass is distinct
from the primary Balmer masses; results are not pooled into a population fraction.

The driver reads the canonical v3 preferred-object table and existing
publication-membership table, checks membership against the identity/evidence
exclusion policies, and retains source identifiers, URLs, error bounds, and
caveat tags. It does not rebuild or write publication products. These inputs
and the implementation are hashed in `results/v4/v4_manifest.json`.

Configuration: [`../../data/scenarios/v4_pbh_growth.json`](../../data/scenarios/v4_pbh_growth.json).
The catalogue literature cutoff remains unchanged; this is a theoretical
scenario addition, not a new observational catalogue source.

## Equations and interpretation

All v4 scenario comparisons use the existing radiation-inclusive flat
cosmology: `H0=67.3 km/s/Mpc`, `Omega_m=0.315`,
`Omega_r=Omega_m/(1+3400)`, `Omega_Lambda=1-Omega_m-Omega_r`.
The reference ranking column alone retains the original matter+Lambda age
relation. Minor numerical differences from the published Dayal benchmark and
v3 reference values are expected because the age calculation includes radiation.

With `Delta_t=t(z_obs)-t(z_accretion)` and `t_Edd=0.45 Gyr`, no mergers, and
constant efficiency, the minimum onset seed for a mean luminosity-based
Eddington ratio bounded by `f_cap` is

```text
log10(M_seed,min/Msun) = log10(M_BH/Msun)
                       - f_cap * (1-epsilon)/epsilon * Delta_t/t_Edd / ln(10).
```

This is a minimum for **some** mean rate between zero and the cap. It is not a
prediction that all seeds grow continuously at the cap. A seed in the interval
`[M_seed,min, M_BH]` can reproduce the central mass within that prescription.
Seeds already above the target cannot reproduce it without mass loss and are
excluded; a clipped required rate of zero is not evidence of compatibility.

Sensitivity tables use caps `0.3,1,2`, efficiencies `0.1` and
`1-sqrt(8/9)=0.0571909584`, and separate mass offsets `0,-0.5 dex`. The cap of 2
is a constant-efficiency formal super-Eddington sensitivity; slim-disc physics,
spin evolution, feedback, and gas limitations are not modelled. The seed-mass
map spans `10^-6–10^7 Msun` for visualization, not an allowed PBH prior or a
formation-model prediction. Any subsolar requirements must separately pass
survival and external-constraint tests.

## Monte Carlo support

Each object has 10,000 equal-side half-normal log-mass draws using the existing
asymmetric-error helper and a fixed, stable per-object random stream. Source
errors are treated as Gaussian scales as in the current analysis; no posterior
reconstruction or additional calibration scatter is claimed. Redshifts and
scenario parameters remain fixed. A `-0.5 dex` offset translates the same mass
draws rather than resampling them. Missing errors yield central-mass results
and **missing**, not certain, probability/percentile products.

`mass_draw_fraction_within_growth_cap` is the fraction of those draws satisfying

```text
M_seed <= M_draw <= M_seed * exp[growth_at_cap].
```

It is conditional support from the adopted mass-error approximation, **not** a
probability of PBH origin, model evidence, or a probability that gas supply is
adequate. Seed-overprediction fractions are reported separately. The map CSV
stores the displayed baseline (`epsilon=0.1`, cap 1, offset 0); the compact
minimum-seed table stores the full efficiency/cap/offset sensitivity grid.
No rate or seed prior is integrated over. Identical onset mass and growth
parameters give identical answers for primordial and astrophysical labels.

## Abundance and observational constraints: not yet tested

Growth compatibility is necessary but insufficient for PBH viability. A next
stage would specify a formation mechanism and PBH mass distribution, an
independent descendant number density, seed occupation/success fractions, and
growth histories consistent with gas availability. The heterogeneous atlas
counts have no common survey volume or completeness correction and cannot be
used to estimate a PBH abundance or dark-matter fraction. Dayal's density result
cannot be transferred to this catalogue without those inputs.

The resulting PBH population must be compared with applicable mass-dependent
microlensing, CMB/accretion, dynamical and gravitational-wave constraints, with
their assumptions and evolution accounted for. Extended mass functions cannot
generally be checked by treating every monochromatic limit as independent.
See [Carr et al., *Constraints on Primordial Black Holes*](https://arxiv.org/abs/2002.12778)
and the primary CMB-accretion calculation of
[Ali-Haïmoud & Kamionkowski (2017)](https://doi.org/10.1103/PhysRevD.95.043534).
These are reading references, not digitized or evaluated bounds in v4.

Rejecting a particular `100 Msun, z=30, epsilon=0.1` control does not reject
stellar seeding generally, and does not establish that PBHs are required.

## Run and verify

### Current central-mass results

For `epsilon=0.1`, cap 1, and no mergers, the equality-onset minimum seeds are
approximately 1,184 Msun (UNCOVER-20466), 535 Msun (COSMOS3D-13852), 495 Msun
(RUBIES-EGS-55604), and 267 Msun (GN-z11). Starting at `z=30` instead requires
approximately 8,527, 3,855, 3,569, and 1,924 Msun, respectively. These are
algebraic growth requirements at the adopted central masses, not PBH formation
predictions. They show that simply changing the timing of a 100 Msun seed is
insufficient at this efficiency and rate cap; they do not establish a primordial
origin. The tables quantify the large sensitivity to efficiency, allowed mean
rate, and mass estimates.

### Commands

From the repository root, in the existing pinned Python 3.12 environment:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m src.internal.pbh_growth_v4 --write
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m src.internal.pbh_growth_v4 --verify
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p 'test_pbh_v4.py'
```

Alternatively use the optional `scripts/05_pbh_growth_v4.ipynb`. The existing
00–04 workflows and v1/v2/v3 dataset interfaces retain their original scope.
v4 has its own verification and manifest; manuscript/poster integration is a
separate future decision. Verification rebuilds tables independently, compares
PNG pixels and decoded PDF contents in a temporary directory, and detects
changed inputs, implementation, or stored artifacts before accepting them.

Minimum log-seed columns allow an absolute regeneration difference of
`1e-13` dex to accommodate macOS/Linux cancellation roundoff near zero.
Other numerical columns retain the shared strict tolerances; stored artifact
hashes, input hashes, and figure comparisons remain unchanged.

During the disposable CI notebook workflow, regenerated v3 input CSV bytes may
differ across platforms. If `HIGHZ_BASELINE_ROOT` identifies an independent
checkout whose input bytes match the pinned v4 hashes, verification compares
the regenerated CSV contents against that baseline using the shared numerical
tolerances. Changed measurements still fail. Code and non-CSV inputs always
require exact hashes; verification never refreshes the manifest implicitly.
