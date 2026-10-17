"""Reviewed October 2026 admissions; source-native inputs remain immutable."""

from __future__ import annotations
import re
import numpy as np
import pandas as pd
from src.models import cosmic_time_gyr
from src.internal.compatibility.v7_admission import (
    validate_v7_admission,
    validate_v7_observables,
)
from src.internal.compatibility.v7_core_catalogue import (
    _set_eligibility,
    _build_host_systems,
    _build_strata,
)
from src.internal.compatibility.v7_catalogue import (
    _aggregate_objects_with_preferred_evidence,
)

# Hashes identify the pinned archive or publisher payload, not generated data.
METADATA = {
    "taylor25_capers_lrd_z9": dict(
        version="arXiv:2505.04609v4",
        url="https://arxiv.org/html/2505.04609v4",
        doi="10.3847/2041-8213/ade789",
        archive="https://arxiv.org/src/2505.04609v4",
        sha="b176066077fcf145f797d86124a8b97fa65dbf3dce709d25783fec57ad92a885",
        survey="CAPERS",
        field="COSMOS",
        status="secure",
        locator="Table 1; Section IV.2",
        basis="Broad Hbeta S/N about 10 with narrower forbidden lines; source canonical virial mass",
        caveats="prism_resolution;gas_enshrouded_lrd;dust_alternatives_correlated;high_redshift_virial_calibration;coordinate_frame_unreported",
    ),
    "tripodi25_canucs_lrd": dict(
        version="Nature Communications 16 9830 (2025); published 2025-11-19",
        url="https://www.nature.com/articles/s41467-025-65070-x",
        doi="10.1038/s41467-025-65070-x",
        archive="https://www.nature.com/articles/s41467-025-65070-x",
        sha="b85e970ba757e82925de7c2f97ca8b68eeecd97ebacd2e794eefa830f9764b92",
        survey="CANUCS",
        field="MACS1149",
        status="secure",
        locator="Abstract mass interval; Supplementary Tables 1 and 3; Methods",
        basis="Broad Hbeta S/N 6 without broad OIII; NIV and CIV corroboration",
        caveats="high_redshift_virial_calibration;source_corrected_lensing;mass_dust_treatment_unspecified;morishita_lens_model_differs",
    ),
    "schindler25_j1007": dict(
        version="Nature Astronomy 9 1732-1744 (2025); published 2025-09-17",
        url="https://www.nature.com/articles/s41550-025-02660-1",
        doi="10.1038/s41550-025-02660-1",
        archive="https://media.springernature.com/full/springer-static/esm/art%3A10.1038%2Fs41550-025-02660-1/MediaObjects/41550_2025_2660_Tab1_ESM.jpg",
        sha="b251f05ff8e4aa64c5842209d6950b8aa3b31ceb4845adc588d82d75f622d673",
        survey="JWST GO-2073",
        field="J1007",
        status="secure",
        locator="Extended Data Tables 1-3; Methods SMBH mass",
        basis="Source secure type-1 broad Hbeta AGN with high-ionization evidence",
        caveats="high_redshift_virial_calibration;dust_alternative_correlated;total_hbeta_luminosity_recipe;redshift_error_text_table_discrepancy",
    ),
    "takechi26_macs0416_y1": dict(
        version="arXiv:2605.14922v1",
        url="https://arxiv.org/html/2605.14922v1",
        doi="10.48550/arXiv.2605.14922",
        archive="https://arxiv.org/src/2605.14922v1",
        sha="f36a625bc25c4681a777b79229175ade06555b312d76392b8509cefdbf6f169c",
        survey="DREAMS;CANUCS",
        field="MACS0416",
        status="candidate",
        locator="Sections II.2.2, III.3, IV.2.1; Figures 6-7",
        basis="One D2 spaxel meets broad Hbeta AIC criterion; weak flux and only about 1-sigma width separation from OIII leave outflow ambiguity",
        caveats="weak_broad_hbeta;outflow_ambiguity;mass_interval_confidence_unspecified;calibration_scatter_inclusion_unspecified;host_centroid_not_nucleus;source_corrected_lensing",
    ),
    "fudamoto25_sapphires_z847": dict(
        version="arXiv:2503.15597v1",
        url="https://arxiv.org/html/2503.15597v1",
        doi="10.48550/arXiv.2503.15597",
        archive="https://arxiv.org/src/2503.15597v1",
        sha="1802281772393b71361020f936ba2457eca22c7668fa5ee5696257377add9445",
        survey="SAPPHIRES",
        field="MACS0416 parallel",
        status="candidate",
        locator="Table 1; Sections II, III.3, IV.2; Table 2 note a",
        basis="LRD colors and Hbeta width 1010+/-190 km/s; peak S/N only 2.5 and foreground-contaminated compactness",
        caveats="no_published_mbh;weak_hbeta_peak;foreground_neighbour_identity_unresolved;compactness_contaminated;no_broad_narrow_decomposition",
    ),
}


def log_interval(mass, minus, plus):
    """Convert a linear central value and its endpoint distances to dex."""
    if not 0 < minus < mass or plus <= 0:
        raise ValueError("Mass interval must have positive lower endpoint and errors")
    return (
        np.log10(mass),
        np.log10(mass / (mass - minus)),
        np.log10((mass + plus) / mass),
    )


def sexagesimal(value, *, ra=False):
    first, minutes, seconds = map(float, value.split(":"))
    sign = -1 if value.startswith("-") else 1
    return sign * (abs(first) + minutes / 60 + seconds / 3600) * (15 if ra else 1)


def source_records(inputs):
    """Read each source under its own units and uncertainty conventions."""

    def first(name):
        frame = inputs[name]
        if len(frame) != 1:
            raise ValueError(f"{name} requires exactly one source target")
        return frame.iloc[0]

    r = first("capers_expansion")
    records = [
        dict(
            source_key=r.source_key,
            measurement_id="CAPERSLRDz9_taylor25",
            object_id=r.object_id,
            ra_deg=r.ra_deg,
            dec_deg=r.dec_deg,
            redshift=r.redshift,
            redshift_err=r.redshift_err,
            mass=(r.log_mbh_msun, r.log_mbh_err_minus, r.log_mbh_err_plus),
            width=(
                r.hbeta_broad_fwhm_km_s,
                r.hbeta_broad_fwhm_err,
                r.hbeta_broad_fwhm_err,
            ),
            flux=(
                r.hbeta_broad_flux * 1e-20,
                r.hbeta_broad_flux_err * 1e-20,
                r.hbeta_broad_flux_err * 1e-20,
            ),
            aliases=r.published_aliases,
            phenotype="lrd;compact;red",
            lensing="not_reported",
            mu=np.nan,
            uncertainty=r.mbh_formal_uncertainty_kind,
        )
    ]
    r = first("canucs_expansion")
    records.append(
        dict(
            source_key=r.source_key,
            measurement_id=r.measurement_id,
            object_id=r.object_id,
            ra_deg=sexagesimal(r.ra_sexagesimal, ra=True),
            dec_deg=sexagesimal(r.dec_sexagesimal),
            redshift=r.redshift,
            redshift_err=r.redshift_err,
            mass=log_interval(r.mbh_msun, r.mbh_err_minus_msun, r.mbh_err_plus_msun),
            width=(r.broad_fwhm_km_s, r.broad_fwhm_err_minus, r.broad_fwhm_err_plus),
            flux=(29.8e-19, 4.7e-19, 4.7e-19),
            aliases="5112687",
            phenotype="lrd;compact",
            lensing="lensed",
            mu=r.lensing_mu,
            uncertainty="reported_16th_84th_percentile_interval_calibration_decomposition_unspecified",
        )
    )
    frame = inputs["j1007_expansion"]
    if set(frame.dust_treatment) != {"observed", "dust_corrected"}:
        raise ValueError("J1007 requires observed and correlated dust alternative")
    r = frame.loc[frame.dust_treatment.eq("observed")].iloc[0]
    records.append(
        dict(
            source_key=r.source_key,
            measurement_id=r.measurement_id,
            object_id=r.object_id,
            ra_deg=r.ra_deg,
            dec_deg=r.dec_deg,
            redshift=r.redshift,
            redshift_err=r.redshift_err_plus,
            mass=log_interval(
                r.mass_1e7_msun * 1e7,
                r.mass_err_minus_1e7_msun * 1e7,
                r.mass_err_plus_1e7_msun * 1e7,
            ),
            width=(r.broad_fwhm_km_s, r.broad_fwhm_err_minus, r.broad_fwhm_err_plus),
            flux=(622.95e-20, 75.32e-20, 82.82e-20),
            aliases="J1007-AGN",
            phenotype="lrd",
            lensing="unlensed",
            mu=np.nan,
            uncertainty="posterior_16th_84th_percentiles",
            systematic=0.43,
        )
    )
    r = first("y1_expansion")
    records.append(
        dict(
            source_key="takechi26_macs0416_y1",
            measurement_id="MACS0416Y1_takechi26",
            object_id=r.source_id,
            ra_deg=sexagesimal(r.ra_hms, ra=True),
            dec_deg=sexagesimal(r.dec_dms),
            redshift=r.redshift,
            redshift_err=np.nan,
            mass=log_interval(
                r.mbh_1e6_msun * 1e6, r.mbh_err_minus * 1e6, r.mbh_err_plus * 1e6
            ),
            width=(r.hbeta_fwhm_kms, r.hbeta_fwhm_err_minus, r.hbeta_fwhm_err_plus),
            flux=(
                r.hbeta_broad_flux_1e19_erg_s_cm2 * 1e-19,
                r.hbeta_broad_flux_err_minus * 1e-19,
                r.hbeta_broad_flux_err_plus * 1e-19,
            ),
            aliases=r.aliases,
            phenotype="clumpy",
            lensing="lensed",
            mu=r.magnification,
            uncertainty=r.mass_error_definition,
        )
    )
    r = first("sapphires_expansion")
    records.append(
        dict(
            source_key=r.source_key,
            measurement_id=r.measurement_id,
            object_id=r.object_id,
            ra_deg=r.ra_deg,
            dec_deg=r.dec_deg,
            redshift=r.redshift,
            redshift_err=np.nan,
            mass=(np.nan, np.nan, np.nan),
            width=(r.hbeta_fwhm_kms, r.hbeta_fwhm_err_kms, r.hbeta_fwhm_err_kms),
            flux=(
                r.hbeta_flux_1e19_erg_s_cm2 * 1e-19,
                r.hbeta_flux_err_1e19_erg_s_cm2 * 1e-19,
                r.hbeta_flux_err_1e19_erg_s_cm2 * 1e-19,
            ),
            aliases="ID-8760;8760",
            phenotype="lrd",
            lensing="not_reported",
            mu=np.nan,
            uncertainty="not_published",
        )
    )
    return records


def build_additions(inputs, columns):
    rows = []
    for r in source_records(inputs):
        meta = METADATA[r["source_key"]]
        mass, minus, plus = r["mass"]
        has = np.isfinite(mass)
        ident = re.sub(r"[^A-Z0-9]+", "-", r["object_id"].upper()).strip("-")
        row = {column: np.nan for column in columns}
        row.update(
            catalogue_release="complete-catalogue",
            measurement_id=r["measurement_id"],
            object_id=r["object_id"],
            physical_object_id="HZA-" + ident,
            host_system_id="HZS-" + ident,
            ra_deg=r["ra_deg"],
            dec_deg=r["dec_deg"],
            redshift=r["redshift"],
            redshift_err=r["redshift_err"],
            redshift_kind="spec",
            cosmic_time_gyr=float(cosmic_time_gyr(r["redshift"])),
            survey=meta["survey"],
            program=meta["survey"],
            field=meta["field"],
            object_class="broad_line_agn",
            evidence_status=meta["status"],
            evidence_status_basis=meta["basis"],
            spectroscopic_type="type1_broad_line"
            if has
            else "type1_broad_line_candidate",
            selection_channels="broad_hbeta;photometric_sed"
            if "lrd" in r["phenotype"]
            else "broad_hbeta;host_selected",
            selection_channel="broad_hbeta",
            phenotype_tags=r["phenotype"],
            source_key=r["source_key"],
            source_table=meta["locator"],
            source_paper_version=meta["version"],
            source_url=meta["url"],
            source_doi=meta["doi"],
            source_archive_url=meta["archive"],
            source_archive_sha256=meta["sha"],
            extraction_date="2026-10-17",
            extraction_date_status="recorded",
            selection_criteria="JWST source identification and source-local accretion screen; see extraction notes",
            source_caveat_tags=meta["caveats"],
            notes=meta["basis"],
            quality_flag=meta["status"],
            detection_evidence=meta["basis"],
            log_mbh_msun_std=mass,
            log_mbh_err_plus_std=plus,
            log_mbh_err_minus_std=minus,
            log_mbh_err_plus=plus,
            log_mbh_err_minus=minus,
            mbh_method="single-epoch-virial-hbeta-greeneho2005"
            if has
            else "not_published",
            mbh_interpretation_tag="source_published_virial_mass"
            if has
            else "no_numeric_black_hole_mass_published",
            mbh_formal_uncertainty_kind=r["uncertainty"],
            mbh_statistical_uncertainty_kind=r["uncertainty"],
            log_mbh_systematic_dex=r.get("systematic", np.nan),
            mbh_systematic_kind="separate_virial_calibration_scale"
            if "systematic" in r
            else "not_quantified_as_single_scale",
            mbh_systematic_applied_flag=False,
            mass_comparability_group="virial_balmer_single_epoch"
            if has
            else "no_numeric_mass",
            conditional_mass_flag=False,
            conditional_mass_reason="",
            primary_mass_comparison_flag=has,
            primary_mass_comparison_reason="balmer_single_epoch_primary_stratum"
            if has
            else "no_canonical_numeric_mass",
            host_property_scope="not_published",
            mstar_method="",
            lbol_method="",
            edd_ratio_method="",
            identity_resolution_status="resolved",
            host_system_assignment_status="source_verified_single_object_host",
            preferred_measurement_flag=True,
            preferred_measurement_reason="only admitted measurement; correlated modeling alternatives retained as observables",
            match_method="reviewed aliases and spherical position/redshift screen in both v2 and v3",
            match_reference="source-specific extraction note and identity fixture; no supported existing match",
            published_aliases=r["aliases"],
            lensing_status=r["lensing"],
            lensing_mu=r["mu"],
            lensing_mass_correction_status="applied"
            if r["lensing"] == "lensed"
            else "not_required",
            lensing_provenance="Source explicitly corrects published mass; observed line flux remains magnified"
            if r["lensing"] == "lensed"
            else "Field source; no magnification value adopted; SAPPHIRES source assesses negligible cluster magnification",
            missing_mstar_flag=True,
            missing_lbol_flag=True,
            missing_edd_ratio_flag=True,
            missing_lensing_flag=pd.isna(r["mu"]),
            broad_line_species="Hbeta",
            fwhm_instrument_corrected_flag=(
                np.nan if r["source_key"] == "tripodi25_canucs_lrd" else True
            ),
            lrd_flag="lrd" in r["phenotype"],
            lrd_definition=(
                "source-classified LRD phenotype"
                if "lrd" in r["phenotype"]
                else "source does not classify this galaxy as an LRD"
            ),
            dust_correction_applied_flag=False,
        )
        if r["source_key"] == "tripodi25_canucs_lrd":
            native = inputs["canucs_expansion"].iloc[0]
            row.update(
                log_lbol_erg_s_std=native.log_lbol_erg_s,
                log_lbol_err_plus_std=native.log_lbol_err,
                log_lbol_err_minus_std=native.log_lbol_err,
                log_lbol_err_plus=native.log_lbol_err,
                log_lbol_err_minus=native.log_lbol_err,
                lbol_method="source_3000A_bolometric_correction",
                edd_ratio_std=native.edd_ratio_reported,
                edd_ratio_method="source_correlated_lbol_and_mbh_factor_two_error",
                missing_lbol_flag=False,
                missing_edd_ratio_flag=False,
            )
            host = log_interval(
                native.mstar_msun,
                native.mstar_err_minus_msun,
                native.mstar_err_plus_msun,
            )
            row.update(
                log_mstar_msun_std=host[0],
                log_mstar_err_minus_std=host[1],
                log_mstar_err_plus_std=host[2],
                mstar_method="source_adopted_SED_model_envelope",
                host_property_scope="object_specific",
                missing_mstar_flag=False,
            )
        if r["source_key"] == "schindler25_j1007":
            native = (
                inputs["j1007_expansion"].query('dust_treatment == "observed"').iloc[0]
            )
            row.update(
                log_lbol_erg_s_std=native.log_lbol_erg_s,
                log_lbol_err_plus_std=native.log_lbol_err_plus,
                log_lbol_err_minus_std=native.log_lbol_err_minus,
                log_lbol_err_plus=native.log_lbol_err_plus,
                log_lbol_err_minus=native.log_lbol_err_minus,
                lbol_method="GH05_total_Hbeta_to_continuum_times_9.26",
                edd_ratio_std=native.edd_ratio,
                edd_ratio_method="source_correlated_lbol_and_mbh",
                missing_lbol_flag=False,
                missing_edd_ratio_flag=False,
            )
        if r["source_key"] == "taylor25_capers_lrd_z9":
            row["log_mstar_upper_limit_msun"] = 9.0
            row["host_property_scope"] = "object_specific"
        rows.append(row)
    result = pd.DataFrame(rows, columns=columns)
    for field in (
        "growth_ranking_eligible_flag",
        "growth_ranking_eligibility_reason",
        "primary_growth_ranking_flag",
        "primary_growth_ranking_reason",
    ):
        result[field] = result[field].astype(object)
    result = _set_eligibility(result)
    validate_v7_admission(result)
    return result


def build_observables(inputs):
    rows = []

    def add(
        r, name, values, unit, location=None, censoring="detection", uncertainty=None
    ):
        value, minus, plus = values
        if pd.isna(value):
            return
        rows.append(
            dict(
                observable_id=r["measurement_id"] + "__" + name,
                measurement_id=r["measurement_id"],
                object_id=r["object_id"],
                observable_name=name,
                value=value,
                err_plus=plus,
                err_minus=minus,
                censoring=censoring,
                unit=unit,
                uncertainty_kind="limit"
                if censoring != "detection"
                else (
                    "not_published"
                    if pd.isna(minus) and pd.isna(plus)
                    else (uncertainty or r["uncertainty"])
                ),
                source_location=location or METADATA[r["source_key"]]["locator"],
            )
        )

    for r in source_records(inputs):
        add(r, "log_mbh", r["mass"], "log10(Msun)")
        add(r, "hbeta_fwhm", r["width"], "km/s", uncertainty="source_reported_interval")
        add(
            r,
            "hbeta_flux_observed",
            r["flux"],
            "erg/s/cm2",
            uncertainty="source_reported_interval",
        )
        add(
            r,
            "lensing_mu",
            (
                r["mu"],
                0.01 if r["source_key"] == "tripodi25_canucs_lrd" else 0.02,
                0.08 if r["source_key"] == "tripodi25_canucs_lrd" else 0.01,
            ),
            "dimensionless",
            uncertainty="source_model_interval",
        )
        if r["source_key"] == "taylor25_capers_lrd_z9":
            for a in inputs["capers_alternatives"].to_dict("records"):
                add(
                    r,
                    "mass_alternative_" + a["estimate"],
                    (
                        a["log_mbh_msun"],
                        a["reported_error_dex"],
                        a["reported_error_dex"],
                    ),
                    "log10(Msun)",
                    a["source_locator"],
                    a["censoring"],
                    a["assumptions"],
                )
        if r["source_key"] == "schindler25_j1007":
            a = (
                inputs["j1007_expansion"]
                .query('dust_treatment == "dust_corrected"')
                .iloc[0]
            )
            add(
                r,
                "dust_corrected_log_mbh",
                log_interval(
                    a.mass_1e7_msun * 1e7,
                    a.mass_err_minus_1e7_msun * 1e7,
                    a.mass_err_plus_1e7_msun * 1e7,
                ),
                "log10(Msun)",
                "Extended Data Table 2; correlated dust-model alternative",
            )
        if r["source_key"] == "tripodi25_canucs_lrd":
            for a in inputs["canucs_variants"].to_dict("records"):
                for line in ("hbeta", "5100"):
                    add(
                        r,
                        "fit_" + a["fit"].replace(" ", "_") + "_" + line + "_mass",
                        (
                            a["log_mbh_" + line],
                            a["log_mbh_" + line + "_err"],
                            a["log_mbh_" + line + "_err"],
                        ),
                        "log10(Msun)",
                        "Supplementary Table 3; correlated fit alternative",
                    )
    result = pd.DataFrame(rows)
    validate_v7_observables(
        result, [r["measurement_id"] for r in source_records(inputs)]
    )
    return result


def append_expansion(complete, inputs):
    measurements = complete["measurements"].copy()
    additions = build_additions(inputs, list(measurements.columns))
    if set(additions.physical_object_id) & set(measurements.physical_object_id):
        raise ValueError("New source identity collision requires review")
    measurements = (
        pd.concat([measurements, additions], ignore_index=True)
        .sort_values(
            ["source_key", "redshift", "measurement_id"], ascending=[True, False, True]
        )
        .reset_index(drop=True)
    )
    objects = _aggregate_objects_with_preferred_evidence(measurements)
    result = dict(complete)
    result.update(
        measurements=measurements,
        objects=objects,
        host_systems=_build_host_systems(
            measurements, catalogue_release="complete-catalogue"
        ),
        strata=_build_strata(
            measurements, objects, catalogue_release="complete-catalogue"
        ),
    )
    for name, frame in [
        ("measurement_object_links", measurements),
        ("object_host_links", objects),
    ]:
        result[name] = frame[complete[name].columns].copy()
    aliases = additions[
        complete["aliases"].columns.intersection(additions.columns)
    ].copy()
    aliases["alias_kind"] = "source_object_id"
    result["aliases"] = pd.concat([complete["aliases"], aliases], ignore_index=True)
    obs = build_observables(inputs)
    obs.insert(0, "catalogue_release", "complete-catalogue")
    result["observables"] = pd.concat([complete["observables"], obs], ignore_index=True)
    validate_v7_observables(result["observables"], measurements.measurement_id)
    return result
