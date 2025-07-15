# === fix_step_method.py ===
# 🔧 Fix: Activa deltas en el método step() que es el que usa el test
# ⚡ Impacto: CRÍTICO - Arregla el método correcto

import os
import re
from datetime import datetime

def fix_step_method():
    """Arregla el método step para usar deltas"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar el método step
    pattern = r'(def step\(self[^)]*\):)(.*?)(?=\n\s{0,4}def|\n\s{0,4}async def|\nclass|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encontró método step")
        # Intentar crear uno
        print("🔧 Creando método step...")
        
        # Buscar dónde insertarlo (después de update si existe)
        if 'def update(' in content:
            insert_pattern = r'(def update.*?\n(?:.*?\n)*?)\n(\s{0,4}def)'
            insert_match = re.search(insert_pattern, content, re.DOTALL)
            if insert_match:
                insert_pos = insert_match.end(1)
                indent = '    '
            else:
                insert_pos = content.find('def update(')
                insert_pos = content.find('\n\n', insert_pos) + 2
                indent = '    '
        else:
            # Después de create_source
            insert_pos = content.find('def create_source')
            insert_pos = content.find('\n\n', insert_pos) + 2
            indent = '    '
        
        # Crear método step
        step_method = f'''
{indent}def step(self) -> None:
{indent}    """Ejecuta un paso de simulación con soporte de deltas"""
{indent}    if not self.running:
{indent}        return
{indent}    
{indent}    current_time = time.time()
{indent}    dt = 1.0 / self._update_rate
{indent}    
{indent}    # Sistema de deltas para composición de movimientos
{indent}    all_deltas = []
{indent}    
{indent}    # Actualizar cada SourceMotion y recolectar deltas
{indent}    for source_id, motion in self.motion_states.items():
{indent}        if hasattr(motion, 'update_with_deltas'):
{indent}            deltas = motion.update_with_deltas(current_time, dt)
{indent}            if deltas:
{indent}                all_deltas.extend(deltas)
{indent}    
{indent}    # Aplicar todos los deltas a las posiciones
{indent}    for delta in all_deltas:
{indent}        if delta.source_id < len(self._positions):
{indent}            if delta.position is not None:
{indent}                self._positions[delta.source_id] += delta.position
{indent}    
{indent}    # Llamar a update si existe para mantener compatibilidad
{indent}    if hasattr(self, 'update'):
{indent}        self.update()
'''
        
        content = content[:insert_pos] + step_method + '\n' + content[insert_pos:]
        print("✅ Método step creado")
        
    else:
        print("✅ Método step encontrado, actualizándolo...")
        
        method_def = match.group(1)
        method_content = match.group(2)
        
        # Verificar si ya tiene deltas
        if 'update_with_deltas' in method_content:
            print("   ✅ Ya tiene soporte de deltas")
            return True
        
        # Detectar indentación
        lines = method_content.split('\n')
        first_code_line = next((line for line in lines if line.strip() and not line.strip().startswith('#')), '')
        base_indent = len(first_code_line) - len(first_code_line.lstrip())
        indent = ' ' * base_indent
        
        # Código de deltas
        delta_code = f'''
{indent}# Sistema de deltas para composición de movimientos
{indent}all_deltas = []
{indent}
{indent}# Actualizar cada SourceMotion y recolectar deltas
{indent}for source_id, motion in self.motion_states.items():
{indent}    if hasattr(motion, 'update_with_deltas'):
{indent}        deltas = motion.update_with_deltas(time.time(), 1.0/self._update_rate)
{indent}        if deltas:
{indent}            all_deltas.extend(deltas)
{indent}
{indent}# Aplicar todos los deltas a las posiciones
{indent}for delta in all_deltas:
{indent}    if delta.source_id < len(self._positions):
{indent}        if delta.position is not None:
{indent}            self._positions[delta.source_id] += delta.position
{indent}
'''
        
        # Insertar al principio del método (después del docstring si existe)
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                insert_pos = i
                break
            elif i > 0 and (line.strip().endswith('"""') or line.strip().endswith("'''")):
                insert_pos = i + 1
                break
        
        # Insertar código
        new_lines = lines[:insert_pos] + delta_code.split('\n') + lines[insert_pos:]
        new_method_content = '\n'.join(new_lines)
        
        # Reemplazar en content
        new_content = content[:match.start()] + method_def + new_method_content + content[match.end():]
        content = new_content
    
    # Verificar imports
    if 'import time' not in content:
        content = 'import time\n' + content
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verificar sintaxis
    try:
        compile(content, engine_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print("⚠️ Backup restaurado")
        return False

if __name__ == "__main__":
    print("🔧 FIX DEL MÉTODO STEP()")
    print("="*60)
    print("📌 El test usa engine.step(), NO engine.update()")
    print("🔧 Arreglando el método correcto...\n")
    
    success = fix_step_method()
    
    if success:
        print("\n✅ Método step() actualizado con sistema de deltas!")
        print("\n🎯 AHORA SÍ - Las fuentes DEBEN moverse!")
        print("\n🚀 Ejecuta:")
        print("$ python test_delta_concentration_final.py")
        print("\n✨ Deberías ver:")
        print("   - Distancia inicial: 10.00")
        print("   - Distancia final: ~2.00")
        print("   - Las fuentes convergen al centro!")
    else:
        print("\n❌ Error al actualizar step()")