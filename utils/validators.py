# utils/validators.py - Validaciones para el sistema
import re
from typing import Tuple


class Validators:
    """Clase con métodos de validación para datos argentinos"""
    
    @staticmethod
    def validar_cuit(cuit: str) -> Tuple[bool, str]:
        """
        Valida un CUIT argentino
        Formato: XX-XXXXXXXX-X
        """
        # Limpiar guiones y espacios
        cuit_limpio = cuit.replace('-', '').replace(' ', '').strip()
        
        # Verificar longitud
        if len(cuit_limpio) != 11:
            return False, "El CUIT debe tener 11 dígitos"
        
        # Verificar que sean solo números
        if not cuit_limpio.isdigit():
            return False, "El CUIT solo debe contener números"
        
        # Validación del dígito verificador
        try:
            # Multiplicadores
            multiplicadores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            
            # Calcular suma
            suma = sum(int(cuit_limpio[i]) * multiplicadores[i] for i in range(10))
            
            # Calcular dígito verificador
            resto = suma % 11
            verificador = 11 - resto
            
            if verificador == 11:
                verificador = 0
            elif verificador == 10:
                verificador = 9
            
            # Comparar con el dígito verificador del CUIT
            if int(cuit_limpio[10]) != verificador:
                return False, "CUIT inválido (dígito verificador incorrecto)"
            
            return True, "CUIT válido"
            
        except Exception as e:
            return False, f"Error validando CUIT: {str(e)}"
    
    @staticmethod
    def validar_dni(dni: str) -> Tuple[bool, str]:
        """
        Valida un DNI argentino
        Formato: 7 u 8 dígitos
        """
        # Limpiar puntos y espacios
        dni_limpio = dni.replace('.', '').replace(' ', '').strip()
        
        # Verificar que sean solo números
        if not dni_limpio.isdigit():
            return False, "El DNI solo debe contener números"
        
        # Verificar longitud
        if len(dni_limpio) < 7 or len(dni_limpio) > 8:
            return False, "El DNI debe tener 7 u 8 dígitos"
        
        return True, "DNI válido"
    
    @staticmethod
    def validar_cuit_o_dni(valor: str) -> Tuple[bool, str]:
        """
        Valida CUIT o DNI automáticamente
        """
        valor_limpio = valor.replace('-', '').replace('.', '').replace(' ', '').strip()
        
        if len(valor_limpio) == 11:
            return Validators.validar_cuit(valor)
        elif len(valor_limpio) in [7, 8]:
            return Validators.validar_dni(valor)
        else:
            return False, "Debe ingresar un CUIT (11 dígitos) o DNI (7-8 dígitos)"
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """Valida formato de email"""
        if not email:
            return True, "Email vacío (opcional)"
        
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(patron, email.strip()):
            return True, "Email válido"
        else:
            return False, "Formato de email inválido"
    
    @staticmethod
    def validar_telefono(telefono: str) -> Tuple[bool, str]:
        """
        Valida teléfono argentino
        Acepta: +54, 0, 15, etc.
        """
        if not telefono:
            return False, "El teléfono es obligatorio"
        
        # Limpiar caracteres
        tel_limpio = telefono.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        # Verificar que sean números
        if not tel_limpio.isdigit():
            return False, "El teléfono solo debe contener números"
        
        # Longitud mínima
        if len(tel_limpio) < 8:
            return False, "El teléfono debe tener al menos 8 dígitos"
        
        return True, "Teléfono válido"
    
    @staticmethod
    def validar_monto(monto: str) -> Tuple[bool, str, float]:
        """
        Valida y convierte un monto
        Retorna: (válido, mensaje, monto_float)
        """
        if not monto:
            return False, "El monto es obligatorio", 0.0
        
        try:
            # Limpiar formato
            monto_limpio = monto.replace('$', '').replace('.', '').replace(',', '.').strip()
            monto_float = float(monto_limpio)
            
            if monto_float < 0:
                return False, "El monto no puede ser negativo", 0.0
            
            return True, "Monto válido", monto_float
            
        except ValueError:
            return False, "Formato de monto inválido", 0.0
    
    @staticmethod
    def validar_texto_requerido(texto: str, nombre_campo: str, min_length: int = 2) -> Tuple[bool, str]:
        """Valida que un campo de texto no esté vacío"""
        if not texto or not texto.strip():
            return False, f"El campo {nombre_campo} es obligatorio"
        
        if len(texto.strip()) < min_length:
            return False, f"El campo {nombre_campo} debe tener al menos {min_length} caracteres"
        
        return True, "Válido"
    
    @staticmethod
    def validar_numero_positivo(valor: str, nombre_campo: str) -> Tuple[bool, str, int]:
        """Valida un número entero positivo"""
        try:
            numero = int(valor)
            
            if numero < 0:
                return False, f"{nombre_campo} no puede ser negativo", 0
            
            return True, "Válido", numero
            
        except ValueError:
            return False, f"{nombre_campo} debe ser un número", 0
    
    @staticmethod
    def formatear_cuit(cuit: str) -> str:
        """Formatea un CUIT al estándar XX-XXXXXXXX-X"""
        cuit_limpio = cuit.replace('-', '').replace(' ', '').strip()
        
        if len(cuit_limpio) == 11:
            return f"{cuit_limpio[:2]}-{cuit_limpio[2:10]}-{cuit_limpio[10]}"
        
        return cuit
    
    @staticmethod
    def formatear_dni(dni: str) -> str:
        """Formatea un DNI con puntos"""
        dni_limpio = dni.replace('.', '').replace(' ', '').strip()
        
        if len(dni_limpio) >= 7:
            # Formato: XX.XXX.XXX
            dni_reversed = dni_limpio[::-1]
            grupos = [dni_reversed[i:i+3] for i in range(0, len(dni_reversed), 3)]
            return '.'.join(grupos)[::-1]
        
        return dni
    
    @staticmethod
    def formatear_telefono(telefono: str) -> str:
        """Formatea un teléfono argentino"""
        tel_limpio = telefono.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        if len(tel_limpio) == 10:
            # Formato: (0XXX) XXX-XXXX
            return f"({tel_limpio[:4]}) {tel_limpio[4:7]}-{tel_limpio[7:]}"
        elif len(tel_limpio) == 8:
            # Formato: XXXX-XXXX
            return f"{tel_limpio[:4]}-{tel_limpio[4:]}"
        
        return telefono
    
    @staticmethod
    def formatear_monto(monto: float) -> str:
        """Formatea un monto con separadores de miles"""
        return f"${monto:,.2f}".replace(',', '.')


# Función de ayuda para validar todos los campos de un formulario
def validar_formulario(campos: dict) -> Tuple[bool, list]:
    """
    Valida múltiples campos a la vez
    
    Parámetros:
        campos: dict con formato {'nombre_campo': ('valor', 'tipo_validacion', param_opcional)}
    
    Retorna:
        (True/False, [lista de errores])
    
    Ejemplo:
        campos = {
            'nombre': ('Juan', 'texto_requerido', 'Nombre'),
            'cuit': ('20-12345678-9', 'cuit'),
            'email': ('juan@example.com', 'email')
        }
    """
    errores = []
    validators = Validators()
    
    for campo, datos in campos.items():
        valor = datos[0]
        tipo = datos[1]
        
        if tipo == 'texto_requerido':
            nombre = datos[2] if len(datos) > 2 else campo
            valido, mensaje = validators.validar_texto_requerido(valor, nombre)
            if not valido:
                errores.append(mensaje)
        
        elif tipo == 'cuit':
            valido, mensaje = validators.validar_cuit(valor)
            if not valido:
                errores.append(mensaje)
        
        elif tipo == 'dni':
            valido, mensaje = validators.validar_dni(valor)
            if not valido:
                errores.append(mensaje)
        
        elif tipo == 'cuit_o_dni':
            valido, mensaje = validators.validar_cuit_o_dni(valor)
            if not valido:
                errores.append(mensaje)
        
        elif tipo == 'email':
            if valor:  # Solo validar si hay valor (email es opcional)
                valido, mensaje = validators.validar_email(valor)
                if not valido:
                    errores.append(mensaje)
        
        elif tipo == 'telefono':
            valido, mensaje = validators.validar_telefono(valor)
            if not valido:
                errores.append(mensaje)
        
        elif tipo == 'monto':
            valido, mensaje, _ = validators.validar_monto(valor)
            if not valido:
                errores.append(mensaje)
    
    return len(errores) == 0, errores
