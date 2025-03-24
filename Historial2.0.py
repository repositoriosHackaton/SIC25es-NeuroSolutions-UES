import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class MedicalHistoryApp:
    def __init__(self):
        
        self.conn = sqlite3.connect('medical_history.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER,
            contrasena TEXT NOT NULL
        )''')

        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Enfermedades (
            id_enfermedad INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        )''')

       
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Historial (
            id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            id_enfermedad INTEGER,
            fecha_escaneo DATE,
            imagen TEXT,
            diagnostico TEXT,
            avance REAL,
            FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
            FOREIGN KEY (id_enfermedad) REFERENCES Enfermedades(id_enfermedad)
        )''')

        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Informacion (
            id_informacion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            id_enfermedad INTEGER,
            historial_medico TEXT,
            FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
            FOREIGN KEY (id_enfermedad) REFERENCES Enfermedades(id_enfermedad)
        )''')

        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Avance_enfermedad (
            id_avance INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            id_enfermedad INTEGER,
            porcentaje REAL,
            FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
            FOREIGN KEY (id_enfermedad) REFERENCES Enfermedades(id_enfermedad)
        )''')

        self.conn.commit()

    def registrar_usuario(self, nombre, edad, contrasena):
        """Registrar un nuevo usuario"""
        self.cursor.execute('''
        INSERT INTO Usuario (nombre, edad, contrasena) 
        VALUES (?, ?, ?)
        ''', (nombre, edad, contrasena))
        self.conn.commit()
        return self.cursor.lastrowid

    def registrar_enfermedad(self, nombre, descripcion):
        """Registrar una nueva enfermedad"""
        self.cursor.execute('''
        INSERT INTO Enfermedades (nombre, descripcion) 
        VALUES (?, ?)
        ''', (nombre, descripcion))
        self.conn.commit()
        return self.cursor.lastrowid

    def registrar_historial(self, id_usuario, id_enfermedad, fecha_escaneo, imagen, diagnostico, avance):
        """Registrar un nuevo historial médico"""
        self.cursor.execute('''
        INSERT INTO Historial (id_usuario, id_enfermedad, fecha_escaneo, imagen, diagnostico, avance) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (id_usuario, id_enfermedad, fecha_escaneo, imagen, diagnostico, avance))
        self.conn.commit()
        return self.cursor.lastrowid

    def generar_informe_pdf(self, id_usuario=None):
        """Generar informe PDF de historial médico"""
        archivo_pdf = "informe_historial_medico.pdf"
        c = canvas.Canvas(archivo_pdf, pagesize=letter)
        
        
        if id_usuario:
            self.cursor.execute('''
            SELECT u.nombre, e.nombre, h.fecha_escaneo, h.diagnostico, h.avance
            FROM Historial h
            JOIN Usuario u ON h.id_usuario = u.id_usuario
            JOIN Enfermedades e ON h.id_enfermedad = e.id_enfermedad
            WHERE h.id_usuario = ?
            ''', (id_usuario,))
        else:
            self.cursor.execute('''
            SELECT u.nombre, e.nombre, h.fecha_escaneo, h.diagnostico, h.avance
            FROM Historial h
            JOIN Usuario u ON h.id_usuario = u.id_usuario
            JOIN Enfermedades e ON h.id_enfermedad = e.id_enfermedad
            ''')
        
        historial = self.cursor.fetchall()
        
        
        c.drawString(100, 750, "Informe de Historial Médico")
        c.drawString(100, 730, "==========================")
        
        y = 700
        for i, (nombre_usuario, nombre_enfermedad, fecha, diagnostico, avance) in enumerate(historial, 1):
            c.drawString(100, y, f"{i}. Paciente: {nombre_usuario}")
            c.drawString(100, y-20, f"   Enfermedad: {nombre_enfermedad}")
            c.drawString(100, y-40, f"   Fecha: {fecha}")
            c.drawString(100, y-60, f"   Diagnóstico: {diagnostico}")
            c.drawString(100, y-80, f"   Avance: {avance}%")
            y -= 100
        
        c.save()
        print(f"Informe PDF generado: {archivo_pdf}")

    def mostrar_historial(self, id_usuario=None):
        """Mostrar historial médico"""
        if id_usuario:
            self.cursor.execute('''
            SELECT u.nombre, e.nombre, h.fecha_escaneo, h.diagnostico, h.avance
            FROM Historial h
            JOIN Usuario u ON h.id_usuario = u.id_usuario
            JOIN Enfermedades e ON h.id_enfermedad = e.id_enfermedad
            WHERE h.id_usuario = ?
            ''', (id_usuario,))
        else:
            self.cursor.execute('''
            SELECT u.nombre, e.nombre, h.fecha_escaneo, h.diagnostico, h.avance
            FROM Historial h
            JOIN Usuario u ON h.id_usuario = u.id_usuario
            JOIN Enfermedades e ON h.id_enfermedad = e.id_enfermedad
            ''')
        
        historial = self.cursor.fetchall()
        
        print("Historial Médico:")
        for i, (nombre_usuario, nombre_enfermedad, fecha, diagnostico, avance) in enumerate(historial, 1):
            print(f"{i}. Paciente: {nombre_usuario}")
            print(f"   Enfermedad: {nombre_enfermedad}")
            print(f"   Fecha: {fecha}")
            print(f"   Diagnóstico: {diagnostico}")
            print(f"   Avance: {avance}%")
            print()

    def ejecutar(self):
        while True:
            print("\nOpciones:")
            print("1. Registrar Usuario")
            print("2. Registrar Enfermedad")
            print("3. Registrar Historial Médico")
            print("4. Ver Historial Médico")
            print("5. Generar Informe PDF")
            print("6. Salir")
            opcion = input("Selecciona una opción: ")

            if opcion == "1":
                nombre = input("Nombre del usuario: ")
                edad = int(input("Edad: "))
                contrasena = input("Contraseña: ")
                self.registrar_usuario(nombre, edad, contrasena)
                print("Usuario registrado exitosamente.")

            elif opcion == "2":
                nombre = input("Nombre de la enfermedad: ")
                descripcion = input("Descripción: ")
                self.registrar_enfermedad(nombre, descripcion)
                print("Enfermedad registrada exitosamente.")

            elif opcion == "3":
                id_usuario = int(input("ID de usuario: "))
                id_enfermedad = int(input("ID de enfermedad: "))
                fecha_escaneo = input("Fecha de escaneo (YYYY-MM-DD): ")
                imagen = input("Ruta de imagen (opcional): ")
                diagnostico = input("Diagnóstico: ")
                avance = float(input("Porcentaje de avance: "))
                self.registrar_historial(id_usuario, id_enfermedad, fecha_escaneo, imagen, diagnostico, avance)
                print("Historial médico registrado exitosamente.")

            elif opcion == "4":
                id_usuario = input("ID de usuario (dejar en blanco para ver todos): ")
                if id_usuario:
                    self.mostrar_historial(int(id_usuario))
                else:
                    self.mostrar_historial()

            elif opcion == "5":
                id_usuario = input("ID de usuario (dejar en blanco para informe general): ")
                if id_usuario:
                    self.generar_informe_pdf(int(id_usuario))
                else:
                    self.generar_informe_pdf()

            elif opcion == "6":
                print("Saliendo del programa.")
                self.conn.close()
                break

            else:
                print("Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    app = MedicalHistoryApp()
    app.ejecutar()