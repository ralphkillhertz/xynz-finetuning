# === find_error_in_current_files.py ===
# 🔍 Buscar el error SOLO en archivos actuales
# ⚡ Ignorar backups para enfocarnos en el problema real

import os

print("🎯 Analizando SOLO archivos actuales en trajectory_hub/core/\n")

# Archivos actuales
current_files = {
    'engine': './trajectory_hub/core/enhanced_trajectory_engine.py',
    'components': './trajectory_hub/core/motion_components.py'
}

# Verificar que existen
for name, path in current_files.items():
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✅ {name}: {path} ({size:,} bytes)")
    else:
        print(f"❌ {name}: NO ENCONTRADO en {path}")

print("\n" + "="*50 + "\n")

# Buscar el patrón problemático en motion_components.py actual
if os.path.exists(current_files['components']):
    print("🔍 Analizando motion_components.py actual...\n")
    
    with open(current_files['components'], 'r') as f:
        lines = f.readlines()
    
    # Buscar update_with_deltas
    print("1️⃣ Buscando update_with_deltas:")
    in_method = False
    method_start = 0
    
    for i, line in enumerate(lines):
        if 'def update_with_deltas' in line:
            in_method = True
            method_start = i
            print(f"   Encontrado en línea {i+1}")
            
        if in_method and i < method_start + 50:  # Ver las siguientes 50 líneas
            if 'if ' in line and 'enabled' in line:
                print(f"   Línea {i+1}: {line.strip()}")
                if 'component.enabled' in line and 'isinstance' not in line and 'getattr' not in line:
                    print(f"      ⚠️ POSIBLE PROBLEMA!")
    
    # Buscar en MacroRotation
    print("\n2️⃣ Buscando en clase MacroRotation:")
    in_macro = False
    
    for i, line in enumerate(lines):
        if 'class MacroRotation' in line:
            in_macro = True
            print(f"   Encontrada en línea {i+1}")
            
        if in_macro and 'class ' in line and 'MacroRotation' not in line:
            in_macro = False
            
        if in_macro:
            if 'self.enabled' in line and '=' in line:
                print(f"   Línea {i+1}: {line.strip()}")
            if 'if ' in line and '.enabled' in line:
                print(f"   Línea {i+1}: {line.strip()}")
                
    # Buscar TODAS las comparaciones con enabled
    print("\n3️⃣ TODAS las comparaciones con 'enabled':")
    count = 0
    for i, line in enumerate(lines):
        if 'if ' in line and 'enabled' in line and 'isinstance' not in line:
            count += 1
            print(f"   Línea {i+1}: {line.strip()}")
            if count > 20:
                print("   ... (más de 20 encontradas)")
                break

# Ahora buscar en el test qué está pasando
print("\n" + "="*50 + "\n")
print("🔍 Analizando el flujo en test_rotation_ms_final.py...\n")

if os.path.exists('test_rotation_ms_final.py'):
    with open('test_rotation_ms_final.py', 'r') as f:
        content = f.read()
        
    # Ver si hay algún manejo del error
    if 'Error en macro_rotation' in content:
        print("✅ El test captura el error y muestra: 'Error en macro_rotation'")
        print("   Esto significa que el error está en el procesamiento de macro_rotation")
        
# Buscar específicamente dónde se procesa macro_rotation
print("\n4️⃣ Buscando procesamiento de 'macro_rotation' en update_with_deltas:")

if os.path.exists(current_files['components']):
    with open(current_files['components'], 'r') as f:
        lines = f.readlines()
        
    in_update = False
    for i, line in enumerate(lines):
        if 'def update_with_deltas' in line:
            in_update = True
            continue
            
        if in_update and line.strip() and not line.strip().startswith('#') and line[0] not in ' \t':
            in_update = False
            
        if in_update and 'macro_rotation' in line:
            # Mostrar contexto
            start = max(0, i-3)
            end = min(len(lines), i+4)
            print(f"\n   Contexto alrededor de línea {i+1}:")
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"   {marker} {j+1}: {lines[j].rstrip()}")