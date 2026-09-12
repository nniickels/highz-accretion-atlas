"""Source-linked manuscript comparisons, separate from frozen catalogue admission."""
from __future__ import annotations
import json
from statistics import NormalDist
import pandas as pd
from src import models


def build_review_outputs(root, selection, offsets):
    inputs = json.loads((root/'paper/review_inputs.json').read_text())
    objects = pd.read_csv(root/'data/processed/v3/v3_accreting_objects.csv')
    primary = set(selection.loc[selection.publication_primary_flag, 'physical_object_id'])
    baseline = offsets.loc[offsets.mass_offset_dex.eq(0) & offsets.publication_primary_flag]
    tail = baseline.loc[baseline.required_fedd.gt(1)].copy()
    tail = tail.merge(objects[['physical_object_id', 'source_key', 'redshift', 'mbh_method',
                              'log_mbh_msun_std', 'log_mbh_err_plus_std', 'log_mbh_err_minus_std',
                              'log_mbh_systematic_dex', 'lensing_status']], on='physical_object_id', validate='one_to_one')
    lower = offsets.loc[offsets.mass_offset_dex.eq(-.5), ['physical_object_id', 'required_fedd', 'probability_gt_1']]
    tail = tail.merge(lower.rename(columns={'required_fedd':'f_minus05', 'probability_gt_1':'p_minus05'}), on='physical_object_id', validate='one_to_one')
    if set(tail.object_id) != set(inputs['targets']):
        raise AssertionError('Review notes must cover exactly the reference primary tail')
    for key in ['caveat', 'proposed_observation']:
        tail[key] = tail.object_id.map(lambda x: inputs['targets'][x][key])
    tail = tail.sort_values('required_fedd', ascending=False).reset_index(drop=True)
    # At f_Edd=1 the inverse seed mass exceeds the reference log seed by
    # exactly the downward shift in observed log mass needed to reach unity.
    tail['mass_reduction_to_f1_dex'] = models.required_seed_mass_for_growth(
        tail.log_mbh_msun_std, 1, .1, 30, tail.redshift) - 2
    for offset in (1, 2):
        tail[f'f_minus{offset}dex'] = models.required_fedd_for_seed(
            2, tail.log_mbh_msun_std-offset, .1, 30, tail.redshift)
    sources = pd.DataFrame(inputs['sources'])
    native = pd.read_csv(root/'results/v3/tables/v3_source_caveat_summary.csv')
    if set(sources.source_key) != set(native.source_key):
        raise AssertionError('Source inventory must cover every admitted source family')
    sources = sources.merge(native[['source_key','n_measurements','n_growth_eligible_measurements',
                                   'selection_channels','source_caveat_tags','source_url']], on='source_key', validate='one_to_one')
    counts = objects.loc[objects.physical_object_id.isin(primary)].groupby('source_key').size()
    sources['n_publication_primary_preferred'] = sources.source_key.map(counts).fillna(0).astype(int)
    by_name = objects.set_index('object_id')
    matched = []
    for row in inputs['dayal_comparison']['rows']:
        obj = by_name.loc[row['object_id']]
        old = float(models.required_fedd_for_seed(2, row['log_mass'], .1, 25, row['redshift']))
        revised = float(models.required_fedd_for_seed(2, obj.log_mbh_msun_std, .1, 25, obj.redshift))
        reference = float(models.required_fedd_for_seed(2, obj.log_mbh_msun_std, .1, 30, obj.redshift))
        matched.append(dict(object_id=row['object_id'], source_id=row['source_id'],
            source_url=inputs['dayal_comparison']['source_url'], locator=inputs['dayal_comparison']['locator'],
            earlier_redshift=row['redshift'], earlier_log_mass=row['log_mass'],
            current_redshift=obj.redshift, current_log_mass=obj.log_mbh_msun_std,
            earlier_inputs_z25=old, current_inputs_z25=revised, current_inputs_z30=reference,
            delta_measurement=revised-old, delta_start_time=reference-revised))
    direct = inputs['direct_mass']
    obj = by_name.loc[direct['object_id']]
    external = []
    for label, mass, sigma in [('catalogue_virial',obj.log_mbh_msun_std,obj.log_mbh_err_plus_std),
                               ('external_dynamical',direct['log_mass'],direct['sigma_dex'])]:
        coefficient = float(models.required_fedd_for_seed(2, 3, .1, 30, obj.redshift))
        # Symmetric log-mass errors: exact normal quantiles, no MC noise.
        f = float(models.required_fedd_for_seed(2, mass, .1, 30, obj.redshift))
        external.append(dict(object_id=direct['object_id'], comparison=label, redshift=obj.redshift,
            log_mass=mass, sigma_dex=sigma, required_fedd=f,
            p16=max(0,f+NormalDist().inv_cdf(.16)*sigma*coefficient),
            p84=max(0,f+NormalDist().inv_cdf(.84)*sigma*coefficient),
            probability_gt_1=NormalDist().cdf((f-1)/(sigma*coefficient)),
            source_url=obj.source_url if label=='catalogue_virial' else direct['source_url'],
            locator='Adopted catalogue row '+obj.measurement_id if label=='catalogue_virial' else direct['locator'],
            scope='Separate comparison; no replacement in primary counts'))
    return {'target_robustness':tail, 'source_inventory':sources,
            'matched_literature_comparison':pd.DataFrame(matched),
            'external_direct_mass_comparison':pd.DataFrame(external)}


def tex_escape(value):
    return str(value).replace('&',r'\&').replace('_',r'\_').replace('%',r'\%')


def review_tex(outputs):
    sources = outputs['source_inventory'].set_index('source_key')
    tail = outputs['target_robustness']
    rows, actions = [], []
    for r in tail.itertuples():
        line = r'H$\alpha$' if 'halpha' in r.mbh_method else r'H$\beta$'
        citation = sources.loc[r.source_key, 'citation']
        mass = rf'${r.log_mbh_msun_std:.2f}^{{+{r.log_mbh_err_plus_std:.2f}}}_{{-{r.log_mbh_err_minus_std:.2f}}}$'
        note = ''
        if pd.notna(r.log_mbh_systematic_dex):
            marker = {0.5: 'a', 0.3: 'b'}[r.log_mbh_systematic_dex]
            note = rf'$^{{\rm {marker}}}$'
        elif r.object_id == 'ZS7':
            note = r'$^{\rm c}$'
        # Rounded probabilities are descriptive, never labelled exact certainty.
        prob = lambda p: '$>0.999$' if p>.999 else ('$<0.001$' if p<.001 else f'{p:.3f}')
        rows.append(f'{tex_escape(r.object_id)}{note} \\newline {{\\footnotesize \\citet{{{citation}}}}} & {line} & {mass} & {r.required_fedd:.3f} & {r.p16:.3f} & {prob(r.probability_gt_1)} & {r.f_minus05:.3f} & {prob(r.p_minus05)} & {r.mass_reduction_to_f1_dex:.3f} \\\\')
        actions.append(f'{tex_escape(r.object_id)} & {tex_escape(r.caveat)} \\\\[3pt]')
    inventory = []
    for r in outputs['source_inventory'].itertuples():
        survey = ' / ' + tex_escape(r.label.split(' / ', 1)[1]) if ' / ' in r.label else ''
        if r.label.startswith('Skyfire'):
            survey = ' / Skyfire (CEERS)'
        elif r.citation == 'bogdan2024,zou2026':
            survey = ' / UHZ1'
        inventory.append(f'\\citet{{{r.citation}}}{survey} & {r.n_measurements}/{r.n_growth_eligible_measurements}/{r.n_publication_primary_preferred} & {r.mass_summary} & {tex_escape(r.channel_summary)}; {tex_escape(r.caveat_summary)} \\\\[3pt]')
    matched = [f'{tex_escape(r.object_id)} & {r.earlier_inputs_z25:.3f} & {r.current_inputs_z25:.3f} & {r.current_inputs_z30:.3f} \\\\' for r in outputs['matched_literature_comparison'].itertuples()]
    direct = outputs['external_direct_mass_comparison'].set_index('comparison')
    old, new = direct.loc['catalogue_virial'], direct.loc['external_dynamical']
    direct_text = (
        rf'Using the central mass estimates, the required average Eddington ratio rises from {old.required_fedd:.3f} to {new.required_fedd:.3f}. '
        rf'With a symmetric normal approximation to the quoted log-mass errors, '
        rf'the exact 16th--84th percentile intervals are {old.p16:.3f}--{old.p84:.3f} '
        rf'and {new.p16:.3f}--{new.p84:.3f}, respectively. '
        rf'For the dynamical mass, the unrounded required ratio is just below 1. '
        rf'Its uncertainty interval includes average accretion rates both below and above the Eddington limit. '
        rf'With this mass-error distribution and the growth assumptions held fixed, '
        rf'the probability that the required average Eddington ratio exceeds 1 is {new.probability_gt_1:.3f}.'+'\n')
    revision_rows = []
    labels = {'frozen_v1_measurements': 'Frozen values',
              'published_values_keep_unmatched': 'Published; retain unmatched',
              'published_values_omit_unmatched': 'Published; omit unmatched'}
    for r in outputs['publication_baccus_revision_summary'].itertuples():
        revision_rows.append(
            f'{r.sample.capitalize()} & {labels[r.scenario]} & {r.numerical_objects} & '
            f'{r.point_required_fedd_gt_1}/{r.p16_required_fedd_gt_1}/{r.prob_required_fedd_gt_1_ge_095} \\\\')
    return {'baccus_revision_rows':'\n'.join(revision_rows)+'\n',
            'target_rows':'\n'.join(rows)+'\n', 'target_actions':'\n'.join(actions)+'\n',
            'source_rows':'\n'.join(inventory)+'\n', 'matched_rows':'\n'.join(matched)+'\n',
            'direct_result':direct_text}
