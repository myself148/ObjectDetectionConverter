# 解析器：负责读取并解析 VOC(XML), COCO(JSON), YOLO(TXT)
import xml.etree.ElementTree as ET
import json
import os


# ==========================================
# 1. Pascal VOC (XML) 解析器
# ==========================================
def parse_voc(xml_path):
    """
    解析单个 Pascal VOC XML 文件
    返回格式:
    {
        "filename": "image.jpg",
        "size": {"width": 800, "height": 600},
        "objects": [
            {"name": "dog", "bbox": [xmin, ymin, xmax, ymax]}, ...
        ]
    }
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    filename = root.find('filename').text

    size_node = root.find('size')
    width = int(size_node.find('width').text)
    height = int(size_node.find('height').text)

    objects = []
    for obj in root.findall('object'):
        name = obj.find('name').text
        bndbox = obj.find('bndbox')
        # VOC 坐标通常是 1-based，有时为了精确计算会减 1 转成 0-based，这里先保持原始提取
        xmin = float(bndbox.find('xmin').text)
        ymin = float(bndbox.find('ymin').text)
        xmax = float(bndbox.find('xmax').text)
        ymax = float(bndbox.find('ymax').text)

        objects.append({
            "name": name,
            "bbox": [xmin, ymin, xmax, ymax]
        })

    return {
        "filename": filename,
        "size": {"width": width, "height": height},
        "objects": objects
    }


# ==========================================
# 2. YOLO (TXT) 解析器
# ==========================================
def parse_yolo(txt_path):
    """
    解析单个 YOLO TXT 文件
    注意: YOLO 格式本身不包含图片宽高和类别文本名称，只包含类别 ID 和归一化坐标。
    返回格式:
    {
        "objects": [
            {"class_id": 0, "bbox": [x_center, y_center, width, height]}, ...
        ]
    }
    """
    objects = []
    if not os.path.exists(txt_path):
        return {"objects": []}  # 有些背景图可能没有 txt 文件

    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                w = float(parts[3])
                h = float(parts[4])

                objects.append({
                    "class_id": class_id,
                    "bbox": [x_center, y_center, w, h]
                })

    return {"objects": objects}


# ==========================================
# 3. COCO (JSON) 解析器
# ==========================================
def parse_coco(json_path):
    """
    解析整个 COCO JSON 文件
    注意: COCO 是一个包含整个数据集的大文件。
    为了方便按图片进行转换，我们将它重组为以 image_id 或 filename 为键的字典。
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)

    # 构建类别 ID 到类别名称的映射
    categories = {cat['id']: cat['name'] for cat in coco_data.get('categories', [])}

    # 构建以 image_id 为核心的字典
    images_dict = {}
    for img in coco_data.get('images', []):
        images_dict[img['id']] = {
            "filename": img['file_name'],
            "size": {"width": img['width'], "height": img['height']},
            "objects": []  # 准备存放属于该图的标注
        }

    # 将 annotation 分配给对应的图片
    for ann in coco_data.get('annotations', []):
        image_id = ann['image_id']
        category_id = ann['category_id']
        bbox = ann['bbox']  # COCO 格式: [x_min, y_min, width, height]

        if image_id in images_dict:
            images_dict[image_id]["objects"].append({
                "name": categories.get(category_id, str(category_id)),
                "bbox": bbox
            })

    # 返回一个列表，每个元素相当于解析好的一张图的信息，这样可以与 VOC/YOLO 逻辑对齐
    return list(images_dict.values())