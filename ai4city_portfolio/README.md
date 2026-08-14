```
AI4City_Urban_Regeneration/
├── models/                              # 模型配置与权重
│   ├── cldm_v15.yaml                    # 训练主配置（ControlNet/UNet/VAE/CLIP）
│   ├── cldm_enhanced_urban.yaml         # 推理默认配置（hint_channels=6）
│   ├── cldm_v15 copy.yaml               # 历史/备份配置（8通道尝试）
│   └── control_sd15_ini.ckpt            # 需云盘下载（ControlNet预训练权重，5.3GB）
├── configs/
│   └── train_config.json                # 训练参数模板（可选）
├── data/
│   └── processed_tensors_8channels.pt   # 需云盘下载（原始8通道数据，7.6GB）
├── enhanced_urban_data/
│   ├── enhanced_urban_data.pt           # （当前不使用）需云盘下载（5通道处理数据，4.8GB）
│   ├── visualization/
│   │   └── sample_0_auxiliary_masks.png # 辅助通道可视化示例
│   └── semantic_mask_sample_0.png       # 语义mask示例
├── logs/                                # 训练日志与检查点（大文件，已在 .gitignore）
│   ├── enhanced_urban_controlnet_with_prompt/
│   │   ├── best_model_epoch=24_train_total_loss=0.0000.ckpt      # 最佳模型
│   │   ├── enhanced_urban_controlnet_final.ckpt                  # 最终模型
│   │   └── enhanced_urban_controlnet_logs/
│   │       └── version_1/
│   │           ├── events.out.tfevents.1755354544.pywang-gpu03   # TensorBoard事件
│   │           └── hparams.yaml                                  # 训练超参
│   └── enhanced_urban_controlnet_without_prompt/
│       ├── best_model_epoch=00_train_total_loss=0.0000.ckpt      # 最佳模型
│       └── enhanced_urban_controlnet_logs/
│           └── version_0/
│               ├── events.out.tfevents.1755349917.pywang-gpu03   # TensorBoard事件
│               └── hparams.yaml                                  # 训练超参
├── inference_results_single/
│   ├── generated_urban_morphology.png   # 单张生成RGB
│   ├── generated_mask.png               # 单张生成语义Mask
│   ├── metrics_report.txt               # 指标对比报告
│   └── metrics_comparison.png           # 指标对比可视化
├── inference_results_batch/
│   ├── batch_urban_morphology_grid.png  # 批量生成网格
│   ├── batch_metrics_distribution.png   # 指标分布统计
│   ├── batch_generation_report.txt      # 批量生成报告
│   └── individual_images/
│       ├── image_XXX.png                # 单张RGB
│       └── mask_XXX.png                 # 对应语义Mask
├── cldm/
│   ├── cldm.py                          # ControlLDM 组装与入口
│   ├── ddim_hacked.py                   # DDIM 采样相关改动
│   ├── hack.py                          # 运行时调整/兼容辅助
│   ├── logger.py                        # ImageLogger 封装
│   └── model.py                         # create_model/load_state_dict
├── ldm/                                 # Latent Diffusion Model 组件
│   ├── data/
│   │   ├── __init__.py
│   │   └── util.py
│   ├── models/
│   │   ├── autoencoder.py               # VAE 定义
│   │   └── diffusion/
│   │       ├── __init__.py
│   │       ├── ddim.py
│   │       ├── ddpm.py
│   │       ├── dpm_solver/
│   │       │   ├── __init__.py
│   │       │   ├── dpm_solver.py
│   │       │   └── sampler.py
│   │       ├── plms.py
│   │       └── sampling_util.py
│   ├── modules/
│   │   ├── attention.py
│   │   ├── diffusionmodules/
│   │   │   ├── __init__.py
│   │   │   ├── model.py
│   │   │   ├── openaimodel.py
│   │   │   ├── upscaling.py
│   │   │   └── util.py
│   │   ├── distributions/
│   │   │   ├── __init__.py
│   │   │   └── distributions.py
│   │   ├── ema.py
│   │   ├── encoders/
│   │   │   ├── __init__.py
│   │   │   └── modules.py
│   │   ├── image_degradation/
│   │   │   ├── __init__.py
│   │   │   ├── bsrgan_light.py
│   │   │   ├── bsrgan.py
│   │   │   ├── utils/
│   │   │   │   └── test.png
│   │   │   └── utils_image.py
│   │   └── midas/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       ├── midas/
│   │       │   ├── __init__.py
│   │       │   ├── base_model.py
│   │       │   ├── blocks.py
│   │       │   ├── dpt_depth.py
│   │       │   ├── midas_net_custom.py
│   │       │   ├── midas_net.py
│   │       │   ├── transforms.py
│   │       │   └── vit.py
│   │       └── utils.py
│   └── util.py
├── prepare_enhanced_data.py             # （当前不使用）8→5通道预处理与可视化
├── train_urban_controlnet_enhanced_with_prompt     # 训练入口（带Prompt）
├── train_urban_controlnet_enhanced_without_prompt  # 训练入口（无Prompt）
├── inference_with_metrics_single.py     # 单张推理与评估
├── inference_with_metrics_batch.py      # 批量推理与评估
├── utils.py                             # 颜色映射、Mask↔RGB、指标、可视化
├── config.py                            # 全局开关（save_memory）
├── share.py                             # 共享设置（禁用冗余日志、切片注意力）
├── ai4city.yaml                         # Conda 环境定义
└── README.md                            # 项目说明
```