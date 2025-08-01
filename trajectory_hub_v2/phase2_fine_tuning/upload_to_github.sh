#!/bin/bash
# Script para subir los archivos a GitHub

echo "📤 Subiendo archivos XYNZ a GitHub"
echo "=================================="

# Verificar si estamos en un repositorio git
if [ ! -d ".git" ]; then
    echo "⚠️  No estás en un repositorio Git"
    echo "Primero necesitas inicializar o clonar tu repositorio"
    exit 1
fi

# Agregar archivos de entrenamiento
echo "📁 Agregando archivos de scripts..."
git add scripts/train_simple.py
git add scripts/run_training_optimized.sh
git add scripts/verify_and_fix_dataset.py

# Verificar estado
echo -e "\n📊 Estado actual:"
git status --short

# Confirmar antes de commit
read -p "¿Deseas hacer commit de estos cambios? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Operación cancelada"
    exit 1
fi

# Hacer commit
echo -e "\n💾 Creando commit..."
git commit -m "Add simplified training scripts for XYNZ fine-tuning

- train_simple.py: Script simplificado sin problemas de tokenización
- run_training_optimized.sh: Script bash para ejecutar el entrenamiento
- verify_and_fix_dataset.py: Utilidad para verificar formato JSONL"

# Preguntar si hacer push
read -p "¿Deseas hacer push a GitHub? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "\n🚀 Haciendo push..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ Archivos subidos exitosamente a GitHub"
        echo ""
        echo "📋 Próximos pasos en RunPod:"
        echo "1. cd /workspace/xynz-finetuning"
        echo "2. git pull origin main"
        echo "3. cd phase2_fine_tuning"
        echo "4. chmod +x scripts/*.sh"
        echo "5. ./scripts/run_training_optimized.sh"
    else
        echo "❌ Error al hacer push"
        echo "Verifica tu conexión y permisos"
    fi
else
    echo "ℹ️  Commit creado localmente. Puedes hacer push más tarde con: git push origin main"
fi