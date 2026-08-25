# Research-Grade Observational Atlas Roadmap

Purpose of this file:
- Preserve the full project roadmap for future Codex threads.
- Make it easy to remember what has been completed, what comes next, and what prompts to give Codex.
- Treat this project as a living final-paper / atlas project, not as a sequence of disposable reports.
- Use `.codex_tmp/catalogue-expansion-guide.md` as the current literature-reviewed companion for source priority, taxonomy, growth eligibility, and disputed-object handling (reviewed 2026-08-17).

Chosen project direction:
- Path B: observational atlas / follow-up triage.
- Main product: a source-tracked, uncertainty-aware atlas of high-redshift accreting black-hole candidates.
- Main scientific use: identify which objects are most informative for seed mass, accretion history, mass inference, and follow-up observations.
- Formation models are diagnostic tools, not claims of proof.

Working thesis:
> A reproducible, source-tracked, uncertainty-aware atlas of high-redshift accreting black-hole candidates can separate robust growth-challenging objects from interpretation-dependent ones, providing a ranked target list for follow-up and seed/accretion modeling.

Careful claim posture:
- Do say: "These objects are high-leverage under stated assumptions."
- Do say: "The ranking changes under mass-systematic and accretion-history assumptions."
- Do say: "This framework identifies which measurements most affect growth interpretation."
- Do not say: "Standard cosmology is broken."
- Do not say: "PBHs are required."
- Do not say: "Heavy seeds are proven."
- Do not say: "All high-redshift AGN are impossible in standard models."

## Completed Work

### Current release snapshot

- v5 is the current catalogue and science release: 106 measurements represent
  99 physical objects at `z >= 4`.
- v3 remains frozen as the JADES + Taylor comparison release.
- v4 now has five release-specific figures, separate detection-confidence and
  mass-reliability semantics, explicit identity decisions, and sensitivity for
  both multiply measured objects.
- v4.0.1 completes the maintenance gate with pinned dependencies, CI, release
  hashes, write-free reproduction, collision-safe ID allocation, reviewed
  manual identity assertions, and source-specific virial-method metadata.
- The Harikane measurement-version ingestion, first class-aware taxonomy
  scaffolding, primary-ranking gate, paper-facing ranking comparison, and
  effective two-state duty-cycle diagnostics are complete. The claim audit is
  recorded in `docs/v5-manuscript-claim-audit.md`; next specify class-specific
  eligibility rules before the first heterogeneous v6 source.
- The phase descriptions and prompt sequence below preserve project history;
  they are not all outstanding tasks.

### Project setup and framing
- Repository exists as `highz-accretion-atlas`.
- Project motivation is documented in the README.
- The basic problem has been framed around high-redshift JWST black holes, seed masses, radiative efficiency, average Eddington fractions, and available cosmic time.
- The project has moved from "make growth plots" toward "build an observational atlas and follow-up triage tool."

### v1 data foundation
- v1 uses one clean source class from one source paper: JADES broad-line AGN from Juodzbalis et al. 2025.
- Raw catalogue exists at `data/raw/v1_raw.csv`.
- Processed catalogue exists at `data/processed/v1_processed.csv`.
- Source registry exists at `data/sources.md`.
- Catalogue schema exists at `docs/catalogue-schema.md`.
- v1 raw file has 34 rows.
- v1 processed file filters to 23 objects at `z >= 4`.
- Processed v1 catalogue tracks:
  - measurement ID
  - object ID
  - coordinates
  - redshift
  - redshift kind
  - cosmic time
  - survey
  - object class
  - black-hole mass and uncertainties
  - black-hole mass method
  - host stellar mass and uncertainties
  - host mass method
  - bolometric luminosity and uncertainties
  - bolometric luminosity method
  - black-hole-to-stellar mass ratio
  - Eddington ratio
  - AGN contamination flag
  - lensing magnification fields
  - missing-field flags
  - interpretation tags
  - quality flag
  - project version
  - source key
  - source table
  - notes

### v1 catalogue checks already verified
- Processed sample size: 23 rows.
- Redshift range: `z = 4.133-8.913`.
- Black-hole mass range: `log10(MBH/Msun) = 6.06-8.57`.
- Host stellar mass range where present: `log10(Mstar/Msun) = 7.40-10.93`.
- Quality flags: 18 robust, 5 tentative.
- Missing host stellar mass: 4 objects.
- Missing bolometric luminosity: 0 objects.
- Missing Eddington ratio: 0 objects.
- Missing lensing magnification: 23 objects.

### Standardization pipeline
- `src/standardize_data.py` implements canonical raw fields, validation, numeric coercion, optional missingness flags, and processed output assembly.
- `scripts/process_data.py` regenerates `data/processed/v1_processed.csv` from `data/raw/v1_raw.csv`.
- Validation includes:
  - required canonical columns
  - required values
  - numeric parsing
  - unique `measurement_id`
  - `redshift >= 4` filtering
  - positive cosmic time
  - conditional method fields for host mass and luminosity
  - generated missing-value flags

### Growth model
- `src/models.py` implements the v1 black-hole growth model.
- Implemented model components:
  - Planck-style flat Lambda-CDM cosmic time
  - available growth time between `z_seed` and `z_obs`
  - Dayal-style exponential growth
  - predicted final black-hole mass
  - required seed mass for a target final mass
  - required average `f_Edd`
  - seed model ranges
  - thin-disk spin-dependent radiative efficiency
  - illustrative slim-disk effective efficiency above Eddington
  - merger boost as multiplicative final-mass factor
- Sanity checks have been run and passed:
  - zero accretion preserves seed mass
  - `B_merge = 2` adds `log10(2) = 0.301 dex`
  - spin efficiencies match expected Kerr thin-disk values
  - required seed mass and required `f_Edd` round-trip correctly

### Scoring / compatibility
- `src/scoring.py` implements:
  - seed mass compatibility score
  - required-`f_Edd` score
  - aggregate feasibility score
  - model-table scoring
  - summary statistics
- Important interpretation caveat:
  - A low compatibility score can mean a fixed growth scenario overgrows the object, not necessarily that the object is impossible.
  - Future descriptions should distinguish "exact-fit compatibility" from "physically impossible."

### v1 evaluation products
- `scripts/v1_evaluate.ipynb` builds v1 science outputs.
- Generated CSV outputs:
  - `results/v1_evaluation_table.csv`
  - `results/v1_required_fedd_by_seed_mass.csv`
  - `results/v1_required_mseed_by_growth_assumption.csv`
  - `results/v1_sample_summary.csv`
  - `results/v1_mass_compatibility_spin_merger_grid.csv`
- Generated figure outputs:
  - `results/v1_mbh_vs_redshift_growth_tracks.png`
  - `results/v1_sample_compatibility_summary.png`
  - per-object parameter maps in `results/v1_parameter_maps/`
  - per-object seed-redshift maps in `results/v1_seed_redshift_maps/`
  - one 3D seed-redshift test in `results/v1_seed_redshift_3d_tests/`
- Verified counts:
  - 8832 evaluation rows
  - 2208 required-`f_Edd` rows
  - 2208 required-seed rows
  - 384 sample-summary rows
  - 138 per-object parameter maps
  - 23 seed-redshift maps
  - 1 seed-redshift 3D test
- Duplicate checks passed for the generated result tables.

### Initial high-leverage objects
- GN-38509:
  - robust
  - high black-hole mass
  - strong growth leverage
  - high-value spotlight object
- GS-20057765:
  - highest-redshift v1 object
  - tentative
  - very high black-hole-to-host mass ratio where host mass is reported
  - high-value but should be caveated
- GS-20030333:
  - high redshift
  - tentative
  - lacks host stellar mass
- GS-164055:
  - high redshift
  - tentative
  - lacks host stellar mass
- GN-4685:
  - high redshift
  - tentative
  - useful for high-z comparison
- GN-954:
  - robust
  - high mass at z around 6.8
  - useful comparison object

### Initial findings to preserve
- Under baseline `z_seed = 30`, `epsilon = 0.1`, no merger boost:
  - `100 Msun` seeds require median lifetime-average `f_Edd` around 0.645 and max around 1.355.
  - `10^4 Msun` seeds require median `f_Edd` around 0.394 and max around 0.847.
  - `10^5 Msun` seeds require median `f_Edd` around 0.268 and max around 0.592.
- Under continuous `f_Edd = 1`, `epsilon = 0.1`, no merger, v1 objects are generally reachable from modest seeds by `z_seed = 30`.
- Under gentler `f_Edd = 0.3`, `epsilon = 0.1`, no merger, hardest objects require heavy or above-heavy seed masses.
- Current reported Eddington ratios in v1 are low, roughly `0.015-0.38`, so future duty-cycle analysis is important.
- The most useful scientific product is not "growth tracks exist"; it is ranking which objects remain interesting under transparent assumptions.

## Final Paper / Atlas Structure

### Abstract
Intermediate steps:
- Write a 150-250 word placeholder abstract early.
- Update after uncertainty propagation.
- Update again after dataset expansion.
- Final abstract should state:
  - dataset scope
  - growth diagnostic framework
  - major ranking result
  - what objects/classes are high-priority
  - limitations

Codex prompt:
> Draft a concise abstract for the observational atlas paper using the current roadmap and v1 results. Keep claims careful and make clear this is a ranking/triage framework, not proof of a formation channel.

### Introduction
Intermediate steps:
- Summarize why JWST high-z accreting black holes matter.
- Explain why high-z black-hole growth is a timing problem.
- Introduce seed scenarios:
  - light Pop III remnants
  - intermediate cluster/nuclear cluster seeds
  - heavy direct-collapse / supermassive-star seeds
  - PBH-like early seeds as an exploratory category
- Explain why literature measurements are method-dependent.
- Explain why a source-tracked atlas is useful.
- State the project goal as observational triage.

Codex prompt:
> Draft the introduction section for the atlas paper. Use cautious language, emphasize unsettled mass inference and object selection, and motivate a source-tracked atlas.

### Data and Source Selection
Intermediate steps:
- Describe v1 JADES/Juodzbalis sample.
- Describe redshift cut.
- Explain why start with broad-line AGN.
- Add a source inclusion table.
- For future sources, document:
  - paper
  - sample
  - object class
  - fields available
  - mass method
  - caveats
  - ingestion status

Codex prompt:
> Create a data/source-selection section outline for the current v1 catalogue and planned v2 expansion sources, including object-class caveats.

### Catalogue Construction
Intermediate steps:
- Describe raw-to-processed pipeline.
- Define measurement rows vs physical objects.
- Explain provenance fields.
- Explain missing-value flags.
- Explain quality flags.
- Explain method tags.
- Explain future cross-matching.
- Include schema summary in main text and full schema in appendix.

Codex prompt:
> Write the catalogue construction methods section from the current schema and standardization pipeline. Emphasize reproducibility, provenance, and missingness handling.

### Growth Model
Intermediate steps:
- Define cosmic time model.
- Define growth equation.
- Define seed redshift.
- Define seed mass ranges.
- Define `f_Edd`.
- Define radiative efficiency.
- Define spin-to-efficiency mapping.
- Define merger boost.
- Define slim-disk approximation and caveat that it is illustrative.
- Define required seed mass.
- Define required average `f_Edd`.
- Define what compatibility means.

Codex prompt:
> Draft the growth-model methods section from `src/models.py`, using equations and careful definitions. Include limitations of constant-average accretion and the illustrative slim-disk treatment.

### Systematics and Uncertainty Model
Intermediate steps:
- Add Monte Carlo sampling for reported `MBH` uncertainties.
- Decide how to treat asymmetric uncertainties.
- Add mass-systematic shifts:
  - baseline
  - `MBH - 0.3 dex`
  - `MBH + 0.3 dex`
  - optional extreme low-mass/scattering case
- Add host mass uncertainty.
- Add lensing uncertainty for lensed samples.
- Add object class/method caveat priors or flags.
- Report percentiles and probability metrics.

Codex prompt:
> Design and implement an uncertainty propagation module for the atlas. Use reported asymmetric MBH errors where available, include systematic mass-shift scenarios, and output per-object percentiles for required f_Edd and required seed mass.

### Results
Intermediate steps:
- Present catalogue overview.
- Present baseline growth requirements.
- Present object rankings.
- Present robust-vs-tentative split.
- Present systematics sensitivity.
- Present method-dependence once duplicate measurements exist.
- Present object-class comparisons after expansion.

Codex prompt:
> Analyze the current v1 result tables and produce a ranked list of high-leverage objects under baseline assumptions, including why each object is scientifically interesting and what caveats apply.

### Discussion
Intermediate steps:
- Interpret what the rankings mean.
- Explain why high required `f_Edd` is not automatically impossible.
- Compare current Eddington ratio vs lifetime-average requirement.
- Discuss seed models as diagnostics.
- Discuss mass inference systematics.
- Discuss follow-up priorities:
  - deeper spectroscopy
  - direct/dynamical mass constraints
  - X-ray constraints
  - lensing models
  - MIRI/SED decomposition
- Compare broad-line AGN, LRDs, X-ray candidates, and quasars once included.

Codex prompt:
> Draft a careful discussion section explaining what the rankings mean, what they do not prove, and which follow-up observations would most improve interpretation.

### Limitations
Intermediate steps:
- Acknowledge current v1 uses one source class and one source paper.
- Acknowledge simplified growth history.
- Acknowledge no full selection function yet.
- Acknowledge virial mass systematics.
- Acknowledge object-class mixing risks.
- Acknowledge illustrative slim-disk approximation.
- Acknowledge uncertain duty cycles.
- Acknowledge incomplete lensing handling until lensed samples are ingested.

Codex prompt:
> Write a limitations section for the atlas paper that is honest but not self-defeating.

### Appendix / Supplement
Intermediate steps:
- Full schema.
- Full source registry.
- Full processed catalogue.
- Full result tables.
- Full per-object map gallery.
- Sanity checks.
- Sensitivity tables.
- Literature candidate-source list.

Codex prompt:
> Create an appendix outline for the atlas paper, including tables and figure galleries that should not be in the main text.

## Detailed Implementation Roadmap

### Phase 1: Define final ranking metrics
Goal:
- Decide how objects will be ranked and why.

Intermediate steps:
1. List all candidate ranking metrics.
2. Separate physics metrics from data-quality metrics.
3. Define baseline physical metrics:
   - required `f_Edd` for fixed seeds
   - required seed mass for fixed `f_Edd`
   - minimum `z_seed` for fixed seed and `f_Edd`
   - black-hole-to-host stellar mass ratio
4. Define uncertainty metrics:
   - probability required `f_Edd > 1`
   - probability required seed mass `> 10^5 Msun`
   - probability required seed mass `> 10^6 Msun`
   - percentile range of required `f_Edd`
   - percentile range of required seed mass
5. Define observational caveat metrics:
   - robust/tentative quality
   - mass method
   - object class
   - missing host mass
   - lensing correction present/absent
   - duplicate measurement spread
6. Define follow-up priority:
   - high physical pressure
   - robust measurement
   - large uncertainty leverage
   - observationally actionable
7. Write metric definitions in a methods document.
8. Implement a ranking-table generator.
9. Validate ranking output on v1.
10. Use rankings to choose spotlight objects.

Codex prompt:
> Add a ranking metric design document for the observational atlas, then inspect the current v1 outputs and propose the columns needed for a final object-ranking table. Do not implement until the design is clear.

### Phase 2: Start final manuscript skeleton
Goal:
- Create the final paper scaffold early and update it as the project grows.

Intermediate steps:
1. Create `paper/` or `docs/manuscript/` directory if desired.
2. Create a main manuscript markdown or LaTeX file.
3. Add section headings.
4. Add placeholder figure callouts.
5. Add placeholder table callouts.
6. Add a running "claims checklist".
7. Add a running "citations needed" section.
8. Add a running "results not yet verified" section.
9. Add a figure inventory table.
10. Add an appendix inventory table.

Codex prompt:
> Create a manuscript skeleton for the final observational-atlas paper with placeholders for figures, tables, claims, citations needed, and appendices.

### Phase 3: Polish existing v1 final-figure prototypes
Goal:
- Convert current plots from exploratory to paper-readable.

Intermediate steps:
1. Audit all v1 exploratory figures and v2 final-style prototypes.
2. Decide which figures become main figures.
3. Decide which become appendix figures.
4. Reduce clutter in `MBH` vs redshift plot.
5. Make a small set of track assumptions visually legible.
6. Make a clean sample compatibility heatmap.
7. Make required-`f_Edd` by seed-mass figure.
8. Make ranked-object plot.
9. Make spotlight object maps.
10. Add consistent styling, captions, colors, and labels.
11. Ensure figures are interpretable without reading code.
12. Save final-style versions separately from exploratory figures.

Codex prompt:
> Review the current figures in `results/` and propose a final-figure set. Then refactor plotting code to create cleaner paper-style versions without deleting the existing exploratory outputs.

### Phase 4: Add uncertainty propagation
Goal:
- Move from point-estimate constraints to uncertainty-aware object rankings.

Intermediate steps:
1. Decide uncertainty distributions for reported `MBH`.
2. Implement sampling for asymmetric errors.
3. Decide number of Monte Carlo samples per object.
4. Sample `MBH` for each object.
5. Recompute required `f_Edd` for fixed seed assumptions.
6. Recompute required seed mass for fixed growth assumptions.
7. Add systematic mass shift scenarios.
8. Add host mass uncertainty sampling.
9. Add lensing uncertainty sampling where available.
10. Store per-sample or summarized outputs.
11. Summarize median, 16th, 84th, 5th, 95th percentiles.
12. Compute probabilities of threshold crossing.
13. Add uncertainty-aware ranking tables.
14. Plot uncertainty-aware rankings.
15. Validate output with deterministic seeds.

Codex prompt:
> Implement uncertainty propagation for v1 growth diagnostics. Use a deterministic random seed, asymmetric MBH errors, baseline and systematic mass-shift variants, and output percentile/probability summary CSVs.

### Phase 5: Expand broad-line AGN sample first
Goal:
- Build a larger, methodologically comparable BLAGN base before adding more ambiguous classes.

Status (2026-08-17): Taylor CEERS/RUBIES ingestion and the v3 JADES +
Taylor science workflow are complete. The v3 release contains 60 `z >= 4`
measurements representing 59 physical objects.

Status update (2026-08-22): Matthee EIGER/FRESCO and Lin ASPIRE are complete in
v4. The combined release contains 96 measurements representing 94 physical
objects. One new cross-paper identity, GOODS-S-13971 = GS-204851, is explicit.

Candidate sources:
- Taylor CEERS/RUBIES BLAGN: completed for the current 62-object source; the
  retained `z >= 4` layer has 37 measurements / 36 physical objects.
- Matthee EIGER/FRESCO and Lin ASPIRE broad-Halpha samples as complementary
  NIRCam WFSS selections. **Completed in v4.**
- Harikane faint BLAGN: **completed in v5** as ten measurement versions, with
  five verified overlaps and five new physical objects. Earlier CEERS/JADES
  discovery papers remain possible separate measurement-version layers.
- THRILS deep-spectroscopy BLAGN and evidence-graded ALPINE-CRISTAL candidates.
- Jones et al. as a host-mass/remeasurement layer after stable physical-object IDs exist.
- Baccus and Xu as a large archival audit only after duplicate resolution works.

Authoritative source-order notes and literature links:
- See `.codex_tmp/catalogue-expansion-guide.md`.

Intermediate steps per source:
1. Read the paper.
2. Identify tables with object-level redshift and mass.
3. Identify available `MBH`, `Lbol`, `f_Edd`, `Mstar`, uncertainties.
4. Record mass method.
5. Record luminosity method.
6. Record host method.
7. Record quality/candidate flags.
8. Add source registry entry.
9. Create raw source rows or source-specific ingestion script.
10. Standardize into canonical schema.
11. Validate required columns.
12. Check coordinates and aliases.
13. Run pipeline.
14. Compare output to paper.
15. Add source-specific caveats.
16. Recompute results.
17. Update figure/table inventory.

Codex prompt:
> Ingest the next broad-line AGN source into the atlas. First read the source registry and schema, then add source-tracked raw rows or an ingestion script, validate the processed catalogue, and summarize new objects and caveats.

### Phase 6: Add cross-matching and measurement versioning
Goal:
- Preserve multiple measurements while linking them to the same physical object.

Status (2026-08-17): complete for the current JADES + Taylor release, including
stable physical-object IDs, a separate link table, documented preferred
measurements, and measurement/object ranking products. General coordinate and
redshift matching helpers for future sources remain planned.

Status update (2026-08-22): the reusable coordinate/redshift candidate helper,
alias table, reviewed-candidate table, ambiguity rejection, and preference
continuity rule are complete for v4. Probabilistic matching remains future work.

Corrected-v4 update: pairwise candidate generation among newly added sources,
an explicit reviewed override registry, and one-at-a-time alternate-measurement
ranking sensitivity are complete. Probabilistic matching remains future work.

Intermediate steps:
1. Add a stable `physical_object_id` concept.
2. Keep `measurement_id` as row-level ID.
3. Add aliases table.
4. Add coordinate-based matching helper.
5. Add redshift tolerance matching.
6. Add manual override table for known aliases.
7. Add duplicate-measurement summary.
8. Add per-object preferred/default measurement rules.
9. Add measurement comparison plots.
10. Add object-level ranking separate from measurement-level ranking.
11. Preserve all measurements in the full catalogue.
12. Document duplicate handling in methods.

Codex prompt:
> Design the cross-matching and measurement-versioning layer for the atlas. Keep one row per paper measurement, add stable physical object IDs, and propose validation checks before implementation.

### Phase 7: Expand to additional object classes
Goal:
- Turn BLAGN foundation into a broader observational atlas.

Suggested order:
1. Lensed high-z AGN candidates.
2. X-ray-selected candidates, with UHZ1 marked disputed under the 2026 reanalysis rather than treated as confirmed.
3. Photometric LRD candidates; broad-Halpha LRDs belong in the BLAGN layer, with `lrd` stored as an independent phenotype.
4. High-ionization-line candidates.
5. XQR-30 and classical luminous quasars as a separate comparison stratum.

Intermediate steps:
1. Define object class taxonomy.
2. Define required fields per object class.
3. Define method tags per class.
4. Define caveat tags per class.
5. Decide which quantities are directly observed vs model inferred.
6. Add class-specific source registry entries.
7. Add class-specific ingestion functions if needed.
8. Keep plots separated by object class.
9. Avoid combining classes statistically until method differences are handled.
10. Add object-class comparison section to paper.

Codex prompt:
> Extend the catalogue design to support multiple high-z accreting black-hole candidate classes. Define object-class tags, method tags, caveat tags, and plotting rules before adding rows.

### Phase 8: Add duty-cycle and accretion-history diagnostics
Goal:
- Make growth interpretation more physical than constant average `f_Edd` alone.

Status (2026-08-25): completed for the v5 BLAGN science layer with burst
`f_Edd={1,2,3}`, zero quiescent accretion, asymmetric statistical MBH sampling,
measurement/object products, and explicit current-versus-lifetime semantics.
The implementation is an effective two-state sensitivity, not a time-resolved
feedback or stochastic-light-curve model.

Intermediate steps:
1. Define lifetime-average `f_Edd`.
2. Define burst duty cycle `D`.
3. Define burst accretion rate `f_Edd,burst`.
4. Implement required duty cycle:
   - given seed mass
   - given burst accretion rate
   - given radiative efficiency
   - given seed redshift
5. Compare required lifetime-average `f_Edd` to reported current `f_Edd`.
6. Add plots of current vs required average `f_Edd`.
7. Add duty-cycle ranking.
8. Add caveat that current accretion need not equal historical average.
9. Add discussion of bursty growth and feedback limits.

Codex prompt:
> Add duty-cycle diagnostics to the growth model and result tables. Compute required duty cycle for fixed seed mass, burst f_Edd, efficiency, and seed redshift, then compare to reported current Eddington ratios.

### Phase 9: Build final atlas/ranking products
Goal:
- Produce the core table and figures that define the observational atlas.

Status (2026-08-17): measurement- and physical-object-level point rankings,
uncertainty rankings, and source/survey/field/LRD-stratified summaries are
complete for JADES + Taylor and generalized in v4. Robust-only/tentative-only
derivative tables remain planned; v3 figures are complete.

Intermediate steps:
1. Create measurement-level ranking table.
2. Create physical-object-level ranking table.
3. Create robust-only ranking table.
4. Create tentative/candidate ranking table.
5. Create method-dependent ranking table.
6. Create follow-up priority matrix.
7. Add rank categories:
   - robust high pressure
   - tentative high pressure
   - method-sensitive
   - host-ratio tension
   - high-redshift leverage
   - quasar anchor
8. Add short object notes for top-ranked objects.
9. Add "what measurement would matter most" column.
10. Add atlas summary plots.

Codex prompt:
> Generate final-style atlas ranking tables from the current result products. Include physical stress metrics, uncertainty robustness, quality/method caveats, and a short follow-up priority reason for each top object.

### Phase 10: Final paper figures
Goal:
- Assemble the polished figure set for the final paper.

Likely main figures:
1. Catalogue overview in redshift-mass space.
2. Object-class and method map.
3. Required `f_Edd` ranking.
4. Required seed-mass ranking.
5. Compatibility heatmap.
6. Uncertainty/systematics robustness plot.
7. Spotlight object maps.
8. Follow-up priority matrix.

Likely appendix figures:
- Full growth-track comparison.
- Full per-object parameter map gallery.
- Full seed-redshift map gallery.
- Sensitivity tests by mass shift.
- Sensitivity tests by seed redshift.
- Sensitivity tests by spin/efficiency.
- Source-by-source comparison plots.

Codex prompt:
> Build the final paper figure inventory and map each current or planned plot to a manuscript section. Identify which existing figures should be replaced, simplified, or moved to the appendix.

### Phase 11: Final manuscript assembly
Goal:
- Turn the living draft into a polished paper/report.

Intermediate steps:
1. Freeze dataset version for the draft.
2. Freeze figure set.
3. Freeze result tables.
4. Verify all numeric claims.
5. Add citations.
6. Write final abstract.
7. Write final introduction.
8. Write final methods.
9. Write final results.
10. Write final discussion.
11. Write limitations.
12. Write conclusion.
13. Build appendix.
14. Check consistency of terminology.
15. Check every claim has a source or table.
16. Check no overclaims remain.
17. Prepare professor-facing summary.

Codex prompt:
> Audit the draft manuscript for unsupported claims, unclear definitions, missing citations, and figure/table mismatches. Return a prioritized revision checklist.

## Source Expansion Tracking

### Highest-priority BLAGN sources
- Juodzbalis et al. JADES broad-line AGN:
  - status: v1 baseline ingested.
- Taylor et al. CEERS/RUBIES BLAGN:
  - status: ingested and evaluated; 37 `z >= 4` measurements represent 36
    physical objects, producing a 60-measurement / 59-object combined release.
- Matthee et al. EIGER/FRESCO and Lin et al. ASPIRE:
  - status: completed in v4 as complementary NIRCam WFSS expansions; 36
    measurements contribute 35 additional physical objects after linking
    GOODS-S-13971 to JADES GS-204851.
- Harikane et al. faint BLAGN:
  - status: completed in v5; ten rows, five verified overlaps, five new objects.
- Earlier CEERS/JADES discovery papers:
  - status: possible future measurement-version layers after cross-matching.
- THRILS and ALPINE-CRISTAL-JWST:
  - status: planned selection-bias/evidence-graded extensions.
- Jones et al. and Baccus and Xu:
  - status: deferred until stable physical-object IDs and duplicate resolution exist.

### High-priority non-BLAGN / mixed candidates
- UHZ1:
  - status: disputed after the 2026 full-exposure Chandra reanalysis.
  - retain in the evidence catalogue but exclude from confirmed-object growth rankings unless stronger evidence appears.
- GN-z11:
  - very high redshift.
  - mass/accretion interpretation needs caution.
- A2744-QSO1:
  - lensed candidate.
  - attach direct/dynamical and virial results as measurements of one physical object.
- Photometric LRD candidates:
  - store `lrd` as a phenotype, not as proof of accretion.
  - exclude from the primary growth ranking without credible AGN evidence and a defensible black-hole mass posterior.

### Quasar anchors
- XQR-30 and other z > 6 luminous quasars:
  - useful comparison sample.
  - not directly comparable to faint JWST BLAGN/LRDs.
  - should be plotted as anchors or a separate analysis stratum.

## Figure Inventory and Intended Use

## Intended Paper Products

### Main-text products
- Catalogue overview in redshift-mass space.
- Object ranking by growth pressure.
- Required `f_Edd` summaries for fixed seed masses.
- Required seed-mass summaries for fixed accretion histories.
- Compatibility heatmap across seed/growth assumptions.
- Uncertainty and systematics robustness plots.
- Selected object-level parameter maps.
- Follow-up priority table or matrix.

### Appendix / supplement products
- Full catalogue schema.
- Full source registry.
- Full processed catalogue tables.
- Full result tables.
- Full per-object parameter-map gallery.
- Full seed-redshift map gallery.
- Validation checks.
- Sensitivity tests.
- Source-by-source caveats.

Use this section to decide what belongs in the final paper versus what should stay in the appendix. The main text should showcase the atlas logic and strongest rankings; the appendix should preserve the comprehensive technical and visual record.

### Current figures likely useful in main text after polishing
- `v1_sample_compatibility_summary.png`
  - Use: sample-level scenario compatibility.
  - Needs: clearer caveat about exact-fit compatibility and overgrowth.
- `v1_mbh_vs_redshift_growth_tracks.png`
  - Use: overview / visual motivation.
  - Needs: simplified track set for main paper.
- Selected seed-redshift maps:
  - Use: object-level timing diagnostic.
  - Strong candidates: GN-38509, GS-20057765.
- Selected parameter maps:
  - Use: object-level seed/accretion tradeoff.
  - Strong candidates: GN-38509, GS-20057765.

### Current figures likely appendix/supplement
- Full per-object parameter-map gallery.
- Full seed-redshift map gallery.
- 3D seed-redshift test unless it becomes scientifically clearer.
- Older growth-track variants.

### Missing figures to create
- Ranked object stress-test plot.
- Uncertainty-aware ranking plot.
- Current vs required `f_Edd` plot.
- Physical pressure vs measurement robustness plot.
- Follow-up priority matrix.
- Object class/method map after expansion.
- Duplicate-measurement comparison plot after cross-matching.

## Key Concepts to Keep Straight

### Measurement row vs physical object
- `measurement_id` should identify one source-paper measurement.
- Future `physical_object_id` should identify the astronomical object.
- Multiple papers can produce multiple measurement rows for the same physical object.
- Do not overwrite measurements just because a later paper exists.

### Compatibility vs possibility
- A scenario can be incompatible because it undergrows the black hole.
- A scenario can also be incompatible because it overgrows the black hole.
- Compatibility is an exact-scenario match unless defined otherwise.
- For physical interpretation, required-parameter metrics are often clearer than binary compatibility.

### Current Eddington ratio vs lifetime-average growth
- Reported `f_Edd` is a current or inferred observed-state quantity.
- Required average `f_Edd` is a historical average over seed-to-observation time.
- These should not be treated as identical.
- The gap between current and required average may motivate duty-cycle analysis.

### Object classes should not be blindly mixed
- Broad-line AGN, LRDs, X-ray candidates, lensed AGN, and luminous quasars have different selection functions and mass methods.
- It is fine to show them together in atlas plots if visually distinguished.
- It is risky to draw population-level conclusions without method-aware caveats.

## Historical Prompt Sequence

This is an audit trail of the sequence that produced v1--v4, not the current
task queue. Use the immediate-next-task section below for new work.

1. "Read `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md`, then inspect the repo and summarize the exact next coding task for Phase 1."
2. "Design the final ranking metrics and output columns, but do not implement yet."
3. "Implement the v2 ranking table from the v1 result CSVs and write a short verification summary."
4. "Create final-style v2 figure prototypes for the v1-catalogue ranking table and simplified growth overview."
5. "Design the uncertainty propagation module and output schema."
6. "Implement uncertainty propagation for v1 only."
7. "Update the manuscript skeleton with current methods/results placeholders."
8. "Choose the next broad-line AGN source to ingest and produce an ingestion plan."
9. "Ingest the next BLAGN source with provenance and validation."
10. "Design cross-matching / physical object IDs before adding more overlapping sources."
11. "Recompute the atlas rankings and compare the v2 v1-catalogue analysis with the v3 expanded BLAGN rankings."
12. "Plan the first non-BLAGN object class expansion with caveat tags."

## Immediate Next Best Task after v5

The v3 figure task, v5 Harikane expansion, evidence/eligibility gate,
reproducibility manifest, paper-facing ranking comparison, and first
accretion-history diagnostics are complete. The next best concrete task is to
define class-specific eligibility and mass-comparability rules before adding a
heterogeneous v6 source, while completing the citation and figure-selection
audit in parallel.

Historical v3 figure brief:

- Compare v2 (v1-catalogue) and v3 mass-redshift coverage without pooling
  unlike selection functions.
- Plot measurement- and physical-object-level v3 rankings separately.
- Show the Taylor-specific `+/-0.5 dex` virial sensitivity independently from
  reported statistical errors and the common `+/-0.3 dex` comparison.
- Keep the v2 figure artifacts frozen as the reproducible pre-expansion record.

The next task should turn the current v4 tables into paper-ready comparisons,
while preserving the completed v2 and v3 artifacts and avoiding another source
ingestion before v4 has been interpreted visually.
