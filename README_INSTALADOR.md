# 📦 Crear Instalador de CONECTAR para Windows

## Requisitos

### En Linux (para desarrollo):
- Python 3.9+
- PyInstaller
- Todas las dependencias del proyecto instaladas

### En Windows (para crear el instalador):
- **Inno Setup 6** (gratuito)
  - Descargar de: https://jrsoftware.org/isdl.php
  - Instalar en Windows

## Proceso Completo

### Paso 1: Construir el Ejecutable (en Linux)
```bash
cd ~/proyectos/sistema-inmobiliario
source venv/bin/activate
./build_windows.sh
```

Esto creará:
- `dist/CONECTAR` - Ejecutable para Linux
- `dist/CONECTAR.exe` - Ejecutable para Windows (si usas Wine/cross-compile)

**IMPORTANTE**: PyInstaller crea ejecutables para el sistema donde se ejecuta.
- En Linux → Ejecutable para Linux
- En Windows → Ejecutable para Windows

### Paso 2: Crear el Ejecutable en Windows

#### Opción A: Compilar directamente en Windows

1. Copia todo el proyecto a una máquina Windows
2. Instala Python 3.9+ en Windows
3. Abre PowerShell o CMD como Administrador
4. Ejecuta:
```cmd
cd C:\ruta\al\proyecto\sistema-inmobiliario
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pyinstaller build.spec --clean
```

#### Opción B: Usar Wine en Linux (más complejo)
```bash
# Instalar Wine
sudo apt install wine winetricks

# Instalar Python en Wine
# (proceso complejo, no recomendado)
```

### Paso 3: Crear el Instalador con Inno Setup (en Windows)

1. **Abrir Inno Setup Compiler** en Windows
2. **File → Open** → Seleccionar `installer.iss`
3. **Build → Compile**
4. El instalador se creará en `installer_output/`

Resultado:
- `CONECTAR_Setup_v1.0.0.exe` - Instalador completo

### Paso 4: Personalizar el Instalador

Edita `installer.iss` para cambiar:
```ini
; Versión
#define MyAppVersion "1.0.0"

; URL de tu sitio web
#define MyAppURL "https://www.conectar.com.ar"

; Icono del instalador
SetupIconFile=imagenes\favicon.png
```

## Características del Instalador

✅ **Instalación profesional**
- Se instala en `C:\Program Files\CONECTAR\`
- Crea accesos directos en el menú de inicio
- Opción de crear icono en el escritorio
- Opción de crear icono en inicio rápido

✅ **Desinstalación limpia**
- Desinstalador automático
- Opción de conservar o eliminar datos

✅ **Preguntas durante la instalación**
- ¿Crear icono en escritorio? (marcado por defecto)
- ¿Crear icono en inicio rápido? (opcional)
- ¿Ejecutar CONECTAR al terminar? (opcional)

## Estructura del Instalador
```
CONECTAR_Setup_v1.0.0.exe
  │
  ├── CONECTAR.exe (ejecutable principal)
  ├── imagenes/
  │   ├── logo.png
  │   └── favicon.png
  └── [dependencias empaquetadas]
```

## Distribución

### Para usuarios finales:
1. Envíales `CONECTAR_Setup_v1.0.0.exe`
2. Doble click para instalar
3. Seguir el asistente de instalación
4. Listo para usar

### Tamaño aproximado:
- Ejecutable: ~50-80 MB
- Instalador completo: ~60-90 MB

## Actualizar la Versión

1. Edita `installer.iss`:
```ini
#define MyAppVersion "1.1.0"
```

2. Recompila el ejecutable y el instalador

3. Los usuarios pueden instalar sobre la versión anterior

## Problemas Comunes

### Error: "No se puede crear el ejecutable"
- Verifica que todas las dependencias estén instaladas
- Asegúrate de estar en el entorno virtual
- Limpia builds anteriores: `rm -rf build dist`

### El ejecutable no abre
- Verifica que existan las carpetas `imagenes/`
- Revisa el log en `dist/`
- Ejecuta desde terminal para ver errores

### El instalador falla
- Verifica que `dist/CONECTAR.exe` exista
- Comprueba rutas en `installer.iss`
- Ejecuta Inno Setup como Administrador

## Testing

Antes de distribuir:

1. **Prueba el ejecutable**:
   - Copia `dist/CONECTAR.exe` a otra carpeta
   - Copia la carpeta `imagenes/` también
   - Ejecuta y verifica que todo funcione

2. **Prueba el instalador**:
   - Instala en una máquina limpia
   - Verifica los accesos directos
   - Prueba todas las funcionalidades
   - Desinstala y verifica que se limpie correctamente

## Notas de Seguridad

- Windows Defender puede marcar el .exe como "no reconocido"
- Para evitar esto, firma digitalmente el ejecutable (requiere certificado)
- Alternativamente, distribuye el código fuente

## Soporte

Para problemas con el instalador:
- Contactar a soporte técnico
- Email: contacto@conectar.com.ar