# modules/pagos.py - Módulo de Gestión de Pagos
import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from datetime import datetime
from calendar import monthrange

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from utils.validators import Validators, validar_formulario
from utils.pdf_generator import ReciboPDF, DialogoImpresion, generar_recibo_pago
from components.date_picker import DatePicker, formato_db_a_visual, formato_visual_a_db

class PagosModule(ctk.CTkFrame):
    """Módulo completo de gestión de pagos"""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        super().__init__(parent, fg_color="transparent")
        
        self.db_manager = db_manager
        self.validators = Validators()
        self.pagos = []
        
        self.create_widgets()
        self.cargar_pagos()
    
    def create_widgets(self):
        """Crea la interfaz del módulo"""
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="💰 Gestión de Pagos",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Frame de acciones
        actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(
            actions_frame,
            text="➕ Registrar Pago",
            command=self.abrir_formulario_nuevo,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="🔄 Actualizar",
            command=self.cargar_pagos,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3498db"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="📊 Ver Saldos",
            command=self.mostrar_saldos,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#9b59b6"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="📄 Generar Recibo",
            command=self.generar_recibo_seleccionado,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e67e22"
        ).pack(side="left", padx=5)
        
        # Filtros
        filter_frame = ctk.CTkFrame(container, fg_color="transparent")
        filter_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(filter_frame, text="Año:", font=ctk.CTkFont(size=13)).pack(side="left", padx=5)
        
        años = [str(y) for y in range(datetime.now().year - 2, datetime.now().year + 2)]
        self.filter_anio = ctk.CTkOptionMenu(
            filter_frame,
            values=["Todos"] + años,
            command=self.filtrar_por_periodo,
            width=100
        )
        self.filter_anio.set(str(datetime.now().year))
        self.filter_anio.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Mes:", font=ctk.CTkFont(size=13)).pack(side="left", padx=5)
        
        meses = ["Todos", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.filter_mes = ctk.CTkOptionMenu(
            filter_frame,
            values=meses,
            command=self.filtrar_por_periodo,
            width=100
        )
        self.filter_mes.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="🔍 Buscar:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(20, 5))
        
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Inquilino o dirección...",
            width=250,
            height=35
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.buscar())
        
        # Frame de lista
        self.list_frame = ctk.CTkFrame(container, corner_radius=10)
        self.list_frame.pack(fill="both", expand=True, pady=10)
        
        # Variable para el pago seleccionado
        self.pago_seleccionado = None
    
    def cargar_pagos(self):
        """Carga todos los pagos"""
        self.search_entry.delete(0, 'end')
        
        query = '''
            SELECT p.*,
                   i.direccion as inmueble_direccion,
                   inq.nombre || ' ' || inq.apellido as inquilino_nombre,
                   prop.nombre || ' ' || prop.apellido as propietario_nombre
            FROM pagos p
            JOIN contratos c ON p.contrato_id = c.id
            JOIN inmuebles i ON c.inmueble_id = i.id
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            LEFT JOIN propietarios prop ON i.propietario_id = prop.id
            ORDER BY p.fecha_pago DESC, p.periodo_anio DESC, p.periodo_mes DESC
        '''
        self.pagos = self.db_manager.execute_query(query)
        self.filtrar_por_periodo(None)
    
    def filtrar_por_periodo(self, _):
        """Filtra pagos por año y mes"""
        anio = self.filter_anio.get()
        mes = self.filter_mes.get()
        
        filtrados = self.pagos
        
        if anio != "Todos":
            filtrados = [p for p in filtrados if p['periodo_anio'] == int(anio)]
        
        if mes != "Todos":
            filtrados = [p for p in filtrados if p['periodo_mes'] == int(mes)]
        
        self.mostrar_pagos(filtrados)
    
    def buscar(self):
        """Busca pagos por texto"""
        termino = self.search_entry.get().strip().lower()
        
        if not termino:
            self.filtrar_por_periodo(None)
            return
        
        filtrados = [
            p for p in self.pagos
            if termino in p['inquilino_nombre'].lower() or
               termino in p['inmueble_direccion'].lower() or
               (p['propietario_nombre'] and termino in p['propietario_nombre'].lower())
        ]
        
        self.mostrar_pagos(filtrados)
    
    def mostrar_pagos(self, pagos):
        """Muestra la lista de pagos"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not pagos:
            ctk.CTkLabel(
                self.list_frame,
                text="No se encontraron pagos",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Encabezados
        headers = ["☑", "ID", "Fecha", "Período", "Inquilino", "Inmueble", "Total", "Alq", "Exp", "EMSA", "SAMSA", "Acciones"]
        header_frame = ctk.CTkFrame(self.list_frame, fg_color="#2ecc71")
        header_frame.pack(fill="x", padx=5, pady=5)
        
        widths = [30, 40, 90, 80, 140, 160, 90, 80, 60, 70, 70, 120]
        for i, (header, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white",
                width=width
            ).grid(row=0, column=i, padx=2, pady=8, sticky="w")
        
        for pago in pagos:
            self.crear_fila_pago(pago)
    
    def crear_fila_pago(self, pago):
        """Crea una fila para un pago"""
        row_frame = ctk.CTkFrame(self.list_frame, fg_color=("#ffffff", "#2d2d2d"))
        row_frame.pack(fill="x", padx=5, pady=2)
        
        widths = [30, 40, 90, 80, 140, 160, 90, 80, 60, 70, 70, 120]
        
        # Checkbox para seleccionar
        var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=var,
            width=30,
            command=lambda: self.seleccionar_pago(pago['id'], var.get())
        )
        checkbox.grid(row=0, column=0, padx=2, pady=5)
        
        meses = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        periodo = f"{meses[pago['periodo_mes']]}/{pago['periodo_anio']}"
        
        datos = [
            str(pago['id']),
            pago['fecha_pago'],
            periodo,
            pago['inquilino_nombre'][:18] + "..." if len(pago['inquilino_nombre']) > 18 else pago['inquilino_nombre'],
            pago['inmueble_direccion'][:22] + "..." if len(pago['inmueble_direccion']) > 22 else pago['inmueble_direccion'],
            f"${pago['monto_total']:,.0f}",
            f"${pago['monto_alquiler']:,.0f}",
            f"${pago['monto_expensas']:,.0f}" if pago['monto_expensas'] else "-",
            f"${pago['monto_emsa']:,.0f}" if pago['monto_emsa'] else "-",
            f"${pago['monto_samsa']:,.0f}" if pago['monto_samsa'] else "-"
        ]
        
        for i, (dato, width) in enumerate(zip(datos, widths[1:-1]), start=1):
            ctk.CTkLabel(
                row_frame,
                text=dato,
                font=ctk.CTkFont(size=10),
                width=width,
                anchor="w"
            ).grid(row=0, column=i, padx=2, pady=5, sticky="w")
        
        # Botones de acción
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=11, padx=2, pady=2)
        
        ctk.CTkButton(
            action_frame,
            text="👁️",
            width=32,
            height=26,
            command=lambda: self.ver_detalle(pago['id']),
            fg_color="#3498db"
        ).pack(side="left", padx=1)
        
        ctk.CTkButton(
            action_frame,
            text="📄",
            width=32,
            height=26,
            command=lambda: self.generar_recibo(pago['id']),
            fg_color="#e67e22"
        ).pack(side="left", padx=1)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️",
            width=32,
            height=26,
            command=lambda: self.eliminar_pago(pago['id']),
            fg_color="#e74c3c"
        ).pack(side="left", padx=1)
    
    def seleccionar_pago(self, pago_id, seleccionado):
        """Selecciona un pago para generar recibo"""
        if seleccionado:
            self.pago_seleccionado = pago_id
        else:
            self.pago_seleccionado = None
    
    def abrir_formulario_nuevo(self):
        """Abre el formulario para nuevo pago"""
        FormularioPago(self, self.db_manager, None, self.cargar_pagos)

    def ver_detalle(self, pago_id):
        """Muestra detalle del pago"""
        query = '''
            SELECT p.*,
                   c.monto_mensual as monto_contrato,
                   i.direccion as inmueble_direccion,
                   i.partida_inmobiliaria,
                   i.conexion_emsa,
                   i.conexion_samsa,
                   inq.nombre || ' ' || inq.apellido as inquilino_nombre,
                   inq.cuit_dni as inquilino_cuit,
                   prop.nombre || ' ' || prop.apellido as propietario_nombre
            FROM pagos p
            JOIN contratos c ON p.contrato_id = c.id
            JOIN inmuebles i ON c.inmueble_id = i.id
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            LEFT JOIN propietarios prop ON i.propietario_id = prop.id
            WHERE p.id = ?
        '''
        resultado = self.db_manager.execute_query(query, (pago_id,))
        
        if resultado:
            DetallePago(self, resultado[0], self.db_manager)
    
    def generar_recibo(self, pago_id):
        """Genera recibo para un pago"""
        try:
            # Generar PDF
            generador = ReciboPDF(self.db_manager)
            ruta, mensaje = generador.generar_recibo(pago_id, abrir_pdf=True)
            
            if not ruta:
                messagebox.showerror("Error", mensaje)
                return
            
            # Preguntar si desea imprimir
            respuesta = DialogoImpresion.preguntar_impresion()
            
            if respuesta is True:  # Imprimir
                exito, msg_impresion = generador.imprimir_pdf(ruta)
                if exito:
                    messagebox.showinfo("Éxito", f"{mensaje}\n\n{msg_impresion}")
                else:
                    messagebox.showwarning("Advertencia", f"{mensaje}\n\nPero hubo un problema al imprimir:\n{msg_impresion}")
            elif respuesta is False:  # Solo ver
                messagebox.showinfo("Éxito", mensaje)
            # Si es None (Cancelar), no hace nada más
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar recibo:\n{str(e)}")

    def generar_recibo_seleccionado(self):
        """Genera recibo del pago seleccionado"""
        if not self.pago_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un pago marcando el checkbox")
            return
        
        self.generar_recibo(self.pago_seleccionado)
    
    def eliminar_pago(self, pago_id):
        """Elimina un pago"""
        if messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro que desea eliminar este pago?"
        ):
            if self.db_manager.delete('pagos', pago_id):
                messagebox.showinfo("Éxito", "Pago eliminado correctamente")
                self.cargar_pagos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el pago")
    
    def mostrar_saldos(self):
        """Muestra saldos de inquilinos"""
        VentanaSaldos(self, self.db_manager)


class FormularioPago(ctk.CTkToplevel):
    """Formulario para registrar pagos"""
    
    def __init__(self, parent, db_manager: DatabaseManager, pago=None, callback=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.pago = pago
        self.callback = callback
        self.validators = Validators()
        
        self.title("Registrar Pago")
        self.geometry("750x700")
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
        """Crea el formulario"""
        # Frame con scroll
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        title = ctk.CTkLabel(
            main_frame,
            text="💰 Registrar Pago",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        self.entries = {}
        self.combos = {}
        
        # Contrato
        self.create_combo_contrato(main_frame)
        
        # Botón para cargar datos del contrato
        ctk.CTkButton(
            main_frame,
            text="📥 Cargar datos del contrato",
            command=self.cargar_datos_contrato,
            height=35,
            fg_color="#3498db"
        ).pack(pady=10)
        
        # Período
        self.create_section(main_frame, "📅 Período del Pago")
        self.create_combo_mes(main_frame)
        self.create_combo_anio(main_frame)
        
        # Fecha de pago con selector
        self.fecha_pago_picker = DatePicker(main_frame, label_text="Fecha de Pago *")
        self.fecha_pago_picker.pack(fill="x", pady=6)
        
        # Montos
        self.create_section(main_frame, "💵 Montos")
        self.create_field(main_frame, "monto_alquiler", "Monto Alquiler *", "text")
        self.create_field(main_frame, "monto_expensas", "Expensas / Gastos Comunes", "text")
        self.create_field(main_frame, "monto_emsa", "EMSA (Luz)", "text")
        self.create_field(main_frame, "monto_samsa", "SAMSA (Agua)", "text")
        self.create_field(main_frame, "monto_otros", "Otros Conceptos", "text")
        
        # Total (calculado automáticamente)
        self.total_label = ctk.CTkLabel(
            main_frame,
            text="Total: $0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2ecc71"
        )
        self.total_label.pack(pady=10)
        
        # Botón calcular
        ctk.CTkButton(
            main_frame,
            text="🧮 Calcular Total",
            command=self.calcular_total,
            height=35,
            fg_color="#9b59b6"
        ).pack(pady=5)
        
        # Método de pago
        self.create_combo_metodo_pago(main_frame)
        
        # Concepto y comprobante
        self.create_field(main_frame, "concepto", "Concepto", "text")
        self.create_field(main_frame, "comprobante", "N° Comprobante / Recibo", "text")
        
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
    
    def create_combo_contrato(self, parent):
        """Selector de contrato"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Contrato *",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        # Obtener contratos activos
        contratos = self.db_manager.get_contratos_activos()
        self.contratos_dict = {}
        
        for c in contratos:
            key = f"{c['inquilino_nombre']} - {c['inmueble_direccion']}"
            self.contratos_dict[key] = {
                'id': c['id'],
                'monto_mensual': c['monto_mensual'],
                'gastos_comunes': c['gastos_comunes'] or 0
            }
        
        contratos_nombres = list(self.contratos_dict.keys())
        
        if not contratos_nombres:
            contratos_nombres = ["No hay contratos activos"]
        
        combo = ctk.CTkComboBox(frame, values=contratos_nombres, width=340, height=35)
        combo.pack(side="left", padx=5)
        self.combos['contrato'] = combo
    
    def create_combo_mes(self, parent):
        """Selector de mes"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Mes *",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        combo = ctk.CTkComboBox(frame, values=meses, width=340, height=35)
        combo.set(meses[datetime.now().month - 1])
        combo.pack(side="left", padx=5)
        self.combos['periodo_mes'] = combo
    
    def create_combo_anio(self, parent):
        """Selector de año"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Año *",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        años = [str(y) for y in range(datetime.now().year - 1, datetime.now().year + 2)]
        
        combo = ctk.CTkComboBox(frame, values=años, width=340, height=35)
        combo.set(str(datetime.now().year))
        combo.pack(side="left", padx=5)
        self.combos['periodo_anio'] = combo
    
    def create_combo_metodo_pago(self, parent):
        """Selector de método de pago"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            frame,
            text="Método de Pago",
            font=ctk.CTkFont(size=13),
            anchor="w",
            width=260
        ).pack(side="left", padx=5)
        
        combo = ctk.CTkComboBox(
            frame,
            values=["efectivo", "transferencia", "cheque", "tarjeta", "otro"],
            width=340,
            height=35
        )
        combo.set("transferencia")
        combo.pack(side="left", padx=5)
        self.combos['metodo_pago'] = combo
    
    def cargar_datos_contrato(self):
        """Carga automáticamente los montos del contrato"""
        contrato_nombre = self.combos['contrato'].get()
        
        if contrato_nombre not in self.contratos_dict:
            messagebox.showerror("Error", "Seleccione un contrato válido")
            return
        
        contrato_info = self.contratos_dict[contrato_nombre]
        
        # Cargar monto de alquiler
        self.entries['monto_alquiler'].delete(0, 'end')
        self.entries['monto_alquiler'].insert(0, str(contrato_info['monto_mensual']))
        
        # Cargar gastos comunes
        if contrato_info['gastos_comunes'] > 0:
            self.entries['monto_expensas'].delete(0, 'end')
            self.entries['monto_expensas'].insert(0, str(contrato_info['gastos_comunes']))
        
        # Poner fecha actual en el selector
        self.fecha_pago_picker.set_date(datetime.now().strftime('%Y-%m-%d'))
        
        messagebox.showinfo("Éxito", "Datos del contrato cargados correctamente")
        self.calcular_total()
    
    def calcular_total(self):
        """Calcula el total del pago"""
        total = 0.0
        
        campos_montos = ['monto_alquiler', 'monto_expensas', 'monto_emsa', 'monto_samsa', 'monto_otros']
        
        for campo in campos_montos:
            valor_str = self.entries[campo].get().strip()
            if valor_str:
                try:
                    valor = float(valor_str.replace(',', '.'))
                    total += valor
                except ValueError:
                    pass
        
        self.total_label.configure(text=f"Total: ${total:,.2f}")

    def guardar(self):
        """Guarda el pago"""
        # Obtener contrato
        contrato_nombre = self.combos['contrato'].get()
        if contrato_nombre not in self.contratos_dict:
            messagebox.showerror("Error", "Debe seleccionar un contrato válido")
            return
        
        datos = {}
        datos['contrato_id'] = self.contratos_dict[contrato_nombre]['id']
        
        # Período
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_nombre = self.combos['periodo_mes'].get()
        datos['periodo_mes'] = meses.index(mes_nombre) + 1
        datos['periodo_anio'] = int(self.combos['periodo_anio'].get())
        
        # Fecha de pago
        datos['fecha_pago'] = self.fecha_pago_picker.get_date()
        
        # Montos
        campos_montos = {
            'monto_alquiler': True,  # obligatorio
            'monto_expensas': False,
            'monto_emsa': False,
            'monto_samsa': False,
            'monto_otros': False
        }
        
        total = 0.0
        
        for campo, obligatorio in campos_montos.items():
            valor_str = self.entries[campo].get().strip()
            
            if obligatorio and not valor_str:
                messagebox.showerror("Error", f"{campo.replace('_', ' ').title()} es obligatorio")
                return
            
            if valor_str:
                valido, mensaje, monto = self.validators.validar_monto(valor_str)
                if not valido:
                    messagebox.showerror("Error", f"{campo}: {mensaje}")
                    return
                
                datos[campo] = monto
                total += monto
            else:
                datos[campo] = 0
        
        datos['monto_total'] = total
        
        # Otros datos
        datos['metodo_pago'] = self.combos['metodo_pago'].get()
        datos['concepto'] = self.entries['concepto'].get().strip()
        datos['comprobante'] = self.entries['comprobante'].get().strip()
        
        # Verificar si ya existe un pago para este período
        query = '''
            SELECT COUNT(*) as total 
            FROM pagos 
            WHERE contrato_id = ? 
            AND periodo_mes = ? 
            AND periodo_anio = ?
        '''
        resultado = self.db_manager.execute_query(
            query, 
            (datos['contrato_id'], datos['periodo_mes'], datos['periodo_anio'])
        )
        
        if resultado and resultado[0]['total'] > 0:
            if not messagebox.askyesno(
                "Advertencia",
                "Ya existe un pago registrado para este período.\n¿Desea continuar?"
            ):
                return
        
        # Guardar
        try:
            if self.db_manager.insert('pagos', datos):
                messagebox.showinfo(
                    "Éxito", 
                    f"Pago registrado correctamente\n\nTotal: ${total:,.2f}"
                )
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo registrar el pago")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")


class DetallePago(ctk.CTkToplevel):
    """Ventana de detalle del pago"""
    
    def __init__(self, parent, pago, db_manager):
        super().__init__(parent)
        
        self.pago = pago
        self.db_manager = db_manager
        
        self.title(f"Pago #{pago['id']}")
        self.geometry("650x750")
        
        self.create_detail_view()
        self.transient(parent)
    
    def create_detail_view(self):
        """Crea la vista de detalle"""
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text=f"💰 Pago #{self.pago['id']}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(0, 20))
        
        meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Información en secciones
        self.add_info_section(main_frame, "📅 Información del Pago", [
            ("Fecha de Pago", self.pago['fecha_pago']),
            ("Período", f"{meses[self.pago['periodo_mes']]} {self.pago['periodo_anio']}"),
            ("Método de Pago", self.pago['metodo_pago'] or "N/A"),
            ("Comprobante", self.pago['comprobante'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "🏠 Inmueble", [
            ("Dirección", self.pago['inmueble_direccion']),
            ("Partida", self.pago['partida_inmobiliaria'] or "N/A"),
            ("EMSA", self.pago['conexion_emsa'] or "N/A"),
            ("SAMSA", self.pago['conexion_samsa'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "👤 Inquilino", [
            ("Nombre", self.pago['inquilino_nombre']),
            ("CUIT/DNI", self.pago['inquilino_cuit']),
        ])
        
        self.add_info_section(main_frame, "👥 Propietario", [
            ("Nombre", self.pago['propietario_nombre'] or "N/A"),
        ])
        
        self.add_info_section(main_frame, "💵 Detalle de Montos", [
            ("Alquiler", f"${self.pago['monto_alquiler']:,.2f}"),
            ("Expensas", f"${self.pago['monto_expensas']:,.2f}" if self.pago['monto_expensas'] else "$ 0.00"),
            ("EMSA (Luz)", f"${self.pago['monto_emsa']:,.2f}" if self.pago['monto_emsa'] else "$ 0.00"),
            ("SAMSA (Agua)", f"${self.pago['monto_samsa']:,.2f}" if self.pago['monto_samsa'] else "$ 0.00"),
            ("Otros", f"${self.pago['monto_otros']:,.2f}" if self.pago['monto_otros'] else "$ 0.00"),
        ])
        
        # Total destacado
        total_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#2ecc71")
        total_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            total_frame,
            text=f"TOTAL: ${self.pago['monto_total']:,.2f}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=20)
        
        if self.pago.get('concepto'):
            self.add_info_section(main_frame, "📝 Concepto", [
                ("", self.pago['concepto']),
            ])
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="📄 Generar Recibo",
            width=180,
            height=40,
            command=lambda: messagebox.showinfo("Info", "Función de PDF en desarrollo")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            command=self.destroy,
            width=180,
            height=40
        ).pack(side="left", padx=5)
    
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
                    wraplength=550,
                    justify="left"
                ).pack(padx=20, pady=10)

class VentanaSaldos(ctk.CTkToplevel):
    """Ventana para ver saldos de inquilinos (a favor o en contra)"""
    
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        
        self.db_manager = db_manager
        
        self.title("Saldos de Inquilinos")
        self.geometry("1000x650")
        
        self.create_saldos_view()
        self.transient(parent)
    
    def create_saldos_view(self):
        """Crea la vista de saldos"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text="📊 Estado de Cuentas por Inquilino",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(0, 20))
        
        # Info sobre saldos
        info_frame = ctk.CTkFrame(main_frame, fg_color=("#e8f4f8", "#1a3a4a"), corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_text = (
            "🟢 A FAVOR: El inquilino pagó de más\n"
            "🔴 DEUDA: El inquilino debe más de un mes\n"
            "⚪ AL DÍA: Pagos al día (puede tener pequeñas diferencias)"
        )
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(pady=15, padx=20)
        
        # Calcular saldos
        saldos = self.calcular_saldos()
        
        if not saldos:
            ctk.CTkLabel(
                main_frame,
                text="No hay contratos activos con información de saldos",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)
            return
        
        # Crear tabla de saldos
        list_frame = ctk.CTkScrollableFrame(main_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Encabezados
        headers = ["Inquilino", "Inmueble", "Contrato", "Total Pagado", "Meses", "Esperado", "Saldo", "Estado"]
        header_frame = ctk.CTkFrame(list_frame, fg_color="#9b59b6")
        header_frame.pack(fill="x", padx=5, pady=5)
        
        widths = [160, 180, 100, 110, 70, 110, 110, 100]
        for i, (header, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
                width=width
            ).grid(row=0, column=i, padx=5, pady=10)
        
        # Datos
        for saldo in saldos:
            self.crear_fila_saldo(list_frame, saldo, widths)
        
        # Resumen total
        resumen_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("#e8f4f8", "#1a3a4a"))
        resumen_frame.pack(fill="x", pady=15)
        
        total_a_favor = sum(s['saldo'] for s in saldos if s['saldo'] > 0)
        total_deuda = sum(abs(s['saldo']) for s in saldos if s['saldo'] < 0)
        
        resumen_text = f"Total A Favor: ${total_a_favor:,.2f}  |  Total Deuda: ${total_deuda:,.2f}"
        
        ctk.CTkLabel(
            resumen_frame,
            text=resumen_text,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=12)
        
        # Botón cerrar
        ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.destroy,
            width=200,
            height=40
        ).pack(pady=10)
    
    def calcular_saldos(self):
        """Calcula los saldos de cada inquilino"""
        query = '''
            SELECT 
                c.id as contrato_id,
                inq.nombre || ' ' || inq.apellido as inquilino_nombre,
                i.direccion as inmueble_direccion,
                c.monto_mensual as monto_contrato,
                SUM(p.monto_total) as total_pagado,
                COUNT(p.id) as cantidad_pagos,
                julianday('now') - julianday(c.fecha_inicio) as dias_transcurridos
            FROM contratos c
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            JOIN inmuebles i ON c.inmueble_id = i.id
            LEFT JOIN pagos p ON c.id = p.contrato_id
            WHERE c.estado = 'activo'
            GROUP BY c.id
            ORDER BY inquilino_nombre
        '''
        
        resultados = self.db_manager.execute_query(query)
        
        saldos = []
        for r in resultados:
            # Calcular meses transcurridos (aproximado)
            meses_transcurridos = max(1, int(r['dias_transcurridos'] / 30))
            
            # Monto esperado total
            monto_esperado = r['monto_contrato'] * meses_transcurridos
            
            # Total pagado
            total_pagado = r['total_pagado'] or 0
            
            # Saldo (positivo = a favor, negativo = deuda)
            saldo = total_pagado - monto_esperado
            
            # Determinar estado
            estado = "Al día"
            if saldo > r['monto_contrato'] * 0.1:  # Más del 10% de un mes a favor
                estado = "A favor"
            elif saldo < -r['monto_contrato']:  # Debe más de un mes completo
                estado = "Deuda"
            
            saldos.append({
                'inquilino': r['inquilino_nombre'],
                'inmueble': r['inmueble_direccion'],
                'monto_contrato': r['monto_contrato'],
                'total_pagado': total_pagado,
                'meses_transcurridos': meses_transcurridos,
                'monto_esperado': monto_esperado,
                'saldo': saldo,
                'estado': estado
            })
        
        return saldos
    
    def crear_fila_saldo(self, parent, saldo, widths):
        """Crea una fila de saldo"""
        row_frame = ctk.CTkFrame(parent, fg_color=("#ffffff", "#2d2d2d"))
        row_frame.pack(fill="x", padx=5, pady=2)
        
        colors = {
            "Al día": "green",
            "A favor": "blue",
            "Deuda": "red"
        }
        
        # Formato de saldo con símbolo
        saldo_texto = f"${abs(saldo['saldo']):,.2f}"
        if saldo['saldo'] > 0:
            saldo_texto = f"+{saldo_texto}"
        elif saldo['saldo'] < 0:
            saldo_texto = f"-{saldo_texto}"
        
        datos = [
            saldo['inquilino'][:22] + "..." if len(saldo['inquilino']) > 22 else saldo['inquilino'],
            saldo['inmueble'][:25] + "..." if len(saldo['inmueble']) > 25 else saldo['inmueble'],
            f"${saldo['monto_contrato']:,.0f}",
            f"${saldo['total_pagado']:,.2f}",
            str(saldo['meses_transcurridos']),
            f"${saldo['monto_esperado']:,.2f}",
            saldo_texto,
            saldo['estado']
        ]
        
        for i, (dato, width) in enumerate(zip(datos, widths)):
            # Color especial para saldo y estado
            color = None
            if i == 6:  # Saldo
                color = "blue" if saldo['saldo'] > 0 else ("red" if saldo['saldo'] < 0 else "gray")
            elif i == 7:  # Estado
                color = colors.get(saldo['estado'])
            
            ctk.CTkLabel(
                row_frame,
                text=dato,
                font=ctk.CTkFont(size=11),
                width=width,
                text_color=color
            ).grid(row=0, column=i, padx=5, pady=8)

    