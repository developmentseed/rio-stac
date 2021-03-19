"""Create STAC Item from a rasterio dataset."""

import datetime
import os
import warnings
from contextlib import ExitStack
from typing import Any, Dict, List, Optional, Tuple, Union

import pystac
import rasterio
from rasterio import warp
from rasterio.io import DatasetReader, DatasetWriter, MemoryFile
from rasterio.vrt import WarpedVRT


def bbox_to_geom(bbox: Tuple[float, float, float, float]) -> Dict:
    """Return a geojson geometry from a bbox."""
    # TODO: Handle dateline crossing geometry
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

    # To Do: handle non-geo data
    if src_dst.crs is not None:
        bbox = warp.transform_bounds(
            src_dst.crs, "epsg:4326", *src_dst.bounds, densify_pts=21
        )
    else:
        warnings.warn(
            "Input file doesn't have geom information, setting bbox to (-180,-90,180,90)."
        )
        bbox = [-180.0, -90.0, 180.0, 90.0]

    metadata["bbox"] = list(bbox)
    metadata["footprint"] = bbox_to_geom(bbox)

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


def get_media_type(
    src_dst: Union[DatasetReader, DatasetWriter, WarpedVRT, MemoryFile]
) -> Optional[pystac.MediaType]:
    """Find MediaType for a raster dataset."""
    driver = src_dst.driver

    if driver == "GTiff":
        if src_dst.crs:
            return pystac.MediaType.GEOTIFF
        else:
            return pystac.MediaType.TIFF

    elif driver in [
        "JP2ECW",
        "JP2KAK",
        "JP2LURA",
        "JP2MrSID",
        "JP2OpenJPEG",
        "JPEG2000",
    ]:
        return pystac.MediaType.JPEG2000

    elif driver in ["HDF4", "HDF4Image"]:
        return pystac.MediaType.HDF

    elif driver in ["HDF5", "HDF5Image"]:
        return pystac.MediaType.HDF5

    elif driver == "JPEG":
        return pystac.MediaType.JPEG

    elif driver == "PNG":
        return pystac.MediaType.PNG

    warnings.warn("Could not determine the media type from GDAL driver.")
    return None


def create_stac_item(
    source: Union[str, DatasetReader, DatasetWriter, WarpedVRT, MemoryFile],
    input_datetime: Optional[datetime.datetime] = None,
    extensions: Optional[List[str]] = None,
    collection: Optional[str] = None,
    properties: Optional[Dict] = None,
    id: Optional[str] = None,
    assets: Optional[Dict[str, pystac.Asset]] = None,
    asset_name: str = "asset",
    asset_roles: Optional[List[str]] = None,
    asset_media_type: Optional[Union[str, pystac.MediaType]] = None,
    asset_href: Optional[str] = None,
) -> pystac.Item:
    """Create a Stac Item.

    Args:
        source (str or rasterio openned dataset): input path or rasterio dataset.
        input_datetime (datetime.datetime, optional): datetime associated with the item.
        extensions (list of str): input list of extensions to use in the item.
        collection (str, optional): collection's name the item belong to.
        properties (dict, optional): additional properties to add in the item.
        id (str, optional): id to assign to the item (default to the source basename).
        assets (dict, optional): Assets to set in the item. If set we won't create one from the source.
        asset_name (str, optional): asset name in the Assets object.
        asset_roles (list of str, optional): list of asset's role.
        asset_media_type (str or pystac.MediaType, optional): asset's media type.
        asset_href (str, optional): asset's URI (default to input path).

    Returns:
        pystac.Item: valid STAC Item.

    """
    with ExitStack() as ctx:
        if isinstance(source, (DatasetReader, DatasetWriter, WarpedVRT)):
            src_dst = source
        else:
            src_dst = ctx.enter_context(rasterio.open(source))

        meta = get_metadata(src_dst)

        media_type = (
            get_media_type(src_dst) if asset_media_type == "auto" else asset_media_type
        )

    properties = properties or {}

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
    if assets:
        for key, asset in assets.items():
            item.add_asset(
                key=key, asset=asset,
            )

    else:
        item.add_asset(
            key=asset_name,
            asset=pystac.Asset(href=asset_href or meta["name"], media_type=media_type),
        )

    return item
