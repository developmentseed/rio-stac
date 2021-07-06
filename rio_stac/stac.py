"""Create STAC Item from a rasterio dataset."""

import datetime
import math
import os
import warnings
from contextlib import ExitStack
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy
import pystac
import rasterio
from rasterio import warp
from rasterio.io import DatasetReader, DatasetWriter, MemoryFile
from rasterio.vrt import WarpedVRT

PROJECTION_EXT_VERSION = "v1.0.0"
RASTER_EXT_VERSION = "v1.1.0"


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
    return metadata


def get_projection_info(
    src_dst: Union[DatasetReader, DatasetWriter, WarpedVRT, MemoryFile]
) -> Dict:
    """Get projection metadata.

    see: https://github.com/stac-extensions/projection/#item-properties-or-asset-fields

    """
    try:
        epsg = src_dst.crs.to_epsg() or None
    except AttributeError:
        epsg = None

    meta = {
        "epsg": epsg,
        "geometry": bbox_to_geom(src_dst.bounds),
        "bbox": list(src_dst.bounds),
        "shape": [src_dst.height, src_dst.width],
        "transform": list(src_dst.transform),
    }
    # rasterio can't reproduce wkt2
    # ref: https://github.com/mapbox/rasterio/issues/2044
    # if epsg is None:
    #      meta["wkt2"] = src_dst.crs.to_wkt()
    return meta


def _get_stats(arr: numpy.ma.array, **kwargs: Any) -> Dict:
    """Calculate array statistics."""
    sample, edges = numpy.histogram(arr[~arr.mask])
    return {
        "statistics": {
            "mean": arr.mean().item(),
            "minimum": arr.min().item(),
            "maximum": arr.max().item(),
            "stdev": arr.std().item(),
            "valid_percent": numpy.count_nonzero(~arr.mask)
            / float(arr.data.size)
            * 100,
        },
        "histogram": {
            "count": len(edges),
            "min": edges.min(),
            "max": edges.max(),
            "buckets": sample.tolist(),
        },
    }


def get_raster_info(
    src_dst: Union[DatasetReader, DatasetWriter, WarpedVRT, MemoryFile],
    max_size: int = 1024,
) -> List[Dict]:
    """Get raster metadata.

    see: https://github.com/stac-extensions/raster#raster-band-object

    """
    height = src_dst.height
    width = src_dst.width
    if max_size:
        if max(width, height) > max_size:
            ratio = height / width
            if ratio > 1:
                height = max_size
                width = math.ceil(height / ratio)
            else:
                width = max_size
                height = math.ceil(width * ratio)

    meta: List[Dict] = []

    area_or_point = src_dst.tags()["AREA_OR_POINT"].lower()

    # Missing `bits_per_sample` and `spatial_resolution`
    for band in src_dst.indexes:
        value = {
            "sampling": area_or_point,
            "data_type": src_dst.dtypes[band - 1],
            "scale": src_dst.scales[band - 1],
            "offset": src_dst.offsets[band - 1],
        }

        # If the Nodata is not set we don't forward it.
        if src_dst.nodata is not None:
            if numpy.isnan(src_dst.nodata):
                value["nodata"] = "nan"
            elif src_dst.nodata and numpy.inf:
                value["nodata"] = "inf"
            elif src_dst.nodata and -numpy.inf:
                value["nodata"] = "-inf"
            else:
                value["nodata"] = src_dst.nodata

        if src_dst.units[band - 1] is not None:
            value["unit"] = src_dst.units[band - 1]

        value.update(
            _get_stats(
                src_dst.read(indexes=band, out_shape=(height, width), masked=True)
            )
        )
        meta.append(value)

    return meta


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
    collection_url: Optional[str] = None,
    properties: Optional[Dict] = None,
    id: Optional[str] = None,
    assets: Optional[Dict[str, pystac.Asset]] = None,
    asset_name: str = "asset",
    asset_roles: Optional[List[str]] = None,
    asset_media_type: Optional[Union[str, pystac.MediaType]] = None,
    asset_href: Optional[str] = None,
    with_proj: bool = False,
    with_raster: bool = False,
    raster_max_size: int = 1024,
) -> pystac.Item:
    """Create a Stac Item.

    Args:
        source (str or opened rasterio dataset): input path or rasterio dataset.
        input_datetime (datetime.datetime, optional): datetime associated with the item.
        extensions (list of str): input list of extensions to use in the item.
        collection (str, optional): name of collection the item belongs to.
        collection_url (str, optional): Link to the STAC Collection.
        properties (dict, optional): additional properties to add in the item.
        id (str, optional): id to assign to the item (default to the source basename).
        assets (dict, optional): Assets to set in the item. If set we won't create one from the source.
        asset_name (str, optional): asset name in the Assets object.
        asset_roles (list of str, optional): list of str | list of asset's roles.
        asset_media_type (str or pystac.MediaType, optional): asset's media type.
        asset_href (str, optional): asset's URI (default to input path).
        with_proj (bool): Add the `projection` extension and properties (default to False).
        with_raster (bool): Add the `raster` extension and properties (default to False).
        raster_max_size (int): Limit array size from which to get the raster statistics, This is used to reduce data transfer. Defaults to 1024.

    Returns:
        pystac.Item: valid STAC Item.

    """
    properties = properties or {}
    extensions = extensions or []

    with ExitStack() as ctx:
        if isinstance(source, (DatasetReader, DatasetWriter, WarpedVRT)):
            src_dst = source
        else:
            src_dst = ctx.enter_context(rasterio.open(source))

        meta = get_metadata(src_dst)

        media_type = (
            get_media_type(src_dst) if asset_media_type == "auto" else asset_media_type
        )

        # add projection properties
        if with_proj:
            properties.update(
                {
                    f"proj:{name}": value
                    for name, value in get_projection_info(src_dst).items()
                }
            )
            extensions.append(
                f"https://stac-extensions.github.io/projection/{PROJECTION_EXT_VERSION}/schema.json",
            )

        # add raster properties
        if with_raster:
            properties.update({"raster:bands": get_raster_info(src_dst)})
            extensions.append(
                f"https://stac-extensions.github.io/raster/{RASTER_EXT_VERSION}/schema.json",
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

    # if we add a collection we MUST add a link
    if collection:
        item.add_link(
            pystac.Link(
                pystac.RelType.COLLECTION,
                collection_url or collection,
                media_type=pystac.MediaType.JSON,
            )
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
