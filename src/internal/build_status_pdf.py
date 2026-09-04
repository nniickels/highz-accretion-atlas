"""Compile the original-format repository status document."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/archive/project-history/highz_accretion_atlas_status.tex"
OUTPUT = ROOT / "docs/archive/project-history/highz_accretion_atlas_status.pdf"


def build() -> None:
    """Compile the existing ignored local status document in place."""
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Local ignored status source is required: {SOURCE}")
    tectonic = shutil.which("tectonic")
    if tectonic is None:
        raise RuntimeError("Tectonic is required to build the repository status PDF")
    subprocess.run([tectonic, SOURCE.name], cwd=SOURCE.parent, check=True)
    if not OUTPUT.is_file():
        raise FileNotFoundError(OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} from {SOURCE.relative_to(ROOT)}")


def main() -> None:
    build()


if __name__ == "__main__":
    main()
