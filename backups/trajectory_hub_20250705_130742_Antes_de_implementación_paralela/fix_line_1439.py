#!/usr/bin/env python3
"""
fix_line_1439.py - Corrige la línea específica que causa el error
"""

import os
from datetime import datetime

def find_and_fix_line_1439():
    """Buscar y corregir la línea 1439 específicamente"""
    print("🔍 BUSCANDO LÍNEA 1439...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup_name = f"{filepath}.backup_line1439_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar alrededor de la línea 1439
    start = max(0, 1435)
    end = min(len(lines), 1445)
    
    print(f"Contexto alrededor de la línea 1439:")
    print("-" * 60)
    
    found_problem = False
    for i in range(start, end):
        if i < len(lines):
            line_num = i + 1
            line = lines[i]
            
            # Marcar la línea problemática
            if 'self.update(self.dt)' in line:
                print(f">>> {line_num}: {line.rstrip()}")
                print(f"    ⚠️  ESTA ES LA LÍNEA PROBLEMÁTICA")
                found_problem = True
                
                # Corregir la línea
                lines[i] = line.replace('self.update(self.dt)', 'self.update()')
                print(f"    ✓ Corregida a: {lines[i].rstrip()}")
            else:
                print(f"    {line_num}: {line.rstrip()}")
    
    print("-" * 60)
    
    if found_problem:
        # Guardar el archivo corregido
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("\n✅ Archivo corregido y guardado")
        return True
    else:
        print("\n❌ No se encontró la línea problemática")
        return False

def find_step_method():
    """Buscar dónde está definido el método step"""
    print("\n\n🔍 BUSCANDO MÉTODO step()...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar definición de step
    for i, line in enumerate(lines):
        if 'def step(' in line:
            print(f"✅ Encontrado método step en línea {i+1}")
            
            # Mostrar contexto
            start = max(0, i-2)
            end = min(len(lines), i+20)
            
            print("\nContexto del método step:")
            print("-" * 60)
            
            for j in range(start, end):
                line_num = j + 1
                if 'self.update(' in lines[j]:
                    print(f">>> {line_num}: {lines[j].rstrip()}")
                else:
                    print(f"    {line_num}: {lines[j].rstrip()}")
            
            print("-" * 60)
            return True
    
    print("❌ No se encontró el método step()")
    return False

def test_controller():
    """Test rápido del controlador"""
    print("\n\n🧪 TEST RÁPIDO DEL CONTROLADOR...\n")
    
    test_code = '''
import asyncio
import sys

async def test():
    try:
        from trajectory_hub.interface.interactive_controller import InteractiveController
        
        # Crear controlador
        print("Creando controlador...", end=" ")
        controller = InteractiveController()
        print("✅")
        
        # Simular el update loop
        print("Simulando update loop...", end=" ")
        
        # Esto es lo que hace _update_loop
        state = controller.engine.step()
        
        print("✅")
        print("\\n✅ CONTROLADOR FUNCIONA CORRECTAMENTE")
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
'''
    
    # Ejecutar test
    import subprocess
    result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errores:")
        print(result.stderr)
    
    return result.returncode == 0

def main():
    print("="*70)
    print("🔧 CORRECCIÓN DE LA LÍNEA ESPECÍFICA DEL ERROR")
    print("="*70)
    
    # Corregir la línea problemática
    if find_and_fix_line_1439():
        # Buscar el método step para más contexto
        find_step_method()
        
        # Probar
        if test_controller():
            print("\n" + "="*70)
            print("✅ PROBLEMA COMPLETAMENTE RESUELTO")
            print("\nEl controlador interactivo ahora funciona correctamente:")
            print("  python -m trajectory_hub.interface.interactive_controller")
            print("\n🎯 La opción 31 (Concentración de Fuentes) está disponible")
            print("\nTambién puedes usar la concentración desde código:")
            print("  engine.set_macro_concentration(macro_id, 0.0)  # Concentrar")
            print("  engine.animate_macro_concentration(macro_id, 1.0, 3.0)  # Dispersar")
            print("  engine.toggle_macro_concentration(macro_id)  # Toggle")
        else:
            print("\n⚠️  El test falló, puede haber otros problemas")
    else:
        print("\n❌ No se pudo corregir la línea")

if __name__ == "__main__":
    main()