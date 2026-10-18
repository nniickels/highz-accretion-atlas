"""Read-only CAPERS source checks; run with Python from any working directory."""
from pathlib import Path
import csv
import json
import math

ROOT = Path(__file__).resolve().parents[2]

def load_csv(name):
    return list(csv.DictReader((ROOT / 'data/raw' / name).open()))

def main():
    validation = ROOT / 'data/validation'
    expected = json.loads((validation / 'capers_lrd_z9_expected_values.json').read_text())
    rows = load_csv('capers_lrd_z9_v4_properties.csv')
    assert len(rows) == 1
    row = rows[0]
    for key, value in expected['properties'].items():
        assert math.isclose(float(row[key]), value, rel_tol=0, abs_tol=1e-10), key
    assert row['coordinate_frame'] == 'not_explicitly_reported'
    assert row['lensing_mu'] == ''
    assert row['dust_correction_applied'] == row['additional_systematic_applied'] == 'False'
    alts = load_csv('capers_lrd_z9_v4_mass_alternatives.csv')
    assert len(alts) == 5
    for alt in alts:
        mass, error, censoring = expected['mass_alternatives'][alt['estimate']]
        assert float(alt['log_mbh_msun']) == mass
        assert (float(alt['reported_error_dex']) if alt['reported_error_dex'] else None) == error
        assert alt['censoring'] == censoring
    assert sum(x['proposed_use'] == 'preferred_growth_mass' for x in alts) == 1
    assert next(x for x in alts if x['estimate'] == 'assumed_eddington_lower_bound')['proposed_use'] == 'context_only_no_independent_growth_inference'
    cells = load_csv('capers_lrd_z9_v4_table_cells.csv')
    assert {str(i): sum(x['source_table'] == str(i) for x in cells) for i in [1, 2, 3]} == expected['table_data_rows']
    identities = json.loads((validation / 'capers_lrd_z9_identity_checks.json').read_text())
    for version, audit in identities.items():
        assert audit['alias_matches'] == audit['within_2_arcsec'] == []
        assert audit['nearest_five'][0]['separation_arcsec'] > 185
        assert len(audit['missing_coordinates']) == (27 if version == 'v3' else 0)
    print('CAPERS: 17 numerical property anchors, five mass semantics, 48 table rows and identity audit checks passed.')

if __name__ == '__main__':
    main()
