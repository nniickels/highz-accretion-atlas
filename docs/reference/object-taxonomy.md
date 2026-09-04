# Accreting massive-black-hole taxonomy

The atlas concerns high-redshift accreting massive-black-hole systems and
candidates. AGN, broad-line AGN, quasars, and LRDs are not interchangeable:
spectroscopic type, luminosity regime, and observational phenotype are recorded
on independent axes.

Canonical measurements separate:

- `object_class` and `spectroscopic_type`;
- `evidence_status`: `secure`, `probable`, `candidate`, or `disputed`;
- selection channels and phenotype tags;
- lensing status and correction provenance;
- mass method, reported uncertainty, and method systematic;
- mass-comparability group and growth-ranking eligibility.

Exactly one preferred measurement controls each physical object's canonical
evidence and mass status. All linked measurement statuses, sources, and bases
remain on the object row, so alternates are visible without being counted as
independent objects.

`growth_ranking_eligible_flag` requires a supported numeric mass, resolved
identity and lensing treatment, and an identified comparison method.
`primary_growth_ranking_flag` additionally requires sufficiently credible
evidence for the stated comparison. Candidate, disputed, conditional-mass, and
no-mass records remain in catalogue and caveat products even when unranked.
