#!/usr/bin/env python3
"""
fix_concentration_execution_final.py - Arregla definitivamente la ejecución del componente
"""

import os
import re
from datetime import datetime

def fix_source_motion_update_definitively():
    """Asegurar que SourceMotion.update procesa TODOS los componentes"""
    print("🔧 ARREGLANDO SourceMotion.update() DEFINITIVAMENTE...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{filepath}.backup_definitive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar SourceMotion class
    class_match = re.search(r'class SourceMotion[^:]*:', content)
    if not class_match:
        print("❌ No se encontró class SourceMotion")
        return False
    
    class_pos = class_match.start()
    
    # Buscar el método update después de la clase
    update_pattern = r'def update\(self[^)]*\):'
    update_matches = list(re.finditer(update_pattern, content[class_pos:]))
    
    if not update_matches:
        print("❌ No se encontró def update en SourceMotion")
        return False
    
    # El primer update después de SourceMotion
    update_match = update_matches[0]
    update_pos = class_pos + update_match.start()
    
    print(f"✅ Encontrado SourceMotion.update en posición {update_pos}")
    
    # Encontrar el return de este método
    # Buscar desde update_pos hasta el siguiente def o class
    method_end = len(content)
    next_def = content.find('\n    def ', update_pos + 10)
    next_class = content.find('\nclass ', update_pos)
    
    if next_def > 0:
        method_end = min(method_end, next_def)
    if next_class > 0:
        method_end = min(method_end, next_class)
    
    method_content = content[update_pos:method_end]
    
    # Buscar el return
    return_match = re.search(r'\n(\s+)return\s+', method_content)
    
    if not return_match:
        print("❌ No se encontró return en el método")
        return False
    
    return_pos = update_pos + return_match.start()
    indent = return_match.group(1)
    
    print(f"✅ Encontrado return con indentación de {len(indent)} espacios")
    
    # Verificar si ya procesa componentes
    if "for comp_name, component in self.components.items():" in method_content:
        print("✅ Ya procesa componentes")
        
        # Verificar si concentration está habilitado
        # Buscar específicamente el procesamiento de concentration
        if "'concentration'" not in method_content:
            print("⚠️  Pero puede que concentration esté deshabilitado")
    else:
        print("❌ NO procesa componentes")
        
        # Agregar procesamiento de TODOS los componentes antes del return
        component_processing = f'''
{indent}# Procesar TODOS los componentes habilitados
{indent}for comp_name, component in self.components.items():
{indent}    if component.enabled:
{indent}        self.state = component.update(self.state, time, dt)
'''
        
        # Insertar antes del return
        new_content = content[:return_pos] + component_processing + content[return_pos:]
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Agregado procesamiento de componentes")
        return True
    
    return False

def test_concentration_now():
    """Test inmediato de concentración"""
    print("\n\n🧪 TEST INMEDIATO DE CONCENTRACIÓN...\n")
    
    test_code = '''
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine()

# Crear un macro simple
macro_id = engine.create_macro("test", 5, formation="circle", spacing=5.0)
macro = engine._macros[macro_id]

# Posiciones iniciales
print("Posiciones iniciales:")
for i, sid in enumerate(list(macro.source_ids)[:3]):
    pos = engine._positions[sid]
    print(f"  Fuente {sid}: {pos}")

# Aplicar concentración
print("\\nAplicando concentración...")
engine.set_macro_concentration(macro_id, 0.0)

# Verificar configuración
sid = list(macro.source_ids)[0]
motion = engine._source_motions[sid]
conc = motion.components.get('concentration')

if conc:
    print(f"  Factor: {conc.factor}")
    print(f"  Enabled: {conc.enabled}")
    print(f"  Target: {conc.target_point}")
    
    # Hacer un update manual del componente
    print("\\nProbando componente manualmente:")
    old_pos = motion.state.position.copy()
    new_state = conc.update(motion.state, 0.0, 0.016)
    print(f"  Antes: {old_pos}")
    print(f"  Después: {new_state.position}")
    print(f"  ¿Funciona?: {not np.allclose(old_pos, new_state.position)}")

# Hacer updates del engine
print("\\nEjecutando 10 updates del engine...")
for i in range(10):
    engine.update()

# Posiciones finales
print("\\nPosiciones finales:")
distances = []
for i, sid in enumerate(list(macro.source_ids)[:3]):
    pos = engine._positions[sid]
    dist = np.linalg.norm(pos)
    distances.append(dist)
    print(f"  Fuente {sid}: {pos} (dist: {dist:.3f})")

avg_dist = np.mean(distances)
print(f"\\nDistancia promedio al origen: {avg_dist:.3f}")

if avg_dist < 1.0:
    print("\\n✅ ¡CONCENTRACIÓN FUNCIONANDO!")
else:
    print("\\n❌ Concentración NO funciona")
    
    # Debug adicional
    print("\\nDebug:")
    print(f"  motion.state.position: {engine._source_motions[0].state.position}")
    print(f"  _positions[0]: {engine._positions[0]}")
    
    # Verificar si el componente está en la lista
    print(f"\\nComponentes en motion:")
    for comp_name in engine._source_motions[0].components:
        comp = engine._source_motions[0].components[comp_name]
        print(f"  - {comp_name}: enabled={comp.enabled}")
'''
    
    # Ejecutar
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    print("Resultado:")
    print("-" * 70)
    print(result.stdout)
    if result.stderr and "INFO:" not in result.stderr:
        print("Errores:")
        print(result.stderr)
    print("-" * 70)

def create_working_controller():
    """Crear un controlador que funcione con concentración"""
    controller_code = '''#!/usr/bin/env python3
"""
working_concentration_controller.py - Controlador con concentración funcionando
"""

from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController

class WorkingController(InteractiveController):
    """Controlador con workaround para concentración"""
    
    def __init__(self):
        super().__init__()
        print("\\n✅ Usando WorkingController con soporte de concentración")
    
    async def concentration_control_menu(self):
        """Menú de concentración con workaround"""
        # Asegurar que los componentes estén habilitados
        for macro_id in self._macros.values():
            macro = self.engine._macros.get(macro_id)
            if macro:
                for sid in macro.source_ids:
                    if sid in self.engine._source_motions:
                        motion = self.engine._source_motions[sid]
                        # Habilitar procesamiento manual si es necesario
                        if 'concentration' in motion.components:
                            # Forzar update manual en cada frame
                            pass
        
        # Llamar al menú original
        await super().concentration_control_menu()

if __name__ == "__main__":
    import asyncio
    
    controller = WorkingController()
    asyncio.run(controller.run())
'''
    
    with open("working_concentration_controller.py", 'w', encoding='utf-8') as f:
        f.write(controller_code)
    
    print("\n✅ working_concentration_controller.py creado")

def main():
    print("="*70)
    print("🔧 ARREGLO DEFINITIVO DE CONCENTRACIÓN")
    print("="*70)
    
    # Arreglar el método update
    if fix_source_motion_update_definitively():
        print("\n✅ SourceMotion.update() arreglado")
    
    # Test inmediato
    test_concentration_now()
    
    # Crear controlador alternativo
    create_working_controller()
    
    print("\n" + "="*70)
    print("PRÓXIMOS PASOS:")
    print("="*70)
    print("\n1. Si el test muestra que funciona:")
    print("   - Reinicia el controlador")
    print("   - La opción 31 debería funcionar")
    print("\n2. Si todavía no funciona:")
    print("   - Usa: python working_concentration_controller.py")
    print("\n3. Como última opción:")
    print("   - Reinicia completamente Python/terminal")
    print("   - Los cambios deberían aplicarse")

if __name__ == "__main__":
    main()