# modules/inquilinos.py - Módulo de Gestión de Inquilinos
import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from utils.validators import Validators, validar_formulario
from components.date_picker import DatePicker, formato_db_a_visual

class InquilinosModule(ctk.CTkFrame):
    """Módulo completo de gestión de inquilinos"""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        super().__init__(parent, fg_color="transparent")
        
        self.db_manager = db_manager
        self.validators = Validators()
        self.inquilinos = []
        
        self.create_widgets()
        self.cargar_inquilinos()
    
    def create_widgets(self):
        """Crea la interfaz del módulo"""
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            container,
            text="👥 Gestión de Inquilinos",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Frame de acciones
        actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(
            actions_frame,
            text="➕ Nuevo Inquilino",
            command=self.abrir_formulario_nuevo,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#f39c12",
            hover_color="#e67e22"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="🔄 Actualizar",
            command=self.cargar_inquilinos,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3498db"
        ).pack(side="left", padx=5)
        
        # Frame de búsqueda
        search_frame = ctk.CTkFrame(container, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="🔍 Buscar:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Nombre, apellido o CUIT/DNI...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar())
        
        # Frame de lista
        self.list_frame = ctk.CTkFrame(container, corner_radius=10)
        self.list_frame.pack(fill="both", expand=True, pady=10)
    
    def cargar_inquilinos(self):
        """Carga todos los inquilinos desde la base de datos"""
        self.search_entry.delete(0, 'end')
        
        query = '''
            SELECT i.*,
                   CASE WHEN c.id IS NOT NULL THEN 'Sí' ELSE 'No' END as tiene_contrato,
                   CASE WHEN c.id IS NOT NULL THEN im.direccion ELSE NULL END as inmueble_actual
            FROM inquilinos i
            LEFT JOIN contratos c ON i.id = c.inquilino_id AND c.estado = 'activo'
            LEFT JOIN inmuebles im ON c.inmueble_id = im.id
            ORDER BY i.apellido, i.nombre
        '''
        self.inquilinos = self.db_manager.execute_query(query)
        self.mostrar_inquilinos(self.inquilinos)
    
    def buscar(self):
        """Busca inquilinos por texto"""
        termino = self.search_entry.get().strip().lower()
        
        if not termino:
            self.mostrar_inquilinos(self.inquilinos)
            return
        
        filtrados = [
            i for i in self.inquilinos
            if termino in i['nombre'].lower() or
               termino in i['apellido'].lower() or
               termino in i['cuit_dni'].lower() or
               (i['telefono'] and termino in i['telefono'].lower())
        ]
        
        self.mostrar_inquilinos(filtrados)
    
    def mostrar_inquilinos(self, inquilinos):
        """Muestra la lista de inquilinos"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not inquilinos:
            ctk.CTkLabel(
                self.list_frame,
                text="No se encontraron inquilinos",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Encabezados
        headers = ["ID", "Nombre", "Apellido", "CUIT/DNI", "Teléfono", "Email", "Con Contrato", "Inmueble", "Acciones"]
        header_frame = ctk.CTkFrame(self.list_frame, fg_color="#f39c12")
        header_frame.pack(fill="x", padx=5, pady=5)
        
        widths = [50, 110, 110, 120, 110, 160, 100, 160, 150]
        for i, (header, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white",
                width=width
            ).grid(row=0, column=i, padx=5, pady=10, sticky="w")
        
        # Datos
        for inq in inquilinos:
            self.crear_fila_inquilino(inq)
    
    def crear_fila_inquilino(self, inq):
        """Crea una fila para un inquilino"""
        row_frame = ctk.CTkFrame(self.list_frame, fg_color=("#ffffff", "#2d2d2d"))
        row_frame.pack(fill="x", padx=5, pady=2)
        
        widths = [50, 110, 110, 120, 110, 160, 100, 160, 150]
        
        datos = [
            str(inq['id']),
            inq['nombre'],
            inq['apellido'],
            inq['cuit_dni'],
            inq['telefono'] or "N/A",
            inq['email'] or "N/A",
            inq['tiene_contrato'],
            inq['inmueble_actual'] or "N/A"
        ]
        
        for i, (dato, width) in enumerate(zip(datos, widths[:-1])):
            color = "green" if i == 6 and dato == "Sí" else None
            ctk.CTkLabel(
                row_frame,
                text=dato,
                font=ctk.CTkFont(size=12),
                width=width,
                anchor="w",
                text_color=color
            ).grid(row=0, column=i, padx=5, pady=8, sticky="w")
        
        # Botones de acción
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=8, padx=5, pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="✏️",
            width=40,
            height=30,
            command=lambda: self.editar_inquilino(inq['id']),
            fg_color="#3498db"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=40,
            height=30,
            command=lambda: self.eliminar_inquilino(inq['id'], inq['nombre'], inq['apellido']),
            fg_color="#e74c3c"
        ).pack(side="left", padx=2)
    
    def abrir_formulario_nuevo(self):
        """Abre el formulario para nuevo inquilino"""
        FormularioInquilino(self, self.db_manager, None, self.cargar_inquilinos)
    
    def editar_inquilino(self, inquilino_id):
        """Abre el formulario para editar inquilino"""
        inquilino = self.db_manager.get_by_id('inquilinos', inquilino_id)
        if inquilino:
            FormularioInquilino(self, self.db_manager, inquilino, self.cargar_inquilinos)
    
    def eliminar_inquilino(self, inquilino_id, nombre, apellido):
        """Elimina un inquilino"""
        # Verificar si tiene contratos activos
        query = "SELECT COUNT(*) as total FROM contratos WHERE inquilino_id = ? AND estado = 'activo'"
        result = self.db_manager.execute_query(query, (inquilino_id,))
        
        if result and result[0]['total'] > 0:
            messagebox.showerror(
                "No se puede eliminar",
                f"El inquilino {nombre} {apellido} tiene contratos activos.\n" +
                "Finalice los contratos primero."
            )
            return
        
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar al inquilino {nombre} {apellido}?"
        ):
            if self.db_manager.delete('inquilinos', inquilino_id):
                messagebox.showinfo("Éxito", "Inquilino eliminado correctamente")
                self.cargar_inquilinos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el inquilino")


class FormularioInquilino(ctk.CTkToplevel):
    """Formulario para crear/editar inquilinos"""
    
    def __init__(self, parent, db_manager: DatabaseManager, inquilino=None, callback=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.inquilino = inquilino
        self.callback = callback
        self.validators = Validators()
        
        self.title("Nuevo Inquilino" if not inquilino else "Editar Inquilino")
        self.geometry("650x680")
        self.resizable(False, False)
        
        self.center_window()
        self.create_form()
        
        if inquilino:
            self.cargar_datos()
        
        self.transient(parent)
        self.grab_set()
    
    def center_window(self):
        """Centra la ventana"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_form(self):
        """Crea el formulario"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        title = ctk.CTkLabel(
            main_frame,
            text="📝 Datos del Inquilino",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 25))
        
        self.entries = {}
        
        campos = [
            ("nombre", "Nombre *", "text"),
            ("apellido", "Apellido *", "text"),
            ("cuit_dni", "CUIT/DNI *", "text"),
            ("telefono", "Teléfono *", "text"),
            ("email", "Email", "text"),
            ("direccion", "Dirección *", "text"),
            ("fecha_nacimiento", "Fecha de Nacimiento (AAAA-MM-DD)", "text"),
            ("ocupacion", "Ocupación", "text"),
        ]
        
        for field_name, label, field_type in campos:
            self.create_field(main_frame, field_name, label, field_type)
        
        note = ctk.CTkLabel(
            main_frame,
            text="* Campos obligatorios",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        note.pack(pady=10)
        
        # Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Guardar",
            command=self.guardar,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancelar",
            command=self.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e74c3c"
        ).pack(side="left", padx=10)
    
    def create_field(self, parent, name, label, field_type):
        """Crea un campo del formulario"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=200
        ).pack(side="left", padx=5)
        
        entry = ctk.CTkEntry(
            frame,
            width=300,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        entry.pack(side="left", padx=5)
        self.entries[name] = entry
    
    def cargar_datos(self):
        """Carga los datos del inquilino en el formulario"""
        if not self.inquilino:
            return
        
        for field in self.entries.keys():
            if field in self.inquilino and self.inquilino[field]:
                self.entries[field].insert(0, str(self.inquilino[field]))
    
    def guardar(self):
        """Guarda el inquilino"""
        datos = {field: entry.get().strip() for field, entry in self.entries.items()}
        
        # Validar campos obligatorios
        campos_validar = {
            'nombre': (datos['nombre'], 'texto_requerido', 'Nombre'),
            'apellido': (datos['apellido'], 'texto_requerido', 'Apellido'),
            'cuit_dni': (datos['cuit_dni'], 'cuit_o_dni'),
            'telefono': (datos['telefono'], 'telefono'),
            'direccion': (datos['direccion'], 'texto_requerido', 'Dirección'),
        }
        
        if datos['email']:
            campos_validar['email'] = (datos['email'], 'email')
        
        valido, errores = validar_formulario(campos_validar)
        
        if not valido:
            messagebox.showerror("Errores de validación", "\n".join(errores))
            return
        
        # Validar fecha de nacimiento si existe
        if datos['fecha_nacimiento']:
            try:
                datetime.strptime(datos['fecha_nacimiento'], '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use: AAAA-MM-DD")
                return
        
        # Verificar CUIT/DNI duplicado
        excluir_id = self.inquilino['id'] if self.inquilino else None
        if self.db_manager.verificar_cuit_dni_existe(datos['cuit_dni'], 'inquilinos', excluir_id):
            messagebox.showerror("Error", "Ya existe un inquilino con ese CUIT/DNI")
            return
        
        # Guardar
        try:
            if self.inquilino:
                if self.db_manager.update('inquilinos', self.inquilino['id'], datos):
                    messagebox.showinfo("Éxito", "Inquilino actualizado correctamente")
                    if self.callback:
                        self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el inquilino")
            else:
                if self.db_manager.insert('inquilinos', datos):
                    messagebox.showinfo("Éxito", "Inquilino creado correctamente")
                    if self.callback:
                        self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear el inquilino")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
