# modules/contratos.py - Módulo de Gestión de Contratos
import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from utils.validators import Validators, validar_formulario
from components.date_picker import DatePicker, formato_db_a_visual, formato_visual_a_db

class ContratosModule(ctk.CTkFrame):
    """Módulo completo de gestión de contratos"""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        super().__init__(parent, fg_color="transparent")
        
        self.db_manager = db_manager
        self.validators = Validators()
        self.contratos = []
        
        self.create_widgets()
        self.cargar_contratos()
    
    def create_widgets(self):
        """Crea la interfaz del módulo"""
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="📝 Gestión de Contratos",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Frame de acciones
        actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(
            actions_frame,
            text="➕ Nuevo Contrato",
            command=self.abrir_formulario_nuevo,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1abc9c",
            hover_color="#16a085"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="🔄 Actualizar",
            command=self.cargar_contratos,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3498db"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="📊 Contratos a Vencer",
            command=self.mostrar_proximos_vencer,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e67e22"
        ).pack(side="left", padx=5)
        
        # Filtros
        filter_frame = ctk.CTkFrame(container, fg_color="transparent")
        filter_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(filter_frame, text="Estado:", font=ctk.CTkFont(size=13)).pack(side="left", padx=5)
        
        self.filter_estado = ctk.CTkOptionMenu(
            filter_frame,
            values=["Todos", "activo", "finalizado", "rescindido", "renovado"],
            command=self.filtrar_por_estado,
            width=150
        )
        self.filter_estado.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="🔍 Buscar:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(20, 5))
        
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Inquilino o dirección...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar())
        
        # Frame de lista
        self.list_frame = ctk.CTkFrame(container, corner_radius=10)
        self.list_frame.pack(fill="both", expand=True, pady=10)
    
    def cargar_contratos(self):
        """Carga todos los contratos"""
        self.search_entry.delete(0, 'end')
        self.filter_estado.set("Todos")
        
        query = '''
            SELECT c.*,
                   i.direccion as inmueble_direccion,
                   i.tipo as inmueble_tipo,
                   inq.nombre || ' ' || inq.apellido as inquilino_nombre,
                   inq.telefono as inquilino_telefono,
                   p.nombre || ' ' || p.apellido as propietario_nombre,
                   julianday(c.fecha_fin) - julianday('now') as dias_restantes
            FROM contratos c
            JOIN inmuebles i ON c.inmueble_id = i.id
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            LEFT JOIN propietarios p ON i.propietario_id = p.id
            ORDER BY c.fecha_inicio DESC
        '''
        self.contratos = self.db_manager.execute_query(query)
        self.mostrar_contratos(self.contratos)
    
    def filtrar_por_estado(self, estado):
        """Filtra contratos por estado"""
        if estado == "Todos":
            self.mostrar_contratos(self.contratos)
        else:
            filtrados = [c for c in self.contratos if c['estado'] == estado]
            self.mostrar_contratos(filtrados)
    
    def buscar(self):
        """Busca contratos por texto"""
        termino = self.search_entry.get().strip().lower()
        
        if not termino:
            estado = self.filter_estado.get()
            self.filtrar_por_estado(estado)
            return
        
        filtrados = [
            c for c in self.contratos
            if termino in c['inquilino_nombre'].lower() or
               termino in c['inmueble_direccion'].lower() or
               (c['propietario_nombre'] and termino in c['propietario_nombre'].lower())
        ]
        
        self.mostrar_contratos(filtrados)
    
    def mostrar_contratos(self, contratos):
        """Muestra la lista de contratos"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not contratos:
            ctk.CTkLabel(
                self.list_frame,
                text="No se encontraron contratos",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Encabezados
        headers = ["ID", "Inmueble", "Inquilino", "Inicio", "Fin", "Monto", "Ajuste", "Estado", "Días Rest.", "Acciones"]
        header_frame = ctk.CTkFrame(self.list_frame, fg_color="#1abc9c")
        header_frame.pack(fill="x", padx=5, pady=5)
        
        widths = [40, 180, 150, 90, 90, 100, 80, 90, 80, 180]
        for i, (header, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
                width=width
            ).grid(row=0, column=i, padx=3, pady=10, sticky="w")
        
        for contrato in contratos:
            self.crear_fila_contrato(contrato)
    
    def crear_fila_contrato(self, contrato):
        """Crea una fila para un contrato"""
        row_frame = ctk.CTkFrame(self.list_frame, fg_color=("#ffffff", "#2d2d2d"))
        row_frame.pack(fill="x", padx=5, pady=2)
        
        widths = [40, 180, 150, 90, 90, 100, 80, 90, 80, 180]
        
        # Colores por estado
        colors = {
            "activo": "green",
            "finalizado": "gray",
            "rescindido": "red",
            "renovado": "blue"
        }
        
        # Color para días restantes
        dias_restantes = int(contrato['dias_restantes']) if contrato['dias_restantes'] else 0
        color_dias = "red" if dias_restantes < 30 and contrato['estado'] == 'activo' else None
        
        datos = [
            str(contrato['id']),
            contrato['inmueble_direccion'][:25] + "..." if len(contrato['inmueble_direccion']) > 25 else contrato['inmueble_direccion'],
            contrato['inquilino_nombre'][:20] + "..." if len(contrato['inquilino_nombre']) > 20 else contrato['inquilino_nombre'],
            contrato['fecha_inicio'],
            contrato['fecha_fin'],
            f"${contrato['monto_mensual']:,.0f}",
            f"{contrato['tipo_ajuste']}/{contrato['frecuencia_ajuste']}m",
            contrato['estado'],
            f"{dias_restantes}d" if contrato['estado'] == 'activo' else "-"
        ]
        
        for i, (dato, width) in enumerate(zip(datos, widths[:-1])):
            color = None
            if i == 7:  # Estado
                color = colors.get(contrato['estado'])
            elif i == 8:  # Días restantes
                color = color_dias
            
            ctk.CTkLabel(
                row_frame,
                text=dato,
                font=ctk.CTkFont(size=11),
                width=width,
                anchor="w",
                text_color=color
            ).grid(row=0, column=i, padx=3, pady=6, sticky="w")
        
        # Botones de acción
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=9, padx=3, pady=3)
        
        ctk.CTkButton(
            action_frame,
            text="👁️",
            width=35,
            height=28,
            command=lambda: self.ver_detalle(contrato['id']),
            fg_color="#3498db"
        ).pack(side="left", padx=1)
        
        ctk.CTkButton(
            action_frame,
            text="✏️",
            width=35,
            height=28,
            command=lambda: self.editar_contrato(contrato['id']),
            fg_color="#f39c12"
        ).pack(side="left", padx=1)
        
        if contrato['estado'] == 'activo':
            ctk.CTkButton(
                action_frame,
                text="📈",
                width=35,
                height=28,
                command=lambda: self.aplicar_ajuste(contrato['id']),
                fg_color="#9b59b6"
            ).pack(side="left", padx=1)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=35,
            height=28,
            command=lambda: self.eliminar_contrato(contrato['id']),
            fg_color="#e74c3c"
        ).pack(side="left", padx=1)
    
    def abrir_formulario_nuevo(self):
        """Abre el formulario para nuevo contrato"""
        FormularioContrato(self, self.db_manager, None, self.cargar_contratos)
    
    def editar_contrato(self, contrato_id):
        """Edita un contrato"""
        contrato = self.db_manager.get_by_id('contratos', contrato_id)
        if contrato:
            FormularioContrato(self, self.db_manager, contrato, self.cargar_contratos)
    def ver_detalle(self, contrato_id):
        """Muestra detalle del contrato"""
        query = '''
            SELECT c.*,
                   i.direccion as inmueble_direccion,
                   i.tipo as inmueble_tipo,
                   i.partida_inmobiliaria,
                   inq.nombre || ' ' || inq.apellido as inquilino_nombre,
                   inq.cuit_dni as inquilino_cuit,
                   inq.telefono as inquilino_telefono,
                   inq.email as inquilino_email,
                   p.nombre || ' ' || p.apellido as propietario_nombre,
                   p.telefono as propietario_telefono
            FROM contratos c
            JOIN inmuebles i ON c.inmueble_id = i.id
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            LEFT JOIN propietarios p ON i.propietario_id = p.id
            WHERE c.id = ?
        '''
        resultado = self.db_manager.execute_query(query, (contrato_id,))
        
        if resultado:
            DetalleContrato(self, resultado[0], self.db_manager)
    
    def aplicar_ajuste(self, contrato_id):
        """Aplica un ajuste al contrato"""
        AplicarAjuste(self, contrato_id, self.db_manager, self.cargar_contratos)
    
    def eliminar_contrato(self, contrato_id):
        """Elimina un contrato"""
        query = "SELECT COUNT(*) as total FROM pagos WHERE contrato_id = ?"
        result = self.db_manager.execute_query(query, (contrato_id,))
        
        if result and result[0]['total'] > 0:
            messagebox.showerror(
                "No se puede eliminar",
                "Este contrato tiene pagos registrados.\n" +
                "Elimine los pagos primero o cambie el estado del contrato."
            )
            return
        
        if messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro que desea eliminar este contrato?"
        ):
            if self.db_manager.delete('contratos', contrato_id):
                messagebox.showinfo("Éxito", "Contrato eliminado correctamente")
                self.cargar_contratos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el contrato")
    
    def mostrar_proximos_vencer(self):
        """Muestra contratos próximos a vencer"""
        proximos = [c for c in self.contratos 
                   if c['estado'] == 'activo' and c['dias_restantes'] and c['dias_restantes'] <= 60]
        
        if not proximos:
            messagebox.showinfo("Info", "No hay contratos próximos a vencer en los próximos 60 días")
            return
        
        self.mostrar_contratos(proximos)


class FormularioContrato(ctk.CTkToplevel):
    """Formulario para crear/editar contratos"""
    
    def __init__(self, parent, db_manager: DatabaseManager, contrato=None, callback=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.contrato = contrato
        self.callback = callback
        self.validators = Validators()
        
        self.title("Nuevo Contrato" if not contrato else "Editar Contrato")
        self.geometry("750x700") 
        self.resizable(False, False)
        
        self.center_window()
        self.create_form()
        
        if contrato:
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
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        title = ctk.CTkLabel(
            main_frame,
            text="📝 Datos del Contrato",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        self.entries = {}
        self.combos = {}
        
        # Inmueble
        self.create_combo_inmueble(main_frame)
        
        # Inquilino
        self.create_combo_inquilino(main_frame)
    
        # Fechas con selector de calendario
        self.create_section(main_frame, "📅 Fechas del Contrato")
        
        # Fecha de inicio
        self.fecha_inicio_picker = DatePicker(main_frame, label_text="Fecha de Inicio *")
        self.fecha_inicio_picker.pack(fill="x", pady=6)
        
        # Fecha de fin
        self.fecha_fin_picker = DatePicker(main_frame, label_text="Fecha de Fin *")
        self.fecha_fin_picker.pack(fill="x", pady=6)
        # Montos
        self.create_section(main_frame, "💰 Montos")
        self.create_field(main_frame, "monto_mensual", "Monto Mensual *", "text")
        self.create_field(main_frame, "deposito", "Depósito", "text")
        self.create_field(main_frame, "gastos_comunes", "Gastos Comunes / Expensas", "text")
        
        # Ajustes
        self.create_section(main_frame, "📈 Ajustes por Inflación (Ley Argentina)")
        self.create_combo_ajuste(main_frame)
        self.create_combo_frecuencia(main_frame)
        
        # Estado
        self.create_combo_estado(main_frame)
        
        # Observaciones
        self.create_section(main_frame, "📝 Observaciones")
        self.create_textbox(main_frame, "observaciones", "Observaciones adicionales")
        
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
        """Crea una sección"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(15, 5))
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")
    
    def create_field(self, parent, name, label, field_type):
        """Crea un campo"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        entry = ctk.CTkEntry(frame, width=340, height=35, font=ctk.CTkFont(size=13))
        entry.pack(side="left", padx=5)
        self.entries[name] = entry
    
    def create_combo_inmueble(self, parent):
        """Selector de inmueble"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Inmueble *",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        inmuebles = self.db_manager.get_inmuebles_disponibles()
        self.inmuebles_dict = {
            f"{i['direccion']} ({i['tipo']})": i['id'] 
            for i in inmuebles
        }
        
        if not self.contrato:
            inmuebles_nombres = list(self.inmuebles_dict.keys())
        else:
            inmueble_actual = self.db_manager.get_by_id('inmuebles', self.contrato['inmueble_id'])
            if inmueble_actual:
                key = f"{inmueble_actual['direccion']} ({inmueble_actual['tipo']})"
                self.inmuebles_dict[key] = inmueble_actual['id']
            inmuebles_nombres = list(self.inmuebles_dict.keys())
        
        if not inmuebles_nombres:
            inmuebles_nombres = ["No hay inmuebles disponibles"]
        
        combo = ctk.CTkComboBox(frame, values=inmuebles_nombres, width=340, height=35)
        combo.pack(side="left", padx=5)
        self.combos['inmueble'] = combo
    
    def create_combo_inquilino(self, parent):
        """Selector de inquilino"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Inquilino *",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        inquilinos = self.db_manager.get_all('inquilinos', 'apellido, nombre')
        self.inquilinos_dict = {
            f"{i['nombre']} {i['apellido']} - {i['cuit_dni']}": i['id']
            for i in inquilinos
        }
        inquilinos_nombres = list(self.inquilinos_dict.keys())
        
        if not inquilinos_nombres:
            inquilinos_nombres = ["No hay inquilinos registrados"]
        
        combo = ctk.CTkComboBox(frame, values=inquilinos_nombres, width=340, height=35)
        combo.pack(side="left", padx=5)
        self.combos['inquilino'] = combo
    
    def create_combo_ajuste(self, parent):
        """Selector de tipo de ajuste"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Tipo de Índice",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        combo = ctk.CTkComboBox(
            frame,
            values=["IPC", "ICL", "fijo", "otro"],
            width=340,
            height=35
        )
        combo.set("IPC")
        combo.pack(side="left", padx=5)
        self.combos['tipo_ajuste'] = combo
    
    def create_combo_frecuencia(self, parent):
        """Selector de frecuencia de ajuste"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Frecuencia de Ajuste (meses)",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        combo = ctk.CTkComboBox(
            frame,
            values=["3", "4", "6", "12"],
            width=340,
            height=35
        )
        combo.set("4")
        combo.pack(side="left", padx=5)
        self.combos['frecuencia_ajuste'] = combo
    
    def create_combo_estado(self, parent):
        """Selector de estado"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Estado",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        combo = ctk.CTkComboBox(
            frame,
            values=["activo", "finalizado", "rescindido", "renovado"],
            width=340,
            height=35
        )
        combo.set("activo")
        combo.pack(side="left", padx=5)
        self.combos['estado'] = combo
    
    def create_textbox(self, parent, name, placeholder):
        """Crea campo de texto multilínea"""
        textbox = ctk.CTkTextbox(parent, width=600, height=80)
        textbox.pack(pady=5)
        self.entries[name] = textbox
    def cargar_datos(self):
        """Carga datos del contrato"""
        if not self.contrato:
            return
        
        # Campos de texto
        # Fechas
        if self.contrato.get('fecha_inicio'):
            self.fecha_inicio_picker.set_date(self.contrato['fecha_inicio'])
        
        if self.contrato.get('fecha_fin'):
            self.fecha_fin_picker.set_date(self.contrato['fecha_fin'])
        
        # Campos de texto (sin fechas)
        campos_texto = ['monto_mensual', 'deposito', 'gastos_comunes']
        for field in campos_texto:
            if field in self.contrato and self.contrato[field]:
                self.entries[field].insert(0, str(self.contrato[field]))
        
        # Observaciones
        if self.contrato.get('observaciones'):
            self.entries['observaciones'].insert("1.0", self.contrato['observaciones'])
        
        # Combos
        if self.contrato.get('tipo_ajuste'):
            self.combos['tipo_ajuste'].set(self.contrato['tipo_ajuste'])
        
        if self.contrato.get('frecuencia_ajuste'):
            self.combos['frecuencia_ajuste'].set(str(self.contrato['frecuencia_ajuste']))
        
        if self.contrato.get('estado'):
            self.combos['estado'].set(self.contrato['estado'])
        
        # Inmueble e inquilino
        if self.contrato.get('inmueble_id'):
            inmueble = self.db_manager.get_by_id('inmuebles', self.contrato['inmueble_id'])
            if inmueble:
                key = f"{inmueble['direccion']} ({inmueble['tipo']})"
                self.combos['inmueble'].set(key)
        
        if self.contrato.get('inquilino_id'):
            inquilino = self.db_manager.get_by_id('inquilinos', self.contrato['inquilino_id'])
            if inquilino:
                key = f"{inquilino['nombre']} {inquilino['apellido']} - {inquilino['cuit_dni']}"
                self.combos['inquilino'].set(key)
    
    def guardar(self):
        """Guarda el contrato"""
        # Obtener datos
        datos = {}
        
        # Inmueble
        inmueble_nombre = self.combos['inmueble'].get()
        if inmueble_nombre in self.inmuebles_dict:
            datos['inmueble_id'] = self.inmuebles_dict[inmueble_nombre]
        else:
            messagebox.showerror("Error", "Debe seleccionar un inmueble válido")
            return
        
        # Inquilino
        inquilino_nombre = self.combos['inquilino'].get()
        if inquilino_nombre in self.inquilinos_dict:
            datos['inquilino_id'] = self.inquilinos_dict[inquilino_nombre]
        else:
            messagebox.showerror("Error", "Debe seleccionar un inquilino válido")
            return
        
        # Fechas
        # Fechas desde los selectores
        datos['fecha_inicio'] = self.fecha_inicio_picker.get_date()
        datos['fecha_fin'] = self.fecha_fin_picker.get_date()
        
        # Obtener objetos datetime para validación
        try:
            fecha_inicio_dt = self.fecha_inicio_picker.get_date_object()
            fecha_fin_dt = self.fecha_fin_picker.get_date_object()

            if fecha_fin_dt <= fecha_inicio_dt:
                messagebox.showerror("Error", "La fecha de fin debe ser posterior a la de inicio")
                return
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use: AAAA-MM-DD")
            return

        # Monto mensual (obligatorio) - validar y convertir
        monto_str = self.entries['monto_mensual'].get().strip()
        if not monto_str:
            messagebox.showerror("Error", "El monto mensual es obligatorio")
            return

        valido, mensaje, monto = self.validators.validar_monto(monto_str)
        if not valido:
            messagebox.showerror("Error", mensaje)
            return

        datos['monto_mensual'] = monto
        
        # Otros montos
        deposito_str = self.entries['deposito'].get().strip()
        if deposito_str:
            valido, mensaje, deposito = self.validators.validar_monto(deposito_str)
            if valido:
                datos['deposito'] = deposito
        
        gastos_str = self.entries['gastos_comunes'].get().strip()
        if gastos_str:
            valido, mensaje, gastos = self.validators.validar_monto(gastos_str)
            if valido:
                datos['gastos_comunes'] = gastos
        
        # Ajustes
        datos['tipo_ajuste'] = self.combos['tipo_ajuste'].get()
        datos['frecuencia_ajuste'] = int(self.combos['frecuencia_ajuste'].get())
        
        # Calcular fecha de próximo ajuste
        fecha_proximo_ajuste = fecha_inicio_dt + relativedelta(months=datos['frecuencia_ajuste'])
        datos['fecha_proximo_ajuste'] = fecha_proximo_ajuste.strftime('%Y-%m-%d')
        
        # Estado
        datos['estado'] = self.combos['estado'].get()
        
        # Observaciones
        datos['observaciones'] = self.entries['observaciones'].get("1.0", "end-1c").strip()
        
        # Guardar
        try:
            if self.contrato:
                if self.db_manager.update('contratos', self.contrato['id'], datos):
                    # Actualizar estado del inmueble
                    if datos['estado'] == 'activo':
                        self.db_manager.update('inmuebles', datos['inmueble_id'], {'estado': 'alquilado'})
                    elif datos['estado'] in ['finalizado', 'rescindido']:
                        self.db_manager.update('inmuebles', datos['inmueble_id'], {'estado': 'disponible'})
                    
                    messagebox.showinfo("Éxito", "Contrato actualizado correctamente")
                    if self.callback:
                        self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el contrato")
            else:
                # Verificar que el inmueble esté disponible
                inmueble = self.db_manager.get_by_id('inmuebles', datos['inmueble_id'])
                if inmueble and inmueble['estado'] != 'disponible':
                    if not messagebox.askyesno(
                        "Advertencia",
                        f"El inmueble está en estado '{inmueble['estado']}'.\n¿Desea continuar?"
                    ):
                        return
                
                if self.db_manager.insert('contratos', datos):
                    # Actualizar estado del inmueble
                    if datos['estado'] == 'activo':
                        self.db_manager.update('inmuebles', datos['inmueble_id'], {'estado': 'alquilado'})
                    
                    messagebox.showinfo("Éxito", "Contrato creado correctamente")
                    if self.callback:
                        self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear el contrato")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")


class DetalleContrato(ctk.CTkToplevel):
    """Ventana de detalle del contrato"""
    
    def __init__(self, parent, contrato, db_manager):
        super().__init__(parent)
        
        self.contrato = contrato
        self.db_manager = db_manager
        
        self.title(f"Contrato #{contrato['id']}")
        self.geometry("700x800")
        
        self.create_detail_view()
        self.transient(parent)
    
    def create_detail_view(self):
        """Crea la vista de detalle"""
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text=f"📝 Contrato #{self.contrato['id']}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(0, 20))
        
        # Información en secciones
        self.add_info_section(main_frame, "🏠 Inmueble", [
            ("Dirección", self.contrato['inmueble_direccion']),
            ("Tipo", self.contrato['inmueble_tipo']),
            ("Partida", self.contrato['partida_inmobiliaria'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "👤 Inquilino", [
            ("Nombre", self.contrato['inquilino_nombre']),
            ("CUIT/DNI", self.contrato['inquilino_cuit']),
            ("Teléfono", self.contrato['inquilino_telefono']),
            ("Email", self.contrato['inquilino_email'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "👥 Propietario", [
            ("Nombre", self.contrato['propietario_nombre'] or "N/A"),
            ("Teléfono", self.contrato['propietario_telefono'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "📅 Fechas", [
            ("Inicio", self.contrato['fecha_inicio']),
            ("Fin", self.contrato['fecha_fin']),
            ("Próximo Ajuste", self.contrato['fecha_proximo_ajuste'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "💰 Montos", [
            ("Mensual", f"${self.contrato['monto_mensual']:,.2f}"),
            ("Depósito", f"${self.contrato['deposito']:,.2f}" if self.contrato['deposito'] else "N/A"),
            ("Gastos Comunes", f"${self.contrato['gastos_comunes']:,.2f}" if self.contrato['gastos_comunes'] else "N/A"),
        ])
        
        self.add_info_section(main_frame, "📈 Ajustes", [
            ("Tipo", self.contrato['tipo_ajuste']),
            ("Frecuencia", f"Cada {self.contrato['frecuencia_ajuste']} meses"),
            ("Estado", self.contrato['estado']),
        ])
        
        if self.contrato.get('observaciones'):
            self.add_info_section(main_frame, "📝 Observaciones", [
                ("", self.contrato['observaciones']),
            ])
        
        # Historial de ajustes
        self.mostrar_historial_ajustes(main_frame)
        
        # Botón cerrar
        ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.destroy,
            width=200,
            height=40
        ).pack(pady=20)
    
    def add_info_section(self, parent, title, items):
        """Agrega sección de información"""
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
                    wraplength=600,
                    justify="left"
                ).pack(padx=20, pady=10)
    
    def mostrar_historial_ajustes(self, parent):
        """Muestra historial de ajustes del contrato"""
        query = '''
            SELECT *
            FROM ajustes_contratos
            WHERE contrato_id = ?
            ORDER BY fecha_ajuste DESC
        '''
        ajustes = self.db_manager.execute_query(query, (self.contrato['id'],))
        
        if ajustes:
            frame = ctk.CTkFrame(parent, corner_radius=10)
            frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                frame,
                text="📊 Historial de Ajustes",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=(15, 10))
            
            for ajuste in ajustes:
                ajuste_frame = ctk.CTkFrame(frame, fg_color="transparent")
                ajuste_frame.pack(fill="x", padx=20, pady=5)
                
                texto = f"📅 {ajuste['fecha_ajuste']} - " \
                       f"${ajuste['monto_anterior']:,.0f} → ${ajuste['monto_nuevo']:,.0f} " \
                       f"({ajuste['porcentaje_ajuste']:.2f}% {ajuste['tipo_indice']})"
                
                ctk.CTkLabel(
                    ajuste_frame,
                    text=texto,
                    font=ctk.CTkFont(size=12)
                ).pack(anchor="w")
class AplicarAjuste(ctk.CTkToplevel):
    """Ventana para aplicar ajuste a un contrato"""
    
    def __init__(self, parent, contrato_id, db_manager, callback):
        super().__init__(parent)
        
        self.contrato_id = contrato_id
        self.db_manager = db_manager
        self.callback = callback
        
        self.contrato = db_manager.get_by_id('contratos', contrato_id)
        
        self.title("Aplicar Ajuste de Contrato")
        self.geometry("500x550")
        self.resizable(False, False)
        
        self.center_window()
        self.create_form()
        
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
        """Crea el formulario de ajuste"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        title = ctk.CTkLabel(
            main_frame,
            text="📈 Aplicar Ajuste de Alquiler",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Info actual
        info_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#e8f4f8", "#1a3a4a"))
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Monto Actual: ${self.contrato['monto_mensual']:,.2f}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Tipo de ajuste: {self.contrato['tipo_ajuste']}",
            font=ctk.CTkFont(size=13)
        ).pack(pady=5)
        
        # Fecha del ajuste
        fecha_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        fecha_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            fecha_frame,
            text="Fecha del Ajuste (AAAA-MM-DD):",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=5)
        
        self.fecha_entry = ctk.CTkEntry(fecha_frame, width=400, height=35)
        self.fecha_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.fecha_entry.pack(pady=5)
        
        # Porcentaje de ajuste
        porcent_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        porcent_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            porcent_frame,
            text="Porcentaje de Ajuste (%):",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=5)
        
        self.porcentaje_entry = ctk.CTkEntry(porcent_frame, width=400, height=35)
        self.porcentaje_entry.pack(pady=5)
        
        # Observaciones
        obs_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        obs_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            obs_frame,
            text="Observaciones:",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=5)
        
        self.observaciones_text = ctk.CTkTextbox(obs_frame, width=400, height=80)
        self.observaciones_text.pack(pady=5)
        
        # Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="✅ Aplicar Ajuste",
            command=self.aplicar,
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
    
    def aplicar(self):
        """Aplica el ajuste"""
        # Validar fecha
        fecha_str = self.fecha_entry.get().strip()
        try:
            fecha_ajuste = datetime.strptime(fecha_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido")
            return
        
        # Validar porcentaje
        porcentaje_str = self.porcentaje_entry.get().strip()
        try:
            porcentaje = float(porcentaje_str.replace(',', '.'))
            if porcentaje <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Porcentaje inválido")
            return
        
        # Calcular nuevo monto
        monto_anterior = self.contrato['monto_mensual']
        monto_nuevo = monto_anterior * (1 + porcentaje / 100)
        
        # Confirmar
        if not messagebox.askyesno(
            "Confirmar Ajuste",
            f"Monto anterior: ${monto_anterior:,.2f}\n" +
            f"Porcentaje: {porcentaje}%\n" +
            f"Nuevo monto: ${monto_nuevo:,.2f}\n\n" +
            f"¿Aplicar este ajuste?"
        ):
            return
        
        # Guardar en historial
        ajuste_datos = {
            'contrato_id': self.contrato_id,
            'fecha_ajuste': fecha_str,
            'monto_anterior': monto_anterior,
            'monto_nuevo': monto_nuevo,
            'porcentaje_ajuste': porcentaje,
            'tipo_indice': self.contrato['tipo_ajuste'],
            'observaciones': self.observaciones_text.get("1.0", "end-1c").strip()
        }
        
        if not self.db_manager.insert('ajustes_contratos', ajuste_datos):
            messagebox.showerror("Error", "No se pudo guardar el ajuste")
            return
        
        # Actualizar contrato
        frecuencia = self.contrato['frecuencia_ajuste']
        proximo_ajuste = fecha_ajuste + relativedelta(months=frecuencia)
        
        contrato_datos = {
            'monto_mensual': monto_nuevo,
            'fecha_ultimo_ajuste': fecha_str,
            'fecha_proximo_ajuste': proximo_ajuste.strftime('%Y-%m-%d')
        }
        
        if self.db_manager.update('contratos', self.contrato_id, contrato_datos):
            messagebox.showinfo(
                "Éxito",
                f"Ajuste aplicado correctamente\n\n" +
                f"Nuevo monto: ${monto_nuevo:,.2f}\n" +
                f"Próximo ajuste: {proximo_ajuste.strftime('%Y-%m-%d')}"
            )
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el contrato")