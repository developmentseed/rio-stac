"""Create STAC Item from a rasterio dataset."""

import datetime
import os
from contextlib import ExitStack
from typing import Any, Dict, List, Optional, Tuple, Union

import pystac
import rasterio
from rasterio import warp
from rasterio.io import DatasetReader, DatasetWriter, MemoryFile
from rasterio.vrt import WarpedVRT


def bbox_to_geom(bbox: Tuple[float, float, float, float]) -> Dict:
    """Return a geojson geometry from a bbox."""
    # TODO: Handle dateline geometry
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [bbox[0], bbox[3]],
                [bbox[0], bbox[1]],
                [bbox[2], bbox[1]],
                [bbox[2], bbox[3]],
                [bbox[0], bbox[3]],
            ]
        ],
    }


def get_metadata(
    src_dst: Union[DatasetReader, DatasetWriter, WarpedVRT, MemoryFile]
) -> Dict:
    """Get Raster Metadata."""
    metadata: Dict[str, Any] = {}

    metadata["name"] = src_dst.name

    bbox = warp.transform_bounds(
        src_dst.crs, "epsg:4326", *src_dst.bounds, densify_pts=21
    )

    metadata["bbox"] = list(bbox)
    metadata["footprint"] = bbox_to_geom(bbox)

    # GDAL Metadata
    metadata["tags"] = src_dst.tags()
    metadata["width"] = src_dst.width
    metadata["height"] = src_dst.height
    metadata["dtype"] = src_dst.dtypes[0]

    # Proj
    try:
        epsg = src_dst.crs.to_epsg() or None
    except AttributeError:
        epsg = None

    metadata["proj"] = {
        "epsg": epsg,
        "geometry": bbox_to_geom(src_dst.bounds),
        "bbox": list(src_dst.bounds),
        "shape": [src_dst.height, src_dst.width],
        "transform": list(src_dst.transform),
    }

    # rasterio can't reproduce wkt2
    # ref: https://github.com/mapbox/rasterio/issues/2044
    # if epsg is None:
    #      metadata["proj"]["wkt2"] = src_dst.crs.to_wkt()

    return metadata


def create_stac_item(
    source: Union[str, DatasetReader, DatasetWriter, WarpedVRT, MemoryFile],
    input_datetime: Optional[datetime.datetime] = None,
    extensions: Optional[List[str]] = None,
    item_links: List = [],
    collection: Optional[str] = None,
    item_properties: Optional[Dict] = None,
    id: Optional[str] = None,
    asset_name: str = "cog",
    asset_roles: Optional[List[str]] = None,
    asset_media_type: pystac.MediaType = pystac.MediaType.COG,
    assert_href: Optional[str] = None,
) -> pystac.Item:
    """Create a Stac Item."""

    with ExitStack() as ctx:
        if isinstance(source, (DatasetReader, DatasetWriter, WarpedVRT)):
            src_dst = source
        else:
            src_dst = ctx.enter_context(rasterio.open(source))

        meta = get_metadata(src_dst)

    properties = item_properties or {}

    extensions = extensions or []

    if "proj" in extensions:
        properties.update(
            {
                f"proj:{name}": value
                for name, value in meta["proj"].items()
                if value is not None
            }
        )

    # item
    item = pystac.Item(
        id=id or os.path.basename(meta["name"]),
        geometry=meta["footprint"],
        bbox=meta["bbox"],
        collection=collection,
        stac_extensions=extensions,
        datetime=input_datetime,
        properties=properties,
    )

    # item.assets
    item.add_asset(
        key=asset_name,
        asset=pystac.Asset(
            href=assert_href or meta["name"], media_type=asset_media_type,
        ),
    )

    return item.to_dict()
