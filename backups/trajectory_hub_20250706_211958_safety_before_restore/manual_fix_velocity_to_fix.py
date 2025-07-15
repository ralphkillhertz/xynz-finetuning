#!/usr/bin/env python3
"""
🔧 Corrección manual: Encontrar y cambiar 'velocity' → 'fix' donde sea necesario
⚡ Busca específicamente los valores por defecto
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def find_and_fix_velocity_defaults():
    """Buscar y corregir valores por defecto de 'velocity'"""
    
    print("🔍 BUSCANDO Y CORRIGIENDO REFERENCIAS A 'velocity'")
    print("="*60)
    
    # Archivo principal a revisar
    engine_file = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    try:
        with open(engine_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # Buscar patrones específicos
        patterns = [
            # Valor por defecto en parámetros
            (r"movement_mode\s*=\s*movement_mode\s+or\s+['\"]velocity['\"]", 
             "movement_mode = movement_mode or 'fix'",
             "Valor por defecto en parámetro"),
            
            # Asignación directa
            (r"movement_mode\s*=\s*['\"]velocity['\"]",
             "movement_mode = 'fix'",
             "Asignación directa"),
            
            # En diccionarios o llamadas
            (r"['\"]movement_mode['\"]\s*:\s*['\"]velocity['\"]",
             "'movement_mode': 'fix'",
             "En diccionario"),
            
            # Como argumento
            (r"movement_mode\s*=\s*['\"]velocity['\"]",
             "movement_mode='fix'",
             "Como argumento")
        ]
        
        for pattern, replacement, description in patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"\n✅ Encontrado: {description}")
                for match in matches:
                    print(f"   '{match}'")
                content = re.sub(pattern, replacement, content)
                changes.append(description)
        
        # Buscar el método set_individual_trajectories específicamente
        print("\n🔍 Analizando set_individual_trajectories...")
        
        # Encontrar el método completo
        method_match = re.search(
            r'(def set_individual_trajectories\(self[^:]*:\s*\n)((?:        .*\n)*)',
            content
        )
        
        if method_match:
            method_body = method_match.group(2)
            
            # Buscar líneas con movement_mode
            lines = method_body.split('\n')
            for i, line in enumerate(lines):
                if 'movement_mode' in line:
                    print(f"   Línea {i}: {line.strip()}")
                    
                    # Si tiene 'velocity', cambiarlo
                    if "'velocity'" in line or '"velocity"' in line:
                        new_line = line.replace("'velocity'", "'fix'").replace('"velocity"', "'fix'")
                        lines[i] = new_line
                        print(f"   → Cambiado a: {new_line.strip()}")
                        changes.append(f"Línea en set_individual_trajectories")
            
            # Reconstruir el método si hubo cambios
            if len(changes) > len(patterns):
                method_body_new = '\n'.join(lines)
                content = content.replace(method_match.group(2), method_body_new)
        
        # Guardar si hubo cambios
        if content != original:
            with open(engine_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✅ Archivo actualizado con {len(changes)} cambios")
        else:
            print("\n⚠️ No se encontraron referencias a 'velocity' para cambiar")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # También revisar motion_components.py para el alias
    print("\n🔧 Agregando alias en motion_components.py...")
    
    try:
        with open('trajectory_hub/core/motion_components.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar set_movement_mode en IndividualTrajectory
        in_class = False
        class_indent = 0
        
        for i, line in enumerate(lines):
            # Detectar clase IndividualTrajectory
            if 'class IndividualTrajectory' in line:
                in_class = True
                class_indent = len(line) - len(line.lstrip())
                continue
            
            # Si estamos en la clase
            if in_class:
                # Verificar si salimos de la clase
                if line.strip() and len(line) - len(line.lstrip()) <= class_indent:
                    if line.strip().startswith('class'):
                        in_class = False
                        continue
                
                # Buscar set_movement_mode
                if 'def set_movement_mode(self' in line:
                    print(f"✅ Encontrado set_movement_mode en línea {i+1}")
                    
                    # Buscar dónde insertar el código
                    # Típicamente después de los docstrings
                    j = i + 1
                    while j < len(lines) and (lines[j].strip().startswith('"""') or 
                                            lines[j].strip() == '' or 
                                            '"""' in lines[j]):
                        j += 1
                    
                    # Insertar el código de manejo de strings
                    indent = '        '  # 8 espacios para método de clase
                    alias_code = [
                        f"{indent}# Manejar strings y alias\n",
                        f"{indent}if isinstance(mode, str):\n",
                        f"{indent}    # Alias para compatibilidad\n",
                        f"{indent}    if mode == 'velocity':\n",
                        f"{indent}        mode = 'fix'\n",
                        f"{indent}    # Convertir string a enum\n",
                        f"{indent}    try:\n",
                        f"{indent}        mode = TrajectoryMovementMode(mode)\n",
                        f"{indent}    except ValueError:\n",
                        f"{indent}        # Por defecto usar FIX\n",
                        f"{indent}        mode = TrajectoryMovementMode.FIX\n",
                        f"\n"
                    ]
                    
                    # Verificar si ya existe este código
                    existing_code = ''.join(lines[j:j+20])
                    if 'if isinstance(mode, str)' not in existing_code:
                        lines[j:j] = alias_code
                        
                        # Guardar
                        with open('trajectory_hub/core/motion_components.py', 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        
                        print("✅ Alias agregado en motion_components.py")
                    else:
                        print("ℹ️ El alias ya existe")
                    
                    break
                    
    except Exception as e:
        print(f"❌ Error en motion_components: {e}")
    
    return True

def verify_fix():
    """Verificar que el fix funcionó"""
    
    print("\n\n🧪 VERIFICACIÓN RÁPIDA")
    print("="*50)
    
    try:
        from trajectory_hub.core.motion_components import IndividualTrajectory, MotionState
        import numpy as np
        
        # Test 1: Con string 'velocity'
        print("1. Test con mode='velocity':")
        traj = IndividualTrajectory()
        traj.set_trajectory('circle', center=np.array([0, 0, 0]), radius=1.0)
        
        try:
            traj.set_movement_mode('velocity', movement_speed=1.0)
            print("   ✅ 'velocity' aceptado (con alias)")
        except:
            print("   ❌ 'velocity' no funciona")
            
        # Test 2: Con string 'fix'
        print("\n2. Test con mode='fix':")
        traj2 = IndividualTrajectory()
        traj2.set_trajectory('circle', center=np.array([0, 0, 0]), radius=1.0)
        traj2.set_movement_mode('fix', movement_speed=1.0)
        
        # Verificar movimiento
        state = MotionState(position=np.array([0, 0, 0]))
        for i in range(3):
            state = traj2.update(state, i * 0.016, 0.016)
        
        if traj2.position_on_trajectory > 0:
            print("   ✅ Las trayectorias se mueven con 'fix'")
        else:
            print("   ❌ Las trayectorias NO se mueven")
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

if __name__ == "__main__":
    print("🔧 CORRECCIÓN MANUAL DE 'velocity' → 'fix'")
    print("="*70)
    
    # Aplicar correcciones
    find_and_fix_velocity_defaults()
    
    # Verificar
    verify_fix()
    
    print("\n" + "="*70)
    print("✅ Corrección completada")
    print("\nAhora ejecuta el controlador interactivo y prueba:")
    print("  - Opción 10: Trayectorias individuales")
    print("  - Opción 31: Control de concentración")