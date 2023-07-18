import os
import tkinter as tk
import json
from tkinter import filedialog
from googletrans import Translator as GoogleTranslator
from translate import Translator as LocalTranslator
class TranslatorGUI:
    def __init__(self):
        self.folder_path = ""
        self.original_file_names = []
        self.original_file_paths = []  # 用于存储文件的完整路径
        self.translated_file_names = []  # 用于存储翻译后的文件名
        self.target_language = 'zh-CN'  # 默认目标语言为中文（简体）

        self.window = tk.Tk()
        self.window.title("文件名翻译器")
        self.window.geometry("1000x800")

        # 左侧部分
        left_frame = tk.Frame(self.window)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # 中间部分
        middle_frame = tk.Frame(self.window)
        middle_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        # 右侧部分
        right_frame = tk.Frame(self.window)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        # 设置第1列的权重为3
        self.window.columnconfigure(0, weight=3);self.window.rowconfigure(0, weight=1)       
        # 设置第2列的权重为4
        self.window.columnconfigure(1, weight=5);self.window.rowconfigure(0, weight=1)
        # 设置第3列的权重为3
        self.window.columnconfigure(2, weight=3);self.window.rowconfigure(0, weight=1)        

        # 创建选择文件夹按钮
        select_folder_button = tk.Button(left_frame, text="选择文件夹", command=self.select_folder)
        select_folder_button.grid(row=0, column=0, padx=10, pady=10)
        # 创建选择文件按钮
        select_file_button = tk.Button(left_frame, text="选择文件", command=self.select_files)
        select_file_button.grid(row=1, column=0, padx=10, pady=10)
        # 创建翻译文件名按钮
        translate_button = tk.Button(middle_frame, text="翻译文件名", command=self.translate_file_names)
        translate_button.grid(row=0, column=0, padx=10, pady=10)
        # 创建"用翻译名重命名"按钮
        rename_button = tk.Button(right_frame, text="用翻译名重命名", command=self.rename_files)
        rename_button.grid(row=0, column=0, padx=10, pady=10)
        # 创建"回退为原文件名"按钮
        restore_button = tk.Button(right_frame, text="回退为原文件名", command=self.restore_file_names)
        restore_button.grid(row=1, column=0, padx=10, pady=10)
        # 创建翻译引擎标签
        tk.Label(left_frame, text="\n当前使用的翻译引擎:").grid(row=2, column=0, padx=5, pady=0,sticky="s")
        # 创建复选框控件，用于选择翻译引擎
        self.engine_var = tk.StringVar()
        self.engine_var.set("译技术mymemory")
        engines = [ "译技术mymemory","谷歌翻译(需翻墙)","自由译libre(等更新)","微软翻译(需API密钥)","深度ai译deepl(需API密钥)"]
        tk.OptionMenu(left_frame, self.engine_var, *engines).grid(row=3, column=0, padx=10, pady=0,sticky="n")
        # 创建原语言和目标语言标签
        tk.Label(middle_frame, text="\n原语言：").grid(row=1, column=0)
        tk.Label(middle_frame, text="目标语言：").grid(row=3, column=0)


        # 创建选择原语言和目标语言的下拉菜单
        self.source_language_var = tk.StringVar()
        self.target_language_var = tk.StringVar()
        self.source_language_var.set("自动")  
        self.target_language_var.set("中文（简体）")  
        source_language_menu = tk.OptionMenu(middle_frame, self.source_language_var, "自动", "英语", "俄语", "德语", "中文（繁体）", "中文（简体）", "西班牙语", "法语", "日语", "韩语")
        source_language_menu.grid(row=2, column=0)
        target_language_menu = tk.OptionMenu(middle_frame, self.target_language_var, "中文（简体）",  "俄语", "德语", "中文（繁体）","英语", "西班牙语", "法语", "日语", "韩语")
        target_language_menu.grid(row=4, column=0)

        # 在right_frame中创建一个标签，用于显示API密钥输入框的提示
        api_key_label = tk.Label(right_frame, text="输入API密钥：")
        api_key_label.grid(row=2, column=0, padx=5, pady=5)

        # 创建用于输入API密钥的Entry小部件
        self.api_key_entry = tk.Entry(right_frame, show="*")  # 使用show="*"来隐藏输入的内容
        self.api_key_entry.grid(row=3, column=0, padx=5, pady=5)

        # 创建一个按钮，用于保存API密钥
        save_api_key_button = tk.Button(right_frame, text="保存API密钥", command=self.save_api_key)
        save_api_key_button.grid(row=4, column=0, padx=5, pady=10)

        # 加载已保存的API密钥（如果有）
        self.load_api_key()


        # 创建"原文件名展示框"标签
        tk.Label(left_frame, text="\n\n原文件名展示框").grid(row=4, column=0,padx=10, pady=0, sticky="s")
        # 创建"翻译名称预览框"标签
        tk.Label(middle_frame, text="\n\n翻译名称预览框,双击可修改").grid(row=5, column=0, padx=10, pady=0, sticky="s")
        # 创建"实时文件名展示框"标签
        tk.Label(right_frame, text="\n\n实时文件名展示框").grid(row=5, column=0, padx=10, pady=0, sticky="s")

        # 创建原文件名列表框
        self.file_listbox = tk.Listbox(left_frame)
        self.file_listbox.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
        #设置权重填满竖向
        left_frame.columnconfigure(0, weight=1);left_frame.rowconfigure(5, weight=1)

        # 创建翻译名称列表框
        self.translated_file_listbox = tk.Listbox(middle_frame, selectmode=tk.EXTENDED)
        self.translated_file_listbox.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
        #设置权重填满竖向
        middle_frame.columnconfigure(0, weight=1);middle_frame.rowconfigure(6, weight=1)

        # 创建实时文件名列表框
        self.realtime_file_listbox = tk.Listbox(right_frame)
        self.realtime_file_listbox.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
        #设置权重填满竖向
        right_frame.columnconfigure(0, weight=1);right_frame.rowconfigure(6, weight=1)

        # 绑定双击事件，允许编辑翻译名称预览框中的文件名
        self.translated_file_listbox.bind("<Double-Button-1>", self.edit_translated_filename)

        # 创建Entry小部件，用于编辑翻译名称预览框中的文件名
        self.edit_entry = None

    def translate_file_names(self):
        self.translated_file_listbox.delete(0, tk.END)
        self.translated_file_names = []
        self.source_language = self.get_eng_name(self.source_language_var.get())
        self.target_language = self.get_eng_name(self.target_language_var.get())
        self.engine = self.get_eng_name(self.engine_var.get())
        file_names_to_translate = [os.path.splitext(file_name)[0].lower() for file_name in self.file_listbox.get(0,tk.END)]
        # print("\n\n读取名称\n\n",file_names_to_translate)
        file_names_to_translate=(";\n".join(file_names_to_translate))
        # print("\n\n转为字符串\n\n"+file_names_to_translate)
        file_names_to_translate = file_names_to_translate.replace('-', ' ').replace('_', ' ').replace(',', ' ').strip()
        # print("\n\n去除其他符号\n\n"+file_names_to_translate)
        # try:
        if self.engine == "GoogleTranslator":
            # 翻译引擎是 GoogleTranslator
            # 在这里进行对应的处理
            translator=GoogleTranslator()
            translated_text = translator.translate(file_names_to_translate, dest=self.target_language,src=self.source_language)
            self.translated_file_names = translated_text.text
        else:
            translator=LocalTranslator(from_lang=self.source_language.replace('auto', 'autodetect'),to_lang=self.target_language,provider = self.engine,secret_access_key ="self.api_key_entry.get()")
            if len(file_names_to_translate) > 500:
                temp_len_text = file_names_to_translate
                # 如果字符数超过500，切割字符串，保留最接近500字符的部分
                while len(temp_len_text) > 500:
                    temp_text = temp_len_text[:500]
                    # print("\n\ntemp_text\n\n",temp_text)
                    last_newline_index = temp_text.rfind('\n')
                    if last_newline_index != -1:
                        temp_to_translate = temp_text[:last_newline_index]
                        
                    else:
                        temp_to_translate = temp_text
                    # print("\n\ntemp_to_translate\n\n",temp_to_translate)
                    temp_translated = translator.translate(temp_to_translate)
                    # print("\n\n单段翻译后\n\n",temp_translated)
                    if "PLEASE SELECT TWO DISTINCT LANGUAGES" in temp_translated:
                        temp_translated =  temp_to_translate
                    self.translated_file_names.append(temp_translated)
                    temp_to_translate=""
                    temp_len_text = temp_len_text[last_newline_index + 1:]
                # 翻译最后剩余的部分
                temp_to_translate = temp_len_text
                temp_translated = translator.translate(temp_to_translate)
                if "PLEASE SELECT TWO DISTINCT LANGUAGES" in temp_translated:
                    temp_translated =  temp_to_translate
                self.translated_file_names.append(temp_translated)
                temp_to_translate=""
            else:
                # 字符数未超过500，直接进行翻译
                self.translated_file_names = translator.translate(file_names_to_translate)
                if "PLEASE SELECT TWO DISTINCT LANGUAGES" in self.translated_file_names:
                    self.translated_file_names =  file_names_to_translate
        # print("\n\n翻译后\n\n",self.translated_file_names)
        
        self.translated_file_names="".join(self.translated_file_names)
        self.translated_file_names = self.translated_file_names.replace(',', ' ').replace('；\n', ',').replace(';\n', ',').replace(';', ' ').replace('\n', ',').replace('；', '').split(",")
        # print("\n\n最终字符\n\n",self.translated_file_names)

        self.translated_file_names_with_extension = []
        for translated_file_name, original_file_name in zip(self.translated_file_names, self.file_listbox.get(0, tk.END)):
            _, extension = os.path.splitext(original_file_name)
            self.translated_file_listbox.insert(tk.END, translated_file_name + extension)
            self.translated_file_names_with_extension.append(translated_file_name + extension)
        self.translated_file_names=self.translated_file_names_with_extension
        # print("\n\n后缀字符\n\n",self.translated_file_names)

        # except Exception as e:
        #     print("翻译出错:", e)
        #     translated_file_names = [file_name for file_name in self.file_listbox.get(0, tk.END)]
        #     self.translated_file_listbox.insert

        # 语言转换模块
    def get_eng_name(self, engname):
        eng_name = {
            "自动": "auto",
            "英语": "en",
            "俄语": "ru",
            "德语": "de",
            "中文（繁体）": "zh-TW",
            "中文（简体）": "zh-CN",
            "西班牙语": "es",
            "法语": "fr",
            "日语": "ja",
            "韩语": "ko",
            "译技术mymemory": "mymemory",
            "谷歌翻译(需翻墙)": "GoogleTranslator",
            "自由译libre(等更新)": "libre",
            "微软翻译(需API密钥)": "microsoft",
            "深度ai译deepl(需API密钥)": "deepl"
        }
        return eng_name.get(engname,"en")  # 默认为英语    

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.original_file_names = []  # 清空原文件名列表
            self.original_file_paths = []  # 清空原文件路径列表
            self.translated_file_names = []  # 清空翻译后的文件名列表
            self.translated_file_listbox.delete(0, tk.END)  # 清空翻译名称预览框
            self.folder_path = folder_path
            self.update_file_listbox()

            # 更新self.original_file_names和self.original_file_paths列表
            for file_name in os.listdir(self.folder_path):
                self.original_file_names.append(file_name)
                self.original_file_paths.append(os.path.join(self.folder_path, file_name))

    def select_files(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.original_file_names = []  # 清空原文件名列表
            self.original_file_paths = []  # 清空原文件路径列表
            self.translated_file_names = []  # 清空翻译后的文件名列表
            self.translated_file_listbox.delete(0, tk.END)  # 清空翻译名称预览框
            self.folder_path = os.path.dirname(file_paths[0])
            self.original_file_paths = list(file_paths)
            self.original_file_names = [os.path.basename(path) for path in file_paths]
            self.file_listbox.delete(0, tk.END)  # Clear the previous file list
            for file_name in self.original_file_names:
                self.file_listbox.insert(tk.END, file_name)

    def update_file_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file_name in os.listdir(self.folder_path):
            self.file_listbox.insert(tk.END, file_name)

    def rename_files(self):
        self.realtime_file_listbox.delete(0, tk.END) 
        for i, translated_name in enumerate(self.translated_file_names):
            if i < len(self.original_file_paths):
                old_path = self.original_file_paths[i]
                new_path = os.path.join(self.folder_path, translated_name)
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    print("命名出错:", e)
                self.realtime_file_listbox.insert(tk.END, translated_name)

    def restore_file_names(self):
        self.realtime_file_listbox.delete(0, tk.END)  
        for i, file_name in enumerate(self.original_file_names):
            if i < len(self.original_file_paths):
                old_path = os.path.join(self.folder_path, self.translated_file_listbox.get(i))
                new_path = os.path.join(self.folder_path, file_name)
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    print("命名出错:", e) 
                self.realtime_file_listbox.insert(tk.END, file_name)
    def load_api_key(self):
        # 尝试从配置文件中加载API密钥
        if os.path.exists("config.json"):
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                if "api_key" in config:
                    api_key = config["api_key"]
                    self.api_key_entry.insert(0, api_key)

    def save_api_key(self):
        # 获取用户输入的API密钥
        api_key = self.api_key_entry.get()

        # 保存API密钥到配置文件
        config = {"api_key": api_key}
        with open("config.json", "w") as config_file:
            json.dump(config, config_file)

        print("API密钥已保存至同目录下config.json文件。")

    def edit_translated_filename(self, event):
        selected_indices = self.translated_file_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]

            # 销毁先前的Entry小部件，避免多个Entry小部件重叠
            if self.edit_entry:
                self.edit_entry.destroy()

            # 创建Entry小部件以允许编辑
            selected_filename = self.translated_file_listbox.get(index)
            self.edit_entry = tk.Entry(self.translated_file_listbox)
            self.edit_entry.pack()
            self.edit_entry.insert(0, selected_filename)  # 在Entry小部件中显示当前文件名

            def on_edit_complete(event):
                new_filename = self.edit_entry.get()

                # 更新列表框中的文件名
                self.translated_file_listbox.delete(index)
                self.translated_file_listbox.insert(index, new_filename)

                # 更新文件名列表
                self.translated_file_names[index] = new_filename

                # 销毁Entry小部件
                self.edit_entry.destroy()
                self.edit_entry = None

            def on_edit_cancel(event):
                # 销毁Entry小部件
                self.edit_entry.destroy()
                self.edit_entry = None

            # 绑定编辑完成和取消事件
            self.edit_entry.bind("<Return>", on_edit_complete)
            self.edit_entry.bind("<FocusOut>", on_edit_complete)
            self.edit_entry.bind("<Escape>", on_edit_cancel)

            self.edit_entry.focus_set()

    def run(self):
        self.window.mainloop()
    
if __name__ == "__main__":
    app = TranslatorGUI()
    app.run()
