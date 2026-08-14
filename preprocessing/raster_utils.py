"""
Raster-related utilities extracted from notebooks.
These are copies (not moves) of key functions so original notebooks remain unchanged.
"""
import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.warp import reproject, calculate_default_transform, Resampling as WarpResampling


def reproject_and_resample_band(src_path, band_idx, ref_crs, ref_transform, ref_width, ref_height):
    try:
        with rasterio.open(src_path) as src:
            dst_array = np.empty((ref_height, ref_width), dtype=np.float32)
            reproject(
                source=rasterio.band(src, band_idx),
                destination=dst_array,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=ref_transform,
                dst_crs=ref_crs,
                resampling=WarpResampling.nearest,
            )
            return dst_array
    except Exception as e:
        print(f"reproject_and_resample_band error: {e}")
        return None


def resample_and_merge_multiband(base_raster, layers_dict, output_path, dst_epsg=32651):
    with rasterio.open(base_raster) as ref:
        src_crs = ref.crs
        dst_crs = rasterio.crs.CRS.from_epsg(dst_epsg)
        dst_transform, dst_width, dst_height = calculate_default_transform(
            src_crs, dst_crs, ref.width, ref.height, *ref.bounds
        )
        ref_meta = ref.meta.copy()

    dtype = np.float32
    nodata_val = np.nan
    layer_order = [
        "water",
        "park",
        "street",
        "building_height",
        "building_type",
        "building_style",
        "landuse",
        "lst",
    ]
    band_count = len(layer_order)
    merged_array = np.full((band_count, dst_height, dst_width), nodata_val, dtype=dtype)
    for i, layer in enumerate(layer_order):
        path = layers_dict.get(layer)
        if layer.startswith("building_"):
            band_map = {"building_height": 1, "building_type": 2, "building_style": 3}
            band_index = band_map.get(layer, 1)
        else:
            band_index = 1
        if path and os.path.exists(path):
            arr = reproject_and_resample_band(path, band_index, dst_crs, dst_transform, dst_width, dst_height)
            if arr is not None:
                valid_mask = (~np.isnan(arr)) & (arr != 0) & (arr != 255)
                cleaned = np.full_like(arr, nodata_val)
                cleaned[valid_mask] = arr[valid_mask]
                merged_array[i] = cleaned

    out_meta = ref_meta.copy()
    out_meta.update({
        "count": band_count,
        "dtype": "float32",
        "height": dst_height,
        "width": dst_width,
        "transform": dst_transform,
        "crs": dst_crs,
        "nodata": nodata_val,
    })
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with rasterio.open(output_path, "w", **out_meta) as dst:
        dst.write(merged_array)
    return output_path


def rasterize_by_grid_with_auto_class_mapping(shapefile_path, grid_path, class_field, output_dir, resolution=10, nodata=255):
    gdf = gpd.read_file(shapefile_path)
    grid = gpd.read_file(grid_path)
    if not gdf.crs.is_projected:
        gdf = gdf.to_crs(epsg=32651)
    if not grid.crs.is_projected:
        grid = grid.to_crs(epsg=32651)
    if gdf.crs != grid.crs:
        grid = grid.to_crs(gdf.crs)
    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notnull()]
    grid = grid[~grid.geometry.is_empty & grid.geometry.notnull()]
    if class_field not in gdf.columns:
        raise ValueError(f"字段 {class_field} 不存在于 shapefile 中")
    unique_classes = sorted(gdf[class_field].dropna().unique())
    class_to_id = {cls: idx+1 for idx, cls in enumerate(unique_classes)}
    gdf['class_val'] = gdf[class_field].map(class_to_id).fillna(0).astype(int)
    os.makedirs(output_dir, exist_ok=True)
    for idx, cell in grid.iterrows():
        grid_geom = cell.geometry
        clipped = gpd.overlay(gdf, gpd.GeoDataFrame(geometry=[grid_geom], crs=gdf.crs), how="intersection")
        if clipped.empty:
            continue
        minx, miny, maxx, maxy = grid_geom.bounds
        width = int((maxx - minx) / resolution)
        height = int((maxy - miny) / resolution)
        transform = from_origin(minx, maxy, resolution, resolution)
        shapes_list = [(geom, val) for geom, val in zip(clipped.geometry, clipped['class_val'])]
        raster = rasterize(
            shapes=shapes_list,
            out_shape=(height, width),
            transform=transform,
            fill=nodata,
            dtype='uint8'
        )
        tile_id = cell.get("ID", idx)
        out_path = os.path.join(output_dir, f"tile_{tile_id}.tif")
        with rasterio.open(
            out_path,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=1,
            dtype="uint8",
            crs=gdf.crs,
            transform=transform,
            nodata=nodata,
        ) as dst:
            dst.write(raster, 1)
    return True


def rasterize_multiple_fields_to_multiband(shapefile_path, grid_path, class_fields, output_dir, resolution=10, nodata=255, start_id=0):
    gdf = gpd.read_file(shapefile_path)
    grid = gpd.read_file(grid_path)
    if not gdf.crs.is_projected:
        gdf = gdf.to_crs(epsg=32651)
    if not grid.crs.is_projected:
        grid = grid.to_crs(epsg=32651)
    if gdf.crs != grid.crs:
        grid = grid.to_crs(gdf.crs)
    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notnull()]
    grid = grid[~grid.geometry.is_empty & grid.geometry.notnull()]
    os.makedirs(output_dir, exist_ok=True)
    field_maps = {}
    for field in class_fields:
        if field not in gdf.columns:
            raise ValueError(f"字段 {field} 不存在于 shapefile 中")
        if gdf[field].dtype.kind in ['O', 'U']:
            unique_vals = sorted(gdf[field].dropna().unique())
            val_map = {v: i+1 for i, v in enumerate(unique_vals)}
            field_maps[field] = val_map
            gdf[f"__mapped_{field}"] = gdf[field].map(val_map).fillna(0).astype(int)
        else:
            gdf[f"__mapped_{field}"] = gdf[field].fillna(0)
    for idx, cell in grid.iterrows():
        tile_id = cell.get("ID", idx)
        if tile_id < start_id:
            continue
        out_path = os.path.join(output_dir, f"building_tile_{tile_id}.tif")
        if os.path.exists(out_path):
            continue
        grid_geom = cell.geometry
        clipped = gpd.overlay(gdf, gpd.GeoDataFrame(geometry=[grid_geom], crs=gdf.crs), how="intersection")
        if clipped.empty:
            continue
        minx, miny, maxx, maxy = grid_geom.bounds
        width = int((maxx - minx) / resolution)
        height = int((maxy - miny) / resolution)
        transform = from_origin(minx, maxy, resolution, resolution)
        bands = []
        for field in class_fields:
            mapped_col = f"__mapped_{field}"
            class_vals = clipped[mapped_col]
            shapes_list = [(geom, val) for geom, val in zip(clipped.geometry, class_vals)]
            raster = rasterize(
                shapes=shapes_list,
                out_shape=(height, width),
                transform=transform,
                fill=nodata,
                dtype='uint8' if class_vals.dtype == int else 'float32',
            )
            bands.append(raster)
        bands_array = np.stack(bands, axis=0)
        with rasterio.open(
            out_path,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=len(class_fields),
            dtype=bands_array.dtype,
            crs=gdf.crs,
            transform=transform,
            nodata=nodata,
        ) as dst:
            dst.write(bands_array)
    return True


def raster_to_geojson_per_band(raster_path, output_folder, band_index=1, nodata=None):
    os.makedirs(output_folder, exist_ok=True)
    with rasterio.open(raster_path) as src:
        band = src.read(band_index)
        transform = src.transform
        if nodata is None:
            nodata = src.nodata
        mask = band != nodata
        results = (
            {'properties': {'value': int(v)}, 'geometry': s}
            for s, v in shapes(band, mask=mask, transform=transform)
        )
        gdf = gpd.GeoDataFrame.from_features(results, crs=src.crs)
        out_path = os.path.join(output_folder, f"{os.path.basename(raster_path)}_band{band_index}.geojson")
        gdf.to_file(out_path, driver='GeoJSON')
    return out_path
