import tkinter as tk
from tkinter import ttk, filedialog
import threading
import requests
import json
import time
import os

# API 地址
api_url = "http://localhost:7870/v2/tts"
speakers_api_url = "http://localhost:7870/v1/speakers/list"

# 获取 speakers 列表
def get_speakers():
    try:
        response = requests.get(speakers_api_url)
        if response.status_code == 200:
            speakers_data = response.json()
            speakers = []
            for speaker in speakers_data.get("data", []):
                meta_data = speaker.get("data", {}).get("meta", {}).get("data", {})
                name = meta_data.get("name")
                if name:
                    speakers.append(name)
            return speakers
    except Exception as e:
        print("获取 speakers 异常:", e)
    return []

# 发送一个段落的 TTS 请求
def send_paragraph_request(text, speaker_name, save_dir, index):
    params = {
        "text": text,
        "spk": {"from_spk_name": speaker_name},
        "tts": {
            "sample_rate": 44100,  # 提高采样率到44100 Hz
            "output_format": "wav",  # 保持wav格式，以避免压缩损失
            "bitrate": "192k"  # 如果有bitrate选项，增加比特率以提高音质
        }
    }
    try:
        response = requests.post(api_url, json=params)
        if response.status_code == 200:
            timestamp = int(time.time())
            filename = f"output_{timestamp}_{index+1}.wav"
            output_path = os.path.join(save_dir, filename)
            with open(output_path, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print("请求失败:", response.status_code, response.text)
            return None
    except Exception as e:
        print("发送请求异常:", e)
        return None

# 后台线程：每段文字一个音频
def process_text_in_thread(text, speaker_name, result_label, convert_button, save_dir):
    paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
    results = []
    for i, para in enumerate(paragraphs):
        filename = send_paragraph_request(para, speaker_name, save_dir, i)
        if filename:
            results.append(filename)

    if results:
        result_label.config(text=f"完成！生成 {len(results)} 个音频。")
    else:
        result_label.config(text="生成失败。")

# 异步获取发音人列表
def fetch_speakers_async(app):
    speakers = get_speakers()
    if not speakers:
        speakers = ["没有可用的发音人"]
    app.speakers = speakers
    app.speaker_combobox['values'] = speakers
    app.speaker_combobox.set(speakers[0] if speakers else "没有可用的发音人")

# GUI 窗口类
class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文字转语音")
        self.root.geometry("800x600")
        self.speakers = []
        self.save_dir = os.getcwd()

        # 文本输入
        self.text_label = tk.Label(root, text="请输入文本（每段一行）：", font=("Arial", 14))
        self.text_label.pack(pady=10)

        self.text_entry = tk.Text(root, height=12, font=("Arial", 14))
        self.text_entry.pack(pady=10, fill=tk.BOTH, expand=True)
        self.text_entry.insert(tk.END, "第一段文本\n空行\n第二段文本\n空行\n第三段文本")

        # 发音人选择
        self.speaker_label = tk.Label(root, text="选择发音人：", font=("Arial", 12))
        self.speaker_label.pack(pady=5)

        self.speaker_combobox = ttk.Combobox(root, values=self.speakers, font=("Arial", 12))
        self.speaker_combobox.pack()

        # 保存路径选择
        self.path_button = tk.Button(root, text="选择保存路径", font=("Arial", 12), command=self.select_save_dir)
        self.path_button.pack(pady=5)

        # 按钮框
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.convert_button = tk.Button(button_frame, text="开始转换", font=("Arial", 14), command=self.convert_text)
        self.convert_button.pack(side=tk.LEFT, padx=10)

        self.clear_button = tk.Button(button_frame, text="清除文本", font=("Arial", 14), command=self.clear_text)
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # 结果提示
        self.result_label = tk.Label(root, text="", font=("Arial", 14), fg="green")
        self.result_label.pack(pady=20)

        # 异步加载 speakers
        threading.Thread(target=fetch_speakers_async, args=(self,), daemon=True).start()

    def select_save_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.save_dir = path

    def convert_text(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        if not text:
            self.result_label.config(text="请输入文本。")
            return

        speaker = self.speaker_combobox.get()
        self.result_label.config(text="正在处理，请稍等...")

        # 按钮立刻恢复
        self.convert_button.config(state=tk.NORMAL)

        # 后台执行转换操作，不阻塞主线程
        threading.Thread(
            target=process_text_in_thread,
            args=(text, speaker, self.result_label, self.convert_button, self.save_dir),
            daemon=True
        ).start()

    def clear_text(self):
        self.text_entry.delete("1.0", tk.END)
        self.result_label.config(text="")

# 运行程序
if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
