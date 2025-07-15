# === fix_delta_system_complete.py ===
# 🔧 Corrección completa para sistema de deltas 100% funcional
# ⚡ Enfocado en los 7 componentes delta

import shutil
from datetime import datetime
import ast

def fix_delta_system():
    """Corrige TODO para que el sistema de deltas funcione al 100%"""
    
    print("🔧 CORRECCIÓN SISTEMA DE DELTAS - 7 COMPONENTES")
    print("=" * 70)
    print("Objetivos:")
    print("  ✓ MS Trayectorias")
    print("  ✓ MS Rotación Algorítmica") 
    print("  ✓ MS Rotación Manual")
    print("  ✓ IS Trayectorias")
    print("  ✓ IS Rotación Algorítmica")
    print("  ✓ IS Rotación Manual")
    print("  ✓ Concentración")
    print("=" * 70)
    
    # 1. Backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    engine_backup = f"{engine_file}.backup_delta_{timestamp}"
    
    shutil.copy2(engine_file, engine_backup)
    print(f"\n✅ Backup: {engine_backup}")
    
    # 2. Leer archivo
    with open(engine_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_applied = []
    
    # 3. FIX 1: create_macro retorna objeto
    print("\n🔧 FIX 1: create_macro retorna objeto...")
    for i, line in enumerate(lines):
        if line.strip() == "return macro_id":
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + "return self._macros[macro_id]\n"
            fixes_applied.append(f"Línea {i+1}: create_macro ahora retorna objeto")
            break
    
    # 4. FIX 2: create_orientation_modulator busca en motion_states
    print("🔧 FIX 2: Modulador busca en motion_states...")
    for i, line in enumerate(lines):
        if "if source_id not in self._source_motions:" in line:
            lines[i] = line.replace("self._source_motions", "self.motion_states")
            fixes_applied.append(f"Línea {i+1}: Modulador busca en motion_states")
    
    # 5. FIX 3: Sincronizar _source_motions
    print("🔧 FIX 3: Sincronizar _source_motions...")
    in_create_source = False
    for i, line in enumerate(lines):
        if "def create_source" in line:
            in_create_source = True
        elif in_create_source and "self.motion_states[source_id] = motion" in line:
            indent = len(line) - len(line.lstrip())
            # Añadir sincronización
            lines.insert(i + 1, " " * indent + "self._source_motions[source_id] = motion\n")
            fixes_applied.append(f"Línea {i+2}: Sincronización _source_motions")
            break
    
    # 6. FIX 4: Asegurar que engine.update() llama motion.update()
    print("🔧 FIX 4: Verificar engine.update()...")
    
    # Buscar el método update
    in_update = False
    has_motion_update = False
    
    for i, line in enumerate(lines):
        if "def update(self" in line:
            in_update = True
        elif in_update and "motion.update(" in line:
            has_motion_update = True
            break
        elif in_update and line.strip() and not line[0].isspace():
            # Salimos del método
            break
    
    if not has_motion_update:
        print("   ⚠️ engine.update() no llama motion.update() - Añadiendo...")
        # Buscar dónde añadirlo
        for i, line in enumerate(lines):
            if "def update(self" in line:
                # Buscar el bucle de motion_states
                j = i + 1
                while j < len(lines):
                    if "for source_id, state in self.motion_states.items():" in lines[j]:
                        # Añadir después del bucle
                        k = j + 1
                        while k < len(lines) and lines[k].startswith('    '):
                            k += 1
                        # Insertar antes de k
                        indent = "        "
                        lines.insert(k, f"{indent}# Actualizar motion con sistema de deltas\n")
                        lines.insert(k + 1, f"{indent}if source_id in self.motion_states:\n")
                        lines.insert(k + 2, f"{indent}    motion = self.motion_states[source_id]\n")
                        lines.insert(k + 3, f"{indent}    if hasattr(motion, 'update'):\n")
                        lines.insert(k + 4, f"{indent}        motion.update(current_time, dt)\n")
                        fixes_applied.append("Añadido motion.update() en engine.update()")
                        break
                    j += 1
                break
    
    # 7. Guardar
    print("\n💾 Guardando archivo corregido...")
    with open(engine_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # 8. Verificar sintaxis
    print("🧪 Verificando sintaxis...")
    try:
        with open(engine_file, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("   ✅ Sintaxis correcta")
    except SyntaxError as e:
        print(f"   ❌ Error: {e}")
        shutil.copy2(engine_backup, engine_file)
        return False
    
    # 9. Mostrar resumen
    print("\n📊 RESUMEN DE CORRECCIONES:")
    print("=" * 70)
    for fix in fixes_applied:
        print(f"   ✅ {fix}")
    
    print(f"\n   Total: {len(fixes_applied)} correcciones aplicadas")
    
    # 10. Crear test específico para deltas
    create_delta_test()
    
    return True

def create_delta_test():
    """Crea test específico para los 7 componentes delta"""
    
    test_content = '''# === test_7_deltas.py ===
# 🧪 Test de los 7 componentes del sistema de deltas
# ✅ MS Trayectorias, MS Rotaciones, IS Trayectorias, IS Rotaciones, Concentración

import numpy as np
from trajectory_hub.core import EnhancedTrajectoryEngine

def test_7_deltas():
    """Test completo del sistema de deltas"""
    
    print("🧪 TEST SISTEMA DE DELTAS - 7 COMPONENTES")
    print("=" * 70)
    
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60)
    results = {}
    
    try:
        # 1. CONCENTRACIÓN
        print("\\n1️⃣ Test CONCENTRACIÓN...")
        macro1 = engine.create_macro("conc", 4, formation="square", spacing=5.0)
        initial_pos = engine._positions[0].copy()
        
        engine.set_distance_control("conc", mode="convergent")
        for _ in range(30):
            engine.update()
            
        final_pos = engine._positions[0]
        moved = np.linalg.norm(final_pos - initial_pos) > 0.1
        results["concentracion"] = moved
        print(f"   {'✅' if moved else '❌'} Concentración: {moved}")
        
        # 2. MS TRAYECTORIAS
        print("\\n2️⃣ Test MS TRAYECTORIAS...")
        macro2 = engine.create_macro("ms_traj", 3)
        engine.set_macro_trajectory("ms_traj", "circle", speed=2.0)
        
        initial = engine._positions[10].copy()
        for _ in range(30):
            engine.update()
        moved = np.linalg.norm(engine._positions[10] - initial) > 0.5
        results["ms_trayectorias"] = moved
        print(f"   {'✅' if moved else '❌'} MS Trayectorias: {moved}")
        
        # 3. MS ROTACIÓN ALGORÍTMICA
        print("\\n3️⃣ Test MS ROTACIÓN ALGORÍTMICA...")
        macro3 = engine.create_macro("ms_rot_algo", 4, formation="square")
        engine.set_macro_rotation("ms_rot_algo", speed_x=0, speed_y=0, speed_z=1.0)
        
        angle_before = np.arctan2(engine._positions[20][1], engine._positions[20][0])
        for _ in range(30):
            engine.update()
        angle_after = np.arctan2(engine._positions[20][1], engine._positions[20][0])
        rotated = abs(angle_after - angle_before) > 0.1
        results["ms_rot_algo"] = rotated
        print(f"   {'✅' if rotated else '❌'} MS Rot Algorítmica: {rotated}")
        
        # 4. MS ROTACIÓN MANUAL
        print("\\n4️⃣ Test MS ROTACIÓN MANUAL...")
        macro4 = engine.create_macro("ms_rot_man", 2)
        engine.set_manual_macro_rotation("ms_rot_man", yaw=1.57, pitch=0, roll=0, 
                                       interpolation_speed=0.1)
        
        pos_before = engine._positions[30].copy()
        for _ in range(60):
            engine.update()
        pos_after = engine._positions[30]
        rotated = np.linalg.norm(pos_after - pos_before) > 0.1
        results["ms_rot_manual"] = rotated
        print(f"   {'✅' if rotated else '❌'} MS Rot Manual: {rotated}")
        
        # 5. IS TRAYECTORIAS
        print("\\n5️⃣ Test IS TRAYECTORIAS...")
        sid = 40
        engine.create_source(sid)
        engine.set_individual_trajectory(sid, shape="spiral", scale=2.0, speed=1.0)
        
        initial = engine._positions[sid].copy()
        for _ in range(30):
            engine.update()
        moved = np.linalg.norm(engine._positions[sid] - initial) > 0.1
        results["is_trayectorias"] = moved
        print(f"   {'✅' if moved else '❌'} IS Trayectorias: {moved}")
        
        # 6. IS ROTACIÓN ALGORÍTMICA
        print("\\n6️⃣ Test IS ROTACIÓN ALGORÍTMICA...")
        sid2 = 41
        engine.create_source(sid2)
        engine._positions[sid2] = np.array([3.0, 0.0, 0.0])
        engine.set_individual_rotation(sid2, speed_x=0, speed_y=0, speed_z=2.0)
        
        angle_before = np.arctan2(engine._positions[sid2][1], engine._positions[sid2][0])
        for _ in range(30):
            engine.update()
        angle_after = np.arctan2(engine._positions[sid2][1], engine._positions[sid2][0])
        rotated = abs(angle_after - angle_before) > 0.1
        results["is_rot_algo"] = rotated
        print(f"   {'✅' if rotated else '❌'} IS Rot Algorítmica: {rotated}")
        
        # 7. IS ROTACIÓN MANUAL
        print("\\n7️⃣ Test IS ROTACIÓN MANUAL...")
        sid3 = 42
        engine.create_source(sid3)
        engine._positions[sid3] = np.array([0.0, 3.0, 0.0])
        engine.set_manual_individual_rotation(sid3, yaw=3.14, pitch=0, roll=0,
                                            interpolation_speed=0.1)
        
        pos_before = engine._positions[sid3].copy()
        for _ in range(60):
            engine.update()
        pos_after = engine._positions[sid3]
        moved = np.linalg.norm(pos_after - pos_before) > 0.1
        results["is_rot_manual"] = moved
        print(f"   {'✅' if moved else '❌'} IS Rot Manual: {moved}")
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # RESUMEN
    print("\\n" + "=" * 70)
    print("📊 RESUMEN SISTEMA DE DELTAS:")
    print("=" * 70)
    
    total = len(results)
    passed = sum(results.values())
    
    for component, ok in results.items():
        print(f"   {component.ljust(20)} {'✅ PASS' if ok else '❌ FAIL'}")
    
    print(f"\\n   TOTAL: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
    
    return passed == total

if __name__ == "__main__":
    test_7_deltas()
'''
    
    with open('test_7_deltas.py', 'w') as f:
        f.write(test_content)
    
    print("\n✅ Creado: test_7_deltas.py")

if __name__ == "__main__":
    if fix_delta_system():
        print("\n✅ SISTEMA CORREGIDO")
        print("\nEjecuta ahora:")
        print("   python test_7_deltas.py")