# rio-stac


<p align="center">
  <img src="" style="max-width: 800px;" alt="rio-tiler"></a>
</p>
<p align="center">
  <em>Create a STAC Items from a raster dataset.</em>
</p>
<p align="center">
  <a href="https://github.com/developmentseed/rio-stac/actions?query=workflow%3ACI" target="_blank">
      <img src="https://github.com/developmentseed/rio-stac/workflows/CI/badge.svg" alt="Test">
  </a>
  <a href="https://codecov.io/gh/developmentseed/rio-stac" target="_blank">
      <img src="https://codecov.io/gh/developmentseed/rio-stac/branch/master/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/rio-stac" target="_blank">
      <img src="https://img.shields.io/pypi/v/rio-stac?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypistats.org/packages/rio-stac" target="_blank">
      <img src="https://img.shields.io/pypi/dm/rio-stac.svg" alt="Downloads">
  </a>
  <a href="https://github.com/developmentseed/rio-stac/blob/master/LICENSE" target="_blank">
      <img src="https://img.shields.io/github/license/developmentseed/rio-stac.svg" alt="Downloads">
  </a>
</p>

---

**Documentation**: <a href="https://developmentseed.github.io/rio-stac/" target="_blank">https://developmentseed.github.io/rio-stac/</a>

**Source Code**: <a href="https://github.com/developmentseed/rio-stac" target="_blank">https://github.com/developmentseed/rio-stac</a>

---

## Install

```bash
$ pip install pip -U
$ pip install rio-stac

# Or using source

$ pip install git+http://github.com/developmentseed/rio-stac
```

## CLI

```
$ rio stac --help

Usage: rio stac [OPTIONS] INPUT

  Rasterio stac cli.

Options:
  -d, --datetime TEXT             The date and time of the assets, in UTC (e.g 2020-01-01, 2020-01-01T01:01:01).
  -e, --extension TEXT            STAC extension the Item implements.
  -c, --collection TEXT           The Collection ID that this item belongs to.
  -p, --property NAME=VALUE       Additional property to add.
  --id TEXT                       Item id.
  -n, --asset-name TEXT           Asset name.
  --asset-href TEXT               Overwrite asset href.
  --asset-mediatype [COG|GEOJSON|GEOPACKAGE|GEOTIFF|HDF|HDF5|JPEG|JPEG2000|JSON|PNG|TEXT|TIFF|XML|auto] Asset media-type.
  -o, --output PATH               Output file name
  --help                          Show this message and exit.
```

## Example

```
$ rio stac S-2_20200422_COG.tif | jq
{
  "type": "Feature",
  "stac_version": "1.0.0-beta.2",
  "id": "eu_webAligned_256pxWEBP.tif",
  "properties": {
    "proj:epsg": 3857,
    "proj:geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [
            -10018754.17139461,
            20037508.3427892
          ],
          [
            -10018754.17139461,
            -2.9802322387695312e-08
          ],
          [
            10018754.171394618,
            -2.9802322387695312e-08
          ],
          [
            10018754.171394618,
            20037508.3427892
          ],
          [
            -10018754.17139461,
            20037508.3427892
          ]
        ]
      ]
    },
    "proj:bbox": [
      -10018754.17139461,
      -2.9802322387695312e-08,
      10018754.171394618,
      20037508.3427892
    ],
    "proj:shape": [
      8192,
      8192
    ],
    "proj:transform": [
      2445.9849051256383,
      0,
      -10018754.17139461,
      0,
      -2445.9849051256383,
      20037508.3427892,
      0,
      0,
      1
    ],
    "datetime": "2021-03-19T02:27:33.266356Z"
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          -89.9999999999999,
          85.05112877980656
        ],
        [
          -89.9999999999999,
          -2.671665932429354e-13
        ],
        [
          89.99999999999996,
          -2.671665932429354e-13
        ],
        [
          89.99999999999996,
          85.05112877980656
        ],
        [
          -89.9999999999999,
          85.05112877980656
        ]
      ]
    ]
  },
  "links": [],
  "assets": {
    "asset": {
      "href": "asset"
    }
  },
  "bbox": [
    -89.9999999999999,
    -2.671665932429354e-13,
    89.99999999999996,
    85.05112877980656
  ],
  "stac_extensions": [
    "proj"
  ]
}
```



## Contribution & Development

See [CONTRIBUTING.md](https://github.com/developmentseed/rio-stac/blob/master/CONTRIBUTING.md)

## Authors

See [AUTHORS.txt](https://github.com/developmentseed/rio-stac/blob/master/AUTHORS.txt) for a listing of individual contributors.

## Changes

See [CHANGES.md](https://github.com/developmentseed/rio-stac/blob/master/CHANGES.md).

## License

See [LICENSE](https://github.com/developmentseed/rio-stac/blob/master/LICENSE)
