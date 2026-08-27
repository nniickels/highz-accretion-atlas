# v6 BLAGN catalogue schema

v6 is the final planned same-class broad-line-AGN consolidation. It adds the
seven-row Davis/THRILS source table to frozen v5, applies `z >= 4` during
processing, and produces 112 literature measurements representing 105 physical
objects. All v1--v5 products and default-measurement choices remain unchanged.

| Product | Rows | Purpose |
| --- | ---: | --- |
| `data/raw/davis26_thrils_blagn_table5.csv` | 7 | Complete source-native Appendix Table 5 extraction plus exact-ID coordinate provenance |
| `data/processed/v6/v6_blagn_measurements.csv` | 112 | Every retained literature measurement |
| `data/processed/v6/v6_blagn_objects.csv` | 105 | One reproducible default measurement per object |
| `data/crossmatch/v6/v6_measurement_object_links.csv` | 112 | Measurement/object links and default rules |
| `data/crossmatch/v6/v6_object_aliases.csv` | 112 | Source aliases and coordinates |
| `data/crossmatch/v6/v6_reviewed_match_candidates.csv` | 0 | Empty, schema-preserving candidate registry |

Six THRILS rows pass the redshift cut and all are new physical objects. The
known THRILS/Taylor repeat lies below `z=4`, so it is documented in raw-source
caveats without changing the processed identity graph.

THRILS adds source-native ID fields, Table 5 redshift and flux measurements,
programme coordinates/redshift with independent provenance, broad-Halpha FWHM
where explicitly published, mass-method and formal/systematic uncertainty
metadata, selection criteria, and source caveats. Missing host, luminosity,
Eddington-ratio, LRD, absorption-fit, and unreported FWHM values remain missing.
LRD is an orthogonal phenotype, never the object class.

The six new rows are `secure_accreting_mbh`, `type1_broad_line`, and
growth-ranking eligible because Davis reports individually selected broad-Halpha
components and virial masses without a recorded alternative physical
interpretation. This is an evidence/taxonomy assignment, not a claim that
single-epoch masses lack substantial calibration uncertainty.

