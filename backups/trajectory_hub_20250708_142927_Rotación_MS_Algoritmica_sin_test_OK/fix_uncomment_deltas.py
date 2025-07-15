# === fix_uncomment_deltas.py ===
# 🔧 Fix DEFINITIVO - Descomenta el código de deltas
# ⚡ El código está comentado, por eso no funciona

import os
from datetime import datetime

def fix_uncomment_deltas():
    """Descomenta el código de deltas que está entre comillas triples"""
    
    print("🔧 DESCOMENTANDO CÓDIGO DE DELTAS")
    print("="*60)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar las comillas triples que comentan el código
    comment_start = -1
    comment_end = -1
    
    for i, line in enumerate(lines):
        if '"""' in line and 'CORRECCIÓN FINAL' in lines[i-1] if i > 0 else False:
            comment_start = i
        elif '"""' in line and comment_start > 0 and i > comment_start:
            comment_end = i
            break
    
    print(f"📍 Comentario encontrado:")
    print(f"   Inicio: línea {comment_start + 1}")
    print(f"   Fin: línea {comment_end + 1}")
    
    if comment_start > 0 and comment_end > 0:
        # Eliminar las líneas con """ 
        lines[comment_start] = ''  # Eliminar línea de inicio
        lines[comment_end] = ''    # Eliminar línea de fin
        
        print("✅ Comillas triples eliminadas")
        print("✅ Código de deltas ahora está activo")
    else:
        print("❌ No se encontraron las comillas triples")
        return False
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Archivo actualizado")
    
    # Verificar sintaxis
    try:
        with open(engine_path, 'r', encoding='utf-8') as f:
            compile(f.read(), engine_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return False

if __name__ == "__main__":
    print("🎯 PROBLEMA DEFINITIVO ENCONTRADO")
    print("\nEl código de procesamiento de deltas está COMENTADO")
    print("Está entre comillas triples (líneas 5-35)")
    print("Por eso NUNCA se ejecuta")
    
    if fix_uncomment_deltas():
        print("\n✅ CÓDIGO DESCOMENTADO")
        print("\n🎉 AHORA SÍ FUNCIONARÁ")
        print("\n📋 Ejecuta:")
        print("$ python test_final_success.py")