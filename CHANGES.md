
## 0.2.0 (TBD)

* fix validation issue with Collection and extension for STAC 1.0.0
* add collection_url option to customize the collection link

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
