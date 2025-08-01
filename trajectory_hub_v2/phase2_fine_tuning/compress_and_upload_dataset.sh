#!/bin/bash
# Script para comprimir y subir dataset a GitHub

echo "📦 Comprimiendo dataset XYNZ..."
cd dataset/processed/alpaca

# Comprimir archivos JSONL
tar -czf xynz_dataset.tar.gz train.jsonl validation.jsonl

# Mostrar tamaño
echo "📊 Tamaño del archivo comprimido:"
ls -lh xynz_dataset.tar.gz

# Volver al directorio de fase 2
cd ../../..

# Verificar tamaño (GitHub tiene límite de 100MB por archivo)
SIZE=$(du -m dataset/processed/alpaca/xynz_dataset.tar.gz | cut -f1)
if [ $SIZE -gt 100 ]; then
    echo "⚠️  Archivo muy grande para GitHub (${SIZE}MB > 100MB)"
    echo "Dividiendo en partes..."
    cd dataset/processed/alpaca
    split -b 95M xynz_dataset.tar.gz xynz_dataset_part_
    echo "✅ Dividido en partes de 95MB"
    cd ../../..
fi

echo ""
echo "📤 Para subir a GitHub:"
echo "1. git add dataset/processed/alpaca/xynz_dataset*"
echo "2. git commit -m 'Add XYNZ training dataset (16,500 examples)'"
echo "3. git push origin feature/phase2-fine-tuning"
echo ""
echo "O usa Git LFS para archivos grandes:"
echo "git lfs track 'dataset/processed/alpaca/*.tar.gz'"
echo "git add .gitattributes"
echo "git add dataset/processed/alpaca/xynz_dataset.tar.gz"