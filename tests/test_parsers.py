# 测试各种格式文件解析是否正确
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.parsers import parse_yolo


def test_parse_yolo(tmp_path):
    # pytest 提供的 tmp_path 可以自动生成临时目录用于测试
    test_file = tmp_path / "test_anno.txt"
    test_file.write_text("0 0.5 0.5 0.2 0.2\n1 0.3 0.3 0.1 0.1\n")

    result = parse_yolo(str(test_file))
    objects = result["objects"]

    assert len(objects) == 2
    assert objects[0]["class_id"] == 0
    assert objects[1]["class_id"] == 1