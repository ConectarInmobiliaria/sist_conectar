# components/date_picker.py - Selector de Fechas con Calendario
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime


class DatePicker(ctk.CTkFrame):
    """Widget de selección de fecha con calendario emergente"""
    
    def __init__(self, parent, label_text="Fecha", default_date=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.label_text = label_text
        self.selected_date = default_date if default_date else datetime.now()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crea los widgets del selector"""
        # Frame contenedor
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", pady=6)
        
        # Label
        self.label = ctk.CTkLabel(
            container,
            text=self.label_text,
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        )
        self.label.pack(side="left", padx=5)
        
        # Entry para mostrar la fecha
        self.date_entry = ctk.CTkEntry(
            container,
            width=240,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.date_entry.pack(side="left", padx=5)
        
        # Botón de calendario
        self.calendar_button = ctk.CTkButton(
            container,
            text="📅",
            width=50,
            height=35,
            command=self.open_calendar,
            font=ctk.CTkFont(size=16)
        )
        self.calendar_button.pack(side="left", padx=5)
        
        # Actualizar entry con fecha inicial
        self.update_entry()
    
    def update_entry(self):
        """Actualiza el entry con la fecha seleccionada en formato DD/MM/AAAA"""
        self.date_entry.delete(0, 'end')
        fecha_formateada = self.selected_date.strftime('%d/%m/%Y')
        self.date_entry.insert(0, fecha_formateada)
    
    def open_calendar(self):
        """Abre la ventana del calendario"""
        CalendarWindow(self, self.selected_date, self.on_date_selected)
    
    def on_date_selected(self, date):
        """Callback cuando se selecciona una fecha del calendario"""
        self.selected_date = date
        self.update_entry()
    
    def get_date(self):
        """Obtiene la fecha en formato YYYY-MM-DD (para base de datos)"""
        return self.selected_date.strftime('%Y-%m-%d')
    
    def get_date_formatted(self):
        """Obtiene la fecha en formato DD/MM/YYYY (para mostrar)"""
        return self.selected_date.strftime('%d/%m/%Y')
    
    def set_date(self, date_string):
        """
        Establece la fecha desde un string
        Acepta formatos: YYYY-MM-DD o DD/MM/YYYY
        """
        try:
            # Intentar formato YYYY-MM-DD (de base de datos)
            if '-' in date_string:
                self.selected_date = datetime.strptime(date_string, '%Y-%m-%d')
            # Intentar formato DD/MM/YYYY
            elif '/' in date_string:
                self.selected_date = datetime.strptime(date_string, '%d/%m/%Y')
            else:
                return False
            
            self.update_entry()
            return True
        except ValueError:
            return False
    
    def get_date_object(self):
        """Retorna el objeto datetime"""
        return self.selected_date


class CalendarWindow(ctk.CTkToplevel):
    """Ventana emergente con calendario"""
    
    def __init__(self, parent, initial_date, callback):
        super().__init__(parent)
        
        self.callback = callback
        self.selected_date = initial_date
        
        # Configurar ventana
        self.title("Seleccionar Fecha")
        self.geometry("350x400")
        self.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Crear widgets
        self.create_widgets()
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        self.focus()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea los widgets del calendario"""
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="📅 Seleccionar Fecha",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(0, 15))
        
        # Calendario
        self.calendar = Calendar(
            main_frame,
            selectmode='day',
            year=self.selected_date.year,
            month=self.selected_date.month,
            day=self.selected_date.day,
            date_pattern='dd/mm/yyyy',
            background='#2b5797',
            foreground='white',
            selectbackground='#1abc9c',
            selectforeground='white',
            normalbackground='white',
            normalforeground='black',
            headersbackground='#2b5797',
            headersforeground='white',
            weekendbackground='#f0f0f0',
            weekendforeground='black',
            othermonthbackground='#e0e0e0',
            othermonthforeground='gray'
        )
        self.calendar.pack(pady=10)
        
        # Frame de botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        # Botón Hoy
        ctk.CTkButton(
            button_frame,
            text="📍 Hoy",
            command=self.select_today,
            width=100,
            height=35,
            fg_color="#3498db"
        ).pack(side="left", padx=5)
        
        # Botón Aceptar
        ctk.CTkButton(
            button_frame,
            text="✓ Aceptar",
            command=self.accept,
            width=100,
            height=35,
            fg_color="#2ecc71"
        ).pack(side="left", padx=5)
        
        # Botón Cancelar
        ctk.CTkButton(
            button_frame,
            text="✗ Cancelar",
            command=self.destroy,
            width=100,
            height=35,
            fg_color="#e74c3c"
        ).pack(side="left", padx=5)
    
    def select_today(self):
        """Selecciona la fecha de hoy"""
        hoy = datetime.now()
        self.calendar.selection_set(hoy)
    
    def accept(self):
        """Acepta la fecha seleccionada"""
        fecha_seleccionada_str = self.calendar.get_date()
        
        try:
            # El calendario devuelve en formato DD/MM/YYYY
            fecha = datetime.strptime(fecha_seleccionada_str, '%d/%m/%Y')
            
            # Llamar al callback con la fecha
            self.callback(fecha)
            
            # Cerrar ventana
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Error al procesar la fecha seleccionada")


# Funciones auxiliares para conversión de fechas
def formato_db_a_visual(fecha_db):
    """
    Convierte fecha de base de datos (YYYY-MM-DD) a formato visual (DD/MM/YYYY)
    """
    try:
        fecha = datetime.strptime(fecha_db, '%Y-%m-%d')
        return fecha.strftime('%d/%m/%Y')
    except:
        return fecha_db


def formato_visual_a_db(fecha_visual):
    """
    Convierte fecha visual (DD/MM/YYYY) a formato base de datos (YYYY-MM-DD)
    """
    try:
        fecha = datetime.strptime(fecha_visual, '%d/%m/%Y')
        return fecha.strftime('%Y-%m-%d')
    except:
        return fecha_visual


def validar_fecha_formato_visual(fecha_str):
    """
    Valida que la fecha esté en formato DD/MM/YYYY
    Retorna: (es_valido, mensaje)
    """
    try:
        datetime.strptime(fecha_str, '%d/%m/%Y')
        return True, "Fecha válida"
    except ValueError:
        return False, "Formato de fecha inválido. Use DD/MM/AAAA"