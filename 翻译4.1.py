import requests
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import hashlib  # 需要导入hashlib库
import random
import webbrowser

def open_youdao():
    webbrowser.open("https://fanyi.youdao.com/")

# 百度翻译的API地址和密钥，需要自己申请
api_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
app_id = "20230527001691245"
secret_key = "fgwnTwFogexEqunVpHpK"

# 支持的语言列表，可以根据需要增加或删除
languages = ["自动检测", "中文", "英语", "日语", "韩语", "法语", "德语", "西班牙语", "俄语"]

# 语言代码的对应字典，用于生成请求参数
language_codes = {
    "自动检测": "auto",
    "中文": "zh",
    "英语": "en",
    "日语": "jp",
    "韩语": "kor",
    "法语": "fra",
    "德语": "de",
    "西班牙语": "spa",
    "俄语": "ru"
}

# 创建主窗口
window = tk.Tk()
window.title("基于百度翻译的简易翻译软件")
window.geometry("1200x700")

# 创建输入文本框和滚动条
input_text = tk.Text(window, font=("宋体", 16))
input_text.place(x=50, y=100, width=300, height=470)
input_scroll = tk.Scrollbar(window)
input_scroll.place(x=350, y=100, width=20, height=470)
input_scroll.config(command=input_text.yview)
input_text.config(yscrollcommand=input_scroll.set)

# 创建输出文本框和滚动条
output_text = tk.Text(window, font=("宋体", 16), state="disabled")
output_text.place(x=450, y=100, width=300, height=350)
output_scroll = tk.Scrollbar(window)
output_scroll.place(x=750, y=100, width=20, height=350)
output_scroll.config(command=output_text.yview)
output_text.config(yscrollcommand=output_scroll.set)

#分词框和滚动条
#fenci_text = tk.Text(window, font=("宋体", 16),state="disabled")
#fenci_text.place(x=850, y=100, width=300, height=250)
#fenci_scroll = tk.Scrollbar(window)
#fenci_scroll.place(x=1150, y=100, width=20, height=250)
#fenci_scroll.config(command=fenci_text.yview)
#fenci_text.config(yscrollcommand=fenci_scroll.set)

#词频框和滚动条
#cipin_text = tk.Text(window, font=("宋体", 16),state="disabled")
#cipin_text.place(x=850, y=380, width=300, height=200)
#cipin_scroll = tk.Scrollbar(window)
#cipin_scroll.place(x=1150, y=380, width=20, height=200)
#cipin_scroll.config(command=fenci_text.yview)
#cipin_text.config(yscrollcommand=fenci_scroll.set)

# 创建历史记录文本框和滚动条
history_text = tk.Text(window, font=("宋体", 16), state="disabled")
history_text.place(x=450, y=470, width=300, height=100)
history_scroll = tk.Scrollbar(window)
history_scroll.place(x=750, y=470, width=20, height=100)
history_scroll.config(command=history_text.yview)
history_text.config(yscrollcommand=history_scroll.set)

# 创建源语言和目标语言的下拉菜单
source_language = tk.StringVar()
source_language.set("自动检测")
source_menu = ttk.Combobox(window, textvariable=source_language, values=languages, state="readonly")
source_menu.place(x=50, y=50, width=150)

target_language = tk.StringVar()
target_language.set("英语")
target_menu = ttk.Combobox(window, textvariable=target_language, values=languages, state="readonly")
target_menu.place(x=450, y=50, width=150)


# 定义翻译函数，调用百度翻译的API，并处理返回结果
def translate():
    # 获取输入文本，源语言和目标语言
    query = input_text.get("1.0", "end").strip()
    from_lang = language_codes[source_language.get()]
    to_lang = language_codes[target_language.get()]

    # 判断输入是否为空，如果为空则弹出提示框
    if not query:
        messagebox.showinfo("提示", "请输入要翻译的内容")
        return

    # 生成请求参数，包括签名和随机数
    salt = str(random.randint(32768, 65536))
    sign = app_id + query + salt + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    params = {
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'appid': app_id,
        'salt': salt,
        'sign': sign
    }

    # 发送请求并获取响应
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        result = response.json()

        # 判断是否有错误码，如果有则弹出提示框
        if result.get("error_code"):
            messagebox.showerror("错误", result.get("error_msg"))
            return

        # 提取翻译结果，并显示在输出文本框中
        output_text.config(state="normal")
        output_text.delete("1.0", "end")
        for item in result.get("trans_result"):
            output_text.insert("end", item.get("dst") + "\n")
        output_text.config(state="disabled")


        # 将输入和输出添加到历史记录文本框中，并限制最多显示10条记录
        history_text.config(state="normal")
        history_lines = history_text.get("1.0", "end").split("\n\n")
        if len(history_lines) > 10:
            history_lines.pop(0)
            history_lines.pop(0)
            history_text.delete("1.0", "end")
            history_text.insert("end", "\n\n".join(history_lines))
        history_text.insert("end", query + "\n" + output_text.get("1.0", "end").strip() + "\n\n")
        history_text.config(state="disabled")

    except Exception as e:
        # 如果发生异常，则弹出提示框
        messagebox.showerror("错误", str(e))


# 定义复制函数，将输出文本框中的内容复制到剪贴板中
def copy():
    # 获取输出文本框中的内容，并去掉末尾的换行符
    content = output_text.get("1.0", "end").strip()

    # 判断输出是否为空，如果为空则弹出提示框
    if not content:
        messagebox.showinfo("提示", "没有可复制的内容")
        return

    # 将内容复制到剪贴板中，并弹出提示框
    window.clipboard_clear()
    window.clipboard_append(content)
    messagebox.showinfo("提示", "已复制到剪贴板")




# 定义清空函数，清空输入文本框和输出文本框中的内容
def clear():
    input_text.delete("1.0", "end")
    output_text.config(state="normal")
    output_text.delete("1.0", "end")
    output_text.config(state="disabled")
    history_text.config(state="normal")
    history_text.delete("1.0", "end")
    history_text.config(state="disabled")


# 定义打开文件函数，选择并读取一个文档文件，并显示在输入文本框中
def open_file():
    # 弹出文件选择对话框，只允许选择txt格式的文件
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

    # 判断文件路径是否为空，如果为空则返回
    if not file_path:
        return

    # 尝试打开并读取文件内容，并显示在输入文本框中
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        input_text.delete("1.0", "end")
        input_text.insert("end", content)

    except Exception as e:
        # 如果发生异常，则弹出提示框
        messagebox.showerror("错误", str(e))


# 定义保存文件函数，将输出文本框中的内容保存到一个文档文件中
def save_file():
    # 获取输出文本框中的内容，并去掉末尾的换行符
    content = output_text.get("1.0", "end").strip()

    # 判断输出是否为空，如果为空则弹出提示框
    if not content:
        messagebox.showinfo("提示", "没有可保存的内容")
        return

    # 弹出文件保存对话框，只允许保存为txt格式的文件
    file_path = filedialog.asksaveasfilename(filetypes=[("Text files", "*.txt")], defaultextension=".txt")

    # 判断文件路径是否为空，如果为空则返回
    if not file_path:
        return

    # 尝试打开并写入文件内容，并弹出提示框
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("提示", "已保存到" + file_path)

    except Exception as e:
        # 如果发生异常，则弹出提示框
        messagebox.showerror("错误", str(e))


# 创建翻译按钮，并绑定翻译函数
translate_button = tk.Button(window, text="翻译", command=translate)
translate_button.place(x=250, y=50, width=100)

# 创建复制按钮，并绑定复制函数
copy_button = tk.Button(window, text="复制结果", command=copy)
copy_button.place(x=650, y=50, width=100)


# 创建清空按钮，并绑定清空函数
clear_button = tk.Button(window, text="清空内容", command=clear)
clear_button.place(x=650, y=580, width=100)

# 创建打开文件按钮，并绑定打开文件函数
open_file_button = tk.Button(window, text="打开文件", command=open_file)
open_file_button.place(x=50, y=580, width=100)

# 创建保存文件按钮，并绑定保存文件函数
save_file_button = tk.Button(window, text="保存文件", command=save_file)
save_file_button.place(x=450, y=580, width=100)

#创建分词按钮
#fenci_button=tk.Button(window,text="分词",command=clear)
#fenci_button.place(x=850, y=50, width=100)

#创建词频按钮
#cipin_button=tk.Button(window,text="词频",command=clear)
#cipin_button.place(x=1050, y=50, width=100)


# 启动主循环，显示窗口
window.mainloop()
