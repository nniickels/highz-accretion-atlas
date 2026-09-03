"""Build the repository status PDF from canonical v3 products."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/archive/project-history/highz_accretion_atlas_status.pdf"
BLUE = colors.HexColor("#176B87")
ORANGE = colors.HexColor("#B66A1E")
GRAY = colors.HexColor("#4B5563")


def _footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(0.72 * inch, 0.42 * inch, "High-Redshift Accretion Atlas - repository status")
    canvas.drawRightString(7.78 * inch, 0.42 * inch, f"Page {document.page}")
    canvas.restoreState()


def _figure(path: str, caption: str, *, width: float = 7.0 * inch) -> list[object]:
    image_path = ROOT / path
    if not image_path.is_file():
        raise FileNotFoundError(image_path)
    image = Image(str(image_path))
    ratio = image.imageHeight / image.imageWidth
    image.drawWidth = width
    image.drawHeight = width * ratio
    return [
        image,
        Spacer(1, 5),
        Paragraph(caption, STYLES["Caption"]),
        Spacer(1, 10),
    ]


STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle(
    "TitleAtlas", parent=STYLES["Title"], fontName="Helvetica-Bold",
    fontSize=22, leading=26, textColor=BLUE, alignment=TA_CENTER, spaceAfter=8,
))
STYLES.add(ParagraphStyle(
    "SubtitleAtlas", parent=STYLES["Heading2"], fontName="Helvetica",
    fontSize=13, leading=17, textColor=GRAY, alignment=TA_CENTER, spaceAfter=16,
))
STYLES.add(ParagraphStyle(
    "H1Atlas", parent=STYLES["Heading1"], fontName="Helvetica-Bold",
    fontSize=15, leading=18, textColor=BLUE, spaceBefore=5, spaceAfter=8,
))
STYLES.add(ParagraphStyle(
    "BodyAtlas", parent=STYLES["BodyText"], fontName="Helvetica",
    fontSize=9.4, leading=13.2, textColor=colors.HexColor("#222222"), spaceAfter=7,
))
STYLES.add(ParagraphStyle(
    "Caption", parent=STYLES["BodyText"], fontName="Helvetica-Oblique",
    fontSize=8.3, leading=11, textColor=GRAY, spaceAfter=5,
))


def p(text: str) -> Paragraph:
    return Paragraph(text, STYLES["BodyAtlas"])


def h(text: str) -> Paragraph:
    return Paragraph(text, STYLES["H1Atlas"])


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=letter,
        rightMargin=0.65 * inch, leftMargin=0.65 * inch,
        topMargin=0.62 * inch, bottomMargin=0.62 * inch,
        title="The High-Redshift Accretion Atlas - Repository Status",
        author="Repository status document",
    )
    story: list[object] = [
        Spacer(1, 0.15 * inch),
        Paragraph("The High-Redshift Accretion Atlas", STYLES["TitleAtlas"]),
        Paragraph("A Tour of the Final Catalogue and Paper-Ready Results", STYLES["SubtitleAtlas"]),
        Paragraph("Repository status document - 2 September 2026", STYLES["Caption"]),
        Spacer(1, 10),
        h("Executive summary"),
        p(
            "Versions identify nested scientific datasets rather than software releases. "
            "v1 is the complete analysis of the original 23-object JADES broad-line AGN "
            "catalogue; v2 applies the same analysis to 112 comparable broad-line AGN; "
            "and v3 is the final JWST-identified heterogeneous atlas within the "
            "27 August 2026 source-family review cutoff. It contains 142 measurements, "
            "133 physical objects, and 132 host systems."
        ),
        p(
            "All three datasets use the same corrected identity rules, cosmology, growth "
            "model, uncertainty propagation, comparison policy, and visual grammar. In "
            "v3, 112 objects support numerical growth inference and 21 remain visible as "
            "explicit no-inference cases. Results are diagnostic comparisons under stated "
            "assumptions, not evidence for a unique seed or accretion history."
        ),
        h("Canonical dataset scopes"),
    ]
    table = Table([
        ["Version", "Scope", "Measurements", "Objects", "Hosts", "Numeric"],
        ["v1", "Original JADES BLAGN", "23", "23", "23", "23"],
        ["v2", "Expanded comparable BLAGN", "119", "112", "111", "112"],
        ["v3", "JWST-identified atlas", "142", "133", "132", "112"],
    ], colWidths=[0.55*inch, 2.55*inch, 0.82*inch, 0.65*inch, 0.58*inch, 0.62*inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#B9C2C9")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F3F6F7")]),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTSIZE", (0,0), (-1,-1), 8.2),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.extend([table, Spacer(1, 10), p(
        "Canonical catalogues live under <font name='Courier'>data/processed/&lt;version&gt;/</font>; "
        "identity products under <font name='Courier'>data/crossmatch/&lt;version&gt;/</font>; "
        "and numerical and visual products under <font name='Courier'>results/&lt;version&gt;/</font>."
    ), PageBreak()])

    story.extend([h("The final catalogue"), p(
        "The landscape separates growth-eligible preferred objects from retained catalogue-only "
        "evidence records. Alternate literature measurements are preserved, but one documented "
        "preferred measurement drives each object-level result."
    )])
    story.extend(_figure(
        "results/v3/figures/v3_catalogue_growth_landscape.png",
        "<b>Figure 1.</b> Final v3 catalogue landscape. Heterogeneous classes remain visually "
        "distinct and unsupported masses are not invented.", width=7.0*inch,
    ))
    story.extend([PageBreak(), h("Growth model and complete object coverage"), p(
        "The atlas evaluates a Dayal-style exponential black-hole growth relation with cosmic "
        "time from a flat Planck-style cosmology. The baseline uses seed redshift 30, radiative "
        "efficiency 0.1, and no merger boost. It solves both for the lifetime-average Eddington "
        "ratio at fixed seed mass and for seed mass at fixed accretion history."
    )])
    story.extend(_figure(
        "results/v3/figures/v3_all_object_growth_tracks.png",
        "<b>Figure 2.</b> All 112 supported masses appear against reference tracks; the lower "
        "panel retains the redshifts and classes of all 23 no-inference objects.", width=7.0*inch,
    ))
    story.extend([p(
        "A separate full-assumption companion preserves the historical v1 grid: three seed "
        "masses crossed with three Eddington fractions, four constant efficiencies, and two "
        "merger boosts (72 curves). It is stored as "
        "<font name='Courier'>results/v3/figures/"
        "v3_all_object_growth_tracks_full_assumptions.png</font>."
    )])
    story.extend([PageBreak(), h("Class-aware growth pressure"), p(
        "Global ranks are navigation aids only. Scientific comparisons are retained within "
        "object class and mass-comparability group, and pooled demographic inference is "
        "explicitly disallowed."
    )])
    story.extend(_figure(
        "results/v3/figures/v3_class_aware_growth_pressure.png",
        "<b>Figure 3.</b> Required accretion and seed-mass pressure by object class. The "
        "distributions are descriptive because the source selections are heterogeneous.",
    ))
    story.extend([PageBreak(), h("Uncertainty and duty-cycle diagnostics"), p(
        "Every eligible measurement and object has 10,000 deterministic Monte Carlo draws from "
        "reported asymmetric black-hole mass uncertainties. Statistical errors remain separate "
        "from source-specific virial systematics. Two-state histories retain duty cycles above "
        "one as evidence that a fixed burst scenario is insufficient."
    )])
    story.extend(_figure(
        "results/v3/figures/v3_monte_carlo_summary.png",
        "<b>Figure 4.</b> Monte Carlo pressure summary for all 112 numerical objects, with an "
        "explicit accounting of the 23 unavailable cases.",
    ))
    story.extend([PageBreak(), h("Compatibility across assumption families"), p(
        "Compatibility is evaluated object by object across four seed families, three spin "
        "cases, two merger cases, and three lifetime-average Eddington ratios. Unsupported "
        "objects have unavailable values rather than false incompatibilities."
    )])
    story.extend(_figure(
        "results/v3/figures/v3_compatibility_summary.png",
        "<b>Figure 5.</b> Class-specific compatibility fractions across seed, spin, merger, "
        "and accretion assumptions.",
    ))
    story.extend([PageBreak(), h("From catalogue scale to individual objects"), p(
        "Each of the 133 v3 objects has an f_Edd-mass sheet and a seed-redshift-mass panel. The "
        "112 supported objects receive numerical products; the remaining 21 receive status "
        "panels explaining why no inference is made."
    )])
    story.extend(_figure(
        "results/v3/parameter_maps/fedd_mass_maps/v3_fedd_mass_map_hza-gn-38509.png",
        "<b>Figure 6.</b> GN-38509 f_Edd-mass sheet. Six spin/merger combinations show "
        "which seed and accretion choices reproduce the preferred mass.",
    ))
    story.extend([PageBreak(), h("Measurement choice and provenance"), p(
        "Thirteen eligible alternate measurements are compared with preferred rows. Source "
        "keys, table locations, publication versions, archive records, uncertainties, identity "
        "decisions, and caveats remain available beside derived quantities. The follow-up "
        "matrix retains all 133 objects (112 ranked; 21 explicitly unranked), and the source "
        "caveat table covers all 11 admitted families."
    )])
    story.extend(_figure(
        "results/v3/figures/v3_measurement_sensitivity.png",
        "<b>Figure 7.</b> Sensitivity of mass and required accretion to retained alternate "
        "measurements.",
    ))
    story.extend([PageBreak(), h("Repository workflow and verification"), p(
        "Public workflows are the ordered notebooks under <font name='Courier'>scripts/</font>. "
        "They call testable Python implementation under <font name='Courier'>src/internal/</font>. "
        "Only the source-admission builders required for exact reconstruction retain historical "
        "names under <font name='Courier'>src/internal/compatibility/</font>. Obsolete release-era "
        "data, results, manifests, and documentation were removed from the public tree and remain "
        "recoverable from Git history."
    )])
    workflow = Table([
        ["Order", "Notebook", "Purpose"],
        ["1", "00_process_catalogues.ipynb", "Materialize v1/v2/v3 catalogues"],
        ["2", "01_generate_science.ipynb", "Rankings, uncertainty, duty cycles"],
        ["3", "02_generate_figures.ipynb", "Paper summary figures"],
        ["4", "03_generate_atlas.ipynb", "Atlases, result inventory, manifests"],
        ["5", "04_verify.ipynb", "Provenance, manifests, exact reproduction, tests"],
    ], colWidths=[0.5*inch, 2.45*inch, 3.6*inch])
    workflow.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ORANGE),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#C8C8C8")),
        ("FONTSIZE", (0,0), (-1,-1), 8.3),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.extend([workflow, Spacer(1, 10), p(
        "The final verification gate checks strict v1 < v2 < v3 measurement membership, "
        "catalogue and analysis cardinalities, the result inventory, canonical SHA-256 manifests, exact in-memory "
        "CSV reproduction, 10,000-draw products, compatibility coverage, image resolution, "
        "and two per-object gallery panels for every catalogue object."
    ), h("Literature boundary and next dataset"), p(
        "The canonical source-family review cutoff is 27 August 2026. v3 is final within its "
        "declared admitted-source scope, not an evergreen exhaustive census. Relevant sources "
        "that require new adapters or comparability policy are listed in "
        "<font name='Courier'>docs/current/literature-scope.md</font> and will create a new "
        "dataset version rather than mutate v3."
    ), h("Current status"), p(
        "The migration is structurally complete: v1/v2/v3 are the public datasets; canonical "
        "data, tables, figures, galleries, and manifests are retained; implementation is Python "
        "under src; user workflows are notebooks; contribution history and this status document "
        "are versioned; and the required historical source-admission bridge is isolated as "
        "internal compatibility code."
    )])

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


def main() -> None:
    build()


if __name__ == "__main__":
    main()
