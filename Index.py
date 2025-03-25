from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.image import Image
import webbrowser

kv = '''
ScreenManager:
    LoadingScreen:
    MainScreen:

<LoadingScreen>:
    name: "loading"
    MDBoxLayout:
        orientation: "vertical"
        MDLabel:
            id: loading_label
            text: "Designed by NeuroSolutions UES"
            halign: "center"
            font_style: "H5"

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "OpticVision AI"
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(30)
            padding: dp(30)
            Image:
                source: "Iconos\Scan.png"
                allow_stretch: True
                on_touch_down: app.open_scan()
            MDLabel:
                text: "Escanear"
                halign: "center"
            Image:
                source: "Iconos\chatbot_icon.png"
                allow_stretch: True
                on_touch_down: app.open_chatbot()
            MDLabel:
                text: "Chatbot"
                halign: "center"
            Image:
                source: "Iconos\history_icon.png"
                allow_stretch: True
                on_touch_down: app.open_history()
            MDLabel:
                text: "Historial"
                halign: "center"
            Image:
                source: "Iconos\icon_tutorial.png"
                allow_stretch: True
                on_touch_down: app.play_tutorial()
            MDLabel:
                text: "Tutorial"
                halign: "center"
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: 0, 0, 0, 1
            MDLabel:
                text: "NeuroSolutions UES"
                halign: "center"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
'''

class LoadingScreen(Screen):
    def on_enter(self):
        self.loading_phases = [
            "Designed by NeuroSolutions UES",
            "OpticVision AI",
            "Samsung Innovation Campus"
        ]
        self.index = 0
        Clock.schedule_interval(self.update_label, 2)

    def update_label(self, dt):
        if self.index < len(self.loading_phases):
            self.ids.loading_label.text = self.loading_phases[self.index]
            self.index += 1
        else:
            Clock.unschedule(self.update_label)
            self.manager.current = "main"

class MainScreen(Screen):
    pass

class OpticVisionApp(MDApp):
    def build(self):
        return Builder.load_string(kv)

    def open_scan(self):
        webbrowser.open("scan.py")

    def open_chatbot(self):
        webbrowser.open("chatbot.py")

    def open_history(self):
        webbrowser.open("history.py")

    def play_tutorial(self):
        webbrowser.open("tutorial.mp4")

if __name__ == '__main__':
    OpticVisionApp().run()
