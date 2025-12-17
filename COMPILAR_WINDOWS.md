# 🚀 Guía Rápida: Compilar CONECTAR para Windows

## Opción 1: Compilar en Windows (RECOMENDADO)

### Pre-requisitos en Windows:
- Windows 10/11
- Python 3.9 o superior instalado
- Git (opcional, para clonar el proyecto)

### Pasos:

**1. Copiar el proyecto a Windows**

Opciones:
- USB/Pendrive
- Compartir carpeta de red
- Git: `git clone <url-repositorio>`
- Comprimir y enviar por email

**2. Abrir PowerShell o CMD en la carpeta del proyecto**
```cmd
cd C:\Users\TuUsuario\Desktop\sistema-inmobiliario
```

**3. Crear entorno virtual**
```cmd
python -m venv venv
```

**4. Activar entorno virtual**
```cmd
venv\Scripts\activate
```

**5. Instalar dependencias**
```cmd
pip install -r requirements.txt
pip install pyinstaller
```

**6. Compilar el ejecutable**
```cmd
pyinstaller build.spec --clean
```

⏳ Esto tomará varios minutos...

**7. Verificar que se creó el ejecutable**
```cmd
dir dist\CONECTAR.exe
```

**8. Probar el ejecutable**
```cmd
cd dist
CONECTAR.exe
```

---

### Crear el Instalador (Opcional pero recomendado)

**9. Descargar e instalar Inno Setup**

- Ir a: https://jrsoftware.org/isdl.php
- Descargar: `innosetup-6.x.x.exe`
- Instalar con opciones por defecto

**10. Abrir Inno Setup Compiler**

- Buscar en menú inicio: "Inno Setup Compiler"

**11. Abrir el script de instalación**

- File → Open
- Seleccionar: `C:\ruta\al\proyecto\installer.iss`

**12. Compilar el instalador**

- Build → Compile
- O presionar F9

**13. Ubicar el instalador**

El instalador estará en:
```
C:\ruta\al\proyecto\installer_output\CONECTAR_Setup_v1.0.0.exe
```

---

## Opción 2: Compilar en Linux (Para testing)

**NOTA**: Esto crea un ejecutable para Linux, NO para Windows.
```bash
cd ~/proyectos/sistema-inmobiliario
source venv/bin/activate
./preparar_distribucion.sh
./build_windows.sh
```

El ejecutable estará en `dist/CONECTAR`

---

## 📦 Resultado Final

### Solo Ejecutable:
- `dist/CONECTAR.exe` (50-80 MB)
- Requiere copiar la carpeta `imagenes/` junto al .exe

### Con Instalador:
- `installer_output/CONECTAR_Setup_v1.0.0.exe` (60-90 MB)
- Instalador completo, incluye todo
- Crea accesos directos automáticamente

---

## 🎯 Distribución

### Para usuarios finales:

**Opción A - Solo ejecutable:**
1. Crear carpeta `CONECTAR`
2. Copiar `CONECTAR.exe` dentro
3. Copiar carpeta `imagenes/` dentro
4. Comprimir todo en `CONECTAR.zip`
5. Distribuir el .zip

**Opción B - Con instalador (RECOMENDADO):**
1. Distribuir directamente `CONECTAR_Setup_v1.0.0.exe`
2. Usuario hace doble click
3. Sigue el asistente
4. Listo para usar

---

## ⚠️ Problemas Comunes

### "Python no se reconoce como comando"
- Asegúrate de que Python esté en el PATH
- Durante la instalación de Python, marca: "Add Python to PATH"
- O reinstala Python

### "No se puede crear el ejecutable"
- Verifica que instalaste todas las dependencias: `pip list`
- Cierra el ejecutable si está abierto
- Elimina carpetas: `build/` y `dist/`
- Intenta de nuevo

### "Windows Defender bloquea el ejecutable"
- Normal para ejecutables sin firma digital
- Click en "Más información" → "Ejecutar de todas formas"
- Para distribución profesional, considera firmar el ejecutable

### "No aparece el logo"
- Verifica que `imagenes/logo.png` exista
- Verifica que la carpeta `imagenes/` esté junto al .exe
- Con el instalador, esto se maneja automáticamente

### "Error al abrir el PDF"
- Instala un lector de PDF (Adobe Reader, SumatraPDF, etc.)
- Configura el lector por defecto en Windows

---

## 📊 Tamaños Aproximados

- Código fuente completo: ~5 MB
- Ejecutable compilado: ~50-80 MB
- Instalador completo: ~60-90 MB
- Base de datos vacía: ~100 KB
- Base de datos con datos: Variable

---

## 🔐 Seguridad

El ejecutable incluye:
- ✅ Base de datos SQLite local
- ✅ Sincronización con Supabase
- ✅ Trabajo offline
- ✅ Todas las dependencias empaquetadas
- ❌ NO incluye las credenciales de Supabase visibles
- ❌ NO incluye código fuente visible

---

## 📝 Notas Adicionales

### Primera ejecución:
1. Se crea `inmobiliaria.db` automáticamente
2. Se crea carpeta `recibos/` al generar el primer recibo
3. Usuario por defecto: `admin` / `admin123`

### Actualizar el sistema:
1. Compilar nueva versión
2. Cambiar versión en `installer.iss`
3. Distribuir nuevo instalador
4. Usuarios pueden instalar sobre la versión anterior
5. La base de datos se conserva

### Desinstalación:
- A través de "Agregar o quitar programas" en Windows
- La base de datos se conserva por seguridad
- Los recibos generados se conservan

---

## 🆘 Soporte

Si tienes problemas:
1. Verifica que seguiste todos los pasos
2. Lee la sección de "Problemas Comunes"
3. Revisa los logs en la carpeta `build/`
4. Contacta al desarrollador

---

## ✅ Checklist

Antes de distribuir:

- [ ] Ejecutable compilado correctamente
- [ ] Logo e imágenes incluidas
- [ ] Probado en máquina limpia de Windows
- [ ] Login funciona
- [ ] Todos los módulos abren correctamente
- [ ] Puede crear registros (propietarios, inquilinos, etc.)
- [ ] Genera PDFs correctamente
- [ ] Sincronización con Supabase funciona
- [ ] Instalador crea accesos directos
- [ ] Desinstalador funciona correctamente

---

¡Listo para distribuir! 🎉