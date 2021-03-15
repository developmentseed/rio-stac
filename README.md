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
rio stac --help
Usage: rio stac [OPTIONS] INPUT

  Rasterio stac cli.

Options:
  -d, --datetime               TEXT        The searchable date and time of the assets, in UTC.
  --with-proj / --without-proj             Add PROJ extension and metadata.
  -e, --extention              TEXT        STAC extension the Item implements.
  -c, --collection             TEXT        The Collection ID that this item belongs to.
  -p, --property               NAME=VALUE  Additional property to add.
  --id                         TEXT        Item id.
  -n, --asset-name             TEXT        Asset name.
  -o, --output                 PATH        Output file name
  --help                                   Show this message and exit.
```

## Example

```
$ rio stac S-2_20200422_COG.tif | jq
{
  "type": "Feature",
  "stac_version": "1.0.0-beta.2",
  "id": "S-2_20200422_COG.tif",
  "properties": {
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
    "datetime": "2021-03-15T22:39:56.257899Z"
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
  "links": [],
  "assets": {
    "cog": {
      "href": "S-2_20200422_COG.tif",
      "type": "image/tiff; application=geotiff; profile=cloud-optimized"
    }
  },
  "bbox": [
    6.608576517072109,
    51.270642883468916,
    11.64938680867944,
    53.89267160832536
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
