"""``pytest`` configuration."""

import pytest
import rasterio
import json
from pathlib import Path

import pystac.validation
from pystac.validation.stac_validator import JsonSchemaSTACValidator

with rasterio.Env() as env:
    drivers = env.drivers()


requires_hdf5 = pytest.mark.skipif(
    "HDF5" not in drivers.keys(), reason="Only relevant if HDF5 drivers is supported"
)
requires_hdf4 = pytest.mark.skipif(
    "HDF4" not in drivers.keys(), reason="Only relevant if HDF4 drivers is supported"
)


@pytest.fixture
def runner():
    """CLI Runner fixture."""
    from click.testing import CliRunner

    return CliRunner()


def pytest_configure():
    """Use local copies of extension schemas to avoid network validation."""
    schema_dir = Path(__file__).parent / "schemas"
    validator = JsonSchemaSTACValidator()
    validator.schema_cache.update(
        {
            "https://stac-extensions.github.io/projection/v2.0.0/schema.json": json.loads(
                (schema_dir / "projection-2.0.0.json").read_text()
            ),
            "https://stac-extensions.github.io/raster/v2.0.0/schema.json": json.loads(
                (schema_dir / "raster-2.0.0.json").read_text()
            ),
            "https://stac-extensions.github.io/eo/v2.0.0/schema.json": json.loads(
                (schema_dir / "eo-2.0.0.json").read_text()
            ),
            "https://stac-extensions.github.io/scientific/v1.0.0/schema.json": json.loads(
                (schema_dir / "scientific-1.0.0.json").read_text()
            ),
        }
    )
    pystac.validation.set_validator(validator)
