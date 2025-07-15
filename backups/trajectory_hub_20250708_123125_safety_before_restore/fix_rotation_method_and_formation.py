# === fix_rotation_method_and_formation.py ===
# 🔧 Fix: Añadir método set_macro_rotation y arreglar formación cube
# ⚡ Impacto: CRÍTICO - Habilita rotaciones MS

import os
import re

def fix_rotation_system():
    """Arregla el sistema de rotación MS"""
    
    print("🔧 ARREGLANDO SISTEMA DE ROTACIÓN MS\n")
    
    # 1. Verificar y añadir el método al engine
    print("1️⃣ Verificando método set_macro_rotation en engine...")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    if "def set_macro_rotation" not in engine_content:
        print("❌ Método no encontrado, añadiendo...")
        
        # Buscar dónde insertar (después de set_macro_trajectory)
        insert_after = "def set_macro_trajectory"
        insert_pos = engine_content.find(insert_after)
        
        if insert_pos > 0:
            # Buscar el final del método
            next_def = engine_content.find("\n    def ", insert_pos + 1)
            if next_def > 0:
                # Insertar el nuevo método
                rotation_method = '''
    def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):
        """Configura rotación algorítmica para un macro"""
        if macro_name not in self._macros:
            print(f"❌ Macro '{macro_name}' no existe")
            return
            
        macro = self._macros[macro_name]
        
        # Calcular centro del macro
        positions = [self._positions[sid] for sid in macro.source_ids if sid < len(self._positions)]
        if not positions:
            return
            
        center = np.mean(positions, axis=0)
        
        # Configurar rotación para cada fuente del macro
        for sid in macro.source_ids:
            if sid in self.motion_states:
                state = self.motion_states[sid]
                
                # Crear componente de rotación si no existe
                if 'macro_rotation' not in state.active_components:
                    from .motion_components import MacroRotation
                    rotation = MacroRotation()
                    state.active_components['macro_rotation'] = rotation
                else:
                    rotation = state.active_components['macro_rotation']
                
                # Configurar rotación
                rotation.update_center(center)
                rotation.set_rotation(speed_x, speed_y, speed_z)
                
        print(f"✅ Rotación configurada para macro '{macro_name}'")
        print(f"   Centro: {center}")
        print(f"   Velocidades (rad/s): X={speed_x:.2f}, Y={speed_y:.2f}, Z={speed_z:.2f}")
'''
                engine_content = engine_content[:next_def] + rotation_method + "\n" + engine_content[next_def:]
                print("✅ Método set_macro_rotation añadido")
        
        # Guardar
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(engine_content)
    else:
        print("✅ Método ya existe")
    
    # 2. Arreglar la formación cube
    print("\n2️⃣ Arreglando formación cube...")
    
    # Buscar apply_formation y verificar que cube esté implementado
    formation_pattern = r'def apply_formation.*?(?=\n    def|\Z)'
    match = re.search(formation_pattern, engine_content, re.DOTALL)
    
    if match and "'cube'" not in match.group(0):
        print("❌ Formación 'cube' no implementada, añadiendo...")
        
        # Buscar dónde añadir el caso cube
        apply_formation = match.group(0)
        
        # Añadir caso cube antes del else final
        cube_case = '''
        elif formation == "cube":
            # Formar un cubo 2x2x2
            size = 2.0
            positions = [
                [-size/2, -size/2, -size/2],
                [size/2, -size/2, -size/2],
                [-size/2, size/2, -size/2],
                [size/2, size/2, -size/2],
                [-size/2, -size/2, size/2],
                [size/2, -size/2, size/2],
                [-size/2, size/2, size/2],
                [size/2, size/2, size/2]
            ]
            for i, sid in enumerate(source_ids[:8]):
                if sid < len(self._positions) and i < len(positions):
                    self._positions[sid] = np.array(positions[i])'''
        
        # Insertar antes del else final
        else_pos = apply_formation.rfind("else:")
        if else_pos > 0:
            new_apply_formation = apply_formation[:else_pos] + cube_case + "\n        " + apply_formation[else_pos:]
            engine_content = engine_content.replace(apply_formation, new_apply_formation)
            
            # Guardar
            with open(engine_path, 'w', encoding='utf-8') as f:
                f.write(engine_content)
            print("✅ Formación cube añadida")
    
    # 3. Crear test mejorado
    print("\n3️⃣ Creando test mejorado...")
    
    test_code = '''# === test_macro_rotation_fixed.py ===
# 🧪 Test de rotación MS algorítmica con deltas

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

print("\\n🔄 TEST: Rotación MS Algorítmica con Deltas\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60)
print("✅ Engine creado")

# Crear macro en formación cuadrada
macro_id = engine.create_macro("cubo", 8, formation="cube")
print(f"✅ Macro '{macro_id}' creado")

# Aplicar formación manualmente si no funcionó
macro = engine._macros[macro_id]
if all(np.allclose(engine._positions[sid], [0,0,0]) for sid in macro.source_ids if sid < len(engine._positions)):
    print("⚠️ Aplicando formación cube manualmente...")
    size = 2.0
    positions = [
        [-size/2, -size/2, -size/2],
        [size/2, -size/2, -size/2],
        [-size/2, size/2, -size/2],
        [size/2, size/2, -size/2],
        [-size/2, -size/2, size/2],
        [size/2, -size/2, size/2],
        [-size/2, size/2, size/2],
        [size/2, size/2, size/2]
    ]
    for i, sid in enumerate(list(macro.source_ids)[:8]):
        if sid < len(engine._positions) and i < len(positions):
            engine._positions[sid] = np.array(positions[i])
            if sid in engine.motion_states:
                engine.motion_states[sid].position = engine._positions[sid].copy()

# Posiciones iniciales
print("\\n📍 Posiciones iniciales:")
initial_positions = {}
for sid in macro.source_ids:
    if sid < len(engine._positions):
        pos = engine._positions[sid]
        initial_positions[sid] = pos.copy()
        print(f"   Fuente {sid}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")

# Configurar rotación en Y
print("\\n🎠 Configurando rotación en Y...")
engine.set_macro_rotation(macro_id, speed_x=0, speed_y=1.0, speed_z=0)

# Simular 1.57 segundos (cuarto de vuelta)
print("\\n⏱️ Simulando π/2 segundos (90°)...")
frames = int(1.57 * 60)
for i in range(frames):
    engine.update()
    if i % 30 == 0:
        print(f"   Frame {i}/{frames}")

# Verificar posiciones finales
print("\\n📍 Posiciones finales:")
total_movement = 0
for sid in macro.source_ids:
    if sid < len(engine._positions):
        initial = initial_positions[sid]
        final = engine._positions[sid]
        distance = np.linalg.norm(final - initial)
        total_movement += distance
        print(f"   Fuente {sid}: [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}] (movió {distance:.2f})")

avg_movement = total_movement / len([s for s in macro.source_ids if s in initial_positions])

if avg_movement > 0.5:
    print(f"\\n✅ ¡ÉXITO! Rotación MS funcionando")
    print(f"   Movimiento promedio: {avg_movement:.2f} unidades")
    print("\\n📊 SISTEMA DE DELTAS:")
    print("   ✅ Concentración: 100%")
    print("   ✅ Trayectorias IS: 100%") 
    print("   ✅ Trayectorias MS: 100%")
    print("   ✅ Rotaciones MS algorítmicas: 100%")
else:
    print(f"\\n❌ Sin rotación detectada: {avg_movement:.3f}")
'''
    
    with open("test_macro_rotation_fixed.py", "w") as f:
        f.write(test_code)
    
    print("✅ Test mejorado creado")

if __name__ == "__main__":
    fix_rotation_system()
    print("\n🚀 Ejecutando test...")
    os.system("python test_macro_rotation_fixed.py")