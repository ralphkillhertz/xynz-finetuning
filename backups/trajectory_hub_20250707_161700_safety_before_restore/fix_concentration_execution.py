#!/usr/bin/env python3
"""
fix_concentration_execution.py - Asegura que ConcentrationComponent se ejecute
"""

import os
import re
from datetime import datetime

def find_source_motion_update():
    """Encontrar el método update de SourceMotion"""
    print("🔍 BUSCANDO SourceMotion.update()...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar SourceMotion class y su método update
    pattern = r'class SourceMotion.*?def update\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("✅ Encontrado SourceMotion.update()")
        update_content = match.group(1)
        
        # Verificar qué componentes se procesan
        print("\nComponentes procesados actualmente:")
        components = re.findall(r"'([^']+)'\s*in\s*self\.components", update_content)
        for comp in components:
            print(f"  - {comp}")
        
        # Verificar si concentration está
        if "'concentration'" in update_content:
            print("\n✅ 'concentration' YA está en el código")
            
            # Verificar si realmente se ejecuta
            if "self.components['concentration'].update" in update_content:
                print("✅ concentration.update() se llama")
            else:
                print("❌ concentration está mencionado pero NO se ejecuta")
        else:
            print("\n❌ 'concentration' NO se procesa")
        
        return True, update_content
    else:
        print("❌ No se encontró SourceMotion.update()")
        return False, None

def fix_source_motion_update():
    """Agregar procesamiento de concentration a SourceMotion.update"""
    print("\n\n🔧 CORRIGIENDO SourceMotion.update()...\n")
    
    filepath = "trajectory_hub/core/motion_components.py"
    
    # Backup
    backup_name = f"{filepath}.backup_concexec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método update de SourceMotion
    # Primero encontrar la clase
    class_start = content.find("class SourceMotion")
    if class_start == -1:
        print("❌ No se encontró class SourceMotion")
        return False
    
    # Buscar el método update después de la clase
    update_start = content.find("def update(self", class_start)
    if update_start == -1:
        print("❌ No se encontró def update en SourceMotion")
        return False
    
    # Encontrar el final del método (siguiente def o fin de clase)
    next_def = content.find("\n    def ", update_start + 1)
    if next_def == -1:
        next_def = content.find("\nclass", update_start)
    if next_def == -1:
        next_def = len(content)
    
    # Extraer el método completo
    method_content = content[update_start:next_def]
    
    # Verificar si ya procesa concentration
    if "'concentration'" in method_content and "concentration'].update" in method_content:
        print("✅ Ya procesa concentration correctamente")
        return True
    
    # Buscar dónde insertar el procesamiento de concentration
    # Debe ser AL FINAL, después de todos los otros componentes
    
    # Buscar el return statement
    return_match = re.search(r'(\s+)(return\s+)', method_content)
    
    if return_match:
        indent = return_match.group(1)
        
        # Código a insertar antes del return
        concentration_code = f'''
{indent}# Concentración se aplica como último paso
{indent}if 'concentration' in self.components:
{indent}    self.state = self.components['concentration'].update(
{indent}        self.state, current_time, dt
{indent}    )
'''
        
        # Insertar antes del return
        insert_pos = update_start + return_match.start()
        new_content = content[:insert_pos] + concentration_code + content[insert_pos:]
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Agregado procesamiento de concentration al final de update()")
        return True
    else:
        print("❌ No se encontró el return statement")
        return False

def verify_concentration_works():
    """Verificar que ahora funciona"""
    print("\n\n🧪 VERIFICANDO QUE CONCENTRATION FUNCIONA...\n")
    
    test_code = '''
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine y macro
engine = EnhancedTrajectoryEngine()
macro_id = engine.create_macro("test", 3, formation="circle", spacing=2.0)

# Obtener posiciones iniciales
macro = engine._macros[macro_id]
sid = list(macro.source_ids)[0]
initial_pos = engine._source_motions[sid].state.position.copy()
print(f"Posición inicial: {initial_pos}")

# Aplicar concentración
engine.set_macro_concentration(macro_id, 0.0)  # Concentrar en un punto

# Hacer updates
for _ in range(5):
    engine.update()

# Verificar posición final
final_pos = engine._source_motions[sid].state.position
distance = np.linalg.norm(final_pos - initial_pos)

print(f"Posición final: {final_pos}")
print(f"Distancia movida: {distance:.3f}")

if distance > 0.1:
    print("\\n✅ LA CONCENTRACIÓN FUNCIONA")
else:
    print("\\n❌ La concentración NO funciona")
'''
    
    # Ejecutar test
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    print("Resultado del test:")
    print("-" * 40)
    print(result.stdout)
    if result.stderr:
        print("Errores:")
        print(result.stderr)
    print("-" * 40)
    
    return "FUNCIONA" in result.stdout

def create_final_test():
    """Crear test final visual"""
    test_code = '''#!/usr/bin/env python3
"""
test_concentration_visual.py - Test visual de la concentración
"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import time

print("🎯 TEST VISUAL DE CONCENTRACIÓN\\n")

# Crear engine
engine = EnhancedTrajectoryEngine()

# Crear macro con más fuentes
macro_id = engine.create_macro("visual_test", 10, formation="circle", spacing=5.0)
print("✅ Macro creado con 10 fuentes en círculo\\n")

# Mostrar posiciones iniciales
print("Posiciones iniciales:")
macro = engine._macros[macro_id]
for i, sid in enumerate(list(macro.source_ids)[:3]):
    pos = engine._source_motions[sid].state.position
    print(f"  Fuente {sid}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")

# Aplicar concentración animada
print("\\n🎬 Animando concentración (3 segundos)...")
engine.animate_macro_concentration(macro_id, 0.0, 3.0, "ease_in_out")

# Simular 3 segundos
frames = 180  # 60 fps * 3 segundos
for i in range(frames):
    engine.update()
    
    # Mostrar progreso cada 0.5 segundos
    if i % 30 == 0:
        t = i / 60.0
        state = engine.get_macro_concentration_state(macro_id)
        print(f"  t={t:.1f}s - Factor: {state['factor']:.3f}")

# Mostrar posiciones finales
print("\\nPosiciones finales (concentradas):")
for i, sid in enumerate(list(macro.source_ids)[:3]):
    pos = engine._source_motions[sid].state.position
    print(f"  Fuente {sid}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")

# Verificar que están cerca del centro
distances = []
center = engine._macros[macro_id].concentration_point
for sid in macro.source_ids:
    pos = engine._source_motions[sid].state.position
    dist = np.linalg.norm(pos - center)
    distances.append(dist)

max_dist = max(distances)
avg_dist = np.mean(distances)

print(f"\\n📊 Resultados:")
print(f"  - Distancia máxima al centro: {max_dist:.3f}")
print(f"  - Distancia promedio: {avg_dist:.3f}")

if max_dist < 0.5:
    print("\\n✅ CONCENTRACIÓN EXITOSA - Todas las fuentes están en el punto central")
else:
    print("\\n❌ La concentración no funcionó correctamente")
'''
    
    with open("test_concentration_visual.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("\n✅ test_concentration_visual.py creado")

def main():
    print("="*60)
    print("🔧 FIX PARA EJECUTAR CONCENTRATION COMPONENT")
    print("="*60)
    
    # Diagnóstico
    found, content = find_source_motion_update()
    
    if found:
        # Aplicar corrección
        if fix_source_motion_update():
            # Verificar
            if verify_concentration_works():
                create_final_test()
                
                print("\n" + "="*60)
                print("✅ CONCENTRACIÓN CORREGIDA Y FUNCIONANDO")
                print("\nAhora:")
                print("1. Reinicia el controlador")
                print("2. La concentración debería funcionar en Spat")
                print("\nPuedes probar también:")
                print("  python test_concentration_visual.py")
            else:
                print("\n⚠️  Se aplicó la corrección pero necesita más verificación")
        else:
            print("\n❌ No se pudo aplicar la corrección")
    else:
        print("\n❌ No se encontró el código a corregir")

if __name__ == "__main__":
    main()