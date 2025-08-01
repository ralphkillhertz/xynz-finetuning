#!/bin/bash
# Script optimizado para ejecutar el entrenamiento XYNZ en RunPod

echo "🚀 XYNZ Fine-tuning - Script Optimizado"
echo "======================================"
date

# Configurar entorno
export CUDA_VISIBLE_DEVICES=0
export TRANSFORMERS_CACHE=/workspace/cache
export HF_DATASETS_CACHE=/workspace/cache
export PYTHONUNBUFFERED=1

# Crear directorios necesarios
mkdir -p /workspace/xynz-finetuning/models
mkdir -p /workspace/xynz-finetuning/logs
mkdir -p /workspace/cache

# Cambiar al directorio de trabajo
cd /workspace/xynz-finetuning/trajectory_hub_v2/phase2_fine_tuning

# Verificar GPU
echo -e "\n📊 Información de GPU:"
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits

# Verificar dataset
echo -e "\n📚 Verificando dataset:"
if [ -f "dataset/processed/alpaca/train.jsonl" ]; then
    echo "✅ Train dataset encontrado"
    echo "Ejemplos: $(wc -l < dataset/processed/alpaca/train.jsonl)"
else
    echo "❌ ERROR: No se encontró train.jsonl"
    exit 1
fi

if [ -f "dataset/processed/alpaca/validation.jsonl" ]; then
    echo "✅ Validation dataset encontrado"
    echo "Ejemplos: $(wc -l < dataset/processed/alpaca/validation.jsonl)"
else
    echo "❌ ERROR: No se encontró validation.jsonl"
    exit 1
fi

# Ejecutar entrenamiento
echo -e "\n🎯 Iniciando entrenamiento..."
echo "Configuración:"
echo "- Modelo: DeepSeek-R1-Distill-Qwen-7B"
echo "- Épocas: 3"
echo "- LoRA r: 32"
echo "- Batch size: 2"
echo "- Gradient accumulation: 8"

# Ejecutar con logging detallado
python scripts/train_simple.py 2>&1 | tee logs/training_$(date +%Y%m%d_%H%M%S).log

# Verificar resultado
if [ $? -eq 0 ]; then
    echo -e "\n✅ Entrenamiento completado exitosamente"
    echo "Modelo guardado en: /workspace/xynz-finetuning/trajectory_hub_v2/phase2_fine_tuning/models/deepseek-xynz-lora"
    
    # Mostrar tamaño del modelo
    echo -e "\n📦 Tamaño del modelo:"
    du -sh /workspace/xynz-finetuning/trajectory_hub_v2/phase2_fine_tuning/models/deepseek-xynz-lora/
else
    echo -e "\n❌ Error durante el entrenamiento"
    echo "Revisa los logs en: logs/"
    exit 1
fi

echo -e "\n🎉 Proceso finalizado"
date