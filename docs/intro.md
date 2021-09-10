
`rio-stac` can be used either from the command line as a rasterio plugin (`rio stac`) or from your own script.

For more information about the `Item` specification, please see https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md

# CLI

```
$ rio stac --help

Usage: rio stac [OPTIONS] INPUT

  Rasterio STAC plugin: Create a STAC Item for raster dataset.

Options:
  -d, --datetime TEXT               The date and time of the assets, in UTC (e.g 2020-01-01, 2020-01-01T01:01:01).
-e, --extension TEXT                STAC extensions the Item implements (default is set to ["proj"]). Multiple allowed (e.g. `-e extensionUrl1 -e extensionUrl2`).
  -c, --collection TEXT             The Collection ID that this item belongs to.
  --collection-url TEXT             Link to the STAC Collection.
  -p, --property NAME=VALUE         Additional property to add (e.g `-p myprops=1`). Multiple allowed.
  --id TEXT                         Item id.
  -n, --asset-name TEXT             Asset name.
  --asset-href TEXT                 Overwrite asset href.
  --asset-mediatype [COG|GEOJSON|GEOPACKAGE|GEOTIFF|HDF|HDF5|JPEG|JPEG2000|JSON|PNG|TEXT|TIFF|XML|auto] Asset media-type.
  --with-proj / --without-proj      Add the projection extension and properties (default to True).
  --with-raster / --without-raster  Add the raster extension and properties (default to True).
  -o, --output PATH                 Output file name
  --help                            Show this message and exit.
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

    By default the `projection` extension and properties will be added to the item.

    link: https://github.com/stac-extensions/projection/

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

- **raster extension** (--with-raster / --without-raster)

    By default the `raster` extension and properties will be added to the item.

    link: https://github.com/stac-extensions/raster

    ```
    "raster:bands": [
      {
        "sampling": "point",
        "data_type": "uint16",
        "scale": 1,
        "offset": 0,
        "statistics": {
          "mean": 2107.524612053134,
          "minimum": 1,
          "maximum": 7872,
          "stdev": 2271.0065537857326,
          "valid_percent": 9.564764936336924e-05
        },
        "histogram": {
          "count": 11,
          "min": 1,
          "max": 7872,
          "buckets": [503460, 0, 0, 161792, 283094, 0, 0, 0, 87727, 9431]
        }
      }
    ]
    ```

    You can pass `--without-raster` to disable it.

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

```json
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
      "href": "raster.tif",
      "raster:bands": [
        {
          "sampling": "point",
          "data_type": "uint16",
          "scale": 1,
          "offset": 0,
          "statistics": {
            "mean": 2107.524612053134,
            "minimum": 1,
            "maximum": 7872,
            "stdev": 2271.0065537857326,
            "valid_percent": 9.564764936336924e-05
          },
          "histogram": {
            "count": 11,
            "min": 1,
            "max": 7872,
            "buckets": [503460, 0, 0, 161792, 283094, 0, 0, 0, 87727, 9431]
          }
        }
      ],
    }
  },
  "bbox": [...],
  "stac_extensions": [
    "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
    "https://stac-extensions.github.io/raster/v1.0.0/schema.json"
  ]
}
```

```json
$ rio stac S-2_20200422_COG.tif \
    -d 2020-04-22 \
    -c myprivatecollection \
    -p comments:name=myfile \
    --id COG \
    -n mosaic \
    --asset-href https://somewhere.overtherainbow.io/S-2_20200422_COG.tif \
    --asset-mediatype COG | jq

{
  "type": "Feature",
  "stac_version": "1.0.0",
  "id": "COG",
  "properties": {
    "comments:name": "myfile",
    "proj:epsg": 32632,
    "proj:geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            342765,
            5971585
          ],
          [
            342765,
            5682885
          ],
          [
            674215,
            5682885
          ],
          [
            674215,
            5971585
          ],
          [
            342765,
            5971585
          ]
        ]
      ]
    },
    "proj:bbox": [
      342765,
      5682885,
      674215,
      5971585
    ],
    "proj:shape": [
      28870,
      33145
    ],
    "proj:transform": [
      10,
      0,
      342765,
      0,
      -10,
      5971585,
      0,
      0,
      1
    ],
    "datetime": "2020-04-22T00:00:00Z"
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          6.608576517072109,
          53.89267160832536
        ],
        [
          6.608576517072109,
          51.270642883468916
        ],
        [
          11.64938680867944,
          51.270642883468916
        ],
        [
          11.64938680867944,
          53.89267160832536
        ],
        [
          6.608576517072109,
          53.89267160832536
        ]
      ]
    ]
  },
  "links": [
    {
      "rel": "collection",
      "href": "myprivatecollection",
      "type": "application/json"
    }
  ],
  "assets": {
    "mosaic": {
      "href": "https://somewhere.overtherainbow.io/S-2_20200422_COG.tif",
      "type": "image/tiff; application=geotiff; profile=cloud-optimized",
      "raster:bands": [
        {
          "sampling": "area",
          "data_type": "uint8",
          "scale": 1,
          "offset": 0,
          "statistics": {
            "mean": 70.14680057905686,
            "minimum": 0,
            "maximum": 255,
            "stdev": 36.47197403839734,
            "valid_percent": 49.83785997057175
          },
          "histogram": {
            "count": 11,
            "min": 0,
            "max": 255,
            "buckets": [
              21135,
              129816,
              152194,
              76363,
              39423,
              20046,
              10272,
              3285,
              1115,
              1574
            ]
          }
        },
        {
          "sampling": "area",
          "data_type": "uint8",
          "scale": 1,
          "offset": 0,
          "statistics": {
            "mean": 70.72913714816694,
            "minimum": 0,
            "maximum": 255,
            "stdev": 34.031434334640124,
            "valid_percent": 49.83785997057175
          },
          "histogram": {
            "count": 11,
            "min": 0,
            "max": 255,
            "buckets": [
              14829,
              116732,
              171933,
              81023,
              38736,
              18977,
              8362,
              2259,
              918,
              1454
            ]
          }
        },
        {
          "sampling": "area",
          "data_type": "uint8",
          "scale": 1,
          "offset": 0,
          "statistics": {
            "mean": 47.96346845392258,
            "minimum": 0,
            "maximum": 255,
            "stdev": 32.447819767110225,
            "valid_percent": 49.83785997057175
          },
          "histogram": {
            "count": 11,
            "min": 0,
            "max": 255,
            "buckets": [
              110478,
              177673,
              93767,
              41101,
              20804,
              7117,
              1939,
              856,
              829,
              659
            ]
          }
        }
      ],
    }
  },
  "bbox": [
    6.608576517072109,
    51.270642883468916,
    11.64938680867944,
    53.89267160832536
  ],
  "stac_extensions": [
    "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
    "https://stac-extensions.github.io/raster/v1.0.0/schema.json"
  ],
  "collection": "myprivatecollection"
}
```


# API

see: [api](api/rio_stac/stac.md)
