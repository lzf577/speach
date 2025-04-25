from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Window
import requests
import threading
import time
import os

Window.softinput_mode = 'below_target'

KV = '''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: 'main'
    text_input: text_input
    speaker_spinner: speaker_spinner
    batch_input: batch_input
    result_label: result_label

    MDBoxLayout:
        orientation: 'vertical'
        padding: "10dp"
        spacing: "10dp"

        MDTopAppBar:
            title: "文字转语音 (安卓版)"
            elevation: 4

        MDTextField:
            id: text_input
            hint_text: "输入多段文本，每段换行"
            multiline: True
            mode: "rectangle"

        MDSpinner:
            id: speaker_spinner
            text: "加载中..."
            size_hint_y: None
            height: "48dp"

        MDTextField:
            id: batch_input
            hint_text: "批量大小 (默认 4)"
            text: "4"
            input_filter: 'int'
            mode: "rectangle"

        MDRaisedButton:
            text: "开始转换"
            on_release: app.start_conversion()

        MDLabel:
            id: result_label
            text: ""
            halign: "center"
'''

class MainScreen(Screen):
    pass

class TTSApp(MDApp):
    save_dir = "/sdcard/Download"  # 安卓设备的保存路径

    def build(self):
        self.title = "批量文字转语音"
        self.theme_cls.primary_palette = "Teal"
        screen = Builder.load_string(KV)
        self.get_speakers_async()
        return screen

    def get_speakers_async(self):
        def worker():
            try:
                resp = requests.get("http://192.168.41.111:7870/v1/speakers/list")  # Android 模拟器用 10.0.2.2
                data = resp.json()
                speaker_names = [
                    sp.get("data", {}).get("meta", {}).get("data", {}).get("name", "未知")
                    for sp in data.get("data", [])
                ]
                self.root.get_screen('main').speaker_spinner.values = speaker_names
                self.root.get_screen('main').speaker_spinner.text = speaker_names[0] if speaker_names else "无"
            except Exception as e:
                self.root.get_screen('main').speaker_spinner.text = "获取失败"
        threading.Thread(target=worker, daemon=True).start()

    def start_conversion(self):
        screen = self.root.get_screen('main')
        text = screen.text_input.text.strip()
        if not text:
            screen.result_label.text = "请输入文本。"
            return

        try:
            batch_size = int(screen.batch_input.text)
        except ValueError:
            batch_size = 4

        speaker = screen.speaker_spinner.text
        paragraphs = [p.strip() for p in text.splitlines() if p.strip()]

        def process():
            for i, para in enumerate(paragraphs):
                self.send_request(para, speaker, batch_size, i)
            screen.result_label.text = f"完成，生成 {len(paragraphs)} 段音频。"

        threading.Thread(target=process, daemon=True).start()
        screen.result_label.text = "正在生成..."

    def send_request(self, text, speaker_name, batch_size, index):
        payload = {
            "text": text,
            "spk": {"from_spk_name": speaker_name},
            "tts": {
                "sample_rate": 22050,
                "output_format": "wav",
                "batch_size": batch_size
            }
        }
        try:
            resp = requests.post("http://192.168.41.111:7870/v2/tts", json=payload)
            if resp.status_code == 200:
                filename = f"tts_output_{int(time.time())}_{index}.wav"
                with open(os.path.join(self.save_dir, filename), "wb") as f:
                    f.write(resp.content)
        except Exception as e:
            print("请求错误：", e)

if __name__ == "__main__":
    TTSApp().run()