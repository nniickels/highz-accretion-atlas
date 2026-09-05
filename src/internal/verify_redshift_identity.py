"""Independent source-cell checks and a complete, non-automatic identity review.

An audit can run successfully while reporting unresolved identities. Use
--require-resolved for a publication gate; never equate a reproducible catalogue
with a scientifically reconciled object list.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'data/validation/redshift_identity_checks.json'


def separation_arcsec(left, right):
    """Independent haversine separation, stable even for coincident targets."""
    ra1, dec1, ra2, dec2 = np.deg2rad([
        left['ra_deg'], left['dec_deg'], right['ra_deg'], right['dec_deg'],
    ])
    h = np.sin((dec1-dec2)/2)**2 + np.cos(dec1)*np.cos(dec2)*np.sin((ra1-ra2)/2)**2
    return float(np.rad2deg(2*np.arcsin(np.sqrt(np.clip(h, 0, 1))))*3600)


def verify_redshift_identity(root: Path = ROOT, fixture: dict | None = None) -> dict:
    """Check all versions against reviewed cells and report unresolved pairs."""
    fixture = fixture if fixture is not None else json.loads((root / FIXTURE.relative_to(ROOT)).read_text())
    reference = fixture['measurements']
    ids = [r['measurement_id'] for r in reference]
    catalogue = pd.read_csv(root/'data/processed/v3/v3_accreting_measurements.csv').set_index('measurement_id')
    if len(ids) != len(set(ids)) or set(ids) != set(catalogue.index):
        raise AssertionError('Redshift audit must cover every measurement exactly once')
    registry = pd.read_csv(root/'data/source_provenance_registry.csv').query('source_role == "primary_measurement"').set_index('source_key')
    by_id = {r['measurement_id']: r for r in reference}
    count = 0
    for r in reference:
        if 'redshift' not in r['fields']:
            raise AssertionError('Every measurement needs independent redshift evidence')
        if r['registered_primary_archive_sha256'] != registry.loc[r['source_key'], 'source_archive_sha256']:
            raise AssertionError('Redshift audit registered source version differs')
        fields = set(r['fields']) | set(r['unavailable_fields'])
        if not {'redshift', 'ra_deg', 'dec_deg'} <= fields:
            raise AssertionError('Incomplete coordinate coverage accounting')
        if set(r['fields']) & set(r['unavailable_fields']):
            raise AssertionError('Source field cannot also be unavailable')
        for field, evidence in r['fields'].items():
            for key in ('evidence', 'source_url', 'source_archive_sha256', 'source_member', 'source_member_sha256', 'locator'):
                if not evidence.get(key):
                    raise AssertionError(f'Missing independent provenance {key}')
            for key in ('source_archive_sha256', 'source_member_sha256'):
                if len(evidence[key]) != 64 or set(evidence[key]) - set('0123456789abcdef'):
                    raise AssertionError('Invalid source evidence hash')
            count += 1
    for version in ('v1', 'v2', 'v3'):
        measurements = pd.read_csv(root/f'data/processed/{version}/{version}_accreting_measurements.csv').set_index('measurement_id')
        objects = pd.read_csv(root/f'data/processed/{version}/{version}_accreting_objects.csv')
        aliases = pd.read_csv(root/f'data/crossmatch/{version}/{version}_object_aliases.csv')
        links = pd.read_csv(root/f'data/crossmatch/{version}/{version}_measurement_object_links.csv').set_index('measurement_id')
        if not measurements.index.is_unique or set(links.index) != set(measurements.index) or not links.index.is_unique:
            raise AssertionError(f'{version}: invalid measurement/link identity coverage')
        expected_alias_ids = set(catalogue.index[catalogue.physical_object_id.isin(measurements.physical_object_id)])
        if set(aliases.measurement_id) != expected_alias_ids or not aliases.measurement_id.is_unique:
            raise AssertionError(f'{version}: incomplete alias identity coverage')
        for mid, actual in measurements.iterrows():
            ref = by_id[mid]
            if actual.source_key != ref['source_key'] or actual.object_id != ref['source_object_id']:
                raise AssertionError(f'{mid}: source-native identity differs')
            for field, evidence in ref['fields'].items():
                expected = evidence['expected']
                ok = actual[field] == expected if isinstance(expected, str) else pd.notna(actual[field]) and np.isclose(actual[field], expected, rtol=0, atol=1e-8)
                if not ok:
                    raise AssertionError(f'{version}/{mid}/{field}: {actual[field]!r} differs from source {expected!r}')
            for field in ref['unavailable_fields']:
                if pd.notna(actual[field]):
                    raise AssertionError(f'{mid}: newly populated coordinate requires source review')
            for field in ('physical_object_id', 'host_system_id', 'preferred_measurement_flag'):
                if actual[field] != links.loc[mid, field]:
                    raise AssertionError(f'{mid}: identity link disagrees with measurement')
        for _, alias in aliases.iterrows():
            actual = catalogue.loc[alias.measurement_id]
            for field in ('object_id', 'source_key', 'physical_object_id', 'host_system_id', 'redshift', 'ra_deg', 'dec_deg'):
                if not (pd.isna(alias[field]) and pd.isna(actual[field])) and alias[field] != actual[field]:
                    raise AssertionError(f'{alias.measurement_id}: alias {field} differs')
        preferred = measurements.loc[measurements.preferred_measurement_flag]
        if not preferred.physical_object_id.is_unique or set(preferred.physical_object_id) != set(measurements.physical_object_id) or not objects.physical_object_id.is_unique:
            raise AssertionError(f'{version}: each physical object needs exactly one preferred measurement')
        if set(objects.measurement_id) != set(preferred.index):
            raise AssertionError(f'{version}: object table differs from preferred measurements')
        for _, obj in objects.iterrows():
            row = preferred.loc[obj.measurement_id]
            for field in ('physical_object_id', 'host_system_id', 'source_key', 'object_id', 'redshift', 'ra_deg', 'dec_deg'):
                if not (pd.isna(obj[field]) and pd.isna(row[field])) and obj[field] != row[field]:
                    raise AssertionError(f'{obj.measurement_id}: object {field} differs from preferred row')
    reviews = {tuple(sorted((p['left'], p['right']))): p for p in fixture['pair_reviews']}
    if len(reviews) != len(fixture['pair_reviews']):
        raise AssertionError('Duplicate identity review pair')
    found = {}
    records = catalogue.to_dict('index')
    for left, right in combinations(records, 2):
        a, b = records[left], records[right]
        distance = separation_arcsec(a, b)
        if distance <= 2.0 or a['physical_object_id'] == b['physical_object_id']:
            found[tuple(sorted((left, right)))] = distance
    if set(found) != set(reviews):
        raise AssertionError('Unreviewed or stale all-catalogue identity pairs')
    unresolved = set()
    for key, distance in found.items():
        review = reviews[key]
        a, b = (records[mid] for mid in key)
        if not np.isclose(distance, review['separation_arcsec'], rtol=0, atol=1e-6):
            raise AssertionError('Reviewed identity separation changed')
        if not np.isclose(abs(a['redshift']-b['redshift']), review['redshift_delta'], rtol=0, atol=1e-8):
            raise AssertionError('Reviewed identity redshift difference changed')
        if not review['review_basis']:
            raise AssertionError('Identity decision lacks scientific basis')
        if review['issue_group']:
            unresolved.add(review['issue_group'])
        elif (a['physical_object_id'] == b['physical_object_id']) != review['expected_same_object']:
            raise AssertionError('Resolved identity decision disagrees with catalogue')
    admission = fixture['mascia_admission_review']
    if len(admission) != 20 or len({r['source_object_id'] for r in admission}) != 20:
        raise AssertionError('Mascia audit must account for all 20 source rows')
    for entry in admission:
        candidates = {mid for mid, row in records.items() if separation_arcsec(entry, row) <= .5 and abs(entry['redshift']-row['redshift']) <= .01}
        if candidates != set(entry['candidate_measurement_ids']):
            raise AssertionError('Mascia admission identity candidates changed')
        if entry['source_object_id'] == 'GS_3073':
            if candidates or entry['status'] != 'not_same_as_zs7_scope_exclusion':
                raise AssertionError('GS_3073 cannot be treated as a ZS7 alias')
    return dict(source_fields=count, redshifts=len(reference), coordinate_pairs=sum('ra_deg' in r['fields'] for r in reference), missing_coordinate_pairs=sum('ra_deg' in r['unavailable_fields'] for r in reference), reviewed_pairs=len(reviews), unresolved_identity_groups=sorted(unresolved), scientific_identity_status='open' if unresolved else 'resolved')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-resolved', action='store_true', help='Fail while any scientific identity group remains open')
    args = parser.parse_args()
    report = verify_redshift_identity()
    print(json.dumps(report, indent=2))
    if args.require_resolved and report['unresolved_identity_groups']:
        raise SystemExit('Publication identity gate FAILED: unresolved identity groups remain')


if __name__ == '__main__':
    main()
