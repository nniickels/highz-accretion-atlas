# Catalogue admission and identity record

The full catalogue contains 252 broad-line AGN, 49 narrow-line candidates,
30 photometric candidates, ten high-ionization candidates, and two X-ray
candidates. Preferred-row evidence labels comprise 217 secure, 41 probable,
84 candidate, and one disputed classification. These full-catalogue counts
precede the manuscript exclusions.

## Source-admission checks

The NEXUS, COSMOS-3D, and Seven Wonders source sets contribute 30
measurements and 29 object records; their [extraction note](nexus-cosmos3d-seven-wonders-extraction-notes.md)
records the source tables. NX10835 lies 0.066 arcsec from an existing Mascia
identifier at consistent redshift, so the mass-bearing NEXUS measurement is
preferred for the same object. Other source additions and exclusions are listed
in the [source bibliography](../../data/sources.md).

The Scholtz et al. paper reports 42 objects, but its published table contains
41 rows. Exactly 21
table rows satisfy $z\geq4$; all are admitted. One is identity-linked to a
broad-line object, yielding 20 distinct narrow-line candidates from that source.
JADES-NS-GS00099671 is retained with its published host and bolometric
observables but without a black-hole mass estimate.

## Preferred measurements and identity exclusions

Measurement, object and host identifiers link each value to its location in
the source, publication version and quoted uncertainty. We choose preferred
measurements using the source assessments.
The CEERS-2782 group uses RUBIES-EGS-50052 because the source prefers its
higher-signal-to-noise spectrum over the slit-loss measurement. NX10835 uses
the newly available NEXUS mass; UHZ1 uses the later full-dataset evidence
assessment and remains outside numerical growth inference. The measurement--object
link table records each choice and its reason.

Before the conservative identity exclusions, there are 248 eligible measurements
and 241 preferred objects: 240 Balmer-line and one UV single-epoch virial masses.
The method-defined primary subset has 237 measurements and 230 objects.
The six excluded records link to seven admitted measurements; the three with
eligible masses are GDS_1210_9515, GS-8083 and GS-10013704. All three otherwise
pass the primary cuts. The other three excluded records lack eligible masses.
These records remain excluded until their identities can be resolved.
The open groups are Baccus GDS_1210_9515 versus JADES GS-8083,
GS-10013704 versus Scholtz 99671, and Scholtz 16745 versus 208643.
The first requires target/spectral and preferred-mass reconciliation;
the latter two require imaging and aperture checks.
The manuscript evidence policy additionally places four tentative JADES detections
in the exploratory sample only. The final samples contain 223 primary objects
and 238 expanded objects: fourteen additional candidates and GN-z11. Output
fields call the expanded sample `exploratory`. MACS0416-Y1 is one of the
expanded-only candidates; the four tentative JADES detections remain outside
the primary sample. Policies are
recorded in `data/publication/evidence_selection.json` and `data/publication/identity_exclusions.json`.
All original measurements and catalogue flags remain available.

## Measurement revision and validation coverage

In the comparison with the published Baccus Table 1 measurements, 32 central
masses change by −0.10 to +0.04 dex. The manuscript reports the threshold-count
and ranking comparisons, including the treatment of unmatched records.

Independent source checks cover all admitted mass/error fields, 355 central
redshifts and 328 available coordinate pairs. Twenty-seven rows lack coordinates.
Validation of redshift uncertainties, full posteriors and auxiliary observables
is incomplete.
