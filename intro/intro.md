
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
  --with-proj / --without-proj      Add the 'projection' extension and properties (default to True).
  --with-raster / --without-raster  Add the 'raster' extension and properties (default to True).
  --with-eo / --without-eo          Add the 'eo' extension and properties (default to True).
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
        "proj:epsg": 3857,
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

- **eo extension** (--with-eo / --without-eo)

    By default the `eo` extension and properties will be added to the item. The `eo:cloud_cover` value will be fetched from [GDAL Raster data model](https://gdal.org/user/raster_data_model) metadata.

    link: https://github.com/stac-extensions/eo/

    Cloud Cover property
    ```json
    "eo:cloud_cover": 2
    ```

    Asset's bands
    ```json
    "eo:bands": [
      {
        "name": "b1",
        "description": "red"
      },
      {
        "name": "b2"
        "description": "green"
      },
      {
        "name": "b3"
        "description": "blue"
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

    You can add multiple properties to the item using `-p {KEY}={VALUE}` notation. This option can be set multiple times.

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

### Example

```json
// rio stac tests/fixtures/dataset_cog.tif | jq
{
  "type": "Feature",
  "stac_version": "1.0.0",
  "id": "dataset_cog.tif",
  "properties": {
    "proj:epsg": 32621,
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
    "proj:projjson": {
      "$schema": "https://proj.org/schemas/v0.4/projjson.schema.json",
      "type": "ProjectedCRS",
      "name": "WGS 84 / UTM zone 21N",
      "base_crs": {
        "name": "WGS 84",
        "datum": {
          "type": "GeodeticReferenceFrame",
          "name": "World Geodetic System 1984",
          "ellipsoid": {
            "name": "WGS 84",
            "semi_major_axis": 6378137,
            "inverse_flattening": 298.257223563
          }
        },
        "coordinate_system": {
          "subtype": "ellipsoidal",
          "axis": [
            {
              "name": "Geodetic latitude",
              "abbreviation": "Lat",
              "direction": "north",
              "unit": "degree"
            },
            {
              "name": "Geodetic longitude",
              "abbreviation": "Lon",
              "direction": "east",
              "unit": "degree"
            }
          ]
        },
        "id": {
          "authority": "EPSG",
          "code": 4326
        }
      },
      "conversion": {
        "name": "UTM zone 21N",
        "method": {
          "name": "Transverse Mercator",
          "id": {
            "authority": "EPSG",
            "code": 9807
          }
        },
        "parameters": [
          {
            "name": "Latitude of natural origin",
            "value": 0,
            "unit": "degree",
            "id": {
              "authority": "EPSG",
              "code": 8801
            }
          },
          {
            "name": "Longitude of natural origin",
            "value": -57,
            "unit": "degree",
            "id": {
              "authority": "EPSG",
              "code": 8802
            }
          },
          {
            "name": "Scale factor at natural origin",
            "value": 0.9996,
            "unit": "unity",
            "id": {
              "authority": "EPSG",
              "code": 8805
            }
          },
          {
            "name": "False easting",
            "value": 500000,
            "unit": "metre",
            "id": {
              "authority": "EPSG",
              "code": 8806
            }
          },
          {
            "name": "False northing",
            "value": 0,
            "unit": "metre",
            "id": {
              "authority": "EPSG",
              "code": 8807
            }
          }
        ]
      },
      "coordinate_system": {
        "subtype": "Cartesian",
        "axis": [
          {
            "name": "Easting",
            "abbreviation": "",
            "direction": "east",
            "unit": "metre"
          },
          {
            "name": "Northing",
            "abbreviation": "",
            "direction": "north",
            "unit": "metre"
          }
        ]
      },
      "id": {
        "authority": "EPSG",
        "code": 32621
      }
    },
    "proj:wkt2": "PROJCS[\"WGS 84 / UTM zone 21N\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",-57],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",EAST],AXIS[\"Northing\",NORTH],AUTHORITY[\"EPSG\",\"32621\"]]",
    "datetime": "2023-12-08T09:30:38.153261Z"
  },
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
  "links": [],
  "assets": {
    "asset": {
      "href": "/Users/vincentsarago/Dev/DevSeed/rio-stac/tests/fixtures/dataset_cog.tif",
      "raster:bands": [
        {
          "data_type": "uint16",
          "scale": 1.0,
          "offset": 0.0,
          "sampling": "point",
          "statistics": {
            "mean": 2107.524612053134,
            "minimum": 1,
            "maximum": 7872,
            "stddev": 2271.0065537857326,
            "valid_percent": 0.00009564764936336924
          },
          "histogram": {
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
      "eo:bands": [
        {
          "name": "b1",
          "description": "gray"
        }
      ],
      "roles": []
    }
  },
  "bbox": [
    -61.28762442711404,
    72.22979795551834,
    -52.301598718454485,
    74.62204314252978
  ],
  "stac_extensions": [
    "https://stac-extensions.github.io/projection/v1.1.0/schema.json",
    "https://stac-extensions.github.io/raster/v1.1.0/schema.json",
    "https://stac-extensions.github.io/eo/v1.1.0/schema.json"
  ]
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
// {
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
            342765.0,
            5682885.0
          ],
          [
            674215.0,
            5682885.0
          ],
          [
            674215.0,
            5971585.0
          ],
          [
            342765.0,
            5971585.0
          ],
          [
            342765.0,
            5682885.0
          ]
        ]
      ]
    },
    "proj:bbox": [
      342765.0,
      5682885.0,
      674215.0,
      5971585.0
    ],
    "proj:shape": [
      28870,
      33145
    ],
    "proj:transform": [
      10.0,
      0.0,
      342765.0,
      0.0,
      -10.0,
      5971585.0,
      0.0,
      0.0,
      1.0
    ],
    "proj:projjson": {
      "$schema": "https://proj.org/schemas/v0.4/projjson.schema.json",
      "type": "ProjectedCRS",
      "name": "WGS 84 / UTM zone 32N",
      "base_crs": {
        "name": "WGS 84",
        "datum": {
          "type": "GeodeticReferenceFrame",
          "name": "World Geodetic System 1984",
          "ellipsoid": {
            "name": "WGS 84",
            "semi_major_axis": 6378137,
            "inverse_flattening": 298.257223563
          }
        },
        "coordinate_system": {
          "subtype": "ellipsoidal",
          "axis": [
            {
              "name": "Geodetic latitude",
              "abbreviation": "Lat",
              "direction": "north",
              "unit": "degree"
            },
            {
              "name": "Geodetic longitude",
              "abbreviation": "Lon",
              "direction": "east",
              "unit": "degree"
            }
          ]
        },
        "id": {
          "authority": "EPSG",
          "code": 4326
        }
      },
      "conversion": {
        "name": "UTM zone 32N",
        "method": {
          "name": "Transverse Mercator",
          "id": {
            "authority": "EPSG",
            "code": 9807
          }
        },
        "parameters": [
          {
            "name": "Latitude of natural origin",
            "value": 0,
            "unit": "degree",
            "id": {
              "authority": "EPSG",
              "code": 8801
            }
          },
          {
            "name": "Longitude of natural origin",
            "value": 9,
            "unit": "degree",
            "id": {
              "authority": "EPSG",
              "code": 8802
            }
          },
          {
            "name": "Scale factor at natural origin",
            "value": 0.9996,
            "unit": "unity",
            "id": {
              "authority": "EPSG",
              "code": 8805
            }
          },
          {
            "name": "False easting",
            "value": 500000,
            "unit": "metre",
            "id": {
              "authority": "EPSG",
              "code": 8806
            }
          },
          {
            "name": "False northing",
            "value": 0,
            "unit": "metre",
            "id": {
              "authority": "EPSG",
              "code": 8807
            }
          }
        ]
      },
      "coordinate_system": {
        "subtype": "Cartesian",
        "axis": [
          {
            "name": "Easting",
            "abbreviation": "",
            "direction": "east",
            "unit": "metre"
          },
          {
            "name": "Northing",
            "abbreviation": "",
            "direction": "north",
            "unit": "metre"
          }
        ]
      },
      "id": {
        "authority": "EPSG",
        "code": 32632
      }
    },
    "proj:wkt2": "PROJCS[\"WGS 84 / UTM zone 32N\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",9],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",EAST],AXIS[\"Northing\",NORTH],AUTHORITY[\"EPSG\",\"32632\"]]",
    "datetime": "2020-04-22T00:00:00Z"
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          6.745709371926977,
          51.27558086786243
        ],
        [
          11.497498156319669,
          51.270642883468916
        ],
        [
          11.64938680867944,
          53.86346627759
        ],
        [
          6.608576517072109,
          53.868886713141336
        ],
        [
          6.745709371926977,
          51.27558086786243
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
          "data_type": "uint8",
          "scale": 1.0,
          "offset": 0.0,
          "sampling": "area",
          "statistics": {
            "mean": 70.14680057905686,
            "minimum": 0,
            "maximum": 255,
            "stddev": 36.47197403839734,
            "valid_percent": 49.83785997057175
          },
          "histogram": {
            "count": 11,
            "min": 0.0,
            "max": 255.0,
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
          "data_type": "uint8",
          "scale": 1.0,
          "offset": 0.0,
          "sampling": "area",
          "statistics": {
            "mean": 70.72913714816694,
            "minimum": 0,
            "maximum": 255,
            "stddev": 34.031434334640124,
            "valid_percent": 49.83785997057175
          },
          "histogram": {
            "count": 11,
            "min": 0.0,
            "max": 255.0,
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
          "data_type": "uint8",
          "scale": 1.0,
          "offset": 0.0,
          "sampling": "area",
          "statistics": {
            "mean": 47.96346845392258,
            "minimum": 0,
            "maximum": 255,
            "stddev": 32.447819767110225,
            "valid_percent": 49.83785997057175
          },
          "histogram": {
            "count": 11,
            "min": 0.0,
            "max": 255.0,
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
      "eo:bands": [
        {
          "name": "b1",
          "description": "red"
        },
        {
          "name": "b2",
          "description": "green"
        },
        {
          "name": "b3",
          "description": "blue"
        }
      ],
      "roles": []
    }
  },
  "bbox": [
    6.608576517072109,
    51.270642883468916,
    11.64938680867944,
    53.868886713141336
  ],
  "stac_extensions": [
    "https://stac-extensions.github.io/projection/v1.1.0/schema.json",
    "https://stac-extensions.github.io/raster/v1.1.0/schema.json",
    "https://stac-extensions.github.io/eo/v1.1.0/schema.json"
  ],
  "collection": "myprivatecollection"
}
```


# API

see: [api](api/rio_stac/stac.md)
