# UHZ1 X-ray Evidence-History Extraction Notes

## Source boundary

v3 adds one physical object, UHZ1 (`UNCOVER-26185`), as two literature
measurement versions. This is an evidence-history family rather than two
independent objects:

- Bogdán et al. (2024), Nature Astronomy 8, 126--133,
  DOI `10.1038/s41550-023-02111-9`, arXiv `2305.15458v2`.
- Zou et al. (2026), submitted, arXiv `2603.24893v1`.

Goulding et al. (2023), ApJL 955 L24, DOI
`10.3847/2041-8213/acf7c5`, arXiv `2308.02750v3`, supplies the companion
spectroscopic and host-galaxy context used in the audit. The three
downloaded source archives have SHA-256 hashes recorded in the v3 dataset manifest.
The extraction date is 2026-08-27.

## Identity and source values

Both rows use the source-published position RA `00:14:16.096`, Dec
`-30:22:40.285` (3.5670666667, -30.3778569444 degrees) and are assigned to
`HZA-UHZ1` / `HZS-UHZ1`. The original row retains its source-era photometric
redshift `z≈10.3`; the reanalysis row retains `z_spec=10.054`. Their different
redshifts are not averaged.

Bogdán et al. report a 4.2--4.4 sigma hard-band excess, 42 total and 20.6 net
counts, an adopted intrinsic `2--10 keV` luminosity of `1.9e44 erg/s`, and a
bolometric luminosity near `5e45 erg/s`. The paper's `10^7--10^8 Msun` range
depends on an Eddington-accretion assumption and an X-ray absorption/bolometric
model. v3 preserves the bounds as censored observables and deliberately does
not turn their midpoint into a canonical mass.

Zou et al. reanalyse the full 2.2 Ms Chandra data and report a 2.3--2.9 sigma
hard-band range across plausible reductions. The additional exposure does not
show a persistent signal. Their nine MIRI Table 3 flux-density upper limits are
preserved in full, along with the derived `L_bol < 1.3e45 erg/s` limit.

## Admission decisions

- `UHZ1_bogdan24` is retained as `candidate`, nonpreferred, and auditable.
- `UHZ1_zou26` is `disputed` and preferred because it is the latest full-data,
  multiwavelength assessment.
- Both rows are `object_class=xray_agn_candidate` and
  `mass_comparability_group=no_numeric_mass`.
- Both are excluded from growth rankings with `missing_numeric_mbh`; this is an
  evidence boundary, not deletion from the atlas.
- Lensing magnifications remain source-versioned (3.81 and 3.71). No value is
  averaged, and no unresolved lensing-dependent mass is admitted.
