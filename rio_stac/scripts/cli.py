"""rio_stac.scripts.cli."""

import json

import click
import rasterio
from pystac import MediaType
from pystac.utils import datetime_to_str, str_to_datetime
from rasterio.rio import options

from rio_stac import create_stac_item


def _cb_key_val(ctx, param, value):
    if not value:
        return {}
    else:
        out = {}
        for pair in value:
            if "=" not in pair:
                raise click.BadParameter(
                    "Invalid syntax for KEY=VAL arg: {}".format(pair)
                )
            else:
                k, v = pair.split("=", 1)
                out[k] = v
        return out


@click.command()
@options.file_in_arg
@click.option(
    "--datetime",
    "-d",
    "input_datetime",
    type=str,
    help="The date and time of the assets, in UTC (e.g 2020-01-01, 2020-01-01T01:01:01).",
)
@click.option(
    "--extension",
    "-e",
    type=str,
    multiple=True,
    help="STAC extension URL the Item implements.",
)
@click.option(
    "--collection", "-c", type=str, help="The Collection ID that this item belongs to."
)
@click.option("--collection-url", type=str, help="Link to the STAC Collection.")
@click.option(
    "--property",
    "-p",
    metavar="NAME=VALUE",
    multiple=True,
    callback=_cb_key_val,
    help="Additional property to add.",
)
@click.option("--id", type=str, help="Item id.")
@click.option(
    "--asset-name",
    "-n",
    type=str,
    default="asset",
    help="Asset name.",
    show_default=True,
)
@click.option("--asset-href", type=str, help="Overwrite asset href.")
@click.option(
    "--asset-mediatype",
    type=click.Choice([it.name for it in MediaType] + ["auto"]),
    help="Asset media-type.",
)
@click.option(
    "--with-proj/--without-proj",
    default=True,
    help="Add the 'projection' extension and properties.",
    show_default=True,
)
@click.option(
    "--with-raster/--without-raster",
    default=True,
    help="Add the 'raster' extension and properties.",
    show_default=True,
)
@click.option(
    "--with-eo/--without-eo",
    default=True,
    help="Add the 'eo' extension and properties.",
    show_default=True,
)
@click.option(
    "--max-raster-size",
    type=int,
    default=1024,
    help="Limit array size from which to get the raster statistics.",
    show_default=True,
)
@click.option(
    "--densify-geom",
    type=int,
    help="Densifies the number of points on each edges of the polygon geometry to account for non-linear transformation.",
)
@click.option(
    "--geom-precision",
    type=int,
    default=-1,
    help="Round geometry coordinates to this number of decimal. By default, coordinates will not be rounded",
)
@click.option("--output", "-o", type=click.Path(exists=False), help="Output file name")
@click.option(
    "--config",
    "config",
    metavar="NAME=VALUE",
    multiple=True,
    callback=options._cb_key_val,
    help="GDAL configuration options.",
)
def stac(
    input,
    input_datetime,
    extension,
    collection,
    collection_url,
    property,
    id,
    asset_name,
    asset_href,
    asset_mediatype,
    with_proj,
    with_raster,
    with_eo,
    max_raster_size,
    densify_geom,
    geom_precision,
    output,
    config,
):
    """Rasterio STAC plugin: Create a STAC Item for raster dataset."""
    property = property or {}
    densify_geom = densify_geom or 0

    if input_datetime:
        if "/" in input_datetime:
            start_datetime, end_datetime = input_datetime.split("/")
            property["start_datetime"] = datetime_to_str(str_to_datetime(start_datetime))
            property["end_datetime"] = datetime_to_str(str_to_datetime(end_datetime))
            input_datetime = None
        else:
            input_datetime = str_to_datetime(input_datetime)

    if asset_mediatype and asset_mediatype != "auto":
        asset_mediatype = MediaType[asset_mediatype]

    extensions = [e for e in extension if e]

    with rasterio.Env(**config):
        item = create_stac_item(
            input,
            input_datetime=input_datetime,
            extensions=extensions,
            collection=collection,
            collection_url=collection_url,
            properties=property,
            id=id,
            asset_name=asset_name,
            asset_href=asset_href,
            asset_media_type=asset_mediatype,
            with_proj=with_proj,
            with_raster=with_raster,
            with_eo=with_eo,
            raster_max_size=max_raster_size,
            geom_densify_pts=densify_geom,
            geom_precision=geom_precision,
        )

    if output:
        with open(output, "w") as f:
            f.write(json.dumps(item.to_dict(), separators=(",", ":")))
    else:
        click.echo(json.dumps(item.to_dict(), separators=(",", ":")))
