"""Extract the authoritative 50-object Shen et al. (2019) CDS tables.

This is an offline audit utility. Download the exact CDS ``table1.dat`` and
``table3.dat`` files, then pass them explicitly. Checksums, row counts, object
ordering, and fixed scientific anchors prevent silent source drift.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TABLE1_SHA256 = "40ed1598d8c6d4d4a4aa580c578742f9e0334c26bb9dd762a9a0375231a7239f"
TABLE3_SHA256 = "e1eae3266b9ccfc966303c6e389e9c16141678199924a67ab4c786fed3240323"
SAMPLE_OUTPUT = ROOT / "data/raw/shen19_gnirs_table1.csv"
CATALOG_OUTPUT = ROOT / "data/raw/shen19_gnirs_table3.csv"


def _verified_lines(path: Path, expected_sha256: str) -> list[str]:
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"Source checksum mismatch for {path}: {actual}")
    lines = payload.decode("ascii").splitlines()
    if len(lines) != 50:
        raise ValueError(f"Expected 50 rows in {path}, found {len(lines)}")
    return lines


def _value(raw: str) -> float | str:
    value = raw.strip()
    if not value or value == "---":
        return ""
    number = float(value)
    # The CDS table uses zero as the null sentinel for line measurements and
    # masses, and -99 for the Eddington ratio. Conversion is field-specific.
    return number


def _sexagesimal(major: str, minute: str, second: str, *, ra: bool) -> float:
    sign = -1.0 if major.startswith("-") else 1.0
    decimal = abs(float(major)) + float(minute) / 60.0 + float(second) / 3600.0
    return decimal * 15.0 if ra else sign * decimal


def _measurement_id(object_id: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "-", object_id).strip("-").upper()
    return f"GNIRS50-{token}_shen19"


def _parse_sample(lines: list[str]) -> list[dict[str, object]]:
    records = []
    for line in lines:
        object_id = line[3:13].strip()
        ra_h, ra_m, ra_s = line[14:16], line[17:19], line[20:25]
        dec_d = line[26:30].strip()
        dec_m, dec_s = line[30:32], line[33:37]
        records.append({
            "measurement_id": _measurement_id(object_id),
            "object_id": object_id,
            "ra_hms": f"{ra_h.strip()}:{ra_m.strip()}:{ra_s.strip()}",
            "dec_dms": f"{dec_d}:{dec_m.strip()}:{dec_s.strip()}",
            "ra_deg": _sexagesimal(ra_h, ra_m, ra_s, ra=True),
            "dec_deg": _sexagesimal(dec_d, dec_m, dec_s, ra=False),
            "original_redshift": _value(line[38:43]),
            "systemic_redshift": _value(line[44:49]),
            "systemic_redshift_err": _value(line[50:55]),
            "j_mag": _value(line[56:61]),
            "j_mag_err": _value(line[62:66]),
            "h_mag": _value(line[67:72]),
            "h_mag_err": _value(line[73:77]),
            "ks_mag": _value(line[78:83]),
            "ks_mag_err": _value(line[84:88]),
            "photometry_reference": line[89:100].strip(),
            "discovery_reference_key": line[101:103].strip(),
            "comment": line[104:119].strip(),
        })
    return records


SCALAR_NAMES = [
    "object_id", "original_redshift", "systemic_redshift", "systemic_redshift_err",
    "mgii_redshift", "mgii_redshift_err", "ciii_redshift", "ciii_redshift_err",
    "civ_redshift", "civ_redshift_err", "siiv_redshift", "siiv_redshift_err",
    "log_l1350_erg_s", "log_l1350_err", "log_l1700_erg_s", "log_l1700_err",
    "log_l3000_erg_s", "log_l3000_err", "log_lbol_erg_s", "log_lbol_err",
]
LINE_NAMES = ["peak_angstrom", "fwhm_km_s", "log_l_erg_s", "ew_angstrom", "centroid_angstrom"]


def _clean_catalog_value(field: str, value: float | str) -> float | str:
    if value == "":
        return ""
    if field == "log_edd_ratio" and value == -99:
        return ""
    if field.startswith(("mgii_", "ciii_", "civ_", "siiv_", "log_mbh")) and value == 0:
        return ""
    if field.endswith("_err") and value == -1:
        return ""
    return value


def _parse_catalog(lines: list[str]) -> list[dict[str, object]]:
    records = []
    for line in lines:
        groups = line.split("|")
        if len(groups) != 36:
            raise ValueError(f"Expected 36 pipe groups, found {len(groups)}")
        record = {"object_id": groups[0].strip()}
        record.update(zip(SCALAR_NAMES[1:], (_value(item) for item in groups[1:20]), strict=True))
        for prefix, group in zip(["mgii", "ciii", "civ", "siiv"], groups[20:24], strict=True):
            for suffix, raw in zip(LINE_NAMES, group.split(), strict=True):
                record[f"{prefix}_{suffix}"] = _value(raw)
        for prefix, group in zip(["mgii", "ciii", "civ", "siiv"], groups[24:28], strict=True):
            for suffix, raw in zip(LINE_NAMES, group.split(), strict=True):
                record[f"{prefix}_{suffix}_err"] = _value(raw)
        tail_names = [
            "log_mbh_civ_msun", "log_mbh_civ_err", "log_mbh_mgii_msun",
            "log_mbh_mgii_err", "log_mbh_fiducial_msun", "log_mbh_fiducial_err",
            "log_edd_ratio", "log_edd_ratio_err",
        ]
        record.update(zip(tail_names, (_value(item) for item in groups[28:]), strict=True))
        record = {field: _clean_catalog_value(field, value) for field, value in record.items()}
        record["measurement_id"] = _measurement_id(str(record["object_id"]))
        records.append({"measurement_id": record.pop("measurement_id"), **record})
    return records


def extract(table1_path: Path, table3_path: Path) -> tuple[list[dict], list[dict]]:
    sample = _parse_sample(_verified_lines(table1_path, TABLE1_SHA256))
    catalog = _parse_catalog(_verified_lines(table3_path, TABLE3_SHA256))
    sample_ids = [row["object_id"] for row in sample]
    catalog_ids = [row["object_id"] for row in catalog]
    if set(sample_ids) != set(catalog_ids) or len(set(sample_ids)) != 50:
        raise ValueError("Shen et al. sample and catalog object membership does not match")
    catalog_by_id = {row["object_id"]: row for row in catalog}
    catalog = [catalog_by_id[object_id] for object_id in sample_ids]
    if sample_ids[:3] != ["P000+26", "J0002+2550", "J0008-0626"] or sample_ids[-1] != "J2356+0023":
        raise ValueError("Shen et al. object-order anchors do not match")
    by_id = {row["object_id"]: row for row in catalog}
    if not math.isclose(float(by_id["J0002+2550"]["log_mbh_fiducial_msun"]), 9.6767):
        raise ValueError("Shen et al. J0002+2550 mass anchor does not match")
    if by_id["J0055+0146"]["log_mbh_fiducial_msun"] != "":
        raise ValueError("Shen et al. J0055+0146 missing-mass anchor does not match")
    return sample, catalog


def _write_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table1", type=Path)
    parser.add_argument("table3", type=Path)
    args = parser.parse_args()
    sample, catalog = extract(args.table1, args.table3)
    _write_csv(SAMPLE_OUTPUT, sample)
    _write_csv(CATALOG_OUTPUT, catalog)
    print(f"Wrote 50 rows: {SAMPLE_OUTPUT.relative_to(ROOT)}")
    print(f"Wrote 50 rows: {CATALOG_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
