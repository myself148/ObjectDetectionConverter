# 存放坐标推导和转换公式
# core/coordinate_math.py

def coco_to_voc(coco_box):
    """ [x_min, y_min, width, height] -> [x_min, y_min, x_max, y_max] """
    x_min, y_min, w, h = coco_box
    return [x_min, y_min, x_min + w, y_min + h]

def voc_to_coco(voc_box):
    """ [x_min, y_min, x_max, y_max] -> [x_min, y_min, width, height] """
    x_min, y_min, x_max, y_max = voc_box
    return [x_min, y_min, x_max - x_min, y_max - y_min]

def yolo_to_voc(yolo_box, img_width, img_height):
    """ [x_center, y_center, w_norm, h_norm] -> [x_min, y_min, x_max, y_max] """
    x_c, y_c, w_n, h_n = yolo_box
    w_abs, h_abs = w_n * img_width, h_n * img_height
    x_c_abs, y_c_abs = x_c * img_width, y_c * img_height
    return [
        x_c_abs - w_abs / 2.0,
        y_c_abs - h_abs / 2.0,
        x_c_abs + w_abs / 2.0,
        y_c_abs + h_abs / 2.0
    ]

def voc_to_yolo(voc_box, img_width, img_height):
    """ [x_min, y_min, x_max, y_max] -> [x_center, y_center, w_norm, h_norm] """
    x_min, y_min, x_max, y_max = voc_box
    w_abs = x_max - x_min
    h_abs = y_max - y_min
    x_c_abs = x_min + w_abs / 2.0
    y_c_abs = y_min + h_abs / 2.0
    return [
        x_c_abs / img_width,
        y_c_abs / img_height,
        w_abs / img_width,
        h_abs / img_height
    ]