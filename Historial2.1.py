from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


import os


Window.size = (400, 700)
Window.clearcolor = (1, 1, 1, 1)  


SCAN_HISTORY_DATA = [
    
]

class PDFDownloadPopup(Popup):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.title = "Descargar PDF"
        self.size_hint = (0.8, 0.4)
        
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        
        self.path_input = TextInput(
            text=os.path.expanduser('~/Downloads/historial_opticvision.pdf'),
            multiline=False
        )
        layout.add_widget(Label(text="Ruta de guardado:"))
        layout.add_widget(self.path_input)
        
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        cancel_btn = Button(
            text='Cancelar', 
            on_press=self.dismiss,
            background_color=get_color_from_hex('#FF0000')
        )
        
        download_btn = Button(
            text='Descargar', 
            on_press=self.generate_pdf,
            background_color=get_color_from_hex('#2196F3')
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(download_btn)
        
        layout.add_widget(btn_layout)
        
        self.content = layout
        
        
        self.scan_history_data = data

    def generate_pdf(self, *args):
        try:
            
            pdf_data = [["ID", "Usuario", "Condición", "Fecha", "Diagnóstico IA", "Confianza IA", "Avance"]]
            
            for entry in self.scan_history_data:
                pdf_data.append([
                    entry.get("ID", ""),
                    entry.get("Usuario", ""),
                    entry.get("Condición", ""),
                    entry.get("Fecha", ""),
                    entry.get("DiagnósticoIA", ""),
                    entry.get("ConfianzaIA", ""),
                    entry.get("Avance", "")
                ])
            
           
            pdf_path = self.path_input.text
            
            
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            table = Table(pdf_data)
            
            
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.blue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            
            
            elements = [table]
            doc.build(elements)
            
            
            success_popup = Popup(
                title='Descarga Exitosa', 
                content=Label(text=f'PDF guardado en:\n{pdf_path}'),
                size_hint=(0.8, 0.3)
            )
            success_popup.open()
            
           
            self.dismiss()
        
        except Exception as e:
            
            error_popup = Popup(
                title='Error', 
                content=Label(text=f'Error al generar PDF:\n{str(e)}'),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()

class ColoredBoxLayout(BoxLayout):
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        if bg_color:
            with self.canvas.before:
                Color(*bg_color)
                self.rect = Rectangle(pos=self.pos, size=self.size)
            
            self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size

class HistorialApp(App):
    def build(self):
       
        main_layout = BoxLayout(orientation='vertical')
        
        
        header = ColoredBoxLayout(
            bg_color=get_color_from_hex('#2196F3'),
            size_hint_y=None, 
            height=60,
            orientation='horizontal'
        )
        
        
        back_btn = Button(
            text='← Atrás', 
            background_color=get_color_from_hex('#2196F3'),
            color=(1,1,1,1),
            size_hint_x=0.3,
            border=(0,0,0,0)  
        )
        header.add_widget(back_btn)
        
        
        app_title = Label(
            text='OpticVision AI', 
            color=(1,1,1,1),
            font_size='18sp',
            bold=True,
            size_hint_x=0.7
        )
        header.add_widget(app_title)
        
        main_layout.add_widget(header)
        
       
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        
        title = Label(
            text='Historial de Análisis AI', 
            font_size='20sp',
            color=(0,0,0,1),
            size_hint_y=None,
            height=50
        )
        content_layout.add_widget(title)
        
        
        table_header = ColoredBoxLayout(
            bg_color=get_color_from_hex('#2196F3'),
            size_hint_y=None, 
            height=50
        )
        
        
        header_texts = ["ID", "Usuario", "Condición", "Fecha", "Diagnóstico IA", "Confianza IA", "Avance"]
        for text in header_texts:
            label = Label(
                text=text, 
                color=(1,1,1,1),
                font_size='12sp',
                bold=True
            )
            table_header.add_widget(label)
        
        content_layout.add_widget(table_header)
        
        
        scroll_view = ScrollView()
        
        
        data_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        data_layout.bind(minimum_height=data_layout.setter('height'))
        
        
        for entry in SCAN_HISTORY_DATA:
            row = BoxLayout(size_hint_y=None, height=40)
            row_data = [
                entry["ID"], 
                entry["Usuario"], 
                entry["Condición"], 
                entry["Fecha"], 
                entry["DiagnósticoIA"], 
                entry["ConfianzaIA"], 
                entry["Avance"]
            ]
            for data in row_data:
                label = Label(
                    text=str(data), 
                    color=(0,0,0,1),
                    font_size='12sp'
                )
                row.add_widget(label)
            data_layout.add_widget(row)
        
        
        scroll_view.add_widget(data_layout)
        content_layout.add_widget(scroll_view)
        
        
        bottom_section = BoxLayout(orientation='vertical', size_hint_y=None, height=100)
        
        
        bottom_section.add_widget(Label())
        
        
        pdf_btn = Button(
            text='📄 Descargar PDF', 
            background_color=get_color_from_hex('#2196F3'),
            color=(1,1,1,1),
            size_hint=(None, None),
            height=50,
            width=200,
            pos_hint={'center_x': 0.5}
        )
        pdf_btn.bind(on_press=self.open_pdf_download)
        bottom_section.add_widget(pdf_btn)
        
        
        bottom_section.add_widget(Label())
        
        
        main_layout.add_widget(content_layout)
        main_layout.add_widget(bottom_section)
        
        return main_layout
    
    def open_pdf_download(self, *args):
        
        pdf_popup = PDFDownloadPopup(SCAN_HISTORY_DATA)
        pdf_popup.open()

if __name__ == '__main__':
    HistorialApp().run()