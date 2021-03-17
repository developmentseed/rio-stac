"""rio_stac.scripts.cli."""
import datetime
import json

import click
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
    help="The searchable date and time of the assets, in UTC.",
)
@click.option(
    "--extension",
    "-e",
    type=str,
    default=["proj"],
    multiple=True,
    help="STAC extension the Item implements.",
)
@click.option(
    "--collection", "-c", type=str, help="The Collection ID that this item belongs to."
)
@click.option(
    "--property",
    "-p",
    metavar="NAME=VALUE",
    multiple=True,
    callback=_cb_key_val,
    help="Additional property to add.",
)
@click.option("--id", type=str, help="Item id.")
@click.option("--asset-name", "-n", type=str, default="cog", help="Asset name.")
@click.option("--asset-href", type=str, default="asset", help="Overwrite asset href.")
@click.option("--output", "-o", type=click.Path(exists=False), help="Output file name")
def stac(
    input,
    input_datetime,
    extension,
    collection,
    property,
    id,
    asset_name,
    asset_href,
    output,
):
    """Rasterio stac cli."""
    property = property or {}

    if not input_datetime:
        input_datetime = datetime.datetime.utcnow()
    else:
        if isinstance(input_datetime, str) and "/" in input_datetime:
            start_datetime, end_datetime = input_datetime.split("/")
            property["start_datetime"] = datetime_to_str(
                str_to_datetime(start_datetime)
            )
            property["end_datetime"] = datetime_to_str(str_to_datetime(end_datetime))
            input_datetime = None

    item = create_stac_item(
        input,
        input_datetime=input_datetime,
        extensions=extension,
        collection=collection,
        item_properties=property,
        id=id,
        asset_name=asset_name,
        asset_href=asset_href,
    )

    if output:
        with open(output, "w") as f:
            f.write(json.dumps(item, separators=(",", ":")))
    else:
        click.echo(json.dumps(item, separators=(",", ":")))
