# === fix_final_issues.py ===
# 🔧 Fix: Arregla SourceMotion(state) y parámetros del engine
# ⚡ Impacto: CRÍTICO - Corrige últimos errores

import os
import re
from datetime import datetime

def fix_source_motion_call():
    """Arregla la llamada a SourceMotion para usar solo state"""
    
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
    print(f"✅ Backup creado: {backup_path}")
    
    # Fix 1: SourceMotion solo necesita state
    old_line = "motion = SourceMotion(source_id, state)"
    new_line = "motion = SourceMotion(state)"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print(f"✅ Actualizado: {new_line}")
    
    # Añadir asignación de source_id después si es necesario
    if new_line in content:
        # Buscar la línea y añadir después
        lines = content.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == new_line.strip():
                # Añadir asignación de source_id
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + "motion.source_id = source_id")
                print("✅ Añadido: motion.source_id = source_id")
        
        content = '\n'.join(new_lines)
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def find_engine_params():
    """Encuentra los parámetros correctos del engine"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar __init__
    pattern = r'class EnhancedTrajectoryEngine.*?def __init__\(self([^)]*)\):'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        params = match.group(1).strip()
        print(f"\n📋 Parámetros de EnhancedTrajectoryEngine.__init__:")
        print(f"   {params}")
        
        # Extraer nombres de parámetros
        param_names = []
        if params:
            # Simple parser para parámetros
            parts = params.split(',')
            for part in parts:
                if ':' in part:
                    name = part.split(':')[0].strip()
                    param_names.append(name)
                elif '=' in part:
                    name = part.split('=')[0].strip()
                    param_names.append(name)
        
        return param_names
    
    return []

def create_corrected_test():
    """Crea test con parámetros correctos"""
    
    params = find_engine_params()
    
    # Determinar qué parámetro usar
    if 'max_sources' in params:
        param_str = "max_sources=5"
    elif 'n_max_sources' in params:
        param_str = "n_max_sources=5"
    else:
        param_str = ""  # Sin parámetros
    
    test_code = f'''# === test_corrected.py ===
# Test con parámetros correctos

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST CORREGIDO")
print("="*50)

try:
    # Crear engine con parámetros correctos
    engine = EnhancedTrajectoryEngine({param_str})
    print("✅ Engine creado")
    
    # Crear una fuente
    engine.create_source(0, "test_0")
    print("✅ Fuente creada")
    
    # Crear un macro
    engine.create_macro("test", [0, 1, 2])
    print("✅ Macro creado")
    
    print("\\n✅ SISTEMA FUNCIONANDO")
    
except Exception as e:
    print(f"❌ Error: {{e}}")
    import traceback
    traceback.print_exc()
'''
    
    with open('test_corrected.py', 'w') as f:
        f.write(test_code)
    
    print(f"\n✅ Test corregido creado: test_corrected.py")
    if param_str:
        print(f"   Usando: EnhancedTrajectoryEngine({param_str})")
    else:
        print("   Usando: EnhancedTrajectoryEngine() sin parámetros")

if __name__ == "__main__":
    print("🔧 FIX FINAL DE ISSUES")
    print("="*60)
    
    # Fix 1: Arreglar SourceMotion
    print("\n1️⃣ Arreglando SourceMotion...")
    success1 = fix_source_motion_call()
    
    # Fix 2: Encontrar parámetros correctos
    print("\n2️⃣ Analizando parámetros del engine...")
    params = find_engine_params()
    
    # Crear test corregido
    create_corrected_test()
    
    if success1:
        print("\n✅ Fixes aplicados")
        print("\n📋 Prueba el test corregido:")
        print("$ python test_corrected.py")
        print("\nSi funciona, intenta:")
        print("$ python test_delta_concentration_final.py")
    else:
        print("\n❌ Algunos fixes fallaron")