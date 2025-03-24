from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

class RegistroForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)

        # Fondo del formulario
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Color neutro
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)

        # Nombre
        self.add_widget(Label(text="Nombre:", size_hint_y=None, height=40, color=[0, 0, 0, 1], font_size=18))
        self.nombre_input = TextInput(hint_text="Ingresa tu nombre", size_hint_y=None, height=40)
        self.add_widget(self.nombre_input)

        # Edad
        self.add_widget(Label(text="Edad:", size_hint_y=None, height=40, color=[0, 0, 0, 1], font_size=18))
        self.edad_input = TextInput(hint_text="Ingresa tu edad (solo números)", input_filter="int", size_hint_y=None, height=40)
        self.add_widget(self.edad_input)

        # Historial Médico
        self.add_widget(Label(text="Historial Médico:", size_hint_y=None, height=40, color=[0, 0, 0, 1], font_size=18))
        self.historial_input = TextInput(hint_text="Describe tu historial médico", size_hint_y=None, height=80, multiline=True)
        self.add_widget(self.historial_input)

        # Botón Registrar
        self.submit_button = Button(text="Registrar", size_hint_y=None, height=50, background_color=[0.2, 0.5, 0.8, 1], color=[1, 1, 1, 1], font_size=18)
        self.submit_button.bind(on_press=self.registrar_datos)
        self.add_widget(self.submit_button)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def registrar_datos(self, instance):
        nombre = self.nombre_input.text.strip()
        edad = self.edad_input.text.strip()
        historial = self.historial_input.text.strip()

        if not nombre or not edad or not historial:
            self.mostrar_popup("Error", "Todos los campos son obligatorios.")
            return

        if not (0 <= int(edad) <= 100):
            self.mostrar_popup("Error", "La edad debe estar entre 0 y 100.")
            return

        self.mostrar_popup("Éxito", "Datos registrados correctamente.")
        self.nombre_input.text = ""
        self.edad_input.text = ""
        self.historial_input.text = ""

    def mostrar_popup(self, titulo, mensaje):
        popup = Popup(title=titulo, content=Label(text=mensaje), size_hint=(0.8, 0.4), auto_dismiss=True)
        popup.open()

class RegistroApp(App):
    def build(self):
        return RegistroForm()

if __name__ == "__main__":
    RegistroApp().run()