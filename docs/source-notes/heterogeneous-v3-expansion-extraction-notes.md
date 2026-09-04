# Heterogeneous v3 expansion extraction notes

Reviewed and implemented 2026-09-03. The identity-audited rows documented here
are admitted to v3 only. The separate same-class BLAGN expansion of v2 is
documented in `baccus26-fei26-v2-expansion-extraction-notes.md`.

This revision retains only datasets that contribute at least one demonstrated
new, JWST-identified z >= 4 candidate after the screening completed here.

The pre-expansion v3 object table contained 174 objects: 152 broad-line AGN, 20
narrow-line candidates, GN-z11 as the sole high-ionization-class object, and
UHZ1 as the sole X-ray-class object. The narrow-line family already contains
high-ionization evidence. Consequently, the exclusive `object_class` counts
are not counts of all objects with each evidence channel.

The screening boundary is the existing JWST-identification scope and z >= 4.
Catalogue inclusion and eligibility for numerical growth calculations are
separate decisions. The admission decisions recorded here apply the existing
catalogue policies to the source tables.

Here, `JWST-identified` means that JWST data supplied the initial object-level
accretion/AGN identification, or were essential to associating another-band
detection with the high-redshift galaxy. Merely receiving JWST follow-up does
not qualify an AGN that was already identified from pre-JWST data.

## Scope assignment

“Plottable” below means eligible for the current numerical mass-growth analysis,
which requires a source-published BH mass that can be used without assuming the
same Eddington ratio being tested. Ranges, upper limits, and masses inferred from
an assumed Eddington ratio remain useful contextual graphics but do not count as
growth-plottable objects.

None of the catalogues documented in this note qualifies for the **v2
scientific scope**. V2 is the comparable JWST broad-line AGN dataset; these
catalogues either lack object-level BH masses or add heterogeneous evidence or
mass-method strata. Mascia's broad-line-emitter catalogue is not a v2 exception
because it does not publish object-level BH masses and remains agnostic about
the central engine. Dataset assignment is source-level: a heterogeneous source
belongs to v3 even if one of its rows resembles a v2 object.

The appropriate additions all belong to the **v3 scientific scope**:

| Source | Admitted new objects | New growth-plottable objects | Object type |
| --- | ---: | ---: | --- |
| Chisholm: GN-42437 | 1 | 0 | Narrow-line, very-high-ionization [Ne V] candidate |
| Tang high-ionization survey | 3, including 2 tentative | 0 | Narrow high-ionization N V/[Ne IV]/[Ne V] candidates |
| Mazzolari CEERS selection | 25 after 2 known overlaps | 0 | Narrow-line AGN candidates; 5 new rows carry high-ionization/He II selection evidence |
| MEOW | 12 source-new rows after catalogue crossmatch | 0 | MIRI SED-selected obscured AGN and composite candidates |
| SMILES | 19 JWST-only rows after catalogue crossmatch | 0 | MIRI SED-selected obscured AGN candidates |
| GHZ9 | 1 | 0 | JWST-associated X-ray/UV AGN candidate |
| Zhang narrow-line LRDs | 5 after catalogue crossmatch | 0 | Narrow-line little-red-dot candidates |
| Chavez Ortiz: GHZ2 | 1 | 0 | Spectral/photometric-model AGN candidate |
| Mascia compact blue emitters | 8 after coordinate-redshift and alias review of 20 rows | 0 | Compact blue broad-line-emitter candidates |
| Treiber UNCOVER high-ionization sample | 2 new components after catalogue crossmatch | 0 | Narrow high-ionization-line candidates |
| Naidu: MoM-BH*-1 | 1 | 0 | Gas-enshrouded broad-Hbeta accretor candidate |

The admitted rows sum to 78 new physical objects. Nine objects have some contextual mass constraint:
GN-42437's method-dependent range, GHZ9's conditional estimate, five Zhang upper
limits, GHZ2's Eddington-ratio-dependent estimate, and MoM-BH*-1's
model/scattering-dependent range. None is eligible as a new canonical point in
the current growth calculations.

These labels describe which existing scientific dataset each family extends:
v2-scoped additions would flow into v3, while the families above extend v3 only.
The user-authorized heterogeneous expansion is implemented directly in v3 and
remains reproducible through the shared build pipeline.

## Admitted sources

### 1. Chisholm et al. (2024): GN-42437

**Admission role: high-ionization addition.** The z = 5.58724 source has
published [Ne V] emission and a narrow-line spectrum in a compact, low-mass
starburst host. Tables 3–4 provide line measurements and ratios. The paper
discusses approximate BH masses spanning log(MBH/Msun) ~ 5–7 through several
methods; these are not a single independently measured mass with a posterior.
The method-dependent estimates are retained separately and the canonical
growth mass is unset. The coordinate comparison found no nearby
pre-expansion catalogue entry.

[Primary paper](https://arxiv.org/abs/2402.18643)
([published article](https://doi.org/10.1093/mnras/stae2199)).

### 2. Tang et al. (2025): high-ionization NIRSpec survey

**Admission role: UV/neon high-ionization survey.** Tables 1–2 contain
line fluxes, limits, and equivalent widths for N V emitters CEERS-1025
(z = 8.7166) and CEERS-7902 (z = 6.9827). Appendix A adds tentative GS-81034
([Ne V], z = 5.3904) and GS-20025526 ([Ne IV], z = 7.9507), and revisits
GN-42437 and GN-z11. Preserve the unusual single-component N V identification
and the tentative neon detections explicitly.

CEERS-7902 is identified in the paper as RUBIES-55604: the current catalogue
already has RUBIES-EGS-55604. Treat this as new evidence for an existing
object. GN-z11 is also already present. CEERS-1025 and the two tentative GS
sources have no nearby match in the coordinate screen. The parent
spectroscopic sample is not admitted as AGN candidates.

[Source v2, accepted by ApJ](https://arxiv.org/abs/2505.06359v2);
[tables and Appendix A](https://arxiv.org/html/2505.06359v2).

### 3. Mazzolari et al. (2024): CEERS narrow-line selection

**Admission role: narrow-line expansion.** Appendix C/Table 3 has 52 entries;
my count of its tabulated redshifts gives **27 at z >= 4**. These include
CEERS-1019 and CEERS-1244, already represented in the catalogue. Thus even
before coordinate audit, this yields 25 additional objects.
Diagnostic selections include UV/high-ionization and optical auroral-line
methods; only rows with that explicit evidence are labelled high-ionization detections.

The table supplies redshift, diagnostic, luminosity, attenuation, stellar
mass, SFR, and tentative flags, but no canonical BH mass. Coordinates were
recovered from the source survey, with all asterisks and missing values retained.

[Published paper](https://doi.org/10.1051/0004-6361/202451860);
[Table 3](https://arxiv.org/html/2408.15615v3#A3).

### 4. Leung et al. (2026): MEOW

**Admission role: obscured and composite systems after row-level discovery audit.** Table 3 lists 16 sources at
z ~ 4.5–7.2, with coordinates, redshift provenance, luminosities, AGN fractions,
and aliases. The analysis separates ten AGN-dominated from six composite
systems. Keep the MIRI SED selection distinct from spectroscopic AGN evidence.
No BH mass column is supplied.

Table 3 agrees with the abstract in listing 12 spectroscopic and four
photometric redshifts. The paper also says 12 of the 16 are newly identified;
admission is restricted to those rows. GNz7q is explicitly excluded from new
membership because it was identified from archival HST and other pre-JWST data
in 2022. Existing GOODS-N BLAGN and SMILES overlaps were reviewed by coordinate
and alias; the paper's newly identified count is not assumed to be the number
new to this catalogue.

[Submitted ApJ preprint](https://arxiv.org/abs/2607.02666v1);
[Table 3](https://arxiv.org/html/2607.02666v1).

### 5. Lyu et al. (2024): SMILES MIRI-selected candidates

**Admission role: infrared evidence with a row-level pre-JWST exclusion.** The paper's high-redshift subsample
contains 20 AGN candidates at z > 4, reaching ~8.4. Table 2 is available in
machine-readable form and includes coordinates, redshift type, luminosity,
stellar mass, and selection codes. These add SED-selected obscured candidates,
not automatically narrow-line or spectroscopically confirmed AGN.

Crossmatch against JADES/FRESCO and MEOW, preserve photo-z versus spec-z, and
retain SED-model ambiguity. Do not derive canonical BH masses from luminosity
by assuming an Eddington ratio. The SMILES general photometry/spectroscopy
release is useful supporting data, not itself a table of confirmed AGN.
The paper reports that 19 of its 20 high-z candidates are identified only by
the JWST/MIRI SED analysis and one was already selected by pre-JWST methods.
The extraction admits the 19 JWST-only rows and excludes the remaining object,
whose original identification does not satisfy the project boundary.

[Primary paper](https://arxiv.org/abs/2310.12330);
[Table 2 and selection discussion](https://arxiv.org/html/2310.12330v2);
[MAST SMILES data](https://archive.stsci.edu/hlsp/smiles).

### 6. Napolitano et al. (2025): GHZ9

**Admission role: combined X-ray and UV evidence at z = 10.145.** Table 1 supplies
UV/optical line measurements and limits; the analysis also discusses Chandra
association and lensing. [Ne IV] and [Ne V] are upper limits, so GHZ9 must not
be labelled a neon-line detection. Its UV diagnostics admit mixed stellar
and AGN contributions.

Published luminosity-based BH estimates assume an accretion rate relative to
Eddington; they remain conditional estimates rather than an independent
canonical mass used to test that same assumption. The extraction preserves X-ray association,
spectral-model, and magnification uncertainties.

[Primary paper](https://arxiv.org/abs/2410.18763);
[published record](https://doi.org/10.3847/1538-4357/ade706).

### 7. Zhang et al. (2025/2026): narrow-line little red dots

**Admission role: exploratory phenotype extension.** The revised Table 1 lists
five objects at z = 4.985–6.785, rather than requiring broad Balmer emission.
They form a narrow-line LRD subset with explicit alternatives involving
compact star formation. The revised mass discussion treats the BH estimates
as conditional upper limits; these must not become measured point masses.

The extraction uses v2, whose revision specifically changes the mass-upper-limit analysis.
Source-native measurements are in Tables 1–2, and the authors release data
and code. LRD phenotype, spectroscopic type, and accretion evidence are stored
separately so the candidate interpretation is not promoted to secure AGN
evidence.

[Accepted ApJ version](https://arxiv.org/abs/2506.04350v2);
[author data/code](https://github.com/Zijian-astro/NL-LRD-2025-Data).

### 8. Chavez Ortiz et al. (2025): GHZ2

**Admission role: exploratory candidate at z = 12.34.** Joint JWST spectral and
photometric modelling identifies a possible AGN contribution, adding a new
object rather than measurements for an existing catalogue member. The quoted
BH mass assumes an Eddington ratio of 0.5 and has a much larger systematic
uncertainty than its formal error. Store it as a conditional estimate, not an
independent canonical mass or numerical growth anchor.

The 6 August 2026 v2 source archive was rechecked on 3 September 2026. It
retains the same archive SHA-256 as the previously downloaded unversioned
archive and reports the context mass as log(MBH/Msun) = 7.20 +/- 0.04 at the
assumed Eddington ratio, with about 1 dex systematic uncertainty.

[Primary preprint v2](https://arxiv.org/abs/2511.03035v2).

### 9. Mascia et al. (2026): compact blue broad-line emitters

**Admission role: v3-scoped broad-line candidate phenotype.** The JWST/NIRSpec and
NIRCam selection returns 20 compact blue broad-line emitters at 4 <= z <= 7.
A coordinate-redshift and alias comparison to the pre-expansion v3 objects matches
12 rows, including `GS_3073 = ZS7`, and leaves **8 new objects**. The paper publishes redshifts,
coordinates, continuum slopes, compactness, Balmer decrements, and line
measurements, but no object-level BH masses. Its photoionization discussion is
deliberately agnostic about whether every central engine is an accreting BH, so
new rows are represented as broad-line-emitter candidates rather than
canonical v2 broad-line AGN.

[Primary preprint and Table 2](https://arxiv.org/html/2608.25021v1).

### 10. Treiber et al. (2025): UNCOVER high-ionization candidates

**Admission role: heterogeneous high-ionization source.** The source catalogue
contains two components not already represented after object-level identity
review: UNCOVER-47584 at z = 4.474 and component 2 of UNCOVER-10646 at z =
8.511. Their NIRSpec high-ionization evidence is retained without inventing a
black-hole mass. The catalogue is heterogeneous and therefore belongs to v3 at
the source level.

[Published article](https://doi.org/10.3847/1538-4357/adc38f);
[source record](https://arxiv.org/abs/2409.12232).

### 11. Naidu et al. (2026): MoM-BH*-1

**Admission role: gas-enshrouded accretor candidate.** JWST spectroscopy
identifies broad Hbeta in MoM-BH*-1 at z = 7.7569. Its quoted black-hole mass
range depends on the source's obscuration and scattering model and remains a
contextual constraint rather than a canonical growth mass. The heterogeneous
source is therefore v3-only.

[Published article](https://doi.org/10.1038/s41586-026-10846-4).

## Implemented admission decisions

The admission includes GN-42437, Tang's object-level high-ionization
measurements, Mazzolari's z >= 4 subset, the identity-screened JWST rows from
MEOW and SMILES, GHZ9, the narrow-line LRDs, GHZ2, and the unmatched Mascia
rows. Narrow-line LRDs and GHZ2 remain exploratory extensions. The Mascia rows
form a candidate phenotype batch rather than a v2 mass-bearing BLAGN family.

Every family has an archived source version, deterministic extraction, explicit
limits and method assumptions, and reviewed object/host identities. Their
source metadata are recorded in `data/source_provenance_registry.csv`.

The positional identity screen used spherical separations to the pre-expansion v3
measurement coordinates. Nearest separations were 66.37 arcsec for CEERS-1025,
48.66 for GN-42437, 110.98 for GS-81034, and 49.97 for GS-20025526.
CEERS-7902 lies 0.716 arcsec from RUBIES-EGS-55604, with
consistent redshifts and an explicit published alias link. The admitted table
excludes reviewed aliases and overlaps rather than duplicating them.

The catalogue stores high-ionization evidence as an overlapping selection
channel, with sample size and mass availability explicit. These 78 additions
broaden evidence coverage; none adds a canonical numerical growth point. The
separate v2 BLAGN expansion initially raised the shared v3 numerical sample to
212 objects. The later final-completion sources documented separately raise it
to 237 objects.
