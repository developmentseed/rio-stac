"""rio_stac.scripts.cli."""
import json

import click
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
    type=str,
    help="The searchable date and time of the assets, in UTC.",
)
@click.option(
    "--with-proj/--without-proj", default=True, help="Add PROJ extension and metadata."
)
@click.option(
    "--extention",
    "-e",
    type=str,
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
@click.option("--output", "-o", type=click.Path(exists=False), help="Output file name")
def stac(
    input, datetime, with_proj, extention, collection, property, asset_name, id, output
):
    """Rasterio stac cli."""
    item = create_stac_item(
        input,
        datetime=datetime,
        proj=with_proj,
        extentions=extention,
        collection=collection,
        item_properties=property,
        id=id,
        asset_name=asset_name,
    )

    if output:
        with open(output, "w") as f:
            f.write(json.dumps(item))
    else:
        click.echo(json.dumps(item))
