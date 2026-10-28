# Literature scope and cutoff

The current v1/v2/v3 source-family membership reflects the literature review
completed on **2026-09-03**. The cutoff records the review date for the current
catalogue state; it does not imply that v3 is an exhaustive census of every
high-redshift accreting black-hole report published before that date.

## Admission scope

A source enters a dataset only when the repository contains:

- a stable primary-source or archive record;
- source-native tabular measurements suitable for deterministic extraction;
- explicit evidence, mass-method, uncertainty, lensing, and missingness rules;
- identity and host-system review where cross-source overlap is possible; and
- regression anchors proving row membership and published values.

v1 contains the original JADES BLAGN source family. v2 adds comparable JWST
broad-line source families with canonical masses. v3 adds JWST-identified
heterogeneous X-ray, narrow-line, high-ionization, infrared, photometric, and
broad-line-candidate source datasets. Ground-selected legacy quasar samples are
outside the catalogue boundary. The authoritative included-source list is
`data/source_provenance_registry.csv`.

## Considered but not admitted by the cutoff

| Source | Status in v3 | Reason |
| --- | --- | --- |
| Juodzbalis et al. (2026), *A direct black-hole mass measurement in a little red dot at high redshift*, DOI `10.1038/s41586-026-10579-4` | external comparison only | The source is A2744-QSO1, already represented in v2/v3. Its pinned v2 archive reports a preferred direct MOKA3D mass of log(MBH/Msun)=7.7+/-0.3 plus an inclination-free lower-limit result. It requires a direct-mass adapter and adds zero objects. |
| Jin et al., J0226 JWST BLAGN sample | screened, no new membership | All four physical objects are represented by admitted Baccus rows, so adding the dataset would not contribute a new candidate. |
| Baccus GLIMPSE, MACS0416, and MACS1149 cluster-field rows without published magnifications | source-local exclusions | Thirteen otherwise-new Baccus objects lack source-published lensing corrections. Three GLIMPSE objects enter independently through Fei with explicit corrections; the remaining ten are not admitted as comparable mass points. |

The **17 October 2026** edition expands v2/v3 membership at the unchanged
**2026-09-03** literature cutoff: v2 is the comparable
Balmer source-family collection and v3 contains v2 plus other evidence/methods.
The preceding edition is recoverable at Git commit
`fc0c5501ad2271865b1c040307cad8dd8ca5721a` (v2: 218/211/210;
v3: 350/338/337 measurements/object records/hosts). This is a membership
expansion, not an accuracy correction or a new v4 catalogue.

| Admitted family | Placement | Reason |
| --- | --- | --- |
| Taylor CAPERS-LRD-z9, arXiv:2505.04609v4 | v2 and v3 | New object with source-canonical broad-Hbeta virial mass |
| Tripodi CANUCS-LRD-z8.6, published 19 November 2025 | v2 and v3 | New object with lens-corrected Balmer virial mass |
| Schindler J1007_AGN, published 17 September 2025 | v2 and v3 | New object; conservative observed Balmer baseline, correlated dust alternative retained |
| Takechi MACS0416-Y1, arXiv:2605.14922v1 | v2 and v3 | New candidate with lens-corrected Balmer mass; expanded-only inference |
| Fudamoto SAPPHIRES ID-8760, arXiv:2503.15597v1 | v3 only | New tentative LRD/AGN without a published numerical BH mass |

All adopted versions predate the cutoff; actual retrieval/admission is
2026-10-17. Every new family contributes one new physical object under the
reviewed source/alias/coordinate screen. Morishita arXiv:2508.01372v2 is
same-object CANUCS evidence, not another admitted family or mass: it removes
the v1 mass calculation and reuses Tripodi. The five extraction notes and
source-native screens retain exclusions, model alternatives and missingness.
SAPPHIRES's unidentified foreground contaminant remains a caveat, not a forced
object match. The three pre-existing unresolved identity groups remain open.

This edition adds these five families. Other new source families or
measurements require a separately documented membership revision;
the A2744 direct mass comparison below remains external.
Accuracy fixes, publication-status corrections, and provenance updates apply to
every affected existing version. Any correction to an extracted value must be
documented against the primary source and accompanied by regenerated products
and explicitly reviewed manifests.

Current dataset membership and counts are described in
[`../guides/versioning.md`](../guides/versioning.md), with source-specific
extraction decisions in [`../source-notes/`](../source-notes/).

## External A2744-QSO1 comparison

The direct estimate is evaluated as an external, fixed-assumption comparison in
[`external_direct_mass_comparison.csv`](../../results/v3/selected_samples/tables/external_direct_mass_comparison.csv).
It neither adds an object nor replaces the canonical virial measurement. Its
interval crosses the reference growth threshold, so frozen membership does not
prevent evaluating the measurement's scientific implication. Adopting it as a
preferred canonical value would require an explicit membership and method-policy
revision, with identity and error semantics reviewed.

The Baccus published-value sensitivity similarly tests measurement revisions
without admitting new rows or changing classification and selection policies.
