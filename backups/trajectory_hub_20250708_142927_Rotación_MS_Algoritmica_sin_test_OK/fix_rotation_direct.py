# === fix_rotation_direct.py ===
# 🔧 Arreglar directamente la línea problemática
# ⚡ Cambiar set_rotation por asignaciones directas

from pathlib import Path

print("🔧 Fix directo del problema...")

engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
content = engine_path.read_text()

# Buscar la línea problemática
problem_line = content.find("rotation.set_rotation(")
if problem_line > 0:
    print("✅ Encontrada llamada a set_rotation")
    
    # Encontrar el final de la llamada
    paren_count = 1
    pos = problem_line + len("rotation.set_rotation(")
    call_end = pos
    
    while paren_count > 0 and call_end < len(content):
        if content[call_end] == '(':
            paren_count += 1
        elif content[call_end] == ')':
            paren_count -= 1
        call_end += 1
    
    # Extraer la llamada completa
    call = content[problem_line:call_end]
    print(f"   Llamada actual: {call}")
    
    # Reemplazar con asignaciones directas
    new_code = """# Configurar rotación directamente
                rotation.speed_x = speed_x
                rotation.speed_y = speed_y
                rotation.speed_z = speed_z
                if center is not None:
                    rotation.center = center
                rotation.enabled = (
                    abs(float(speed_x)) > 0.001 or
                    abs(float(speed_y)) > 0.001 or
                    abs(float(speed_z)) > 0.001
                )"""
    
    # Reemplazar
    content = content[:problem_line] + new_code + content[call_end:]
    
    # Guardar
    backup = engine_path.with_suffix('.backup_before_fix')
    engine_path.rename(backup)
    engine_path.write_text(content)
    
    print("✅ Arreglado!")
    print(f"   Backup: {backup}")
else:
    print("❌ No se encontró rotation.set_rotation")
    
    # Buscar alternativas
    if "rotation." in content:
        print("\n🔍 Buscando usos de rotation...")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "rotation." in line and "set_" in line:
                print(f"   Línea {i}: {line.strip()}")

print("\n📝 Ejecuta: python test_rotation_final_working.py")