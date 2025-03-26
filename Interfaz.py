from kivy.config import Config
Config.set('input', 'wm_pen', '')
Config.set('input', 'wm_touch', '')
Config.write()

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ObjectProperty

from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.toolbar import MDTopAppBar

import tensorflow as tf
import numpy as np
from PIL import Image, ImageFile
import cv2
import os
import webbrowser
from datetime import datetime

from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

ImageFile.LOAD_TRUNCATED_IMAGES = True
TARGET_SIZE = (160, 160)

try:
    model = tf.keras.models.load_model("optimized_model.h5")
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    MODEL_LOADED = True
except Exception as e:
    print(f"Error al cargar el modelo: {str(e)}")
    model = None
    MODEL_LOADED = False

DIAGNOSIS_DICT = {
    0: "Otra condición",
    1: "Oclusión de rama de vena retiniana",
    2: "Catarata",
    3: "Catarata con polvo del cristalino",
    4: "Catarata con retinopatía no proliferativa moderada",
    5: "Oclusión de arteria retiniana central",
    6: "Oclusión de vena retiniana central",
    7: "Atrofia coriorretiniana",
    8: "Despigmentación del epitelio pigmentario retiniano",
    9: "Retinopatía diabética",
    10: "Retinopatía diabética con degeneración macular seca",
    11: "Drusen",
    12: "Drusen con polvo del cristalino",
    13: "Degeneración macular seca",
    14: "Degeneración macular seca con retinopatía diabética",
    15: "Degeneración macular seca con glaucoma",
    16: "Membrana epirretiniana",
    17: "Membrana epirretiniana sobre la mácula",
    18: "Membrana epirretiniana con polvo del cristalino",
    19: "Glaucoma",
    20: "Glaucoma con retinopatía diabética",
    21: "Glaucoma con retinopatía hipertensiva",
    22: "Glaucoma con membrana epirretiniana macular",
    23: "Glaucoma con retinopatía no proliferativa moderada",
    24: "Retinopatía hipertensiva",
    25: "Mancha láser con retinopatía no proliferativa moderada",
    26: "Polvo del cristalino con drusen",
    27: "Polvo del cristalino con membrana epirretiniana macular",
    28: "Polvo del cristalino con fondo de ojo normal",
    29: "Baja calidad de imagen",
    30: "Membrana epirretiniana macular",
    31: "Membrana epirretiniana macular con polvo del cristalino",
    32: "Membrana epirretiniana macular con retinopatía no proliferativa leve",
    33: "Membrana epirretiniana macular con retinopatía no proliferativa moderada",
    34: "Maculopatía",
    35: "Retinopatía no proliferativa leve",
    36: "Retinopatía no proliferativa leve con membrana epirretiniana",
    37: "Retinopatía no proliferativa leve con retinopatía hipertensiva",
    38: "Retinopatía no proliferativa leve con membrana epirretiniana macular",
    39: "Retinopatía no proliferativa moderada",
    40: "Retinopatía no proliferativa moderada con catarata",
    41: "Retinopatía no proliferativa moderada con membrana epirretiniana",
    42: "Retinopatía no proliferativa moderada con retinopatía hipertensiva",
    43: "Retinopatía no proliferativa moderada con mancha láser",
    44: "Retinopatía no proliferativa moderada con membrana epirretiniana macular",
    45: "Retinopatía no proliferativa moderada con fibras nerviosas mielinizadas",
    46: "Retinopatía no proliferativa moderada con miopía patológica",
    47: "Fibras nerviosas mielinizadas",
    48: "Fondo de ojo normal",
    49: "Fondo de ojo normal con polvo del cristalino",
    50: "Miopía patológica",
    51: "Proliferación del epitelio pigmentario",
    52: "Retinopatía diabética proliferativa",
    53: "Retinopatía diabética proliferativa con retinopatía hipertensiva",
    54: "Opacidad de medios refractivos",
    55: "Pigmentación retiniana",
    56: "Retinitis pigmentosa",
    57: "Retinopatía no proliferativa severa",
    58: "Retinopatía no proliferativa severa con retinopatía hipertensiva",
    59: "Retinopatía diabética proliferativa severa",
    60: "Cambio membranoso moteado",
    61: "Glaucoma sospechoso",
    62: "Glaucoma sospechoso con drusen",
    63: "Glaucoma sospechoso con retinopatía no proliferativa moderada",
    64: "Fondo de ojo teselado",
    65: "Fondo de ojo teselado con atrofia peripapilar",
    66: "Degeneración vítrea",
    67: "Degeneración macular húmeda"
}

def preprocess_image(img_path):
    try:
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            img = img.resize(TARGET_SIZE)
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
    except Exception as e:
        print(f"Error al preprocesar imagen {img_path}: {str(e)}")
        return None

def predict_diagnosis(img_array):
    if not MODEL_LOADED:
        return "Error: Modelo de IA no disponible", 0.0
    
    try:
        if img_array.shape[1:3] != TARGET_SIZE:
            return f"Error: Tamaño de imagen incorrecto. Esperado {TARGET_SIZE}", 0.0
            
        pred = model.predict(img_array)
        pred_class = np.argmax(pred, axis=1)[0]
        diagnosis = DIAGNOSIS_DICT.get(pred_class, "Diagnóstico no disponible")
        confidence = float(np.max(pred)) * 100
        return diagnosis, confidence
    except Exception as e:
        print(f"Error en predicción: {str(e)}")
        return f"Error en diagnóstico: {str(e)}", 0.0

def generate_pdf(diagnosis, confidence, image_path, output_dir="reportes"):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(output_dir, f"diagnostico_{timestamp}.pdf")
        
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "NEURO SOLUTIONS UES", 0, 1, 'C')
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Reporte de Diagnóstico Ocular", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, "Paciente:", 0, 0)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, "Nombre del Paciente", 0, 1)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, "Fecha:", 0, 0)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, datetime.now().strftime('%d/%m/%Y %H:%M'), 0, 1)
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Resultados del Análisis", 0, 1)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 8, f"Diagnóstico: {diagnosis}")
        pdf.multi_cell(0, 8, f"Confianza del modelo: {confidence:.2f}%")
        pdf.ln(10)
        
        fig = plt.figure(figsize=(6, 3))
        plt.barh(['Confianza'], [confidence], color='skyblue')
        plt.xlim(0, 100)
        plt.title('Nivel de Confianza del Diagnóstico')
        canvas = FigureCanvasAgg(fig)
        temp_img = "temp_plot.png"
        canvas.print_figure(temp_img, dpi=100)
        plt.close()
        
        if os.path.exists(image_path):
            pdf.image(image_path, x=10, y=100, w=80)
        pdf.image(temp_img, x=100, y=100, w=100)
        
        pdf.set_y(160)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Recomendaciones:", 0, 1)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 7, "1. Este diagnóstico ha sido generado por inteligencia artificial y debe ser confirmado por un especialista.")
        pdf.multi_cell(0, 7, "2. Se recomienda consultar con un oftalmólogo para una evaluación completa.")
        pdf.multi_cell(0, 7, "3. En caso de emergencia, acuda inmediatamente a un centro médico especializado.")
        pdf.ln(10)
        
        pdf.set_y(-30)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, "NEURO SOLUTIONS UES - Sistema de Diagnóstico Ocular Avanzado", 0, 0, 'C')
        
        pdf.output(pdf_path)
        
        if os.path.exists(temp_img):
            os.remove(temp_img)
            
        return pdf_path
    except Exception as e:
        print(f"Error al generar PDF: {str(e)}")
        return None

class CustomToolbar(MDTopAppBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = self.theme_cls.primary_color
        self.specific_text_color = (1, 1, 1, 1)
        self.elevation = 10
        
    def on_title(self, instance, value):
        if value == "OpticVision AI":
            self.left_action_items = []
        else:
            self.left_action_items = [["arrow-left", lambda x: self.go_back()]]
    
    def go_back(self):
        app = MDApp.get_running_app()
        app.root.current = "main"

class MainScreen(Screen):
    pass

class UploadScreen(Screen):
    file_path = StringProperty("")
    
    def choose_file(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
            ext=[".png", ".jpg", ".jpeg"]
        )
        self.file_manager.show(os.path.expanduser("~"))

    def select_path(self, path):
        if path.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.file_path = path
            self.ids.image_preview.source = path
        else:
            self.show_dialog("Formato no soportado. Use PNG, JPG o JPEG")
        self.exit_manager()

    def exit_manager(self, *args):
        self.file_manager.close()

    def run_diagnosis(self):
        if not self.file_path:
            self.show_dialog("No se ha seleccionado ninguna imagen")
            return
            
        img_array = preprocess_image(self.file_path)
        if img_array is None:
            self.show_dialog("Error al procesar la imagen. Intente con otra.")
            return
            
        diagnosis, confidence = predict_diagnosis(img_array)
        
        if diagnosis.startswith("Error"):
            self.show_dialog(diagnosis)
            return
            
        self.manager.get_screen("result").set_result(diagnosis, confidence, self.file_path)
        self.manager.current = "result"

    def show_dialog(self, text):
        dialog = MDDialog(
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

class CameraScreen(Screen):
    image_path = StringProperty("")
    
    def on_enter(self):
        self.ids.camera_view.play = True
    
    def on_leave(self):
        self.ids.camera_view.play = False
    
    def capture_image(self):
        camera = self.ids.camera_view
        if not camera.play:
            self.show_dialog("La cámara no está activa")
            return
            
        texture = camera.texture
        if not texture:
            self.show_dialog("No se pudo capturar la imagen")
            return
            
        try:
            size = texture.size
            pixels = texture.pixels
            arr = np.frombuffer(pixels, np.uint8)
            arr = arr.reshape(size[1], size[0], 4)
            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.image_path = f"captured_{timestamp}.png"
            cv2.imwrite(self.image_path, cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
            
            img_array = preprocess_image(self.image_path)
            if img_array is None:
                self.show_dialog("Error al procesar imagen capturada")
                return
                
            diagnosis, confidence = predict_diagnosis(img_array)
            
            if diagnosis.startswith("Error"):
                self.show_dialog(diagnosis)
                return
                
            self.manager.get_screen("result").set_result(diagnosis, confidence, self.image_path)
            self.manager.current = "result"
            
        except Exception as e:
            self.show_dialog(f"Error al capturar imagen: {str(e)}")

    def show_dialog(self, text):
        dialog = MDDialog(
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

class ResultScreen(Screen):
    diagnosis_text = StringProperty("")
    confidence_text = StringProperty("")
    image_path = StringProperty("")
    
    def set_result(self, diagnosis, confidence, image_path):
        self.diagnosis_text = diagnosis
        self.confidence_text = f"Confianza: {confidence:.2f}%"
        self.image_path = image_path
    
    def generate_report(self):
        pdf_path = generate_pdf(
            self.diagnosis_text, 
            float(self.confidence_text.split(": ")[1].replace("%", "")), 
            self.image_path
        )
        
        if pdf_path:
            dialog = MDDialog(
                title="Reporte Generado",
                text=f"PDF guardado en:\n{pdf_path}",
                buttons=[
                    MDRaisedButton(
                        text="Abrir PDF",
                        on_release=lambda x: self.open_pdf(pdf_path, dialog)
                    ),
                    MDFlatButton(
                        text="Cerrar",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
        else:
            self.show_dialog("Error al generar el reporte PDF")

    def open_pdf(self, pdf_path, dialog):
        try:
            webbrowser.open(pdf_path)
        except Exception as e:
            self.show_dialog(f"No se pudo abrir el PDF: {str(e)}")
        dialog.dismiss()

    def show_dialog(self, text):
        dialog = MDDialog(
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

class WindowManager(ScreenManager):
    pass

Builder.load_string('''
#:import WindowManager __main__.WindowManager
#:import CustomToolbar __main__.CustomToolbar

<CustomToolbar>:
    title: "OpticVision AI"
    right_action_items: [["information-outline", lambda x: app.show_about()]]

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"
        CustomToolbar:
            title: "OpticVision AI"
        BoxLayout:
            orientation: "vertical"
            padding: dp(40)
            spacing: dp(30)
            MDRaisedButton:
                text: "Subir Imagen"
                pos_hint: {"center_x": 0.5}
                size_hint: 0.8, None
                height: dp(50)
                on_release: app.root.current = "upload"
            MDRaisedButton:
                text: "Scan en Tiempo Real"
                pos_hint: {"center_x": 0.5}
                size_hint: 0.8, None
                height: dp(50)
                on_release: app.root.current = "camera"
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            MDLabel:
                text: "NEURO SOLUTIONS UES"
                halign: "center"
                theme_text_color: "Secondary"
                font_style: "Caption"

<UploadScreen>:
    name: "upload"
    BoxLayout:
        orientation: "vertical"
        CustomToolbar:
            title: "Subir Imagen"
        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding: dp(20)
                spacing: dp(20)
                size_hint_y: None
                height: self.minimum_height
                MDRaisedButton:
                    text: "Seleccionar Imagen"
                    size_hint: 1, None
                    height: dp(50)
                    on_release: root.choose_file()
                Image:
                    id: image_preview
                    source: ""
                    allow_stretch: True
                    keep_ratio: True
                    size_hint_y: None
                    height: dp(300)
        MDRaisedButton:
            text: "Realizar Diagnóstico"
            pos_hint: {"center_x": 0.5}
            size_hint: 0.8, None
            height: dp(50)
            on_release: root.run_diagnosis()
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            MDLabel:
                text: "NEURO SOLUTIONS UES"
                halign: "center"
                theme_text_color: "Secondary"
                font_style: "Caption"

<CameraScreen>:
    name: "camera"
    BoxLayout:
        orientation: "vertical"
        CustomToolbar:
            title: "Escaneo en Tiempo Real"
        BoxLayout:
            Camera:
                id: camera_view
                resolution: (640, 480)
                play: False
        MDRaisedButton:
            text: "Capturar Imagen"
            pos_hint: {"center_x": 0.5}
            size_hint: 0.8, None
            height: dp(50)
            on_release: root.capture_image()
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            MDLabel:
                text: "NEURO SOLUTIONS UES"
                halign: "center"
                theme_text_color: "Secondary"
                font_style: "Caption"

<ResultScreen>:
    name: "result"
    BoxLayout:
        orientation: "vertical"
        CustomToolbar:
            title: "Resultado"
        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding: dp(20)
                spacing: dp(20)
                size_hint_y: None
                height: self.minimum_height
                MDLabel:
                    text: "Diagnóstico:"
                    halign: "center"
                    font_style: "H5"
                MDLabel:
                    text: root.diagnosis_text
                    halign: "center"
                    theme_text_color: "Primary"
                    size_hint_y: None
                    height: self.texture_size[1]
                MDLabel:
                    text: root.confidence_text
                    halign: "center"
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    height: dp(30)
                Image:
                    source: root.image_path
                    allow_stretch: True
                    keep_ratio: True
                    size_hint_y: None
                    height: dp(300)
        MDRaisedButton:
            text: "Generar PDF"
            pos_hint: {"center_x": 0.5}
            size_hint: 0.8, None
            height: dp(50)
            on_release: root.generate_report()
        BoxLayout:
            size_hint_y: None
            height: dp(30)
            MDLabel:
                text: "NEURO SOLUTIONS UES"
                halign: "center"
                theme_text_color: "Secondary"
                font_style: "Caption"
''')

class OcularApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        Window.size = (400, 700)
        
        if not MODEL_LOADED:
            from kivy.clock import Clock
            Clock.schedule_once(self.show_model_error)
            
        sm = WindowManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(UploadScreen(name='upload'))
        sm.add_widget(CameraScreen(name='camera'))
        sm.add_widget(ResultScreen(name='result'))
        
        return sm
    
    def show_model_error(self, dt):
        dialog = MDDialog(
            title="Error Importante",
            text="El modelo de IA no se cargó correctamente. La aplicación no funcionará completamente.",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def show_about(self):
        dialog = MDDialog(
            title="Acerca de",
            text="OpticVision AI v1.0\n\nSistema de diagnóstico ocular asistido por IA\n\nNEURO SOLUTIONS UES",
            buttons=[MDFlatButton(text="Cerrar", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def on_stop(self):
        for file in os.listdir():
            if file.startswith("captured_") and file.endswith(".png"):
                try:
                    os.remove(file)
                except:
                    pass

if __name__ == '__main__':
    OcularApp().run()
