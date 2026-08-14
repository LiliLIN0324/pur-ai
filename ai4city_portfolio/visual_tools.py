"""精简的可视化与指标工具（用于作品集演示）。

此文件从原始 AI4City 工具中提取出核心、独立的可视化与指标计算功能，
以便在不依赖整个项目的情况下运行演示。
"""
import os
from typing import Dict, Optional

import torch
import numpy as np
import matplotlib.pyplot as plt


class Visualizer:
    """用于可视化 8 通道城市张量的轻量工具类。

    支持输入形状 `(8, H, W)` 或 `(B, 8, H, W)`（取第一个样本）。
    """

    def __init__(self, save_dir: str = "visualizations"):
        # 保存目录（不存在则创建）
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

        # 通道名称（简短中文/英文说明）
        self.channel_names = {
            0: "水体 (Water)",
            1: "公园 (Park)",
            2: "道路 (Street)",
            3: "建筑高度 (Building Height)",
            4: "建筑类型 (Building Type)",
            5: "建筑风格 (Building Style)",
            6: "土地利用 (Land Use)",
            7: "地表温度 (LST)"
        }

    def visualize_8channel_tensor(self,
                                  tensor: torch.Tensor,
                                  title: str = "8 通道城市张量",
                                  save_path: Optional[str] = None) -> plt.Figure:
        """将 8 通道张量绘制为 2x4 网格并返回 matplotlib Figure。

        Args:
            tensor: 输入张量，形状 `(8,H,W)` 或 `(B,8,H,W)`。
            title: 图像总标题。
            save_path: 可选保存路径（PNG）。
        """
        # 如果有批次维度，取第一个样本
        if len(tensor.shape) == 4:
            tensor = tensor[0]

        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.flatten()

        for i in range(8):
            channel_data = tensor[i].cpu().numpy()
            # 归一化到 [0,1] 以便显示
            if channel_data.max() > channel_data.min():
                channel_data = (channel_data - channel_data.min()) / (channel_data.max() - channel_data.min())

            im = axes[i].imshow(channel_data, cmap='viridis')
            axes[i].set_title(self.channel_names.get(i, str(i)), fontsize=10)
            axes[i].axis('off')
            plt.colorbar(im, ax=axes[i], fraction=0.046, pad=0.04)

        plt.suptitle(title, fontsize=14)
        plt.tight_layout()

        # 保存图像（如果提供路径）
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def visualize_metrics(self, metrics: Dict[str, float], title: str = "指标", save_path: Optional[str] = None) -> plt.Figure:
        """绘制简单的柱状图来展示指标值。

        Args:
            metrics: 指标字典（键->值）。
            title: 图像标题。
            save_path: 可选保存路径。
        """
        fig, ax = plt.subplots(figsize=(8, 4))
        labels = list(metrics.keys())
        values = list(metrics.values())
        bars = ax.bar(labels, values, color='skyblue')
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2., value, f'{value:.3f}', ha='center', va='bottom')
        ax.set_title(title)
        ax.set_ylabel('数值')
        plt.xticks(rotation=45)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        return fig


class MetricsCalculator:
    """从 8 通道张量计算一组简化的城市指标（用于演示）。

    注意：这些计算为演示用途，已简化并非严格工程实现。
    """

    def calculate_urban_metrics(self, tensor: torch.Tensor) -> Dict[str, float]:
        # 支持 (8,H,W) 或 (B,8,H,W)
        if len(tensor.shape) == 4:
            tensor = tensor[0]

        H, W = tensor.shape[1], tensor.shape[2]
        total_area = float(H * W)

        metrics: Dict[str, float] = {}

        # 容积率（简化）：建筑高度通道总体和 / 面积
        building_height = tensor[3]
        total_building_volume = float(torch.sum(building_height).item())
        metrics['FAR'] = total_building_volume / total_area

        # 绿地比率：公园通道 + 指定土地利用值（示例使用值 2）
        park_channel = tensor[1]
        landuse_channel = tensor[6]
        park_area = float(torch.sum(park_channel > 0).item())
        green_landuse_area = float(torch.sum(landuse_channel == 2).item())
        metrics['GreenRatio'] = (park_area + green_landuse_area) / total_area

        # 平均建筑高度
        metrics['AvgBuildingHeight'] = float(torch.mean(building_height).item())

        # 水体比率
        water_channel = tensor[0]
        water_area = float(torch.sum(water_channel > 0).item())
        metrics['WaterRatio'] = water_area / total_area

        # 道路密度（简化）
        street_channel = tensor[2]
        street_area = float(torch.sum(street_channel > 0).item())
        metrics['StreetDensity'] = street_area / total_area

        return metrics


def create_visualizer(save_dir: str = "visualizations") -> Visualizer:
    return Visualizer(save_dir)


def create_metrics_calculator() -> MetricsCalculator:
    return MetricsCalculator()
