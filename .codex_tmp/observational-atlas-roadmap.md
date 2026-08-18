# High-z Accretion Atlas: Research-Grade Roadmap

Thread intent:
- This project path is Path B: an observational atlas / follow-up triage project.
- Draft the final paper continuously throughout the project.
- Do not make a separate v1 report unless the user later asks for one.
- Keep the main claim careful: this project identifies robust and assumption-dependent high-redshift accreting black-hole candidates; it does not claim a single formation channel is proven.
- Use `.codex_tmp/catalogue-expansion-guide.md` for the literature-reviewed source order, object taxonomy, growth-eligibility rules, and corrections to the older v2 candidate-source memo (reviewed 2026-08-17).

Working thesis:
> A reproducible, source-tracked, uncertainty-aware atlas of high-redshift accreting black-hole candidates can separate robust growth-challenging objects from interpretation-dependent ones, providing a ranked target list for follow-up and seed/accretion modeling.

Completed so far:
- Project framing around high-z JWST accreting black holes, seed masses, accretion histories, and object triage.
- v1 catalogue from the Juodzbalis/JADES broad-line AGN sample.
- Raw catalogue has 34 rows; processed v1 filters to 23 objects at z >= 4.
- Catalogue tracks provenance, source table, object class, methods, missing values, quality flags, and interpretation tags.
- Schema and validation rules exist in docs.
- Dayal-style exponential growth model implemented.
- Planck-style cosmic time implemented.
- Required seed mass and required average f_Edd utilities implemented.
- Spin-dependent thin-disk efficiencies implemented.
- Merger boost implemented.
- Illustrative slim-disk effective efficiency above Eddington implemented.
- v1 evaluation tables, required-f_Edd tables, required-seed tables, and sample summaries generated.
- Growth-track plots, sample compatibility heatmap, per-object parameter maps, seed-redshift maps, and one 3D seed-redshift test generated.
- Initial high-leverage objects identified: GN-38509, GS-20057765, GS-20030333, GS-164055, GN-4685, GN-954.

Primary project path from here:
1. Define final ranking metrics.
   - Required f_Edd for fixed seed masses.
   - Required seed mass for fixed accretion histories.
   - Probability of requiring super-Eddington average growth.
   - Probability of requiring heavy seeds.
   - Robustness to MBH systematic shifts.
   - Host MBH/Mstar tension.
   - Measurement quality and method caveats.
   - Follow-up priority.

2. Start and maintain final manuscript skeleton.
   - Abstract draft.
   - Introduction.
   - Data and source selection.
   - Catalogue construction.
   - Growth model.
   - Systematic assumptions.
   - Results.
   - Object ranking.
   - Discussion.
   - Limitations.
   - Future work.
   - Appendix: full catalogue, scenario tables, map gallery, validation checks.

3. Polish v1 figures into final-style prototypes.
   - Clean MBH vs redshift figure with fewer tracks.
   - Sample compatibility heatmap.
   - Required f_Edd by seed mass.
   - Ranked object stress-test plot.
   - Selected object maps for GN-38509 and GS-20057765.
   - Seed-redshift map showing how early seeding changes conclusions.

4. Add uncertainty and systematics.
   - Monte Carlo over reported MBH uncertainties.
   - Virial/systematic MBH shifts, including +/-0.3 dex and possibly an extreme negative shift for scattering/mass-systematics tests.
   - Host stellar mass uncertainty.
   - Lensing uncertainty where relevant in later samples.
   - Report percentiles and probabilities rather than only point estimates.

5. Expand broad-line AGN first.
   - Add the z >= 4 subset of the current 62-object Taylor CEERS/RUBIES BLAGN catalogue first. **Completed 2026-08-17.**
   - Add Matthee EIGER/FRESCO and Lin ASPIRE as complementary NIRCam WFSS selections.
   - Add Harikane and earlier CEERS/JADES discovery papers as measurement-version layers after cross-matching.
   - Add THRILS and evidence-graded ALPINE-CRISTAL candidates.
   - Defer large overlapping compilations such as Baccus and Xu until physical-object IDs work.
   - Recompute rankings and test whether v1 high-leverage objects remain special.

6. Add cross-matching and measurement versioning.
   - Stable physical object IDs. **Completed for JADES + Taylor.**
   - One row per paper measurement. **Completed for JADES + Taylor.**
   - Aliases, coordinates, field, and redshift matching.
   - Preserve method-dependent measurements rather than overwriting. **Completed for the explicit CEERS-2782/RUBIES-EGS-50052 duplicate.**
   - Measurement- and physical-object-level point and uncertainty rankings. **Completed 2026-08-17.**

7. Expand to additional high-z accreting-BH candidate classes.
   - Lensed high-z AGN candidates.
   - X-ray-selected candidates, with UHZ1 retained as disputed rather than confirmed under the current literature assessment.
   - Photometric LRD candidates, while treating LRD as a phenotype rather than an accretion class.
   - High-ionization-line candidates.
   - XQR-30/classical luminous quasars as a separate comparison stratum.
   - Keep object classes and mass methods visually/statistically distinct.

8. Add duty-cycle and accretion-history diagnostics.
   - Lifetime-average f_Edd.
   - Burst duty cycle D.
   - Burst accretion rate f_Edd,burst.
   - Required duty cycle for each object.
   - Compare current reported Eddington ratio against lifetime-average requirement.

9. Build final atlas/ranking products.
   - Main ranked object table.
   - Robust vs tentative high-pressure objects.
   - Method-dependent objects.
   - Follow-up priority matrix.
   - Full appendix/supplement map gallery.

Final paper posture:
- Main paper is an observational atlas / follow-up triage paper.
- Formation models are used as diagnostics, not as claims of proof.
- Avoid claims such as "standard cosmology is broken", "PBHs are required", or "heavy seeds are proven".
- Prefer claims such as "these objects remain high-leverage under specified assumptions" and "these measurements most affect the growth interpretation".
