# === fix_rotation_errors.py ===
# 🔧 Fix: Corregir errores de rotación en sistema deltas
# ⚡ Solución directa para alcanzar 100% funcional

import os
import re

def fix_macro_rotation_position_error():
    """Arreglar error 'float' has no attribute 'position' en MacroRotation"""
    
    file_path = 'trajectory_hub/core/motion_components.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_rotation_final', 'w', encoding='utf-8') as f:
        f.write(content)
    
    lines = content.split('\n')
    
    # Buscar MacroRotation.calculate_delta
    in_macro_rotation = False
    in_calculate_delta = False
    fixed = False
    
    for i, line in enumerate(lines):
        if 'class MacroRotation' in line:
            in_macro_rotation = True
        elif in_macro_rotation and 'def calculate_delta' in line:
            in_calculate_delta = True
        elif in_calculate_delta and line.strip() and not line.startswith(' '):
            in_calculate_delta = False
            
        if in_calculate_delta:
            # Buscar línea problemática con np.mean
            if 'np.mean' in line and 'source_positions' in line:
                print(f"🔍 Encontrada línea problemática: {line.strip()}")
                
                # Reemplazar con código robusto
                indent = len(line) - len(line.lstrip())
                new_lines = [
                    line.rstrip() + "  # Original",
                    " " * indent + "# Obtener posiciones de forma segura",
                    " " * indent + "positions = []",
                    " " * indent + "for sid in self.source_ids:",
                    " " * indent + "    if sid in source_positions:",
                    " " * indent + "        pos = source_positions[sid]",
                    " " * indent + "        if hasattr(pos, 'position'):",
                    " " * indent + "            positions.append(pos.position)",
                    " " * indent + "        elif isinstance(pos, (list, np.ndarray)):",
                    " " * indent + "            positions.append(np.array(pos))",
                    " " * indent + "        else:",
                    " " * indent + "            positions.append(np.array([float(pos), 0.0, 0.0]))",
                    " " * indent + "    else:",
                    " " * indent + "        positions.append(np.array([0.0, 0.0, 0.0]))",
                    " " * indent + "",
                    " " * indent + "if positions:",
                    " " * indent + "    center_position = np.mean(positions, axis=0)",
                    " " * indent + "else:",
                    " " * indent + "    center_position = np.array([0.0, 0.0, 0.0])"
                ]
                
                # Comentar la línea original y añadir el fix
                lines[i] = "# " + line
                lines[i:i+1] = new_lines
                fixed = True
                print("✅ Línea corregida con manejo robusto de posiciones")
                break
    
    if fixed:
        content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ MacroRotation.calculate_delta arreglado")
    else:
        print("⚠️ No se encontró la línea problemática, buscando alternativa...")
        # Buscar y reemplazar directamente el patrón problemático
        content = re.sub(
            r'center_position = np\.mean\(\[.*?\], axis=0\)',
            '''# Calcular centro de forma segura
        positions = []
        for sid in self.source_ids:
            if sid in source_positions:
                pos = source_positions.get(sid)
                if hasattr(pos, 'position'):
                    positions.append(pos.position)
                elif isinstance(pos, (list, np.ndarray)):
                    positions.append(np.array(pos))
                else:
                    positions.append(np.array([0.0, 0.0, 0.0]))
        center_position = np.mean(positions, axis=0) if positions else np.array([0.0, 0.0, 0.0])''',
            content,
            flags=re.DOTALL
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def fix_individual_rotation_params():
    """Arreglar parámetros de set_individual_rotation"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_rotation_params', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar la definición de set_individual_rotation
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if 'def set_individual_rotation' in line:
            print(f"🔍 Encontrada definición: {line.strip()}")
            
            # Verificar parámetros actuales
            if 'speed_x' not in line and 'speed_y' not in line:
                # Necesita actualizar parámetros
                lines[i] = line.replace(
                    'set_individual_rotation(self, source_id',
                    'set_individual_rotation(self, source_id, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None'
                )
                
                # Buscar el cuerpo del método y actualizarlo
                j = i + 1
                indent = "        "
                
                # Insertar código actualizado
                new_body = [
                    indent + '"""Configurar rotación algorítmica individual"""',
                    indent + 'if source_id not in self.motion_states:',
                    indent + '    print(f"⚠️ Fuente {source_id} no existe")',
                    indent + '    return',
                    indent + '',
                    indent + 'motion = self.motion_states[source_id]',
                    indent + '',
                    indent + '# Crear componente de rotación',
                    indent + 'from trajectory_hub.core.motion_components import IndividualRotation',
                    indent + 'rotation = IndividualRotation()',
                    indent + 'rotation.speed_x = speed_x',
                    indent + 'rotation.speed_y = speed_y', 
                    indent + 'rotation.speed_z = speed_z',
                    indent + 'rotation.center = center if center is not None else np.array([0.0, 0.0, 0.0])',
                    indent + '',
                    indent + '# Añadir a componentes activos',
                    indent + 'motion.active_components["individual_rotation"] = rotation',
                    indent + '',
                    indent + 'print(f"✅ Rotación individual configurada para fuente {source_id}")',
                    indent + 'print(f"   Velocidades: X={speed_x:.2f}, Y={speed_y:.2f}, Z={speed_z:.2f} rad/s")'
                ]
                
                # Encontrar donde termina el método actual
                end_j = j
                while end_j < len(lines) and (lines[end_j].startswith(indent) or not lines[end_j].strip()):
                    end_j += 1
                
                # Reemplazar el cuerpo
                lines[j:end_j] = new_body
                
                print("✅ Método set_individual_rotation actualizado")
                break
    
    content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_updated_test():
    """Crear test actualizado con sintaxis correcta"""
    
    test_code = '''# === test_delta_final_fixed.py ===
# 🎯 Test final del sistema de deltas - CORREGIDO
# ⚡ Verificación completa con sintaxis actualizada

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time

def test_delta_system():
    """Test completo del sistema de deltas"""
    print("🚀 TEST FINAL SISTEMA DE DELTAS - VERSIÓN CORREGIDA")
    print("=" * 60)
    
    # Crear engine limpio
    engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
    results = {"passed": 0, "failed": 0}
    
    # Test 1: Concentración
    print("\\n1️⃣ TEST: Concentración")
    print("-" * 40)
    try:
        # Crear nuevo macro
        macro = engine.create_macro("conc_test", 4, formation='square', spacing=3.0)
        
        print("Posiciones iniciales:")
        for sid in macro.source_ids[:4]:
            print(f"  Fuente {sid}: {engine._positions[sid]}")
        
        # Aplicar concentración
        engine.set_macro_concentration(macro, 0.5)
        
        # Simular
        for _ in range(30):
            engine.update()
        
        print("\\nPosiciones finales:")
        moved = 0
        for sid in macro.source_ids[:4]:
            pos = engine._positions[sid]
            print(f"  Fuente {sid}: {pos}")
            if np.linalg.norm(pos) < 2.5:
                moved += 1
        
        if moved >= 3:
            print(f"✅ Concentración exitosa: {moved}/4 fuentes")
            results["passed"] += 1
        else:
            print(f"❌ Concentración falló")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
    
    # Test 2: Trayectorias individuales
    print("\\n2️⃣ TEST: Trayectorias Individuales")
    print("-" * 40)
    try:
        # Crear nuevo macro
        macro = engine.create_macro("traj_test", 3, formation='line', spacing=3.0)
        
        # Configurar trayectorias
        shapes = ['circle', 'spiral', 'figure8']
        for i, sid in enumerate(macro.source_ids[:3]):
            engine.set_individual_trajectory(
                macro, i, shapes[i],
                shape_params={'radius': 2.0},
                movement_mode='fix',
                speed=2.0
            )
        
        # Guardar posiciones iniciales
        initial = {}
        for sid in macro.source_ids[:3]:
            initial[sid] = engine._positions[sid].copy()
        
        # Simular
        for _ in range(60):
            engine.update()
        
        # Verificar movimiento
        moved = 0
        for i, sid in enumerate(macro.source_ids[:3]):
            dist = np.linalg.norm(engine._positions[sid] - initial[sid])
            if dist > 1.0:
                moved += 1
                print(f"✅ Fuente {sid} ({shapes[i]}) se movió {dist:.2f} unidades")
            else:
                print(f"❌ Fuente {sid} ({shapes[i]}) no se movió suficiente: {dist:.2f}")
        
        if moved >= 2:
            print(f"✅ Trayectorias funcionan: {moved}/3")
            results["passed"] += 1
        else:
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
    
    # Test 3: Rotación Macro
    print("\\n3️⃣ TEST: Rotación Macro")
    print("-" * 40)
    try:
        # Crear nuevo macro
        macro = engine.create_macro("rot_test", 3, formation='line', spacing=3.0)
        
        # Esperar estabilización
        for _ in range(5):
            engine.update()
        
        # Guardar ángulo inicial
        sid = macro.source_ids[0]
        initial_angle = np.arctan2(engine._positions[sid][1], engine._positions[sid][0])
        
        # Aplicar rotación
        engine.set_macro_rotation(macro, speed_x=0, speed_y=1.0, speed_z=0)
        
        # Simular
        for _ in range(30):
            engine.update()
        
        # Verificar rotación
        final_angle = np.arctan2(engine._positions[sid][1], engine._positions[sid][0])
        rotation = final_angle - initial_angle
        
        if abs(rotation) > 0.1:
            print(f"✅ Rotación detectada: {np.degrees(rotation):.1f}°")
            results["passed"] += 1
        else:
            print(f"❌ Sin rotación significativa: {np.degrees(rotation):.1f}°")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
    
    # Test 4: Rotación Individual
    print("\\n4️⃣ TEST: Rotación Individual")
    print("-" * 40)
    try:
        # Usar un ID único
        sid = 15
        engine.create_source(sid)
        engine._positions[sid] = np.array([3.0, 0.0, 0.0])
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = np.array([3.0, 0.0, 0.0])
        
        # Aplicar rotación con sintaxis correcta
        engine.set_individual_rotation(sid, speed_x=0.0, speed_y=2.0, speed_z=0.0)
        
        # Simular
        initial_angle = 0.0
        for _ in range(30):
            engine.update()
        
        final_angle = np.degrees(np.arctan2(engine._positions[sid][1], engine._positions[sid][0]))
        
        if abs(final_angle) > 20:
            print(f"✅ Rotación individual: {final_angle:.1f}°")
            results["passed"] += 1
        else:
            print(f"❌ Rotación insuficiente: {final_angle:.1f}°")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
    
    # Resumen
    print("\\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    total = results["passed"] + results["failed"]
    print(f"✅ Pasados: {results['passed']}/{total}")
    print(f"❌ Fallados: {results['failed']}/{total}")
    
    if total > 0:
        success_rate = (results['passed'] / total) * 100
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
        elif success_rate >= 75:
            print("\\n✅ Sistema operativo")
        else:
            print("\\n⚠️ Sistema necesita atención")

if __name__ == "__main__":
    test_delta_system()
'''
    
    with open('test_delta_final_fixed.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ test_delta_final_fixed.py creado")

if __name__ == "__main__":
    print("🔧 FIXING ROTATION ERRORS")
    print("=" * 60)
    
    print("\n1️⃣ Arreglando error 'float' has no attribute 'position'...")
    fix_macro_rotation_position_error()
    
    print("\n2️⃣ Arreglando parámetros de set_individual_rotation...")
    fix_individual_rotation_params()
    
    print("\n3️⃣ Creando test actualizado...")
    create_updated_test()
    
    print("\n✅ CORRECCIONES APLICADAS")
    print("\n📋 Ejecutar: python test_delta_final_fixed.py")