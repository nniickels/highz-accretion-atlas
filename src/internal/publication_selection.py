"""Reproduce conservative manuscript samples without claiming identity resolution.

The immutable catalogue remains a provisional evidence atlas. Every object linked
to an open identity group is withheld from manuscript inference. This check is
additional to, and never replaces, verify_redshift_identity --require-resolved.
"""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path
import numpy as np
import pandas as pd
from src import models
from src.internal.verify_redshift_identity import verify_redshift_identity

ROOT = Path(__file__).resolve().parents[2]
POLICY = Path('paper/identity_exclusions.json')
DESTINATION = Path('paper/analysis')
SCENARIOS = [('reference', 2, .1, 30), ('seed_1e3', 3, .1, 30),
             ('seed_1e5', 5, .1, 30), ('seed_z20', 2, .1, 20),
             ('nonspinning', 2, 1-np.sqrt(8/9), 30)]


def build_publication_outputs(root=ROOT, policy=None):
    policy = policy if policy is not None else json.loads((root/POLICY).read_text())
    if policy.get('disposition') != 'exclude_all_open_identity_groups_from_manuscript_inference':
        raise AssertionError('Unapproved publication exclusion disposition')
    fixture = json.loads((root/'data/validation/redshift_identity_checks.json').read_text())
    expected = {}
    for pair in fixture['pair_reviews']:
        if pair['issue_group']:
            expected.setdefault(pair['issue_group'], set()).update([pair['left'], pair['right']])
    groups = policy['groups']
    if len({g['issue_group'] for g in groups}) != len(groups):
        raise AssertionError('Duplicate publication exclusion group')
    actual = {g['issue_group']: set(g['measurement_ids']) for g in groups}
    if actual != expected or any(not g.get('reason') for g in groups):
        raise AssertionError('Publication exclusions must cover every open group exactly')
    measurements = pd.read_csv(root/'data/processed/v3/v3_accreting_measurements.csv')
    objects = pd.read_csv(root/'data/processed/v3/v3_accreting_objects.csv')
    group_by_object = {}
    for group, mids in actual.items():
        rows = measurements.loc[measurements.measurement_id.isin(mids)]
        if set(rows.measurement_id) != mids:
            raise AssertionError('Unknown excluded measurement')
        for oid in rows.physical_object_id:
            if oid in group_by_object and group_by_object[oid] != group:
                raise AssertionError('Overlapping identity groups require review')
            group_by_object[oid] = group
    selection = objects[['physical_object_id', 'measurement_id', 'object_id',
                         'growth_ranking_eligible_flag', 'primary_growth_ranking_flag']].copy()
    selection['open_identity_group'] = selection.physical_object_id.map(group_by_object).fillna('')
    excluded = selection.open_identity_group.ne('')
    selection['excluded_identity_flag'] = excluded
    selection['publication_primary_flag'] = selection.primary_growth_ranking_flag & ~excluded
    selection['publication_exploratory_flag'] = selection.growth_ranking_eligible_flag & ~excluded
    selection = selection.sort_values('physical_object_id').reset_index(drop=True)
    point = pd.read_csv(root/'results/v3/tables/v3_object_point_ranking.csv')
    errors = pd.read_csv(root/'results/v3/tables/v3_object_uncertainty_ranking.csv')
    rows = []
    for scope in ['catalogue', 'publication']:
        for sample in ['primary', 'exploratory']:
            subset = point if sample == 'exploratory' else point.loc[point.primary_growth_ranking_flag]
            if scope == 'publication':
                subset = subset.loc[~subset.physical_object_id.isin(group_by_object)]
            e = errors.loc[errors.physical_object_id.isin(subset.physical_object_id)]
            for scenario, seed, epsilon, zseed in SCENARIOS:
                required = models.required_fedd_for_seed(seed, subset.log_mbh_msun_std,
                                                        epsilon, zseed, subset.redshift)
                q25, median, q75 = np.quantile(required, [.25, .5, .75])
                rows.append(dict(scope=scope, sample=sample, scenario=scenario,
                    n_objects=len(subset), above_unity=int((required > 1).sum()),
                    q25=q25, median=median, q75=q75,
                    p16_above_unity=int(e.required_fedd_seed1e2_p16.gt(1).sum()) if scenario == 'reference' else np.nan,
                    probability_ge_095=int(e.prob_required_fedd_seed1e2_gt_1.ge(.95).sum()) if scenario == 'reference' else np.nan,
                    top_five=';'.join(subset.iloc[np.argsort(-required, kind='stable')[:5]].object_id)))
    from src.internal.publication_systematics import build_mass_offset_outputs
    return {'publication_object_selection': selection, 'identity_exclusion_sensitivity': pd.DataFrame(rows),
            **build_mass_offset_outputs(selection, errors)}


def verify_publication_selection(root=ROOT):
    audit = verify_redshift_identity(root)
    outputs = build_publication_outputs(root)
    for name, expected in outputs.items():
        path = root/DESTINATION/f'{name}.csv'
        actual = pd.read_csv(path, keep_default_na=False)
        # Round-trip expected CSV too, so empty and missing cells have identical semantics.
        reference = pd.read_csv(io.StringIO(expected.to_csv(index=False)), keep_default_na=False)
        pd.testing.assert_frame_equal(actual, reference, check_exact=False, rtol=1e-12, atol=1e-12)
    selected = outputs['publication_object_selection']
    if selected.loc[selected.excluded_identity_flag, ['publication_primary_flag', 'publication_exploratory_flag']].any().any():
        raise AssertionError('An unresolved identity leaked into publication inference')
    return {'publication_exclusion_check': 'pass',
            'scientific_identity_status': audit['scientific_identity_status'],
            'unresolved_identity_groups': audit['unresolved_identity_groups'],
            'excluded_object_records': int(selected.excluded_identity_flag.sum()),
            'publication_primary_objects': int(selected.publication_primary_flag.sum()),
            'publication_exploratory_objects': int(selected.publication_exploratory_flag.sum())}


def write_publication_outputs(root=ROOT):
    """Regenerate manuscript products after canonical v3 science generation."""
    outputs = build_publication_outputs(root)
    (root/DESTINATION).mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(root/DESTINATION/f'{name}.csv', index=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate committed manuscript selection and sensitivity tables')
    args = parser.parse_args()
    if args.write:
        write_publication_outputs()
    print(json.dumps(verify_publication_selection(), indent=2))

if __name__ == '__main__':
    main()
