
## Next (TBD)

* add python 3.10 support (https://github.com/developmentseed/rio-stac/pull/37)

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
