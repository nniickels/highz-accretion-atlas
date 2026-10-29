# Scientific assumptions and limits

The catalogue supports growth calculations and comparisons within compatible
object classes and mass methods. Its heterogeneous selection does not support
population fractions, number densities, or seed-channel frequencies. See
[selection and completeness](selection-completeness.md).

## Growth assumptions

The [model guide](model-menu.md) defines the growth equation and implemented
scenarios. Baseline rankings, duty cycles, and seed-redshift maps use efficiency
0.1 and matter-plus-Lambda cosmic ages. The v3 minimum-seed table and v4 include
radiation; each [result table](catalogue-results.md) records its assumptions.

Spin-separated accretion maps and compatibility matrices use ideal Kerr
thin-disk efficiencies below an Eddington ratio of one and
`epsilon_eff = epsilon_spin*f*exp(1-f)` above it. This illustrative
photon-trapping rule assumes `f=1+ln(mdot)`, with accretion rate normalized by
`L_Edd/(epsilon_spin*c^2)`. It does not model spin evolution, feedback, or gas
supply. Growth tracks retain their stated constant efficiencies.

Requirements depend strongly on these choices. Holding the reference assumptions
fixed, changing efficiency from 0.1 to `1-sqrt(8/9)=0.05719` multiplies required
rates by 0.54594 and leaves no central-mass requirements above unity in the
expanded sample. This is parameter sensitivity, not a spin measurement or proof
that the required fuel was available. Average rates also do not rule out brief
super-Eddington episodes.

Fixed-history compatibility requires the calculated starting mass to fall within
the tested seed-mass range. If the required mass is below that range, even its
smallest seed would overgrow the object under the fixed history. If it is above
the range, even its largest seed would fall short. These exclusions apply to
the stated history, not every possible accretion rate or duty cycle. PBH-labelled mass
ranges do not establish primordial formation or abundance; see the
[v4 methods and limits](pbh-growth-v4.md).

## Uncertainties

Reported mass errors use 10,000 equal-side half-normal draws in log mass,
with separate scales above and below the central value. The metadata label is
`equal_side_half_normal_in_log_mbh`. These approximate quoted intervals rather
than reconstruct source posteriors. Redshifts and scenario parameters remain
fixed; the sampled fractions are conditional on those choices.

Additional method systematics remain separate unless explicitly applied in a
sensitivity test. ZS7's reported 0.4-dex error already includes calibration
scatter. Source-model alternatives, such as dust corrections, are correlated
interpretations of one measurement, not independent objects or posterior draws.

Twelve NEXUS masses lack reported errors. Their point values are retained with
`mbh_uncertainty_mode=point_estimate_no_reported_mbh_error`; probabilities and
uncertainty ranks are unavailable. The Monte Carlo figure shows them as open
diamonds in a separate “No error” row.

## Samples, identities, and ranks

[Catalogue eligibility](catalogue-schema.md) and
[publication selection](../../data/publication/README.md#sample-selection) have
different purposes. Candidate, disputed, conditional, and mass-free records remain
available even when excluded from numerical comparisons.

Three [identity groups](../source-notes/redshift-identity-audit.md) remain open,
so stored object IDs are not a validated unique-object census. The publication
samples exclude all six affected records. Central redshifts and available
coordinates pass independent source checks; redshift uncertainties, full
posteriors, and auxiliary observables have partial coverage. See
[validation coverage](../../data/validation/README.md).

Required-rate rankings order a stated growth requirement. The
[browsing score](../guides/catalogue-navigation-score.md) and follow-up priorities
are heuristics, without probabilistic calibration or measured information gain.
Comparisons across incompatible mass methods or object classes are not justified
by a shared position in a ranking.

Follow-up category `A_high_central_growth_requirement` identifies high central
requirements in objects passing the catalogue primary criteria with secure
source evidence; it does not imply robustness to calibration uncertainty. Unresolved identities receive
`identity_review_required` and no numerical follow-up score or rank.

The [literature scope](literature-scope.md) defines membership and source-version
choices. Reproduction checks establish implementation consistency; they do not
validate mass estimators, resolve identities, or establish that an assumed growth
history is physically achievable.
