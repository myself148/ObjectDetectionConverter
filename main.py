import sys
import os

# 将项目根目录加入 sys.path，确保能正确找到 ui 和 core 包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.app import ODConverterApp

if __name__ == "__main__":
    app = ODConverterApp()
    app.mainloop()