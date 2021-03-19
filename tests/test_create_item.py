"""test media type functions."""

import datetime
import os

import pystac
import pytest
import rasterio

from rio_stac.stac import create_stac_item

from .conftest import requires_hdf4, requires_hdf5

PREFIX = os.path.join(os.path.dirname(__file__), "fixtures")
input_date = datetime.datetime.utcnow()


@pytest.mark.parametrize(
    "file",
    [
        "dataset_cog.tif",
        "dataset_gdalcog.tif",
        "dataset_geo.tif",
        "dataset.tif",
        "dataset.jp2",
        "dataset.jpg",
        "dataset.png",
        "dataset.webp",
    ],
)
def test_create_item(file):
    """Should run without exceptions."""
    src_path = os.path.join(PREFIX, file)
    with rasterio.open(src_path) as src_dst:
        assert create_stac_item(src_dst, input_datetime=input_date)


@requires_hdf4
def test_hdf4():
    """Test hdf4."""
    src_path = os.path.join(PREFIX, "dataset.hdf")
    with rasterio.open(src_path) as src_dst:
        assert create_stac_item(src_dst, input_datetime=input_date)


@requires_hdf5
def test_hdf5():
    """Test hdf5."""
    src_path = os.path.join(PREFIX, "dataset.h5")
    with rasterio.open(src_path) as src_dst:
        assert create_stac_item(src_dst, input_datetime=input_date)


def test_create_item_options():
    """Should return the correct mediatype."""
    src_path = os.path.join(PREFIX, "dataset_cog.tif")

    # pass string
    assert create_stac_item(src_path, input_datetime=input_date)

    item = create_stac_item(
        src_path, input_datetime=input_date, asset_media_type=pystac.MediaType.COG,
    ).to_dict()
    assert item["assets"]["asset"]["type"] == pystac.MediaType.COG
    assert item["links"] == []
    assert item["stac_extensions"] == []
    assert list(item["properties"]) == ["datetime"]

    item = create_stac_item(
        src_path,
        input_datetime=input_date,
        extensions=["proj", "comment"],
        properties={"comment:something": "it works"},
    ).to_dict()
    assert "type" not in item["assets"]["asset"]
    assert item["links"] == []
    assert item["stac_extensions"] == ["proj", "comment"]
    assert "datetime" in item["properties"]
    assert "proj:epsg" in item["properties"]
    assert "comment:something" in item["properties"]

    assets = {"cog": pystac.Asset(href=src_path)}
    item = create_stac_item(
        src_path, input_datetime=input_date, assets=assets, collection="mycollection",
    ).to_dict()
    assert item["assets"]["cog"]
    assert item["links"] == []
    assert item["stac_extensions"] == []
    assert "datetime" in item["properties"]
    assert item["collection"] == "mycollection"
