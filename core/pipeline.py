import os
import glob
import shutil
from PIL import Image
from . import parsers
from . import writers
from . import coordinate_math


def get_image_size(img_path):
    try:
        with Image.open(img_path) as img:
            return {"width": img.width, "height": img.height}
    except Exception:
        return {"width": 0, "height": 0}


def run(img_dir, anno_dir, out_dir, src_fmt, tar_fmt, log_callback=print):
    log_callback(f"源格式: {src_fmt} -> 目标格式: {tar_fmt}")

    # ================= 0. 前置安全校验 (空文件夹与格式匹配检测) =================
    log_callback(">>> 正在执行前置安全校验...")

    # 1. 检查图片目录是否为空
    valid_img_exts = ('.jpg', '.png', '.jpeg')
    img_files = [f for f in os.listdir(img_dir) if f.lower().endswith(valid_img_exts)]
    if not img_files:
        raise ValueError(f"图片文件夹为空！未找到支持的图片文件 ({', '.join(valid_img_exts)})")

    # 2. 检查标注目录并严格校验格式匹配
    if src_fmt == "Pascal VOC (XML)":
        anno_files = glob.glob(os.path.join(anno_dir, "*.xml"))
        if not anno_files:
            raise ValueError("格式不匹配或文件夹为空！选择了 VOC(XML)，但在标注文件夹中未找到任何 .xml 文件。")

    elif src_fmt == "YOLO (TXT)":
        anno_files = glob.glob(os.path.join(anno_dir, "*.txt"))
        # 过滤掉 classes.txt 本身的干扰
        anno_files = [f for f in anno_files if os.path.basename(f).lower() != "classes.txt"]
        if not anno_files:
            raise ValueError("格式不匹配或文件夹为空！选择了 YOLO(TXT)，但在标注文件夹中未找到任何 .txt 标注文件。")

    elif src_fmt == "COCO (JSON)":
        anno_files = glob.glob(os.path.join(anno_dir, "*.json"))
        if not anno_files:
            raise ValueError("格式不匹配或文件夹为空！选择了 COCO(JSON)，但在标注文件夹中未找到任何 .json 文件。")

    log_callback(f">>> 校验通过！发现 {len(img_files)} 张图片及对应的格式标注文件。")
    # ================= 1. 创建智能输出目录结构 =================
    target_img_dir = os.path.join(out_dir, "images")
    if tar_fmt == "YOLO (TXT)":
        target_anno_dir = os.path.join(out_dir, "labels")
    elif tar_fmt == "Pascal VOC (XML)":
        target_anno_dir = os.path.join(out_dir, "annotations")
    elif tar_fmt == "COCO (JSON)":
        target_anno_dir = os.path.join(out_dir, "COCO_annotations")

    os.makedirs(target_img_dir, exist_ok=True)
    os.makedirs(target_anno_dir, exist_ok=True)
    log_callback(f"构建输出目录: /images")
    log_callback(f"构建输出目录: /{os.path.basename(target_anno_dir)}")

    yolo_classes_map = {}
    if src_fmt == "YOLO (TXT)":
        classes_path = os.path.join(anno_dir, "classes.txt")
        if os.path.exists(classes_path):
            with open(classes_path, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f.readlines()):
                    yolo_classes_map[idx] = line.strip()
            log_callback(f"成功读取源 YOLO 的 classes.txt，共 {len(yolo_classes_map)} 个类别。")
        else:
            log_callback("⚠️ 警告: 未在标注目录下找到 classes.txt！如果转换报错请检查。")

    target_yolo_class_to_id = {}
    all_coco_data = []
    standardized_data = []

    # ================= 2. 读取与解析 =================
    log_callback("-" * 30)
    log_callback("开始解析源数据...")

    if src_fmt == "COCO (JSON)":
        json_files = glob.glob(os.path.join(anno_dir, "*.json"))
        if not json_files:
            raise FileNotFoundError("在标注目录中没有找到 COCO 的 JSON 文件！")
        log_callback(f"找到 COCO 文件: {os.path.basename(json_files[0])}")

        raw_data = parsers.parse_coco(json_files[0])
        log_callback(f"COCO 解析完毕，共提取 {len(raw_data)} 张图片的标注信息。")

        for img_data in raw_data:
            img_name = img_data["filename"]
            img_path = os.path.join(img_dir, img_name)

            if not os.path.exists(img_path):
                log_callback(f"⚠️ 跳过 {img_name} (在图片库中未找到实体文件)")
                continue

            # 复制图片到目标 images 目录
            shutil.copy(img_path, os.path.join(target_img_dir, img_name))

            for obj in img_data["objects"]:
                obj["bbox"] = coordinate_math.coco_to_voc(obj["bbox"])
            standardized_data.append(img_data)

    else:
        valid_exts = ('.jpg', '.png', '.jpeg')
        img_files = [f for f in os.listdir(img_dir) if f.lower().endswith(valid_exts)]
        log_callback(f"扫描到 {len(img_files)} 张实体图片，正在匹配标注...")

        success_count = 0
        for img_name in img_files:
            img_path = os.path.join(img_dir, img_name)
            base_name = os.path.splitext(img_name)[0]
            img_size = get_image_size(img_path)

            if img_size["width"] == 0:
                log_callback(f"⚠️ 损坏的图片跳过: {img_name}")
                continue

            img_data = {"filename": img_name, "size": img_size, "objects": []}
            has_anno = False

            if src_fmt == "Pascal VOC (XML)":
                xml_path = os.path.join(anno_dir, base_name + ".xml")
                if os.path.exists(xml_path):
                    parsed = parsers.parse_voc(xml_path)
                    img_data["objects"] = parsed["objects"]
                    has_anno = True

            elif src_fmt == "YOLO (TXT)":
                txt_path = os.path.join(anno_dir, base_name + ".txt")
                if os.path.exists(txt_path):
                    parsed = parsers.parse_yolo(txt_path)
                    for obj in parsed["objects"]:
                        class_name = yolo_classes_map.get(obj["class_id"], f"class_{obj['class_id']}")
                        bbox_voc = coordinate_math.yolo_to_voc(obj["bbox"], img_size["width"], img_size["height"])
                        img_data["objects"].append({"name": class_name, "bbox": bbox_voc})
                    has_anno = True

            if has_anno:
                # 复制图片到目标 images 目录
                shutil.copy(img_path, os.path.join(target_img_dir, img_name))
                standardized_data.append(img_data)
                success_count += 1
                if success_count % 50 == 0:  # 减少过多打印造成的卡顿
                    log_callback(f"已成功解析并拷贝 {success_count} 个文件...")
            else:
                log_callback(f"🔍 忽略图片: {img_name} (未找到对应的标注文件)")

        log_callback(f"成功匹配并解析 {success_count} 个文件。")

    # ================= 3. 转换与写入 =================
    log_callback("-" * 30)
    log_callback(f"开始生成目标格式 ({tar_fmt}) ...")

    for idx, img_data in enumerate(standardized_data):
        filename = img_data["filename"]
        base_name = os.path.splitext(filename)[0]
        width, height = img_data["size"]["width"], img_data["size"]["height"]

        if tar_fmt == "Pascal VOC (XML)":
            out_xml_path = os.path.join(target_anno_dir, base_name + ".xml")
            writers.write_voc(out_xml_path, filename, img_data["size"], img_data["objects"])


        elif tar_fmt == "YOLO (TXT)":
            out_txt_path = os.path.join(target_anno_dir, base_name + ".txt")
            yolo_objects = []
            for obj in img_data["objects"]:
                name = obj["name"]
                # 在这里显式为新类别分配 ID，不再依赖 writers.py 的隐式修改
                if name not in target_yolo_class_to_id:
                    target_yolo_class_to_id[name] = len(target_yolo_class_to_id)
                yolo_bbox = coordinate_math.voc_to_yolo(obj["bbox"], width, height)
                yolo_objects.append({"name": name, "bbox": yolo_bbox})
            writers.write_yolo(out_txt_path, yolo_objects, target_yolo_class_to_id)

        elif tar_fmt == "COCO (JSON)":
            coco_objects = []
            for obj in img_data["objects"]:
                coco_bbox = coordinate_math.voc_to_coco(obj["bbox"])
                coco_objects.append({"name": obj["name"], "bbox": coco_bbox})
            all_coco_data.append({
                "filename": filename,
                "size": img_data["size"],
                "objects": coco_objects
            })

        if (idx + 1) % 50 == 0:
            log_callback(f"已生成 {idx + 1} 个标注文件...")

    # ================= 4. 收尾工作 =================
    if tar_fmt == "YOLO (TXT)":
        classes_out_path = os.path.join(target_anno_dir, "classes.txt")
        sorted_classes = sorted(target_yolo_class_to_id.items(), key=lambda item: item[1])
        with open(classes_out_path, "w", encoding="utf-8") as f:
            for name, _ in sorted_classes:
                f.write(f"{name}\n")

        # 🌟 增加终端打印：直观显示到底提取到了几个类、叫什么名字
        log_callback(f"已在 labels 目录生成 classes.txt，共收集到 {len(target_yolo_class_to_id)} 个类别: {list(target_yolo_class_to_id.keys())}")

    elif tar_fmt == "COCO (JSON)":
        json_out_path = os.path.join(target_anno_dir, "annotations.json")
        writers.write_coco(json_out_path, all_coco_data)
        log_callback(f"已在 COCO_annotations 目录中生成包含 {len(all_coco_data)} 张图的 annotations.json")