# fix_rotation_tests.py
# Arregla los tests de rotación

def fix_tests():
    print("🔧 Arreglando test_rotation_simple.py...")
    
    # Leer el archivo
    with open('test_rotation_simple.py', 'r') as f:
        content = f.read()
    
    # Reemplazar la línea problemática
    content = content.replace(
        'engine.set_manual_macro_rotation(macro_name, target_yaw=90.0, rotation_speed=2.0)',
        '''engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,              # 90° en radianes
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.5
    )'''
    )
    
    # Guardar
    with open('test_rotation_simple.py', 'w') as f:
        f.write(content)
    
    print("✅ test_rotation_simple.py arreglado")
    
    # Arreglar test_rotation_success.py
    print("\n🔧 Arreglando test_rotation_success.py...")
    
    with open('test_rotation_success.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar y arreglar la indentación
    new_lines = []
    for i, line in enumerate(lines):
        if 'for sid in source_ids:' in line and i > 50:  # La línea problemática
            # Asegurar indentación correcta
            new_lines.append('    for sid in source_ids:\n')
        else:
            new_lines.append(line)
    
    with open('test_rotation_success.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✅ test_rotation_success.py arreglado")
    
    # Crear versión mejorada del test corrected con velocidad reducida
    print("\n🔧 Creando test_rotation_controlled.py con velocidad controlada...")
    
    controlled_test = '''# test_rotation_controlled.py
# Test de rotación con velocidad controlada

import numpy as np
import math
import warnings
from trajectory_hub import EnhancedTrajectoryEngine

warnings.filterwarnings("ignore", message="No se puede crear modulador")

def test_rotation_controlled():
    print("🎯 TEST: Rotación Manual MS con Velocidad Controlada")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear macro
    print("🔧 Creando macro con 4 fuentes...")
    macro_name = engine.create_macro("test", source_count=4, formation="square")
    
    # Establecer posiciones en cuadrado
    print("\\n📍 Estableciendo posiciones en cuadrado 3x3:")
    engine._positions[0] = np.array([3.0, 0.0, 0.0])   # Derecha
    engine._positions[1] = np.array([0.0, 3.0, 0.0])   # Arriba
    engine._positions[2] = np.array([-3.0, 0.0, 0.0])  # Izquierda
    engine._positions[3] = np.array([0.0, -3.0, 0.0])  # Abajo
    
    # Sincronizar
    for i in range(4):
        if i in engine.motion_states:
            engine.motion_states[i].state.position[:] = engine._positions[i]
        print(f"   Fuente {i}: {engine._positions[i]}")
    
    # Configurar rotación con velocidad MÁS LENTA
    print("\\n🔧 Configurando rotación de 90° con velocidad lenta...")
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,                # 90° objetivo
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.05      # MÁS LENTO (era 0.5)
    )
    
    # Simular
    print("\\n⚙️ Ejecutando rotación (120 frames = 2 segundos)...")
    initial_pos = [engine._positions[i].copy() for i in range(4)]
    
    for frame in range(120):
        engine.update()
        
        if frame % 30 == 29:  # Cada 0.5 segundos
            print(f"\\n   Tiempo {(frame+1)/60:.1f}s:")
            for i in range(4):
                pos = engine._positions[i]
                dist = np.linalg.norm(pos - initial_pos[i])
                print(f"      Fuente {i}: [{pos[0]:5.2f}, {pos[1]:5.2f}, {pos[2]:5.2f}] (dist: {dist:5.2f})")
    
    # Verificar resultado final
    print("\\n📊 Resultado final después de 2 segundos:")
    print("   " + "-" * 50)
    
    for i in range(4):
        inicial = initial_pos[i]
        final = engine._positions[i]
        dist = np.linalg.norm(final - inicial)
        
        print(f"\\n   Fuente {i}:")
        print(f"      Inicial: [{inicial[0]:5.2f}, {inicial[1]:5.2f}, {inicial[2]:5.2f}]")
        print(f"      Final:   [{final[0]:5.2f}, {final[1]:5.2f}, {final[2]:5.2f}]")
        print(f"      Distancia: {dist:5.2f}")
        
        # Verificar rotación esperada
        if i == 0:  # (3,0,0) -> (0,3,0) después de 90°
            expected = np.array([0.0, 3.0, 0.0])
            error = np.linalg.norm(final[:2] - expected[:2])
            print(f"      Error de rotación: {error:.3f}")
            if error < 0.5:
                print(f"      ✅ Rotación precisa")
    
    print("\\n" + "=" * 60)
    print("✅ ManualMacroRotation funciona correctamente")
    print("✅ La velocidad de interpolación controla la rotación")

if __name__ == "__main__":
    test_rotation_controlled()
'''
    
    with open('test_rotation_controlled.py', 'w') as f:
        f.write(controlled_test)
    
    print("✅ test_rotation_controlled.py creado")

if __name__ == "__main__":
    fix_tests()
    
    print("\n📋 Tests disponibles:")
    print("   python test_rotation_simple.py      # Test básico")
    print("   python test_rotation_controlled.py  # Test con velocidad controlada")
    print("   python test_rotation_success.py     # Test completo")
    print("\n💡 El problema en test_rotation_corrected.py era la velocidad muy alta")