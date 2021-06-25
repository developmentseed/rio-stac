
`rio-stac` can be used either from the command line as a rasterio plugin (`rio stac`) or from your own script.

For more information about the `Item` specification, please see https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md

# CLI

```
$ rio stac --help

Usage: rio stac [OPTIONS] INPUT

  Rasterio STAC plugin: Create a STAC Item for raster dataset.

Options:
  -d, --datetime TEXT             The date and time of the assets, in UTC (e.g 2020-01-01, 2020-01-01T01:01:01).
  -e, --extension TEXT            STAC extensions the Item implements (default is set to ["proj"]). Multiple allowed (e.g. `-e extensionUrl1 -e extensionUrl2`).
  -c, --collection TEXT           The Collection ID that this item belongs to.
  --collection-url TEXT           Link to the STAC Collection.
  -p, --property NAME=VALUE       Additional property to add (e.g `-p myprops=1`). Multiple allowed.
  --id TEXT                       Item id.
  -n, --asset-name TEXT           Asset name.
  --asset-href TEXT               Overwrite asset href.
  --asset-mediatype [COG|GEOJSON|GEOPACKAGE|GEOTIFF|HDF|HDF5|JPEG|JPEG2000|JSON|PNG|TEXT|TIFF|XML|auto] Asset media-type.
  --with-proj / --without-proj    Add the projection extension and properties (default to True).
  -o, --output PATH               Output file name
  --help                          Show this message and exit.
```

### How To

The CLI can be run as is, just by passing a `source` raster data. You can also use options to customize the output STAC item:

- **datetime** (-d, --datetime)

    By design, all STAC items must have a datetime in their properties. By default the CLI will set the time to the actual UTC Time. The CLI will accept any format supported by [`dateparser`](https://dateparser.readthedocs.io/en/latest/).

    You can also define `start_datetime` and `end_datetime` by using `--datetime {start}/{end}` notation.

- **extension** (-e, --extension)

    STAC Item can have [extensions](https://github.com/radiantearth/stac-spec/tree/master/extensions) which indicates that the item has additional properies (e.g proj information). This option can be set multiple times.

    You can pass the extension option multiple times: `-e extension1 -e extension2`.

- **projection extension** (--with-proj / --without-proj)

    By default the `projection` extension and properties will be added to the item:
    ```
    {
        "proj:epsg": 3857,
        "proj:geometry": {"type": "Polygon", "coordinates": [...]},
        "proj:bbox": [..],
        "proj:shape": [8192, 8192],
        "proj:transform": [...],
        "datetime": "2021-03-19T02:27:33.266356Z"
    }
    ```

    You can pass `--without-proj` to disable it.

- **collection** (-c, --collection)

    Add a `collection` attribute to the item.

- **collection link** (--collection-url)

    When adding a collection to the Item, the specification state that a Link must also be set. By default the `href` will be set with the collection id. You can specify a custom URL using this option.

- **properties** (-p, --property)

    You can add multiple properties to the item using `-p {KEY}={VALUE}` notation. This option can be set multiple times.

- **id** (--id)

    STAC Item id to set. Default to the source basename.

- **asset name** (-n, --asset-name)

    Name to use in the assets section. Default to `asset`.

    ```
    {
        "asset": {
        "href": "raster.tif"
        }
    }
    ```

- **asset href** (--asset-href)

    Overwrite the HREF in the `asset` object. Default to the source path.

- **media type** (--asset-mediatype)

    Set the asset `mediatype`.

    If set to `auto`, `rio-stac` will try to find the mediatype.


### Example

```
$ rio stac raster.tif | jq
{
  "type": "Feature",
  "stac_version": "1.0.0-beta.2",
  "id": "raster.tif",
  "properties": {
    "proj:epsg": 3857,
    "proj:geometry": {"type": "Polygon", "coordinates": [...]},
    "proj:bbox": [..],
    "proj:shape": [8192, 8192],
    "proj:transform": [...],
    "datetime": "2021-03-19T02:27:33.266356Z"
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [...]
  },
  "links": [],
  "assets": {
    "asset": {
      "href": "raster.tif"
    }
  },
  "bbox": [...],
  "stac_extensions": ["proj"]
}
```

```
$ rio stac S-2_20200422_COG.tif \
    -d 2020-04-22 \
    -e proj -e comments \
    -c myprivatecollection \
    -p comments:name=myfile \
    --id COG \
    -n mosaic \
    --asset-href https://somewhere.overtherainbow.io/S-2_20200422_COG.tif \
    --asset-mediatype COG | jq

{
  "type": "Feature",
  "stac_version": "1.0.0-beta.2",
  "id": "COG",
  "properties": {
    "comments:name": "myfile",
    "proj:epsg": 32632,
    "proj:geometry": {
      "type": "Polygon",
      "coordinates": [...]
    },
    "proj:bbox": [...],
    "proj:shape": [28870, 33145],
    "proj:transform": [...],
    "datetime": "2020-04-22T00:00:00Z"
  },
  "geometry": {"type": "Polygon", "coordinates": [...]},
  "links": [],
  "assets": {
    "mosaic": {
      "href": "https://somewhere.overtherainbow.io/S-2_20200422_COG.tif",
      "type": "image/tiff; application=geotiff; profile=cloud-optimized"
    }
  },
  "bbox": [...],
  "stac_extensions": [
    "proj",
    "comments"
  ],
  "collection": "myprivatecollection"
}
```


# API

see: [api](api/rio_stac/stac.md)
