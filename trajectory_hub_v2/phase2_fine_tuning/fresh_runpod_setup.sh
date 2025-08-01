#!/bin/bash
# Script de instalación completa para RunPod desde cero
# XYNZ Fine-tuning Setup - Fresh Install

echo "======================================"
echo "🚀 XYNZ Fine-tuning - Fresh Setup"
echo "======================================"
echo "Fecha: $(date)"
echo ""

# Limpiar workspace si es necesario
if [ -d "/workspace/xynz-finetuning" ]; then
    echo "⚠️  Directorio existente encontrado"
    read -p "¿Eliminar instalación anterior? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "🗑️  Eliminando instalación anterior..."
        rm -rf /workspace/xynz-finetuning
    else
        echo "❌ Abortando para preservar datos existentes"
        exit 1
    fi
fi

# Ir al workspace
cd /workspace

# Clonar repositorio
echo "📥 Clonando repositorio desde GitHub..."
git clone -b feature/phase2-fine-tuning https://github.com/ralphkillhertz/xynz-finetuning.git

# Verificar clonación
if [ ! -d "xynz-finetuning" ]; then
    echo "❌ Error al clonar repositorio"
    exit 1
fi

cd xynz-finetuning/trajectory_hub_v2/phase2_fine_tuning

# Descomprimir dataset
echo -e "\n📦 Descomprimiendo dataset..."
cd dataset/processed/alpaca
tar -xzf xynz_dataset.tar.gz

# Verificar archivos
echo -e "\n✅ Verificando archivos..."
if [ -f "train.jsonl" ] && [ -f "validation.jsonl" ]; then
    echo "Dataset encontrado:"
    echo "  - train.jsonl: $(wc -l < train.jsonl) ejemplos"
    echo "  - validation.jsonl: $(wc -l < validation.jsonl) ejemplos"
else
    echo "❌ Error: Dataset no encontrado"
    exit 1
fi

# Volver al directorio principal
cd /workspace/xynz-finetuning/trajectory_hub_v2/phase2_fine_tuning

# Hacer ejecutables los scripts
echo -e "\n🔧 Configurando permisos..."
chmod +x scripts/*.sh
chmod +x scripts/*.py
chmod +x *.sh

# Instalar dependencias de Python
echo -e "\n📦 Instalando dependencias de Python..."
pip install --upgrade pip

# Instalar PyTorch con CUDA
echo "🔥 Instalando PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Instalar librerías de entrenamiento
echo "📚 Instalando librerías de ML..."
pip install transformers==4.38.0
pip install peft==0.8.2
pip install datasets==2.16.0
pip install accelerate==0.26.0
pip install bitsandbytes==0.42.0
pip install scipy
pip install tensorboard
pip install sentencepiece  # Requerido para algunos tokenizers

# Verificar GPU
echo -e "\n🖥️  Verificando GPU..."
python -c "import torch; print(f'GPU disponible: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"No disponible\"}')"

# Verificar instalación
echo -e "\n🔍 Verificando instalación..."
python -c "
import transformers
import peft
import datasets
import accelerate
import bitsandbytes
print('✅ Todas las librerías instaladas correctamente')
print(f'Transformers: {transformers.__version__}')
print(f'PEFT: {peft.__version__}')
print(f'Datasets: {datasets.__version__}')
print(f'Accelerate: {accelerate.__version__}')
print(f'Bitsandbytes: {bitsandbytes.__version__}')
"

# Crear directorios necesarios
echo -e "\n📁 Creando directorios..."
mkdir -p models
mkdir -p logs
mkdir -p cache

# Configurar variables de entorno
echo -e "\n🌍 Configurando entorno..."
export TRANSFORMERS_CACHE=/workspace/cache
export HF_DATASETS_CACHE=/workspace/cache
export CUDA_VISIBLE_DEVICES=0

# Mostrar estructura final
echo -e "\n📂 Estructura del proyecto:"
tree -L 3 . || ls -la

echo -e "\n✅ ¡Instalación completa!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configurar Hugging Face (opcional):"
echo "   huggingface-cli login"
echo ""
echo "2. Ejecutar el entrenamiento:"
echo "   ./scripts/run_training_optimized.sh"
echo ""
echo "3. O ejecutar directamente:"
echo "   python scripts/train_simple.py"
echo ""
echo "4. Monitorear con TensorBoard:"
echo "   tensorboard --logdir models/ --host 0.0.0.0 --port 6006"
echo ""
echo "¡Listo para entrenar! 🚀"