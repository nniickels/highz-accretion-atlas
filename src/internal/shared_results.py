"""Resolve unchanged plots to their earliest catalogue version."""
from pathlib import Path
import re

import pandas as pd


VERSIONS = ('v1', 'v2', 'v3')
# These are all object-dependent inputs read by plot_fedd_mass_map.
MAP_FIELDS = ('object_id', 'object_class', 'redshift', 'log_mbh_msun_std')


def fedd_map_paths(root: Path, version: str, objects: pd.DataFrame) -> dict[str, Path]:
    previous = []
    for earlier in VERSIONS[:VERSIONS.index(version)]:
        frame = pd.read_csv(root/'data/processed'/earlier/f'{earlier}_accreting_objects.csv')
        previous.append((earlier, frame.set_index('physical_object_id')))
    paths = {}
    for _, obj in objects.iterrows():
        if not bool(obj.growth_ranking_eligible_flag):
            continue
        owner = version
        for earlier, frame in previous:
            if obj.physical_object_id not in frame.index:
                continue
            old = frame.loc[obj.physical_object_id]
            if bool(old.growth_ranking_eligible_flag) and all(old[k] == obj[k] for k in MAP_FIELDS):
                owner = earlier
                break
        stem = re.sub(r'[^a-z0-9]+', '-', str(obj.physical_object_id).lower()).strip('-')
        paths[obj.physical_object_id] = (
            root/'results'/owner/'parameter_maps/fedd_mass_maps'/f'{owner}_fedd_mass_map_{stem}.png'
        )
    return paths


def sensitivity_figure_path(root: Path, version: str) -> Path:
    fields = ['object_class', 'physical_object_id', 'alternate_measurement_id',
              'delta_log_mbh_alternate_minus_default', 'delta_required_fedd_alternate_minus_default']
    def inputs(release):
        path = root/'results'/release/'tables'/f'{release}_alternate_measurement_sensitivity.csv'
        return pd.read_csv(path)[fields].sort_values(fields[:3]).reset_index(drop=True)
    current = inputs(version)
    owner = version
    for earlier in VERSIONS[:VERSIONS.index(version)]:
        if inputs(earlier).equals(current):
            owner = earlier
            break
    return root/'results'/owner/'figures'/f'{owner}_measurement_sensitivity.png'
