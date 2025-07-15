# === verify_delta_system.py ===
# 🔧 Verificar que el sistema de deltas esté activo
# ⚡ El problema es que engine.update() no procesa deltas

from pathlib import Path

print("🔍 Verificando sistema de deltas en engine.update()...")

engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
content = engine_path.read_text()

# Buscar el método update
update_start = content.find("def update(self")
if update_start > 0:
    # Buscar las siguientes 50 líneas
    update_method = content[update_start:update_start+2000]
    
    print("✅ Método update encontrado")
    
    # Verificar si procesa deltas
    if "update_with_deltas" in update_method:
        print("✅ update_with_deltas está presente")
        
        # Verificar si aplica deltas
        if "delta.position" in update_method or "_positions[sid] +=" in update_method:
            print("✅ Los deltas se aplican a las posiciones")
        else:
            print("❌ Los deltas NO se aplican a las posiciones")
    else:
        print("❌ update_with_deltas NO está presente")
        
    # Verificar si el código de deltas está comentado
    lines = update_method.split('\n')
    for i, line in enumerate(lines[:30]):
        if "motion_states" in line or "delta" in line.lower():
            print(f"   Línea {i}: {line.strip()}")

# Crear fix si es necesario
with open("fix_delta_application.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""Asegurar que el sistema de deltas esté activo en engine.update()"""

from pathlib import Path

print("🔧 Activando sistema de deltas en engine.update()...")

engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
content = engine_path.read_text()

# Buscar el método update
update_start = content.find("def update(self")
if update_start == -1:
    print("❌ No se encontró método update")
    exit(1)

# Buscar el siguiente método
next_method = content.find("\\n    def ", update_start + 1)
if next_method == -1:
    next_method = len(content)

# Verificar si ya procesa deltas
update_content = content[update_start:next_method]
if "update_with_deltas" in update_content and "_positions[sid] +=" in update_content:
    print("✅ Sistema de deltas ya está activo")
    
    # Verificar que no esté comentado
    lines = update_content.split('\\n')
    for line in lines:
        if "motion.update_with_deltas" in line and line.strip().startswith('#'):
            print("❌ El código de deltas está comentado!")
            # Descomentar
            update_content = update_content.replace(line, line.lstrip('#').lstrip())
else:
    print("❌ Sistema de deltas no encontrado, añadiendo...")
    
    # Buscar dónde insertar el código de deltas
    step_line = update_content.find("positions = self.step()")
    if step_line > 0:
        # Insertar después de step()
        insert_pos = update_content.find("\\n", step_line) + 1
        
        delta_code = """
        # Procesar deltas de todos los motion states
        if hasattr(self, 'motion_states'):
            for sid, motion in self.motion_states.items():
                if sid < len(self._positions):
                    # Obtener deltas de todos los componentes activos
                    deltas = motion.update_with_deltas(self._time, dt)
                    
                    # Aplicar deltas a la posición
                    if deltas:
                        for delta in deltas:
                            if hasattr(delta, 'position') and delta.position is not None:
                                self._positions[sid] += delta.position
"""
        
        update_content = update_content[:insert_pos] + delta_code + update_content[insert_pos:]
        
        # Reemplazar en el contenido completo
        content = content[:update_start] + update_content + content[next_method:]
        
        # Guardar
        engine_path.write_text(content)
        print("✅ Sistema de deltas añadido")

print("\\n📝 Ejecuta: python test_rotation_final_working.py")
''')

print("\n✅ Scripts creados")
print("\n📝 Ejecuta:")
print("  1. python fix_delta_application.py")
print("  2. python test_rotation_final_working.py")