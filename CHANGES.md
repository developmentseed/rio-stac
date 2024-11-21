
## 0.10.1 (2024-11-21)

* catch date parsing issue and raise warning

## 0.10.0 (2024-10-29)

* handle `TIFFTAG_DATETIME` metadata for STAC datetime
* only set `proj:epsg` if present else use `proj:wkt2` or `proj:projjson`
* add `geographic_crs` parameter to `create_stac_item` function to enable non-earth raster dataset

## 0.9.0 (2023-12-08)

* add `wkt2` representation of the dataset CRS if available (author @emileten, https://github.com/developmentseed/rio-stac/pull/55)

## 0.8.1 (2023-09-27)

* update `tests` requirements

## 0.8.0 (2023-05-26)

* update `proj` extension to `v1.1.0`
* update `eo` extension to `v1.1.0`

## 0.7.1 (2023-05-03)

* fix bad precision default (author @hrodmn, https://github.com/developmentseed/rio-stac/pull/50)

## 0.7.0 (2023-04-05)

* add `geom_densify_pts` option allow adding points on Polygon edges to account for non-linear transformation
* add `geom_precision` option to control the decimal precision of the output geometry
* rename `rio_stac.stac.get_metadata` to `rio_stac.stac.get_dataset_geom`

## 0.6.1 (2022-10-26)

* add python 3.11 support

## 0.6.0 (2022-10-20)

* remove python 3.7 support (https://github.com/developmentseed/rio-stac/pull/42)
* add `projjson` representation of the dataset CRS if available (author @clausmichele, https://github.com/developmentseed/rio-stac/pull/41)

## 0.5.0 (2022-09-05)

* add python 3.10 support (https://github.com/developmentseed/rio-stac/pull/37)
* get dataset datetime from GDAL Raster Data Model **breaking**
* add `eo` extension support (`eo:cloud_cover`, `eo:bands`) **breaking**
* use `auto` by default for `asset_media_type` **breaking**

## 0.4.2 (2022-06-09)

* fix bad `nan/inf/-inf` nodata test

## 0.4.1 (2022-04-26)

* handle `nan/inf` values to avoid `numpy.histogram` issue (https://github.com/developmentseed/rio-stac/pull/32)

## 0.4.0 (2022-03-29)

* Switch to `pyproject.toml` to simplify setup.

**bug fixes**

* Split geometry to MultiPolygon for dataset crossing the dataline separation (https://github.com/developmentseed/rio-stac/pull/30)
* Use correct coordinates order for Polygon (ref https://github.com/developmentseed/geojson-pydantic/pull/49)

## 0.3.2 (2021-10-29)

**bug fixes**
* Use the raster_max_size and asset_roles arguments in create_stac_item (author @alexgleith, https://github.com/developmentseed/rio-stac/pull/23)
* Fix json serialisation by converting numpy float32 to float (author @alexgleith, https://github.com/developmentseed/rio-stac/pull/24)

## 0.3.1 (2021-10-07)

* update `pystac` requirement to allow up to `<2.0` (author @alexgleith, https://github.com/developmentseed/rio-stac/pull/20)

## 0.3.0 (2021-09-10)

* Move `raster:bands` information in assets (not in properties).
* update pystac version
* fix typo for `stddev` raster information
* drop support of python 3.6 (pystac 1.0.0 dropped support of python 3.6)

## 0.2.1 (2021-08-24)

* use WarpedVRT for data with internal GCPS

## 0.2.0 (2021-07-06)

* fix validation issue with Collection and extension for STAC 1.0.0
* add collection_url option to customize the collection link
* add `raster` extension option (https://github.com/developmentseed/rio-stac/pull/12)
* set `proj:epsg` value to `None` when no `CRS` is found in the dataset.

**breaking changes**

* update pystac version to `>=1.0.0rc1`
* use full URL for extension
* add Collection Link when adding a collection
* add with_proj (--with-proj/--without-proj in the CLI) in `create_stac_item` to add the extension and proj properties in the stac items (will do the same for the raster extension)

## 0.1.1 (2021-03-19)

* fix CLI asset-href default

## 0.1.0 (2021-03-19)

Initial release.

* Design API
* add CLI
* add tests
* write docs
