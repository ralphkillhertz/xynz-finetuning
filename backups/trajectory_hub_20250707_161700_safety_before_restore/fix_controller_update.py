#!/usr/bin/env python3
"""
fix_controller_update.py - Corrige la llamada a update() en el controlador
"""

import os
import re
from datetime import datetime

def fix_controller_update_calls():
    """Corregir todas las llamadas a engine.update(dt) en el controlador"""
    print("🔧 CORRIGIENDO LLAMADAS A UPDATE EN EL CONTROLADOR...\n")
    
    filepath = "trajectory_hub/interface/interactive_controller.py"
    
    if not os.path.exists(filepath):
        print(f"❌ No se encuentra {filepath}")
        return False
    
    # Backup
    backup_name = f"{filepath}.backup_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Contar llamadas a update con parámetro
    update_calls = len(re.findall(r'engine\.update\([^)]+\)', content))
    print(f"Encontradas {update_calls} llamadas a engine.update() con parámetros")
    
    # Reemplazar todas las variantes
    patterns = [
        (r'self\.engine\.update\(dt\)', 'self.engine.update()'),
        (r'self\.engine\.update\(self\.dt\)', 'self.engine.update()'),
        (r'self\.engine\.update\([^)]+\)', 'self.engine.update()'),
        (r'engine\.update\(dt\)', 'engine.update()'),
        (r'engine\.update\([^)]+\)', 'engine.update()'),
    ]
    
    changes_made = 0
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_made += len(matches)
            print(f"  ✓ Reemplazado: {pattern} → {replacement} ({len(matches)} veces)")
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ {changes_made} cambios realizados")
    
    # Buscar el método update_loop específicamente
    update_loop_pos = content.find("async def update_loop")
    if update_loop_pos != -1:
        # Mostrar contexto
        print("\n📋 Contexto del update_loop:")
        print("-" * 50)
        start = update_loop_pos
        end = content.find("\n    async def", update_loop_pos + 1)
        if end == -1:
            end = update_loop_pos + 1000
        
        lines = content[start:end].split('\n')[:20]
        for i, line in enumerate(lines):
            if "update()" in line:
                print(f">>> {line}")
            else:
                print(f"    {line}")
    
    return True

def verify_fix():
    """Verificar que el controlador puede iniciar sin errores"""
    print("\n\n🔍 VERIFICANDO FIX...\n")
    
    try:
        # Importar el controlador
        from trajectory_hub.interface.interactive_controller import InteractiveController
        from trajectory_hub import EnhancedTrajectoryEngine
        
        # Crear instancias
        print("Creando engine...")
        engine = EnhancedTrajectoryEngine()
        
        print("Creando controlador...")
        controller = InteractiveController(engine)
        
        # Verificar que update funciona
        print("Probando engine.update()...")
        engine.update()  # Sin parámetros
        
        print("✅ El controlador se puede instanciar sin errores")
        print("✅ engine.update() funciona sin parámetros")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_controller_test():
    """Crear un test para el controlador con concentración"""
    test_code = '''#!/usr/bin/env python3
"""
test_controller_concentration.py - Test del controlador con concentración
"""

import asyncio
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController

async def test_concentration_menu():
    """Simular el uso del menú de concentración"""
    print("🎮 TEST DEL MENÚ DE CONCENTRACIÓN\\n")
    
    # Crear engine y controlador
    engine = EnhancedTrajectoryEngine()
    controller = InteractiveController(engine)
    
    # Crear un macro
    print("1. Creando macro de prueba...")
    macro_id = engine.create_macro("test_menu", 10, formation="circle")
    controller.macros["Test Menu"] = macro_id
    print(f"   ✅ Macro creado: {macro_id}")
    
    # Establecer concentración directamente
    print("\\n2. Probando concentración...")
    engine.set_macro_concentration(macro_id, 0.5)
    
    # Verificar estado
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✅ Factor: {state['factor']}")
    print(f"   ✅ Habilitado: {state['enabled']}")
    
    # Simular algunos updates
    print("\\n3. Ejecutando updates...")
    for i in range(10):
        engine.update()  # Sin parámetros
    print("   ✅ Updates ejecutados sin errores")
    
    print("\\n✅ TEST COMPLETADO")
    print("\\nEl menú de concentración está disponible:")
    print("- Ejecuta el controlador interactivo")
    print("- Selecciona opción 31")

if __name__ == "__main__":
    asyncio.run(test_concentration_menu())
'''
    
    with open("test_controller_concentration.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("\n✅ test_controller_concentration.py creado")

def main():
    print("="*60)
    print("🔧 FIX PARA UPDATE EN EL CONTROLADOR")
    print("="*60)
    
    # Aplicar correcciones
    if fix_controller_update_calls():
        # Verificar
        if verify_fix():
            create_controller_test()
            
            print("\n" + "="*60)
            print("✅ PROBLEMA RESUELTO")
            print("\nAhora puedes:")
            print("1. Ejecutar el controlador interactivo:")
            print("   python -m trajectory_hub.interface.interactive_controller")
            print("\n2. Usar la opción 31 para concentración")
            print("\n3. Probar con:")
            print("   python test_controller_concentration.py")
        else:
            print("\n⚠️  El fix se aplicó pero puede haber otros problemas")
    else:
        print("\n❌ No se pudo aplicar el fix")

if __name__ == "__main__":
    main()