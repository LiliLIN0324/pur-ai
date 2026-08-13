# 项目代码要点汇总

本文件列出工作区笔记本中最有价值的函数与工作流，便于优先抽取、模块化或用于文档说明。

## 概要
- 目标：整理可复用、工程化价值高的代码单元（函数/处理流程）。
- 用途：生成 `utils.py`、撰写示例用法、制作轻量化 API 文档。

---

## 按笔记本的高价值代码

- 1.ipynb
  - `split_raster_by_grid`：按网格切分大栅格为 tile，便于并行/增量处理。
  - `rasterize_fclass_by_grid` / `rasterize_by_grid_with_auto_class_mapping`：自动类别映射并按格栅化单字段（街道/用地等）。
  - `rasterize_multiple_fields_to_multiband`：多个属性合成多波段 GeoTIFF（建筑高度/类型/风格）。
  - `reproject_and_resample_band` / `resample_and_merge_multiband`：统一 CRS/分辨率并合并多源波段。
  - `raster_to_geojson_per_band`：波段反向矢量化，便于导出与后处理。

- 2.ipynb
  - 重投影/重采样 + 多波段合并（示例实现）：用于把不同来源/波段对齐到同一网格。
  - 按格输出多波段建筑栅格化流程：实战型的输出流水线。
  - 逐波段可视化单元：快速质检合并波段与类别结果。

- kkkk.ipynb
  - 批量重采样与合并脚本：包含文件存在性检查与容错策略（缺层填 NaN）。
  - 矢量化/栅格化互转：模型输出回写为矢量或生成训练标签的关键工具。

- 3.ipynb
  - `rasterize_by_grid_with_auto_class_mapping`：简洁的单字段映射并按 tile 输出，适合生成训练样本。
  - `rasterize_multiple_fields_to_multiband`：多字段合成的复用实现。

- preprocessing.ipynb
  - `export_bounding_rectangle`：生成与 UTM 网格对齐的边界（保证切片无缝对齐）。
  - `generate_aligned_grid`：生成带 `ID` 的规则网格并裁剪研究区（切片基础）。
  - 几何修复与筛选单元：修复 self-intersection、统一 CRS、空间筛选。


## 跨笔记本的工程化要点（高价值）

- 全局类别映射策略（字符串→整数）：保证不同 tile/批次间标签一致。可导出映射以便复现。
- 按 tile 跳过已存在输出与 `start_id` 控制：支持断点续跑与增量处理。
- 文件与波段存在性检查、缺层容错（NaN 填充）：提高批处理鲁棒性。
- 小样本可视化单元：用于快速质检；建议保留并模块化为 `viz.py`。


## 建议的下一步（候选任务）

1. 抽取函数到 `utils.py` 并在笔记本通过 `from utils import ...` 引入。
2. 生成 `examples/` 目录，写小样本脚本（例如 `examples/run_tile.py`）以便 CI/测试。
3. 补充 `requirements.txt`，并在 `README.md` 增加运行说明与快速上手。

---

如果你同意，我可以：
- 直接把这些函数抽成 `utils.py`（并修改笔记本导入），或
- 只生成更完整的 `README.md` 节选（包含示例调用），或
- 先把本文件提交到 Git（然后你决定下一步）。
