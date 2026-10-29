"""Apply reviewed identity and provenance metadata to every catalogue version."""
from pathlib import Path
import json

import pandas as pd

from src.source_provenance import load_source_provenance_registry
from src.standardize_data import add_eddington_ratio_consistency


ROOT = Path(__file__).resolve().parents[1]
IDENTITY_FIELDS = ('scientific_identity_status', 'scientific_identity_issue_group')
JADES_SOURCE = 'juodzbalis25_jades_blagn'
JADES_PROVENANCE_FIELDS = (
    'source_paper_version', 'source_url', 'source_doi',
    'source_archive_url', 'source_archive_sha256',
)


def normalize_boolean_flags(frame):
    """Export boolean flags consistently, preserving unknown values as missing."""
    result = frame.copy()
    tokens = {"true": True, "false": False, "1": True, "0": False,
              "1.0": True, "0.0": False}
    for field in result:
        if not field.endswith("_flag") or field in {"quality_flag", "edd_ratio_consistency_flag"}:
            continue
        def parse(value):
            if pd.isna(value):
                return pd.NA
            token = str(value).strip().lower()
            if token not in tokens:
                raise ValueError(f"Invalid boolean flag {field}: {value!r}")
            return tokens[token]
        result[field] = result[field].map(parse).astype("boolean")
    return result


def update_preferred_measurement_reasons(measurements):
    """Remove singleton claims when a version now retains alternatives."""
    result = measurements.copy()
    multiple = result.groupby("physical_object_id").measurement_id.transform("size").gt(1)
    stale = (multiple & result.preferred_measurement_flag
             & result.preferred_measurement_reason.str.startswith("only ", na=False))
    result.loc[stale, "preferred_measurement_reason"] = (
        "prior-adopted measurement retained for continuity; alternative measurements remain available"
    )
    return result


def annotate_scientific_identity(measurements, pair_reviews):
    """Mark all measurements of an object implicated by an open reviewed pair."""
    groups = {}
    by_id = measurements.set_index('measurement_id')
    for pair in pair_reviews:
        group = pair['issue_group']
        if not group:
            continue
        for mid in (pair['left'], pair['right']):
            if mid not in by_id.index:
                raise ValueError(f'Identity audit refers to an unknown measurement: {mid}')
            oid = by_id.loc[mid, 'physical_object_id']
            if oid in groups and groups[oid] != group:
                raise ValueError('Overlapping scientific identity groups require review')
            groups[oid] = group
    result = measurements.copy()
    result['scientific_identity_issue_group'] = result.physical_object_id.map(groups).fillna('')
    result['scientific_identity_status'] = result.scientific_identity_issue_group.map(
        lambda group: 'unresolved' if group else 'no_open_issue_recorded',
    )
    return result


def apply_catalogue_quality(measurements, *, root=ROOT):
    """Add diagnostics without changing measurements, eligibility or assembly identities."""
    fixture = json.loads((root/'data/validation/redshift_identity_checks.json').read_text())
    result = annotate_scientific_identity(measurements, fixture['pair_reviews'])
    result = add_eddington_ratio_consistency(result)
    registry = load_source_provenance_registry(root/'data/source_provenance_registry.csv')
    source = registry.loc[registry.source_key.eq(JADES_SOURCE) & registry.source_role.eq('primary_measurement')]
    if len(source) != 1:
        raise ValueError('JADES metadata requires exactly one registered primary source')
    jades = result.source_key.eq(JADES_SOURCE)
    for field in JADES_PROVENANCE_FIELDS:
        result.loc[jades, field] = source.iloc[0][field]
    # The archive was subsequently verified; its verification date is not the
    # unknown date of the original catalogue extraction.
    return result
