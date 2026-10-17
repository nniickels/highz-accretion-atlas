"""Deterministic source-local adapter and independent checks; prints, never writes outputs.

Run: python3 data/validation/takechi26_macs0416_y1_adapter.py
Integration must register this source and apply the canonical schema separately.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def adapt():
    rows = list(csv.DictReader((ROOT / 'data/raw/takechi26_macs0416_y1.csv').open()))
    assert len(rows) == 1
    r = rows[0]
    m = float(r['mbh_1e6_msun']) * 1e6
    lo = m - float(r['mbh_err_minus']) * 1e6
    hi = m + float(r['mbh_err_plus']) * 1e6
    h, minutes, seconds = map(float, r['ra_hms'].split(':'))
    d, dm, ds = map(float, r['dec_dms'].split(':'))
    return dict(measurement_id='MACS0416Y1_takechi26', physical_object_id='HZA-MACS0416-Y1',
                host_system_id='HZS-MACS0416-Y1', object_id=r['source_id'],
                source_dataset='takechi26_macs0416_y1', source_version=r['source_version'],
                ra_deg=15*(h+minutes/60+seconds/3600), dec_deg=-(abs(d)+dm/60+ds/3600),
                coordinate_role=r['coordinate_role'], redshift=float(r['redshift']), redshift_kind='spec',
                object_class='broad_line_agn', evidence_status='candidate', spectroscopic_type='type1_broad_line',
                log_mbh_msun_std=math.log10(m), log_mbh_err_minus_std=math.log10(m/lo),
                log_mbh_err_plus_std=math.log10(hi/m), mass_comparability_group='virial_balmer_single_epoch',
                lensing_status='lensed', lensing_mass_correction_status='source_corrected',
                growth_ranking_eligible_flag=True, primary_growth_ranking_flag=False,
                manuscript_primary_proposed=False, manuscript_expanded_proposed=True,
                preferred_measurement_proposed=True, versions_proposed=['v2','v3'],
                calibration_scatter_dex=None, source_error_definition=r['mass_error_definition'])


def verify():
    a=adapt()
    e=json.loads((ROOT/'data/validation/takechi26_macs0416_y1_expected.json').read_text())
    r=next(csv.DictReader((ROOT/'data/raw/takechi26_macs0416_y1.csv').open()))
    for actual, expected in [(10**a['log_mbh_msun_std'],e['mass_msun']),
        (10**(a['log_mbh_msun_std']-a['log_mbh_err_minus_std']),e['mass_lower_endpoint_msun']),
        (10**(a['log_mbh_msun_std']+a['log_mbh_err_plus_std']),e['mass_upper_endpoint_msun']),
        (a['ra_deg'],e['host_ra_deg']),(a['dec_deg'],e['host_dec_deg']),(a['redshift'],e['redshift'])]:
        assert math.isclose(actual,expected,rel_tol=1e-12)
    for keys, expected in [(['hbeta_fwhm_kms','hbeta_fwhm_err_minus','hbeta_fwhm_err_plus'],e['hbeta_fwhm_kms']),
        (['hbeta_broad_flux_1e19_erg_s_cm2','hbeta_broad_flux_err_minus','hbeta_broad_flux_err_plus'],e['observed_hbeta_flux_1e19']),
        (['magnification','magnification_err_minus','magnification_err_plus'],e['magnification'])]:
        assert [float(r[k]) for k in keys] == expected
    assert a['source_version']==e['source_version']
    assert len(list(csv.DictReader((ROOT/'data/raw/takechi26_macs0416_y1_screen.csv').open())))==e['screen_entities']
    p=json.loads((ROOT/'data/validation/source_inputs/takechi26_macs0416_y1_provenance.json').read_text())
    for item in p['payloads']:
        path=item.get('retained_file',item.get('retained_extract'))
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==item['retained_sha256']
    return a

if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
