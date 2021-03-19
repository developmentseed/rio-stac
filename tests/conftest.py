"""``pytest`` configuration."""


import pytest
import rasterio

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
