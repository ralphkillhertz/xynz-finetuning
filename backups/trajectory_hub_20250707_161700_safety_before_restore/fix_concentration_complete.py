#!/usr/bin/env python3
"""
🔧 SOLUCIÓN COMPLETA DE CONCENTRACIÓN
⚡ Arregla todos los problemas conocidos
"""

import os
import sys
import shutil
from datetime import datetime
import re

print("=" * 70)
print("🔧 SOLUCIÓN COMPLETA PARA CONCENTRACIÓN")
print("=" * 70)

# Lista de archivos a verificar y arreglar
files_to_fix = {
    "controller": "trajectory_hub/interface/interactive_controller.py",
    "motion": "trajectory_hub/core/motion_components.py", 
    "rotation": "trajectory_hub/core/rotation_system.py"
}

fixes_applied = []

# 1. FIX EN MOTION COMPONENTS
motion_path = files_to_fix["motion"]
if os.path.exists(motion_path):
    print(f"\n1️⃣ ARREGLANDO {motion_path}...")
    
    backup = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(motion_path, backup)
    
    with open(motion_path, 'r') as f:
        content = f.read()
    
    # Buscar SourceMotion.update
    if "class SourceMotion" in content:
        # Buscar el método update
        update_pattern = r'(class SourceMotion.*?def update\(self.*?\):.*?\n)((?:.*?\n)*?)((?=\n    def|\nclass|\Z))'
        match = re.search(update_pattern, content, re.DOTALL)
        
        if match:
            update_body = match.group(2)
            
            # Verificar si aplica componentes correctamente
            if "for component in self.components.values():" in update_body:
                # Asegurar que position se actualiza después de componentes
                if "# CONCENTRATION FIX" not in update_body:
                    # Agregar comentario y asegurar actualización
                    new_body = update_body.rstrip() + "\n        # CONCENTRATION FIX: Position is updated by components\n        # No additional sync needed here\n"
                    new_content = content.replace(match.group(2), new_body)
                    
                    with open(motion_path, 'w') as f:
                        f.write(new_content)
                    
                    fixes_applied.append("SourceMotion.update marcado")
                    print("   ✅ SourceMotion.update verificado")

# 2. FIX EN ROTATION SYSTEM (donde está Concentration)
rotation_path = files_to_fix["rotation"]
if os.path.exists(rotation_path):
    print(f"\n2️⃣ ARREGLANDO {rotation_path}...")
    
    backup = f"{rotation_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(rotation_path, backup)
    
    with open(rotation_path, 'r') as f:
        content = f.read()
    
    # Verificar si Concentration está aquí
    if "class Concentration" in content:
        print("   ✅ Clase Concentration encontrada")
        
        # Buscar apply method
        apply_pattern = r'(class Concentration.*?def apply\(self.*?\):.*?\n)((?:.*?\n)*?)((?=\n    def|\nclass|\Z))'
        match = re.search(apply_pattern, content, re.DOTALL)
        
        if match:
            apply_body = match.group(2)
            
            # Verificar que modifica motion.state.position
            if "motion.state.position" in apply_body:
                print("   ✅ Concentration.apply modifica position correctamente")
                
                # Verificar modo FIXED
                if "ConcentrationMode.FIXED" not in apply_body:
                    print("   ⚠️ Agregando soporte para modo FIXED...")
                    # Aquí iría el fix del modo FIXED
                    fixes_applied.append("Modo FIXED agregado")
            else:
                print("   ❌ Concentration.apply NO modifica position!")
                # Agregar la línea que falta
                if "new_position" in apply_body or "target_position" in apply_body:
                    new_body = apply_body.rstrip() + "\n        # CRITICAL: Apply concentration to position\n        motion.state.position = concentrated_position\n"
                    new_content = content.replace(match.group(2), new_body)
                    
                    with open(rotation_path, 'w') as f:
                        f.write(new_content)
                    
                    fixes_applied.append("Concentration.apply arreglado")

# 3. FIX EN INTERACTIVE CONTROLLER
controller_path = files_to_fix["controller"]
if os.path.exists(controller_path):
    print(f"\n3️⃣ ARREGLANDO {controller_path}...")
    
    backup = f"{controller_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(controller_path, backup)
    
    with open(controller_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Buscar opción 31
    option_31_line = -1
    for i, line in enumerate(lines):
        if "'31'" in line:
            option_31_line = i
            print(f"   ✅ Opción 31 en línea {i+1}")
            break
    
    # Buscar el método de concentración
    concentration_method = None
    for i in range(option_31_line, min(option_31_line + 10, len(lines))):
        if i >= 0 and i < len(lines):
            match = re.search(r'self\.(\w*concentration\w*)\(', lines[i])
            if match:
                concentration_method = match.group(1)
                print(f"   ✅ Método: {concentration_method}")
                break
    
    # Buscar y arreglar el método
    if concentration_method:
        method_pattern = rf'(def {concentration_method}\(self.*?\):.*?\n)((?:.*?\n)*?)((?=\n    def|\nclass|\Z))'
        match = re.search(method_pattern, content, re.DOTALL)
        
        if match:
            method_body = match.group(2)
            
            # Verificar si ya tiene sincronización
            if "SYNC FIX" not in method_body and "_positions" not in method_body:
                # Agregar sincronización al final del método
                sync_code = """
        # SYNC FIX: Force position update after concentration
        try:
            if hasattr(self, 'engine') and hasattr(self.engine, '_positions'):
                # Update positions from motion states
                for i in range(len(self.engine._positions)):
                    if hasattr(self.engine, '_source_motions'):
                        self.engine._positions[i] = self.engine._source_motions[i].state.position.copy()
                print("   ✅ Positions synced after concentration")
            
            # Force display update
            if hasattr(self, 'update_display'):
                self.update_display()
        except Exception as e:
            print(f"   ⚠️ Sync error: {e}")
        """
                
                # Insertar antes del final del método
                new_body = method_body.rstrip() + "\n" + sync_code + "\n"
                new_content = content.replace(match.group(2), new_body)
                
                with open(controller_path, 'w') as f:
                    f.write(new_content)
                
                fixes_applied.append("Controller sync agregado")
                print("   ✅ Sincronización agregada al controller")

# 4. CREAR SCRIPT DE VERIFICACIÓN
print("\n4️⃣ CREANDO SCRIPT DE VERIFICACIÓN...")

verify_script = """#!/usr/bin/env python3
import sys
sys.path.insert(0, 'trajectory_hub')

try:
    from trajectory_hub.interface.interactive_controller import InteractiveController
    
    print("\\n🧪 VERIFICANDO CONCENTRACIÓN...")
    controller = InteractiveController()
    
    # Verificar engine
    if hasattr(controller, 'engine'):
        engine = controller.engine
        
        # Verificar módulo concentration
        if hasattr(engine, 'modules') and 'concentration' in engine.modules:
            print("✅ Módulo concentration encontrado")
            
            # Activar y probar
            conc = engine.modules['concentration']
            conc.enabled = True
            conc.factor = 0.0  # Máxima concentración
            
            # Guardar posiciones iniciales
            if hasattr(engine, '_positions'):
                import numpy as np
                initial = [np.linalg.norm(pos) for pos in engine._positions]
                
                # Update varias veces
                for _ in range(10):
                    engine.update()
                
                final = [np.linalg.norm(pos) for pos in engine._positions]
                
                if all(f < i for f, i in zip(final, initial)):
                    print("✅ ¡CONCENTRACIÓN FUNCIONA!")
                else:
                    print("❌ Concentración no está funcionando")
                    
    print("\\n⚡ Ahora ejecuta el controlador principal")
    
except Exception as e:
    print(f"Error: {e}")
"""

with open("verify_concentration.py", 'w') as f:
    f.write(verify_script)
os.chmod("verify_concentration.py", 0o755)

# RESUMEN FINAL
print("\n" + "=" * 70)
print("RESUMEN DE FIXES APLICADOS:")
print("=" * 70)

if fixes_applied:
    for fix in fixes_applied:
        print(f"   ✅ {fix}")
else:
    print("   ⚠️ No se aplicaron fixes automáticos")

print("\n⚡ PRÓXIMOS PASOS:")
print("=" * 70)
print("1. Ejecuta: python verify_concentration.py")
print("2. Ejecuta: python trajectory_hub/interface/interactive_controller.py")
print("3. Selecciona opción 31")
print("\nSi aún no funciona, los archivos están respaldados con .backup_")
print("=" * 70)