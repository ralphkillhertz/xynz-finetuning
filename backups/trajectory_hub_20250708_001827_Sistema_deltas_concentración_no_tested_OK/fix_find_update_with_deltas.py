# === fix_find_update_with_deltas.py ===
# 🔍 Busca dónde está update_with_deltas y lo arregla
# ⚡ También arregla el test

import os
import re
from datetime import datetime

def find_update_with_deltas():
    """Busca update_with_deltas en todos los archivos"""
    
    files_to_check = [
        "trajectory_hub/core/motion_components.py",
        "trajectory_hub/core/enhanced_trajectory_engine.py"
    ]
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        print(f"\n🔍 Buscando en {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar update_with_deltas
        if 'update_with_deltas' in content:
            print(f"✅ Encontrado update_with_deltas en {file_path}")
            
            # Buscar la definición
            pattern = r'def update_with_deltas\(self[^)]*\):(.*?)(?=\n\s{0,8}def|\nclass|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                method_content = match.group(1)
                lines = method_content.split('\n')[:10]
                print("📄 Contenido actual:")
                for line in lines:
                    print(f"  {line}")
                
                # Verificar qué retorna
                if 'return' in method_content:
                    return_match = re.search(r'return\s+(.+)', method_content)
                    if return_match:
                        return_value = return_match.group(1).strip()
                        print(f"\n📌 Retorna: {return_value}")
                        
                        # Si retorna un solo objeto, arreglar para que retorne lista
                        if not return_value.startswith('['):
                            print("⚠️ Retorna un solo objeto, debe retornar lista")
                            fix_return_value(file_path, content)
                            return True
    
    return False

def fix_return_value(file_path, content):
    """Arregla el valor de retorno de update_with_deltas"""
    
    # Backup
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✅ Backup creado: {backup_path}")
    
    # Buscar y reemplazar return
    pattern = r'(def update_with_deltas.*?)(return\s+)([^[\s][^\n]+)'
    
    def replace_return(match):
        prefix = match.group(1)
        return_stmt = match.group(2)
        value = match.group(3)
        
        # Si no es una lista, convertirla
        if not value.strip().startswith('['):
            new_value = f"[{value}] if {value} else []"
            print(f"🔧 Cambiando: return {value}")
            print(f"        Por: return {new_value}")
            return prefix + return_stmt + new_value
        return match.group(0)
    
    new_content = re.sub(pattern, replace_return, content, flags=re.DOTALL)
    
    # Escribir archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Archivo actualizado")

def create_working_test():
    """Crea un test que funcione correctamente"""
    
    test_code = '''# === test_delta_final_working.py ===
# Test final corregido

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent
import numpy as np

print("🚀 TEST FINAL DEL SISTEMA DE DELTAS")
print("="*50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5)
engine.running = True

# Crear fuentes
print("\\n1️⃣ Creando fuentes...")
for i in range(3):
    engine.create_source(i, f"test_{i}")
    print(f"  ✅ Fuente {i} creada")

# Establecer posiciones iniciales
positions_list = [
    np.array([10.0, 0.0, 0.0]),
    np.array([0.0, 10.0, 0.0]),
    np.array([-10.0, 0.0, 0.0])
]

for i, pos in enumerate(positions_list):
    engine._positions[i] = pos.copy()

print("\\n📍 Posiciones iniciales:")
for i in range(3):
    print(f"  Source {i}: {engine._positions[i]}")

# Aplicar concentración
print("\\n2️⃣ Aplicando concentración...")
for i in range(3):
    if i in engine.motion_states:
        motion = engine.motion_states[i]
        comp = ConcentrationComponent()
        comp.enabled = True
        comp.concentration_factor = 0.8
        comp.concentration_center = np.array([0.0, 0.0, 0.0])
        motion.add_component(comp, 'concentration')
        print(f"  ✅ Concentración aplicada a fuente {i}")

# Simular frames
print("\\n3️⃣ Simulando 10 frames...")
for frame in range(10):
    engine.step()
    if frame == 0:
        print(f"  Frame {frame}: {engine._positions[0]}")

print("\\n📍 Posiciones finales:")
for i in range(3):
    print(f"  Source {i}: {engine._positions[i]}")

# Verificar movimiento
moved = False
for i in range(3):
    if not np.array_equal(engine._positions[i], positions_list[i]):
        moved = True
        break

if moved:
    print("\\n✅ ¡ÉXITO! ¡LAS FUENTES SE MOVIERON!")
    print("🎉 EL SISTEMA DE DELTAS FUNCIONA")
else:
    print("\\n❌ Las fuentes NO se movieron")
'''
    
    with open('test_delta_final_working.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test corregido creado: test_delta_final_working.py")

if __name__ == "__main__":
    print("🔧 BUSCANDO Y ARREGLANDO UPDATE_WITH_DELTAS")
    print("="*60)
    
    found = find_update_with_deltas()
    
    if found:
        print("\n✅ update_with_deltas arreglado para retornar lista")
    else:
        print("\n❌ No se encontró update_with_deltas")
    
    create_working_test()
    
    print("\n📋 Ejecuta el test corregido:")
    print("$ python test_delta_final_working.py")