# Codex Prompts for Updating the Overleaf Draft

Use these prompts sequentially. They assume the current pasted Overleaf draft is available at:

`C:\Users\nicol\OneDrive\coding\projects\Dayal\highz-accretion-atlas\.codex_tmp\overleaf_draft_from_docx.tex`

The goal is to turn the existing Introduction/Background Theory draft into a concise, publish-ready paper draft that covers the v1 methods and first results without overclaiming. Treat v1 as a controlled pilot catalogue, not a complete population study.

## Prompt 1: Orient to the Draft and Repo

Read the LaTeX draft at `.codex_tmp/overleaf_draft_from_docx.tex` and inspect the repository context before editing. Use `README.md`, `docs/catalogue-schema.md`, `docs/getting-started.md`, `docs/model-menu.md`, `data/sources.md`, `src/standardize_data.py`, `src/models.py`, `src/scoring.py`, `scripts/process_data.py`, `scripts/v1_evaluate.ipynb`, and the CSV/PNG files in `results/`.

Create an updated LaTeX file at `.codex_tmp/overleaf_draft_v1_methods_results.tex`. Preserve the existing tone and mathematical setup where it is accurate, but make the paper more concise and publish-ready. Do not invent results, citations, or analysis not present in the repo. Add Methods and Results sections that accurately describe the v1 catalogue, growth model, scenario grid, generated figures, and headline results. Keep caveats explicit: v1 uses one homogeneous JADES broad-line AGN source class from Juodzbalis et al. (2025), with 23 objects after filtering to `z >= 4`.

## Prompt 2: Tighten the Existing Front Matter

Edit the title, abstract, and opening sections for clarity and concision. The abstract should include Aims, Methods, Results, and a short conclusion-style sentence. The Results sentence should be cautious and quantitative: v1 contains 23 JADES broad-line AGN at `4.133 <= z <= 8.913`, with `log10(M_BH/Msun)` from 6.06 to 8.57. Under the baseline fixed-seed calculation with `epsilon = 0.1`, `z_seed = 30`, and no merger boost, all objects are reachable with `10^4` or `10^5 Msun` seeds at average `f_Edd <= 1`, while `10^2 Msun` seeds require super-Eddington average growth for 5 of 23 objects.

Keep the abstract compact. Do not overstate this as evidence for or against a seed population; describe it as a transparent compatibility diagnostic.

## Prompt 3: Add a Catalogue Methods Section

Add a `\section{Methods}` with a subsection on catalogue construction. Use the repository facts below:

- v1 ingests `data/raw/v1_raw.csv` and writes `data/processed/v1_processed.csv` via `python -m scripts.process_data`.
- Raw v1 has 34 rows; the processed v1 catalogue has 23 rows after applying `redshift >= 4`.
- All processed v1 rows are JADES broad-line AGN from `juodzbalis25_jades_blagn`.
- Source registry citation: Juodzbalis et al. (2025), "JADES: comprehensive census of broad-line AGN from Reionization to Cosmic Noon revealed by JWST", MNRAS, arXiv:2504.03551.
- Extracted values include redshift, black-hole mass, bolometric luminosity, Eddington ratio, and host stellar mass where available.
- MBH method is `single-epoch-virial-halpha` for all 23 objects.
- Host stellar masses use BEAGLE spectral decomposition when available; 19 of 23 have host stellar masses.
- Bolometric luminosities and reported Eddington ratios are available for all 23 objects.
- Lensing magnification is missing for all 23 objects and is explicitly flagged.
- The standardizer validates required identifiers, numeric fields, provenance fields, unique `measurement_id`, optional-field missingness, and positive cosmic time.
- It stores `missing_*` flags, interpretation tags, quality flags, and source provenance.
- Quality flags are 18 robust and 5 tentative.

Write this as compact prose, with a small table if useful. Avoid a procedural README tone; make it read like a manuscript Methods section.

## Prompt 4: Add a Growth Model and Scenario Grid Methods Section

Add a Methods subsection describing the growth model and derived diagnostics. Use the existing equations, but align notation with the implementation in `src/models.py`:

`M_BH(t_obs) = M_seed exp[f_Edd ((1 - epsilon) / epsilon) Delta_t / t_Edd]`

where `t_Edd = c sigma_T / (4 pi G m_p) ~= 0.45 Gyr`, `Delta_t = t(z_obs) - t(z_seed)`, and v1 uses flat Lambda-CDM with `H0 = 70 km/s/Mpc`, `Omega_m = 0.3`, and `Omega_Lambda = 0.7`.

Describe these v1 assumptions:

- Fixed seed redshift: `z_seed = 30`.
- Seed model ranges: light Pop III `10^1-10^2 Msun`, intermediate/cluster `10^3-10^4 Msun`, heavy DCBH-like `10^4-10^6 Msun`, PBH `10^2-10^6 Msun`.
- Interpretation variants: baseline, MBH shifted by `-0.3 dex`, MBH shifted by `+0.3 dex`, and a 20 percent AGN-contamination correction to host stellar mass.
- Growth configurations: `f_Edd=1, epsilon=0.1`; `f_Edd=0.3, epsilon=0.1`; `f_Edd=2, epsilon=0.05`; and `f_Edd=1, epsilon=0.1, B_merge=2`.
- Fixed-seed required-`f_Edd` configurations: seed masses `10^2`, `10^4`, and `10^5 Msun`; `epsilon=0.1` no boost, `epsilon=0.05` no boost, and `epsilon=0.1` with `B_merge=2`.
- The per-object parameter maps use `log10(M_seed/Msun)` from 1.0 to 6.2 and average `f_Edd` from 0 to 3, with `epsilon=0.1` and `z_seed=30`.

Explain the inverse quantities: required average `f_Edd` for a chosen seed mass, and required seed mass for a chosen accretion history. State that labels such as "compatible" are diagnostics of exact scenario assumptions, not posterior probabilities.

## Prompt 5: Add a v1 Sample Properties Results Section

Add `\section{Results}` and start with a subsection summarizing the v1 catalogue. Use these numbers from `data/processed/v1_processed.csv`:

- `N = 23` processed objects.
- Redshift range: 4.133 to 8.913; median 5.480.
- Cosmic age at observation: 0.545 to 1.458 Gyr.
- `log10(M_BH/Msun)` range: 6.06 to 8.57; median 7.33.
- Reported Eddington-ratio range: 0.015 to 0.38; median 0.11.
- Host stellar mass is available for 19 objects, spanning `log10(M*/Msun) = 7.40` to 10.93.
- For the 19 objects with host masses, `log10(M_BH/M*)` has median -1.73 and spans -3.23 to -0.07.

Frame these as descriptive sample properties. Mention that this is a homogeneous broad-line AGN pilot sample, which reduces cross-paper heterogeneity but does not sample all known high-redshift accretion candidates.

## Prompt 6: Add Baseline Growth-Requirement Results

Add a Results subsection for the baseline required average Eddington fractions, using `results/v1_required_fedd_by_seed_mass.csv`. For the baseline case `epsilon=0.1`, `z_seed=30`, and no merger boost:

- For `10^2 Msun` seeds: median required `f_Edd = 0.654`, 16th-84th percentile 0.495-1.056, range 0.374-1.376. 18 of 23 objects are at or below Eddington; 5 require super-Eddington average growth.
- For `10^4 Msun` seeds: median required `f_Edd = 0.400`, 16th-84th percentile 0.304-0.671, range 0.190-0.860. All 23 are at or below Eddington.
- For `10^5 Msun` seeds: median required `f_Edd = 0.272`, 16th-84th percentile 0.196-0.479, range 0.098-0.601. All 23 are at or below Eddington.

Identify the most demanding baseline fixed-seed objects:

- For `10^2 Msun` seeds, the highest required `f_Edd` values are GS-20057765 at `z=8.913` with `f_Edd=1.376`, GS-20030333 at `z=7.891` with `f_Edd=1.150`, and GS-164055 at `z=7.397` with `f_Edd=1.081`.
- For `10^4 Msun` seeds, the highest are GS-20057765 (`0.860`), GN-38509 (`0.752`), and GS-20030333 (`0.726`).
- For `10^5 Msun` seeds, the highest are GS-20057765 (`0.601`), GN-38509 (`0.587`), and GS-20030333 (`0.514`).

Make the interpretation precise: light seeds are not ruled out, but the earliest/more massive objects demand sustained near-Eddington or super-Eddington average growth under the v1 assumptions. Intermediate/heavy seeds reduce the required mean accretion intensity.

## Prompt 7: Add Required Seed-Mass and Compatibility Results

Add a Results subsection summarizing `results/v1_required_mseed_by_growth_assumption.csv` and `results/v1_sample_summary.csv`. Use these baseline values:

- For `f_Edd=1`, `epsilon=0.1`, no boost: median required `log10(M_seed/Msun) = -0.714`, 16th-84th percentile -3.180 to 2.290, max 3.456. This means many objects would be overproduced by strict constant Eddington growth from conventional seeds, so the diagnostic should be read as an exact-history requirement, not a literal seed-mass claim.
- For `f_Edd=0.3`, `epsilon=0.1`: median required `log10(M_seed/Msun) = 4.784`, 16th-84th percentile 4.037 to 5.956, max 6.746. The most demanding objects are GN-38509 (`log M_seed=6.746`), GS-20057765 (`6.168`), and GS-164055 (`6.067`).
- For `f_Edd=1`, `epsilon=0.1`, `B_merge=2`: median required `log10(M_seed/Msun) = -1.015`, max 3.155.
- For `f_Edd=2`, `epsilon=0.05`: the required seed masses are formally below physical seed scales for all objects; phrase this as the configuration having more than enough growth capacity, not as a physical seed-mass result.

Compatibility fractions for baseline interpretation:

- `f_Edd=1`, `epsilon=0.1`: light Pop III 0.043, intermediate 0.043, heavy DCBH 0.000, PBH 0.217.
- `f_Edd=0.3`, `epsilon=0.1`: light Pop III 0.000, intermediate 0.087, heavy DCBH 0.696, PBH 0.826.
- `f_Edd=2`, `epsilon=0.05`: all listed seed-model fractions are 0.000 because the exact required seed masses fall below the model ranges; explicitly explain that this is a limitation of exact-match scoring.
- `f_Edd=1`, `epsilon=0.1`, `B_merge=2`: light Pop III 0.087, intermediate 0.043, heavy DCBH 0.000, PBH 0.174.

Keep this section concise. The key message is that the same objects move between "easy" and "demanding" regimes depending on whether one solves for average accretion at fixed seed mass or solves for exact seed mass at fixed accretion history.

## Prompt 8: Add Figures and Captions

Add LaTeX figure environments for the generated figures if the paths work in the Overleaf project or can be copied there:

- `results/v1_mbh_vs_redshift_growth_tracks.png`
- `results/v1_sample_compatibility_summary.png`
- Use one representative parameter map from `results/v1_parameter_maps/`, preferably `v1_parameter_map_gs20057765-juodzbalis25.png` for the most demanding high-redshift case and/or `v1_parameter_map_gn38509-juodzbalis25.png` for the most massive v1 black hole.

Write manuscript-quality captions:

1. Growth tracks: points are v1 black-hole masses with reported uncertainties; curves start at `z_seed=30`; color marks seed mass and line style marks constant average `f_Edd`; objects above a curve require heavier seeds, higher mean accretion, lower radiative efficiency, or extra growth channels under v1 assumptions.
2. Compatibility summary: left panel is fraction of v1 objects whose exact required seed mass falls inside each seed-model range for a given growth assumption; right panel is median and 16th-84th percentile required average `f_Edd` for fixed seed masses in the baseline `epsilon=0.1` case. State that these are diagnostics, not probabilities.
3. Parameter map: color gives predicted `log10(M_BH/Msun)` over seed mass and average `f_Edd`; solid contour matches observed mass; dashed contours show mass uncertainty; vertical lines mark `10^2`, `10^4`, and `10^5 Msun` seed thresholds; horizontal line marks `f_Edd=1`.

Use `\includegraphics[width=\linewidth]{...}` unless the existing LaTeX style suggests otherwise. If the Overleaf path is unknown, leave clear comments indicating where the PNGs should be uploaded and what filenames to use.

## Prompt 9: Add Discussion, Limitations, and Next Steps

Add a short Discussion section that interprets v1 without overclaiming:

- The v1 sample is homogeneous and source-tracked, which is useful for testing the pipeline and avoiding cross-paper convention mixing.
- It is not yet a census of high-redshift accretion candidates.
- Current results show that seed/accretion requirements are sensitive to assumptions about seed mass, radiative efficiency, average Eddington fraction, seed redshift, and mergers.
- Reported host masses are useful but vulnerable to AGN-contamination systematics; v1 carries a 20 percent host-contamination interpretation variant, but the headline growth results are primarily driven by black-hole mass and redshift.
- Single-epoch virial H-alpha masses carry systematic uncertainties; v1 includes plus/minus 0.3 dex MBH variants as a first-order check.
- Future versions should add additional papers/object classes, duplicate matching, uncertainty propagation via Monte Carlo sampling, and cross-paper measurement comparisons.

Keep the Discussion short and manuscript-like. Do not add speculative claims about primordial black holes or seed channels beyond what is needed to interpret the diagnostics.

## Prompt 10: Final LaTeX QA and Consistency Pass

Do a final QA pass on `.codex_tmp/overleaf_draft_v1_methods_results.tex`:

- Ensure all equations compile and notation is consistent: `M_{\rm BH}`, `M_{\rm seed}`, `f_{\rm Edd}`, `\epsilon`, `z_{\rm seed}`, `\Delta t`, `B_{\rm merge}`.
- Ensure all numeric claims match the repo outputs exactly.
- Remove README-style phrasing and future-section comments.
- Add any needed packages, such as `booktabs`, only if used.
- Ensure figure paths are either valid relative paths or clearly marked Overleaf upload placeholders.
- Ensure the bibliography includes Dayal (2024) and Juodzbalis et al. (2025), plus any other citations already mentioned in the text.
- Keep the manuscript concise. Avoid making the draft longer just because more data are available.
- If possible, run a local LaTeX compile or at least a syntax check. If not possible, report that compilation was not run.

Return a short summary of the new/changed sections and list any remaining assumptions or missing citation details.
