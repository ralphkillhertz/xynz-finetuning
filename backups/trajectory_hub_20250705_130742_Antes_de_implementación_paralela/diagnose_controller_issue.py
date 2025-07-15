#!/usr/bin/env python3
"""
diagnose_controller_issue.py - Diagnostica y corrige el problema del controlador
"""

import os
import re
from datetime import datetime

def find_update_loop():
    """Buscar dónde está el update_loop que causa el error"""
    print("🔍 BUSCANDO UPDATE_LOOP...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar update_loop
    update_loop_match = re.search(r'async def update_loop\(self\):(.*?)(?=\n    async def|\n    def|\nclass|\Z)', 
                                  content, re.DOTALL)
    
    if update_loop_match:
        print("✅ Encontrado update_loop:")
        print("-" * 60)
        lines = update_loop_match.group(0).split('\n')[:30]
        for i, line in enumerate(lines):
            if 'update(' in line.lower():
                print(f">>> {i}: {line}")
            else:
                print(f"    {i}: {line}")
        print("-" * 60)
        
        # Buscar específicamente la línea del error
        if 'self.engine.update(dt)' in update_loop_match.group(0):
            print("\n❌ ENCONTRADO: self.engine.update(dt)")
            return True, "dt"
        elif 'self.engine.update(self.dt)' in update_loop_match.group(0):
            print("\n❌ ENCONTRADO: self.engine.update(self.dt)")
            return True, "self.dt"
        elif re.search(r'self\.engine\.update\([^)]+\)', update_loop_match.group(0)):
            print("\n❌ ENCONTRADO: update con parámetros")
            return True, "params"
    
    # Buscar en el método run
    run_match = re.search(r'async def run\(self\):(.*?)(?=\n    async def|\n    def|\nclass|\Z)', 
                          content, re.DOTALL)
    
    if run_match and 'update(' in run_match.group(0):
        print("\n🔍 Buscando en método run():")
        if 'self.engine.update(dt)' in run_match.group(0):
            print("❌ ENCONTRADO en run(): self.engine.update(dt)")
            return True, "run_dt"
    
    return False, None

def check_init_method():
    """Verificar el método __init__ del controlador"""
    print("\n🔍 VERIFICANDO __init__...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar __init__
    init_match = re.search(r'def __init__\(self[^)]*\):', content)
    
    if init_match:
        print(f"Firma encontrada: {init_match.group(0)}")
        
        # Ver si espera parámetros
        if "def __init__(self):" in content:
            print("✅ __init__ no espera parámetros (crea su propio engine)")
            return "no_params"
        elif "def __init__(self, engine" in content:
            print("✅ __init__ espera un engine como parámetro")
            return "expects_engine"
    
    return None

def fix_all_update_calls():
    """Corregir TODAS las llamadas a update, incluyendo en métodos anidados"""
    print("\n🔧 CORRIGIENDO TODAS LAS LLAMADAS A UPDATE...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    # Backup
    backup_name = f"{filepath}.backup_allupdate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todas las ocurrencias de update con parámetros
    # Ser más agresivo en la búsqueda
    patterns = [
        # Variaciones con self.engine
        (r'self\.engine\.update\(\s*dt\s*\)', 'self.engine.update()'),
        (r'self\.engine\.update\(\s*self\.dt\s*\)', 'self.engine.update()'),
        (r'self\.engine\.update\(\s*[^)]+\s*\)', 'self.engine.update()'),
        # Variaciones sin self
        (r'engine\.update\(\s*dt\s*\)', 'engine.update()'),
        (r'engine\.update\(\s*[^)]+\s*\)', 'engine.update()'),
        # En el update_loop específicamente
        (r'(\s+)self\.engine\.update\(dt\)', r'\1self.engine.update()'),
        (r'(\s+)await self\.engine\.update\(dt\)', r'\1await self.engine.update()'),
    ]
    
    total_changes = 0
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            total_changes += len(matches)
            print(f"  ✓ Reemplazado: {pattern} ({len(matches)} veces)")
    
    # Buscar específicamente en update_loop
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'update_loop' in line:
            # Buscar en las siguientes 50 líneas
            for j in range(i, min(i+50, len(lines))):
                if 'self.engine.update(' in lines[j] and 'self.engine.update()' not in lines[j]:
                    print(f"\n⚠️  Línea {j+1} todavía tiene update con parámetros:")
                    print(f"    {lines[j]}")
                    lines[j] = lines[j].replace('self.engine.update(dt)', 'self.engine.update()')
                    lines[j] = lines[j].replace('self.engine.update(self.dt)', 'self.engine.update()')
                    total_changes += 1
    
    if total_changes > 0:
        # Reconstruir contenido
        content = '\n'.join(lines)
        
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Total de cambios realizados: {total_changes}")
    else:
        print("\n⚠️  No se encontraron más llamadas para corregir")
    
    return total_changes > 0

def create_minimal_controller_test():
    """Crear un test mínimo del controlador"""
    test_code = '''#!/usr/bin/env python3
"""
test_controller_minimal.py - Test mínimo del controlador
"""

import sys
import asyncio

print("🔍 TEST MÍNIMO DEL CONTROLADOR\\n")

# Test 1: Importar
try:
    from trajectory_hub.interface.interactive_controller import InteractiveController
    print("✅ InteractiveController importado")
except Exception as e:
    print(f"❌ Error al importar: {e}")
    sys.exit(1)

# Test 2: Ver firma de __init__
import inspect
sig = inspect.signature(InteractiveController.__init__)
print(f"\\nFirma de __init__: {sig}")

# Test 3: Crear instancia
try:
    # Intentar sin parámetros
    print("\\nIntentando crear sin parámetros...")
    controller = InteractiveController()
    print("✅ Controlador creado sin parámetros")
except TypeError as e:
    print(f"❌ Error: {e}")
    
    # Intentar con engine
    try:
        print("\\nIntentando crear con engine...")
        from trajectory_hub import EnhancedTrajectoryEngine
        engine = EnhancedTrajectoryEngine()
        controller = InteractiveController(engine)
        print("✅ Controlador creado con engine")
    except Exception as e2:
        print(f"❌ Error: {e2}")
        sys.exit(1)

# Test 4: Verificar que tiene engine
if hasattr(controller, 'engine'):
    print(f"\\n✅ Controlador tiene engine: {type(controller.engine)}")
    
    # Test update
    try:
        controller.engine.update()
        print("✅ engine.update() funciona sin parámetros")
    except Exception as e:
        print(f"❌ Error en update: {e}")

print("\\n✅ TESTS BÁSICOS COMPLETADOS")
'''
    
    with open("test_controller_minimal.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("\n✅ test_controller_minimal.py creado")

def main():
    print("="*60)
    print("🔍 DIAGNÓSTICO DEL PROBLEMA DEL CONTROLADOR")
    print("="*60)
    
    # 1. Buscar el problema en update_loop
    found, location = find_update_loop()
    
    # 2. Verificar __init__
    init_type = check_init_method()
    
    # 3. Aplicar correcciones
    if found:
        print("\n" + "="*60)
        print("🔧 APLICANDO CORRECCIONES")
        print("="*60)
        
        if fix_all_update_calls():
            print("\n✅ Correcciones aplicadas")
        else:
            print("\n⚠️  Puede que necesites revisar manualmente")
    
    # 4. Crear test
    create_minimal_controller_test()
    
    print("\n" + "="*60)
    print("RESUMEN:")
    print(f"- Update loop: {'Encontrado y corregido' if found else 'No encontrado'}")
    print(f"- Constructor: {init_type}")
    print("\nPróximos pasos:")
    print("1. Ejecuta: python test_controller_minimal.py")
    print("2. Si funciona, ejecuta el controlador:")
    print("   python -m trajectory_hub.interface.interactive_controller")

if __name__ == "__main__":
    main()