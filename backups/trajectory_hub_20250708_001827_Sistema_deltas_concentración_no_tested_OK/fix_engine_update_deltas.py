# === fix_engine_update_deltas.py ===
# 🔧 Fix: Añade procesamiento de deltas a engine.update()
# ⚡ Este es EL fix definitivo para que las fuentes se muevan

import os
import re
from datetime import datetime

def fix_engine_update():
    """Añade procesamiento de deltas al método update del engine"""
    
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
    
    # Buscar método update
    update_pattern = r'(def update\(self[^)]*\):)(.*?)(?=\n\s{0,4}def|\Z)'
    match = re.search(update_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ No se encontró método update")
        return False
    
    print("✅ Método update encontrado")
    
    # Verificar si ya procesa deltas
    update_body = match.group(2)
    if 'delta' in update_body.lower() and 'motion_states' in update_body:
        print("⚠️ update ya contiene código de deltas")
        return True
    
    # Encontrar dónde insertar el código de deltas
    # Buscar después de actualizar tiempo
    lines = update_body.split('\n')
    insert_line = -1
    
    for i, line in enumerate(lines):
        if 'self._time' in line or 'current_time' in line:
            insert_line = i + 1
            break
    
    if insert_line == -1:
        # Si no encuentra, insertar al principio
        insert_line = 1
    
    # Código de deltas a insertar
    delta_code = '''
        # Procesar deltas de todos los componentes
        if hasattr(self, 'motion_states'):
            for source_id, motion in self.motion_states.items():
                if hasattr(motion, 'update_with_deltas'):
                    # Obtener deltas de todos los componentes
                    deltas = motion.update_with_deltas(self._time, dt)
                    
                    # Aplicar deltas a las posiciones
                    if deltas and isinstance(deltas, list):
                        for delta in deltas:
                            if hasattr(delta, 'position') and delta.position is not None:
                                # Aplicar delta a la posición
                                self._positions[source_id] += delta.position
                                
                            if hasattr(delta, 'orientation') and delta.orientation is not None:
                                # Aplicar delta a la orientación si existe
                                if hasattr(self, '_orientations'):
                                    self._orientations[source_id] += delta.orientation
'''
    
    # Insertar el código
    new_lines = lines[:insert_line] + [delta_code] + lines[insert_line:]
    new_update_body = '\n'.join(new_lines)
    
    # Reconstruir contenido
    new_content = content[:match.start(2)] + new_update_body + content[match.end(2):]
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Código de deltas añadido a update()")
    
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
    print("🔧 FIX DEFINITIVO - AÑADIR DELTAS A ENGINE.UPDATE")
    print("="*60)
    print("\n📌 Problema detectado:")
    print("  - set_macro_concentration SÍ añade componentes ✅")
    print("  - Los componentes tienen calculate_delta ✅")
    print("  - Pero engine.update() NO procesa los deltas ❌")
    print("\n🔧 Aplicando fix...")
    
    success = fix_engine_update()
    
    if success:
        print("\n✅ ¡FIX APLICADO EXITOSAMENTE!")
        print("\n🎯 Ahora ejecuta:")
        print("$ python test_final_concentration.py")
        print("\n🎉 ¡Las fuentes DEBEN moverse!")
    else:
        print("\n❌ Error al aplicar fix")