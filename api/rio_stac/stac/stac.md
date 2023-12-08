# Module rio_stac.stac

Create STAC Item from a rasterio dataset.

## Variables

```python3
EO_EXT_VERSION
```

```python3
EPSG_4326
```

```python3
PROJECTION_EXT_VERSION
```

```python3
RASTER_EXT_VERSION
```

## Functions

    
### bbox_to_geom

```python3
def bbox_to_geom(
    bbox: Tuple[float, float, float, float]
) -> Dict
```

Return a geojson geometry from a bbox.

    
### create_stac_item

```python3
def create_stac_item(
    source: Union[str, rasterio.io.DatasetReader, rasterio.io.DatasetWriter, rasterio.vrt.WarpedVRT, rasterio.io.MemoryFile],
    input_datetime: Union[datetime.datetime, NoneType] = None,
    extensions: Union[List[str], NoneType] = None,
    collection: Union[str, NoneType] = None,
    collection_url: Union[str, NoneType] = None,
    properties: Union[Dict, NoneType] = None,
    id: Union[str, NoneType] = None,
    assets: Union[Dict[str, pystac.asset.Asset], NoneType] = None,
    asset_name: str = 'asset',
    asset_roles: Union[List[str], NoneType] = None,
    asset_media_type: Union[str, pystac.media_type.MediaType, NoneType] = 'auto',
    asset_href: Union[str, NoneType] = None,
    with_proj: bool = False,
    with_raster: bool = False,
    with_eo: bool = False,
    raster_max_size: int = 1024,
    geom_densify_pts: int = 0,
    geom_precision: int = -1
) -> pystac.item.Item
```

Create a Stac Item.

**Parameters:**

| Name | Type | Description | Default |
|---|---|---|---|
| source | str or opened rasterio dataset | input path or rasterio dataset. | None |
| input_datetime | datetime.datetime | datetime associated with the item. | None |
| extensions | list of str | input list of extensions to use in the item. | None |
| collection | str | name of collection the item belongs to. | None |
| collection_url | str | Link to the STAC Collection. | None |
| properties | dict | additional properties to add in the item. | None |
| id | str | id to assign to the item (default to the source basename). | None |
| assets | dict | Assets to set in the item. If set we won't create one from the source. | None |
| asset_name | str | asset name in the Assets object. | None |
| asset_roles | list of str | list of str | list of asset's roles. | None |
| asset_media_type | str or pystac.MediaType | asset's media type. | None |
| asset_href | str | asset's URI (default to input path). | None |
| with_proj | bool | Add the `projection` extension and properties (default to False). | None |
| with_raster | bool | Add the `raster` extension and properties (default to False). | None |
| with_eo | bool | Add the `eo` extension and properties (default to False). | None |
| raster_max_size | int | Limit array size from which to get the raster statistics. Defaults to 1024. | 1024 |
| geom_densify_pts | int | Number of points to add to each edge to account for nonlinear edges transformation (Note: GDAL uses 21). | None |
| geom_precision | int | If >= 0, geometry coordinates will be rounded to this number of decimal. | None |

**Returns:**

| Type | Description |
|---|---|
| pystac.Item | valid STAC Item. |

    
### get_dataset_geom

```python3
def get_dataset_geom(
    src_dst: Union[rasterio.io.DatasetReader, rasterio.io.DatasetWriter, rasterio.vrt.WarpedVRT, rasterio.io.MemoryFile],
    densify_pts: int = 0,
    precision: int = -1
) -> Dict
```

Get Raster Footprint.

    
### get_eobands_info

```python3
def get_eobands_info(
    src_dst: Union[rasterio.io.DatasetReader, rasterio.io.DatasetWriter, rasterio.vrt.WarpedVRT, rasterio.io.MemoryFile]
) -> List
```

Get eo:bands metadata.

see: https://github.com/stac-extensions/eo#item-properties-or-asset-fields

    
### get_media_type

```python3
def get_media_type(
    src_dst: Union[rasterio.io.DatasetReader, rasterio.io.DatasetWriter, rasterio.vrt.WarpedVRT, rasterio.io.MemoryFile]
) -> Union[pystac.media_type.MediaType, NoneType]
```

Find MediaType for a raster dataset.

    
### get_projection_info

```python3
def get_projection_info(
    src_dst: Union[rasterio.io.DatasetReader, rasterio.io.DatasetWriter, rasterio.vrt.WarpedVRT, rasterio.io.MemoryFile]
) -> Dict
```

Get projection metadata.

The STAC projection extension allows for three different ways to describe the coordinate reference system
associated with a raster :
- EPSG code
- WKT2
- PROJJSON

All are optional, and they can be provided altogether as well. Therefore, as long as one can be obtained from
the data, we add it to the returned dictionary.

see: https://github.com/stac-extensions/projection

    
### get_raster_info

```python3
def get_raster_info(
    src_dst: Union[rasterio.io.DatasetReader, rasterio.io.DatasetWriter, rasterio.vrt.WarpedVRT, rasterio.io.MemoryFile],
    max_size: int = 1024
) -> List[Dict]
```

Get raster metadata.

see: https://github.com/stac-extensions/raster#raster-band-object