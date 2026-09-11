# Reproduction and reviewed artifact updates

Run the numbered notebooks in order using the pinned dependencies. The final
atlas step compares regenerated products with an independent baseline before
refreshing release hashes. It checks CSV values with the documented numerical
tolerance and PNG RGB channels with an absolute tolerance of 3 out of 255 at
**every channel of every pixel**, ignoring encoding metadata. This narrow bound
allows rasterization roundoff between platform builds of the pinned renderer.
Dimensions and transparency must match exactly. There is no image averaging,
resizing, alignment, or blurring, so a large gallery cannot hide a local mismatch.
Use `--exact-pixels` with `src.internal.verify_regenerated_artifacts` to require
exact RGB when comparing identical rendering environments. Larger differences
still fail with their maximum channel error and location; inspect them rather
than automatically increasing the tolerance. This image check supplements the
independent numerical checks and does not establish scientific correctness.

The Linux run at commit `ec3d3c3` passed regression, provenance, and numerical
reproduction checks, then failed the former exact-pixel gallery comparison.
A subsequent [Linux diagnostic run](https://github.com/nniickels/highz-accretion-atlas/actions/runs/33928990910)
measured all 1,180 regenerated images: no missing images or dimension changes;
10,969,233,718 RGB channels were identical, 839,325 differed by one level,
3,755 by two, and just three by three. No channel differed by more than three;
the maximum per-image RMS difference was 0.017841 on the 0–255 scale. The
three-level bound comes from this complete measured comparison, not successive
unbounded tolerance increases. A four-level change to even one channel still
fails, regardless of image size. Numerical and transparency checks remain strict.
CI retains an aggregate error reporter on failure so future rendering changes
can be measured without uploading images or accepting fresh hashes.

By default the baseline is the canonical products exported from Git HEAD. In CI,
`HIGHZ_BASELINE_ROOT` points to the original checkout while the notebooks run in
a separate archive workspace. Never point it at the regenerated workspace.
The baseline must contain all canonical artifacts.

For intentional scientific or metadata updates, first inspect the differences
against HEAD and document their reason. Only then explicitly run
`.venv/bin/python -m src.internal.dataset_manifests` and
`.venv/bin/python -m src.internal.verify_source_provenance --write` where needed.
An intentional change will fail reproduction against the old commit until a
reviewed baseline containing the change is committed or supplied separately.
Hash refresh alone is not evidence of reproducibility.

`.venv/bin/python -m src.internal.verify_versions` independently rebuilds
catalogue, science, and per-object compatibility values. To verify regenerated
figures as well, run the complete notebook workflow; comparing stored files
without regeneration only checks baseline agreement. Source-value verification
has its separate, explicitly bounded scope in `data/validation/README.md`.

## Scientific identity gate

`python -m src.internal.verify_redshift_identity` verifies source fields and reports
open identity cases. `--require-resolved` is the strict full-catalogue identity
gate; it currently fails for three groups. Resolving them is required before
readmission or a final unique-object census. The manuscript instead excludes
all six affected records and verifies the 224/234-object samples through
`src.internal.publication_selection`. These exclusions permit the conservative
analysis without claiming identity resolution. Reproduction success alone
does not resolve the groups.
See the [audit record](../source-notes/redshift-identity-audit.md).

## Reviewed correction of 7 September 2026

Two independently reviewed duplicates are now assembled under shared physical
and host IDs, retaining all source measurements and the mass-bearing preferred
rows. v3 changes from 340 to 338 object records and from 339 to 337 host records.
Four obsolete mass-free panels are removed; v1/v2 membership is unchanged.
All versions replace the inaccurate uncertainty-model label with
`equal_side_half_normal_in_log_mbh`, without changing draws or numerical growth
results. Updated counts, identity metadata and summary images are intentional
changes against the prior commit; refreshed manifests describe this reviewed
revision. Regeneration must reproduce this revision in an independent workspace.
Three unresolved identity groups remain subject to the strict full-catalogue
identity gate; the conservative manuscript exclusion check is separate.

## Manuscript reproduction and clean builds

The independent baseline comparison includes generated `paper/analysis/*.csv`,
`paper/analysis/*.tex`, and `paper/figures/*.{png,pdf}`, as well as the canonical dataset
products. CSVs use the shared numerical tolerance; generated LaTeX fragments
must match byte for byte; figures use the same per-channel bound and exact alpha
as the atlas. Source README files and the compiler-dependent manuscript PDF are
outside this artifact set. Missing or unexpected manuscript outputs fail the
comparison. Comparing a workspace with itself, including through a symlink,
is rejected by the comparison API as well as the command line.

CI removes these generated outputs **only in its disposable archive workspace**
before executing notebooks 00--04. The original checkout remains the independent
baseline. This ensures inherited output files cannot hide an incomplete rebuild.
The manuscript is then compiled from that regenerated workspace, with three
LaTeX passes and a check for unresolved references or table-width changes. A
successful compilation in the original checkout would not verify regenerated
manuscript inputs. PDF bytes are not compared between Tectonic and pdfLaTeX.

`requirements-lock.txt` pins the numerical/rendering dependency closure, including
Matplotlib's font and layout dependencies. The notebook lock pins its direct
Jupyter dependencies; it is not a complete transitive lock of the notebook UI.
`requirements-build-lock.txt` pins the explicitly declared setuptools backend.
For the same package build used by CI, install both runtime and build requirements:

```bash
.venv/bin/python -m pip install -r requirements-notebook-lock.txt -r requirements-build-lock.txt
SOURCE_DATE_EPOCH=1788393600 .venv/bin/python -m pip wheel . --no-deps --no-build-isolation --wheel-dir=/tmp/highz-wheels
```

These changes strengthen what a passing reproduction run establishes; they do
not close the separate scientific identity audit or alter the adopted masses.

Validation on 7 September 2026 used a disposable archive of manuscript commit
`664a985`, overlaid with these reproduction fixes. All 1,285 generated artifacts
were removed before notebooks 00--04 ran; the independent comparison of the
regenerated outputs passed. The final notebook passed all 92 tests, source-value
and provenance checks, manuscript checks, and v1/v2/v3 contracts. Rebuilding the
PDF with the same Tectonic compiler and epoch produced the exact committed bytes
(SHA-256 `61cae8a6e779b18794515dea1e4275432167d924643746ce81ac569f5a69bee1`).
Two builds with the pinned setuptools backend and epoch produced identical
wheels. This is local macOS/Python 3.12 validation; Linux CI executes the updated
workflow independently and uses pdfLaTeX for compilation.

## Manuscript tooling repair of 11 September 2026

The regression suite caught three integration failures after the AAS citation
update and appendix-figure additions. Citation checks now recognize natbib
commands and optional bibliography labels; the independent target-table check
separates source citations from object names while retaining all numerical and
ordering assertions. Bibliography and early-start helpers live in `src/internal/`,
leaving `scripts/` for the five public workflow notebooks.

Notebook 02 now regenerates the appendix's early-start vector figure. Generated
`paper/figures/*.tex` files are included in clean-output removal and exact-byte
baseline comparisons. A regression check confirms that changed vector-figure
content is rejected. No numerical baseline or image tolerance was changed.

Validation completed with all five notebooks executed in a disposable archive
after removing all 1,289 generated artifacts. The independent baseline
comparison passed, as did all 93 regression tests, provenance, source-value,
publication-selection and version checks. The pinned package build passed and
includes all relocated helpers. Tectonic compiled the manuscript from the
regenerated inputs to the same PDF bytes as the committed version. This is
local macOS validation; Linux CI still runs its own checks and pdfLaTeX build.

## Pre-rendered manuscript figures

All seven manuscript figures now have deterministic Matplotlib PDF exports
(without creation/modification timestamps), plus PNG previews. Notebook 02
regenerates both formats. The reproduction gate compares PDF bytes and PNG
pixels; Figure 7 no longer requires PGFPlots during manuscript compilation.
Earlier references above to a generated TeX figure describe the previous format.

Local validation passed all 94 tests and independently regenerated all 14
manuscript PNG/PDF exports with matching pixels/bytes. A same-machine Tectonic
build comparison took 4.39 seconds for the previous source and 0.88 seconds for
the optimized source; these are local timings, not Overleaf measurements.
The manuscript PDF decreased from 3,104,922 to 638,660 bytes.
