# === fix_manual_rotation_definitive.py ===
# 🔧 Fix definitivo para rotación manual IS
# ⚡ Corregir center y sincronización

def fix_manual_rotation_definitive():
    """Arreglar definitivamente la rotación manual IS"""
    
    print("🔧 FIX DEFINITIVO: ManualIndividualRotation")
    print("=" * 60)
    
    import os
    engine_file = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    # Leer archivo
    with open(engine_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n1️⃣ Buscando set_manual_individual_rotation...")
    
    # Buscar el método
    in_method = False
    method_start = -1
    indent_level = 0
    
    for i, line in enumerate(lines):
        if 'def set_manual_individual_rotation' in line:
            in_method = True
            method_start = i
            print(f"   Encontrado en línea {i+1}")
            # Detectar nivel de indentación
            indent_level = len(line) - len(line.lstrip())
            continue
            
        if in_method:
            # Si encontramos otra función al mismo nivel, terminamos
            if line.strip() and not line[indent_level:].startswith(' ') and 'def ' in line:
                break
                
            # Buscar donde se crea ManualIndividualRotation
            if 'ManualIndividualRotation(' in line:
                print(f"   Creación en línea {i+1}: {line.strip()}")
                
                # Ver las siguientes líneas para encontrar el center
                for j in range(i, min(i+10, len(lines))):
                    if 'center=' in lines[j]:
                        print(f"   Center en línea {j+1}: {lines[j].strip()}")
                        
                        # Corregir si usa self._positions[source_id]
                        if 'self._positions[source_id]' in lines[j] or 'position' in lines[j]:
                            # Cambiar a None o [0,0,0]
                            lines[j] = lines[j].replace('center=self._positions[source_id]', 'center=None')
                            lines[j] = lines[j].replace('center=position', 'center=None')
                            print(f"   ✅ Corregido a: center=None")
                        break
                        
            # Buscar donde se inicializa current_yaw
            if 'component.current_yaw' in line and 'arctan2' in line:
                print(f"   Current yaw en línea {i+1}: {line.strip()}")
                # Comentar esta línea
                lines[i] = '        # ' + lines[i].lstrip()
                # Añadir línea correcta
                lines.insert(i+1, '        component.current_yaw = 0.0  # Empezar desde 0\n')
                print("   ✅ Corregido current_yaw a 0.0")
                break
    
    # Buscar en motion_components.py también
    print("\n2️⃣ Verificando motion_components.py...")
    
    components_file = os.path.join("trajectory_hub", "core", "motion_components.py")
    with open(components_file, 'r', encoding='utf-8') as f:
        comp_lines = f.readlines()
    
    # Buscar ManualIndividualRotation
    in_class = False
    for i, line in enumerate(comp_lines):
        if 'class ManualIndividualRotation' in line:
            in_class = True
            print(f"   Clase encontrada en línea {i+1}")
            continue
            
        if in_class and line.strip() and not line.startswith(' '):
            # Salimos de la clase
            in_class = False
            
        if in_class:
            # Buscar el método set_target_rotation
            if 'def set_target_rotation' in line:
                print(f"   set_target_rotation en línea {i+1}")
                # Buscar las próximas líneas
                for j in range(i, min(i+20, len(comp_lines))):
                    if 'self.current_yaw = np.arctan2' in comp_lines[j]:
                        print(f"   Current yaw cálculo en línea {j+1}")
                        # Cambiar para usar el ángulo actual de la posición relativa al centro
                        old_line = comp_lines[j]
                        comp_lines[j] = comp_lines[j].replace(
                            'self.current_yaw = np.arctan2(position[1], position[0])',
                            'self.current_yaw = np.arctan2(state.position[1] - self.center[1], state.position[0] - self.center[0])'
                        )
                        if comp_lines[j] != old_line:
                            print("   ✅ Corregido cálculo de current_yaw")
                        break
    
    # Guardar archivos
    print("\n3️⃣ Guardando archivos...")
    
    # Backup
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    shutil.copy(engine_file, f"{engine_file}.backup_{timestamp}")
    shutil.copy(components_file, f"{components_file}.backup_{timestamp}")
    
    # Escribir
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    with open(components_file, 'w', encoding='utf-8') as f:
        f.writelines(comp_lines)
    
    print("\n✅ Archivos actualizados")
    
    # Test final simple
    print("\n4️⃣ Test rápido:")
    test_code = """
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=1, enable_modulator=False)
sid = 0
engine.create_source(sid)
engine._positions[sid] = np.array([3.0, 0.0, 0.0])

# Configurar rotación
engine.set_manual_individual_rotation(sid, yaw=np.pi/2, interpolation_speed=0.9)

# Verificar componente
motion = engine.motion_states[sid]
comp = motion.active_components.get('manual_individual_rotation')
if comp:
    print(f"   Center: {comp.center}")
    print(f"   Current yaw: {comp.current_yaw:.3f}")
    print(f"   Target yaw: {comp.target_yaw:.3f}")
    
    # Sincronizar state
    motion.state.position = engine._positions[sid].copy()
    
    # Test de delta
    for _ in range(10):
        delta = comp.calculate_delta(motion.state, 0, 0.016)
        if delta and np.any(delta.position != 0):
            print(f"   ✅ Delta generado: {delta.position}")
            break
else:
    print("   ❌ No se creó el componente")
"""
    
    try:
        exec(test_code)
    except Exception as e:
        print(f"   ❌ Error en test: {e}")
    
    print("\n📋 Próximo paso: python test_manual_rotation_final.py")

if __name__ == "__main__":
    fix_manual_rotation_definitive()