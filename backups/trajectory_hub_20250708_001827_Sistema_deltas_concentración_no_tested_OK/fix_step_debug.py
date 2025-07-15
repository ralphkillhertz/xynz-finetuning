# === fix_step_debug.py ===
# 🔍 Debug: Encuentra por qué los deltas no se aplican
# ⚡ Añade prints de debug al método step()

import os
import re
from datetime import datetime

def add_debug_to_step():
    """Añade prints de debug al método step para ver qué pasa"""
    
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
        return False
    
    method_def = match.group(1)
    method_content = match.group(2)
    
    # Detectar indentación
    lines = method_content.split('\n')
    first_code_line = next((line for line in lines if line.strip() and not line.strip().startswith('#')), '')
    base_indent = len(first_code_line) - len(first_code_line.lstrip())
    indent = ' ' * base_indent
    
    # Nuevo método step con debug
    new_method = f'''
{indent}"""Ejecuta un paso de simulación con soporte de deltas"""
{indent}if not self.running:
{indent}    return
{indent}
{indent}current_time = time.time()
{indent}dt = 1.0 / self._update_rate
{indent}
{indent}# DEBUG: Verificar estado inicial
{indent}print(f"\\n🔍 DEBUG step():")
{indent}print(f"  - motion_states: {{list(self.motion_states.keys())}}")
{indent}print(f"  - running: {{self.running}}")
{indent}
{indent}# Sistema de deltas para composición de movimientos
{indent}all_deltas = []
{indent}
{indent}# Actualizar cada SourceMotion y recolectar deltas
{indent}for source_id, motion in self.motion_states.items():
{indent}    print(f"\\n  📌 Procesando motion {{source_id}}:")
{indent}    print(f"    - Tipo: {{type(motion).__name__}}")
{indent}    
{indent}    if hasattr(motion, 'update_with_deltas'):
{indent}        print(f"    - ✅ Tiene update_with_deltas")
{indent}        deltas = motion.update_with_deltas(current_time, dt)
{indent}        print(f"    - Deltas retornados: {{len(deltas) if deltas else 0}}")
{indent}        if deltas:
{indent}            for i, delta in enumerate(deltas):
{indent}                print(f"      Delta {{i}}: source_id={{delta.source_id}}, position={{delta.position}}")
{indent}            all_deltas.extend(deltas)
{indent}    else:
{indent}        print(f"    - ❌ NO tiene update_with_deltas")
{indent}
{indent}print(f"\\n  📊 Total deltas recolectados: {{len(all_deltas)}}")
{indent}
{indent}# Aplicar todos los deltas a las posiciones
{indent}for i, delta in enumerate(all_deltas):
{indent}    print(f"\\n  🎯 Aplicando delta {{i}}:")
{indent}    print(f"    - source_id: {{delta.source_id}}")
{indent}    print(f"    - delta.position: {{delta.position}}")
{indent}    print(f"    - len(_positions): {{len(self._positions)}}")
{indent}    
{indent}    if delta.source_id < len(self._positions):
{indent}        if delta.position is not None:
{indent}            old_pos = self._positions[delta.source_id].copy()
{indent}            self._positions[delta.source_id] += delta.position
{indent}            new_pos = self._positions[delta.source_id]
{indent}            print(f"    - ✅ Aplicado: {{old_pos}} -> {{new_pos}}")
{indent}        else:
{indent}            print(f"    - ❌ delta.position es None")
{indent}    else:
{indent}        print(f"    - ❌ source_id {{delta.source_id}} >= len(_positions) {{len(self._positions)}}")
{indent}
{indent}# Llamar a update si existe para mantener compatibilidad
{indent}if hasattr(self, 'update'):
{indent}    self.update()
'''
    
    # Reemplazar el método
    new_content = content[:match.start()] + method_def + new_method + content[match.end():]
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Debug añadido a step()")
    
    # Verificar sintaxis
    try:
        compile(new_content, engine_path, 'exec')
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
    print("🔧 AÑADIENDO DEBUG A STEP()")
    print("="*60)
    
    success = add_debug_to_step()
    
    if success:
        print("\n✅ Debug añadido exitosamente")
        print("\n📋 Ahora ejecuta el test mínimo para ver qué pasa:")
        print("$ python test_delta_minimal.py")
        print("\n👀 Esto mostrará exactamente qué está fallando en step()")
    else:
        print("\n❌ Error al añadir debug")