# === fix_delta_issues.py ===
# 🔧 Fix: Corregir concentración y rotación macro
# ⚡ Solución directa para sistema deltas 100%

import os
import re

def fix_concentration_issue():
    """Arreglar concentración cuando las fuentes están en origen"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_concentration_fix', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar create_macro y asegurar que las formaciones no dejen todo en 0,0,0
    # Añadir spacing por defecto si no existe
    formation_fix = '''
        # Calcular posiciones según formación
        positions = []
        
        if formation == 'circle':
            for i in range(source_count):
                angle = (i / source_count) * 2 * np.pi
                x = spacing * np.cos(angle)
                y = spacing * np.sin(angle)
                positions.append(np.array([x, y, 0.0]))
                
        elif formation == 'line':
            for i in range(source_count):
                x = (i - source_count/2) * spacing
                positions.append(np.array([x, 0.0, 0.0]))
                
        elif formation == 'grid':
            cols = int(np.ceil(np.sqrt(source_count)))
            for i in range(source_count):
                row = i // cols
                col = i % cols
                x = (col - cols/2) * spacing
                y = (row - cols/2) * spacing
                positions.append(np.array([x, y, 0.0]))
                
        elif formation == 'square':
            # Cuadrado - distribuir en los bordes
            side_length = int(np.ceil(source_count / 4))
            for i in range(source_count):
                if i < side_length:  # Lado superior
                    x = (i - side_length/2) * spacing
                    y = spacing * side_length/2
                elif i < 2 * side_length:  # Lado derecho
                    x = spacing * side_length/2
                    y = (side_length/2 - (i - side_length)) * spacing
                elif i < 3 * side_length:  # Lado inferior
                    x = (side_length/2 - (i - 2*side_length)) * spacing
                    y = -spacing * side_length/2
                else:  # Lado izquierdo
                    x = -spacing * side_length/2
                    y = ((i - 3*side_length) - side_length/2) * spacing
                positions.append(np.array([x, y, 0.0]))
                
        else:  # Default o formaciones no implementadas
            # Círculo por defecto
            for i in range(source_count):
                angle = (i / source_count) * 2 * np.pi
                x = spacing * np.cos(angle)
                y = spacing * np.sin(angle)
                positions.append(np.array([x, y, 0.0]))
        
        # Aplicar posiciones a las fuentes
        for i, (sid, pos) in enumerate(zip(source_ids, positions)):
            self._positions[sid] = pos
            if sid in self.motion_states:
                self.motion_states[sid].state.position = pos.copy()
    '''
    
    # Buscar donde se crean las formaciones y reemplazar
    pattern = r'# Aplicar formación inicial.*?(?=\n\s{8}# |\n\s{8}return)'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, formation_fix.strip(), content, flags=re.DOTALL)
        print("✅ Formaciones corregidas para evitar todas las fuentes en 0,0,0")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_rotation_macro_error():
    """Arreglar error 'float' has no attribute 'position'"""
    
    file_path = 'trajectory_hub/core/motion_components.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_rotation_fix', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # El error viene de MacroRotation.calculate_delta
    # Buscar la línea problemática
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Buscar líneas que puedan tener el problema
        if 'center_position = np.mean' in line and 'position' in line:
            # Esta línea probablemente está intentando .position en elementos float
            print(f"🔍 Encontrada línea problemática {i+1}: {line.strip()}")
            
            # La línea probablemente es algo como:
            # center_position = np.mean([s.position for s in source_positions], axis=0)
            # Pero source_positions podría contener floats o arrays
            
            # Corregir para manejar ambos casos
            if '[s.position for s in' in line:
                lines[i] = line.replace(
                    '[s.position for s in source_positions]',
                    '[s if isinstance(s, np.ndarray) else getattr(s, "position", s) for s in source_positions]'
                )
                print(f"✅ Línea {i+1} corregida")
    
    # Buscar específicamente en MacroRotation.calculate_delta
    in_macro_rotation = False
    in_calculate_delta = False
    
    for i, line in enumerate(lines):
        if 'class MacroRotation' in line:
            in_macro_rotation = True
        elif in_macro_rotation and 'def calculate_delta' in line:
            in_calculate_delta = True
        elif in_calculate_delta and 'def ' in line and 'calculate_delta' not in line:
            in_calculate_delta = False
            
        if in_calculate_delta:
            # Buscar accesos a .position que puedan fallar
            if '.position' in line and 'state.position' not in line:
                # Verificar si necesita protección
                if 'for' in line and 'in' in line:
                    # Es un list comprehension
                    original = line
                    # Proteger el acceso
                    line = line.replace('.position', ' if hasattr(p, "position") else p')
                    if line != original:
                        lines[i] = line
                        print(f"✅ Protegido acceso a position en línea {i+1}")
    
    # Guardar
    content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def create_final_test():
    """Crear test final del sistema"""
    
    test_code = '''# === test_delta_system_final.py ===
# 🎯 Test final del sistema de deltas
# ⚡ Verificación completa de funcionalidad

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time

def test_delta_system():
    """Test completo del sistema de deltas"""
    print("🚀 TEST FINAL SISTEMA DE DELTAS")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
    results = {"passed": 0, "failed": 0}
    
    # Test 1: Concentración con formación adecuada
    print("\\n1️⃣ TEST: Concentración")
    print("-" * 40)
    try:
        # Crear macro con spacing adecuado
        macro = engine.create_macro("test_conc", 4, formation='square', spacing=3.0)
        
        # Verificar posiciones iniciales
        print("Posiciones iniciales:")
        for i in range(4):
            print(f"  Fuente {i}: {engine._positions[i]}")
        
        # Aplicar concentración
        engine.set_macro_concentration(macro, 0.5)
        
        # Simular
        for _ in range(30):
            engine.update()
        
        # Verificar
        print("\\nPosiciones finales:")
        moved = 0
        for i in range(4):
            pos = engine._positions[i]
            print(f"  Fuente {i}: {pos}")
            if np.linalg.norm(pos) < 2.5:  # Se acercaron al centro
                moved += 1
        
        if moved >= 3:
            print(f"✅ Concentración exitosa: {moved}/4 fuentes")
            results["passed"] += 1
        else:
            print(f"❌ Concentración falló")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        results["failed"] += 1
    
    # Test 2: Trayectorias individuales
    print("\\n2️⃣ TEST: Trayectorias Individuales")
    print("-" * 40)
    try:
        macro = engine.create_macro("test_traj", 3, formation='line', spacing=3.0)
        
        # Configurar trayectorias
        for i in range(3):
            shape = ['circle', 'spiral', 'figure8'][i]
            engine.set_individual_trajectory(
                macro, i, shape,
                shape_params={'radius': 2.0},
                movement_mode='fix',
                speed=2.0
            )
        
        # Simular
        initial = [engine._positions[i].copy() for i in range(3)]
        
        for _ in range(60):
            engine.update()
        
        # Verificar movimiento
        moved = 0
        for i in range(3):
            dist = np.linalg.norm(engine._positions[i] - initial[i])
            if dist > 1.0:
                moved += 1
                print(f"✅ Fuente {i} se movió {dist:.2f} unidades")
        
        if moved >= 2:
            print(f"✅ Trayectorias funcionan: {moved}/3")
            results["passed"] += 1
        else:
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        results["failed"] += 1
    
    # Test 3: Rotación Macro
    print("\\n3️⃣ TEST: Rotación Macro")
    print("-" * 40)
    try:
        macro = engine.create_macro("test_rot", 3, formation='line', spacing=3.0)
        
        # Estabilizar
        for _ in range(5):
            engine.update()
        
        # Aplicar rotación
        engine.set_macro_rotation(macro, speed_x=0, speed_y=1.0, speed_z=0)
        
        # Simular
        initial_angle = np.arctan2(engine._positions[0][1], engine._positions[0][0])
        
        for _ in range(30):
            engine.update()
        
        final_angle = np.arctan2(engine._positions[0][1], engine._positions[0][0])
        rotation = final_angle - initial_angle
        
        if abs(rotation) > 0.1:
            print(f"✅ Rotación detectada: {np.degrees(rotation):.1f}°")
            results["passed"] += 1
        else:
            print(f"❌ Sin rotación significativa")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        results["failed"] += 1
    
    # Test 4: Rotación Individual
    print("\\n4️⃣ TEST: Rotación Individual")
    print("-" * 40)
    try:
        # Crear fuente individual
        sid = 10
        engine.create_source(sid)
        engine._positions[sid] = np.array([3.0, 0.0, 0.0])
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = np.array([3.0, 0.0, 0.0])
        
        # Aplicar rotación
        engine.set_individual_rotation(sid, speed_y=2.0)
        
        # Simular
        for _ in range(30):
            engine.update()
        
        angle = np.degrees(np.arctan2(engine._positions[sid][1], engine._positions[sid][0]))
        
        if abs(angle) > 20:
            print(f"✅ Rotación individual: {angle:.1f}°")
            results["passed"] += 1
        else:
            print(f"❌ Rotación insuficiente")
            results["failed"] += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
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
    
    with open('test_delta_system_final.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ test_delta_system_final.py creado")

if __name__ == "__main__":
    print("🔧 FIXING DELTA SYSTEM ISSUES")
    print("=" * 60)
    
    print("\n1️⃣ Arreglando concentración...")
    fix_concentration_issue()
    
    print("\n2️⃣ Arreglando rotación macro...")
    fix_rotation_macro_error()
    
    print("\n3️⃣ Creando test final...")
    create_final_test()
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python test_delta_system_final.py")
    print("2. Si todo pasa → Sistema deltas 100% funcional")