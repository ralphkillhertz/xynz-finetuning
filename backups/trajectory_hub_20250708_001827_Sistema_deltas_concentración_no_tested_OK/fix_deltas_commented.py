# === fix_deltas_commented.py ===
# 🔧 Fix preciso - Descomenta el código de deltas
# ⚡ Busca las comillas triples específicas

import os
from datetime import datetime

def fix_commented_deltas():
    """Descomenta el código de deltas que está entre comillas triples"""
    
    print("🔧 DESCOMENTANDO CÓDIGO DE DELTAS - VERSIÓN PRECISA")
    print("="*60)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Backup creado")
    
    # Buscar el método update
    update_line = -1
    for i, line in enumerate(lines):
        if 'def update(self)' in line:
            update_line = i
            print(f"✅ Método update encontrado en línea {i+1}")
            break
    
    if update_line == -1:
        print("❌ No se encontró método update")
        return False
    
    # Buscar las comillas triples después de update
    comment_start = -1
    comment_end = -1
    
    for i in range(update_line, min(update_line + 40, len(lines))):
        if '"""' in lines[i]:
            if comment_start == -1:
                comment_start = i
                print(f"📍 Inicio de comentario encontrado en línea {i+1}: {lines[i].strip()}")
            else:
                comment_end = i
                print(f"📍 Fin de comentario encontrado en línea {i+1}: {lines[i].strip()}")
                break
    
    if comment_start > 0 and comment_end > 0:
        print(f"\n🔍 Contenido comentado (líneas {comment_start+1}-{comment_end+1}):")
        
        # Verificar que contiene el código de deltas
        has_delta_code = False
        for i in range(comment_start, comment_end):
            if 'PROCESAMIENTO DE DELTAS' in lines[i]:
                has_delta_code = True
                print("   ✅ Contiene código de deltas")
                break
        
        if has_delta_code:
            # Eliminar las líneas con comillas triples
            lines[comment_start] = '\n'  # Reemplazar con línea vacía
            lines[comment_end] = '\n'    # Reemplazar con línea vacía
            
            print("\n✅ Comillas triples eliminadas")
            print("✅ Código de deltas activado")
            
            # Escribir archivo
            with open(engine_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
        else:
            print("❌ El bloque comentado no contiene código de deltas")
    else:
        print("❌ No se encontraron las comillas triples correctamente")
        
        # Mostrar las primeras líneas después de update para debug
        print("\n🔍 Primeras 20 líneas después de update():")
        for i in range(update_line, min(update_line + 20, len(lines))):
            print(f"{i+1:3d}: {lines[i].rstrip()}")
    
    return False

if __name__ == "__main__":
    print("🎯 FIX DEL COMENTARIO EN EL CÓDIGO")
    print("\nProblema: El código de deltas está dentro de comillas triples")
    print("Por eso nunca se ejecuta")
    
    if fix_commented_deltas():
        print("\n✅ CÓDIGO ACTIVADO")
        print("\n🎉 Ejecuta ahora:")
        print("$ python test_deltas_working_now.py")
    else:
        print("\n❌ No se pudo arreglar")
        print("\n📋 Solución manual:")
        print("1. Abre trajectory_hub/core/enhanced_trajectory_engine.py")
        print("2. Busca def update(self)")
        print("3. Elimina las comillas triples (líneas 5 y 35 aprox)")
        print("4. Guarda el archivo")