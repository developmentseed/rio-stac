"""rio_stac.scripts.cli."""

import json
import os
import re

import click
import rasterio
from pystac import MediaType
from pystac.utils import datetime_to_str, str_to_datetime
from rasterio.rio import options

from rio_stac import build_stac_assets, create_stac_item


_UNQUOTED_KEY_RE = re.compile(r'(?P<lead>[{,]\s*)(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:')


def _parse_jsonish(value: str):
    """Try to parse JSON, falling back to quoting unquoted keys."""
    stripped = value.strip()
    candidates = [stripped, stripped.replace("'", '"')]
    if stripped.startswith("{") or stripped.startswith("["):
        candidates.append(
            _UNQUOTED_KEY_RE.sub(lambda m: f'{m.group("lead")}"{m.group("key")}":', stripped)
        )

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    return value


def _cb_key_val(ctx, param, value):
    if not value:
        return {}
    else:
        out = {}
        for pair in value:
            if "=" not in pair:
                raise click.BadParameter(f"Invalid syntax for KEY=VAL arg: {pair}")
            else:
                k, v = pair.split("=", 1)
                parsed = _parse_jsonish(v)
                if k in out and isinstance(out[k], dict) and isinstance(parsed, dict):
                    out[k].update(parsed)
                else:
                    out[k] = parsed
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
    help="Additional property to add. JSON values allowed for nested data.",
)
@click.option(
    "--private-property",
    "-P",
    metavar="NAME=VALUE",
    multiple=True,
    callback=_cb_key_val,
    help="Additional property to add under '_private' without JSON braces.",
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
    "--with-private-data/--without-private-data",
    "with_private",
    default=False,
    help="Add the '_private' entry to output item. Implicitly enabled if -P or -p _private=... is used.",
    show_default=False,
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
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=False,
    help="Process input directory recursively.",
)
@click.option(
    "--pattern",
    type=str,
    multiple=True,
    help="Glob pattern to filter files when using --recursive.",
)
def stac(
    input,
    input_datetime,
    extension,
    collection,
    collection_url,
    property,
    private_property,
    id,
    asset_name,
    asset_href,
    asset_mediatype,
    with_proj,
    with_raster,
    with_eo,
    with_private,
    max_raster_size,
    densify_geom,
    geom_precision,
    output,
    config,
    recursive,
    pattern,
):
    """Rasterio STAC plugin: Create a STAC Item for raster dataset."""
    property = property or {}
    private_property = private_property or {}
    densify_geom = densify_geom or 0

    if "_private" in property:
        with_private = True

    if private_property:
        with_private = True

    if "_private" in property and not isinstance(property["_private"], dict):
        raise click.BadParameter("When provided, '_private' must be a JSON object.")

    if with_private:
        base_private = property.get("_private") or {}
        if not isinstance(base_private, dict):
            raise click.BadParameter("When provided, '_private' must be a JSON object.")
        if private_property:
            base_private = {**base_private, **private_property}
        property["_private"] = base_private

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
        if recursive:
            if not os.path.isdir(input):
                raise click.BadParameter("Input must be a directory when using --recursive.")

            assets = build_stac_assets(
                directory=input,
                patterns=list(pattern) if pattern else None,
                asset_media_type=asset_mediatype,
                with_raster=with_raster,
                with_eo=with_eo,
                raster_max_size=max_raster_size,
                histogram_bins=10,  # Default
            )

            if not assets:
                raise click.ClickException("No valid files found in directory matching criteria.")

            # Determine source for Item geometry/bbox
            source = None
            # Prefer a "data" asset as source
            for asset in assets.values():
                if "data" in (asset.roles or []):
                    # Re-construct full path for source opening
                    # asset.href is relative (basename)
                    source = os.path.join(input, asset.href)
                    break

            # Fallback to any asset if no data role found (e.g. only thumbnails?)
            # Or fallback to first found
            if not source and assets:
                # Pick the first one that is likely a raster (not metadata)
                for asset in assets.values():
                    if "metadata" not in (asset.roles or []):
                         source = os.path.join(input, asset.href)
                         break

            if not source:
                 raise click.ClickException("No valid raster asset found to derive Item geometry.")

            if not id:
                id = os.path.basename(input.rstrip(os.sep))

            item = create_stac_item(
                source,
                input_datetime=input_datetime,
                extensions=extensions,
                collection=collection,
                collection_url=collection_url,
                properties=property,
                id=id,
                assets=assets,
                asset_name=asset_name,
                asset_href=asset_href,
                asset_media_type=asset_mediatype,
                with_proj=with_proj,
                with_raster=with_raster,
                with_eo=with_eo,
                with_private=with_private,
                raster_max_size=max_raster_size,
                geom_densify_pts=densify_geom,
                geom_precision=geom_precision,
            )

        else:
            try:
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
                    with_private=with_private,
                    raster_max_size=max_raster_size,
                    geom_densify_pts=densify_geom,
                    geom_precision=geom_precision,
                )
            except rasterio.errors.RasterioIOError:
                if os.path.isdir(input):
                    raise click.ClickException(
                        f"Input '{input}' is a directory. Did you mean to use `--recursive`?"
                    ) from None
                raise

    if output:
        with open(output, "w") as f:
            f.write(json.dumps(item.to_dict(), separators=(",", ":")))
    else:
        click.echo(json.dumps(item.to_dict(), separators=(",", ":")))
