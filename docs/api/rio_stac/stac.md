# Module rio_stac.stac

Create STAC Item from a rasterio dataset.

None

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
    properties: Union[Dict, NoneType] = None,
    id: Union[str, NoneType] = None,
    assets: Union[Dict[str, pystac.item.Asset], NoneType] = None,
    asset_name: str = 'asset',
    asset_roles: Union[List[str], NoneType] = None,
    asset_media_type: Union[str, pystac.media_type.MediaType, NoneType] = None,
    asset_href: Union[str, NoneType] = None
) -> pystac.item.Item
```

    
Create a Stac Item.

**Parameters:**

| Name | Type | Description | Default |
|---|---|---|---|
| source | str or rasterio openned dataset | input path or rasterio dataset. | None |
| input_datetime | datetime.datetime | datetime associated with the item. | None |
| extensions | list of str | input list of extensions to use in the item. | None |
| collection | str | collection's name the item belong to. | None |
| properties | dict | additional properties to add in the item. | None |
| id | str | id to assign to the item (default to the source basename). | None |
| assets | dict | Assets to set in the item. If set we won't create one from the source. | None |
| asset_name | str | asset name in the Assets object. | None |
| asset_roles | list of str | list of asset's role. | None |
| asset_media_type | str or pystac.MediaType | asset's media type. | None |
| asset_href | str | asset's URI (default to input path). | None |

**Returns:**

| Type | Description |
|---|---|
| pystac.Item | valid STAC Item. |

    
### get_media_type

```python3
def get_media_type(
    src_dst: Union[rasterio.io.DatasetReader, rasterio.io.DatasetWriter, rasterio.vrt.WarpedVRT, rasterio.io.MemoryFile]
) -> Union[pystac.media_type.MediaType, NoneType]
```

    
Define or validate MediaType.

    
### get_metadata

```python3
def get_metadata(
    src_dst: Union[rasterio.io.DatasetReader, rasterio.io.DatasetWriter, rasterio.vrt.WarpedVRT, rasterio.io.MemoryFile]
) -> Dict
```

    
Get Raster Metadata.