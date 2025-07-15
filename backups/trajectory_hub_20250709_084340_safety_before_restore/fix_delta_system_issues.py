# === fix_delta_system_issues.py ===
# 🔧 Fix: Corregir problemas del sistema de deltas
# ⚡ Solución para subir del 25% al 100%

import os

def fix_macro_methods():
    """Arreglar métodos que esperan nombre de macro en lugar de objeto"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_macro_methods', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Lista de métodos a arreglar
    methods_to_fix = [
        'set_macro_concentration',
        'set_individual_trajectory', 
        'set_macro_rotation',
        'set_macro_trajectory'
    ]
    
    lines = content.split('\n')
    
    for method_name in methods_to_fix:
        print(f"\n🔍 Buscando {method_name}...")
        
        for i, line in enumerate(lines):
            if f'def {method_name}' in line:
                # Buscar las primeras líneas del método
                j = i + 1
                indent = '        '
                
                # Insertar código para manejar tanto string como objeto
                fix_code = [
                    indent + '# Manejar tanto string como objeto macro',
                    indent + 'if hasattr(macro_id, "name"):  # Es un objeto EnhancedMacroSource',
                    indent + '    macro_name = macro_id.name',
                    indent + '    macro = macro_id',
                    indent + 'else:  # Es un string',
                    indent + '    macro_name = macro_id',
                    indent + '    if macro_name not in self._macros:',
                    indent + '        print(f"⚠️ Macro \'{macro_name}\' no encontrado")',
                    indent + '        return',
                    indent + '    macro = self._macros[macro_name]',
                    indent + ''
                ]
                
                # Buscar dónde insertar (después de la docstring si existe)
                insert_pos = j
                while insert_pos < len(lines) and lines[insert_pos].strip().startswith('"""'):
                    insert_pos += 1
                    if lines[insert_pos].strip().endswith('"""'):
                        insert_pos += 1
                        break
                
                # Insertar el fix
                lines[insert_pos:insert_pos] = fix_code
                print(f"✅ {method_name} actualizado para aceptar objetos")
                break
    
    # Guardar
    content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_update_signatures():
    """Arreglar firmas de update() en componentes"""
    
    file_path = 'trajectory_hub/core/motion_components.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_update_fix', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar y verificar métodos update
    lines = content.split('\n')
    components_to_check = [
        'IndividualRotation',
        'ManualIndividualRotation',
        'ConcentrationComponent',
        'IndividualTrajectory'
    ]
    
    current_class = None
    
    for i, line in enumerate(lines):
        # Detectar clase actual
        for comp in components_to_check:
            if f'class {comp}' in line:
                current_class = comp
                print(f"\n🔍 Revisando {comp}...")
        
        # Si estamos en una clase y encontramos update
        if current_class and 'def update' in line and 'def update_' not in line:
            # Verificar parámetros
            if 'state, current_time, dt' in line:
                print(f"✅ {current_class}.update tiene firma correcta")
            else:
                # Corregir firma
                print(f"⚠️ {current_class}.update tiene firma incorrecta: {line.strip()}")
                # Buscar y reemplazar la línea completa
                indent = len(line) - len(line.lstrip())
                lines[i] = ' ' * indent + 'def update(self, state, current_time, dt):'
                print(f"✅ Corregida")
    
    # Guardar
    content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_concentration_application():
    """Arreglar la aplicación de concentración"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar set_macro_concentration y verificar que active la concentración
    lines = content.split('\n')
    
    in_set_concentration = False
    for i, line in enumerate(lines):
        if 'def set_macro_concentration' in line:
            in_set_concentration = True
            print("🔍 Revisando set_macro_concentration...")
        
        if in_set_concentration and 'print(f"Aplicando concentración' in line:
            # Buscar si se activa concentration_active
            j = i + 1
            found_activation = False
            
            while j < len(lines) and lines[j].startswith('        '):
                if 'concentration_active = True' in lines[j]:
                    found_activation = True
                    break
                j += 1
            
            if not found_activation:
                print("⚠️ No se activa concentration_active, añadiendo...")
                # Añadir activación
                indent = '        '
                lines.insert(i + 1, indent + 'macro.concentration_active = True')
                print("✅ Añadida activación")
            
            in_set_concentration = False
    
    # Guardar
    content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_final_test():
    """Test final actualizado"""
    
    test_code = '''# === test_delta_100.py ===
# 🎯 Test final para alcanzar 100% funcionalidad
# ⚡ Con todas las correcciones aplicadas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np

def test_delta_system():
    """Test completo del sistema de deltas"""
    print("🚀 TEST SISTEMA DE DELTAS - OBJETIVO 100%")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0}
    
    # Test 1: Concentración
    print("\\n1️⃣ TEST: Concentración")
    print("-" * 40)
    try:
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        macro = engine.create_macro("test_conc", 4, formation='square', spacing=3.0)
        
        print("Posiciones iniciales:")
        sids = list(macro.source_ids)[:4]
        for sid in sids:
            print(f"  Fuente {sid}: {engine._positions[sid]}")
        
        # Aplicar concentración con objeto macro
        engine.set_macro_concentration(macro, 0.5)
        
        # Simular más frames
        for _ in range(60):  # Más frames para ver movimiento
            engine.update()
        
        print("\\nPosiciones finales:")
        moved = 0
        for sid in sids:
            pos = engine._positions[sid]
            print(f"  Fuente {sid}: {pos}")
            if np.linalg.norm(pos) < 2.0:  # Se acercaron al centro
                moved += 1
        
        if moved >= 3:
            print(f"✅ Concentración exitosa: {moved}/4 fuentes")
            results["passed"] += 1
        else:
            print(f"❌ Concentración no funcionó: solo {moved}/4 se movieron")
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
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        macro = engine.create_macro("test_traj", 3, formation='line', spacing=3.0)
        
        # Configurar con objeto macro
        shapes = ['circle', 'spiral', 'figure8']
        sids = list(macro.source_ids)[:3]
        
        for i, sid in enumerate(sids):
            engine.set_individual_trajectory(
                macro, i, shapes[i],
                shape_params={'radius': 2.0},
                movement_mode='fix',
                speed=2.0
            )
        
        # Guardar posiciones iniciales
        initial = {sid: engine._positions[sid].copy() for sid in sids}
        
        # Simular
        for _ in range(120):  # Más frames
            engine.update()
        
        # Verificar movimiento
        moved = 0
        for i, sid in enumerate(sids):
            dist = np.linalg.norm(engine._positions[sid] - initial[sid])
            if dist > 0.5:
                moved += 1
                print(f"✅ Fuente {sid} ({shapes[i]}) se movió {dist:.2f} unidades")
            else:
                print(f"❌ Fuente {sid} ({shapes[i]}) no se movió: {dist:.2f}")
        
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
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        macro = engine.create_macro("test_rot", 3, formation='line', spacing=3.0)
        
        # Estabilizar
        for _ in range(10):
            engine.update()
        
        # Guardar ángulo inicial
        sid = list(macro.source_ids)[0]
        initial_angle = np.arctan2(engine._positions[sid][1], engine._positions[sid][0])
        
        # Aplicar rotación con objeto macro
        engine.set_macro_rotation(macro, speed_x=0, speed_y=2.0, speed_z=0)
        
        # Simular
        for _ in range(60):
            engine.update()
        
        # Verificar rotación
        final_angle = np.arctan2(engine._positions[sid][1], engine._positions[sid][0])
        rotation = final_angle - initial_angle
        
        if abs(rotation) > 0.5:
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
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        sid = 8
        engine.create_source(sid)
        engine._positions[sid] = np.array([3.0, 0.0, 0.0])
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = np.array([3.0, 0.0, 0.0])
        
        # Aplicar rotación
        engine.set_individual_rotation(sid, speed_x=0.0, speed_y=3.0, speed_z=0.0)
        
        # Simular
        for _ in range(60):
            engine.update()
        
        final_angle = np.degrees(np.arctan2(engine._positions[sid][1], engine._positions[sid][0]))
        
        if abs(final_angle) > 30:
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
    
    with open('test_delta_100.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ test_delta_100.py creado")

if __name__ == "__main__":
    print("🔧 FIXING DELTA SYSTEM ISSUES")
    print("=" * 60)
    
    print("\n1️⃣ Arreglando métodos para aceptar objetos macro...")
    fix_macro_methods()
    
    print("\n2️⃣ Arreglando firmas de update()...")
    fix_update_signatures()
    
    print("\n3️⃣ Verificando aplicación de concentración...")
    fix_concentration_application()
    
    print("\n4️⃣ Creando test final...")
    create_final_test()
    
    print("\n✅ FIXES APLICADOS")
    print("\n📋 Ejecutar: python test_delta_100.py")