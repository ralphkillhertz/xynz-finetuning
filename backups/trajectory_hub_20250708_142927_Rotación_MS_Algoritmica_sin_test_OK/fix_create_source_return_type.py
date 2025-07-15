# === fix_create_source_return_type.py ===
# 🔧 Fix: create_source debe retornar int, no string
# ⚡ Impacto: CRÍTICO para tests

import os
import re

def fix_create_source():
    """Arreglar create_source para que retorne int"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y arreglar la línea problemática
    # Buscar donde se retorna el source_id
    pattern = r'(def create_source.*?)(return f"[^"]*{source_id}[^"]*")'
    
    def replacement(match):
        method_part = match.group(1)
        return_line = match.group(2)
        
        # Si retorna un string formateado, cambiar para retornar solo el ID
        if 'return f"' in return_line:
            # Extraer solo para retornar el source_id
            new_return = 'return source_id'
            print(f"🔧 Cambiando: {return_line.strip()}")
            print(f"   Por: {new_return}")
            return method_part + new_return
        return match.group(0)
    
    # Aplicar fix
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Si no encontró el patrón, buscar de otra forma
    if new_content == content:
        # Buscar líneas específicas
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'return f"' in line and 'source_id' in line and 'def create_source' in '\n'.join(lines[max(0,i-20):i]):
                print(f"🔧 Encontrado en línea {i+1}: {line.strip()}")
                lines[i] = '        return source_id  # Retornar int, no string'
                new_content = '\n'.join(lines)
                break
    
    if new_content != content:
        # Backup
        import shutil
        from datetime import datetime
        backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_name)
        
        # Escribir
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ create_source arreglado para retornar int")
        return True
    
    print("⚠️ No se encontró el patrón a corregir")
    
    # Diagnóstico adicional
    print("\n🔍 Buscando método create_source...")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def create_source' in line:
            print(f"\nEncontrado en línea {i+1}")
            # Mostrar las siguientes 30 líneas
            for j in range(i, min(i+30, len(lines))):
                if 'return' in lines[j]:
                    print(f"{j+1}: {lines[j].rstrip()}")
    
    return False

if __name__ == "__main__":
    print("🔧 Arreglando create_source...")
    
    if fix_create_source():
        print("\n✅ Fix aplicado")
        print("📝 Ejecuta: python test_macro_rotation_final_correct.py")
    else:
        print("\n⚠️ Necesita revisión manual")