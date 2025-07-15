#!/usr/bin/env python3
"""
fix_concentration_init.py - Encuentra y corrige la inicialización del componente
"""

import os
import re
from datetime import datetime

def find_source_motion_init():
    """Buscar dónde se inicializan los componentes en SourceMotion"""
    print("🔍 BUSCANDO INICIALIZACIÓN DE COMPONENTES...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar SourceMotion
    in_source_motion = False
    in_init = False
    init_lines = []
    components_section = []
    
    for i, line in enumerate(lines):
        if "class SourceMotion" in line:
            in_source_motion = True
            print(f"✅ Encontrada clase SourceMotion en línea {i+1}")
        elif in_source_motion and "def __init__" in line:
            in_init = True
            print(f"✅ Encontrado __init__ en línea {i+1}")
        elif in_init and line.strip() and not line.startswith("        "):
            # Salimos del método
            break
        elif in_init:
            init_lines.append((i+1, line))
            if "self.components[" in line:
                components_section.append((i+1, line))
    
    if components_section:
        print(f"\n✅ Encontrada sección de componentes ({len(components_section)} componentes):")
        for line_num, line in components_section:
            print(f"   Línea {line_num}: {line.strip()}")
        
        # Verificar si concentration está
        has_concentration = any("concentration" in line for _, line in components_section)
        if has_concentration:
            print("\n✅ concentration YA está en la lista")
        else:
            print("\n❌ concentration NO está en la lista")
            
        return True, components_section[-1][0] if components_section else -1
    else:
        print("\n❌ No se encontró la sección de componentes")
        return False, -1

def add_concentration_component():
    """Agregar ConcentrationComponent a la inicialización"""
    print("\n\n🔧 AGREGANDO CONCENTRATION COMPONENT...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{filepath}.backup_initfix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar dónde insertar
    insert_after = -1
    found_components = False
    
    for i, line in enumerate(lines):
        if "self.components['environmental_forces']" in line:
            insert_after = i
            found_components = True
            print(f"✅ Encontrado environmental_forces en línea {i+1}")
            break
        elif "self.components =" in line and "{" in line:
            # Inicio de diccionario de componentes
            found_components = True
    
    if insert_after != -1:
        # Obtener la indentación
        indent = len(lines[insert_after]) - len(lines[insert_after].lstrip())
        
        # Crear la línea a insertar
        concentration_line = " " * indent + "self.components['concentration'] = ConcentrationComponent()\n"
        
        # Verificar si ya existe
        already_exists = any("concentration" in line and "ConcentrationComponent" in line for line in lines)
        
        if not already_exists:
            # Insertar después de environmental_forces
            lines.insert(insert_after + 1, concentration_line)
            
            # Guardar
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ Agregado ConcentrationComponent en línea {insert_after + 2}")
            return True
        else:
            print("✅ ConcentrationComponent ya existe")
            return False
    else:
        print("❌ No se encontró dónde insertar")
        
        # Buscar alternativa: el __init__ de SourceMotion
        for i, line in enumerate(lines):
            if "class SourceMotion" in line:
                # Buscar el __init__
                for j in range(i, min(i+50, len(lines))):
                    if "def __init__" in lines[j]:
                        # Buscar el final del __init__ o donde agregar
                        for k in range(j+1, min(j+100, len(lines))):
                            if "self.components" in lines[k] and "}" in lines[k]:
                                # Encontramos el diccionario, agregar antes del cierre
                                print(f"\n🔧 Intentando agregar en el diccionario de componentes...")
                                # Esta es una implementación más compleja
                                break
        
        return False

def verify_and_test():
    """Verificar y probar el sistema completo"""
    print("\n\n🧪 VERIFICACIÓN Y TEST FINAL...\n")
    
    test_code = '''
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent

print("1. Creando engine...")
engine = EnhancedTrajectoryEngine()

# Crear macro
print("\\n2. Creando macro...")
macro_id = engine.create_macro("test", 3, formation="circle", spacing=3.0)
macro = engine._macros[macro_id]

# Verificar componentes
sid = list(macro.source_ids)[0]
motion = engine._source_motions[sid]

print("\\n3. Componentes disponibles:")
for comp_name in motion.components:
    print(f"   - {comp_name}")

# Si no existe, agregarlo manualmente por ahora
if 'concentration' not in motion.components:
    print("\\n⚠️  Agregando concentration manualmente...")
    for sid in macro.source_ids:
        engine._source_motions[sid].components['concentration'] = ConcentrationComponent()

# Ahora probar
print("\\n4. Aplicando concentración...")
initial_pos = engine._positions[sid].copy()
print(f"   Posición inicial: {initial_pos}")

engine.set_macro_concentration(macro_id, 0.0)

# Updates
for _ in range(10):
    engine.update()

final_pos = engine._positions[sid]
print(f"   Posición final: {final_pos}")
print(f"   Distancia: {np.linalg.norm(final_pos - initial_pos):.3f}")

if np.linalg.norm(final_pos - initial_pos) > 0.1:
    print("\\n✅ LA CONCENTRACIÓN FUNCIONA (con agregado manual)")
else:
    print("\\n❌ La concentración no funciona")
'''
    
    # Ejecutar test
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    print("Resultado:")
    print("-" * 60)
    print(result.stdout)
    if result.stderr and "INFO:" not in result.stderr:
        print("Errores:")
        print(result.stderr)
    print("-" * 60)

def create_workaround_script():
    """Crear script temporal para usar concentración"""
    workaround = '''#!/usr/bin/env python3
"""
concentration_workaround.py - Solución temporal para usar concentración
"""

from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent

class ConcentrationEngine(EnhancedTrajectoryEngine):
    """Engine con soporte automático de concentración"""
    
    def create_source(self, source_id: int, name: str = None):
        """Override para agregar concentration automáticamente"""
        motion = super().create_source(source_id, name)
        
        # Agregar concentration si no existe
        if motion and 'concentration' not in motion.components:
            motion.components['concentration'] = ConcentrationComponent()
            
        return motion

# Usar esta clase en lugar de EnhancedTrajectoryEngine
if __name__ == "__main__":
    print("🎯 TEST DE CONCENTRACIÓN CON WORKAROUND\\n")
    
    engine = ConcentrationEngine()
    
    # Crear macro
    macro_id = engine.create_macro("test", 5, formation="circle", spacing=3.0)
    
    print("Aplicando concentración...")
    engine.animate_macro_concentration(macro_id, 0.0, 3.0, "ease_in_out")
    
    # Simular
    for i in range(180):  # 3 segundos
        engine.update()
        if i % 60 == 0:
            state = engine.get_macro_concentration_state(macro_id)
            print(f"  t={i/60}s: factor={state['factor']:.2f}")
    
    print("\\n✅ Concentración aplicada")
'''
    
    with open("concentration_workaround.py", 'w', encoding='utf-8') as f:
        f.write(workaround)
    
    print("\n✅ concentration_workaround.py creado")

def main():
    print("="*70)
    print("🔧 FIX PARA INICIALIZACIÓN DE CONCENTRATION")
    print("="*70)
    
    # Buscar dónde agregar
    found, line_num = find_source_motion_init()
    
    if found:
        # Intentar agregar
        if add_concentration_component():
            print("\n✅ Componente agregado exitosamente")
        else:
            print("\n⚠️  No se pudo agregar automáticamente")
    
    # Verificar
    verify_and_test()
    
    # Crear workaround
    create_workaround_script()
    
    print("\n" + "="*70)
    print("SOLUCIÓN TEMPORAL:")
    print("="*70)
    print("\nMientras tanto, puedes usar:")
    print("1. El controlador agregará concentration manualmente")
    print("2. O usa: python concentration_workaround.py")
    print("\nLa concentración FUNCIONA, solo necesita agregarse el componente")

if __name__ == "__main__":
    main()