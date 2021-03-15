"""Create STAC Item from a rasterio dataset."""

import datetime as pydatetime
import os
from contextlib import ExitStack
from typing import Any, Dict, List, Optional, Sequence, Union

import pystac
import rasterio
from rasterio import warp
from rasterio.io import DatasetReader, DatasetWriter, MemoryFile
from rasterio.vrt import WarpedVRT


def bbox_to_geom(bbox: Sequence[float]) -> Dict:
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
    source: Union[str, DatasetReader, DatasetWriter, WarpedVRT, MemoryFile]
) -> Dict:
    """Get Raster Metadata."""
    metadata: Dict[str, Any] = {}

    with ExitStack() as ctx:
        if isinstance(source, (DatasetReader, DatasetWriter, WarpedVRT)):
            src_dst = source
        else:
            src_dst = ctx.enter_context(rasterio.open(source))

        bbox = warp.transform_bounds(
            src_dst.crs, "epsg:4326", *src_dst.bounds, densify_pts=21
        )

        metadata["bbox"] = bbox
        metadata["footprint"] = bbox_to_geom(bbox)

        # GDAL Metadata
        metadata["tags"] = src_dst.tags()
        metadata["width"] = src_dst.width
        metadata["height"] = src_dst.height
        metadata["dtype"] = src_dst.dtypes[0]

        # Proj
        try:
            epsg = src_dst.crs.to_epsg() or "null"
        except AttributeError:
            epsg = "null"

        metadata["proj"] = {
            "epsg": epsg,
            "geometry": bbox_to_geom(src_dst.bounds),
            "bbox": src_dst.bounds,
            "shape": [src_dst.height, src_dst.width],
            "transform": list(src_dst.transform),
        }

        # rasterio can't reproduce wkt2
        # ref: https://github.com/mapbox/rasterio/issues/2044
        # if epsg == "null":
        #      metadata["proj"]["wkt2"] = src_dst.crs.to_wkt()

    return metadata


def create_stac_item(
    src_path: str,
    datetime: Optional[Union[str, pydatetime.datetime]] = None,
    proj: bool = True,
    extentions: Optional[List[str]] = None,
    item_links: List = [],
    collection: Optional[str] = None,
    item_properties: Optional[Dict] = None,
    id: Optional[str] = None,
    asset_name: str = "cog",
    asset_roles: Optional[List[str]] = None,
    asset_media_type: pystac.MediaType = pystac.MediaType.COG,
) -> pystac.Item:
    """Create a Stac Item."""
    meta = get_metadata(src_path)

    properties = item_properties or {}

    if not datetime:
        datetime = pydatetime.datetime.utcnow()
    else:
        if isinstance(datetime, str) and "/" in datetime:
            start_datetime, end_datetime = datetime.split("/")
            properties["start_datetime"] = start_datetime
            properties["end_datetime"] = end_datetime
            datetime = None

    extentions = extentions or []
    if proj and "proj" not in extentions:
        extentions.append("proj")

    if "proj" in extentions:
        properties.update(
            {
                f"proj:{name}": value
                for name, value in meta["proj"].items()
                if value is not None
            }
        )

    # item
    item = pystac.Item(
        id=id or os.path.basename(src_path),
        geometry=meta["footprint"],
        bbox=meta["bbox"],
        collection=collection,
        stac_extensions=extentions,
        datetime=datetime,
        properties=properties,
    )

    # item.assets
    item.add_asset(
        key=asset_name, asset=pystac.Asset(href=src_path, media_type=asset_media_type)
    )

    return item.to_dict()
