"""Extract the two authoritative E-XQR-30 source tables from arXiv v1 archives.

This is an audit utility, not a network client.  Download the exact archives
listed below, then pass their paths explicitly.  SHA-256 verification and
fixed 42-row/order anchors prevent a different source version from silently
changing the checked-in raw CSVs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAZZUCCHELLI_SHA256 = "412055cec92c368f711605822d806c949816695a451efee867904d2171fee53f"
DODORICO_SHA256 = "1cf315f5fd4cd9f0edebb840c254dcd6bee26e2a061ce9fc9ff5bc8f344d7c42"
TABLE_OUTPUT = ROOT / "data/raw/xqr30_mazzucchelli23_table1.csv"
COORDINATE_OUTPUT = ROOT / "data/raw/xqr30_dodorico23_coordinates.csv"


def _archive_text(path: Path, expected_sha256: str, member: str) -> str:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"Archive checksum mismatch for {path}: {actual}")
    with tarfile.open(path, "r:gz") as archive:
        handle = archive.extractfile(member)
        if handle is None:
            raise ValueError(f"Archive {path} is missing {member}")
        return handle.read().decode("utf-8")


def _table_lines(text: str, start: str, end: str, expected_columns: int) -> list[list[str]]:
    section = (start + text.split(start, 1)[1]).split(end, 1)[0]
    rows = []
    for line in section.splitlines():
        if "&" not in line or "\\\\" not in line:
            continue
        fields = [field.strip() for field in line.split("\\\\", 1)[0].split("&")]
        if len(fields) == expected_columns:
            rows.append(fields)
    if len(rows) != 42:
        raise ValueError(f"Expected 42 source rows, found {len(rows)}")
    return rows


def _central(value: str) -> float:
    match = re.match(r"^\s*([+-]?[0-9.]+)", value)
    if not match:
        raise ValueError(f"Cannot parse central value: {value}")
    return float(match.group(1))


def _errors(value: str) -> tuple[float | str, float | str]:
    asymmetric = re.search(r"\^\{\+([0-9.]+)\}_\{-([0-9.]+)\}", value)
    if asymmetric:
        return float(asymmetric.group(1)), float(asymmetric.group(2))
    symmetric = re.search(r"\\pm\$?\s*([0-9.]+)", value)
    if symmetric:
        error = float(symmetric.group(1))
        return error, error
    return "", ""


def _coordinate(value: str, *, is_ra: bool) -> float:
    sign = -1.0 if value.strip().startswith("-") else 1.0
    fields = value.strip().lstrip("+-").split(":")
    if len(fields) != 3:
        raise ValueError(f"Invalid sexagesimal coordinate: {value}")
    first, minute, second = map(float, fields)
    decimal = first + minute / 60.0 + second / 3600.0
    return decimal * 15.0 if is_ra else sign * decimal


def _clean_name(value: str) -> str:
    return re.sub(r"\$\^.*$", "", value).strip()


def _measurement_id(name: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()
    return f"XQR30-{token}_mazzucchelli23"


def extract(mazzucchelli_archive: Path, dodorico_archive: Path) -> tuple[list[dict], list[dict]]:
    masses = _archive_text(
        mazzucchelli_archive, MAZZUCCHELLI_SHA256, "XQR30mas_aa.tex",
    )
    sample = _archive_text(
        dodorico_archive, DODORICO_SHA256, "XQR30_general_arxiv.tex",
    )
    mass_rows = _table_lines(
        masses, "PSOJ007+04$^{\\rm a)}$", "\\tablefoot", 12,
    )
    coordinate_rows = _table_lines(
        sample, "PSO J007+04  &", "References: 1 -", 15,
    )

    table_records: list[dict] = []
    coordinate_records: list[dict] = []
    for index, (mass, coordinate) in enumerate(zip(mass_rows, coordinate_rows, strict=True)):
        table_name = _clean_name(mass[0])
        canonical_name = coordinate[0].strip()
        measurement_id = _measurement_id(canonical_name)
        record: dict[str, object] = {
            "measurement_id": measurement_id,
            "object_id": canonical_name,
            "table_alias": table_name,
            "redshift": _central(mass[1]),
            "redshift_from_cii_flag": "\\dagger" in mass[1],
            "bal_flag": "\\ddagger" in mass[0],
            "mgii_telluric_caveat_flag": bool(re.search(r"a(?:b)?\)", mass[0])),
            "civ_low_snr_caveat_flag": "b)" in mass[0],
            "lensed_flag": "c)" in mass[0],
        }
        names = [
            "fwhm_civ_km_s", "fwhm_mgii_km_s", "civ_blueshift_km_s",
            "log_l1350_erg_s", "log_l3000_erg_s", "log_lbol_erg_s",
            "log_mbh_civ_msun", "log_mbh_mgii_msun",
            "edd_ratio_civ", "edd_ratio_mgii",
        ]
        for name, raw in zip(names, mass[2:], strict=True):
            record[name] = _central(raw)
            plus, minus = _errors(raw)
            record[f"{name}_err_plus"] = plus
            record[f"{name}_err_minus"] = minus
        table_records.append(record)
        coordinate_records.append({
            "measurement_id": measurement_id,
            "object_id": canonical_name,
            "ra_hms": coordinate[1],
            "dec_dms": coordinate[2],
            "ra_deg": _coordinate(coordinate[1], is_ra=True),
            "dec_deg": _coordinate(coordinate[2], is_ra=False),
        })

    expected = {
        0: ("PSO J007+04", "PSOJ007+04"),
        30: ("SDSS J0100+2802", "SDSSJ0100+28"),
        34: ("WISEA J0439+1634", "QSOJ0439+1634"),
        41: ("CFHQS J1509-1749", "CFHQSJ1509-1"),
    }
    for index, names in expected.items():
        observed = (coordinate_records[index]["object_id"], table_records[index]["table_alias"])
        if observed != names:
            raise ValueError(f"XQR-30 paired-order anchor mismatch at row {index}: {observed}")
    return table_records, coordinate_records


def _write_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mazzucchelli_archive", type=Path)
    parser.add_argument("dodorico_archive", type=Path)
    args = parser.parse_args()
    tables = extract(args.mazzucchelli_archive, args.dodorico_archive)
    _write_csv(TABLE_OUTPUT, tables[0])
    _write_csv(COORDINATE_OUTPUT, tables[1])
    print(f"Wrote 42 rows: {TABLE_OUTPUT.relative_to(ROOT)}")
    print(f"Wrote 42 rows: {COORDINATE_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
