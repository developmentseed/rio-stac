"""test media type functions."""

import datetime
import os

import numpy
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
        assert create_stac_item(src_dst, input_datetime=input_date).validate()


@requires_hdf4
def test_hdf4():
    """Test hdf4."""
    src_path = os.path.join(PREFIX, "dataset.hdf")
    with rasterio.open(src_path) as src_dst:
        assert create_stac_item(src_dst, input_datetime=input_date).validate()


@requires_hdf5
def test_hdf5():
    """Test hdf5."""
    src_path = os.path.join(PREFIX, "dataset.h5")
    with rasterio.open(src_path) as src_dst:
        assert create_stac_item(src_dst, input_datetime=input_date).validate()


def test_create_item_options():
    """Should return the correct mediatype."""
    src_path = os.path.join(PREFIX, "dataset_cog.tif")

    # pass string
    assert create_stac_item(src_path, input_datetime=input_date).validate()

    # default COG
    item = create_stac_item(
        src_path,
        input_datetime=input_date,
        asset_media_type=pystac.MediaType.COG,
        with_proj=False,
    )
    assert item.validate()
    item_dict = item.to_dict()
    assert item_dict["assets"]["asset"]["type"] == pystac.MediaType.COG
    assert item_dict["links"] == []
    assert item_dict["stac_extensions"] == []
    assert list(item_dict["properties"]) == ["datetime"]

    # additional extensions and properties
    item = create_stac_item(
        src_path,
        input_datetime=input_date,
        extensions=["https://stac-extensions.github.io/scientific/v1.0.0/schema.json"],
        properties={"sci:citation": "A nice image"},
        with_proj=False,
    )
    assert item.validate()
    item_dict = item.to_dict()
    assert "type" not in item_dict["assets"]["asset"]
    assert item_dict["links"] == []
    assert item_dict["stac_extensions"] == [
        "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
    ]
    assert "datetime" in item_dict["properties"]
    assert "proj:epsg" not in item_dict["properties"]
    assert "sci:citation" in item_dict["properties"]

    # additional extensions and properties
    item = create_stac_item(
        src_path,
        input_datetime=input_date,
        extensions=["https://stac-extensions.github.io/scientific/v1.0.0/schema.json"],
        properties={"sci:citation": "A nice image"},
        with_proj=True,
    )
    assert item.validate()
    item_dict = item.to_dict()
    assert "type" not in item_dict["assets"]["asset"]
    assert item_dict["links"] == []
    assert item_dict["stac_extensions"] == [
        "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
        "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
    ]
    assert "datetime" in item_dict["properties"]
    assert "proj:epsg" in item_dict["properties"]
    assert "sci:citation" in item_dict["properties"]

    # external assets
    assets = {"cog": pystac.Asset(href=src_path)}
    item = create_stac_item(
        src_path, input_datetime=input_date, assets=assets, with_proj=False
    )
    assert item.validate()
    item_dict = item.to_dict()
    assert item_dict["assets"]["cog"]
    assert item_dict["links"] == []
    assert item_dict["stac_extensions"] == []
    assert "datetime" in item_dict["properties"]

    # collection
    item = create_stac_item(
        src_path, input_datetime=input_date, collection="mycollection", with_proj=False
    )
    assert item.validate()
    item_dict = item.to_dict()
    assert item_dict["links"][0]["href"] == "mycollection"
    assert item_dict["stac_extensions"] == []
    assert "datetime" in item_dict["properties"]
    assert item_dict["collection"] == "mycollection"

    item = create_stac_item(
        src_path,
        input_datetime=input_date,
        collection="mycollection",
        collection_url="https://stac.somewhere.io/mycollection.json",
        with_proj=False,
    )
    assert item.validate()
    item_dict = item.to_dict()
    assert (
        item_dict["links"][0]["href"] == "https://stac.somewhere.io/mycollection.json"
    )
    assert item_dict["stac_extensions"] == []
    assert "datetime" in item_dict["properties"]
    assert item_dict["collection"] == "mycollection"


def test_create_item_raster():
    """Should return a valid item with raster properties."""
    src_path = os.path.join(PREFIX, "dataset_cog.tif")
    item = create_stac_item(src_path, input_datetime=input_date, with_raster=True,)
    assert item.validate()
    item_dict = item.to_dict()
    assert item_dict["links"] == []
    assert item_dict["stac_extensions"] == [
        "https://stac-extensions.github.io/raster/v1.0.0/schema.json",
    ]
    assert "raster:bands" in item_dict["properties"]
    assert len(item_dict["properties"]["raster:bands"]) == 1
    # Nodata=None not in the properties
    assert "nodata" not in item_dict["properties"]["raster:bands"][0]

    # Unit=None not in the properties
    assert "unit" not in item_dict["properties"]["raster:bands"][0]

    assert item_dict["properties"]["raster:bands"][0]["sampling"] in ["point", "area"]

    src_path = os.path.join(PREFIX, "dataset_nodata_nan.tif")
    item = create_stac_item(src_path, input_datetime=input_date, with_raster=True,)
    assert item.validate()
    item_dict = item.to_dict()
    assert item_dict["stac_extensions"] == [
        "https://stac-extensions.github.io/raster/v1.0.0/schema.json",
    ]
    assert "raster:bands" in item_dict["properties"]
    assert numpy.isnan(item_dict["properties"]["raster:bands"][0]["nodata"])

    src_path = os.path.join(PREFIX, "dataset_with_offsets.tif")
    item = create_stac_item(src_path, input_datetime=input_date, with_raster=True,)
    assert item.validate()
    item_dict = item.to_dict()
    assert item_dict["stac_extensions"] == [
        "https://stac-extensions.github.io/raster/v1.0.0/schema.json",
    ]
    assert "raster:bands" in item_dict["properties"]
    assert item_dict["properties"]["raster:bands"][0]["scale"] == 0.0001
    assert item_dict["properties"]["raster:bands"][0]["offset"] == 1000.0
