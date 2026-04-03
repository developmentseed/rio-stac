
`rio-stac` is a simple [rasterio](https://github.com/mapbox/rasterio) plugin for creating valid STAC items from a raster dataset. The library is built on top of [pystac](https://github.com/stac-utils/pystac) to make sure we follow the STAC specification.

## Installation

We recommend using [uv](https://github.com/astral-sh/uv) for installation:

```bash
$ uv pip install rio-stac
```

Or with standard pip:

```bash
$ pip install pip -U
$ pip install rio-stac
```

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
  -p, --property NAME=VALUE         Additional property to add (e.g `-p myprops=1` or `-p _private={"foo":"bar"}`). Multiple allowed.
  -P, --private-property NAME=VALUE Additional property to add under '_private' (requires --with-private-data, e.g `-P hidden=true`). Multiple allowed.
  --id TEXT                         Item id.
  -n, --asset-name TEXT             Asset name.
  --asset-href TEXT                 Overwrite asset href.
  --asset-mediatype [COG|GEOJSON|GEOPACKAGE|GEOTIFF|HDF|HDF5|JPEG|JPEG2000|JSON|PNG|TEXT|TIFF|XML|auto] Asset media-type.
  --with-proj / --without-proj      Add the 'projection' extension and properties (default to True).
  --with-raster / --without-raster  Add the 'raster' extension and properties (default to True).
  --with-eo / --without-eo          Add the 'eo' extension and properties (default to True).
  --with-private-data / --without-private-data
                                    Add the '_private' entry to output item.
  --max-raster-size INTEGER         Limit array size from which to get the raster statistics (default to 1024).
  --densify-geom INTEGER            Densifies the number of points on each edges of the polygon geometry to account for non-linear transformation.
  --geom-precision INTEGER          Round geometry coordinates to this number of decimal. By default, coordinates will not be rounded
  -o, --output PATH                 Output file name
  --config NAME=VALUE               GDAL configuration options.
  --help                            Show this message and exit.
```

### How To

The CLI can be run as is, just by passing a `source` raster data. You can also use options to customize the output STAC item:

- **datetime** (-d, --datetime)

    By design, all STAC items must have a datetime in their properties. By default the CLI will set the time to the actual UTC Time or use `ACQUISITIONDATETIME` defined in dataset metadata (see [GDAL Raster data model](https://gdal.org/user/raster_data_model.html#imagery-domain-remote-sensing)). The CLI will accept any format supported by [`dateparser`](https://dateparser.readthedocs.io/en/latest/).

    You can also define `start_datetime` and `end_datetime` by using `--datetime {start}/{end}` notation.

    Note: `GDAL Raster data model` metadata are stored in an external file so you may want to set `GDAL_DISABLE_READDIR_ON_OPEN=FALSE` environment variable to allow GDAL to fetch the sidecar files.

- **extension** (-e, --extension)

    STAC Item can have [extensions](https://github.com/radiantearth/stac-spec/tree/master/extensions) which indicates that the item has additional properies (e.g proj information). This option can be set multiple times.

    You can pass the extension option multiple times: `-e extension1 -e extension2`.

- **projection extension** (--with-proj / --without-proj)

    By default the `projection` extension and properties will be added to the item.

    link: https://github.com/stac-extensions/projection/

    ```json
    {
        "proj:code": "EPSG:3857",
        "proj:geometry": {"type": "Polygon", "coordinates": [...]},
        "proj:bbox": [...],
        "proj:shape": [8192, 8192],
        "proj:transform": [...],
        "datetime": "2021-03-19T02:27:33.266356Z"
    }
    ```

    You can pass `--without-proj` to disable it.

- **raster extension** (--with-raster / --without-raster)

    By default the `raster` extension and properties will be added to the item.

    link: https://github.com/stac-extensions/raster

    ```json
    "bands": [
      {
        "raster:sampling": "point",
        "data_type": "uint16",
        "raster:scale": 1,
        "raster:offset": 0,
        "statistics": {
          "mean": 2107.524612053134,
          "minimum": 1,
          "maximum": 7872,
          "stddev": 2271.0065537857326,
          "valid_percent": 9.564764936336924e-05
        },
        "raster:histogram": {
          "count": 11,
          "min": 1,
          "max": 7872,
          "buckets": [503460, 0, 0, 161792, 283094, 0, 0, 0, 87727, 9431]
        }
      }
    ]
    ```

    You can pass `--without-raster` to disable it.

- **eo extension** (--with-eo / --without-eo)

    By default the `eo` extension and properties will be added to the item. The `eo:cloud_cover` value will be fetched from [GDAL Raster data model](https://gdal.org/en/stable/user/raster_data_model.html) metadata.

    link: https://github.com/stac-extensions/eo/

    Cloud Cover property
    ```json
    "eo:cloud_cover": 2
    ```

    Asset's bands
    ```json
    "bands": [
      {
        "name": "b1",
        "description": "red",
        "eo:common_name": "red"
      },
      {
        "name": "b2",
        "description": "green",
        "eo:common_name": "green"
      },
      {
        "name": "b3",
        "description": "blue",
        "eo:common_name": "blue"
      }
    ],
    ```

    You can pass `--without-eo` to disable it.

    Note: `GDAL Raster data model` metadata are stored in an external file so you may want to set `GDAL_DISABLE_READDIR_ON_OPEN=FALSE` environment variable to allow GDAL to fetch the sidecar files.

- **collection** (-c, --collection)

    Add a `collection` attribute to the item.

- **collection link** (--collection-url)

    When adding a collection to the Item, the specification state that a Link must also be set. By default the `href` will be set with the collection id. You can specify a custom URL using this option.

- **properties** (-p, --property)

    You can add multiple properties to the item using `-p {KEY}={VALUE}` notation. This option can be set multiple times. If the value is valid JSON (object or array), it will be parsed so you can pass nested data, e.g. `-p '_private={"foo":"bar"}'` when combining with `--with-private-data`. Lenient JSON (unquoted keys) such as `-p _private={hidden:true}` is also accepted.

- **private properties** (-P, --private-property)

    Shortcut for adding entries under `_private` without building a JSON object. Requires `--with-private-data` and can be set multiple times (e.g. `--with-private-data -P hidden=true -P note='abc'`).

- **id** (--id)

    STAC Item id to set. Default to the source basename.

- **asset name** (-n, --asset-name)

    Name to use in the assets section. Default to `asset`.

    ```json
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

- **geometry density** (--densify-geom)

    When creating the GeoJSON geometry from the input dataset we usually take the `bounding box` of the data and construct a simple Polygon which then get reprojected to EPSG:4326. Sadly the world is neither flat and square, so doing a transformation using bounding box can lead to non-ideal result. To get better results and account for nonlinear transformation you can add `points` on each edge of the polygon using `--densify-geom` option.

- **recursive** (-r, --recursive)

    Process input directory recursively. Instead of creating an Item for a single file, `rio-stac` will scan the directory and create one Item containing multiple assets.

    -   The directory name is used as the default Item ID (unless overridden by `--id`).
    -   Assets are created for found files.
    -   Smart asset detection rules apply:
        -   `.json`, `.xml` and `.safe` files are treated as `metadata`.
        -   3-band rasters without CRS or files with `ql` in name are treated as `thumbnail` (with cleaned properties).
        -   Other rasters are treated as `data`.
    -   General STAC best practices are applied:
        -   `proj:*` properties are moved from the Item level to the Asset level.
        -   Thumbnails are stripped of spatial/spectral metadata.
        -   Metadata assets are stripped of spatial metadata.

- **pattern** (--pattern)

    Glob pattern(s) to filter files when using `--recursive`. Can be specified multiple times.

    Example: `rio stac /path/to/dir --recursive --pattern "*.tif" --pattern "*.json"`

### Example

```json
// rio stac tests/fixtures/dataset_cog.tif | jq
{
  "type": "Feature",
  "stac_version": "1.1.0",
  "stac_extensions": [
    "https://stac-extensions.github.io/projection/v2.0.0/schema.json",
    "https://stac-extensions.github.io/raster/v2.0.0/schema.json",
    "https://stac-extensions.github.io/eo/v2.0.0/schema.json"
  ],
  "id": "dataset_cog.tif",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          -60.72634617297825,
          72.23689137791739
        ],
        [
          -52.91627525610924,
          72.22979795551834
        ],
        [
          -52.301598718454485,
          74.61378388950398
        ],
        [
          -61.28762442711404,
          74.62204314252978
        ],
        [
          -60.72634617297825,
          72.23689137791739
        ]
      ]
    ]
  },
  "bbox": [
    -61.28762442711404,
    72.22979795551834,
    -52.301598718454485,
    74.62204314252978
  ],
  "properties": {
    "proj:code": "EPSG:32621",
    "proj:geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            373185.0,
            8019284.949381611
          ],
          [
            639014.9492102272,
            8019284.949381611
          ],
          [
            639014.9492102272,
            8286015.0
          ],
          [
            373185.0,
            8286015.0
          ],
          [
            373185.0,
            8019284.949381611
          ]
        ]
      ]
    },
    "proj:bbox": [
      373185.0,
      8019284.949381611,
      639014.9492102272,
      8286015.0
    ],
    "proj:shape": [
      2667,
      2658
    ],
    "proj:transform": [
      100.01126757344893,
      0.0,
      373185.0,
      0.0,
      -100.01126757344893,
      8286015.0,
      0.0,
      0.0,
      1.0
    ],
    "datetime": "2025-11-28T13:12:58.968562Z"
  },
  "links": [],
  "assets": {
    "asset": {
      "href": "tests/fixtures/dataset_cog.tif",
      "type": "image/tiff; application=geotiff",
      "bands": [
        {
          "name": "b1",
          "description": "gray",
          "eo:common_name": "pan",
          "data_type": "uint16",
          "raster:scale": 1.0,
          "raster:offset": 0.0,
          "raster:sampling": "point",
          "statistics": {
            "mean": 2107.524612053134,
            "minimum": 1,
            "maximum": 7872,
            "stddev": 2271.006553785732,
            "valid_percent": 9.564764936336924e-05
          },
          "raster:histogram": {
            "count": 11,
            "min": 1.0,
            "max": 7872.0,
            "buckets": [
              503460,
              0,
              0,
              161792,
              283094,
              0,
              0,
              0,
              87727,
              9431
            ]
          }
        }
      ],
      "roles": []
    }
  }
}
```


```json
// rio stac S-2_20200422_COG.tif \
//   -d 2020-04-22 \
//   -c myprivatecollection \
//   -p comments:name=myfile \
//   --id COG \
//   -n mosaic \
//   --asset-href https://somewhere.overtherainbow.io/S-2_20200422_COG.tif \
//   --asset-mediatype COG | jq
{
  "type": "Feature",
  "stac_version": "1.1.0",
  "stac_extensions": [
    "https://stac-extensions.github.io/projection/v2.0.0/schema.json",
    "https://stac-extensions.github.io/raster/v2.0.0/schema.json",
    "https://stac-extensions.github.io/eo/v2.0.0/schema.json"
  ],
  "id": "COG",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          -60.72634617297825,
          72.23689137791739
        ],
        [
          -52.91627525610924,
          72.22979795551834
        ],
        [
          -52.301598718454485,
          74.61378388950398
        ],
        [
          -61.28762442711404,
          74.62204314252978
        ],
        [
          -60.72634617297825,
          72.23689137791739
        ]
      ]
    ]
  },
  "bbox": [
    -61.28762442711404,
    72.22979795551834,
    -52.301598718454485,
    74.62204314252978
  ],
  "properties": {
    "comments:name": "myfile",
    "proj:code": "EPSG:32621",
    "proj:geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            373185.0,
            8019284.949381611
          ],
          [
            639014.9492102272,
            8019284.949381611
          ],
          [
            639014.9492102272,
            8286015.0
          ],
          [
            373185.0,
            8286015.0
          ],
          [
            373185.0,
            8019284.949381611
          ]
        ]
      ]
    },
    "proj:bbox": [
      373185.0,
      8019284.949381611,
      639014.9492102272,
      8286015.0
    ],
    "proj:shape": [
      2667,
      2658
    ],
    "proj:transform": [
      100.01126757344893,
      0.0,
      373185.0,
      0.0,
      -100.01126757344893,
      8286015.0,
      0.0,
      0.0,
      1.0
    ],
    "datetime": "2020-04-22T00:00:00Z"
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
      "bands": [
        {
          "name": "b1",
          "description": "gray",
          "eo:common_name": "pan",
          "data_type": "uint16",
          "raster:scale": 1.0,
          "raster:offset": 0.0,
          "raster:sampling": "point",
          "statistics": {
            "mean": 2107.524612053134,
            "minimum": 1,
            "maximum": 7872,
            "stddev": 2271.006553785732,
            "valid_percent": 9.564764936336924e-05
          },
          "raster:histogram": {
            "count": 11,
            "min": 1.0,
            "max": 7872.0,
            "buckets": [
              503460,
              0,
              0,
              161792,
              283094,
              0,
              0,
              0,
              87727,
              9431
            ]
          }
        }
      ],
      "roles": []
    }
  },
  "collection": "myprivatecollection"
}
```



# API

see: [api](api/rio_stac/stac.md)
