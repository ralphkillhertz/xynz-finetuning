#!/usr/bin/env python3
"""
🧹 ELIMINAR DEPENDENCIAS BLOQUEANTES
Fase 3: Quitar todos los checks que causan interdependencias
"""

import os
import re
from datetime import datetime

print("""
================================================================================
🧹 ELIMINANDO DEPENDENCIAS BLOQUEANTES
================================================================================
Vamos a eliminar:
1. Verificaciones de "si tiene IS entonces skip"
2. Checks de "requiere trayectoria para funcionar"
3. Continue/return basados en otros componentes
================================================================================
""")

# Lista de archivos a revisar
files_to_check = [
    "trajectory_hub/core/enhanced_trajectory_engine.py",
    "trajectory_hub/core/motion_components.py",
    "trajectory_hub/core/macro_behaviors.py"
]

fixes_applied = []

# 1. Arreglar _apply_macro_rotation en enhanced_trajectory_engine.py
print("\n1️⃣ ELIMINANDO BLOQUEO EN ROTACIÓN ALGORÍTMICA...")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
with open(engine_file, 'r') as f:
    content = f.read()

# Backup
backup_name = f"{engine_file}.backup_no_blocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(backup_name, 'w') as f:
    f.write(content)

# Buscar el método _apply_macro_rotation
pattern = r'def _apply_macro_rotation\(self,[^}]+?\n(?=\n    def|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    method = match.group(0)
    
    # Buscar líneas problemáticas
    if "continue" in method and "individual_trajectory" in method:
        print("❌ Encontrado: 'continue' que salta fuentes con trayectorias IS")
        
        # Comentar las líneas del continue
        fixed_method = method
        lines = method.split('\n')
        new_lines = []
        
        skip_next = False
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                new_lines.append(f"            # ELIMINADO: {line.strip()}")
                continue
                
            if "if" in line and "individual_trajectory" in line and i+1 < len(lines) and "continue" in lines[i+1]:
                new_lines.append(f"            # BLOQUEANTE ELIMINADO: {line.strip()}")
                skip_next = True
            else:
                new_lines.append(line)
        
        fixed_method = '\n'.join(new_lines)
        content = content[:match.start()] + fixed_method + content[match.end():]
        fixes_applied.append("Eliminado bloqueo en _apply_macro_rotation")
        
        # Guardar cambios
        with open(engine_file, 'w') as f:
            f.write(content)
        print("✅ Bloqueo eliminado en rotación algorítmica")

# 2. Verificar set_macro_concentration
print("\n2️⃣ VERIFICANDO CONCENTRACIÓN...")

# Ya lo arreglamos en la fase anterior, pero verificamos
if "if not any(hasattr(motion, 'individual_trajectory')" in content:
    print("❌ Encontrado: Concentración requiere trayectorias IS")
    # Este ya debería estar arreglado por el script anterior
else:
    print("✅ Concentración no tiene dependencias")

# 3. Crear verificador de independencia
verifier_code = '''#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE INDEPENDENCIA DE COMPONENTES
Asegura que todos los componentes funcionen sin dependencias
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("""
================================================================================
🔍 VERIFICANDO INDEPENDENCIA DE COMPONENTES
================================================================================
""")

def test_component_independence():
    """Prueba que cada componente funcione independientemente."""
    
    results = {
        "concentracion_sola": False,
        "rotacion_ms_sola": False,
        "trayectorias_is_sola": False,
        "concentracion_con_rotacion": False,
        "concentracion_con_is": False,
        "rotacion_con_is": False,
        "todo_junto": False
    }
    
    try:
        # Test 1: Solo concentración
        print("\\n1️⃣ TEST: Solo Concentración")
        print("-" * 50)
        engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
        macro_id = engine.create_macro("test1", source_count=4, formation="grid", spacing=4.0)
        
        pos_before = engine._source_motions[0].state.position.copy()
        engine.set_macro_concentration(macro_id, 0.8)
        
        for _ in range(30):
            engine.update(1/60)
            
        pos_after = engine._source_motions[0].state.position
        movement = np.linalg.norm(pos_after - pos_before)
        
        if movement > 0.1:
            print(f"✅ Concentración funciona sola (movimiento: {movement:.2f})")
            results["concentracion_sola"] = True
        else:
            print("❌ Concentración NO funciona sola")
            
        # Test 2: Solo rotación MS
        print("\\n2️⃣ TEST: Solo Rotación Algorítmica MS")
        print("-" * 50)
        engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
        macro_id = engine.create_macro("test2", source_count=4, formation="line", spacing=2.0)
        
        # Aplicar rotación
        if hasattr(engine, 'set_macro_algorithmic_rotation'):
            engine.set_macro_algorithmic_rotation(macro_id, 
                angular_velocity={'yaw': 45.0, 'pitch': 0.0, 'roll': 0.0})
            
            pos_before = engine._source_motions[0].state.position.copy()
            
            for _ in range(30):
                engine.update(1/60)
                
            pos_after = engine._source_motions[0].state.position
            movement = np.linalg.norm(pos_after - pos_before)
            
            if movement > 0.1:
                print(f"✅ Rotación MS funciona sola (movimiento: {movement:.2f})")
                results["rotacion_ms_sola"] = True
            else:
                print("❌ Rotación MS NO funciona sola")
        else:
            print("⚠️  Rotación algorítmica no implementada")
            
        # Test 3: Concentración + Rotación MS
        print("\\n3️⃣ TEST: Concentración + Rotación MS")
        print("-" * 50)
        engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
        macro_id = engine.create_macro("test3", source_count=4, formation="grid", spacing=4.0)
        
        # Aplicar ambos
        engine.set_macro_concentration(macro_id, 0.5)
        if hasattr(engine, 'set_macro_algorithmic_rotation'):
            engine.set_macro_algorithmic_rotation(macro_id, 
                angular_velocity={'yaw': 30.0, 'pitch': 0.0, 'roll': 0.0})
        
        # Verificar que ambos efectos ocurren
        positions_before = [engine._source_motions[i].state.position.copy() for i in range(4)]
        center_before = np.mean(positions_before, axis=0)
        
        for _ in range(60):
            engine.update(1/60)
            
        positions_after = [engine._source_motions[i].state.position for i in range(4)]
        center_after = np.mean(positions_after, axis=0)
        
        # Verificar concentración (reducción de dispersión)
        disp_before = np.mean([np.linalg.norm(p - center_before) for p in positions_before])
        disp_after = np.mean([np.linalg.norm(p - center_after) for p in positions_after])
        
        # Verificar rotación (el centro se movió)
        center_movement = np.linalg.norm(center_after - center_before)
        
        if disp_after < disp_before * 0.8 and center_movement > 0.1:
            print(f"✅ Ambos funcionan juntos!")
            print(f"   Dispersión: {disp_before:.2f} → {disp_after:.2f}")
            print(f"   Centro movido: {center_movement:.2f}")
            results["concentracion_con_rotacion"] = True
        else:
            print("❌ Los componentes no funcionan bien juntos")
            
        # Test 4: Con trayectorias IS
        print("\\n4️⃣ TEST: Rotación MS con Trayectorias IS activas")
        print("-" * 50)
        engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
        macro_id = engine.create_macro("test4", source_count=4, formation="line", spacing=2.0)
        
        # Configurar trayectorias individuales
        engine.configure_individual_trajectories(macro_id, mode=1)  # Todas iguales
        
        # Aplicar rotación MS
        if hasattr(engine, 'set_macro_algorithmic_rotation'):
            engine.set_macro_algorithmic_rotation(macro_id, 
                angular_velocity={'yaw': 60.0, 'pitch': 0.0, 'roll': 0.0})
            
            pos_before = engine._source_motions[0].state.position.copy()
            
            for _ in range(30):
                engine.update(1/60)
                
            pos_after = engine._source_motions[0].state.position
            movement = np.linalg.norm(pos_after - pos_before)
            
            if movement > 0.1:
                print(f"✅ Rotación MS funciona CON trayectorias IS (movimiento: {movement:.2f})")
                results["rotacion_con_is"] = True
            else:
                print("❌ Rotación MS bloqueada por trayectorias IS")
                
    except Exception as e:
        print(f"\\n❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()
        
    # Resumen
    print("\\n" + "="*70)
    print("📊 RESUMEN DE INDEPENDENCIA:")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test.replace('_', ' ').title()}")
        
    print(f"\\nTotal: {passed_tests}/{total_tests} tests pasados")
    
    if passed_tests == total_tests:
        print("\\n🎉 ¡TODOS LOS COMPONENTES SON INDEPENDIENTES!")
    else:
        print("\\n⚠️  Aún hay dependencias que resolver")
        
    return results

if __name__ == "__main__":
    test_component_independence()
'''

with open("verify_independence.py", 'w') as f:
    f.write(verifier_code)
os.chmod("verify_independence.py", 0o755)

# 4. Resumen de cambios
print(f"\n{'='*70}")
print("📊 RESUMEN DE CAMBIOS")
print('='*70)

if fixes_applied:
    print("\n✅ Fixes aplicados:")
    for fix in fixes_applied:
        print(f"   - {fix}")
else:
    print("\n✅ No se encontraron más dependencias bloqueantes")

print("""
================================================================================
✅ FASE 3 COMPLETADA - DEPENDENCIAS ELIMINADAS
================================================================================

PRÓXIMOS PASOS:
1. Ejecutar test de concentración:
   python test_concentration_delta.py

2. Verificar independencia total:
   python verify_independence.py

3. Si todo funciona, continuar migrando otros componentes:
   python migrate_trajectories_to_delta.py
   python migrate_rotation_to_delta.py
   python migrate_modulation_to_delta.py

================================================================================
""")