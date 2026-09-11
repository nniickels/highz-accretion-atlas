# Reassessment after priority revisions — 11 September 2026

**Assessment: substantially improved; targeted revision is still warranted before journal submission.** The conditional growth calculations and their presentation are defensible in the checks performed. The revised table now exposes a major limitation of the reported probabilities, and the cosmology attribution and overly broad sample-exclusion statement have been corrected. The strongest remaining concern is the demonstration of scientific contribution beyond earlier studies. This is an internal assessment, not an independent referee decision or an acceptance prediction.

This reassessment supersedes the earlier review's current-status judgments. That review remains a record of its explicitly identified older snapshot. Criteria are originality, scientific rigour, significance and clarity from the [IOP reviewer guidance](https://publishingsupport.iopscience.iop.org/questions/reviewer-report-form-quality-rating-descriptions/), together with reproducibility and submission expectations in the [MNRAS author instructions](https://academic.oup.com/MNRAS/pages/General_Instructions). MNRAS-specific formatting requirements apply only if that journal is chosen.

| Criterion | Current assessment |
|---|---|
| Research question | Clear: quantify growth requirements for adopted masses under explicit seed and accretion assumptions. |
| Originality and significance | Promising catalogue contribution; the difference from prior catalogues and analyses needs more evidence. |
| Mathematical methods | Consistent in the tested fixed-efficiency calculations and new mass-shift calculation. |
| Sample definition | The specific wording mismatch is corrected. Evidence classifications remain source-based judgments whose application should be documented. |
| Uncertainty | Improved substantially. Separately reported calibration scales are visible beside the probabilities. The probabilities remain conditional on incomplete, heterogeneous error budgets. |
| Interpretation | Conclusions accurately state their growth assumptions. Constant-spin and early-onset illustrations have a narrower physical scope. |
| Reproducibility | Deterministic products, generated tables and passing tests support the analysis. Committing this revision records it locally; public release and clean CI on that release remain separate steps. |
| Presentation | Improved notation, conclusions and Table 1. The local compile is free of warnings. Some dense figures and peripheral appendix material remain. |

**Resolved or substantially addressed**

1. **Cosmology attribution:** Section 1.1 now attributes only H0 and Ωm to Dayal and explicitly sets ΩΛ through flatness. The numerical model has not changed. See [line 150](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:150>).
2. **Selection wording:** Section 2 identifies the seven conditionally interpreted masses and explains the separate treatment of COSMOS3D-13852's scattering concern. It no longer implies that every possible virial-mass ambiguity has been excluded. See [line 177](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:177>).
3. **Uncertainty visibility:** Table 1 identifies the separate 0.5-dex and 0.3-dex calibration scales and the scatter already included for ZS7. Its new Δm column gives the mass reduction needed to reach a required average Eddington ratio of one. This directly exposes J0910_2028_12910's 0.330-dex margin relative to its separate 0.5-dex scale. See [line 330](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:330>).
4. **Conclusions and notation:** The conclusion now specifies the seed mass, starting redshift, efficiency and interpretation of the Monte Carlo count. The probability expression uses the required time-average ratio. The lowercase sentence opening and overfull data-path line are corrected.

**Remaining revisions, in priority order**

**1. Demonstrate the added scientific value.** Introduction and Section 4.5; [line 83](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:83>).

The paper combines a larger literature catalogue, traceable measurements, uncertainty propagation, mass-shift tests and individual observational targets. Those are useful contributions. The efficiency and seed-mass dependencies follow from the existing exponential growth relation, so a reader needs to see what the compilation newly establishes. Add a concise comparison with the closest prior studies: sample scope, new objects, revised measurements, and conclusions that change. The four-object Dayal comparison is informative but has limited coverage. This is the largest remaining editorial risk under novelty and significance criteria. An exhaustive priority search has not been performed in this review, so no uniqueness claim is certified.

**2. Document how the source list and evidence classifications were assembled.** Section 2 and Appendix A; [line 162](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:162>).

The source inventory and declared cutoff make the scope visible. They do not fully explain how the source families were found, why that list was adopted, or how source statements were translated into secure, probable and candidate categories. Provide a short, factual account of the search and classification process, with examples of borderline decisions. The correction to the conditional-mass wording is sufficient to resolve the specific contradiction in the earlier review. A source-specific exclusion sensitivity could add evidence, but it requires a justified rule and should not be introduced by choosing arbitrary objects to remove.

**3. Preserve the present limits on probability and physical interpretation.** Section 3.2, Table 1 and Appendices C–D; [line 229](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:229>).

The new notes and Δm values improve interpretation; they do not estimate the distributions of unknown calibration errors. A >95% result remains a statement about the adopted error distribution and growth assumptions. The manuscript is now substantially clearer on this point. A full calibration-aware model would be needed for stronger total-probability claims, but is not required for the descriptive conditional study as currently framed.

Likewise, reaching the central masses at fixed low efficiency establishes mathematical compatibility. It does not establish a sustained gas supply or a particular spin history. The fixed-spin grid and the radiation-free z=3400 extrapolation are labelled as limited calculations. Keep them illustrative, and consider shortening them if their role in the main argument remains small. A radiation-inclusive clock alone would not provide a physical model of early gas accretion.

**4. Complete the public analysis release and journal preparation.** Appendix E; [line 1025](</Users/nickel/Library/CloudStorage/OneDrive-Personal/personal work/projects/Dayal/highz-accretion-atlas/paper/highz_accretion_atlas_v3.tex:1025>).

The older catalogue hash and the current analysis revision serve different purposes. Record the exact analysis release that reproduces the submitted paper and make its inputs, selection mask, code and table data accessible. The commit requested in this turn preserves the current work locally; it is not a public deposit or a remote-CI run. Verify the final release through the documented clean workflow. A persistent archive is useful, but a DOI is not a universal prerequisite to submission.

For MNRAS, the remaining preparation includes its abstract convention, author metadata, figure alt text, data-statement placement and first-citation order of figures. Figure 6 is mentioned before Figure 1. The generic single-column draft has 22 pages, which is not itself a page-limit violation. Figure 1's small labels and the dense compatibility grid deserve attention in the final journal layout. The catalogue browsing score can remain in software documentation if it does not help the scientific argument.

**Verification and scope**

- The preceding full test run passed 99 tests after the numerical addition. The final focused publication-review tests passed 5 tests. No numerical code changed after those checks.
- The publication-generation verification was rerun during this reassessment and passed. It reports 224 primary and 234 expanded-sample objects, with all six unresolved-identity records excluded from manuscript inference.
- The new mass-shift test recovers a required average Eddington ratio of one after applying Δm and verifies values on both sides of that boundary. Existing target values, probabilities and metadata were compared exactly with the preceding commit and are unchanged.
- The final PDF compiled without warnings and Table 1 was visually inspected after the changes. Prior overview inspection covered all manuscript pages; this reassessment concentrated on the changed sections and table.
- The open Overleaf main source was copied and compared exactly with a freshly prepared version of the current repository source. This comparison includes the inlined generated table and comparison text used by Overleaf. The sources matched before recompilation.
- No complete re-extraction of all literature measurements, exhaustive novelty search, or fresh full notebook rebuild was performed during this reassessment. The open scientific identities are disclosed and excluded, rather than treated as resolved.

The draft is suitable for focused scientific feedback. Before submission, the highest-value work is a precise comparison with prior studies and an explicit account of source selection. The remaining physical limitations can be handled by maintaining the current restricted claims; a new accretion simulation or population model is not automatically required.

Reviewed content hashes (SHA-256; unaffected by committing):

```text
paper/highz_accretion_atlas_v3.tex: baffeefe0fe3d4bb3870c78e08d5e24b0b47e5532abe2f74c08d96a5dc7a7508
paper/highz_accretion_atlas_v3.pdf: cce46a74f18a2a77a32f3ee8c39d43ad89e07ecd3f19d461427ac29484e54aef
paper/analysis/target_robustness.csv: c69ecd4a06fc2a7ff245af6e8a906173b614fdf63e9137b2ec507716b3171c13
```
