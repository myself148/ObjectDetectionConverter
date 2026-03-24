import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import threading

# 将项目根目录加入 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import pipeline

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ODConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("目标检测格式转换器")
        self.geometry("800x750")  # 增高窗口以容纳终端

        self.source_format_var = ctk.StringVar(value="Pascal VOC (XML)")
        self.target_format_var = ctk.StringVar(value="YOLO (TXT)")
        self.img_dir_var = ctk.StringVar()
        self.anno_dir_var = ctk.StringVar()
        self.out_dir_var = ctk.StringVar()

        # ==================== UI 元素 ====================
        self.label_title = ctk.CTkLabel(self, text="目标检测数据集转换", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=(15, 5))

        # 配置区
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(self.frame_config, text="当前格式:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0,
                                                                                                padx=10, pady=10)
        ctk.CTkOptionMenu(self.frame_config, values=["Pascal VOC (XML)", "YOLO (TXT)", "COCO (JSON)"],
                          variable=self.source_format_var).grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.frame_config, text="目标格式:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2,
                                                                                                padx=10, pady=10)
        ctk.CTkOptionMenu(self.frame_config, values=["YOLO (TXT)", "Pascal VOC (XML)", "COCO (JSON)"],
                          variable=self.target_format_var).grid(row=0, column=3, padx=10, pady=10)

        # 文件夹选择区
        self.frame_dirs = ctk.CTkFrame(self)
        self.frame_dirs.pack(padx=20, pady=5, fill="x")
        self.frame_dirs.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_dirs, text="图片文件夹:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(self.frame_dirs, textvariable=self.img_dir_var, state="disabled").grid(row=0, column=1, padx=5,
                                                                                            pady=10, sticky="ew")
        ctk.CTkButton(self.frame_dirs, text="浏览...", width=60,
                      command=lambda: self.select_dir(self.img_dir_var)).grid(row=0, column=2, padx=10, pady=10)

        ctk.CTkLabel(self.frame_dirs, text="标注文件夹:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(self.frame_dirs, textvariable=self.anno_dir_var, state="disabled").grid(row=1, column=1, padx=5,
                                                                                             pady=10, sticky="ew")
        ctk.CTkButton(self.frame_dirs, text="浏览...", width=60,
                      command=lambda: self.select_dir(self.anno_dir_var)).grid(row=1, column=2, padx=10, pady=10)

        ctk.CTkLabel(self.frame_dirs, text="输出根目录:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(self.frame_dirs, textvariable=self.out_dir_var, state="disabled").grid(row=2, column=1, padx=5,
                                                                                            pady=10, sticky="ew")
        ctk.CTkButton(self.frame_dirs, text="浏览...", width=60,
                      command=lambda: self.select_dir(self.out_dir_var)).grid(row=2, column=2, padx=10, pady=10)

        # 执行按钮
        self.btn_run = ctk.CTkButton(self, text="开始批量转换", font=ctk.CTkFont(size=16, weight="bold"), height=40,
                                     command=self.start_conversion_thread)
        self.btn_run.pack(padx=20, pady=10, fill="x")

        # 终端输出区 (新增)
        self.label_log = ctk.CTkLabel(self, text="终端输出日志:", font=ctk.CTkFont(weight="bold"))
        self.label_log.pack(padx=20, pady=(5, 0), anchor="w")

        self.textbox_log = ctk.CTkTextbox(self, height=200, fg_color="#1E1E1E", text_color="#00FF00",
                                          font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox_log.pack(padx=20, pady=(0, 15), fill="both", expand=True)
        self.textbox_log.configure(state="disabled")

    # ==================== 逻辑函数 ====================
    def select_dir(self, target_var):
        directory = filedialog.askdirectory(title="选择文件夹")
        if directory:
            target_var.set(directory)

    def write_log(self, text):
        """向终端框写入日志，并自动滚动到底部"""
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", text + "\n")
        self.textbox_log.see("end")
        self.textbox_log.configure(state="disabled")
        self.update_idletasks()  # 强制刷新 UI

    def start_conversion_thread(self):
        """使用子线程运行转换，防止 UI 界面卡死"""
        src = self.source_format_var.get()
        tar = self.target_format_var.get()
        img_dir = self.img_dir_var.get()
        anno_dir = self.anno_dir_var.get()
        out_dir = self.out_dir_var.get()

        if not img_dir or not anno_dir or not out_dir:
            messagebox.showerror("错误", "请选择完整的文件夹路径！")
            return
        if src == tar:
            messagebox.showwarning("警告", "源格式和目标格式相同！")
            return

        self.btn_run.configure(state="disabled", text="正在转换中...")
        self.textbox_log.configure(state="normal")
        self.textbox_log.delete("0.0", "end")  # 清空旧日志
        self.textbox_log.configure(state="disabled")

        # 启动后台线程执行 pipeline
        thread = threading.Thread(target=self.run_pipeline, args=(img_dir, anno_dir, out_dir, src, tar))
        thread.start()

    def run_pipeline(self, img_dir, anno_dir, out_dir, src, tar):
        try:
            self.write_log(">>> 任务启动初始化...")
            # 将 write_log 方法作为回调函数传给 pipeline
            pipeline.run(img_dir, anno_dir, out_dir, src, tar, log_callback=self.write_log)
            self.write_log("\n>>> ✅ 所有转换任务圆满完成！")
            messagebox.showinfo("成功", f"转换完成！文件已输出至:\n{out_dir}")
        except Exception as e:
            self.write_log(f"\n>>> ❌ 发生严重错误: {str(e)}")
            messagebox.showerror("转换失败", f"控制台报错:\n{str(e)}")
        finally:
            self.btn_run.configure(state="normal", text="🚀 开始批量转换")


if __name__ == "__main__":
    app = ODConverterApp()
    app.mainloop()