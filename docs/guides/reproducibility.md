# Reproduction and reviewed artifact updates

Run the numbered notebooks in order using the pinned dependencies. The final
atlas step compares regenerated products with an independent baseline before
refreshing release hashes. It checks CSV values with the documented numerical
tolerance and PNG pixels exactly, ignoring encoding metadata. Renderer or font
changes can therefore fail the pixel gate even when the science is unchanged;
inspect any such difference before accepting it.

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
