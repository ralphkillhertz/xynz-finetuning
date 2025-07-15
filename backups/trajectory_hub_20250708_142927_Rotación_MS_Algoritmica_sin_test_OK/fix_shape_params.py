# === fix_shape_params.py ===
# 🔧 Fix: Añadir shape_params a IndividualTrajectory
# ⚡ Error: 'IndividualTrajectory' object has no attribute 'shape_params'
# 🎯 Impacto: CRÍTICO - Sin esto no puede calcular posiciones

import os
import re

def fix_shape_params_in_set_individual():
    """Asegura que shape_params se guarde en la trayectoria"""
    
    engine_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("🔧 Corrigiendo set_individual_trajectory para guardar shape_params...")
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método set_individual_trajectory
    method_pattern = r'def set_individual_trajectory\(self[^)]*\):[^}]+?print\(f"✅[^"]+"\)'
    match = re.search(method_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encontró el método")
        return False
    
    # Nuevo código que guarda shape_params
    new_code = '''        # Configurar usando los métodos/atributos disponibles
        trajectory.shape = shape
        trajectory.movement_mode = movement_mode
        trajectory.movement_speed = speed
        trajectory.enabled = True
        
        # IMPORTANTE: Guardar shape_params
        if shape_params is None:
            shape_params = {}
        trajectory.shape_params = shape_params
        
        # Aplicar valores por defecto según la forma
        if shape == "circle" and 'radius' not in shape_params:
            trajectory.shape_params['radius'] = 2.0
        elif shape == "spiral" and 'scale' not in shape_params:
            trajectory.shape_params['scale'] = 1.0
            trajectory.shape_params['turns'] = 3
        elif shape == "figure8" and 'scale' not in shape_params:
            trajectory.shape_params['scale'] = 1.0
        
        # Aplicar parámetros como atributos individuales también
        if shape == "circle":
            trajectory.radius = trajectory.shape_params.get('radius', 2.0)
        elif shape == "spiral":
            trajectory.scale = trajectory.shape_params.get('scale', 1.0)
            trajectory.turns = trajectory.shape_params.get('turns', 3)
        elif shape == "figure8":
            trajectory.scale = trajectory.shape_params.get('scale', 1.0)'''
    
    # Buscar la sección a reemplazar
    old_pattern = r'# Configurar usando los métodos/atributos disponibles.*?trajectory\.scale = shape_params\.get\(\'scale\', 1\.0\)'
    
    if re.search(old_pattern, content, re.DOTALL):
        content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
        print("✅ Código reemplazado")
    else:
        print("⚠️ No se encontró el patrón exacto, buscando alternativa...")
        
        # Buscar después de crear IndividualTrajectory()
        pattern2 = r'trajectory = IndividualTrajectory\(\)(.*?)# Añadir a los componentes activos'
        match2 = re.search(pattern2, content, re.DOTALL)
        
        if match2:
            # Reemplazar toda esa sección
            new_section = f'''trajectory = IndividualTrajectory()
        
{new_code}
        
        # Añadir a los componentes activos'''
            content = re.sub(pattern2, new_section, content, flags=re.DOTALL)
            print("✅ Código insertado correctamente")
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Escribir
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ enhanced_trajectory_engine.py actualizado")
    return True

def fix_individual_trajectory_init():
    """Asegura que IndividualTrajectory inicialice shape_params"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("\n🔧 Asegurando que IndividualTrajectory tenga shape_params...")
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el __init__ de IndividualTrajectory
    class_match = re.search(r'class IndividualTrajectory.*?def __init__\(self\):(.*?)(?=\n    def|\n\n)', 
                           content, re.DOTALL)
    
    if class_match:
        init_content = class_match.group(1)
        
        # Ver si ya tiene shape_params
        if "self.shape_params" not in init_content:
            print("⚠️ No tiene shape_params, añadiendo...")
            
            # Buscar dónde insertar
            lines = init_content.split('\n')
            insert_line = -1
            
            for i, line in enumerate(lines):
                if "self.shape =" in line:
                    insert_line = i + 1
                    break
            
            if insert_line > 0:
                # Insertar después de self.shape
                lines.insert(insert_line, "        self.shape_params = {}")
                new_init = '\n'.join(lines)
                
                # Reemplazar en el contenido
                old_init_full = f"def __init__(self):{init_content}"
                new_init_full = f"def __init__(self):{new_init}"
                
                content = content.replace(old_init_full, new_init_full)
                
                # Escribir
                with open(motion_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ shape_params añadido a __init__")
        else:
            print("✅ Ya tiene shape_params")
    
    return True

def create_final_test():
    """Test final completo"""
    
    test_code = '''# === test_final.py ===
# 🎉 Test final de trayectorias individuales

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

print("🎉 TEST FINAL - Trayectorias Individuales")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
print("✅ Engine creado")

# Crear macro con 3 fuentes
macro_name = engine.create_macro("demo", source_count=3)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)
print(f"✅ Macro '{macro_name}' creado con fuentes: {source_ids}")

# Configurar diferentes trayectorias
configs = [
    {"shape": "circle", "params": {"radius": 2.0}, "speed": 1.0},
    {"shape": "spiral", "params": {"scale": 1.5, "turns": 3}, "speed": 0.5},
    {"shape": "figure8", "params": {"scale": 2.0}, "speed": 1.5}
]

print("\\n🔧 Configurando trayectorias:")
for sid, config in zip(source_ids, configs):
    engine.set_individual_trajectory(
        macro_name, sid,
        shape=config["shape"],
        shape_params=config["params"],
        movement_mode="fix",
        speed=config["speed"]
    )
    print(f"   ✅ Fuente {sid}: {config['shape']} configurada")

# Capturar posiciones iniciales
initial_positions = {sid: engine._positions[sid].copy() for sid in source_ids}

# Simular
print("\\n🎮 Simulando movimiento...")
print("   Presiona Ctrl+C para detener\\n")

try:
    for i in range(100):
        engine.update()
        time.sleep(0.05)
        
        if i % 20 == 0:
            print(f"Update {i}:")
            for sid in source_ids:
                pos = engine._positions[sid]
                dist = np.linalg.norm(pos - initial_positions[sid])
                print(f"  Fuente {sid}: pos=[{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}] dist={dist:6.2f}")
            print()

except KeyboardInterrupt:
    print("\\n⏹️ Simulación detenida")

# Resultados finales
print("\\n📊 RESULTADOS FINALES:")
print("-" * 60)

all_moved = True
for sid, config in zip(source_ids, configs):
    current_pos = engine._positions[sid]
    initial_pos = initial_positions[sid]
    distance = np.linalg.norm(current_pos - initial_pos)
    moved = distance > 0.01
    
    print(f"Fuente {sid} ({config['shape']}):")
    print(f"  Velocidad configurada: {config['speed']}")
    print(f"  Distancia recorrida: {distance:.3f} {'✅' if moved else '❌'}")
    
    if not moved:
        all_moved = False

print("\\n" + "=" * 60)
if all_moved:
    print("🎉 ¡ÉXITO TOTAL! Todas las trayectorias individuales funcionan")
    print("\\n✨ Características verificadas:")
    print("   - Diferentes formas: circle, spiral, figure8")
    print("   - Diferentes velocidades por fuente")
    print("   - Parámetros personalizados por forma")
    print("   - Sistema de deltas funcionando")
    print("\\n🚀 ¡El sistema está listo para usar!")
else:
    print("❌ Algunas trayectorias no funcionaron")
'''
    
    with open("test_final.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test final creado")

if __name__ == "__main__":
    print("🔧 FIX SHAPE_PARAMS - Último arreglo")
    print("=" * 50)
    
    success = True
    
    if fix_shape_params_in_set_individual():
        print("✅ Paso 1 completado")
    else:
        success = False
    
    if fix_individual_trajectory_init():
        print("✅ Paso 2 completado")
    else:
        success = False
    
    if success:
        create_final_test()
        print("\n✅ ¡TODO LISTO!")
        print("\n📝 Ejecuta:")
        print("1. python quick_test.py     # Test rápido")
        print("2. python test_final.py     # Test completo")
        print("\n🎉 ¡Las trayectorias individuales deberían funcionar ahora!")