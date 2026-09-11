"""Regenerate the embedded AAS bibliography from references.bib using Tectonic.

Embedding the official BibTeX output keeps the manuscript portable to Overleaf
without another bibliography compilation there. Run from any working directory.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
MANUSCRIPT = PAPER / "highz_accretion_atlas_v3.tex"


def update(manuscript):
    source = manuscript.read_text()
    # Expand table fragments to preserve actual first-citation order for a/b labels.
    expanded = re.sub(
        r"\\tableinput\{([^}]+)\}",
        lambda m: (PAPER / m[1]).read_text(), source,
    )
    keys = list(dict.fromkeys(
        key.strip()
        for match in re.finditer(r"\\cite(?:p|t|author|yearpar|year)?(?:\[[^\]]*\])*\{([^}]+)\}", expanded)
        for key in match[1].split(",")
    ))
    if not keys:
        raise ValueError("No manuscript citations found")
    with tempfile.TemporaryDirectory(prefix="atlas-bibliography-") as tmp:
        work = Path(tmp)
        for name in ("references.bib", "aasjournalv7.1.bst"):
            shutil.copyfile(PAPER / name, work / name)
        (work / "references.tex").write_text(
            r"\documentclass{article}\usepackage[authoryear]{natbib}\usepackage{hyperref}"
            r"\renewcommand{\bibinfo}[2]{}\begin{document}"
            + r"\nocite{" + ",".join(keys) + "}\n"
            + r"\bibliographystyle{aasjournalv7.1}\bibliography{references}\end{document}"
        )
        subprocess.run(["tectonic", "--keep-intermediates", "references.tex"], cwd=work, check=True)
        bibliography = (work / "references.bbl").read_text().strip()
    new_source, count = re.subn(
        r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}",
        lambda _: bibliography, source, flags=re.S,
    )
    if count != 1:
        raise ValueError(f"Expected one bibliography, found {count}")
    manuscript.write_text(new_source)
    print(f"Updated {len(keys)} AAS references in {manuscript.name}")


def main():
    for manuscript in (MANUSCRIPT, PAPER / "supplementary_material.tex"):
        update(manuscript)


if __name__ == "__main__":
    main()
