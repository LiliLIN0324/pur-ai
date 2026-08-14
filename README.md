
AI4City — 项目技术报告（工程/产品/研究汇报版）

版本：v1.0
更新时间：2026-08-14

一、执行摘要（Executive Summary）
----------------
本报告面向产品/研究负责人（Level‑3）与项目评审方，概述 AI4City 项目的目标、数据管线、模型架构、训练与评估策略、当前实现状态与建议的下一步工作。目标是让项目负责人能准确陈述系统为何这样设计、数据如何流动、关键实验如何评估，以及哪些工作需交由 CS 工程团队实现。

二、项目目标与问题定义
----------------
- 目标：在城市更新情景中，基于结构化栅格输入（语义掩码与若干辅助通道）生成满足空间/功能约束且可量化评价的城市布局设计（RGB 可视化 + 语义 mask）。
- 关键设计意图：以生成模型（条件扩散）学习复杂布局分布，同时使用像素级条件（ControlNet）和高层语义条件（Prompt）实现可控性与可解释性。

三、输入 / 输出 与 数据规范
----------------
- 主要输入：多通道栅格数据（训练代码期望存储为 .pt 包含 five_channel_tensors，典型按样本为 5ch / 可扩展为 7ch/8ch/10ch 用于 ControlNet 条件）。关键通道示例：语义 mask、建筑高度、土地利用、LST、道路等。[代码位置：prepare_enhanced_data.py; train_urban_controlnet_*.py]
- 文本条件：可选 prompt（由指标统计生成或固定字符串）。[代码位置：train_urban_controlnet_enhanced_with_prompt.py]
- 输出：生成的 RGB 图像（由 first_stage 解码器得到）与通过颜色反推得到的语义 mask，最终计算城市指标并输出 JSON/报告。[代码位置：inference_with_metrics_single.py]

四、完整处理 Pipeline（关键步骤与目的）
----------------
1) 原始城市数据 → 预处理
  - 输入：矢量/栅格源数据（GIS），输出：统一栅格化张量（保存为 .pt）
  - 目的：把异构数据规范化为可用于模型训练的张量集合。[prepare_enhanced_data.py]

2) 数据加载与包装
  - 输入：five_channel_tensors
  - 处理：Dataset 拆分出 semantic_mask 与 auxiliary_channels；Wrapper 将 semantic_mask 转为 RGB（colormap），与 auxiliary 拼接为 hint（7ch），再生成街道骨架并扩展为 10ch 作为 ControlNet 条件。
  - 输出：训练迭代中传给模型的条件字典 cond={'c_crossattn': [text_embedding], 'c_concat': [control_tensor]}。[train_urban_controlnet_*.py]

3) 模型（训练/初始化）
  - 初始化方式：create_model(config_path) + load_state_dict(resume_path)（通常加载预训练 SD checkpoint）。[cldm/model.py; train scripts]
  - 训练模式：支持 'lora' vs 'full' 两种模式（脚本含 mode 标志），optimizer 配置会依据 sd_locked 控制训练参数集合（control_model 或加上部分 diffusion 模块）。注意：代码中并未找到完整 LoRA adapter 的实现证据，mode 更像是训练策略开关而非完整适配器实现。[train_urban_controlnet_*.py; grep 结果]

4) 采样与解码
  - 采样器：DDIM（可替换 PLMS / DPM），支持 classifier-free guidance（提供无条件 conditioning）。[cldm/cldm.py; ldm samplers]
  - 解码：decode_first_stage 将 latent → RGB；随后通过色彩邻近映射 (_rgb_to_mask) 恢复语义类别 mask（近似方法，依赖 colormap）。[train scripts]

5) 指标计算与评估
  - 指标集合：green_rate, water_rate, building_coverage_rate, road_density, land_use_mix, far, open_space_rate 等（由 UrbanMorphologyMetrics 实现），并可生成报告与可视化。[train scripts; inference_with_metrics_single.py]

五、关键技术与实现细节（事实驱动）
----------------
- ControlNet：项目用法为把多通道 hint（最终为 10ch）作为 c_concat 传递，ControlNet 生成多尺度 control 张量并注入 UNet（代码在 cldm/cldm.py 的 ControlLDM 与 ControlledUnetModel）。[CODE]
- 文本 Prompt：with_prompt 模式会基于数据统计生成文本（指标 + 占比说明），并通过 get_learned_conditioning 转为 cross-attention 条件 c_crossattn。[CODE]
- 指标 loss：UrbanMorphologyLoss 将指标差的 MSE 加权后并入训练总 loss（训练脚本在 training_step 中周期性计算并加权）。[CODE]
- Discrete DiT：README 中有讨论，但当前仓库并未实现离散扩散/DiT；主流程仍为连续 latent diffusion（模型预测 eps / noise）。请在对外陈述中区分“讨论/计划”与“已实现”。[CODE vs README]

六、训练配置要点（可复述的事实）
----------------
- 默认学习率示例：1e-5（脚本参数）；优化器示例：Adam / AdamW（configure_optimizers 中）；scheduler：CosineAnnealingLR（脚本中配置）。[train_urban_controlnet_*.py]
- batch size：脚本接受参数，示例默认为 1–2（受内存与采样步数影响）。
- checkpoint：pytorch_lightning ModelCheckpoint（monitor 'train/total_loss'，save_top_k=1），并在训练完成时保存 final checkpoint。[train scripts]

七、现状差异与风险（必须在对外陈述中说明）
----------------
- LoRA：脚本包含 mode='lora' 标志并打印日志，但仓库未找到实际 LoRA adapter/实现；需与 CS 团队确认或补实现。（风险：如果对外声称已使用 LoRA，会被追问实现证据）[CODE]
- Discrete DiT：README 中提及尝试，但代码库中无实现证据；请勿在演示或面试中把其当作已实现功能。［README vs CODE］
- RGB→Mask 的映射为近似最近邻色彩回溯，易受色偏影响；若需要严格类别边界准确性，应考虑在模型中加入分类 head 或在训练中直接预测离散类别。［CODE: _rgb_to_mask 实现］

八、建议的下一步工作（短期优先级）
----------------
1) 修正代码组织：把 UrbanMorphologyMetrics 提取到公共工具（`utils.py`）以避免导入不一致，保证 inference/训练脚本可直接复用。 （优先级：高）
2) 明确 LoRA 路线：若需要 LoRA，请让 CS 实现 adapter 并在 repo 中提供小样例；否则从文档中移除误导性表述。 （优先级：高）
3) 为对比实验编写自动化脚本：固定 random seed 执行 with_prompt vs without_prompt 的训练与多次采样统计（指标分布、稳定性、视觉一致性）。 （优先级：中）
4) 将 demo 精简为 NumPy/Matplotlib 版本以便公开演示（已在 ai4city_portfolio 中有初步实现）。 （优先级：中）

九、附录 — 重要代码位置（便于面试时快速指引）
----------------
- 训练入口：[AI4City_Urban_Regeneration/train_urban_controlnet_enhanced_with_prompt.py](AI4City_Urban_Regeneration/train_urban_controlnet_enhanced_with_prompt.py)
- 简化训练（无 prompt）：[AI4City_Urban_Regeneration/train_urban_controlnet_enhanced_without_prompt.py](AI4City_Urban_Regeneration/train_urban_controlnet_enhanced_without_prompt.py)
- 推理/评估：[AI4City_Urban_Regeneration/inference_with_metrics_single.py](AI4City_Urban_Regeneration/inference_with_metrics_single.py)
- ControlNet / CLDM：[AI4City_Urban_Regeneration/cldm/](AI4City_Urban_Regeneration/cldm/)
- 基础 LDM：[AI4City_Urban_Regeneration/ldm/](AI4City_Urban_Regeneration/ldm/)
- 可视化/工具：[AI4City_Urban_Regeneration/utils.py](AI4City_Urban_Regeneration/utils.py)
- 数据准备：[AI4City_Urban_Regeneration/prepare_enhanced_data.py](AI4City_Urban_Regeneration/prepare_enhanced_data.py)


