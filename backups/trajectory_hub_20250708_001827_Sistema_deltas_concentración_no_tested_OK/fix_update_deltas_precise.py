# === fix_update_deltas_precise.py ===
# 🔧 Fix preciso para añadir deltas a update()
# ⚡ Basado en la ubicación exacta encontrada

import os
from datetime import datetime

def fix_update_with_deltas():
    """Añade procesamiento de deltas al método update"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_path):
        print("❌ No se encuentra enhanced_trajectory_engine.py")
        return False
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar línea de update
    update_line = -1
    for i, line in enumerate(lines):
        if 'def update(self)' in line:
            update_line = i
            print(f"✅ Método update encontrado en línea {i+1}")
            break
    
    if update_line == -1:
        print("❌ No se encontró método update")
        return False
    
    # Buscar dónde insertar (después de _apply_algorithmic_rotations)
    insert_line = -1
    for i in range(update_line, min(update_line + 20, len(lines))):
        if '_apply_algorithmic_rotations' in lines[i]:
            insert_line = i + 1
            # Saltar líneas vacías o comentarios
            while insert_line < len(lines) and (lines[insert_line].strip() == '' or 
                                               lines[insert_line].strip().startswith('#') or
                                               lines[insert_line].strip().startswith('"""')):
                insert_line += 1
            break
    
    if insert_line == -1:
        # Si no encuentra, insertar después de la definición
        insert_line = update_line + 1
    
    print(f"✅ Insertando código de deltas en línea {insert_line + 1}")
    
    # Determinar la indentación
    indent = '        '  # 8 espacios por defecto
    if insert_line < len(lines):
        # Copiar la indentación de la línea siguiente
        for char in lines[insert_line]:
            if char != ' ':
                break
        else:
            indent = lines[insert_line][:8]
    
    # Código de deltas
    delta_code = f'''
{indent}# 🔧 PROCESAMIENTO DE DELTAS - Sistema de composición
{indent}if hasattr(self, 'motion_states') and hasattr(self, 'dt'):
{indent}    dt = getattr(self, 'dt', 0.016)  # Default 60 FPS
{indent}    current_time = getattr(self, '_time', 0.0)
{indent}    
{indent}    for source_id, motion in self.motion_states.items():
{indent}        if hasattr(motion, 'update_with_deltas'):
{indent}            # Obtener deltas de todos los componentes activos
{indent}            deltas = motion.update_with_deltas(current_time, dt)
{indent}            
{indent}            # Aplicar cada delta a las posiciones
{indent}            if deltas and isinstance(deltas, list):
{indent}                for delta in deltas:
{indent}                    if hasattr(delta, 'position') and delta.position is not None:
{indent}                        # Verificar que no sea vector cero
{indent}                        if not all(v == 0 for v in delta.position):
{indent}                            self._positions[source_id] += delta.position
{indent}                            
{indent}                    # También aplicar orientación si existe
{indent}                    if hasattr(delta, 'orientation') and delta.orientation is not None:
{indent}                        if hasattr(self, '_orientations') and source_id in self._orientations:
{indent}                            self._orientations[source_id] += delta.orientation
{indent}# FIN PROCESAMIENTO DE DELTAS

'''
    
    # Insertar el código
    lines.insert(insert_line, delta_code)
    
    # Escribir archivo
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Código de deltas añadido exitosamente")
    
    # Verificar sintaxis
    try:
        with open(engine_path, 'r', encoding='utf-8') as f:
            compile(f.read(), engine_path, 'exec')
        print("✅ Sintaxis verificada")
        return True
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")
        # Restaurar
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("⚠️ Backup restaurado")
        return False

if __name__ == "__main__":
    print("🔧 FIX PRECISO - PROCESAMIENTO DE DELTAS")
    print("="*60)
    print("\n📌 Información encontrada:")
    print("  - update() está en línea 1153")
    print("  - motion_states se procesa en líneas 1408, 1437, 1797")
    print("  - Necesitamos añadir procesamiento de deltas")
    print("\n🔧 Aplicando fix...")
    
    success = fix_update_with_deltas()
    
    if success:
        print("\n✅ ¡FIX APLICADO!")
        print("\n📋 Ahora ejecuta:")
        print("$ python test_concentration_working.py")
    else:
        print("\n❌ Error al aplicar fix")