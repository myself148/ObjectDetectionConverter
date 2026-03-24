# 🔄 Object Detection Converter (目标检测数据集格式转换器)

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

一个轻量、高效且带有现代桌面 GUI 的目标检测数据集格式转换工具。致力于解决计算机视觉任务中繁琐的数据准备工作，支持一键批量转换，并自动构建标准化的输出目录结构。

## ✨ 核心特性 (Features)

- **🖥️ 现代化的桌面 GUI**：基于 CustomTkinter 构建，支持暗黑模式，操作直观。
- **🔄 多向无缝转换**：支持当前主流目标检测格式间的互相转换。
- **📂 智能目录分配**：自动根据目标格式生成标准的 `images` 和 `labels` / `annotations` / `COCO_annotations` 文件夹。
- **🧠 自动处理 YOLO 类别**：在转换为 YOLO 格式时，自动收集并生成全局 `classes.txt`。
- **🛡️ 强大的容错与终端回显**：内置前置格式校验，并在界面底部提供实时滚动的终端日志，转换进度与错误信息一目了然，彻底告别程序假死。
- **🚀 异步多线程处理**：核心逻辑在后台线程运行，保证 UI 界面丝滑流畅。

## 📦 支持的格式矩阵 (Supported Formats)

| 从 (Source) \ 到 (Target) | Pascal VOC (XML) | YOLO (TXT) | COCO (JSON) |
| :--- | :---: | :---: | :---: |
| **Pascal VOC (XML)** | - | ✅ | ✅ |
| **YOLO (TXT)** | ✅ | - | ✅ |
| **COCO (JSON)** | ✅ | ✅ | - |

> **注**：当以 YOLO (TXT) 为源格式时，标注文件夹内必须包含 `classes.txt` 文件以提供类别映射。

## 🚀 快速开始 (Quick Start)

### 1. 环境安装
确保你的电脑上已安装 Python 3.8 或更高版本。克隆此仓库并安装依赖：

```bash
git clone [https://github.com/myself148/ObjectDetectionConverter.git](https://github.com/myself148/ObjectDetectionConverter.git)
cd ObjectDetectionConverter
pip install -r requirements.txt
```

### 2. 运行程序
在项目根目录执行以下命令启动 GUI 界面：

```bash
python main.py
```

### 3. 使用说明
#### 1、选择格式：在顶部下拉菜单中选择你的源数据格式和期望转换的目标格式。

#### 2、选择路径：

图片文件夹：存放原始图片的目录（.jpg, .png 等）。

标注文件夹：存放源标注文件的目录（例如 .xml 文件夹或 .json 文件所在目录）。

输出根目录：你想保存转换后数据集的位置。

#### 3、开始转换：点击“开始批量转换”，下方的终端面板会实时显示处理进度和日志。