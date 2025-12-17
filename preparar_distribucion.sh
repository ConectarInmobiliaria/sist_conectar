#!/bin/bash
# preparar_distribucion.sh - Prepara el proyecto para crear instalador

echo "============================================"
echo "📦 PREPARANDO PROYECTO PARA DISTRIBUCIÓN"
echo "============================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para verificar archivos
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 ${YELLOW}(falta)${NC}"
        return 1
    fi
}

# Verificar estructura del proyecto
echo "1️⃣  Verificando estructura del proyecto..."
echo ""

ERRORES=0

# Archivos principales
check_file "main.py" || ((ERRORES++))
check_file "database.py" || ((ERRORES++))
check_file "supabase_sync.py" || ((ERRORES++))
check_file "requirements.txt" || ((ERRORES++))
check_file "build.spec" || ((ERRORES++))

echo ""

# Módulos
echo "📂 Módulos:"
check_file "modules/propietarios.py" || ((ERRORES++))
check_file "modules/inquilinos.py" || ((ERRORES++))
check_file "modules/inmuebles.py" || ((ERRORES++))
check_file "modules/contratos.py" || ((ERRORES++))
check_file "modules/pagos.py" || ((ERRORES++))

echo ""

# Utilidades
echo "🔧 Utilidades:"
check_file "utils/validators.py" || ((ERRORES++))
check_file "utils/pdf_generator.py" || ((ERRORES++))
check_file "utils/config_empresa.py" || ((ERRORES++))

echo ""

# Componentes
echo "🎨 Componentes:"
check_file "components/date_picker.py" || ((ERRORES++))

echo ""

# Imágenes
echo "🖼️  Imágenes:"
check_file "imagenes/logo.png" || ((ERRORES++))
check_file "imagenes/favicon.png" || ((ERRORES++))

echo ""
echo "============================================"

if [ $ERRORES -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS LOS ARCHIVOS PRESENTES${NC}"
else
    echo -e "${RED}⚠️  FALTAN $ERRORES ARCHIVO(S)${NC}"
    echo ""
    echo "Por favor, verifica los archivos faltantes antes de continuar."
    exit 1
fi

echo "============================================"
echo ""

# Verificar dependencias
echo "2️⃣  Verificando dependencias de Python..."
echo ""

if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Activando entorno virtual...${NC}"
    source venv/bin/activate
fi

pip list | grep -E "customtkinter|reportlab|tkcalendar|supabase|bcrypt|pillow" || {
    echo -e "${RED}❌ Faltan dependencias${NC}"
    echo ""
    echo "Instalando dependencias..."
    pip install -r requirements.txt
}

echo ""
echo -e "${GREEN}✓${NC} Dependencias verificadas"

# Crear carpeta dist si no existe
echo ""
echo "3️⃣  Preparando estructura de salida..."
mkdir -p dist
mkdir -p installer_output
echo -e "${GREEN}✓${NC} Carpetas de salida creadas"

# Limpiar builds anteriores
echo ""
echo "4️⃣  Limpiando builds anteriores..."
rm -rf build __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo -e "${GREEN}✓${NC} Limpieza completada"

echo ""
echo "============================================"
echo -e "${GREEN}✅ PROYECTO LISTO PARA DISTRIBUCIÓN${NC}"
echo "============================================"
echo ""
echo "Próximos pasos:"
echo ""
echo "  Para Linux:"
echo "    ./build_windows.sh"
echo ""
echo "  Para Windows:"
echo "    1. Copia el proyecto a Windows"
echo "    2. Ejecuta: python -m venv venv"
echo "    3. Ejecuta: venv\\Scripts\\activate"
echo "    4. Ejecuta: pip install -r requirements.txt"
echo "    5. Ejecuta: pyinstaller build.spec --clean"
echo "    6. Abre installer.iss con Inno Setup"
echo "    7. Build → Compile"
echo ""