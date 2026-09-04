# Reproduction and reviewed artifact updates

Run the numbered notebooks in order using the pinned dependencies. The final
atlas step compares regenerated products with an independent baseline before
refreshing release hashes. It checks CSV values with the documented numerical
tolerance and PNG RGB channels with an absolute tolerance of 2 out of 255 at
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
The bounded comparison needs confirmation on Linux; local agreement alone does
not establish that the particular CI difference falls within this bound.

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
