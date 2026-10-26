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
