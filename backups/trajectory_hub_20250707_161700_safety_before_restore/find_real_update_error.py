#!/usr/bin/env python3
"""
find_real_update_error.py - Encuentra el verdadero origen del error update()
"""

import os
import re
import subprocess

def search_all_update_calls():
    """Buscar TODAS las llamadas a update en TODO el proyecto"""
    print("🔍 BÚSQUEDA EXHAUSTIVA DE update() EN TODO EL PROYECTO...\n")
    
    # Usar grep para buscar en todos los archivos Python
    cmd = "grep -n 'update(' trajectory_hub/**/*.py"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            
            # Filtrar resultados
            relevant_calls = []
            for line in lines:
                # Excluir definiciones de métodos
                if 'def update' not in line and 'Update' not in line:
                    # Buscar si tiene parámetros
                    if re.search(r'update\([^)]+\)', line):
                        relevant_calls.append(line)
            
            if relevant_calls:
                print(f"Encontradas {len(relevant_calls)} llamadas a update() con parámetros:\n")
                for call in relevant_calls[:20]:  # Primeras 20
                    print(f"  {call}")
                    
                return relevant_calls
    except Exception as e:
        print(f"Error ejecutando grep: {e}")
    
    return []

def check_engine_step_method():
    """Verificar el método step del engine"""
    print("\n\n🔍 VERIFICANDO MÉTODO step() DEL ENGINE...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(filepath):
        print(f"❌ No se encuentra {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método step
    pattern = r'def step\(self[^)]*\):(.*?)(?=\n    def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("✅ Encontrado método step():")
        print("-" * 60)
        
        method = match.group(0)
        lines = method.split('\n')[:30]
        
        for i, line in enumerate(lines):
            if 'update(' in line:
                print(f">>> {i}: {line}")
                if re.search(r'update\([^)]+\)', line):
                    print(f"    ⚠️  ESTA LÍNEA TIENE UPDATE CON PARÁMETROS")
            else:
                print(f"    {i}: {line}")
        
        print("-" * 60)
        
        # Buscar específicamente self.update
        if 'self.update(' in method:
            print("\n⚠️  step() llama a self.update()")
            
            # Ver si tiene parámetros
            update_calls = re.findall(r'self\.update\([^)]*\)', method)
            for call in update_calls:
                print(f"  Llamada encontrada: {call}")
                if call != "self.update()":
                    print(f"  ❌ PROBLEMA: {call} tiene parámetros")
                    return True
    else:
        print("❌ No se encontró método step()")
    
    return False

def fix_step_method():
    """Corregir el método step si es necesario"""
    print("\n\n🔧 CORRIGIENDO MÉTODO step()...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    from datetime import datetime
    backup_name = f"{filepath}.backup_step_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y corregir en step
    # Patrón más específico para step
    def fix_update_in_step(match):
        method_content = match.group(0)
        
        # Reemplazar update con parámetros
        fixed = re.sub(r'self\.update\([^)]+\)', 'self.update()', method_content)
        
        if fixed != method_content:
            print("✅ Corregido update() en step()")
        
        return fixed
    
    # Aplicar corrección
    pattern = r'(def step\(self[^)]*\):.*?)(?=\n    def|\nclass|\Z)'
    new_content = re.sub(pattern, fix_update_in_step, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Archivo actualizado")
        return True
    
    return False

def test_final():
    """Test final del sistema"""
    print("\n\n🧪 TEST FINAL...\n")
    
    test_code = '''import asyncio
from trajectory_hub import EnhancedTrajectoryEngine

async def test():
    engine = EnhancedTrajectoryEngine()
    
    # Test update
    print("Test update()...", end=" ")
    engine.update()
    print("✅")
    
    # Test step
    print("Test step()...", end=" ")
    state = engine.step()
    print("✅")
    
    print("\\n✅ TODO FUNCIONA CORRECTAMENTE")

asyncio.run(test())
'''
    
    # Ejecutar test
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"❌ Error en test:")
        print(result.stderr)
        return False

def main():
    print("="*70)
    print("🔍 BÚSQUEDA DEL VERDADERO ERROR DE UPDATE")
    print("="*70)
    
    # Buscar todas las llamadas
    calls = search_all_update_calls()
    
    # Verificar step
    has_problem = check_engine_step_method()
    
    if has_problem:
        # Corregir
        if fix_step_method():
            print("\n✅ Problema corregido en step()")
            
            # Verificar
            if test_final():
                print("\n" + "="*70)
                print("✅ SISTEMA COMPLETAMENTE CORREGIDO")
                print("\nAhora puedes usar:")
                print("  python -m trajectory_hub.interface.interactive_controller")
                print("\nLa opción 31 (Concentración) estará disponible")
        else:
            print("\n❌ No se pudo corregir automáticamente")
    else:
        print("\n⚠️  El problema puede estar en otro lugar")
        print("Posibles ubicaciones:")
        for call in calls[:5]:
            print(f"  - {call}")

if __name__ == "__main__":
    main()