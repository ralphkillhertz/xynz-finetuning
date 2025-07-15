#!/usr/bin/env python3
"""
manual_fix_concentration.py - Corrección manual del sistema de concentración
"""

import os
from datetime import datetime

def find_and_show_source_motion():
    """Mostrar la estructura actual de SourceMotion"""
    print("🔍 ANALIZANDO ESTRUCTURA DE SourceMotion...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar SourceMotion
    source_motion_start = -1
    init_start = -1
    init_end = -1
    
    for i, line in enumerate(lines):
        if "class SourceMotion" in line:
            source_motion_start = i
            print(f"Clase SourceMotion encontrada en línea {i+1}")
            
        elif source_motion_start != -1 and "def __init__" in line:
            init_start = i
            print(f"__init__ encontrado en línea {i+1}")
            
        elif init_start != -1 and line.strip() and not line.startswith("        "):
            init_end = i
            break
    
    if init_start != -1:
        print("\nContenido de __init__:")
        print("-" * 60)
        for i in range(init_start, min(init_end if init_end != -1 else init_start + 50, len(lines))):
            print(f"{i+1:4d}: {lines[i].rstrip()}")
        print("-" * 60)
        
        # Buscar patrón de componentes
        components_dict_start = -1
        for i in range(init_start, min(init_end if init_end != -1 else len(lines), len(lines))):
            if "self.components = {" in lines[i]:
                components_dict_start = i
                print(f"\n✅ Encontrado diccionario de componentes en línea {i+1}")
                break
        
        return filepath, lines, components_dict_start
    
    return None, None, -1

def add_concentration_to_dict():
    """Agregar concentration al diccionario de componentes"""
    print("\n\n🔧 AGREGANDO CONCENTRATION AL DICCIONARIO...\n")
    
    filepath, lines, dict_start = find_and_show_source_motion()
    
    if dict_start == -1:
        print("❌ No se encontró el diccionario de componentes")
        return False
    
    # Backup
    backup_name = f"{filepath}.backup_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    # Buscar el final del diccionario
    dict_end = -1
    brace_count = 0
    
    for i in range(dict_start, len(lines)):
        line = lines[i]
        brace_count += line.count('{') - line.count('}')
        
        if brace_count == 0 and '}' in line:
            dict_end = i
            break
    
    if dict_end == -1:
        print("❌ No se encontró el final del diccionario")
        return False
    
    print(f"Diccionario de componentes: líneas {dict_start+1} a {dict_end+1}")
    
    # Verificar si concentration ya está
    already_has = any("concentration" in lines[i] for i in range(dict_start, dict_end))
    
    if already_has:
        print("✅ concentration ya está en el diccionario")
        return False
    
    # Agregar concentration antes del cierre
    indent = "            "  # Ajustar según sea necesario
    concentration_line = f"{indent}'concentration': ConcentrationComponent(),\n"
    
    # Insertar antes del }
    lines.insert(dict_end, concentration_line)
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Agregada línea de concentration en posición {dict_end+1}")
    return True

def final_test_with_debug():
    """Test final con debug detallado"""
    print("\n\n🧪 TEST FINAL CON DEBUG...\n")
    
    test_code = '''
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent

# Crear engine
engine = EnhancedTrajectoryEngine()

# Crear una sola fuente para test simple
engine.create_source(0, "test")
motion = engine._source_motions[0]

print("1. Componentes después de crear fuente:")
for comp in motion.components:
    print(f"   - {comp}")

# Si no existe concentration, agregarlo
if 'concentration' not in motion.components:
    print("\\n2. Agregando concentration manualmente...")
    motion.components['concentration'] = ConcentrationComponent()
    print("   ✅ Agregado")
else:
    print("\\n2. ✅ concentration ya existe")

# Verificar el componente
conc = motion.components['concentration']
print(f"\\n3. Estado inicial de concentration:")
print(f"   - Enabled: {conc.enabled}")
print(f"   - Factor: {conc.factor}")

# Establecer posición inicial
motion.state.position = np.array([5.0, 5.0, 0.0])
engine._positions[0] = motion.state.position.copy()

print(f"\\n4. Posición inicial: {motion.state.position}")

# Configurar concentration
conc.enabled = True
conc.factor = 0.0  # Totalmente concentrado
conc.target_point = np.array([0.0, 0.0, 0.0])

print(f"\\n5. Configuración de concentration:")
print(f"   - Factor: {conc.factor}")
print(f"   - Target: {conc.target_point}")

# Hacer UN update
print("\\n6. Ejecutando UN engine.update()...")
engine.update()

print(f"\\n7. Después del update:")
print(f"   - motion.state.position: {motion.state.position}")
print(f"   - engine._positions[0]: {engine._positions[0]}")
print(f"   - ¿Se movió?: {not np.allclose(motion.state.position, [5.0, 5.0, 0.0])}")

# Verificar si se está ejecutando el update del componente
# Hagamos un update manual para verificar
print("\\n8. Update manual del componente:")
old_pos = motion.state.position.copy()
new_state = conc.update(motion.state, 0.0, 0.016)
print(f"   - Posición antes: {old_pos}")
print(f"   - Posición después: {new_state.position}")
print(f"   - ¿Cambió?: {not np.allclose(old_pos, new_state.position)}")
'''
    
    # Ejecutar test
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    print("Resultado:")
    print("-" * 70)
    print(result.stdout)
    if result.stderr and "INFO:" not in result.stderr:
        print("Errores:")
        print(result.stderr)
    print("-" * 70)

def main():
    print("="*70)
    print("🔧 CORRECCIÓN MANUAL DEL SISTEMA DE CONCENTRACIÓN")
    print("="*70)
    
    # Intentar agregar al diccionario
    if add_concentration_to_dict():
        print("\n✅ Componente agregado al diccionario")
    
    # Test con debug
    final_test_with_debug()
    
    print("\n" + "="*70)
    print("PRÓXIMOS PASOS:")
    print("="*70)
    print("\n1. Si el componente se agrega pero no funciona,")
    print("   el problema puede estar en ConcentrationComponent.update()")
    print("\n2. Si necesitas una solución inmediata:")
    print("   python concentration_workaround.py")

if __name__ == "__main__":
    main()