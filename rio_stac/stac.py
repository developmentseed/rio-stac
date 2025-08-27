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
from pystac.utils import str_to_datetime
from rasterio import transform, warp
from rasterio.features import bounds as feature_bounds
from rasterio.io import DatasetReader, DatasetWriter, MemoryFile
from rasterio.vrt import WarpedVRT

PROJECTION_EXT_VERSION = "v1.1.0"
RASTER_EXT_VERSION = "v1.1.0"
EO_EXT_VERSION = "v1.1.0"

EPSG_4326 = rasterio.crs.CRS.from_epsg(4326)


def bbox_to_geom(bbox: Tuple[float, float, float, float]) -> Dict:
    """Return a geojson geometry from a bbox."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [bbox[0], bbox[1]],
                [bbox[2], bbox[1]],
                [bbox[2], bbox[3]],
                [bbox[0], bbox[3]],
                [bbox[0], bbox[1]],
            ]
        ],
    }


def get_dataset_geom(
    src_dst: Union[DatasetReader, DatasetWriter, WarpedVRT, MemoryFile],
    densify_pts: int = 0,
    precision: int = -1,
    geographic_crs: rasterio.crs.CRS = EPSG_4326,
) -> Dict:
    """Get Raster Footprint."""
    if densify_pts < 0:
        raise ValueError("`densify_pts` must be positive")

    if src_dst.crs is not None:
        # 1. Create Polygon from raster bounds
        geom = bbox_to_geom(src_dst.bounds)

        # 2. Densify the Polygon geometry
        if src_dst.crs != geographic_crs and densify_pts:
            # Derived from code found at
            # https://stackoverflow.com/questions/64995977/generating-equidistance-points-along-the-boundary-of-a-polygon-but-cw-ccw
            coordinates = numpy.asarray(geom["coordinates"][0])

            densified_number = len(coordinates) * densify_pts
            existing_indices = numpy.arange(0, densified_number, densify_pts)
            interp_indices = numpy.arange(existing_indices[-1] + 1)
            interp_x = numpy.interp(interp_indices, existing_indices, coordinates[:, 0])
            interp_y = numpy.interp(interp_indices, existing_indices, coordinates[:, 1])
            geom = {
                "type": "Polygon",
                "coordinates": [[(x, y) for x, y in zip(interp_x, interp_y)]],
            }

        # 3. Reproject the geometry to "epsg:4326"
        geom = warp.transform_geom(src_dst.crs, geographic_crs, geom, precision=precision)
        bbox = feature_bounds(geom)

    else:
        warnings.warn(
            "Input file doesn't have CRS information, setting geometry and bbox to (-180,-90,180,90)."
        )
        bbox = (-180.0, -90.0, 180.0, 90.0)
        geom = bbox_to_geom(bbox)

    return {"bbox": list(bbox), "footprint": geom}


def get_projection_info(
    src_dst: Union[DatasetReader, DatasetWriter, WarpedVRT, MemoryFile],
) -> Dict:
    """Get projection metadata.

    The STAC projection extension allows for three different ways to describe the coordinate reference system
    associated with a raster :
    - EPSG code
    - WKT2
    - PROJJSON

    All are optional, and they can be provided altogether as well. Therefore, as long as one can be obtained from
    the data, we add it to the returned dictionary.

    see: https://github.com/stac-extensions/projection

    """

    epsg = None
    if src_dst.crs is not None:
        # EPSG
        epsg = src_dst.crs.to_epsg() if src_dst.crs.is_epsg_code else None

    meta = {
        "epsg": epsg,
        "geometry": bbox_to_geom(src_dst.bounds),
        "bbox": list(src_dst.bounds),
        "shape": [src_dst.height, src_dst.width],
        "transform": list(src_dst.transform),
    }

    if not epsg and src_dst.crs:
        # WKT2
        try:
            meta["wkt2"] = src_dst.crs.to_wkt()
        except Exception as ex:
            warnings.warn(f"Could not get WKT2 from dataset : {ex}")
            # PROJJSON
            try:
                meta["projjson"] = src_dst.crs.to_dict(projjson=True)
            except (AttributeError, TypeError) as ex:
                warnings.warn(f"Could not get PROJJSON from dataset : {ex}")

    return meta


def get_eobands_info(
    src_dst: Union[DatasetReader, DatasetWriter, WarpedVRT, MemoryFile],
) -> List:
    """Get eo:bands metadata.

    see: https://github.com/stac-extensions/eo#item-properties-or-asset-fields

    """
    eo_bands = []

    colors = src_dst.colorinterp
    for ix in src_dst.indexes:
        band_meta = {"name": f"b{ix}"}

        descr = src_dst.descriptions[ix - 1]
        color = colors[ix - 1].name

        # Description metadata or Colorinterp or Nothing
        description = descr or color
        if description:
            band_meta["description"] = description

        eo_bands.append(band_meta)

    return eo_bands


def _get_stats(arr: numpy.ma.MaskedArray, **kwargs: Any) -> Dict:
    """Calculate array statistics."""
    # Avoid non masked nan/inf values
    numpy.ma.fix_invalid(arr, copy=False)
    sample, edges = numpy.histogram(arr[~arr.mask])
    return {
        "statistics": {
            "mean": arr.mean().item(),
            "minimum": arr.min().item(),
            "maximum": arr.max().item(),
            "stddev": arr.std().item(),
            "valid_percent": float(
                numpy.count_nonzero(~arr.mask) / float(arr.data.size) * 100
            ),
        },
        "histogram": {
            "count": len(edges),
            "min": float(edges.min()),
            "max": float(edges.max()),
            "buckets": sample.tolist(),
        },
    }


def get_raster_info(  # noqa: C901
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

    area_or_point = src_dst.tags().get("AREA_OR_POINT", "").lower()

    # Missing `bits_per_sample` and `spatial_resolution`
    for band in src_dst.indexes:
        value = {
            "data_type": src_dst.dtypes[band - 1],
            "scale": src_dst.scales[band - 1],
            "offset": src_dst.offsets[band - 1],
        }
        if area_or_point:
            value["sampling"] = area_or_point

        # If the Nodata is not set we don't forward it.
        if src_dst.nodata is not None:
            if numpy.isnan(src_dst.nodata):
                value["nodata"] = "nan"
            elif numpy.isposinf(src_dst.nodata):
                value["nodata"] = "inf"
            elif numpy.isneginf(src_dst.nodata):
                value["nodata"] = "-inf"
            else:
                value["nodata"] = src_dst.nodata

        if src_dst.units[band - 1] is not None:
            value["unit"] = src_dst.units[band - 1]

        value.update(
            _get_stats(src_dst.read(indexes=band, out_shape=(height, width), masked=True))
        )
        meta.append(value)

    return meta


def get_media_type(
    src_dst: Union[DatasetReader, DatasetWriter, WarpedVRT, MemoryFile],
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
    asset_media_type: Optional[Union[str, pystac.MediaType]] = "auto",
    asset_href: Optional[str] = None,
    with_proj: bool = False,
    with_raster: bool = False,
    with_eo: bool = False,
    raster_max_size: int = 1024,
    geom_densify_pts: int = 0,
    geom_precision: int = -1,
    geographic_crs: rasterio.crs.CRS = EPSG_4326,
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
        with_eo (bool): Add the `eo` extension and properties (default to False).
        raster_max_size (int): Limit array size from which to get the raster statistics. Defaults to 1024.
        geom_densify_pts (int): Number of points to add to each edge to account for nonlinear edges transformation (Note: GDAL uses 21).
        geom_precision (int): If >= 0, geometry coordinates will be rounded to this number of decimal.

    Returns:
        pystac.Item: valid STAC Item.

    """
    properties = properties or {}
    extensions = extensions or []
    asset_roles = asset_roles or []

    with ExitStack() as ctx:
        if isinstance(source, (DatasetReader, DatasetWriter, WarpedVRT)):
            dataset = source
        else:
            dataset = ctx.enter_context(rasterio.open(source))

        if dataset.gcps[0]:
            src_dst = ctx.enter_context(
                WarpedVRT(
                    dataset,
                    src_crs=dataset.gcps[1],
                    src_transform=transform.from_gcps(dataset.gcps[0]),
                )
            )
        else:
            src_dst = dataset

        dataset_geom = get_dataset_geom(
            src_dst,
            densify_pts=geom_densify_pts,
            precision=geom_precision,
            geographic_crs=geographic_crs,
        )

        media_type = (
            get_media_type(dataset) if asset_media_type == "auto" else asset_media_type
        )

        if "start_datetime" not in properties and "end_datetime" not in properties:
            # Try to get datetime from https://gdal.org/user/raster_data_model.html#imagery-domain-remote-sensing
            acq_date = src_dst.get_tag_item("ACQUISITIONDATETIME", "IMAGERY")
            tiff_date = src_dst.get_tag_item("TIFFTAG_DATETIME")
            dst_date = acq_date or tiff_date
            try:
                dst_datetime = str_to_datetime(dst_date) if dst_date else None
            except ValueError as err:
                warnings.warn(f"Could not get parse date: {dst_date}: {err}")
                dst_datetime = None

            input_datetime = (
                input_datetime
                or dst_datetime
                or datetime.datetime.now(datetime.timezone.utc)
            )

        # add projection properties
        if with_proj:
            extensions.append(
                f"https://stac-extensions.github.io/projection/{PROJECTION_EXT_VERSION}/schema.json",
            )

            properties.update(
                {
                    f"proj:{name}": value
                    for name, value in get_projection_info(src_dst).items()
                }
            )

        # add raster properties
        raster_info = {}
        if with_raster:
            extensions.append(
                f"https://stac-extensions.github.io/raster/{RASTER_EXT_VERSION}/schema.json",
            )

            raster_info = {
                "raster:bands": get_raster_info(dataset, max_size=raster_max_size)
            }

        eo_info: Dict[str, List] = {}
        if with_eo:
            extensions.append(
                f"https://stac-extensions.github.io/eo/{EO_EXT_VERSION}/schema.json",
            )

            eo_info = {"eo:bands": get_eobands_info(src_dst)}

            cloudcover = src_dst.get_tag_item("CLOUDCOVER", "IMAGERY")
            if cloudcover is not None:
                properties.update({"eo:cloud_cover": int(cloudcover)})

    # item
    item = pystac.Item(
        id=id or os.path.basename(dataset.name),
        geometry=dataset_geom["footprint"],
        bbox=dataset_geom["bbox"],
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
            item.add_asset(key=key, asset=asset)

    else:
        item.add_asset(
            key=asset_name,
            asset=pystac.Asset(
                href=asset_href or dataset.name,
                media_type=media_type,
                extra_fields={**raster_info, **eo_info},
                roles=asset_roles,
            ),
        )

    return item
