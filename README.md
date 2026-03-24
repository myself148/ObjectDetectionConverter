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

## 标注格式示例

为了确保转换顺利，请检查你的源数据是否符合以下标准格式：

### 1. Pascal VOC (XML)
每个图片对应一个同名的 `.xml` 文件，包含图像的绝对宽高以及目标的绝对像素坐标 `[xmin, ymin, xmax, ymax]`。
```xml
<annotation>
  <folder>images</folder>
  <filename>image_001.jpg</filename>
  <size>
    <width>800</width>
    <height>600</height>
    <depth>3</depth>
  </size>
  <object>
    <name>dog</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <bndbox>
      <xmin>150</xmin>
      <ymin>200</ymin>
      <xmax>450</xmax>
      <ymax>500</ymax>
    </bndbox>
  </object>
</annotation>
```

### 2. YOLO (TXT)
每个图片对应一个同名的 .txt 文件。每一行代表一个目标，格式为 class_id x_center y_center width height。坐标和宽高必须是 0~1 之间的归一化数值。
(注意：作为源格式读取时，同目录下必须包含 classes.txt 文件用于映射 ID 到类别名称。)

```yolo
0 0.375000 0.583333 0.375000 0.500000
1 0.750000 0.416667 0.200000 0.333333
```

### 3. COCO (JSON)
整个数据集的所有图片和标注集中在一个单一的 .json 文件中。边界框格式为绝对像素下的 [x_min, y_min, width, height]。

```JSON
{
    "images": [
        {
            "id": 1,
            "file_name": "image_001.jpg",
            "width": 800,
            "height": 600
        }
    ],
    "annotations": [
        {
            "id": 1,
            "image_id": 1,
            "category_id": 1,
            "bbox": [150.0, 200.0, 300.0, 300.0],
            "area": 90000.0,
            "iscrowd": 0,
            "segmentation": []
        }
    ],
    "categories": [
        {
            "id": 1,
            "name": "dog",
            "supercategory": "none"
        }
    ]
}
```