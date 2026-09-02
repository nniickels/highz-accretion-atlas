# Multi-class eligibility and mass comparability

This is the active comparison contract for heterogeneous dataset v3. It keeps
identity, evidence, phenotype, mass inference, and ranking eligibility as
separate questions.

Controlled object classes include broad-line AGN, luminous-quasar comparison
objects, narrow/high-ionization-line candidates, and X-ray candidates. Lensing
is a property, and `lrd` is a phenotype; neither is an object class.

Mass-comparability groups distinguish Balmer and UV single-epoch virial masses,
direct methods, proxy or assumed-Eddington masses, and no-numeric-mass cases.
Statistical errors and calibration systematics remain separate. Limits and
conditional values are never converted into apparently measured canonical
masses.

A row can enter numerical growth diagnostics only with a supported mass,
redshift, reproducible method, resolved identity, and resolved lensing
treatment. Primary comparisons additionally require `secure` or `probable`
evidence and a method appropriate to the comparison. Global ranks are
navigation aids; demographic interpretation must remain within compatible
classes, methods, and selection functions.

The public contract is checked by `src.internal.verify_versions`. Historical
source-admission implementations required for reconstruction are isolated under
`src/internal/compatibility/` and are not public dataset interfaces.
