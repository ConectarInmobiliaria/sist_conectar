# modules/inmuebles.py - Módulo de Gestión de Inmuebles
import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from utils.validators import Validators, validar_formulario


class InmueblesModule(ctk.CTkFrame):
    """Módulo completo de gestión de inmuebles"""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        super().__init__(parent, fg_color="transparent")
        
        self.db_manager = db_manager
        self.validators = Validators()
        self.inmuebles = []
        
        self.create_widgets()
        self.cargar_inmuebles()
    
    def create_widgets(self):
        """Crea la interfaz del módulo"""
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="🏠 Gestión de Inmuebles",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Frame de acciones
        actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(
            actions_frame,
            text="➕ Nuevo Inmueble",
            command=self.abrir_formulario_nuevo,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="🔄 Actualizar",
            command=self.cargar_inmuebles,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3498db"
        ).pack(side="left", padx=5)
        
        # Filtros
        filter_frame = ctk.CTkFrame(container, fg_color="transparent")
        filter_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(filter_frame, text="Estado:", font=ctk.CTkFont(size=13)).pack(side="left", padx=5)
        
        self.filter_estado = ctk.CTkOptionMenu(
            filter_frame,
            values=["Todos", "disponible", "alquilado", "vendido", "mantenimiento"],
            command=self.filtrar_por_estado,
            width=150
        )
        self.filter_estado.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="🔍 Buscar:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(20, 5))
        
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Dirección o propietario...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar())
        
        # Frame de lista
        self.list_frame = ctk.CTkFrame(container, corner_radius=10)
        self.list_frame.pack(fill="both", expand=True, pady=10)
    
    def cargar_inmuebles(self):
        """Carga todos los inmuebles"""
        self.search_entry.delete(0, 'end')
        self.filter_estado.set("Todos")
        
        query = '''
            SELECT i.*, p.nombre || ' ' || p.apellido as propietario_nombre
            FROM inmuebles i
            LEFT JOIN propietarios p ON i.propietario_id = p.id
            ORDER BY i.fecha_creacion DESC
        '''
        self.inmuebles = self.db_manager.execute_query(query)
        self.mostrar_inmuebles(self.inmuebles)
    
    def filtrar_por_estado(self, estado):
        """Filtra inmuebles por estado"""
        if estado == "Todos":
            self.mostrar_inmuebles(self.inmuebles)
        else:
            filtrados = [i for i in self.inmuebles if i['estado'] == estado]
            self.mostrar_inmuebles(filtrados)
    
    def buscar(self):
        """Busca inmuebles por texto"""
        termino = self.search_entry.get().strip().lower()
        
        if not termino:
            estado = self.filter_estado.get()
            self.filtrar_por_estado(estado)
            return
        
        filtrados = [
            i for i in self.inmuebles
            if termino in i['direccion'].lower() or
               (i['propietario_nombre'] and termino in i['propietario_nombre'].lower()) or
               (i['partida_inmobiliaria'] and termino in i['partida_inmobiliaria'].lower())
        ]
        
        self.mostrar_inmuebles(filtrados)
    
    def mostrar_inmuebles(self, inmuebles):
        """Muestra la lista de inmuebles"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not inmuebles:
            ctk.CTkLabel(
                self.list_frame,
                text="No se encontraron inmuebles",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Encabezados
        headers = ["ID", "Dirección", "Tipo", "Estado", "Alquiler", "Propietario", "Partida", "Acciones"]
        header_frame = ctk.CTkFrame(self.list_frame, fg_color="#9b59b6")
        header_frame.pack(fill="x", padx=5, pady=5)
        
        widths = [50, 220, 100, 100, 100, 150, 120, 150]
        for i, (header, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white",
                width=width
            ).grid(row=0, column=i, padx=5, pady=10, sticky="w")
        
        for inmueble in inmuebles:
            self.crear_fila_inmueble(inmueble)
    
    def crear_fila_inmueble(self, inmueble):
        """Crea una fila para un inmueble"""
        row_frame = ctk.CTkFrame(self.list_frame, fg_color=("#ffffff", "#2d2d2d"))
        row_frame.pack(fill="x", padx=5, pady=2)
        
        widths = [50, 220, 100, 100, 100, 150, 120, 150]
        
        colors = {
            "disponible": "green",
            "alquilado": "orange",
            "vendido": "red",
            "mantenimiento": "gray"
        }
        
        datos = [
            str(inmueble['id']),
            inmueble['direccion'],
            inmueble['tipo'],
            inmueble['estado'],
            f"${inmueble['precio_alquiler']:,.0f}" if inmueble['precio_alquiler'] else "N/A",
            inmueble['propietario_nombre'] or "Sin propietario",
            inmueble['partida_inmobiliaria'] or "N/A"
        ]
        
        for i, (dato, width) in enumerate(zip(datos, widths[:-1])):
            color = colors.get(inmueble['estado']) if i == 3 else None
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
        action_frame.grid(row=0, column=7, padx=5, pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="👁️",
            width=35,
            height=30,
            command=lambda: self.ver_detalle(inmueble['id']),
            fg_color="#3498db"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="✏️",
            width=35,
            height=30,
            command=lambda: self.editar_inmueble(inmueble['id']),
            fg_color="#f39c12"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=35,
            height=30,
            command=lambda: self.eliminar_inmueble(inmueble['id'], inmueble['direccion']),
            fg_color="#e74c3c"
        ).pack(side="left", padx=2)
    
    def abrir_formulario_nuevo(self):
        """Abre el formulario para nuevo inmueble"""
        FormularioInmueble(self, self.db_manager, None, self.cargar_inmuebles)
    
    def editar_inmueble(self, inmueble_id):
        """Edita un inmueble"""
        inmueble = self.db_manager.get_by_id('inmuebles', inmueble_id)
        if inmueble:
            FormularioInmueble(self, self.db_manager, inmueble, self.cargar_inmuebles)
    
    def ver_detalle(self, inmueble_id):
        """Muestra detalle completo del inmueble"""
        inmueble = self.db_manager.get_by_id('inmuebles', inmueble_id)
        if inmueble:
            DetalleInmueble(self, inmueble, self.db_manager)
    
    def eliminar_inmueble(self, inmueble_id, direccion):
        """Elimina un inmueble"""
        # Verificar si tiene contratos
        query = "SELECT COUNT(*) as total FROM contratos WHERE inmueble_id = ?"
        result = self.db_manager.execute_query(query, (inmueble_id,))
        
        if result and result[0]['total'] > 0:
            messagebox.showerror(
                "No se puede eliminar",
                f"El inmueble en {direccion} tiene contratos asociados.\n" +
                "Elimine los contratos primero."
            )
            return
        
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el inmueble en {direccion}?"
        ):
            if self.db_manager.delete('inmuebles', inmueble_id):
                messagebox.showinfo("Éxito", "Inmueble eliminado correctamente")
                self.cargar_inmuebles()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el inmueble")


class FormularioInmueble(ctk.CTkToplevel):
    """Formulario para crear/editar inmuebles"""
    
    def __init__(self, parent, db_manager: DatabaseManager, inmueble=None, callback=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.inmueble = inmueble
        self.callback = callback
        self.validators = Validators()
        
        self.title("Nuevo Inmueble" if not inmueble else "Editar Inmueble")
        self.geometry("750x700")
        self.resizable(False, False)
        
        self.center_window()
        self.create_form()
        
        if inmueble:
            self.cargar_datos()
        
        self.transient(parent)
        self.grab_set()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_form(self):
        """Crea el formulario"""
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        title = ctk.CTkLabel(
            main_frame,
            text="🏠 Datos del Inmueble",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        self.entries = {}
        self.combos = {}
        
        # Propietario
        self.create_combo_propietario(main_frame)
        
        # Tipo de inmueble
        self.create_combo_tipo(main_frame)
        
        # Ubicación
        self.create_section(main_frame, "📍 Ubicación")
        campos_ubicacion = [
            ("direccion", "Dirección *", "text"),
            ("ciudad", "Ciudad", "text"),
            ("provincia", "Provincia", "text"),
            ("codigo_postal", "Código Postal", "text"),
        ]
        for field in campos_ubicacion:
            self.create_field(main_frame, *field)
        
        # Características
        self.create_section(main_frame, "📐 Características")
        campos_caracteristicas = [
            ("superficie", "Superficie (m²)", "text"),
            ("habitaciones", "Habitaciones", "text"),
            ("banos", "Baños", "text"),
        ]
        for field in campos_caracteristicas:
            self.create_field(main_frame, *field)
        
        # Precios
        self.create_section(main_frame, "💰 Precios")
        campos_precios = [
            ("precio_venta", "Precio de Venta", "text"),
            ("precio_alquiler", "Precio de Alquiler Mensual", "text"),
        ]
        for field in campos_precios:
            self.create_field(main_frame, *field)
        
        # Datos específicos argentinos
        self.create_section(main_frame, "📋 Datos Administrativos (Argentina)")
        campos_admin = [
            ("partida_inmobiliaria", "Partida Inmobiliaria", "text"),
            ("conexion_emsa", "N° Conexión EMSA (Luz)", "text"),
            ("conexion_samsa", "N° Conexión SAMSA (Agua)", "text"),
        ]
        for field in campos_admin:
            self.create_field(main_frame, *field)
        
        # Estado
        self.create_combo_estado(main_frame)
        
        # Descripción
        self.create_section(main_frame, "📝 Descripción")
        self.create_textbox(main_frame, "descripcion", "Descripción detallada del inmueble")
        
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
    
    def create_section(self, parent, title):
        """Crea una sección del formulario"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(15, 5))
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")
    
    def create_field(self, parent, name, label, field_type):
        """Crea un campo del formulario"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=220
        ).pack(side="left", padx=5)
        
        entry = ctk.CTkEntry(frame, width=380, height=35, font=ctk.CTkFont(size=13))
        entry.pack(side="left", padx=5)
        self.entries[name] = entry
    
    def create_combo_propietario(self, parent):
        """Crea selector de propietario"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Propietario *",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=220
        ).pack(side="left", padx=5)
        
        # Obtener propietarios
        propietarios = self.db_manager.get_all('propietarios', 'apellido, nombre')
        self.propietarios_dict = {f"{p['nombre']} {p['apellido']}": p['id'] for p in propietarios}
        propietarios_nombres = list(self.propietarios_dict.keys())
        
        if not propietarios_nombres:
            propietarios_nombres = ["No hay propietarios registrados"]
        
        combo = ctk.CTkComboBox(
            frame,
            values=propietarios_nombres,
            width=380,
            height=35
        )
        combo.pack(side="left", padx=5)
        self.combos['propietario'] = combo
    
    def create_combo_tipo(self, parent):
        """Crea selector de tipo"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Tipo de Inmueble *",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=220
        ).pack(side="left", padx=5)
        
        combo = ctk.CTkComboBox(
            frame,
            values=["casa", "departamento", "local", "oficina", "terreno", "galpon", "otro"],
            width=380,
            height=35
        )
        combo.pack(side="left", padx=5)
        self.combos['tipo'] = combo
    
    def create_combo_estado(self, parent):
        """Crea selector de estado"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Estado",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=220
        ).pack(side="left", padx=5)
        
        combo = ctk.CTkComboBox(
            frame,
            values=["disponible", "alquilado", "vendido", "mantenimiento", "reservado"],
            width=380,
            height=35
        )
        combo.set("disponible")
        combo.pack(side="left", padx=5)
        self.combos['estado'] = combo
    
    def create_textbox(self, parent, name, placeholder):
        """Crea un campo de texto multilínea"""
        textbox = ctk.CTkTextbox(parent, width=600, height=100)
        textbox.pack(pady=5)
        self.entries[name] = textbox
    
    def cargar_datos(self):
        """Carga datos del inmueble"""
        if not self.inmueble:
            return
        
        # Campos normales
        for field, entry in self.entries.items():
            if field == 'descripcion':
                if self.inmueble.get(field):
                    entry.insert("1.0", str(self.inmueble[field]))
            else:
                if field in self.inmueble and self.inmueble[field]:
                    entry.insert(0, str(self.inmueble[field]))
        
        # Combos
        if self.inmueble.get('tipo'):
            self.combos['tipo'].set(self.inmueble['tipo'])
        
        if self.inmueble.get('estado'):
            self.combos['estado'].set(self.inmueble['estado'])
        
        # Propietario
        if self.inmueble.get('propietario_id'):
            prop = self.db_manager.get_by_id('propietarios', self.inmueble['propietario_id'])
            if prop:
                nombre_completo = f"{prop['nombre']} {prop['apellido']}"
                if nombre_completo in self.propietarios_dict:
                    self.combos['propietario'].set(nombre_completo)
    
    def guardar(self):
        """Guarda el inmueble"""
        # Obtener datos básicos
        datos = {}
        
        for field, entry in self.entries.items():
            if field == 'descripcion':
                datos[field] = entry.get("1.0", "end-1c").strip()
            else:
                datos[field] = entry.get().strip()
        
        # Agregar combos
        datos['tipo'] = self.combos['tipo'].get()
        datos['estado'] = self.combos['estado'].get()
        
        # Propietario
        propietario_nombre = self.combos['propietario'].get()
        if propietario_nombre in self.propietarios_dict:
            datos['propietario_id'] = self.propietarios_dict[propietario_nombre]
        else:
            messagebox.showerror("Error", "Debe seleccionar un propietario válido")
            return
        
        # Validar campos obligatorios
        if not datos.get('direccion'):
            messagebox.showerror("Error", "La dirección es obligatoria")
            return
        
        # Convertir números
        campos_numericos = ['superficie', 'habitaciones', 'banos', 'precio_venta', 'precio_alquiler']
        for campo in campos_numericos:
            if datos.get(campo):
                try:
                    datos[campo] = float(datos[campo].replace(',', '.'))
                except ValueError:
                    datos[campo] = None
            else:
                datos[campo] = None
        
        # Guardar
        try:
            if self.inmueble:
                if self.db_manager.update('inmuebles', self.inmueble['id'], datos):
                    messagebox.showinfo("Éxito", "Inmueble actualizado correctamente")
                    if self.callback:
                        self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el inmueble")
            else:
                if self.db_manager.insert('inmuebles', datos):
                    messagebox.showinfo("Éxito", "Inmueble creado correctamente")
                    if self.callback:
                        self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear el inmueble")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")


class DetalleInmueble(ctk.CTkToplevel):
    """Ventana de detalle completo del inmueble"""
    
    def __init__(self, parent, inmueble, db_manager):
        super().__init__(parent)
        
        self.inmueble = inmueble
        self.db_manager = db_manager
        
        self.title(f"Detalle - {inmueble['direccion']}")
        self.geometry("600x700")
        
        self.create_detail_view()
        
        self.transient(parent)
    
    def create_detail_view(self):
        """Crea la vista de detalle"""
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text=f"🏠 {self.inmueble['direccion']}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(0, 20))
        
        # Información en secciones
        self.add_info_section(main_frame, "📍 Ubicación", [
            ("Dirección", self.inmueble['direccion']),
            ("Ciudad", self.inmueble['ciudad'] or "N/A"),
            ("Provincia", self.inmueble['provincia'] or "N/A"),
            ("Código Postal", self.inmueble['codigo_postal'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "📐 Características", [
            ("Tipo", self.inmueble['tipo']),
            ("Superficie", f"{self.inmueble['superficie']} m²" if self.inmueble['superficie'] else "N/A"),
            ("Habitaciones", self.inmueble['habitaciones'] or "N/A"),
            ("Baños", self.inmueble['banos'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "💰 Precios", [
            ("Venta", f"${self.inmueble['precio_venta']:,.0f}" if self.inmueble['precio_venta'] else "No disponible"),
            ("Alquiler Mensual", f"${self.inmueble['precio_alquiler']:,.0f}" if self.inmueble['precio_alquiler'] else "No disponible"),
        ])
        
        self.add_info_section(main_frame, "📋 Datos Administrativos", [
            ("Partida Inmobiliaria", self.inmueble['partida_inmobiliaria'] or "N/A"),
            ("Conexión EMSA (Luz)", self.inmueble['conexion_emsa'] or "N/A"),
            ("Conexión SAMSA (Agua)", self.inmueble['conexion_samsa'] or "N/A"),
            ("Estado", self.inmueble['estado']),
        ])
        
        if self.inmueble.get('descripcion'):
            self.add_info_section(main_frame, "📝 Descripción", [
                ("", self.inmueble['descripcion']),
            ])
        
        # Botón cerrar
        ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.destroy,
            width=200,
            height=40
        ).pack(pady=20)
    
    def add_info_section(self, parent, title, items):
        """Agrega una sección de información"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        for label, value in items:
            if label:
                info_frame = ctk.CTkFrame(frame, fg_color="transparent")
                info_frame.pack(fill="x", padx=20, pady=5)
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"{label}:",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    width=150,
                    anchor="w"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    info_frame,
                    text=str(value),
                    font=ctk.CTkFont(size=13),
                    anchor="w"
                ).pack(side="left", padx=10)
            else:
                ctk.CTkLabel(
                    frame,
                    text=str(value),
                    font=ctk.CTkFont(size=13),
                    wraplength=500,
                    justify="left"
                ).pack(padx=20, pady=10)
