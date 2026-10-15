# Ap&SS submission package

This folder contains the submission package for
*Astrophysics and Space Science* (Ap&SS). It is separate from the original
local manuscript in `paper/main.tex`.

## Files

| File or folder | Purpose |
| --- | --- |
| `main.tex`, `main.pdf` | Submission source and compiled manuscript. |
| `figures/`, `tables/` | Eight scientific figure PDFs and four LaTeX table files. |
| `apss_source.zip` | Manuscript and required figures and tables, with flat filenames for upload. |
| `REPRODUCIBILITY.md` | Scientific verification record and pinned analysis versions. |
| `reproducibility_manifest.json` | Reviewed package hashes and links to the scientific exports. |

The cover letter and compilation files are excluded from Git and the upload
archives. References are embedded in `main.tex`; no BibTeX step is needed.

## Rebuild and verify

From this folder, with Tectonic available:

```bash
python3 build_package.py
python3 verify_package.py
```

The builder compiles the PDF, regenerates the calibration table fragment from
the repository result table, and rebuilds the source ZIP. It does not update reviewed hashes. After inspecting an
intentional package change, run:

```bash
python3 build_package.py --record-reviewed-hashes
python3 verify_package.py
```

The verifier checks file hashes, figures against their pinned scientific exports,
archive contents, figure/table citation order, and the calibration files against
the manuscript's cited repository commit. Hash review does not replace
numerical regeneration; use the commands in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
The builder does not change catalogue data or scientific results.

## Submission notes

The manuscript includes author details, declarations, and disclosure of AI
assistance. Confirm these statements and the affiliation before submission.
Review the portal-generated PDF: a different compiler can change its layout.

The proposed article type is Research Article. Check the journal's current
[submission instructions](https://link.springer.com/journal/10509/submission-guidelines),
[catalogue collection](https://link.springer.com/collections/diddgecaeb), and
[publication options](https://link.springer.com/journal/10509/how-to-publish-with-us)
before choosing portal settings or a publication route.

The calibration calculation is linked through repository commit
`77908cdaadb5898e5f2e1d2d353cf99d2a3a26ac`, alongside the other scientific
code and data. No separate supplementary upload is needed. Submit `main.pdf`
and `apss_source.zip` in the manuscript fields; supply the cover letter separately.
