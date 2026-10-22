# AI4City · 参与式城市更新（Participatory Urban Regeneration Empowered by AI）

用可控扩散模型，从多通道城市栅格条件生成城市肌理的 RGB 图与语义图，再用形态学指标（绿地率、容积率、路网密度、用地混合度）评估生成结果，作为公众参与城市更新的可视化提案工具。

**一句话**：给定现状地块的用地、建筑高度、地表温度、道路等栅格，生成“同一地块的另一种可能”，并算出它比现状好在哪里。

---

## 方法

1. **条件构造**：将用地、建筑高度、LST、道路等图层转成 5 / 7 / 10 通道张量
2. **可控生成**：ControlNet 条件 + 街网骨架提示，DDIM 采样，支持 CFG 调节；可选由统计量生成文本提示
3. **结果还原**：生成 RGB → 按色板反查语义图，得到可统计的用地与绿地分布
4. **指标评估**：绿地率、FAR、道路密度、用地混合度等，与现状对比输出报告

## 目录

```
preprocessing/          栅格转张量、掩膜、统计
  preproc_utils.py
  raster_utils.py
  dscord_orginal/       早期 Discord Bot 版预处理与实验 notebook
ai4city_portfolio/      结果展示与指标计算（demo_portfolio.py、visual_tools.py）
AI4City_Urban_Regeneration/   模型训练与推理代码（git submodule）
```

## 运行

```bash
pip install -r requirements.txt
# 准备栅格数据 → preprocessing → 采样 → 指标评估
```

> **重要**：核心模型代码在 `AI4City_Urban_Regeneration/` 子模块中，当前远程地址不可获取，克隆后该目录为空。数据集与权重（checkpoint、`.pt`）未随仓库分发。因此仓库可直接跑通的只有预处理与指标部分，完整复现需要从作者处获取模型代码与权重。

## 数据

- 输入：研究区栅格（用地、建筑高度、LST、道路），坐标与分辨率需一致
- 输出：生成图、语义图、指标表
- 大数据与权重不入库，请通过网盘或对象存储获取

## 现状

| 部分 | 状态 |
|---|---|
| 栅格预处理 | 可用 |
| 指标计算与展示 | 可用 |
| ControlNet 训练 / 推理 | 代码在不可达子模块中 |
| LoRA、Discrete DiT | 设计过，未实现 |
| RGB → 语义图 | 基于色板的近似还原，非像素级精确 |

## 说明

这是一个研究方法原型，不是生产系统；生成结果需要人工判读，指标只衡量形态，不代表社会经济效果。

## 许可

未声明。引用或复用前请先联系作者。
