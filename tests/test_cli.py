"""tests rio_stac.cli."""

import json
import os

import pystac

from rio_stac.scripts.cli import stac

PREFIX = os.path.join(os.path.dirname(__file__), "fixtures")


def test_rio_stac_cli(runner):
    """Should work as expected."""
    with runner.isolated_filesystem():
        src_path = os.path.join(PREFIX, "dataset_cog.tif")
        result = runner.invoke(stac, [src_path])
        assert not result.exception
        assert result.exit_code == 0
        stac_item = json.loads(result.output)
        assert stac_item["type"] == "Feature"
        assert stac_item["assets"]["asset"]
        assert stac_item["assets"]["asset"]["href"] == src_path
        assert stac_item["links"] == []
        assert stac_item["stac_extensions"] == ["proj"]
        assert "datetime" in stac_item["properties"]
        assert "proj:epsg" in stac_item["properties"]

        result = runner.invoke(
            stac,
            [src_path, "--extension", "", "--datetime", "2010-01-01", "--id", "000001"],
        )
        assert not result.exception
        assert result.exit_code == 0
        stac_item = json.loads(result.output)
        assert stac_item["stac_extensions"] == []
        assert stac_item["id"] == "000001"
        assert "datetime" in stac_item["properties"]
        assert stac_item["properties"]["datetime"] == "2010-01-01T00:00:00Z"

        result = runner.invoke(
            stac, [src_path, "--extension", "", "--datetime", "2010-01-01/2010-01-02"]
        )
        assert not result.exception
        assert result.exit_code == 0
        stac_item = json.loads(result.output)
        assert stac_item["stac_extensions"] == []
        assert "datetime" in stac_item["properties"]
        assert not stac_item["properties"]["datetime"]
        assert stac_item["properties"]["start_datetime"] == "2010-01-01T00:00:00Z"
        assert stac_item["properties"]["end_datetime"] == "2010-01-02T00:00:00Z"

        result = runner.invoke(stac, [src_path, "--asset-mediatype", "COG"])
        assert not result.exception
        assert result.exit_code == 0
        stac_item = json.loads(result.output)
        assert stac_item["assets"]["asset"]["type"] == pystac.MediaType.COG

        result = runner.invoke(stac, [src_path, "--asset-mediatype", "auto"])
        assert not result.exception
        assert result.exit_code == 0
        stac_item = json.loads(result.output)
        assert stac_item["assets"]["asset"]["type"] == pystac.MediaType.GEOTIFF

        result = runner.invoke(stac, [src_path, "--property", "comment:name=something"])
        assert not result.exception
        assert result.exit_code == 0
        stac_item = json.loads(result.output)
        assert stac_item["properties"]["comment:name"] == "something"

        result = runner.invoke(stac, [src_path, "--property", "comment:something"])
        assert result.exception
        assert result.exit_code == 2

        result = runner.invoke(stac, [src_path, "-o", "item.json"])
        assert not result.exception
        assert result.exit_code == 0
        with open("item.json", "r") as f:
            stac_item = json.loads(f.read())
        assert stac_item["type"] == "Feature"
        assert stac_item["assets"]["asset"]
        assert stac_item["links"] == []
        assert stac_item["stac_extensions"] == ["proj"]
        assert "datetime" in stac_item["properties"]
        assert "proj:epsg" in stac_item["properties"]
