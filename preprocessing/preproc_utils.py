"""
数据预处理工具（从 preprocessing.ipynb 提取）

包含：对齐边界、生成网格、裁剪与几何修复等常用函数，便于脚本/笔记本导入调用。
"""
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import box


def export_bounding_rectangle(input_shapefile, output_shapefile, grid_size, target_epsg=32651):
    """导出对齐到 UTM 网格的最小外接矩形并保存为 shapefile。

    参数:
        input_shapefile: 输入边界 shapefile 路径
        output_shapefile: 输出矩形 shapefile 路径
        grid_size: 网格大小（单位与 target_epsg 一致，通常米）
        target_epsg: 目标投影（默认 EPSG:32651）
    返回: 输出文件路径
    """
    gdf = gpd.read_file(input_shapefile)
    gdf = gdf.to_crs(epsg=target_epsg)
    minx, miny, maxx, maxy = gdf.total_bounds
    minx_aligned = np.floor(minx / grid_size) * grid_size
    miny_aligned = np.floor(miny / grid_size) * grid_size
    maxx_aligned = np.ceil(maxx / grid_size) * grid_size
    maxy_aligned = np.ceil(maxy / grid_size) * grid_size
    rectangle = box(minx_aligned, miny_aligned, maxx_aligned, maxy_aligned)
    out_gdf = gpd.GeoDataFrame(geometry=[rectangle], crs=gdf.crs)
    os.makedirs(os.path.dirname(output_shapefile), exist_ok=True)
    out_gdf.to_file(output_shapefile)
    return output_shapefile


def generate_aligned_grid(input_shapefile, output_shapefile, grid_size, target_epsg=32651):
    """生成与研究区对齐的规则网格并裁剪到研究区。

    参数和返回值与 notebook 中的实现一致。
    """
    gdf = gpd.read_file(input_shapefile)
    gdf = gdf.to_crs(epsg=target_epsg)
    minx, miny, maxx, maxy = gdf.total_bounds
    minx_aligned = np.floor(minx / grid_size) * grid_size
    miny_aligned = np.floor(miny / grid_size) * grid_size
    maxx_aligned = np.ceil(maxx / grid_size) * grid_size
    maxy_aligned = np.ceil(maxy / grid_size) * grid_size
    grid_cells = []
    id_counter = 0
    for x0 in np.arange(minx_aligned, maxx_aligned, grid_size):
        for y0 in np.arange(miny_aligned, maxy_aligned, grid_size):
            x1 = x0 + grid_size
            y1 = y0 + grid_size
            cell = box(x0, y0, x1, y1)
            grid_cells.append({"geometry": cell, "ID": id_counter})
            id_counter += 1
    grid_gdf = gpd.GeoDataFrame(grid_cells, crs=gdf.crs)
    grid_clipped = gpd.overlay(grid_gdf, gdf, how='intersection')
    os.makedirs(os.path.dirname(output_shapefile), exist_ok=True)
    grid_clipped.to_file(output_shapefile)
    return output_shapefile


def clip_grid_to_polygon(grid_shapefile, polygon_shapefile, output_shapefile):
    """将现有网格裁剪到给定多边形并保存结果。"""
    grid = gpd.read_file(grid_shapefile)
    poly = gpd.read_file(polygon_shapefile)
    if grid.crs != poly.crs:
        grid = grid.to_crs(poly.crs)
    # 修复常见几何问题
    poly["geometry"] = poly.geometry.buffer(0)
    grid = grid[grid.is_valid]
    grid_intersect = grid[grid.geometry.intersects(poly.unary_union)]
    os.makedirs(os.path.dirname(output_shapefile), exist_ok=True)
    grid_intersect.to_file(output_shapefile)
    return output_shapefile


def fix_geometries(shapefile_path, output_path):
    """尝试修复无效几何并保存新的 shapefile。"""
    gdf = gpd.read_file(shapefile_path)
    gdf["geometry"] = gdf.geometry.buffer(0)
    gdf = gdf[gdf.is_valid]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    gdf.to_file(output_path)
    return output_path
