# === check_method_existence.py ===
# 🔧 Verificar si el método existe y dónde está

import os
import subprocess

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

print("🔍 VERIFICACIÓN DE set_macro_concentration\n")

# 1. Buscar con grep
print("1. Buscando con grep...")
result = subprocess.run(['grep', '-n', 'def set_macro_concentration', engine_file], 
                       capture_output=True, text=True)
if result.stdout:
    print(f"   Encontrado:\n{result.stdout}")
else:
    print("   ❌ NO ENCONTRADO")

# 2. Verificar manualmente
print("\n2. Verificación manual...")
with open(engine_file, 'r') as f:
    lines = f.readlines()
    
found = False
for i, line in enumerate(lines):
    if 'set_macro_concentration' in line:
        print(f"   Línea {i+1}: {line.strip()}")
        found = True
        # Mostrar contexto
        for j in range(max(0, i-2), min(len(lines), i+10)):
            print(f"     {j+1}: {lines[j].rstrip()}")
        break

if not found:
    print("   ❌ NO EXISTE el método")
    
# 3. Insertar directamente
print("\n3. INSERTANDO DIRECTAMENTE...")
    
# Buscar create_macro
create_macro_line = -1
for i, line in enumerate(lines):
    if 'def create_macro' in line and not line.strip().startswith('#'):
        create_macro_line = i
        print(f"   create_macro encontrado en línea {i+1}")
        break

if create_macro_line > 0:
    # Buscar el final de create_macro (siguiente def o final de clase)
    end_line = len(lines)
    indent = ""
    for i in range(create_macro_line + 1, len(lines)):
        if lines[i].strip() and not lines[i].startswith(' '):
            end_line = i
            break
        if lines[i].strip().startswith('def '):
            end_line = i
            # Capturar indentación
            indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
            break
    
    print(f"   Insertando después de línea {end_line}")
    
    # Método simple y directo
    method = f'''{indent}def set_macro_concentration(self, macro_id: str, factor: float):
{indent}    """Set concentration factor."""
{indent}    if macro_id in self._macros:
{indent}        self._macros[macro_id].concentration_factor = factor
{indent}        print(f"✅ {macro_id} concentration = {factor}")
{indent}    else:
{indent}        print(f"❌ Macro {macro_id} not found")

'''
    
    # Insertar
    lines.insert(end_line, method)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    print("   ✅ Método insertado")

# 4. Test inmediato
print("\n4. TEST INMEDIATO:")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    
    # Verificar que el método existe
    if hasattr(engine, 'set_macro_concentration'):
        print("   ✅ Método existe")
        
        # Crear macro y probar
        macro_id = engine.create_macro("test", source_count=2)
        engine.set_macro_concentration(macro_id, 0.5)
        
        # Verificar
        if macro_id in engine._macros:
            factor = getattr(engine._macros[macro_id], 'concentration_factor', None)
            print(f"   Factor guardado: {factor}")
            
            if factor == 0.5:
                print("\n   🎉 ¡FUNCIONA!")
    else:
        print("   ❌ Método NO existe")
        
except Exception as e:
    print(f"   Error: {e}")