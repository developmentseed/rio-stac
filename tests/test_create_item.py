"""Tests for STAC Item creation and post-processing."""
import json
import os
import shutil
from click.testing import CliRunner
from rio_stac.scripts.cli import stac
import pytest
from rio_stac import build_stac_assets, create_stac_item

@pytest.fixture
def s2_safe_dir(tmp_path):
    """Create a mock Sentinel-2 SAFE directory structure."""
    safe_dir = tmp_path / "S2A_MSIL1C_20251128T111431_N0511_R137_T31VEE_20251128T121631.SAFE"
    safe_dir.mkdir()

    # Metadata
    (safe_dir / "MTD_MSIL1C.xml").write_text("<xml>metadata</xml>")
    (safe_dir / "manifest.safe").write_text("<safe>manifest</safe>")

    # Granule dir
    granule_dir = safe_dir / "GRANULE" / "L1C_T31VEE_A054503_20251128T111434" / "IMG_DATA"
    granule_dir.mkdir(parents=True)

    # Fake Raster Bands (copy from fixture)
    fixture_path = "tests/fixtures/dataset.tif"
    if os.path.exists(fixture_path):
        shutil.copy(fixture_path, granule_dir / "T31VEE_20251128T111431_B03.jp2")
        shutil.copy(fixture_path, granule_dir / "T31VEE_20251128T111431_B04.jp2")

    # Quicklook (simulated)
    (safe_dir / "S2A_MSIL1C_20251128T111431_N0511_R137_T31VEE_20251128T121631-ql.jpg").write_bytes(b"fake_jpeg_content")

    return safe_dir

def test_s2_l1c_builder(s2_safe_dir):
    """Test building a STAC Item for S2 L1C product using CLI logic."""
    runner = CliRunner()

    cmd = [
        str(s2_safe_dir),
        "--recursive",
        "--pattern", "*_B02.jp2",
        "--pattern", "*_B03.jp2",
        "--pattern", "*_B04.jp2",
        "--pattern", "manifest.safe",
        "--pattern", "MTD_MSIL1C.xml",
        "--pattern", "*ql.jp*",
    ]

    result = runner.invoke(stac, cmd)
    assert result.exit_code == 0

    item = json.loads(result.output)
    assets = item["assets"]

    # Verify Assets existence
    assert any(k.endswith("B03") for k in assets)
    assert any(k.endswith("B04") for k in assets)
    assert "MTD_MSIL1C" in assets
    assert "manifest" in assets

    # Verify Thumbnail logic
    # Should exist and be named 'thumbnail'
    assert "thumbnail" in assets
    assert "thumbnail" in assets["thumbnail"]["roles"]
    assert assets["thumbnail"]["title"] == "thumbnail"

    # Verify Metadata logic
    assert "metadata" in assets["MTD_MSIL1C"]["roles"]
    assert "metadata" in assets["manifest"]["roles"]

def test_general_post_processing(s2_safe_dir):
    """Test that create_stac_item applies general post-processing rules."""

    # 1. Build Assets
    patterns = [
        "*_B02.jp2", "*_B03.jp2", "*_B04.jp2",
        "manifest.safe", "MTD_MSIL1C.xml", "*ql.jp*"
    ]
    assets = build_stac_assets(
        directory=str(s2_safe_dir),
        patterns=patterns,
        with_proj=True # Ensure proj info is generated for assets
    )

    # 2. Create Item
    # Find a source
    source_path = None
    for key, asset in assets.items():
        if "B03" in key:
             source_path = os.path.join(str(s2_safe_dir), asset.href)
             break

    item = create_stac_item(
        source=source_path,
        assets=assets,
        with_proj=True,
        with_raster=True,
        with_eo=True,
        id="test-item"
    )

    item_dict = item.to_dict()

    # 3.1 Check Item Properties (No proj:*)
    for k in item_dict["properties"]:
        assert not k.startswith("proj:"), f"Item property {k} starts with proj:"

    assets = item_dict["assets"]

    # 4. Check Thumbnail
    assert "thumbnail" in assets
    thumb = assets["thumbnail"]
    assert "thumbnail" in thumb["roles"]
    assert thumb["title"] == "thumbnail"
    assert thumb["proj:code"] is None
    assert "bands" not in thumb
    assert "raster:bands" not in thumb

    # Ensure no other proj fields
    for k in thumb:
        if k.startswith("proj:") and k != "proj:code":
            raise AssertionError(f"Thumbnail has forbidden field {k}")

    # 5. Check Metadata
    meta = assets["MTD_MSIL1C"]
    assert "metadata" in meta["roles"]
    for k in meta:
        assert not k.startswith("proj:")

    # 3.2 Check Data (Raster)
    # Find a band
    band_key = next(k for k in assets if "B03" in k)
    band = assets[band_key]
    assert "data" in band["roles"]
