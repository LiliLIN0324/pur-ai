"""作品集演示脚本（精简版）。

此脚本使用 `visual_tools` 中的轻量工具生成一个合成的 8 通道张量，
并输出可视化 PNG 与若干简化的城市指标，便于离线演示和展示。
"""

import os
from visual_tools import create_visualizer, create_metrics_calculator
import torch


def main():
    print("AI4City 作品集演示 — 生成可视化与指标")

    # 创建本地轻量工具实例
    visualizer = create_visualizer(save_dir="portfolio_visuals")
    metrics_calc = create_metrics_calculator()

    # 合成一个 8 通道张量 (8, H, W)
    H, W = 128, 128
    tensor = torch.zeros(8, H, W)

    # 构造简单的合成模式用于展示：
    # 通道0：水体（竖条）
    tensor[0, :, 30:40] = 1.0
    # 通道1：公园（方块）
    tensor[1, 60:90, 60:90] = 1.0
    # 通道2：道路（对角线）
    for i in range(min(H, W)):
        tensor[2, i, i] = 1.0
    # 通道3：建筑高度（横向梯度）
    xs = torch.linspace(0, 1, W).unsqueeze(0).repeat(H, 1)
    tensor[3] = xs

    # 生成并保存可视化（输出到 portfolio_visuals/）
    os.makedirs("portfolio_visuals", exist_ok=True)
    fig = visualizer.visualize_8channel_tensor(tensor, title="作品集演示 — 8 通道", save_path="portfolio_visuals/demo_8channel.png")
    print("已保存可视化: portfolio_visuals/demo_8channel.png")

    # 计算并打印简化指标
    metrics = metrics_calc.calculate_urban_metrics(tensor)
    print("计算得到的指标：")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")


if __name__ == '__main__':
    main()
