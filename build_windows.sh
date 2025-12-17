#!/bin/bash
# build_windows.sh - Script para construir el ejecutable

echo "============================================"
echo "🏗️  CONSTRUYENDO EJECUTABLE DE CONECTAR"
echo "============================================"
echo ""

# Verificar que estamos en el entorno virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Activando entorno virtual..."
    source venv/bin/activate
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Verificar que existan las imágenes
echo ""
echo "📁 Verificando recursos..."
if [ ! -f "imagenes/logo.png" ]; then
    echo "⚠️  ADVERTENCIA: No se encontró imagenes/logo.png"
fi

if [ ! -f "imagenes/favicon.png" ]; then
    echo "⚠️  ADVERTENCIA: No se encontró imagenes/favicon.png"
fi

# Construir con PyInstaller
echo ""
echo "🔨 Construyendo ejecutable..."
pyinstaller build.spec --clean

# Verificar resultado
if [ -f "dist/CONECTAR" ] || [ -f "dist/CONECTAR.exe" ]; then
    echo ""
    echo "============================================"
    echo "✅ EJECUTABLE CREADO EXITOSAMENTE"
    echo "============================================"
    echo ""
    echo "📦 Ubicación: dist/CONECTAR"
    echo ""
    
    # Mostrar tamaño
    if [ -f "dist/CONECTAR" ]; then
        SIZE=$(du -h "dist/CONECTAR" | cut -f1)
        echo "📊 Tamaño: $SIZE"
    fi
    
    echo ""
    echo "Para probar el ejecutable:"
    echo "  cd dist"
    echo "  ./CONECTAR"
    echo ""
else
    echo ""
    echo "============================================"
    echo "❌ ERROR AL CREAR EL EJECUTABLE"
    echo "============================================"
    echo ""
    echo "Revisa los errores arriba ☝️"
    echo ""
    exit 1
fi