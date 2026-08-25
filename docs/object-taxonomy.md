# Accreting massive-black-hole taxonomy

“Accreting objects” alone is too broad: it also describes stellar binaries,
protostars, white dwarfs, and neutron stars. The atlas concerns
**high-redshift accreting massive-black-hole systems and candidates**.

AGN, broad-line AGN, quasars, and many LRDs can all involve black-hole accretion,
but the terms are not interchangeable. AGN describes an accretion-powered
galactic nucleus; Type 1/broad-line AGN is a spectroscopic subtype; quasar is a
luminous AGN regime; and LRD is a compact/red observational phenotype whose
physical interpretation may be AGN-dominated, stellar, or mixed. A black hole
itself is the compact object, not evidence that it is currently accreting.

The catalogue therefore uses independent axes for evidence strength,
spectroscopic type, selection channel, phenotype, lensing, mass method, and
growth-ranking eligibility. Only objects with sufficiently credible MBH
constraints should enter the primary growth ranking. Unlike selection
functions and evidence classes remain separately summarized and visualized.

For the v5 broad-line sample, `secure_accreting_mbh` means a published robust
broad-line detection without a recorded alternative physical interpretation.
A robust line with a possible outflow or uncertain absorption interpretation
is `probable_accreting_mbh`; a recorded alternative non-AGN explanation is
`candidate_accreting_mbh`. Tentative broad-line detections are also probable,
but their separate detection-confidence field remains tentative. These labels
do not alter published classifications or silently discard measurements.

`evidence_status_basis` records the rule used for each label. Growth ranking is
evaluated only when `growth_ranking_eligible_flag` is true; the v5 science
layer raises an error if an ineligible row is passed to it. The additional
`primary_growth_ranking_flag` limits the primary evidence-supported ordering to
secure and probable systems. Candidate measurements remain preserved in the
full exploratory diagnostic ordering but receive no primary rank. Evidence
status, line-detection confidence, and mass/line-model reliability therefore
remain distinct.

At physical-object level, evidence status is the most conservative status
among all linked measurements. The preferred measurement's status and the
measurement/source identifiers supporting the aggregate status remain
separate provenance fields.
