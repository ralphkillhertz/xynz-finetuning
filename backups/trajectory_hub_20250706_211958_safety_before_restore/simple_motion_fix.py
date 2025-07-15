#!/usr/bin/env python3
"""
🔧 Fix simplificado: Corregir SOLO la línea problemática en SourceMotion
⚡ Busca component.update(time, dt, state) y lo cambia a component.update(state, time, dt)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def apply_simple_fix():
    """Aplicar corrección mínima al problema"""
    
    print("🔧 Aplicando corrección simple a motion_components.py...")
    
    try:
        # Leer archivo
        with open('trajectory_hub/core/motion_components.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar y corregir las líneas problemáticas
        fixed_count = 0
        for i, line in enumerate(lines):
            # Buscar líneas que llamen a component.update con parámetros incorrectos
            if 'component.update(' in line and 'time' in line and 'dt' in line and 'state' in line:
                # Si tiene el orden incorrecto (time, dt, state)
                if 'component.update(time, dt, state)' in line:
                    lines[i] = line.replace(
                        'component.update(time, dt, state)',
                        'component.update(state, time, dt)'
                    )
                    print(f"✅ Corregido en línea {i+1}: component.update(time, dt, state) → component.update(state, time, dt)")
                    fixed_count += 1
        
        if fixed_count == 0:
            # Buscar el patrón real en el método update de SourceMotion
            print("⚠️ Patrón exacto no encontrado. Buscando en método update...")
            
            in_update_method = False
            for i, line in enumerate(lines):
                # Detectar inicio del método update en SourceMotion
                if 'def update(self' in line and i > 0 and 'SourceMotion' in ''.join(lines[max(0, i-20):i]):
                    in_update_method = True
                    print(f"📍 Encontrado SourceMotion.update() en línea {i+1}")
                    continue
                
                # Si estamos en el método update
                if in_update_method:
                    # Fin del método
                    if line.strip() and not line.startswith(' '):
                        in_update_method = False
                        continue
                    
                    # Buscar la llamada a component.update
                    if 'component.update(' in line:
                        print(f"   Línea {i+1}: {line.strip()}")
                        
                        # Ver si necesita corrección
                        if 'state =' in line and 'component.update(' in line:
                            # Analizar los parámetros
                            if '(time, dt, state)' in line:
                                lines[i] = line.replace('(time, dt, state)', '(state, time, dt)')
                                print(f"   ✅ Corregido: (time, dt, state) → (state, time, dt)")
                                fixed_count += 1
                            elif 'time' in line and 'dt' in line:
                                # Puede ser otra variante, mostrar para análisis manual
                                print(f"   ⚠️ Revisar manualmente esta línea")
        
        if fixed_count > 0:
            # Guardar cambios
            with open('trajectory_hub/core/motion_components.py', 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"\n✅ {fixed_count} correcciones aplicadas")
            return True
        else:
            print("\n⚠️ No se encontraron líneas para corregir")
            print("Vamos a buscar el problema real...")
            
            # Mostrar el método update actual
            show_current_update_method()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_current_update_method():
    """Mostrar el método update actual de SourceMotion"""
    print("\n📄 MÉTODO UPDATE ACTUAL DE SOURCEMOTION:")
    print("-"*60)
    
    try:
        with open('trajectory_hub/core/motion_components.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        in_sourcemotion = False
        in_update = False
        indent_level = 0
        
        for i, line in enumerate(lines):
            # Detectar clase SourceMotion
            if 'class SourceMotion' in line:
                in_sourcemotion = True
                continue
            
            if in_sourcemotion:
                # Detectar método update
                if 'def update(self' in line:
                    in_update = True
                    indent_level = len(line) - len(line.lstrip())
                
                if in_update:
                    print(f"{i+1:4d}: {line.rstrip()}")
                    
                    # Detectar fin del método
                    if line.strip() and len(line) - len(line.lstrip()) <= indent_level and 'def ' in line and 'update' not in line:
                        break
                    
                # Detectar fin de la clase
                if line.strip() and not line.startswith(' '):
                    if in_update:
                        break
                    in_sourcemotion = False
                    
    except Exception as e:
        print(f"Error: {e}")

def create_manual_fix():
    """Crear un fix manual basado en lo que vemos"""
    print("\n💡 CREANDO FIX MANUAL")
    print("="*60)
    
    fix_code = '''
# CORRECCIÓN MANUAL PARA motion_components.py
# Buscar en el método update de SourceMotion la línea:
#     state = component.update(time, dt, state)
# Y cambiarla por:
#     state = component.update(state, time, dt)

# O si el código es diferente, asegurarse de que IndividualTrajectory
# reciba los parámetros en el orden correcto: (state, time, dt)
'''
    
    print(fix_code)

if __name__ == "__main__":
    print("🚀 FIX SIMPLE DE MOTION COMPONENTS")
    print("="*60)
    
    if not apply_simple_fix():
        create_manual_fix()