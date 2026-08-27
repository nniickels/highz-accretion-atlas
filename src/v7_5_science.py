"""Release-scoped adapter for class-aware science on the v7.5 catalogue."""

from __future__ import annotations

from contextlib import contextmanager

import pandas as pd

from src import v7_2_science as core
from src.v7_5_catalogue import CATALOGUE_RELEASE


SCIENCE_RELEASE = "v7.5-class-aware-science"
DEFAULT_RANDOM_SEED = core.DEFAULT_RANDOM_SEED
DEFAULT_N_SAMPLES = core.DEFAULT_N_SAMPLES


@contextmanager
def release_context():
    """Scope the reusable class-aware engine to v7.5 without changing v7.2."""
    old_catalogue, old_science = core.CATALOGUE_RELEASE, core.SCIENCE_RELEASE
    core.CATALOGUE_RELEASE, core.SCIENCE_RELEASE = CATALOGUE_RELEASE, SCIENCE_RELEASE
    try:
        yield
    finally:
        core.CATALOGUE_RELEASE, core.SCIENCE_RELEASE = old_catalogue, old_science


def build_outputs(
    measurements: pd.DataFrame,
    objects: pd.DataFrame,
    *,
    n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> dict[str, pd.DataFrame]:
    with release_context():
        measurement_view = core.prepare_science_view(measurements, view="measurement")
        object_view = core.prepare_science_view(objects, view="physical_object")
        measurement_point = core.build_point_ranking(measurement_view)
        object_point = core.build_point_ranking(object_view)
        outputs = {
            "measurement_point_ranking": measurement_point,
            "object_point_ranking": object_point,
            "measurement_uncertainty_ranking": core.build_uncertainty_ranking(
                measurement_view, n_samples=n_samples, random_seed=random_seed,
            ),
            "object_uncertainty_ranking": core.build_uncertainty_ranking(
                object_view, n_samples=n_samples, random_seed=random_seed,
            ),
            "class_method_summary": core.build_class_method_summary(measurement_point, object_point),
            "exclusion_audit": core.build_exclusion_audit(measurements, objects),
            "alternate_measurement_sensitivity": core.build_alternate_measurement_sensitivity(
                measurements, objects,
            ),
            "science_policy": core.build_science_policy(),
        }
    verify_outputs(outputs, n_samples=n_samples)
    return outputs


def verify_outputs(outputs: dict[str, pd.DataFrame], *, n_samples: int) -> None:
    expected = {
        "measurement_point_ranking": 209,
        "object_point_ranking": 196,
        "measurement_uncertainty_ranking": 209,
        "object_uncertainty_ranking": 196,
        "class_method_summary": 36,
        "exclusion_audit": 48,
        "alternate_measurement_sensitivity": 13,
        "science_policy": 4,
    }
    actual = {name: len(frame) for name, frame in outputs.items()}
    if actual != expected:
        raise ValueError(f"v7.5 science counts changed; expected={expected}, observed={actual}")
    for frame in outputs.values():
        if not frame["science_release"].eq(SCIENCE_RELEASE).all():
            raise ValueError("v7.5 science release metadata mismatch")
        if "input_catalogue_release" in frame and not frame[
            "input_catalogue_release"
        ].eq(CATALOGUE_RELEASE).all():
            raise ValueError("v7.5 input catalogue metadata mismatch")
    for name in ["measurement_uncertainty_ranking", "object_uncertainty_ranking"]:
        if not outputs[name]["n_samples"].eq(n_samples).all():
            raise ValueError("v7.5 uncertainty sample count mismatch")
