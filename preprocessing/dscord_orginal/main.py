"""
原始入口脚本（保留副本）。

说明：
- 该文件为原始实现；已创建重命名副本 `app.py`（功能相同），便于之后阅读和维护。
- 我不会删除任何原始文档或笔记本；仅新增文件并添加说明。
"""

import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
import os
import numpy as np

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

    # ✅ 第一步：提前为所有字段生成全局映射字典
    field_maps = {}
    for field in class_fields:
        if field not in gdf.columns:
            raise ValueError(f"字段 {field} 不存在于 shapefile 中")
        if gdf[field].dtype.kind in ['O', 'U']:  # 字符型
            unique_vals = sorted(gdf[field].dropna().unique())
            val_map = {v: i+1 for i, v in enumerate(unique_vals)}
            print(f"字段 {field} 的映射：{val_map}")
            field_maps[field] = val_map
            gdf[f"__mapped_{field}"] = gdf[field].map(val_map).fillna(0).astype(int)
        else:
            gdf[f"__mapped_{field}"] = gdf[field].fillna(0)

    for idx, cell in grid.iterrows():
        tile_id = cell["ID"]

        # ✅ 跳过起始 ID 之前的 tile
        if tile_id < start_id:
            continue

        out_path = os.path.join(output_dir, f"building_tile_{tile_id}.tif")

        if os.path.exists(out_path):
            print(f"⏩ 已存在，跳过: {out_path}")
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
            shapes = [(geom, val) for geom, val in zip(clipped.geometry, class_vals)]

            raster = rasterize(
                shapes=shapes,
                out_shape=(height, width),
                transform=transform,
                fill=nodata,
                dtype='uint8' if class_vals.dtype == int else 'float32'
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
            nodata=nodata
        ) as dst:
            dst.write(bands_array)

        print(f"✅ 输出: {out_path}")

rasterize_multiple_fields_to_multiband(
    shapefile_path=r'D:\shanghai workshop\vector\Building_processed nearest 1 to 500m_finver\result\building_UTM51N.shp',
    grid_path=r"D:\shanghai workshop\vector\shanghai_grid_256m_clipped.shp",
    class_fields=["Height", "Function", "Style"],
    output_dir=r"D:\shanghai workshop\raster\final_building_tiles_with_bands",
    resolution=1,
    nodata=255,
    start_id=90000

)
