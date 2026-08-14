# 项目说明

此项目包含用于将建筑要素按格网裁切并栅格化为多波段 GeoTIFF 的脚本与若干笔记本。

## 文件说明

- `main.py`: 原始脚本（保留副本）。为了不删除任何原始文档，保留此文件不动。
- `app.py`: `main.py` 的已命名拷贝，包含头部说明与 `__main__` 启动保护，推荐使用此文件运行和阅读。
- `*.ipynb`: 若干笔记本，包含实验/预处理等步骤（未修改）。

## 依赖

安装依赖（建议在虚拟环境中运行）：

```bash
pip install geopandas rasterio numpy
```

## 运行

在项目根目录运行：

```bash
python app.py
```

如果你希望继续使用 `main.py`，它仍然可用，内容与 `app.py` 保持一致；我不会删除任何原始文件或笔记本。

## 模块化建议与示例

核心实用函数已抽取到 `utils.py`（包括网格生成、栅格化、多波段合并与重投影/重采样）。示例用法：

```python
from utils import rasterize_multiple_fields_to_multiband

rasterize_multiple_fields_to_multiband(
	shapefile_path=r'D:\shanghai workshop\vector\building_UTM51N.shp',
	grid_path=r'D:\shanghai workshop\vector\shanghai_grid_256m_clipped.shp',
	class_fields=["Height", "Function", "Style"],
	output_dir=r'D:\shanghai workshop\raster\final_building_tiles_with_bands',
	resolution=1,
	nodata=255,
	start_id=0,
)
```

请先安装依赖（见 `requirements.txt`），并在小样本上测试函数以确认参数与路径设置正确。
