# main.py - Sistema de Gestión Inmobiliaria - Versión Modular
import customtkinter as ctk
from tkinter import messagebox
import threading
import bcrypt

# Importar módulos propios
from modules.contratos import ContratosModule
from modules.propietarios import PropietariosModule
from database import DatabaseManager
from supabase_sync import SupabaseSync
from modules.inquilinos import InquilinosModule
from modules.inmuebles import InmueblesModule
from modules.pagos import PagosModule
from utils.config_empresa import ConfigEmpresa
from PIL import Image, ImageTk

# Configuración de CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# CONFIGURACIÓN DE SUPABASE
SUPABASE_URL = "https://hqicpusqpzphmnbgwhao.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhxaWNwdXNxcHpwaG1uYmd3aGFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0MzQ4ODcsImV4cCI6MjA4MTAxMDg4N30.HNrA6Zd-Mk3vus9txWqYbYQFAH9FChSQlEPrKuDTkKU"

class LoginWindow(ctk.CTk):
    """Ventana de inicio de sesión"""
    
    def __init__(self, db_manager):
        super().__init__()
        
        self.db_manager = db_manager
        self.user_data = None
        
        # Configuración de la ventana
        # Configuración de la ventana
        self.title(f"{ConfigEmpresa.NOMBRE} - Sistema de Gestión Inmobiliaria")
        
        # Establecer icono de la ventana (si existe favicon)
        if ConfigEmpresa.favicon_existe():
            try:
                self.iconphoto(True, ImageTk.PhotoImage(file=ConfigEmpresa.FAVICON_PATH))
            except:
                pass  # Si falla, continuar sin icono
        self.geometry("450x550")
        self.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Crear interfaz
        self.create_widgets()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea los widgets de la interfaz"""
        # Frame principal con color de fondo
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#f0f0f0", "#1a1a1a"))
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo/Título
        # Logo de CONECTAR
        if ConfigEmpresa.logo_existe():
            try:
                # Cargar imagen
                logo_img = Image.open(ConfigEmpresa.LOGO_PATH)
                
                # Redimensionar manteniendo proporción (ancho máximo 250px)
                ancho_original, alto_original = logo_img.size
                nuevo_ancho = 250
                nuevo_alto = int((nuevo_ancho / ancho_original) * alto_original)
                logo_img = logo_img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
                
                # Convertir para CTk
                logo_photo = ctk.CTkImage(
                    light_image=logo_img,
                    dark_image=logo_img,
                    size=(nuevo_ancho, nuevo_alto)
                )
                
                # Mostrar logo
                logo_label = ctk.CTkLabel(
                    main_frame,
                    image=logo_photo,
                    text=""
                )
                logo_label.image = logo_photo  # Mantener referencia
                logo_label.pack(pady=(40, 20))
            except Exception as e:
                print(f"Error cargando logo: {e}")
                # Fallback a texto
                title_label = ctk.CTkLabel(
                    main_frame,
                    text=f"🏢 {ConfigEmpresa.NOMBRE}",
                    font=ctk.CTkFont(size=28, weight="bold"),
                    text_color=("#1a1a1a", "#ffffff")
                )
                title_label.pack(pady=(50, 10))
        else:
            # Si no hay logo, mostrar texto
            title_label = ctk.CTkLabel(
                main_frame,
                text=f"🏢 {ConfigEmpresa.NOMBRE}",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=("#1a1a1a", "#ffffff")
            )
            title_label.pack(pady=(50, 10))
        
        # Subtítulo con datos de la empresa
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text=f"Gestión Profesional de Propiedades\n{ConfigEmpresa.DIRECCION_1}\n{ConfigEmpresa.DIRECCION_2}",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#999999"),
            justify="center"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Campo de usuario
        self.username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="👤 Usuario",
            width=320,
            height=45,
            font=ctk.CTkFont(size=14),
            border_width=2
        )
        self.username_entry.pack(pady=12)
        
        # Campo de contraseña
        self.password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="🔒 Contraseña",
            show="•",
            width=320,
            height=45,
            font=ctk.CTkFont(size=14),
            border_width=2
        )
        self.password_entry.pack(pady=12)
        
        # Botón de inicio de sesión
        login_button = ctk.CTkButton(
            main_frame,
            text="Iniciar Sesión",
            command=self.login,
            width=320,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8
        )
        login_button.pack(pady=25)
        
        # Info de usuario por defecto
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(side="bottom", pady=20)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="Credenciales por defecto:\nUsuario: admin | Contraseña: admin123",
            font=ctk.CTkFont(size=11),
            text_color=("#888888", "#777777"),
            justify="center"
        )
        info_label.pack()
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
    
    def login(self):
        """Procesa el inicio de sesión"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        # Verificar credenciales
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, password_hash, nombre_completo, rol, activo
            FROM usuarios WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            return
        
        user_id, password_hash, nombre, rol, activo = result
        
        if not activo:
            messagebox.showerror("Error", "Usuario inactivo")
            return
        
        # Verificar contraseña
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            self.user_data = {
                'id': user_id,
                'username': username,
                'nombre': nombre,
                'rol': rol
            }
            self.destroy()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")


class MainApplication(ctk.CTk):
    """Ventana principal de la aplicación"""
    
    def __init__(self, db_manager, user_data):
        super().__init__()
        
        self.db_manager = db_manager
        self.user_data = user_data
        self.sync_manager = SupabaseSync(db_manager)
        
        # Configuración de la ventana
        self.title("Sistema de Gestión Inmobiliaria - Argentina")
        self.geometry("1400x800")
        
        # Crear interfaz
        self.create_widgets()
        
        # Verificar conexión a Supabase
        self.check_sync()
        
        # Auto-sincronización cada 5 minutos
        self.auto_sync()
    
    def create_widgets(self):
        """Crea la interfaz principal"""
        # Frame superior (barra de herramientas) - MÁS CONTRASTE
        toolbar = ctk.CTkFrame(self, height=65, corner_radius=0, fg_color=("#2b5797", "#1a3d5c"))
        toolbar.pack(fill="x", side="top")
        
        # Título con mejor color
        title = ctk.CTkLabel(
            toolbar,
            text=f"{ConfigEmpresa.NOMBRE} - {self.user_data['nombre']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=25, pady=18)
        
        # Estado de sincronización
        self.sync_label = ctk.CTkLabel(
            toolbar,
            text="⚫ Verificando...",
            font=ctk.CTkFont(size=13),
            text_color="white"
        )
        self.sync_label.pack(side="right", padx=25)
        
        # Botón sincronizar
        sync_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Sincronizar",
            width=130,
            height=35,
            command=self.sync_data,
            fg_color=("#4CAF50", "#2d7a2f"),
            hover_color=("#45a049", "#266626"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        sync_btn.pack(side="right", padx=10)
        
        # Frame lateral (menú) - MUCHO MÁS CONTRASTE
        sidebar = ctk.CTkFrame(
            self, 
            width=220, 
            corner_radius=0,
            fg_color=("#2d3e50", "#1a252f")  # Color más oscuro
        )
        sidebar.pack(fill="y", side="left")

        # Logo CONECTAR en sidebar
        if ConfigEmpresa.logo_existe():
            try:
                # Cargar logo
                logo_img = Image.open(ConfigEmpresa.LOGO_PATH)
                
                # Redimensionar para sidebar (ancho máximo 180px)
                ancho_original, alto_original = logo_img.size
                nuevo_ancho = 180
                nuevo_alto = int((nuevo_ancho / ancho_original) * alto_original)
                logo_img = logo_img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
                
                # Convertir para CTk
                logo_photo = ctk.CTkImage(
                    light_image=logo_img,
                    dark_image=logo_img,
                    size=(nuevo_ancho, nuevo_alto)
                )
                
                # Mostrar logo
                logo_label = ctk.CTkLabel(
                    sidebar,
                    image=logo_photo,
                    text=""
                )
                logo_label.image = logo_photo
                logo_label.pack(pady=(15, 10))
            except Exception as e:
                print(f"Error cargando logo en sidebar: {e}")
                # Fallback a texto
                logo_label = ctk.CTkLabel(
                    sidebar,
                    text=f"🏠 {ConfigEmpresa.NOMBRE}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="white"
                )
                logo_label.pack(pady=(25, 15))
        else:
            # Si no hay logo, mostrar texto
            logo_label = ctk.CTkLabel(
                sidebar,
                text=f"🏠 {ConfigEmpresa.NOMBRE}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            )
            logo_label.pack(pady=(25, 15))
        
        # Datos de la empresa debajo del logo
        info_label = ctk.CTkLabel(
            sidebar,
            text=ConfigEmpresa.NOMBRE_COMPLETO,
            font=ctk.CTkFont(size=9),
            text_color="white"
        )
        info_label.pack(pady=(0, 25))

        # Botones de menú con MUCHO MÁS CONTRASTE
        menu_buttons = [
            ("📊 Dashboard", self.show_dashboard, "#3498db"),
            ("🏠 Inmuebles", self.show_inmuebles, "#9b59b6"),
            ("👤 Propietarios", self.show_propietarios, "#e74c3c"),
            ("👥 Inquilinos", self.show_inquilinos, "#f39c12"),
            ("📝 Contratos", self.show_contratos, "#1abc9c"),
            ("💰 Pagos", self.show_pagos, "#2ecc71"),
            ("📈 Ajustes", self.show_ajustes, "#e67e22"),
            ("⚙️ Configuración", self.show_config, "#95a5a6"),
            ("🚪 Cerrar Sesión", self.logout, "#c0392b"),
        ]
        
        for text, command, color in menu_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                width=190,
                height=42,
                anchor="w",
                fg_color="transparent",
                hover_color=color,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white",  # Texto siempre blanco
                corner_radius=8
            )
            btn.pack(padx=15, pady=6)
        
        # Frame de contenido
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#f5f5f5", "#1a1a1a"))
        self.content_frame.pack(fill="both", expand=True, side="right")
        
        # Mostrar dashboard por defecto
        self.show_dashboard()
    
    def clear_content(self):
        """Limpia el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Muestra el dashboard"""
        self.clear_content()
        
        # Contenedor con scroll
        container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            container,
            text="📊 Panel de Control - Resumen General",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        # Obtener estadísticas
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM inmuebles")
        total_inmuebles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inmuebles WHERE estado = 'disponible'")
        inmuebles_disponibles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inmuebles WHERE estado = 'alquilado'")
        inmuebles_alquilados = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contratos WHERE estado = 'activo'")
        contratos_activos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM propietarios")
        total_propietarios = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inquilinos")
        total_inquilinos = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(monto_mensual) FROM contratos WHERE estado = 'activo'")
        ingresos_mensuales = cursor.fetchone()[0] or 0
        
        # Frame de estadísticas principales
        stats_frame = ctk.CTkFrame(container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 30))
        
        # Tarjetas de estadísticas - 4 columnas
        stats = [
            ("🏠 Total Inmuebles", total_inmuebles, "#3498db"),
            ("✅ Disponibles", inmuebles_disponibles, "#2ecc71"),
            ("🔑 Alquilados", inmuebles_alquilados, "#e67e22"),
            ("📝 Contratos Activos", contratos_activos, "#9b59b6"),
            ("👤 Propietarios", total_propietarios, "#e74c3c"),
            ("👥 Inquilinos", total_inquilinos, "#f39c12"),
            ("💰 Ingresos/Mes", f"${ingresos_mensuales:,.0f}", "#1abc9c"),
            ("📊 Ocupación", f"{(inmuebles_alquilados/total_inmuebles*100) if total_inmuebles > 0 else 0:.0f}%", "#34495e"),
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=color, corner_radius=12)
            card.grid(row=i//4, column=i%4, padx=12, pady=12, sticky="nsew")
            
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="white"
            ).pack(pady=(25, 8))
            
            ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(size=40, weight="bold"),
                text_color="white"
            ).pack(pady=(8, 25))
        
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1, uniform="column")
        stats_frame.grid_rowconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(1, weight=1)
        
        # Contratos próximos a vencer
        info_label = ctk.CTkLabel(
            container,
            text="📅 Información Adicional",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        info_label.pack(pady=(20, 15))
        
        info_frame = ctk.CTkFrame(container, corner_radius=10)
        info_frame.pack(fill="x", pady=10)
        
        cursor.execute('''
            SELECT c.fecha_fin, i.direccion, inq.nombre || ' ' || inq.apellido as inquilino
            FROM contratos c
            JOIN inmuebles i ON c.inmueble_id = i.id
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            WHERE c.estado = 'activo' 
            AND date(c.fecha_fin) <= date('now', '+60 days')
            ORDER BY c.fecha_fin
            LIMIT 5
        ''')
        
        proximos = cursor.fetchall()
        
        if proximos:
            ctk.CTkLabel(
                info_frame,
                text="⚠️ Contratos próximos a vencer (60 días)",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(pady=15)
            
            for contrato in proximos:
                fecha, direccion, inquilino = contrato
                texto = f"• {fecha} - {direccion} - {inquilino}"
                ctk.CTkLabel(
                    info_frame,
                    text=texto,
                    font=ctk.CTkFont(size=13)
                ).pack(pady=5, padx=20, anchor="w")
        else:
            ctk.CTkLabel(
                info_frame,
                text="✅ No hay contratos próximos a vencer",
                font=ctk.CTkFont(size=14),
                text_color="green"
            ).pack(pady=20)
    
    def show_inmuebles(self):
        """Muestra la gestión de inmuebles"""
        self.clear_content()
        
        # Usar el módulo de inmuebles
        inmuebles_module = InmueblesModule(self.content_frame, self.db_manager)
        inmuebles_module.pack(fill="both", expand=True)
        
    def show_propietarios(self):
        """Muestra la gestión de propietarios"""
        self.clear_content()
        
        # Usar el módulo de propietarios
        propietarios_module = PropietariosModule(self.content_frame, self.db_manager)
        propietarios_module.pack(fill="both", expand=True)
    
    def show_inquilinos(self):
        """Muestra la gestión de inquilinos"""
        self.clear_content()
        
        # Usar el módulo de inquilinos
        inquilinos_module = InquilinosModule(self.content_frame, self.db_manager)
        inquilinos_module.pack(fill="both", expand=True)
    
    def show_contratos(self):
        """Muestra la gestión de contratos"""
        self.clear_content()
        
        # Usar el módulo de contratos
        contratos_module = ContratosModule(self.content_frame, self.db_manager)
        contratos_module.pack(fill="both", expand=True)
    
    def show_pagos(self):
        """Muestra la gestión de pagos"""
        self.clear_content()
        
        # Usar el módulo de pagos
        pagos_module = PagosModule(self.content_frame, self.db_manager)
        pagos_module.pack(fill="both", expand=True)
    
    def show_ajustes(self):
        """Muestra historial de ajustes de contratos"""
        self.clear_content()
        
        container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="📈 Historial de Ajustes",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        info = ctk.CTkLabel(
            container,
            text="Registro de ajustes por IPC, ICL u otros índices",
            font=ctk.CTkFont(size=14)
        )
        info.pack(pady=20)
    
    def show_config(self):
        """Muestra la configuración"""
        self.clear_content()
        
        container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="⚙️ Configuración del Sistema",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        # Sección Supabase
        supabase_frame = ctk.CTkFrame(container, corner_radius=15)
        supabase_frame.pack(fill="x", pady=15, padx=20)
        
        ctk.CTkLabel(
            supabase_frame,
            text="☁️ Configuración de Supabase",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            supabase_frame,
            text=f"URL: {SUPABASE_URL}",
            font=ctk.CTkFont(size=13)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            supabase_frame,
            text="Estado de conexión:",
            font=ctk.CTkFont(size=13)
        ).pack(pady=5)
        
        status = "🟢 Conectado" if self.sync_manager.connected else "🔴 Desconectado"
        color = "green" if self.sync_manager.connected else "red"
        
        ctk.CTkLabel(
            supabase_frame,
            text=status,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color
        ).pack(pady=10)
        
        btn_test = ctk.CTkButton(
            supabase_frame,
            text="🔄 Probar Conexión",
            command=self.test_supabase_connection,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_test.pack(pady=20)
        
        # Sección de datos de la empresa
        empresa_frame = ctk.CTkFrame(container, corner_radius=15)
        empresa_frame.pack(fill="x", pady=15, padx=20)
        
        ctk.CTkLabel(
            empresa_frame,
            text="🏢 Datos de la Inmobiliaria",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        info = ctk.CTkLabel(
            empresa_frame,
            text="Configuración pendiente de desarrollo",
            font=ctk.CTkFont(size=14)
        )
        info.pack(pady=30)
    
    def test_supabase_connection(self):
        """Prueba la conexión con Supabase"""
        if self.sync_manager.test_connection():
            messagebox.showinfo("Éxito", "✅ Conexión exitosa con Supabase")
            self.check_sync()
        else:
            messagebox.showerror("Error", "❌ No se pudo conectar con Supabase")
    
    def check_sync(self):
        """Verifica la conexión con Supabase"""
        if self.sync_manager.connected:
            self.sync_label.configure(
                text="🟢 Conectado a Supabase",
                text_color="white"
            )
        else:
            self.sync_label.configure(
                text="⚫ Trabajando sin conexión",
                text_color="white"
            )
    
    def sync_data(self):
        """Sincroniza datos con Supabase"""
        self.sync_label.configure(text="🔄 Sincronizando...")
        self.update()
        
        if self.sync_manager.sync_now():
            messagebox.showinfo("Éxito", "✅ Datos sincronizados correctamente")
            self.check_sync()
        else:
            messagebox.showwarning(
                "Aviso", 
                "No se pudo sincronizar.\n" +
                "Los cambios se guardarán y sincronizarán cuando haya conexión."
            )
    
    def auto_sync(self):
        """Sincronización automática cada 5 minutos"""
        def sync_thread():
            while True:
                import time
                time.sleep(300)  # 5 minutos
                if self.sync_manager.connected:
                    self.sync_manager.sync_now()
        
        thread = threading.Thread(target=sync_thread, daemon=True)
        thread.start()
    
    def logout(self):
        """Cierra sesión"""
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar sesión?"):
            self.destroy()
            run_application()


def run_application():
    """Ejecuta la aplicación"""
    # Inicializar base de datos
    db_manager = DatabaseManager()
    
    # Mostrar ventana de login
    login_window = LoginWindow(db_manager)
    login_window.mainloop()
    
    # Si el login fue exitoso, abrir aplicación principal
    if hasattr(login_window, 'user_data') and login_window.user_data:
        app = MainApplication(db_manager, login_window.user_data)
        app.mainloop()


if __name__ == "__main__":
    print("=" * 60)
    print("🏢 SISTEMA DE GESTIÓN INMOBILIARIA")
    print("   Versión Argentina - Misiones")
    print("=" * 60)
    print("\n✅ Iniciando aplicación...")
    print(f"📁 Base de datos: inmobiliaria.db")
    print(f"☁️  Supabase: Configurado")
    print("\n" + "=" * 60 + "\n")
    
    run_application()
