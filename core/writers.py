# 生成器：负责将中间数据写出为目标格式文件
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import os


# ==========================================
# 1. Pascal VOC (XML) 生成器
# ==========================================
def write_voc(output_path, filename, size_dict, objects):
    """
    生成单个 Pascal VOC XML 文件
    :param output_path: XML 文件的完整保存路径
    :param filename: 图片文件名 (如 image.jpg)
    :param size_dict: 包含宽高的字典 {"width": 800, "height": 600}
    :param objects: 标注列表 [{"name": "dog", "bbox": [xmin, ymin, xmax, ymax]}, ...]
    """
    annotation = ET.Element("annotation")

    ET.SubElement(annotation, "folder").text = "images"
    ET.SubElement(annotation, "filename").text = filename

    # 尺寸信息
    size = ET.SubElement(annotation, "size")
    ET.SubElement(size, "width").text = str(size_dict.get("width", 0))
    ET.SubElement(size, "height").text = str(size_dict.get("height", 0))
    ET.SubElement(size, "depth").text = str(size_dict.get("depth", 3))  # 默认彩色图深度为 3

    # 遍历添加目标框
    for obj_data in objects:
        obj = ET.SubElement(annotation, "object")
        ET.SubElement(obj, "name").text = obj_data["name"]
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "0"
        ET.SubElement(obj, "difficult").text = "0"

        bndbox = ET.SubElement(obj, "bndbox")
        # 确保坐标是整数或浮点数，VOC 习惯用整数或带一位小数
        bbox = obj_data["bbox"]
        ET.SubElement(bndbox, "xmin").text = str(int(float(bbox[0])))
        ET.SubElement(bndbox, "ymin").text = str(int(float(bbox[1])))
        ET.SubElement(bndbox, "xmax").text = str(int(float(bbox[2])))
        ET.SubElement(bndbox, "ymax").text = str(int(float(bbox[3])))

    # 为了让生成的 XML 有漂亮的换行和缩进，使用 minidom 处理一下
    raw_string = ET.tostring(annotation, 'utf-8')
    reparsed = minidom.parseString(raw_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="  ")

    with open(output_path, "w", encoding="utf-8") as f:
        # toprettyxml 会自带一个 xml 声明，这里写入文件
        f.write(pretty_xml_as_string)


# ==========================================
# 2. YOLO (TXT) 生成器
# ==========================================
def write_yolo(output_path, objects, class_name_to_id):
    """
    生成单个 YOLO TXT 文件
    :param output_path: TXT 文件的完整保存路径
    :param objects: 标注列表 [{"name": "dog", "bbox": [x_center, y_center, w, h]}, ...]
    :param class_name_to_id: 字典，如 {"dog": 0, "cat": 1}，用于解决 YOLO 的类别 ID 问题
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for obj in objects:
            name = obj["name"]

            # 核心逻辑：动态分配类别 ID
            if name not in class_name_to_id:
                # 如果遇到新类别，就给它分配一个当前字典长度的新 ID
                class_name_to_id[name] = len(class_name_to_id)

            class_id = class_name_to_id[name]
            bbox = obj["bbox"]

            # YOLO 坐标要求 0~1 之间的归一化数值，保留 6 位小数防止科学计数法
            x_c, y_c, w, h = bbox
            line = f"{class_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n"
            f.write(line)


# ==========================================
# 3. COCO (JSON) 生成器
# ==========================================
def write_coco(output_path, all_images_data):
    """
    生成一个完整的 COCO JSON 文件
    注意：COCO 不是一张图一个文件，而是整个数据集汇总成一个 JSON。
    因此在 Pipeline 中，我们要收集所有图片处理后的数据，最后调这个函数一次。

    :param output_path: 输出的 json 文件路径 (如 output/annotations.json)
    :param all_images_data: 列表，包含所有标准化的图片字典数据
    """
    coco_format = {
        "info": {"description": "Converted Dataset"},
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": []
    }

    class_name_to_id = {}
    annotation_id = 1  # COCO 的 annotation_id 必须是全局唯一的，通常从 1 开始

    for img_id, img_data in enumerate(all_images_data, start=1):
        # 1. 添加 image 信息
        coco_format["images"].append({
            "id": img_id,
            "file_name": img_data["filename"],
            "width": img_data["size"]["width"],
            "height": img_data["size"]["height"]
        })

        # 2. 添加 annotations 信息
        for obj in img_data.get("objects", []):
            name = obj["name"]
            if name not in class_name_to_id:
                # COCO 的 category_id 通常也从 1 开始规范些
                class_name_to_id[name] = len(class_name_to_id) + 1

            cat_id = class_name_to_id[name]
            bbox = obj["bbox"]  # [x_min, y_min, width, height]

            # 计算面积 (COCO 需要)
            area = bbox[2] * bbox[3]

            coco_format["annotations"].append({
                "id": annotation_id,
                "image_id": img_id,
                "category_id": cat_id,
                "bbox": bbox,
                "area": area,
                "iscrowd": 0,
                "segmentation": []  # 目标检测没有多边形分割
            })
            annotation_id += 1

    # 3. 添加 categories 信息
    for name, cat_id in class_name_to_id.items():
        coco_format["categories"].append({
            "id": cat_id,
            "name": name,
            "supercategory": "none"
        })

    # 写入 JSON 文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(coco_format, f, indent=4, ensure_ascii=False)