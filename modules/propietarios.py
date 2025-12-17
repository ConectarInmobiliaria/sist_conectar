# modules/propietarios.py - Módulo de Gestión de Propietarios
import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from utils.validators import Validators, validar_formulario


class PropietariosModule(ctk.CTkFrame):
    """Módulo completo de gestión de propietarios"""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        super().__init__(parent, fg_color="transparent")
        
        self.db_manager = db_manager
        self.validators = Validators()
        self.propietarios = []
        
        self.create_widgets()
        self.cargar_propietarios()
    
    def create_widgets(self):
        """Crea la interfaz del módulo"""
        # Contenedor con scroll
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            container,
            text="👤 Gestión de Propietarios",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Frame de acciones
        actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=15)
        
        # Botones de acción
        ctk.CTkButton(
            actions_frame,
            text="➕ Nuevo Propietario",
            command=self.abrir_formulario_nuevo,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="🔄 Actualizar",
            command=self.cargar_propietarios,
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
    
    def cargar_propietarios(self):
        """Carga todos los propietarios desde la base de datos"""
        # Limpiar búsqueda
        self.search_entry.delete(0, 'end')
        
        # Obtener propietarios con información de inmuebles
        query = '''
            SELECT p.*, COUNT(i.id) as cantidad_inmuebles
            FROM propietarios p
            LEFT JOIN inmuebles i ON p.id = i.propietario_id
            GROUP BY p.id
            ORDER BY p.apellido, p.nombre
        '''
        self.propietarios = self.db_manager.execute_query(query)
        self.mostrar_propietarios(self.propietarios)
    
    def buscar(self):
        """Busca propietarios por texto"""
        termino = self.search_entry.get().strip().lower()
        
        if not termino:
            self.mostrar_propietarios(self.propietarios)
            return
        
        # Filtrar propietarios
        filtrados = [
            p for p in self.propietarios
            if termino in p['nombre'].lower() or
               termino in p['apellido'].lower() or
               termino in p['cuit_dni'].lower() or
               (p['telefono'] and termino in p['telefono'].lower())
        ]
        
        self.mostrar_propietarios(filtrados)
    
    def mostrar_propietarios(self, propietarios):
        """Muestra la lista de propietarios"""
        # Limpiar frame
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not propietarios:
            ctk.CTkLabel(
                self.list_frame,
                text="No se encontraron propietarios",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Encabezados
        headers = ["ID", "Nombre", "Apellido", "CUIT/DNI", "Teléfono", "Email", "Propiedades", "Acciones"]
        header_frame = ctk.CTkFrame(self.list_frame, fg_color="#e74c3c")
        header_frame.pack(fill="x", padx=5, pady=5)
        
        widths = [50, 120, 120, 130, 120, 180, 100, 150]
        for i, (header, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white",
                width=width
            ).grid(row=0, column=i, padx=5, pady=10, sticky="w")
        
        # Datos
        for prop in propietarios:
            self.crear_fila_propietario(prop)
    
    def crear_fila_propietario(self, prop):
        """Crea una fila para un propietario"""
        row_frame = ctk.CTkFrame(self.list_frame, fg_color=("#ffffff", "#2d2d2d"))
        row_frame.pack(fill="x", padx=5, pady=2)
        
        widths = [50, 120, 120, 130, 120, 180, 100, 150]
        
        # Datos
        datos = [
            str(prop['id']),
            prop['nombre'],
            prop['apellido'],
            prop['cuit_dni'],
            prop['telefono'] or "N/A",
            prop['email'] or "N/A",
            str(prop['cantidad_inmuebles'])
        ]
        
        for i, (dato, width) in enumerate(zip(datos, widths[:-1])):
            ctk.CTkLabel(
                row_frame,
                text=dato,
                font=ctk.CTkFont(size=12),
                width=width,
                anchor="w"
            ).grid(row=0, column=i, padx=5, pady=8, sticky="w")
        
        # Botones de acción
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=7, padx=5, pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="✏️",
            width=40,
            height=30,
            command=lambda: self.editar_propietario(prop['id']),
            fg_color="#3498db"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=40,
            height=30,
            command=lambda: self.eliminar_propietario(prop['id'], prop['nombre'], prop['apellido']),
            fg_color="#e74c3c"
        ).pack(side="left", padx=2)
    
    def abrir_formulario_nuevo(self):
        """Abre el formulario para nuevo propietario"""
        FormularioPropietario(self, self.db_manager, None, self.cargar_propietarios)
    
    def editar_propietario(self, propietario_id):
        """Abre el formulario para editar propietario"""
        propietario = self.db_manager.get_by_id('propietarios', propietario_id)
        if propietario:
            FormularioPropietario(self, self.db_manager, propietario, self.cargar_propietarios)
    
    def eliminar_propietario(self, propietario_id, nombre, apellido):
        """Elimina un propietario"""
        # Verificar si tiene propiedades
        query = "SELECT COUNT(*) as total FROM inmuebles WHERE propietario_id = ?"
        result = self.db_manager.execute_query(query, (propietario_id,))
        
        if result and result[0]['total'] > 0:
            messagebox.showerror(
                "No se puede eliminar",
                f"El propietario {nombre} {apellido} tiene propiedades asociadas.\n" +
                "Elimine o reasigne las propiedades primero."
            )
            return
        
        # Confirmar eliminación
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar al propietario {nombre} {apellido}?"
        ):
            if self.db_manager.delete('propietarios', propietario_id):
                messagebox.showinfo("Éxito", "Propietario eliminado correctamente")
                self.cargar_propietarios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el propietario")


class FormularioPropietario(ctk.CTkToplevel):
    """Formulario para crear/editar propietarios"""
    
    def __init__(self, parent, db_manager: DatabaseManager, propietario=None, callback=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.propietario = propietario
        self.callback = callback
        self.validators = Validators()
        
        # Configurar ventana
        self.title("Nuevo Propietario" if not propietario else "Editar Propietario")
        self.geometry("650x650")
        self.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Crear formulario
        self.create_form()
        
        # Si es edición, cargar datos
        if propietario:
            self.cargar_datos()
        
        # Hacer modal
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
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="📝 Datos del Propietario",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 25))
        
        # Campos del formulario
        self.entries = {}
        
        campos = [
            ("nombre", "Nombre *", "text"),
            ("apellido", "Apellido *", "text"),
            ("cuit_dni", "CUIT/DNI *", "text"),
            ("telefono", "Teléfono *", "text"),
            ("email", "Email", "text"),
            ("direccion", "Dirección *", "text"),
        ]
        
        for field_name, label, field_type in campos:
            self.create_field(main_frame, field_name, label, field_type)
        
        # Nota
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
            width=120
        ).pack(side="left", padx=5)
        
        if field_type == "text":
            entry = ctk.CTkEntry(
                frame,
                width=350,
                height=35,
                font=ctk.CTkFont(size=13)
            )
            entry.pack(side="left", padx=5)
            self.entries[name] = entry
    
    def cargar_datos(self):
        """Carga los datos del propietario en el formulario"""
        if not self.propietario:
            return
        
        for field in ['nombre', 'apellido', 'cuit_dni', 'telefono', 'email', 'direccion']:
            if field in self.propietario and self.propietario[field]:
                self.entries[field].insert(0, str(self.propietario[field]))
    
    def guardar(self):
        """Guarda el propietario"""
        # Obtener valores
        datos = {field: entry.get().strip() for field, entry in self.entries.items()}
        
        # Validar campos obligatorios
        campos_validar = {
            'nombre': (datos['nombre'], 'texto_requerido', 'Nombre'),
            'apellido': (datos['apellido'], 'texto_requerido', 'Apellido'),
            'cuit_dni': (datos['cuit_dni'], 'cuit_o_dni'),
            'telefono': (datos['telefono'], 'telefono'),
            'direccion': (datos['direccion'], 'texto_requerido', 'Dirección'),
        }
        
        # Validar email solo si hay valor
        if datos['email']:
            campos_validar['email'] = (datos['email'], 'email')
        
        valido, errores = validar_formulario(campos_validar)
        
        if not valido:
            messagebox.showerror("Errores de validación", "\n".join(errores))
            return
        
        # Verificar CUIT/DNI duplicado
        excluir_id = self.propietario['id'] if self.propietario else None
        if self.db_manager.verificar_cuit_dni_existe(datos['cuit_dni'], 'propietarios', excluir_id):
            messagebox.showerror("Error", "Ya existe un propietario con ese CUIT/DNI")
            return
        
        # Guardar
        try:
            if self.propietario:
                # Actualizar
                if self.db_manager.update('propietarios', self.propietario['id'], datos):
                    messagebox.showinfo("Éxito", "Propietario actualizado correctamente")
                    if self.callback:
                        self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el propietario")
            else:
                # Crear nuevo
                if self.db_manager.insert('propietarios', datos):
                    messagebox.showinfo("Éxito", "Propietario creado correctamente")
                    if self.callback:
                        self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear el propietario")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
