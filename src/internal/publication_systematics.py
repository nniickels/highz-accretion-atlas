"""Conditional mass-scale stress tests, not a calibrated systematic posterior."""
from __future__ import annotations
import numpy as np
import pandas as pd
from src import models
from src.internal.compatibility.v7_science_core import _rng
from src.internal.uncertainty import asymmetric_normal_samples

MASS_OFFSETS_DEX = (-0.5, -0.3, 0.0, 0.3, 0.5)


def build_mass_offset_outputs(selection, errors):
    """Translate the same reported-error draws by each fixed log-mass offset.

    Offsets are coherent across the selected sample, not independent scatter.
    Missing-error objects contribute only point estimates at every offset.
    """
    membership = selection.set_index('physical_object_id')
    ids = membership.index[membership.publication_exploratory_flag]
    rows = []
    for _, obj in errors.loc[errors.physical_object_id.isin(ids)].sort_values('physical_object_id').iterrows():
        has_error = bool(obj.reported_mass_errors_sampled)
        draws = asymmetric_normal_samples(
            obj.log_mbh_msun_std, obj.log_mbh_err_plus_std, obj.log_mbh_err_minus_std,
            n_samples=int(obj.n_samples), rng=_rng(int(obj.random_seed), str(obj.ranking_id)))
        for offset in MASS_OFFSETS_DEX:
            values = models.required_fedd_for_seed(2, draws + offset, .1, 30, obj.redshift)
            rows.append(dict(physical_object_id=obj.physical_object_id,
                measurement_id=obj.measurement_id, object_id=obj.object_id,
                publication_primary_flag=bool(membership.loc[obj.physical_object_id, 'publication_primary_flag']),
                mass_offset_dex=offset, n_samples=int(obj.n_samples) if has_error else 0,
                random_seed=int(obj.random_seed), reported_mass_errors_sampled=has_error,
                required_fedd=float(models.required_fedd_for_seed(2, obj.log_mbh_msun_std + offset, .1, 30, obj.redshift)),
                p16=float(np.quantile(values, .16)) if has_error else np.nan,
                probability_gt_1=float(np.mean(values > 1)) if has_error else np.nan))
    detail = pd.DataFrame(rows)
    summary = []
    for sample in ('primary', 'exploratory'):
        subset = detail.loc[detail.publication_primary_flag] if sample == 'primary' else detail
        for offset, group in subset.groupby('mass_offset_dex', sort=True):
            summary.append(dict(sample=sample, mass_offset_dex=offset,
                n_objects=len(group), n_reported_errors=int(group.reported_mass_errors_sampled.sum()),
                above_unity=int(group.required_fedd.gt(1).sum()),
                p16_above_unity=int(group.p16.gt(1).sum()),
                probability_ge_095=int(group.probability_gt_1.ge(.95).sum())))
    return {'mass_offset_object_sensitivity': detail, 'mass_offset_sensitivity': pd.DataFrame(summary)}
