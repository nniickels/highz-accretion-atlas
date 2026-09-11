# First-read clarity edits

Revisions to the passages raised in the first message. Numerical inputs, equations and sample membership are unchanged.

## 1

Before:

```text
growth assumptions. We test which objects still require average accretion above
the Eddington limit when we account for reported mass errors, shift the adopted
mass scale, or use an alternative mass estimate.
We list all 12 primary objects above this threshold under the reference
assumptions, describe the limitations of their mass estimates, and propose
observations to test them. For four objects shared with the Dayal study, we
separately test the effects of updated measurements and an earlier start to
growth. We also test an independent dynamical mass for A2744-QSO1 while retaining
the catalogue's adopted measurement.
```

After:

```text
growth assumptions. We calculate whether each black hole could reach its observed
mass while accreting, on average, at or below the Eddington limit. We repeat
this calculation using masses drawn from the published uncertainty intervals,
uniform shifts in the mass estimates, and alternative published measurements.
These tests show how the inferred accretion rate depends on mass uncertainty
and the method used to estimate the mass.
For $100\,M_\odot$ seeds formed at $z=30$, radiative efficiency $\epsilon=0.1$
and no mass added by mergers, 12 objects in our Balmer-line sample require an
average Eddington ratio above one. We list all 12, describe the limitations
reported for their mass estimates, and propose observations to test those estimates.
For four objects also studied by Dayal, we calculate separately how the
required accretion rates change when we update the measured masses and redshifts
and when we start growth earlier. For A2744-QSO1, we repeat the calculation
with an independent dynamical mass estimate. We keep the original mass estimate
in the catalogue and report the dynamical comparison separately.
```

## 2

Before:

```text
The contributing studies use different target-selection
criteria and detection limits, so the combined catalogue has no single model
for the probability that an object enters the sample.
```

After:

```text
The contributing studies targeted different kinds of objects and reached
different detection limits. The probability that a black hole would be selected
and detected therefore varies between studies and is unknown for the combined sample.
```

## 3

Before:

```text
mass boost. We approximate the mass added by mergers by multiplying the seed
mass by a constant factor.
```

After:

```text
mass boost. We represent mergers by multiplying the seed mass by a constant
factor before calculating accretion. This approximation omits the timing and
sequence of mergers, their mass ratios, and mass lost through gravitational radiation.
```

## 4

Before:

```text
If the seed mass after the merger boost exceeds the observed mass, we record
zero required accretion. The model already contains too much mass, even before
accretion begins.
```

After:

```text
If $B_{\rm merge}M_{\rm seed}$ exceeds the observed black-hole mass, the
logarithm is negative and we set the required average Eddington ratio to zero.
Even with zero accretion, this seed and merger contribution predict a mass
larger than observed. Reproducing the observed mass would require a smaller
seed, a smaller merger contribution, or a model that includes mass loss.
```

## 5

Before:

```text
Cosmic ages use a flat $\Lambda$CDM approximation with Planck-like parameters:
```

After:

```text
We calculate cosmic ages in a spatially flat $\Lambda$CDM model, using the
Planck-based parameters quoted by \citet{dayal2024}:
```

## 6

Before:

```text
a cosmological constant and neglects radiation. Our $H_0$ and $\Omega_m$
match the values quoted by \citet{dayal2024}, who cite Planck; we explicitly
impose flatness in the age relation.
```

After:

```text
a cosmological constant and neglects radiation. Spatial flatness fixes
$\Omega_\Lambda=1-\Omega_m$ in this approximation.
```

## 7

Before:

```text
The primary sample uses Balmer-line single-epoch virial masses with secure or
probable evidence and no conditional broad-line-region interpretation. These
estimators combine broad H$\alpha$ or H$\beta$ widths with luminosity-based
estimates of the emitting region's radius. Their calibration is based on reverberation mapping of nearby AGN \citep{shen2013}. Grouping them makes the
mass methods more comparable. Their accuracy at high redshift still depends
on calibration, gas dynamics, geometry, obscuration and lensing.
```

After:

```text
For the main comparison, we use masses estimated from broad H$\alpha$ or
H$\beta$ emission lines in objects with secure or probable evidence for an
accreting black hole. We exclude objects whose mass estimate depends on an
unresolved interpretation of the broad emission as a gravitationally bound
broad-line region. We refer to the resulting 224 objects as the primary sample.
These single-epoch virial estimators combine the line width, which estimates
gas velocity, with a luminosity-based estimate of the broad-line region's radius.
Their calibration is based on reverberation mapping of nearby AGN \citep{shen2013}.
Using the same line family and mass-estimation framework reduces differences
between methods in the comparison. Applying these calibrations at high redshift
still requires assessing gas dynamics, geometry, obscuration and lensing for
each object.
```

## 8

Before:

```text
The ten additional exploratory objects comprise nine candidates and GN-z11,
whose mass is inferred from rest-frame ultraviolet lines using local virial
relations \citep{maiolino2024}. We keep this estimate separate to track its
different line and calibration assumptions. We assess the limitations of each mass estimate individually.
```

After:

```text
We also analyse an expanded sample of 234 objects, labelled exploratory in
the tables and figures. It includes the 224 primary objects, nine additional
candidates, and GN-z11. GN-z11's mass is inferred from rest-frame ultraviolet
emission lines using local virial relations \citep{maiolino2024}. We include
it in the expanded comparison because its lines and calibration differ from
those of the Balmer-line sample. The sample division reflects the evidence
for accretion and the methods being compared; the reliability of each mass
estimate requires an individual assessment.
```

## 9

Before:

```text
Objects without reported mass errors contribute a growth requirement at the
published central mass. Calculating a threshold-exceedance probability would
require an additional assumption about their uncertainty. The selected studies
still differ in calibration, target selection and detection limits.
```

After:

```text
When a paper gives a mass without an uncertainty, we can calculate the average
Eddington ratio needed to reach that mass. We cannot calculate the probability
that this ratio exceeds one from the published information, because no mass
uncertainty distribution is available. We therefore include these objects in
calculations at their published masses and omit them from probability calculations.
The mass estimates retained in each sample still use different calibrations,
and the contributing studies have different target-selection criteria and
detection limits.
```

## 10

Before:

```text
held fixed. We approximate each mass distribution from its quoted uncertainty interval. The 12 primary
objects without reported errors contribute point estimates only; probability
calculations use 212 primary and 222 inclusive exploratory objects.
The draws use the quoted errors only.
```

After:

```text
held fixed. For each sampled mass, we calculate the average Eddington ratio
needed to grow from the assumed seed to that mass. The fraction of the 10,000
Monte Carlo draws with a required ratio above one estimates the probability
that growth requires an average rate above the Eddington limit, given the
adopted mass-error distribution and growth assumptions. The draws use the
quoted errors only. Probability calculations include 212 primary and 222
expanded-sample objects; the 12 objects without reported errors enter only
calculations at their published masses.
```

## 11

Before:

```text
We calculate a separate exceedance probability for each fixed mass offset,
using the same growth assumptions.
```

After:

```text
For each offset, we report the fraction of shifted Monte Carlo draws that
require an average Eddington ratio above one. Each probability assumes that
particular mass shift and the stated seed mass, starting redshift, radiative
efficiency and merger contribution. We assign no probability to the offsets
and report their results separately.
```

## 12

Before:

```text
A fixed history is compatible with an object when its required seed mass
(Eq.~\ref{eq:required-seed}) lies within the chosen interval in
$\log_{10}(M_{\rm seed}/M_\odot)$: $[1,2]$ (light), $[3,4]$ (intermediate),
$[4,6]$ (heavy), or $[2,6]$ (broad).
```

After:

```text
For each assumed accretion rate, efficiency, starting redshift and merger
contribution, we solve Eq.~\ref{eq:required-seed} for the initial seed mass
that would grow to the observed black-hole mass. We then check whether that
seed falls in each of four mass ranges: $10$--$100\,M_\odot$ (light),
$10^3$--$10^4\,M_\odot$ (intermediate), $10^4$--$10^6\,M_\odot$ (heavy),
and $10^2$--$10^6\,M_\odot$ (broad). We count an object as compatible with a
range when some seed within it can reproduce the observed mass under these assumptions.
```

## 13

Before:

```text
The seed intervals overlap and are tested separately, without probability
weights. The broad interval spans several possible seed-formation channels. If the required seed is below the
interval's lower bound, even the smallest seed in that interval would grow
beyond the observed mass under the specified history. Compatibility fractions
give the percentage of objects in our sample that a specified history can
reproduce. Their interpretation is limited to this sample because the
contributing studies use different target-selection criteria and detection limits.
```

After:

```text
The seed-mass ranges overlap and are tested separately, without probability
weights. The broad range spans several possible seed-formation channels.
If the seed mass needed to reproduce an object is smaller than the lower
bound of a tested range, even the smallest seed in that range would grow
larger than the observed black hole at the assumed accretion rate. That object
is therefore excluded from the count for that range and set of growth assumptions.
For each set of assumptions, we report the percentage of catalogue objects
whose observed masses can be reproduced from a seed in the tested range.
These percentages describe this literature sample. Estimating the corresponding
percentages among all high-redshift black holes would require accounting for
how each contributing study selected and detected its objects.
```

## 14

Before:

```text
For A2744-QSO1, we compare the frozen virial mass
```

After:

```text
For A2744-QSO1, we compare the virial mass adopted in the catalogue
```

## 15

Before:

```text
Faster growth can also
overproduce the observed mass, moving the required seed below its interval.
```

After:

```text
At higher accretion rates, even the smallest seed in a tested mass range can
grow larger than the observed black hole. Such objects reduce the percentage
reproduced from seeds in that range.
```


## Additional changes

- Abstract: spell out what remains above 95% after a mass shift and explain 0.5 dex as a factor of about 3.2. Name the required average Eddington ratio in the dynamical-mass result.
- Generated dynamical comparison: replace “point requirement,” “threshold” and “conditional exceedance probability” with the required average Eddington ratio and the assumptions used for its probability. Update the generator so the wording survives regeneration.
- Remove the repeated threshold summary following that comparison.
- Retain the 2026a/2026b citation suffixes: the bibliography contains two different Juodzbalis-led papers published in 2026.
- Retain the requested track-selection sentence ending after “observed masses,” Monte Carlo description, and stress-test wording.
