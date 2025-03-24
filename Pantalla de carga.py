from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Image(source="logo.png"))
        Clock.schedule_once(self.switch_to_main, 3)

    def switch_to_main(self, dt):
        self.manager.current = "menu"
        
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")

        buttons = ["Escaneo IA", "Historial", "Chatbot"]
        for btn_text in buttons:
            btn = Button(text=btn_text, size_hint=(1, 0.2))
            layout.add_widget(btn)

#Aún me falta agregar parte del menú.
#El avance no fue tanto debido a contratiempos y cambios en el código.