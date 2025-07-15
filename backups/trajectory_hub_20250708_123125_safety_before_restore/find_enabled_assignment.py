# === find_enabled_assignment.py ===
# 🔍 Buscar dónde self.enabled se convierte en array
# ⚡ El problema está en la asignación, no en la comparación

import os

print("🔍 Buscando asignaciones problemáticas de 'enabled'\n")

filepath = './trajectory_hub/core/motion_components.py'

with open(filepath, 'r') as f:
    lines = f.readlines()

print("1️⃣ Buscando en __init__ de MacroRotation:\n")

# Encontrar __init__ de MacroRotation
in_macro = False
in_init = False

for i, line in enumerate(lines):
    if 'class MacroRotation' in line:
        in_macro = True
        
    if in_macro and 'def __init__' in line:
        in_init = True
        print(f"✅ __init__ encontrado en línea {i+1}")
        
    if in_init and in_macro:
        if 'def ' in line and '__init__' not in line:
            in_init = False
            
        if 'self.enabled' in line:
            print(f"   Línea {i+1}: {line.strip()}")
            # Ver contexto
            if i > 0:
                print(f"   Línea {i}: {lines[i-1].strip()}")

print("\n2️⃣ Buscando TODAS las asignaciones a 'enabled' en el archivo:\n")

count = 0
for i, line in enumerate(lines):
    if 'enabled =' in line or '.enabled =' in line:
        count += 1
        print(f"Línea {i+1}: {line.strip()}")
        
        # Buscar si hay arrays cerca
        context_start = max(0, i-3)
        context_end = min(len(lines), i+3)
        
        for j in range(context_start, context_end):
            if 'array' in lines[j] or 'np.' in lines[j]:
                print(f"   ⚠️ Array encontrado cerca en línea {j+1}: {lines[j].strip()}")
                
        if count > 20:
            print("... (más de 20 encontradas)")
            break

print("\n3️⃣ Buscando el problema específico en línea 706:\n")

# La línea 706 que vimos antes
if len(lines) > 705:
    print(f"Línea 706: {lines[705].strip()}")
    print("\nContexto completo:")
    for i in range(700, min(710, len(lines))):
        print(f"   {i+1}: {lines[i].rstrip()}")

print("\n4️⃣ Buscando dónde se COMPARA enabled sin getattr:\n")

# Buscar comparaciones directas
for i, line in enumerate(lines):
    if 'if ' in line and 'enabled' in line:
        # Excluir casos seguros
        if 'getattr' in line or 'isinstance' in line:
            continue
            
        # Si es solo "if enabled:" o "if self.enabled:"
        if line.strip() in ['if enabled:', 'if self.enabled:', 'if component.enabled:']:
            print(f"Línea {i+1}: {line.strip()}")
            print(f"   ⚠️ COMPARACIÓN DIRECTA SIN PROTECCIÓN")

print("\n" + "="*50)
print("\n💡 El problema está en la línea 706:")
print("   self.enabled = bool(abs(speed_x) > 0.001 or abs(speed_y) > 0.001 or abs(speed_z) > 0.001)")
print("\n   Si speed_x, speed_y o speed_z son arrays, la comparación falla!")