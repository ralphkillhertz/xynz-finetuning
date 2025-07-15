# === fix_macro_trajectory_final.py ===
# 🔧 Fix: Arreglar create_macro para que REALMENTE configure las fuentes
# ⚡ Y corregir el problema del SET

import re

print("🔧 ARREGLANDO create_macro Y source_ids...\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Buscar create_macro
create_match = re.search(r'def create_macro\(.*?\):.*?(?=\n    def|\Z)', content, re.DOTALL)
if not create_match:
    print("❌ No se encontró create_macro")
    exit(1)

old_method = create_match.group(0)
print("✅ Método create_macro encontrado")

# Ver si ya añade a motion_states
if 'active_components["macro_trajectory"]' in old_method:
    print("⚠️ Parece que SÍ intenta añadir a active_components")
    print("🔍 Verificando por qué no funciona...")
else:
    print("❌ NO añade macro_trajectory a active_components")

# 2. Buscar la clase Macro para arreglar source_ids
macro_class_match = re.search(r'class Macro:.*?(?=\nclass|\Z)', content, re.DOTALL)
if macro_class_match:
    old_class = macro_class_match.group(0)
    
    # Si source_ids se inicializa como set, cambiarlo a lista
    if 'source_ids: List[int]' in old_class or 'self.source_ids = source_ids' in old_class:
        print("✅ Clase Macro encontrada")
        
        # Reemplazar para asegurar que sea lista
        new_class = old_class
        if 'self.source_ids = source_ids' in new_class:
            new_class = new_class.replace(
                'self.source_ids = source_ids',
                'self.source_ids = list(source_ids) if not isinstance(source_ids, list) else source_ids'
            )
            content = content.replace(old_class, new_class)
            print("✅ source_ids convertido a lista en __init__")

# 3. Arreglar create_macro para que REALMENTE añada el componente
# Buscar dónde se crea el macro
lines = old_method.split('\n')
fixed_lines = []
macro_created = False
component_added = False

for i, line in enumerate(lines):
    fixed_lines.append(line)
    
    # Después de crear el macro
    if '_macros[' in line and '=' in line and not macro_created:
        macro_created = True
        # Insertar código para añadir componente a motion_states
        indent = '        '  # 8 espacios
        
        # Ver si ya existe código de añadir componentes
        remaining_lines = '\n'.join(lines[i+1:])
        if 'active_components["macro_trajectory"]' not in remaining_lines:
            print("✅ Insertando código para añadir componente a motion_states")
            fixed_lines.extend([
                '',
                f'{indent}# IMPORTANTE: Añadir trajectory_component a cada fuente',
                f'{indent}if hasattr(macro, "trajectory_component") and macro.trajectory_component:',
                f'{indent}    for sid in macro.source_ids:',
                f'{indent}        if sid in self.motion_states:',
                f'{indent}            self.motion_states[sid].active_components["macro_trajectory"] = macro.trajectory_component',
                f'{indent}            logger.debug(f"macro_trajectory añadido a fuente {{sid}}")',
                ''
            ])
            component_added = True

# Reconstruir método
if component_added:
    new_method = '\n'.join(fixed_lines)
    content = content.replace(old_method, new_method)
    print("✅ create_macro actualizado")

# 4. Añadir método add_source a Macro si no existe
if 'def add_source' not in content:
    print("🔧 Añadiendo método add_source a Macro...")
    
    # Buscar el final de __init__ de Macro
    init_end = content.find('self.created_at = time.time()')
    if init_end != -1:
        insert_pos = content.find('\n', init_end) + 1
        
        add_source_method = '''
    def add_source(self, source_id: int):
        """Añadir una fuente al macro"""
        if hasattr(self, 'source_ids'):
            if isinstance(self.source_ids, set):
                self.source_ids.add(source_id)
            elif isinstance(self.source_ids, list):
                if source_id not in self.source_ids:
                    self.source_ids.append(source_id)
'''
        content = content[:insert_pos] + add_source_method + content[insert_pos:]
        print("✅ Método add_source añadido")

# Guardar cambios
with open(file_path, 'w') as f:
    f.write(content)

print("\n✅ Archivo actualizado")

# Test inmediato
print("\n🧪 TEST INMEDIATO:")
import subprocess
result = subprocess.run(['python', '-c', '''
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
macro_id = engine.create_macro("test", 3)

# Verificar
macro = engine._macros[macro_id]
print(f"✅ Macro creado: {macro_id}")
print(f"✅ source_ids tipo: {type(macro.source_ids)}")
print(f"✅ source_ids: {macro.source_ids}")

# Verificar motion_states
ok = 0
for sid in macro.source_ids:
    if sid in engine.motion_states:
        comps = engine.motion_states[sid].active_components
        if "macro_trajectory" in comps:
            ok += 1

print(f"\\n{'✅' if ok == len(macro.source_ids) else '❌'} {ok}/{len(macro.source_ids)} fuentes con macro_trajectory")

# Test movimiento
def circ(t): return np.array([5*np.cos(t), 5*np.sin(t), 0])
engine.set_macro_trajectory(macro_id, circ)

p0 = engine._positions[list(macro.source_ids)[0]].copy()
for _ in range(60): engine.update()
p1 = engine._positions[list(macro.source_ids)[0]]

dist = np.linalg.norm(p1 - p0)
print(f"\\nMovimiento: {dist:.3f} unidades")
if dist > 0.1:
    print("\\n🎉 ¡MacroTrajectory FUNCIONA!")
'''], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print(f"Error: {result.stderr}")