# === fix_source_motion_init.py ===
# 🔧 Fix: Corrige la inicialización de SourceMotion
# ⚡ Impacto: ALTO - SourceMotion espera diferentes parámetros

import os
import re
from datetime import datetime

def diagnose_source_motion():
    """Diagnostica cómo se debe inicializar SourceMotion"""
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    if not os.path.exists(motion_path):
        print("❌ No se encuentra motion_components.py")
        return None
    
    print("🔍 Analizando SourceMotion...")
    
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar SourceMotion.__init__
    pattern = r'class SourceMotion.*?def __init__\(self([^)]*)\):'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        params = match.group(1).strip()
        print(f"✅ Encontrado SourceMotion.__init__(self{params})")
        
        # Analizar parámetros
        if not params:
            print("  📌 SourceMotion NO espera parámetros adicionales")
            return "no_params"
        elif 'state' in params and 'source_id' not in params:
            print("  📌 SourceMotion espera solo 'state'")
            return "state_only"
        elif 'source_id' in params and 'state' in params:
            print("  📌 SourceMotion espera 'source_id' y 'state'")
            return "both"
        else:
            print(f"  ⚠️ Parámetros no reconocidos: {params}")
            return "unknown"
    
    return None

def fix_create_source_call():
    """Arregla la llamada a SourceMotion en create_source"""
    
    # Primero diagnosticar
    init_type = diagnose_source_motion()
    
    if not init_type:
        print("❌ No se pudo diagnosticar SourceMotion")
        return False
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✅ Backup creado: {backup_path}")
    
    # Buscar la línea problemática
    problem_line = "motion = SourceMotion(source_id, state)"
    
    if init_type == "no_params":
        # SourceMotion no espera parámetros
        new_line = "motion = SourceMotion()"
        # Necesitamos asignar source_id y state después
        post_init = """
        # Asignar propiedades después de crear
        if hasattr(motion, 'source_id'):
            motion.source_id = source_id
        if hasattr(motion, 'state'):
            motion.state = state
        elif hasattr(motion, 'motion_state'):
            motion.motion_state = state"""
            
    elif init_type == "state_only":
        # SourceMotion espera solo state
        new_line = "motion = SourceMotion(state)"
        # Asignar source_id después si es necesario
        post_init = """
        # Asignar source_id si es necesario
        if hasattr(motion, 'source_id'):
            motion.source_id = source_id"""
            
    else:  # both o unknown
        # Mantener como está o intentar orden inverso
        new_line = "motion = SourceMotion(source_id, state)"
        post_init = ""
    
    # Reemplazar
    if problem_line in content:
        if post_init:
            # Necesitamos añadir código después
            indent = "        "  # Asumiendo indentación estándar
            replacement = new_line + post_init.replace("\n", "\n" + indent)
            content = content.replace(problem_line, replacement)
        else:
            content = content.replace(problem_line, new_line)
        
        print(f"✅ Actualizado: {new_line}")
        
        # Escribir archivo
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Verificar sintaxis
        try:
            compile(content, engine_path, 'exec')
            print("✅ Sintaxis verificada")
            return True
        except Exception as e:
            print(f"❌ Error de sintaxis: {e}")
            # Restaurar
            with open(backup_path, 'r', encoding='utf-8') as f:
                original = f.read()
            with open(engine_path, 'w', encoding='utf-8') as f:
                f.write(original)
            print("⚠️ Backup restaurado")
            return False
    else:
        print("❌ No se encontró la línea a reemplazar")
        return False

def create_simple_test():
    """Crea un test simple para verificar la creación de fuentes"""
    test_code = '''# === test_source_creation.py ===
# Test simple de creación de fuentes

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import SourceMotion, MotionState

print("🧪 TEST DE CREACIÓN DE FUENTES")
print("="*50)

# Test 1: Crear SourceMotion directamente
print("\\n1️⃣ Test directo de SourceMotion:")
try:
    state = MotionState()
    
    # Intentar diferentes formas
    try:
        motion1 = SourceMotion()
        print("  ✅ SourceMotion() funciona")
    except:
        pass
    
    try:
        motion2 = SourceMotion(state)
        print("  ✅ SourceMotion(state) funciona")
    except:
        pass
    
    try:
        motion3 = SourceMotion(0, state)
        print("  ✅ SourceMotion(id, state) funciona")
    except:
        pass
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: Crear a través del engine
print("\\n2️⃣ Test a través del engine:")
try:
    engine = EnhancedTrajectoryEngine(n_sources=5)
    engine.create_source(0, "test_0")
    print("  ✅ create_source funciona")
    
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open('test_source_creation.py', 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test creado: test_source_creation.py")

if __name__ == "__main__":
    print("🔧 FIX DE SOURCEMOTION INIT")
    print("="*60)
    
    # Crear test
    create_simple_test()
    
    # Aplicar fix
    success = fix_create_source_call()
    
    if success:
        print("\n✅ Fix aplicado")
        print("\n📋 Prueba primero el test simple:")
        print("$ python test_source_creation.py")
        print("\nLuego intenta:")
        print("$ python test_delta_concentration_final.py")
    else:
        print("\n❌ No se pudo aplicar el fix")
        print("\nEjecuta el test para diagnosticar:")
        print("$ python test_source_creation.py")