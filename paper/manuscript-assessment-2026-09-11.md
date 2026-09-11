# Manuscript assessment — 11 September 2026

**Recommendation: substantive revision before journal submission.** The draft has a defensible catalogue-based contribution and its main calculations are consistent with its stated assumptions. I would request revisions to the sample rules, presentation of uncertainty, and statement of scientific contribution. I found a specific attribution error and several smaller presentation problems. This is my assessment of the current draft, not an external referee decision or a prediction of acceptance.

I reviewed the 22-page PDF, the manuscript including its appendices and generated tables, selected classification and calculation code, and several central references. I inspected all pages at overview scale and Figures 1, 2 and 4 and Table 1 at larger scale. The review checks selected scientific claims; it does not independently re-extract all 350 literature measurements or establish that the source list is exhaustive. No manuscript or Overleaf edits were made during this assessment.

The criteria are originality, scientific rigour, significance, reproducibility, and clarity, following the [IOP reviewer criteria](https://publishingsupport.iopscience.iop.org/questions/reviewer-report-form-quality-rating-descriptions/). I also used the [MNRAS author instructions](https://academic.oup.com/MNRAS/pages/General_Instructions) for journal expectations. No target journal has been selected, so MNRAS-specific formatting points below are conditional. This is an astronomical catalogue and modelling paper; it does not require a clinical-study reporting checklist.

| Criterion | Assessment | Main reason |
|---|---|---|
| Research question | Clear | Which observed masses require large average Eddington ratios under specified growth assumptions? |
| Originality and significance | Needs stronger demonstration | The source-linked catalogue and sensitivity comparisons add value; exponential growth and efficiency scaling are established results. |
| Equations and numerical implementation | Sound in the checks performed | The fixed-efficiency growth relation, inverse calculation and checked numerical results agree. |
| Sample definition | Needs revision | The prose about uncertain broad-line interpretations is broader than the actual exclusion flags. |
| Uncertainty analysis | Valid as conditional propagation; interpretation needs strengthening | The quoted errors contain different mixtures of measurement and calibration uncertainty. |
| Conclusions | Mostly appropriately bounded | Seed, efficiency and starting-time dependence are disclosed; the ranking must remain tied to adopted mass estimates. |
| Reproducibility | Strong local implementation; release unfinished | Deterministic calculations and tests exist, but the exact revised analysis and test repair are still uncommitted locally. |
| Presentation | Readable, with remaining corrections | Named-object figures and tables help; notation, appendix scope and a few recent edits need attention. |

**1. Make the classification rules operational and consistent with the included objects. High priority.**

Location: Section 2, [manuscript line 175](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:175>).

The draft says that it excludes objects whose masses depend on an unresolved interpretation of the broad emission as a gravitationally bound broad-line region. Yet COSMOS3D-13852 is included and ranked among the strongest constraints while Section 5.2 reports a possible 1–2 dex mass bias from scattering. Its stored flags are `evidence_status=secure`, `conditional_mass_flag=False`, and primary inclusion true. CEERS-1019 is also included despite the separately discussed limited significance of its broad component.

This is a mismatch between the wording of the rule and its operational meaning, rather than evidence that these objects must automatically be removed. Evidence for an accreting black hole and confidence in a virial mass are different assessments. Explain what constitutes a conditional mass in the catalogue, who assigns the evidence classifications, which source statements support them, and how borderline cases are treated. A small decision table would make the selection reproducible from the paper. Repeat the main counts after excluding the particular objects whose virial interpretation is questioned; report that sensitivity without silently changing the catalogue.

Grouping Hα/Hβ single-epoch estimators is scientifically reasonable for a comparison by method. It does not provide a universal ordering of mass reliability. Preserve the individual assessment of UV and dynamical measurements. The discussion of calibration and virial assumptions in [Shen (2013)](https://ned.ipac.caltech.edu/level5/Sept13/Shen/paper.pdf) supports treating these as separate questions.

**2. Make the uncertainty attached to each high-probability result visible beside that result. High priority.**

Locations: Section 3.2, Table 1 and Section 5.2; [manuscript line 221](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:221>).

The Monte Carlo procedure is described clearly. Its probabilities describe the adopted mass-error distributions with the growth parameters held fixed. The problem is that these distributions represent different uncertainty budgets. J0910_2028_12910 has a quoted error of 0.01 dex and a separate 0.5 dex calibration scale; ZS7's quoted error already includes calibration scatter. Their probability values therefore cannot be interpreted as equivalent measures of total physical confidence.

The draft acknowledges this, but Table 1 foregrounds the probabilities while the larger uncertainties are elsewhere. Add an error-content indicator or a separate systematic-uncertainty column next to the mass and probability. A source-specific sensitivity summary for the 12 objects would be more informative than the uniform shifts alone. Avoid adding the same Gaussian scatter to every object, which could double-count included uncertainties and invent distributions for unknown biases.

A useful supplementary quantity is the downward mass shift needed to bring the central required ratio to one. Independently calculating this from the growth equation gives approximately 0.330 dex for J0910_2028_12910, 1.576 dex for COSMOS3D-13852, and 1.921 dex for UNCOVER-20466. The 0.330-dex margin is smaller than J0910's separately listed 0.5-dex calibration scale. These margins quantify sensitivity without assigning a probability to an unknown correction. They depend on the same reference growth assumptions.

A complete hierarchical population model is not necessary for a paper restricted to these conditional object-level calculations. It would become necessary to justify stronger population or total-probability claims.

**3. State more precisely what the new analysis adds to prior work. High priority for publication, rather than a calculation error.**

Locations: Introduction, Section 4.5 and Conclusions; [manuscript line 83](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:83>).

The larger catalogue, source provenance, explicit uncertainty handling, matched comparison, and named targets are the strongest contributions. The dependence on seed mass, radiative efficiency and growth time follows directly from the established growth equation. The four-object Dayal comparison is useful and properly holds cosmology fixed, but its limited coverage does not demonstrate how much the overall scientific picture has changed.

Add a concise comparison with prior catalogues or growth studies: their scope, which objects are newly assessed here, how measurement revisions change the conclusions, and which specific result would be unavailable without this compilation. Identify how the 32 source families were found and selected, even if the catalogue is explicitly bounded to a declared list. Do not claim exhaustive coverage without a documented search. An exhaustive new literature review is outside this assessment, so I cannot certify priority or uniqueness.

This recommendation follows the journal's requirement to demonstrate novelty and significance; there is no requirement that the equations themselves be new. A carefully documented astronomical catalogue can provide a substantial contribution.

**4. Correct the attribution of the cosmological parameters. Definite factual wording correction.**

Location: Section 1.1, [manuscript line 150](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:150>).

The current sentence attributes the listed parameter set to Dayal, including ΩΛ = 0.685. The [published Dayal paper](https://research.rug.nl/files/1151545270/aa51481-24.pdf), page A182, 2, lists ΩΛ = 0.673, Ωm = 0.315 and h = 0.673. The draft matches the listed H0 and Ωm and imposes ΩΛ = 1 − Ωm = 0.685. Whether Dayal's ΩΛ is a typographical error cannot be established here.

State that H0 and Ωm match Dayal's quoted values and that this work fixes ΩΛ by spatial flatness. No change to the calculations is indicated by this wording issue. “Planck-based” and “flat ΛCDM” are compatible descriptions, but they do not establish equality of every quoted parameter. My preceding wording edit introduced this overbroad attribution; the earlier, more explicit distinction should be restored.

**5. Keep the physical interpretation within the limits of the growth model. Medium priority.**

Locations: Section 4.4, Appendix C and Appendix D.4; [manuscript line 772](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:772>).

The fixed-efficiency exponential model is appropriate for the stated conditional question. The finding that all central masses can be reached at ε = 1 − √(8/9) is an algebraic result. It does not by itself demonstrate that the required gas supply and low efficiency can be maintained during growth. The draft largely makes this distinction already; retain it.

The spin grid fixes ideal a = −1, 0, +1 efficiencies and uses a simplified supercritical prescription. These are illustrative calculations. Keep them subordinate to the fixed-efficiency results, and describe the grid as constant-state calculations wherever it is shown. A full spin-evolution or radiation-hydrodynamic model would be an extension of the project, not a prerequisite for these bounded conclusions.

The z = 3400 appendix is explicitly an extrapolation of a cosmology without radiation. That disclosure prevents it from being a hidden approximation, but the connection to primordial growth remains physically incomplete. Either make it a short mathematical illustration, or use radiation-inclusive ages and clearly specify the onset and availability of gas accretion if it is to support a physical PBH claim. Changing the age formula alone would not establish a viable early accretion history. The arbitrary catalogue navigation score can move to software documentation because it does not support the scientific conclusions.

**6. Complete a reproducible release of the revised analysis. Required before making a final release claim.**

Location: Appendix E, [manuscript line 988](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:988>).

The catalogue baseline hash is provided, and the updated manuscript correctly distinguishes identity exclusions from resolution of the identities. The exact revised manuscript, generated prose, and PDF comparison repair currently include uncommitted local changes. A reader needs a version identifier for the analysis that produces the submitted paper in addition to the older catalogue identifier.

Create a release containing the code, dependencies, selection mask, external comparison inputs, table data and figure inputs; record the analysis revision in the data-availability statement. Check the final release with a clean rebuild after the changes are committed. The prior successful local rebuild and current passing tests provide useful evidence, but remote CI for the uncommitted changes has not run. A DOI is useful for permanence; it should not be represented as an existing identifier or a universal pre-submission requirement. MNRAS does require a data-availability statement and supports formal data/software citations.

**7. Specific presentation corrections. Lower priority.**

- Section 4.2 writes P(f_Edd > 1), whereas Table 1 uses the required time-average quantity. Use the barred, required-ratio notation consistently in text, table headings and relevant plot axes. The current figures frequently abbreviate it to “Required f_Edd.”
- Appendix D.4 has “(Figure …). at fixed observed mass …” at [manuscript line 922](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:922>). Capitalize the new sentence. This was introduced during the previous style pass.
- The conclusion still uses “reference point requirements,” “probability threshold” and a blanket “conservative” sample description. Use the physical quantity and exact assumptions, or define the limited sense of conservative as the identity exclusions. This remains unfinished from the clarity pass.
- Figure 1 has small legend and named-object labels at page scale. Increase their size and consider simplifying the plotted tracks. The data-dependent choice of tracks is disclosed in the appendix; a short reminder in the caption would make the visual comparison easier to interpret. It should not be read as a fit.
- Figure 4 is dense relative to its supporting role. Figure 3 and Table 1 convey the principal scientific result more directly.
- The current PDF has 22 pages in the generic article class. This is not, by itself, excessive or a journal violation. The navigation-score appendix and repeated sample/probability caveats are candidates for shortening.
- For an MNRAS submission, adapt the structured abstract to its single-paragraph convention, provide figure alt text and the required author metadata, and put the data statement in the prescribed location. The current abstract is approximately 236 whitespace-separated words, so I do not find a word-limit problem. Figure 6 is referenced in the main methods before Figures 1–5; adjust numbering or first-reference order for that journal.
- There is a small existing 3.27-pt overfull line in the data-availability paragraph. The overview review found no major clipping or broken tables. Final typography should be checked in the selected journal class.

**Checks that support the manuscript**

- The required growth equation has the expected ε/(1 − ε), elapsed-time and logarithmic mass dependence. The zero floor is now explained accurately, including the case where the initial mass is too large.
- Recalculation of the 12 listed central requirements gives a maximum of 1.452204. Scaling by the exact non-spinning thin-disc efficiency gives 0.792819, consistent with the printed 0.793.
- Analytic integration of the same equal-side half-normal mass distributions gives six of the 12 objects with P ≥ 0.95. The largest absolute difference from their stored Monte Carlo probabilities is 0.00686; the six-object classification is unchanged in this check.
- The preceding validation of this unchanged code state passed all 98 unit tests and the publication-table checks. This review did not repeat the full notebook rebuild or re-extract every source value.
- The [published dynamical-mass paper](https://www.nature.com/articles/s41586-026-10579-4) reports the MOKA3D value log M = 7.7 ± 0.3 used here and distinguishes it from the inclination-unconstrained lower limits. The manuscript's selected comparison is supported by that source.
- The bibliography contains two different Juodzbalis-led 2026 papers, so 2026a/2026b is appropriate. Expanding the included table fragments revealed no missing citation keys or uncited bibliography entries.
- Excluding unresolved identity records is a defensible way to bound the analysis. Resolving those records is necessary for their readmission, rather than a prerequisite for analysing the unaffected objects.
- A combined selection function is unnecessary for descriptive calculations on these objects. It is needed for the population claims that the manuscript explicitly avoids.

The revision priorities are to align classification prose with the actual decisions, show source-specific uncertainty beside the headline results, establish the catalogue's added scientific value, correct the cosmology attribution, and identify the exact released analysis. The conditional growth results appear defensible within the checked assumptions. Their astrophysical strength depends on the reliability of the adopted masses and on the growth assumptions remaining explicit.

Reviewed snapshot (SHA-256):

```text
paper/highz_accretion_atlas_v3.tex: 1ec35a99908bd4be40ed5121f8ed41707b75a581d1cbdbd495ae3677e6b4e3b1
paper/highz_accretion_atlas_v3.pdf: 30eaa44f66804d506d2e389518daa6f7d403b637ee06f2b3f46668e6c3c7a176
paper/analysis/target_robustness.csv: f86fa152b9f10f6182cf5a8e41d97b0e2ae4bf6afdd0fcef243d89cc2ce87b3d
```
