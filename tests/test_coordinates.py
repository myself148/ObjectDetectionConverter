# 测试坐标系转换的准确性
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.coordinate_math import voc_to_yolo, yolo_to_voc, coco_to_voc, voc_to_coco

def test_voc_to_yolo():
    # 假设图片 400x400，框在中心，宽高各 200
    voc_box = [100, 100, 300, 300]
    expected_yolo = [0.5, 0.5, 0.5, 0.5]
    result = voc_to_yolo(voc_box, 400, 400)
    assert result == expected_yolo

def test_coco_to_voc():
    # COCO: [x_min, y_min, w, h] -> VOC: [x_min, y_min, x_max, y_max]
    coco_box = [50, 50, 100, 150]
    expected_voc = [50, 50, 150, 200]
    assert coco_to_voc(coco_box) == expected_voc