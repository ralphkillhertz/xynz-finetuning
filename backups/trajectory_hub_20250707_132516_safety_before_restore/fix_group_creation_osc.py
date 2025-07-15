# === fix_group_creation_osc.py ===
# 🔧 Fix: Asegurar que los grupos se crean en Spat
# ⚡ Las posiciones funcionan, faltan los grupos

import os

def add_group_creation():
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    print("🔧 ARREGLANDO CREACIÓN DE GRUPOS OSC\n")
    
    # Buscar create_macro
    for i, line in enumerate(lines):
        if 'def create_macro(' in line and not line.strip().startswith('#'):
            print(f"✅ create_macro encontrado en línea {i+1}")
            
            # Buscar return macro_id
            for j in range(i, min(i+100, len(lines))):
                if 'return macro_id' in lines[j]:
                    print(f"   return en línea {j+1}")
                    
                    # Insertar código OSC antes del return
                    indent = '        '  # 8 espacios
                    osc_code = f'''{indent}# Crear grupo en Spat via OSC
{indent}if hasattr(self, 'osc_bridge') and self.osc_bridge:
{indent}    try:
{indent}        # Usar el nombre del macro (sin el prefijo macro_X_)
{indent}        group_name = name
{indent}        print(f"📡 Creando grupo OSC: '{{group_name}}'")
{indent}        
{indent}        # Crear el grupo
{indent}        if hasattr(self.osc_bridge, 'create_group'):
{indent}            self.osc_bridge.create_group(macro_id, group_name)
{indent}        
{indent}        # Añadir cada fuente al grupo
{indent}        if hasattr(self.osc_bridge, 'add_source_to_group'):
{indent}            for sid in source_ids:
{indent}                self.osc_bridge.add_source_to_group(sid, group_name)
{indent}        
{indent}    except Exception as e:
{indent}        print(f"❌ Error OSC: {{e}}")
{indent}        import traceback
{indent}        traceback.print_exc()

'''
                    lines.insert(j, osc_code)
                    break
            break
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ Código OSC añadido a create_macro")
    
    # Test
    with open("test_groups_osc.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST GRUPOS OSC\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

print("\\nCreando macro 'Pajaros' con 3 fuentes...")
macro_id = engine.create_macro("Pajaros", source_count=3, formation="triangle")

print("\\n✅ VERIFICA EN SPAT OSC MONITOR:")
print("   Deberías ver:")
print("   - /group/new ['Pajaros']")
print("   - /source/0/group ['Pajaros']")
print("   - /source/1/group ['Pajaros']") 
print("   - /source/2/group ['Pajaros']")

print("\\n🎯 En Spat, el grupo 'Pajaros' debería existir")
print("   con las fuentes 1, 2 y 3 dentro")
''')

if __name__ == "__main__":
    add_group_creation()