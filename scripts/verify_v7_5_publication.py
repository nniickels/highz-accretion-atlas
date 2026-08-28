"""Verify v7.5 manuscript and publication-readiness artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.release_verification import require_clean_worktree, verify_artifact_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases/v7.5-publication-manifest.json"
ARTIFACTS = {
    "CITATION.cff", "LICENSE", "CONTRIBUTING.md",
    "docs/v7.5-release-notes.md", "docs/v7.5-claim-audit.md",
    "docs/v7.5-citation-audit.md", "paper/README.md",
    "paper/highz_accretion_atlas_v7_5.tex",
    "paper/highz_accretion_atlas_v7_5.pdf",
}


def verify_publication_contract() -> None:
    pdf = ROOT / "paper/highz_accretion_atlas_v7_5.pdf"
    if not pdf.read_bytes().startswith(b"%PDF-") or pdf.stat().st_size < 1_000_000:
        raise AssertionError("Authoritative manuscript PDF is missing or unexpectedly small")
    tex = (ROOT / "paper/highz_accretion_atlas_v7_5.tex").read_text()
    for claim in ["234 / 219 / 218", "209 / 196", "588 / 6", "JADES-NS-GS00099671"]:
        if claim not in tex:
            raise AssertionError(f"Authoritative manuscript is missing audited claim: {claim}")
    for figure in [
        "v7_5_catalogue_growth_landscape.png", "v7_5_class_aware_growth_pressure.png",
        "v7_5_uncertainty_robustness.png", "v7_5_measurement_sensitivity.png",
    ]:
        if figure not in tex:
            raise AssertionError(f"Authoritative manuscript is missing figure: {figure}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.5 publication")
    manifest = json.loads(MANIFEST_PATH.read_text())
    if manifest.get("release") != "v7.5-publication" or manifest.get("manuscript_pages") != 7:
        raise AssertionError("v7.5 publication manifest metadata mismatch")
    verify_artifact_manifest(
        root=ROOT, artifacts=manifest.get("artifacts"), expected_paths=ARTIFACTS,
        release_label="v7.5 publication",
    )
    verify_publication_contract()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.5 publication")
    print("Verified v7.5 manuscript, metadata, claim audit, citation audit, and hashes")


if __name__ == "__main__":
    main()
