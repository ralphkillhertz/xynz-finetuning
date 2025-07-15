# === find_update_method.py ===
# 🔧 Encuentra el método update en el engine
# ⚡ Búsqueda más flexible

import os
import re

def find_update_method():
    """Encuentra el método update con búsqueda flexible"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando método update...")
    
    # Buscar todas las definiciones de métodos
    method_pattern = r'^\s*(def\s+\w+\s*\([^)]*\):)'
    methods = re.findall(method_pattern, content, re.MULTILINE)
    
    print(f"\n📋 Total de métodos encontrados: {len(methods)}")
    
    # Buscar específicamente update
    update_methods = []
    for method in methods:
        if 'update' in method.lower():
            update_methods.append(method.strip())
    
    if update_methods:
        print(f"\n✅ Métodos con 'update': {len(update_methods)}")
        for m in update_methods:
            print(f"   - {m}")
    else:
        print("\n❌ No se encontró ningún método con 'update'")
        
        # Buscar otros métodos de actualización
        print("\n🔍 Buscando métodos alternativos...")
        candidates = ['step', 'tick', 'process', 'advance', 'run']
        for candidate in candidates:
            pattern = f'def\\s+{candidate}\\s*\\('
            if re.search(pattern, content):
                print(f"   ✅ Encontrado: {candidate}")
                
                # Mostrar contexto
                match = re.search(f'(def\\s+{candidate}[^:]+:)(.{{200}})', content, re.DOTALL)
                if match:
                    print(f"      Firma: {match.group(1)}")
                    preview = match.group(2).replace('\n', ' ')[:100]
                    print(f"      Preview: {preview}...")
    
    # Buscar líneas específicas con update
    print("\n🔍 Buscando llamadas a update:")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def update' in line:
            print(f"\n✅ Línea {i+1}: {line.strip()}")
            # Mostrar contexto
            for j in range(max(0, i-2), min(len(lines), i+10)):
                print(f"   {j+1}: {lines[j]}")
            break
    
    # Buscar procesamiento de motion_states
    print("\n🔍 Buscando procesamiento de motion_states:")
    for i, line in enumerate(lines):
        if 'motion_states' in line and ('for' in line or 'update' in line):
            print(f"   Línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    find_update_method()