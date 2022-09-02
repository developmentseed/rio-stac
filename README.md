# rio-stac

<p align="center">
  <img src="https://user-images.githubusercontent.com/10407788/111794250-696da080-889c-11eb-9043-5bdc3aadb8bf.png" alt="rio-stac"></a>
</p>
<p align="center">
  <em>Create STAC Items from raster datasets.</em>
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

`rio-stac` is a simple [rasterio](https://github.com/mapbox/rasterio) plugin for creating valid STAC items from a raster dataset. The library is built on top of [pystac](https://github.com/stac-utils/pystac) to make sure we follow the STAC specification.

## Installation

```bash
$ pip install pip -U

# From Pypi
$ pip install rio-stac

# Or from source
$ pip install git+http://github.com/developmentseed/rio-stac
```

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

See https://developmentseed.org/rio-stac/intro/ for more.

## Contribution & Development

See [CONTRIBUTING.md](https://github.com/developmentseed/rio-stac/blob/master/CONTRIBUTING.md)

## Authors

See [contributors](https://github.com/developmentseed/rio-stac/graphs/contributors)

## Changes

See [CHANGES.md](https://github.com/developmentseed/rio-stac/blob/master/CHANGES.md).

## License

See [LICENSE](https://github.com/developmentseed/rio-stac/blob/master/LICENSE)
