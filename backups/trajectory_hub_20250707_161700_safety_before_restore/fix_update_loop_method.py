#!/usr/bin/env python3
"""
fix_update_loop_method.py - Encuentra y corrige el método _update_loop
"""

import os
import re
from datetime import datetime

def find_update_loop_method():
    """Buscar el método _update_loop que causa el problema"""
    print("🔍 BUSCANDO MÉTODO _update_loop...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar _update_loop
    pattern = r'async def _update_loop\(self\):(.*?)(?=\n    async def|\n    def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("✅ Encontrado método _update_loop:")
        print("-" * 70)
        
        method_content = match.group(0)
        lines = method_content.split('\n')
        
        for i, line in enumerate(lines[:50]):  # Primeras 50 líneas
            if 'update(' in line:
                print(f">>> Línea {i}: {line}")
                
                # Verificar si tiene parámetros
                if re.search(r'update\([^)]+\)', line):
                    print(f"    ⚠️  ESTA ES LA LÍNEA PROBLEMÁTICA")
            else:
                print(f"    Línea {i}: {line}")
        
        print("-" * 70)
        return True, method_content
    else:
        print("❌ No se encontró _update_loop")
        return False, None

def fix_update_loop():
    """Corregir el método _update_loop"""
    print("\n🔧 CORRIGIENDO _update_loop...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    # Backup
    backup_name = f"{filepath}.backup_updateloop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrones específicos para _update_loop
    # Buscar dentro del contexto del método
    pattern = r'(async def _update_loop\(self\):.*?)(self\.engine\.update\([^)]*\))'
    
    def replace_update(match):
        method_start = match.group(1)
        update_call = match.group(2)
        
        # Reemplazar cualquier update con parámetros por update sin parámetros
        new_update = 'self.engine.update()'
        
        print(f"  Reemplazando: {update_call}")
        print(f"  Por: {new_update}")
        
        return method_start + new_update
    
    # Aplicar el reemplazo
    new_content = re.sub(pattern, replace_update, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("\n✅ Corrección aplicada")
        return True
    else:
        # Intentar un enfoque más directo
        print("Intentando corrección directa...")
        
        # Buscar líneas específicas en _update_loop
        lines = content.split('\n')
        in_update_loop = False
        changes = 0
        
        for i, line in enumerate(lines):
            if 'async def _update_loop(self):' in line:
                in_update_loop = True
                indent = len(line) - len(line.lstrip())
            elif in_update_loop and line.strip() and not line.startswith(' ' * (indent + 1)):
                # Salimos del método
                in_update_loop = False
            elif in_update_loop and 'self.engine.update(' in line:
                # Esta es la línea problemática
                print(f"\n  Línea {i+1}: {line.strip()}")
                
                # Corregir la línea
                new_line = re.sub(r'self\.engine\.update\([^)]*\)', 'self.engine.update()', line)
                
                if new_line != line:
                    lines[i] = new_line
                    changes += 1
                    print(f"  Corregida a: {new_line.strip()}")
        
        if changes > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f"\n✅ {changes} líneas corregidas")
            return True
    
    return False

def verify_fix():
    """Verificar que la corrección funcionó"""
    print("\n🔍 VERIFICANDO CORRECCIÓN...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar en _update_loop
    pattern = r'async def _update_loop\(self\):(.*?)(?=\n    async def|\n    def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        method_content = match.group(1)
        
        # Buscar llamadas a update con parámetros
        update_calls = re.findall(r'self\.engine\.update\([^)]+\)', method_content)
        
        if update_calls:
            print(f"❌ Todavía hay {len(update_calls)} llamadas con parámetros:")
            for call in update_calls:
                print(f"  - {call}")
            return False
        else:
            print("✅ No hay llamadas a update con parámetros en _update_loop")
            
            # Verificar que hay llamadas sin parámetros
            clean_calls = re.findall(r'self\.engine\.update\(\)', method_content)
            print(f"✅ Hay {len(clean_calls)} llamadas correctas a update()")
            return True
    
    return False

def main():
    print("="*70)
    print("🔧 CORRECCIÓN ESPECÍFICA DE _update_loop")
    print("="*70)
    
    # Buscar el método
    found, content = find_update_loop_method()
    
    if found:
        # Corregir
        if fix_update_loop():
            # Verificar
            if verify_fix():
                print("\n" + "="*70)
                print("✅ PROBLEMA RESUELTO")
                print("\nAhora el controlador debería funcionar correctamente:")
                print("  python -m trajectory_hub.interface.interactive_controller")
                print("\nLa opción 31 estará disponible para concentración")
            else:
                print("\n⚠️  La corrección puede no estar completa")
                print("Revisa manualmente el método _update_loop")
        else:
            print("\n❌ No se pudo aplicar la corrección")
    else:
        print("\n❌ No se encontró el método _update_loop")
        print("El problema puede estar en otro lugar")

if __name__ == "__main__":
    main()