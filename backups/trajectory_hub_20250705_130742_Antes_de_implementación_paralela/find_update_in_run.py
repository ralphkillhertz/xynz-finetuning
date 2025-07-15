#!/usr/bin/env python3
"""
find_update_in_run.py - Encuentra y corrige la llamada a update en el método run
"""

import os
import re
from datetime import datetime

def find_update_in_controller():
    """Buscar TODAS las llamadas a update en el controlador"""
    print("🔍 BUSCANDO TODAS LAS LLAMADAS A UPDATE...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar todas las líneas con "update("
    update_calls = []
    for i, line in enumerate(lines):
        if '.update(' in line and 'def update' not in line:
            update_calls.append((i+1, line.strip()))
    
    if update_calls:
        print(f"Encontradas {len(update_calls)} llamadas a update():\n")
        for line_num, line in update_calls:
            print(f"  Línea {line_num}: {line}")
            
            # Ver si tiene parámetros
            if re.search(r'\.update\([^)]+\)', line):
                print(f"    ⚠️  TIENE PARÁMETROS")
            else:
                print(f"    ✅ Sin parámetros")
    
    # Buscar específicamente en create_task o asyncio
    print("\n\n🔍 BUSCANDO EN TAREAS ASÍNCRONAS...\n")
    
    task_lines = []
    for i, line in enumerate(lines):
        if 'create_task' in line or 'asyncio' in line:
            # Mirar las siguientes líneas también
            context = lines[max(0, i-2):min(len(lines), i+3)]
            for j, ctx_line in enumerate(context):
                if 'update' in ctx_line:
                    task_lines.append((i+j-1, ctx_line.strip()))
    
    if task_lines:
        print("Encontradas en contexto de tareas:")
        for line_num, line in task_lines:
            print(f"  Línea {line_num}: {line}")
    
    # Buscar el método run específicamente
    print("\n\n🔍 ANALIZANDO MÉTODO RUN...\n")
    
    run_start = -1
    for i, line in enumerate(lines):
        if 'async def run(self):' in line:
            run_start = i
            break
    
    if run_start != -1:
        print(f"Método run() encontrado en línea {run_start+1}")
        
        # Buscar el final del método
        indent_level = len(lines[run_start]) - len(lines[run_start].lstrip())
        run_end = len(lines)
        
        for i in range(run_start + 1, len(lines)):
            line = lines[i]
            if line.strip() and not line.startswith(' ' * (indent_level + 1)):
                run_end = i
                break
        
        # Analizar el método run
        run_method = lines[run_start:run_end]
        print(f"\nContenido del método run() ({len(run_method)} líneas):")
        print("-" * 60)
        
        for i, line in enumerate(run_method[:30]):  # Primeras 30 líneas
            if 'update' in line:
                print(f">>> {run_start+i+1}: {line.rstrip()}")
            elif 'create_task' in line or 'dt' in line:
                print(f"!!! {run_start+i+1}: {line.rstrip()}")
            else:
                print(f"    {run_start+i+1}: {line.rstrip()}")
    
    return update_calls

def fix_specific_update_calls():
    """Corregir las llamadas específicas encontradas"""
    print("\n\n🔧 APLICANDO CORRECCIONES ESPECÍFICAS...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    # Backup
    backup_name = f"{filepath}.backup_specific_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrones más específicos para el método run
    patterns = [
        # En lambdas o tasks
        (r'lambda: self\.engine\.update\(dt\)', 'lambda: self.engine.update()'),
        (r'lambda: self\.engine\.update\([^)]+\)', 'lambda: self.engine.update()'),
        # En el bucle principal
        (r'await self\.engine\.update\(dt\)', 'await self.engine.update()'),
        (r'self\.engine\.update\(dt\)', 'self.engine.update()'),
        # Con self.dt
        (r'self\.engine\.update\(self\.dt\)', 'self.engine.update()'),
        # En general
        (r'\.update\(dt\)', '.update()'),
        (r'\.update\(self\.dt\)', '.update()'),
    ]
    
    changes = 0
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes += len(matches)
            print(f"  ✓ Reemplazado: {pattern} ({len(matches)} veces)")
    
    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Total: {changes} cambios aplicados")
    else:
        print("\n⚠️  No se encontraron más patrones para corregir")
    
    # Verificación manual línea por línea
    print("\n🔍 VERIFICACIÓN MANUAL...\n")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    manual_fixes = 0
    for i, line in enumerate(lines):
        if '.update(' in line and 'def update' not in line:
            # Verificar si tiene parámetros
            if re.search(r'\.update\([^)]+\)', line):
                print(f"  Línea {i+1} todavía tiene parámetros: {line.strip()}")
                
                # Corregir manualmente
                new_line = re.sub(r'\.update\([^)]+\)', '.update()', line)
                if new_line != line:
                    lines[i] = new_line
                    manual_fixes += 1
                    print(f"  ✓ Corregido a: {new_line.strip()}")
    
    if manual_fixes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"\n✅ {manual_fixes} correcciones manuales adicionales")
    
    return changes + manual_fixes

def create_run_test():
    """Crear test específico para el método run"""
    test_code = '''#!/usr/bin/env python3
"""
test_controller_run.py - Test del método run del controlador
"""

import asyncio
import sys

async def test_run():
    print("🔍 TEST DEL MÉTODO RUN\\n")
    
    # Importar
    from trajectory_hub.interface.interactive_controller import InteractiveController
    
    # Crear controlador
    print("1. Creando controlador...")
    controller = InteractiveController()
    print("   ✅ Controlador creado")
    
    # Crear un macro para tener algo que actualizar
    print("\\n2. Creando macro de prueba...")
    macro_id = controller.engine.create_macro("test", 5)
    controller.macros["Test"] = macro_id
    print("   ✅ Macro creado")
    
    # Simular parte del run loop
    print("\\n3. Simulando bucle de actualización...")
    
    error_count = 0
    max_errors = 5
    
    for i in range(10):
        try:
            # Esto es lo que hace el controlador
            controller.engine.update()
            print(f"   ✓ Update {i+1} exitoso")
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error en update {i+1}: {e}")
            if error_count >= max_errors:
                print("   ❌ Demasiados errores, deteniendo")
                break
    
    if error_count == 0:
        print("\\n✅ BUCLE DE ACTUALIZACIÓN FUNCIONA CORRECTAMENTE")
    else:
        print(f"\\n❌ Hubo {error_count} errores")
    
    # Test del método step si existe
    if hasattr(controller, 'step'):
        print("\\n4. Probando step()...")
        try:
            controller.step()
            print("   ✅ step() funciona")
        except Exception as e:
            print(f"   ❌ Error en step(): {e}")

if __name__ == "__main__":
    asyncio.run(test_run())
'''
    
    with open("test_controller_run.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("\n✅ test_controller_run.py creado")

def main():
    print("="*60)
    print("🔍 BÚSQUEDA EXHAUSTIVA DE UPDATE CON PARÁMETROS")
    print("="*60)
    
    # Buscar todas las llamadas
    update_calls = find_update_in_controller()
    
    # Aplicar correcciones
    fixes = fix_specific_update_calls()
    
    # Crear test
    create_run_test()
    
    print("\n" + "="*60)
    print("RESUMEN:")
    print(f"- Llamadas a update encontradas: {len(update_calls)}")
    print(f"- Correcciones aplicadas: {fixes}")
    print("\nPróximos pasos:")
    print("1. Ejecuta: python test_controller_run.py")
    print("2. Si funciona, ejecuta el controlador:")
    print("   python -m trajectory_hub.interface.interactive_controller")

if __name__ == "__main__":
    main()