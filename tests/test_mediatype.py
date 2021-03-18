"""test media type functions."""

import os

import pystac
import pytest
import rasterio

from rio_stac.stac import get_media_type

from .conftest import requires_hdf4, requires_hdf5

PREFIX = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.mark.parametrize(
    "file,mediatype",
    [
        ["dataset_cog.tif", pystac.MediaType.GEOTIFF],
        ["dataset_gdalcog.tif", pystac.MediaType.GEOTIFF],
        ["dataset_geo.tif", pystac.MediaType.GEOTIFF],
        ["dataset.tif", pystac.MediaType.TIFF],
        ["dataset.jp2", pystac.MediaType.JPEG2000],
        ["dataset.jpg", pystac.MediaType.JPEG],
        ["dataset.png", pystac.MediaType.PNG],
    ],
)
def test_get_mediatype(file, mediatype):
    """Should return the correct mediatype."""
    src_path = os.path.join(PREFIX, file)
    with rasterio.open(src_path) as src_dst:
        assert get_media_type(src_dst) == mediatype


@requires_hdf4
def test_hdf4():
    """Test hdf4 mediatype."""
    src_path = os.path.join(PREFIX, "dataset.hdf")
    with rasterio.open(src_path) as src_dst:
        assert get_media_type(src_dst) == pystac.MediaType.HDF


@requires_hdf5
def test_hdf5():
    """Test hdf5 mediatype."""
    src_path = os.path.join(PREFIX, "dataset.h5")
    with rasterio.open(src_path) as src_dst:
        assert get_media_type(src_dst) == pystac.MediaType.HDF5


def test_unknow():
    """Should warn when media type is not found."""
    src_path = os.path.join(PREFIX, "dataset.webp")
    with rasterio.open(src_path) as src_dst:
        with pytest.warns(UserWarning):
            assert not get_media_type(src_dst)
