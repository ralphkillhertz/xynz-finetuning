# === fix_update_method_now.py ===
# 🔧 Fix directo del método update
# ⚡ Sin complicaciones de strings

import os
import re

def fix_update_method():
    """Arreglar el método update directamente"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    if not os.path.exists(file_path):
        print(f"❌ No se encontró {file_path}")
        return False
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_update_fix', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar el método update y el loop problemático
    # El error está en: motion.update(dt * motion)
    # Debe ser: motion.update(current_time, dt)
    
    # Patrón para encontrar motion.update con parámetros incorrectos
    pattern1 = r'motion\.update\(dt \* motion\)'
    if pattern1 in content:
        content = content.replace('motion.update(dt * motion)', 'motion.update(self._time, dt)')
        print("✅ Corregido: motion.update(dt * motion) → motion.update(self._time, dt)")
    
    # Otro patrón posible
    pattern2 = r'motion\.update\(dt\s*\*\s*motion\)'
    content = re.sub(pattern2, 'motion.update(self._time, dt)', content)
    
    # También buscar motion.update(dt) y cambiarlo
    pattern3 = r'motion\.update\(dt\)'
    if pattern3 in content:
        content = content.replace('motion.update(dt)', 'motion.update(self._time, dt)')
        print("✅ Corregido: motion.update(dt) → motion.update(self._time, dt)")
    
    # Buscar en el contexto del loop
    loop_pattern = r'(for source_id, motion in self\.motion_states\.items\(\):.*?)(motion\.update\([^)]+\))'
    
    def fix_update_call(match):
        loop_part = match.group(1)
        update_call = match.group(2)
        
        # Si el update tiene multiplicación o parámetros incorrectos
        if '*' in update_call or 'dt * motion' in update_call:
            return loop_part + 'motion.update(self._time, dt)'
        elif 'motion.update(dt)' in update_call:
            return loop_part + 'motion.update(self._time, dt)'
        else:
            return match.group(0)
    
    content = re.sub(loop_pattern, fix_update_call, content, flags=re.DOTALL)
    
    # Si no encontramos el patrón específico, buscar de forma más general
    if 'motion.update(' in content:
        # Buscar todas las ocurrencias en el método update
        update_method_pattern = r'(def update\(self.*?\n)(.*?)(?=\n    def|\nclass|\Z)'
        
        def fix_update_method_content(match):
            method_def = match.group(1)
            method_body = match.group(2)
            
            # Arreglar cualquier motion.update que tenga multiplicación
            method_body = re.sub(
                r'motion\.update\([^)]*\*[^)]*\)',
                'motion.update(self._time, dt)',
                method_body
            )
            
            # Asegurar que self._time existe
            if 'self._time' not in method_body and 'current_time' in method_body:
                # Agregar self._time = current_time
                lines = method_body.split('\n')
                for i, line in enumerate(lines):
                    if 'current_time = time.time()' in line:
                        lines.insert(i + 1, '        self._time = current_time')
                        break
                method_body = '\n'.join(lines)
            
            return method_def + method_body
        
        content = re.sub(update_method_pattern, fix_update_method_content, content, flags=re.DOTALL)
    
    # Guardar archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Método update corregido")
    return True

def verify_fix():
    """Verificar que el fix funcionó"""
    
    verification_script = '''import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Test rápido
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
macro = engine.create_macro("test", 2)
engine.set_macro_concentration(macro, 0.5)

try:
    engine.update()
    print("✅ Update funciona correctamente")
except Exception as e:
    print(f"❌ Error: {e}")
'''
    
    with open('verify_update_fix.py', 'w', encoding='utf-8') as f:
        f.write(verification_script)
    
    print("✅ verify_update_fix.py creado")

if __name__ == "__main__":
    print("🔧 FIXING UPDATE METHOD DIRECTLY")
    print("=" * 60)
    
    if fix_update_method():
        verify_fix()
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Ejecutar: python verify_update_fix.py")
        print("2. Si funciona, ejecutar: python test_system_working.py")
        print("3. Si todo OK → Implementar MCP Server")