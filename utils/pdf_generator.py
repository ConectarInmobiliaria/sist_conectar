# utils/pdf_generator.py - Generador de PDFs para Recibos
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from utils.config_empresa import ConfigEmpresa

class ReciboPDF:
    """Generador de recibos en PDF - 2 recibos por hoja A4"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.width, self.height = A4
        
        # Crear carpeta principal de recibos si no existe
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recibos")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def get_datos_pago(self, pago_id):
        """Obtiene todos los datos necesarios para el recibo"""
        query = '''
            SELECT 
                p.*,
                c.monto_mensual as monto_contrato,
                c.fecha_inicio as contrato_inicio,
                c.fecha_fin as contrato_fin,
                i.direccion as inmueble_direccion,
                i.tipo as inmueble_tipo,
                i.ciudad as inmueble_ciudad,
                i.provincia as inmueble_provincia,
                i.partida_inmobiliaria,
                i.conexion_emsa,
                i.conexion_samsa,
                inq.nombre || ' ' || inq.apellido as inquilino_nombre,
                inq.cuit_dni as inquilino_cuit,
                inq.direccion as inquilino_direccion,
                inq.telefono as inquilino_telefono,
                prop.nombre || ' ' || prop.apellido as propietario_nombre,
                prop.cuit_dni as propietario_cuit,
                prop.telefono as propietario_telefono,
                prop.direccion as propietario_direccion
            FROM pagos p
            JOIN contratos c ON p.contrato_id = c.id
            JOIN inmuebles i ON c.inmueble_id = i.id
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            LEFT JOIN propietarios prop ON i.propietario_id = prop.id
            WHERE p.id = ?
        '''
        
        resultado = self.db_manager.execute_query(query, (pago_id,))
        return resultado[0] if resultado else None
    
    def get_carpeta_propietario(self, propietario_nombre, inmueble_direccion):
        """Crea y retorna la carpeta organizada por propietario e inmueble"""
        # Limpiar nombres para usar en carpetas
        prop_limpio = "".join(c for c in propietario_nombre if c.isalnum() or c in (' ', '_')).strip()
        inm_limpio = "".join(c for c in inmueble_direccion if c.isalnum() or c in (' ', '_')).strip()
        
        # Crear estructura: recibos/Propietario/Inmueble/
        carpeta_prop = os.path.join(self.base_dir, prop_limpio)
        carpeta_inmueble = os.path.join(carpeta_prop, inm_limpio)
        
        if not os.path.exists(carpeta_inmueble):
            os.makedirs(carpeta_inmueble)
        
        return carpeta_inmueble
    
    def generar_recibo(self, pago_id, abrir_pdf=True):
        """Genera un PDF con 2 recibos por hoja A4"""
        # Obtener datos
        datos = self.get_datos_pago(pago_id)
        
        if not datos:
            return None, "No se encontraron datos del pago"
        
        # Crear nombre de archivo
        meses = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", 
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        mes_nombre = meses[datos['periodo_mes']]
        
        nombre_archivo = f"Recibo_{datos['inquilino_nombre'].replace(' ', '_')}_{mes_nombre}_{datos['periodo_anio']}.pdf"
        
        # Obtener carpeta del propietario
        carpeta = self.get_carpeta_propietario(
            datos['propietario_nombre'], 
            datos['inmueble_direccion']
        )
        
        ruta_completa = os.path.join(carpeta, nombre_archivo)
        
        # Crear PDF
        c = canvas.Canvas(ruta_completa, pagesize=A4)
        
        # Dibujar primer recibo (parte superior)
        self.dibujar_recibo(c, datos, y_inicio=self.height - 1*cm, es_original=True)
        
        # Línea de corte
        c.setDash(3, 3)
        c.line(1*cm, self.height/2, self.width - 1*cm, self.height/2)
        c.setDash()
        
        # Dibujar segundo recibo (parte inferior - copia)
        self.dibujar_recibo(c, datos, y_inicio=self.height/2 - 1*cm, es_original=False)
        
        # Guardar PDF
        c.save()
        
        # Abrir PDF si se solicita
        if abrir_pdf:
            self.abrir_pdf(ruta_completa)
        
        return ruta_completa, "Recibo generado exitosamente"
    
    def dibujar_recibo(self, c, datos, y_inicio, es_original=True):
        """Dibuja un recibo individual en el canvas"""
        y = y_inicio
        x_left = 2*cm
        x_right = self.width - 2*cm

        # Tipo de recibo
        tipo = "ORIGINAL" if es_original else "COPIA"
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(x_right, y, tipo)
        y -= 0.5*cm

        # Logo de CONECTAR
        if ConfigEmpresa.logo_existe():
            try:
                from PIL import Image as PILImage

                # Cargar logo
                logo_img = PILImage.open(ConfigEmpresa.LOGO_PATH)
                ancho_original, alto_original = logo_img.size

                # Calcular dimensiones manteniendo proporción
                # Logo rectangular: ancho máximo 4cm
                ancho_logo = 4*cm
                alto_logo = (ancho_logo / ancho_original) * alto_original

                # Si es muy alto, limitar altura
                if alto_logo > 2*cm:
                    alto_logo = 2*cm
                    ancho_logo = (alto_logo / alto_original) * ancho_original

                c.drawImage(
                    ConfigEmpresa.LOGO_PATH,
                    x_left,
                    y - alto_logo - 0.2*cm,
                    width=ancho_logo,
                    height=alto_logo,
                    preserveAspectRatio=True,
                    mask='auto'
                )

                logo_width = ancho_logo + 0.5*cm
            except Exception as e:
                print(f"Error cargando logo en PDF: {e}")
                logo_width = 0
        else:
            logo_width = 0

        # Encabezado con datos de CONECTAR
        x_texto = x_left + logo_width

        c.setFont("Helvetica-Bold", 16)
        c.drawString(x_texto, y - 0.5*cm, "RECIBO DE ALQUILER")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_texto, y - 1*cm, ConfigEmpresa.NOMBRE_COMPLETO)

        c.setFont("Helvetica", 9)
        c.drawString(x_texto, y - 1.5*cm, ConfigEmpresa.DIRECCION_1)
        c.drawString(x_texto, y - 1.9*cm, ConfigEmpresa.DIRECCION_2)

        # Si hay teléfono o email, agregarlos
        info_adicional_y = y - 2.3*cm
        if ConfigEmpresa.TELEFONO:
            c.drawString(x_texto, info_adicional_y, f"Tel: {ConfigEmpresa.TELEFONO}")
            info_adicional_y -= 0.4*cm
        if ConfigEmpresa.EMAIL:
            c.drawString(x_texto, info_adicional_y, f"Email: {ConfigEmpresa.EMAIL}")

        y -= 3*cm

        # Número de recibo y fecha (formateada a DD-MM-AAAA si es posible)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_left, y, f"Recibo N°: {datos['id']:06d}")

        # Intentar parsear y formatear la fecha a DD-MM-AAAA
        fecha_pago_raw = datos.get('fecha_pago')
        fecha_str = ''
        if fecha_pago_raw:
            try:
                # Primero probar ISO / RFC compatible (yyyy-mm-dd o with time)
                try:
                    dt = datetime.fromisoformat(fecha_pago_raw)
                except Exception:
                    # Probar formatos comunes
                    try:
                        dt = datetime.strptime(fecha_pago_raw, '%Y-%m-%d')
                    except Exception:
                        try:
                            dt = datetime.strptime(fecha_pago_raw, '%d-%m-%Y')
                        except Exception:
                            dt = None

                if dt:
                    fecha_str = dt.strftime('%d-%m-%Y')
                else:
                    # Si no se pudo parsear, mostrar el valor crudo
                    fecha_str = fecha_pago_raw
            except Exception:
                fecha_str = fecha_pago_raw

        c.drawRightString(x_right, y, f"Fecha: {fecha_str}")

        y -= 0.8*cm

        # Período
        meses_completos = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_nombre = meses_completos[datos['periodo_mes']]

        c.setFont("Helvetica", 10)
        c.drawString(x_left, y, f"Período: {mes_nombre} de {datos['periodo_anio']}")

        y -= 1*cm

        # Línea separadora
        c.setStrokeColor(colors.grey)
        c.line(x_left, y, x_right, y)
        y -= 0.5*cm

        # Nota: Se omiten intencionalmente los datos del propietario en el recibo
        # (espacio reducido para mantener el formato)
        y -= 0.2*cm

        # Datos del Inquilino
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_left, y, "INQUILINO")
        y -= 0.5*cm

        c.setFont("Helvetica", 9)
        c.drawString(x_left, y, f"Nombre: {datos['inquilino_nombre']}")
        y -= 0.4*cm
        c.drawString(x_left, y, f"CUIT/DNI: {datos['inquilino_cuit']}")
        c.drawString(x_left + 6*cm, y, f"Tel: {datos['inquilino_telefono']}")
        y -= 0.4*cm
        c.drawString(x_left, y, f"Dirección: {datos['inquilino_direccion']}")

        y -= 0.8*cm

        # Datos del Inmueble
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_left, y, "INMUEBLE")
        y -= 0.5*cm

        c.setFont("Helvetica", 9)
        c.drawString(x_left, y, f"Dirección: {datos['inmueble_direccion']}")
        y -= 0.4*cm
        c.drawString(x_left, y, f"Ciudad: {datos['inmueble_ciudad']}, {datos['inmueble_provincia']}")
        y -= 0.4*cm


        y -= 0.5*cm

        # Línea separadora
        c.setStrokeColor(colors.grey)
        c.line(x_left, y, x_right, y)
        y -= 0.5*cm

        # Detalle de pagos
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_left, y, "DETALLE DEL PAGO")
        y -= 0.6*cm

        # Tabla de conceptos
        c.setFont("Helvetica", 9)
        conceptos = []

        # Alquiler
        conceptos.append(("Alquiler del mes", f"$ {datos['monto_alquiler']:,.2f}"))

        # Expensas
        if datos.get('monto_expensas') and datos['monto_expensas'] > 0:
            conceptos.append(("Expensas / Gastos Comunes", f"$ {datos['monto_expensas']:,.2f}"))

        # EMSA
        if datos.get('monto_emsa') and datos['monto_emsa'] > 0:
            emsa_texto = f"EMSA (Luz)"
            if datos.get('conexion_emsa'):
                emsa_texto += f" - N° {datos['conexion_emsa']}"
            conceptos.append((emsa_texto, f"$ {datos['monto_emsa']:,.2f}"))

        # SAMSA
        if datos.get('monto_samsa') and datos['monto_samsa'] > 0:
            samsa_texto = f"SAMSA (Agua)"
            if datos.get('conexion_samsa'):
                samsa_texto += f" - N° {datos['conexion_samsa']}"
            conceptos.append((samsa_texto, f"$ {datos['monto_samsa']:,.2f}"))

        # Otros
        if datos.get('monto_otros') and datos['monto_otros'] > 0:
            conceptos.append(("Otros conceptos", f"$ {datos['monto_otros']:,.2f}"))

        # Dibujar conceptos
        for concepto, monto in conceptos:
            c.drawString(x_left + 0.5*cm, y, concepto)
            c.drawRightString(x_right, y, monto)
            y -= 0.4*cm

        y -= 0.3*cm

        # Línea antes del total
        c.setStrokeColor(colors.black)
        c.line(x_left, y, x_right, y)
        y -= 0.5*cm

        # Total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_left, y, "TOTAL PAGADO:")
        c.drawRightString(x_right, y, f"$ {datos['monto_total']:,.2f}")

        y -= 0.8*cm

        # Método de pago
        c.setFont("Helvetica", 9)
        if datos.get('metodo_pago'):
            c.drawString(x_left, y, f"Método de pago: {datos['metodo_pago'].upper()}")

        if datos.get('comprobante'):
            c.drawRightString(x_right, y, f"Comprobante: {datos['comprobante']}")

        y -= 0.8*cm

        # Concepto/Observaciones
        if datos.get('concepto'):
            c.setFont("Helvetica-Oblique", 8)
            # Dividir texto largo en múltiples líneas
            texto = datos['concepto']
            max_chars = 80
            if len(texto) > max_chars:
                lineas = [texto[i:i+max_chars] for i in range(0, len(texto), max_chars)]
                for linea in lineas[:2]:  # Máximo 2 líneas
                    c.drawString(x_left, y, f"Obs: {linea}")
                    y -= 0.3*cm
            else:
                c.drawString(x_left, y, f"Observaciones: {texto}")

    def abrir_pdf(self, ruta):
        """Abre el PDF generado con el visor predeterminado del sistema"""
        import subprocess
        import platform
        
        try:
            sistema = platform.system()
            
            if sistema == 'Linux':
                subprocess.run(['xdg-open', ruta])
            elif sistema == 'Windows':
                os.startfile(ruta)
            elif sistema == 'Darwin':  # macOS
                subprocess.run(['open', ruta])
        except Exception as e:
            print(f"No se pudo abrir el PDF automáticamente: {e}")
    
    def imprimir_pdf(self, ruta):
        """Envía el PDF a la impresora predeterminada"""
        import subprocess
        import platform
        
        try:
            sistema = platform.system()
            
            if sistema == 'Linux':
                # En Linux, usar lp o lpr
                try:
                    subprocess.run(['lp', ruta], check=True)
                    return True, "Documento enviado a la impresora"
                except subprocess.CalledProcessError:
                    try:
                        subprocess.run(['lpr', ruta], check=True)
                        return True, "Documento enviado a la impresora"
                    except:
                        return False, "No se encontró ningún comando de impresión (lp/lpr)"
            
            elif sistema == 'Windows':
                # En Windows, usar el comando print
                import win32api
                import win32print
                
                printer_name = win32print.GetDefaultPrinter()
                win32api.ShellExecute(
                    0,
                    "print",
                    ruta,
                    f'/d:"{printer_name}"',
                    ".",
                    0
                )
                return True, f"Documento enviado a {printer_name}"
            
            elif sistema == 'Darwin':  # macOS
                subprocess.run(['lpr', ruta], check=True)
                return True, "Documento enviado a la impresora"
            
            else:
                return False, "Sistema operativo no soportado"
        
        except Exception as e:
            return False, f"Error al imprimir: {str(e)}"
    
    def generar_e_imprimir(self, pago_id):
        """Genera el recibo y pregunta si desea imprimirlo"""
        # Generar PDF
        ruta, mensaje = self.generar_recibo(pago_id, abrir_pdf=True)
        
        if not ruta:
            return False, mensaje
        
        return ruta, mensaje
    
    def listar_recibos_propietario(self, propietario_nombre):
        """Lista todos los recibos de un propietario"""
        prop_limpio = "".join(c for c in propietario_nombre if c.isalnum() or c in (' ', '_')).strip()
        carpeta_prop = os.path.join(self.base_dir, prop_limpio)
        
        if not os.path.exists(carpeta_prop):
            return []
        
        recibos = []
        for root, dirs, files in os.walk(carpeta_prop):
            for file in files:
                if file.endswith('.pdf'):
                    recibos.append(os.path.join(root, file))
        
        return recibos
    
    def abrir_carpeta_recibos(self, propietario_nombre=None, inmueble_direccion=None):
        """Abre la carpeta de recibos en el explorador de archivos"""
        import subprocess
        import platform
        
        if propietario_nombre and inmueble_direccion:
            carpeta = self.get_carpeta_propietario(propietario_nombre, inmueble_direccion)
        elif propietario_nombre:
            prop_limpio = "".join(c for c in propietario_nombre if c.isalnum() or c in (' ', '_')).strip()
            carpeta = os.path.join(self.base_dir, prop_limpio)
        else:
            carpeta = self.base_dir
        
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        
        try:
            sistema = platform.system()
            
            if sistema == 'Linux':
                subprocess.run(['xdg-open', carpeta])
            elif sistema == 'Windows':
                os.startfile(carpeta)
            elif sistema == 'Darwin':
                subprocess.run(['open', carpeta])
            
            return True, "Carpeta abierta correctamente"
        except Exception as e:
            return False, f"Error al abrir carpeta: {str(e)}"


class DialogoImpresion:
    """Diálogo para preguntar si desea imprimir el recibo"""
    
    @staticmethod
    def preguntar_impresion():
        """Muestra un diálogo preguntando si desea imprimir"""
        from tkinter import messagebox
        
        respuesta = messagebox.askyesnocancel(
            "Imprimir Recibo",
            "El recibo se generó correctamente.\n\n" +
            "¿Desea imprimirlo ahora?\n\n" +
            "Sí: Enviar a impresora\n" +
            "No: Solo ver el PDF\n" +
            "Cancelar: Cerrar"
        )
        
        return respuesta  # True = Imprimir, False = Solo ver, None = Cancelar


# Función auxiliar para generar recibo desde cualquier parte del sistema
def generar_recibo_pago(db_manager, pago_id, imprimir=False):
    """
    Función auxiliar para generar recibos
    
    Parámetros:
        db_manager: Instancia del gestor de base de datos
        pago_id: ID del pago
        imprimir: Si True, intenta imprimir automáticamente
    
    Retorna:
        (ruta_archivo, mensaje_resultado)
    """
    generador = ReciboPDF(db_manager)
    
    # Generar el PDF
    ruta, mensaje = generador.generar_recibo(pago_id, abrir_pdf=True)
    
    if not ruta:
        return None, mensaje
    
    # Si se solicita imprimir
    if imprimir:
        exito, msg_impresion = generador.imprimir_pdf(ruta)
        if exito:
            mensaje += f"\n{msg_impresion}"
        else:
            mensaje += f"\nAdvertencia: {msg_impresion}"
    
    return ruta, mensaje