# === fix_shape_params_direct.py ===
# 🔧 Fix directo y definitivo para shape_params
# ⚡ Busca y corrige el problema exacto
# 🎯 Impacto: CRÍTICO - Sin esto no funciona

import os
import re

def find_set_individual_trajectory():
    """Encuentra exactamente dónde está set_individual_trajectory"""
    
    engine_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("🔍 Buscando set_individual_trajectory...")
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar la definición del método
    for i, line in enumerate(lines):
        if "def set_individual_trajectory" in line:
            print(f"✅ Encontrado en línea {i+1}")
            
            # Mostrar las siguientes 30 líneas para ver el método
            print("\n📝 Método actual:")
            for j in range(min(30, len(lines) - i)):
                print(f"{i+j+1}: {lines[i+j].rstrip()}")
            
            return engine_path, i
    
    return None, -1

def fix_set_individual_direct():
    """Arregla directamente el método para que guarde shape_params"""
    
    engine_path, line_num = find_set_individual_trajectory()
    
    if not engine_path:
        print("❌ No se encontró el método")
        return False
    
    print("\n🔧 Aplicando fix directo...")
    
    # Leer el archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar dónde insertar el código
    insert_line = -1
    for i in range(line_num, min(line_num + 50, len(lines))):
        if "trajectory = IndividualTrajectory()" in lines[i]:
            # Buscar unas líneas después para insertar
            for j in range(i+1, min(i+10, len(lines))):
                if "trajectory." in lines[j]:
                    insert_line = j
                    break
            break
    
    if insert_line > 0:
        print(f"✅ Insertando código en línea {insert_line+1}")
        
        # Insertar la línea que guarda shape_params
        indent = "        "  # 8 espacios
        new_lines = [
            f"{indent}# IMPORTANTE: Inicializar shape_params\n",
            f"{indent}trajectory.shape_params = shape_params if shape_params is not None else {{}}\n",
            f"{indent}\n"
        ]
        
        # Insertar las nuevas líneas
        for i, new_line in enumerate(new_lines):
            lines.insert(insert_line + i, new_line)
        
        # Hacer backup
        import shutil
        from datetime import datetime
        backup_name = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_path, backup_name)
        print(f"✅ Backup creado: {backup_name}")
        
        # Escribir el archivo
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ Fix aplicado exitosamente")
        return True
    else:
        print("❌ No se pudo encontrar dónde insertar el código")
        return False

def verify_shape_params_in_init():
    """Verifica que shape_params esté en __init__"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("\n🔍 Verificando __init__ de IndividualTrajectory...")
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si shape_params ya está inicializado
    if "self.shape_params = {}" in content:
        print("✅ shape_params ya está inicializado en __init__")
        return True
    
    print("⚠️ shape_params NO está en __init__, verificando estructura...")
    
    # Mostrar la estructura actual de IndividualTrajectory
    class_match = re.search(r'class IndividualTrajectory.*?def __init__\(self\):(.*?)(?=\n    def)', 
                           content, re.DOTALL)
    
    if class_match:
        init_content = class_match.group(1)
        print("\n📝 __init__ actual:")
        print(init_content[:500])  # Primeros 500 caracteres
    
    return False

def create_debug_test():
    """Test de debug para ver el estado del objeto"""
    
    test_code = '''# === debug_test.py ===
# Debug detallado del problema

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine y configurar
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60, enable_modulator=False)
macro_name = engine.create_macro("test", source_count=1)
sid = list(engine._macros[macro_name].source_ids)[0]

# Configurar trayectoria
engine.set_individual_trajectory(
    macro_name, sid,
    shape="circle",
    shape_params={'radius': 2.0},
    movement_mode="fix",
    speed=1.0
)

# Debug: Ver qué tiene el objeto
motion = engine.motion_states[sid]
if 'individual_trajectory' in motion.active_components:
    traj = motion.active_components['individual_trajectory']
    
    print("🔍 DEBUG - Atributos de IndividualTrajectory:")
    attrs = [attr for attr in dir(traj) if not attr.startswith('_')]
    for attr in sorted(attrs):
        try:
            value = getattr(traj, attr)
            if not callable(value):
                print(f"  - {attr}: {value}")
        except:
            pass
    
    # Verificar específicamente shape_params
    print("\\n🔍 shape_params existe:", hasattr(traj, 'shape_params'))
    if hasattr(traj, 'shape_params'):
        print(f"   Valor: {traj.shape_params}")
    else:
        print("   ❌ NO EXISTE")
        print("\\n   Intentando añadirlo manualmente...")
        traj.shape_params = {'radius': 2.0}
        print("   ✅ Añadido manualmente")
    
    # Probar un update
    try:
        print("\\n🧪 Probando update...")
        engine.update()
        print("✅ Update ejecutado sin errores")
    except Exception as e:
        print(f"❌ Error: {e}")
'''
    
    with open("debug_test.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test de debug creado")

if __name__ == "__main__":
    print("🔧 FIX DIRECTO SHAPE_PARAMS")
    print("=" * 50)
    
    # Paso 1: Encontrar y arreglar set_individual_trajectory
    if fix_set_individual_direct():
        print("\n✅ Paso 1 completado")
    
    # Paso 2: Verificar __init__
    verify_shape_params_in_init()
    
    # Crear test de debug
    create_debug_test()
    
    print("\n📝 Ejecuta:")
    print("1. python debug_test.py    # Para ver qué está pasando")
    print("2. python quick_test.py    # Para probar si funciona")