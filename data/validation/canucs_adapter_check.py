"""Standalone CANUCS conversion and source-anchor check; run from repository root."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def canonical_row():
    """Convert source-native values without another lens or dust correction."""
    with (ROOT / 'data/raw/tripodi25_canucs_lrd_z86.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    row = rows[0]
    mass = float(row['mbh_msun'])
    h, m, s = map(float, row['ra_sexagesimal'].split(':'))
    d, dm, ds = map(float, row['dec_sexagesimal'].split(':'))
    return row | {
        'ra_deg': 15 * (h + m / 60 + s / 3600),
        'dec_deg': d + dm / 60 + ds / 3600,
        'log_mbh_msun': math.log10(mass),
        'log_mbh_err_plus': math.log10((mass + float(row['mbh_err_plus_msun'])) / mass),
        'log_mbh_err_minus': math.log10(mass / (mass - float(row['mbh_err_minus_msun']))),
        'object_class': 'broad_line_agn',
        'mass_comparability_group': 'virial_balmer_single_epoch',
        'evidence_status': 'secure',
        'lensing_mass_correction_status': 'source_corrected',
        'conditional_mass_flag': False,
    }


def check():
    row = canonical_row()
    expected = json.loads((ROOT / 'data/validation/canucs_expected_values.json').read_text())
    for field, value in (expected['expected'] | expected['expected_conversion']).items():
        assert math.isclose(float(row[field]), value, abs_tol=1e-10, rel_tol=0), field
    assert row['mbh_lensing_state'] == 'source_corrected_mu1.07'
    assert row['line_flux_lensing_state'] == 'observed_not_corrected'
    payloads = json.loads((ROOT / 'data/validation/canucs_source_payloads.json').read_text())
    for payload in payloads['payloads']:
        assert hashlib.sha256((ROOT / payload['path']).read_bytes()).hexdigest() == payload['sha256']
    print('CANUCS: one proposed measurement; source anchors, endpoint conversion and five payload hashes pass.')


if __name__ == '__main__':
    check()
