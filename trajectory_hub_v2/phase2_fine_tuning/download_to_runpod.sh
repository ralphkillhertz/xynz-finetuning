#!/bin/bash
# Script para ejecutar en RunPod para descargar y preparar todo

echo "🚀 XYNZ Fine-tuning - Setup en RunPod"
echo "====================================="

# Directorio de trabajo
WORK_DIR="/workspace/xynz-finetuning"

# Crear directorio si no existe
mkdir -p $WORK_DIR
cd $WORK_DIR

# Opción 1: Clonar desde GitHub (si tienes el repo)
echo "📥 Descargando archivos desde GitHub..."
if [ -d ".git" ]; then
    echo "Actualizando repositorio existente..."
    git pull origin main
else
    echo "Clonando repositorio..."
    # Reemplaza con tu URL de GitHub
    git clone https://github.com/ralphkillhertz/xynz-finetuning.git .
fi

# Opción 2: Descargar archivos directamente (alternativa)
# echo "📥 Descargando archivos directamente..."
# mkdir -p phase2_fine_tuning/scripts
# cd phase2_fine_tuning/scripts
# wget https://raw.githubusercontent.com/tu-usuario/repo/main/scripts/train_simple.py
# wget https://raw.githubusercontent.com/tu-usuario/repo/main/scripts/run_training_optimized.sh
# wget https://raw.githubusercontent.com/tu-usuario/repo/main/scripts/verify_and_fix_dataset.py

# Hacer ejecutables los scripts
echo -e "\n🔧 Configurando permisos..."
cd $WORK_DIR/phase2_fine_tuning
chmod +x scripts/*.sh
chmod +x scripts/*.py

# Verificar estructura
echo -e "\n📁 Verificando estructura de archivos..."
if [ -f "scripts/train_simple.py" ]; then
    echo "✅ train_simple.py encontrado"
else
    echo "❌ ERROR: train_simple.py no encontrado"
fi

if [ -f "scripts/run_training_optimized.sh" ]; then
    echo "✅ run_training_optimized.sh encontrado"
else
    echo "❌ ERROR: run_training_optimized.sh no encontrado"
fi

# Verificar dataset
echo -e "\n📚 Verificando dataset..."
if [ -f "dataset/processed/alpaca/train.jsonl" ]; then
    echo "✅ Dataset de entrenamiento encontrado"
    echo "Ejemplos: $(wc -l < dataset/processed/alpaca/train.jsonl)"
else
    echo "⚠️  Dataset no encontrado. Necesitas generarlo o subirlo."
fi

# Instalar dependencias si es necesario
echo -e "\n📦 Verificando dependencias..."
python -c "import transformers, peft, datasets, accelerate, bitsandbytes" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependencias faltantes..."
    pip install transformers==4.38.0 peft==0.8.2 datasets==2.16.0 accelerate==0.26.0 bitsandbytes==0.42.0
fi

echo -e "\n✅ Setup completado!"
echo ""
echo "📋 Para iniciar el entrenamiento:"
echo "cd $WORK_DIR/phase2_fine_tuning"
echo "./scripts/run_training_optimized.sh"
echo ""
echo "O directamente:"
echo "python scripts/train_simple.py"