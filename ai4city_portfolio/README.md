AI4City — 作品集精简版

这是从 AI4City_Urban_Regeneration 项目中提取的轻量演示代码，面向公开展示与作品集使用。该包体积小、可离线运行，便于在网页或演示中嵌入。

本包内容
- [demo_portfolio.py](demo_portfolio.py): 最小可运行的演示脚本，会生成一个合成的 8 通道张量，输出可视化图片并打印指标。
- [visual_tools.py](visual_tools.py): 自包含的 `Visualizer` 与 `MetricsCalculator`，用于演示展示。
- [requirements.txt](requirements.txt): 演示所需的最小依赖清单。

快速开始（Windows）

1. 创建并激活虚拟环境：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. 安装依赖：

```powershell
pip install -r requirements.txt
```

3. 运行演示：

```powershell
python demo_portfolio.py
```

演示说明
- 生成一个小型合成 8 通道张量（包含水体、公园、道路、建筑高度等简化模式）。
- 使用 `visual_tools.Visualizer.visualize_8channel_tensor` 将 8 个通道绘制为 2x4 网格并保存为 PNG。
- 使用 `MetricsCalculator.calculate_urban_metrics` 计算一组简化的城市指标并在控制台打印结果。

输出文件
- `portfolio_visuals/demo_8channel.png`: 演示生成的通道可视化图片。

设计说明
- 本演示刻意避免包含训练代码、模型检查点和大型数据文件，便于公开共享。
- 如果希望移除 PyTorch 依赖并改写为纯 NumPy 实现，我可以帮你完成迁移以便于在无深度学习环境下发布。

许可与致谢
- 本文件夹仅提取并重用原始 AI4City 项目的部分辅助工具用于演示，工作区中保留了原始项目副本。

后续支持
- 我可以将此包打包为单文件 ZIP、生成 GitHub 仓库布局建议，或将 README/示例进一步本地化为中文教程。如需我继续处理，请告诉我你要哪个方向。