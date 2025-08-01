#!/usr/bin/env python3
"""
Script para verificar y corregir el formato del dataset XYNZ
"""
import json
import os
from pathlib import Path

def verify_jsonl(file_path):
    """Verifica que un archivo JSONL esté bien formateado"""
    print(f"\n📋 Verificando: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    valid_lines = 0
    errors = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                # Verificar estructura esperada
                if 'instruction' not in obj or 'output' not in obj:
                    errors.append(f"Línea {i}: Falta 'instruction' o 'output'")
                else:
                    valid_lines += 1
            except json.JSONDecodeError as e:
                errors.append(f"Línea {i}: Error JSON - {e}")
    
    print(f"✅ Líneas válidas: {valid_lines}")
    
    if errors:
        print(f"⚠️  Errores encontrados: {len(errors)}")
        for error in errors[:5]:  # Mostrar solo primeros 5 errores
            print(f"   {error}")
        if len(errors) > 5:
            print(f"   ... y {len(errors) - 5} errores más")
        return False
    
    return True

def fix_jsonl_format(input_path, output_path):
    """Intenta reparar un archivo JSONL mal formateado"""
    print(f"\n🔧 Reparando formato JSONL...")
    
    # Leer contenido completo
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Intentar diferentes métodos de reparación
    objects = []
    
    # Método 1: Buscar JSONs individuales
    import re
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, content)
    
    for match in matches:
        try:
            obj = json.loads(match)
            if 'instruction' in obj and 'output' in obj:
                objects.append(obj)
        except:
            pass
    
    if not objects:
        # Método 2: Intentar split por líneas
        for line in content.split('\n'):
            if line.strip():
                try:
                    obj = json.loads(line)
                    if 'instruction' in obj and 'output' in obj:
                        objects.append(obj)
                except:
                    pass
    
    # Guardar objetos válidos
    if objects:
        with open(output_path, 'w', encoding='utf-8') as f:
            for obj in objects:
                f.write(json.dumps(obj, ensure_ascii=False) + '\n')
        print(f"✅ Archivo reparado: {len(objects)} objetos válidos guardados")
        return True
    else:
        print("❌ No se pudieron recuperar objetos válidos")
        return False

def main():
    """Verificar y reparar datasets"""
    base_path = "/workspace/xynz-finetuning/phase2_fine_tuning/dataset/processed/alpaca"
    
    # Archivos a verificar
    files = [
        f"{base_path}/train.jsonl",
        f"{base_path}/validation.jsonl"
    ]
    
    print("🔍 Verificación de Dataset XYNZ")
    print("=" * 40)
    
    all_valid = True
    
    for file_path in files:
        if not verify_jsonl(file_path):
            all_valid = False
            
            # Intentar reparar
            backup_path = file_path + ".backup"
            fixed_path = file_path + ".fixed"
            
            print(f"\n🔧 Intentando reparar {file_path}...")
            
            # Hacer backup
            import shutil
            shutil.copy(file_path, backup_path)
            print(f"📁 Backup creado: {backup_path}")
            
            # Intentar reparar
            if fix_jsonl_format(file_path, fixed_path):
                # Reemplazar original con versión reparada
                shutil.move(fixed_path, file_path)
                print(f"✅ Archivo reparado exitosamente")
                
                # Verificar de nuevo
                verify_jsonl(file_path)
            else:
                print(f"❌ No se pudo reparar automáticamente")
    
    if all_valid:
        print("\n✅ Todos los archivos están en formato correcto")
    else:
        print("\n⚠️  Algunos archivos necesitan atención")
    
    # Mostrar estadísticas
    print("\n📊 Estadísticas del dataset:")
    for file_path in files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = sum(1 for line in f if line.strip())
            print(f"  {os.path.basename(file_path)}: {lines} ejemplos")

if __name__ == "__main__":
    main()