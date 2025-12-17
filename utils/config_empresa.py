# utils/config_empresa.py - Configuración de la Inmobiliaria
import os

class ConfigEmpresa:
    """Configuración centralizada de la inmobiliaria"""
    
    # Datos de la empresa
    NOMBRE = "CONECTAR"
    NOMBRE_COMPLETO = "Inmobiliaria CONECTAR"
    
    # Dirección
    DIRECCION_1 = "Av. López y Planes y Av. Padre Kolping"
    DIRECCION_2 = "Posadas, Misiones - Argentina"
    
    # Contacto (puedes agregar después)
    TELEFONO = ""  # Ej: "(0376) 4-123456"
    EMAIL = ""     # Ej: "contacto@conectar.com.ar"
    CUIT = ""      # Ej: "20-12345678-9"
    
    # Rutas de imágenes
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CARPETA_IMAGENES = os.path.join(BASE_DIR, "imagenes")
    
    LOGO_PATH = os.path.join(CARPETA_IMAGENES, "logo.png")
    FAVICON_PATH = os.path.join(CARPETA_IMAGENES, "favicon.png")
    
    @classmethod
    def logo_existe(cls):
        """Verifica si existe el logo"""
        return os.path.exists(cls.LOGO_PATH)
    
    @classmethod
    def favicon_existe(cls):
        """Verifica si existe el favicon"""
        return os.path.exists(cls.FAVICON_PATH)
    
    @classmethod
    def get_direccion_completa(cls):
        """Retorna la dirección completa en una línea"""
        return f"{cls.DIRECCION_1}, {cls.DIRECCION_2}"