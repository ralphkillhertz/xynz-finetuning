#!/usr/bin/env python3
"""
fix_dt_reference.py - Corrige las referencias a dt en el método update
"""

import os
import re
from datetime import datetime

def fix_dt_references():
    """Corregir todas las referencias a dt en update()"""
    print("🔧 CORRIGIENDO REFERENCIAS A dt...\n")
    
    filepath = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Backup
    backup_name = f"{filepath}.backup_dt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp '{filepath}' '{backup_name}'")
    print(f"✅ Backup creado: {backup_name}")
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar el método update
    update_start = content.find("def update(self)")
    if update_start == -1:
        print("❌ No se encontró def update(self)")
        return False
    
    # Encontrar el siguiente método (para saber dónde termina update)
    next_method = content.find("\n    def ", update_start + 1)
    if next_method == -1:
        # Si no hay siguiente método, buscar el final de la clase
        next_method = content.find("\nclass ", update_start)
        if next_method == -1:
            next_method = len(content)
    
    # Extraer el método update completo
    update_method = content[update_start:next_method]
    
    # Contar referencias a dt
    dt_count = update_method.count("dt)")
    dt_count += update_method.count("dt,")
    dt_count += update_method.count("dt ")
    dt_count += update_method.count("(dt")
    
    print(f"Encontradas {dt_count} referencias a 'dt' en update()")
    
    # Reemplazar dt por self.dt
    # Pero solo cuando dt no es parte de otra palabra
    original_update = update_method
    
    # Patrones a reemplazar
    replacements = [
        (r'\(dt\)', '(self.dt)'),
        (r', dt\)', ', self.dt)'),
        (r'\(dt,', '(self.dt,'),
        (r', dt,', ', self.dt,'),
        (r' dt ', ' self.dt '),
        (r' dt\n', ' self.dt\n'),
        (r'_apply_algorithmic_rotations\(dt\)', '_apply_algorithmic_rotations(self.dt)'),
        (r'motion\.update\(self\._time, dt\)', 'motion.update(self._time, self.dt)'),
        (r'update_positions\(dt\)', 'update_positions(self.dt)'),
        (r'deform\(.*?, dt\)', lambda m: m.group(0).replace(', dt)', ', self.dt)')),
    ]
    
    for pattern, replacement in replacements:
        if callable(replacement):
            update_method = re.sub(pattern, replacement, update_method)
        else:
            update_method = re.sub(pattern, replacement, update_method)
    
    # Verificar que no reemplazamos self.self.dt
    update_method = update_method.replace("self.self.dt", "self.dt")
    
    # Reconstruir el contenido
    new_content = content[:update_start] + update_method + content[next_method:]
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Referencias a dt corregidas")
    
    # Mostrar algunos cambios
    print("\nEjemplos de cambios:")
    lines_original = original_update.split('\n')
    lines_new = update_method.split('\n')
    
    changes_shown = 0
    for i, (orig, new) in enumerate(zip(lines_original, lines_new)):
        if orig != new and changes_shown < 5:
            print(f"\n  Línea {i}:")
            print(f"  - Antes:   {orig.strip()}")
            print(f"  + Después: {new.strip()}")
            changes_shown += 1
    
    return True

def verify_update_works():
    """Verificar que update() funciona ahora"""
    print("\n\n🔍 VERIFICANDO QUE UPDATE FUNCIONA...\n")
    
    try:
        from trajectory_hub import EnhancedTrajectoryEngine
        
        # Crear engine
        engine = EnhancedTrajectoryEngine()
        
        # Crear una fuente simple
        engine.create_source(0, "test")
        
        # Intentar update
        print("Llamando a engine.update()...")
        engine.update()
        print("✅ update() funciona sin errores")
        
        # Verificar que el tiempo avanza
        initial_time = engine._time
        for i in range(5):
            engine.update()
        
        if engine._time > initial_time:
            print(f"✅ El tiempo avanza correctamente: {initial_time:.3f} → {engine._time:.3f}")
        else:
            print("❌ El tiempo no avanza")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_test():
    """Crear test simple para verificar"""
    test_code = '''#!/usr/bin/env python3
"""
test_concentration_simple.py - Test simple del sistema
"""

from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST SIMPLE DE CONCENTRACIÓN\\n")

# Crear engine
engine = EnhancedTrajectoryEngine()
print("✅ Engine creado")

# Crear macro
macro_id = engine.create_macro("test", 5, formation="circle")
print(f"✅ Macro creado: {macro_id}")

# Establecer concentración
engine.set_macro_concentration(macro_id, 0.0)  # Totalmente concentrado
print("✅ Concentración establecida en 0.0")

# Updates
print("\\nEjecutando updates...")
for i in range(10):
    engine.update()
    if i % 3 == 0:
        state = engine.get_macro_concentration_state(macro_id)
        print(f"  Frame {i}: factor={state.get('factor', 'N/A')}")

print("\\n✅ TEST COMPLETADO SIN ERRORES")
'''
    
    with open("test_concentration_simple.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("\n✅ test_concentration_simple.py creado")

def main():
    print("="*60)
    print("🔧 CORRIGIENDO REFERENCIAS A dt EN UPDATE")
    print("="*60)
    
    # Corregir referencias
    if fix_dt_references():
        # Verificar
        if verify_update_works():
            create_simple_test()
            
            print("\n" + "="*60)
            print("✅ PROBLEMA RESUELTO")
            print("\nAhora puedes ejecutar:")
            print("  python test_concentration_simple.py")
            print("  python test_concentration_final.py")
            print("\nO usar el controlador interactivo:")
            print("  python -m trajectory_hub.interface.interactive_controller")
            print("  (Opción 31 para concentración)")
        else:
            print("\n⚠️  update() todavía tiene problemas")
            print("Revisa manualmente el método")
    else:
        print("\n❌ No se pudieron corregir las referencias")

if __name__ == "__main__":
    main()