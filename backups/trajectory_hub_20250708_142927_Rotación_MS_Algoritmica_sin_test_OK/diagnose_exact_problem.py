# === diagnose_exact_problem.py ===
# 🔧 Encontrar exactamente qué está pasando
# ⚡ Debug línea por línea

from pathlib import Path

print("🔍 DIAGNÓSTICO EXACTO DEL PROBLEMA")
print("=" * 60)

# 1. Ver qué hay exactamente en set_macro_rotation
engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
content = engine_path.read_text()

print("1️⃣ Contenido de set_macro_rotation:")
set_macro_start = content.find("def set_macro_rotation")
if set_macro_start > 0:
    # Encontrar las siguientes 50 líneas
    lines = content[set_macro_start:].split('\n')[:50]
    
    # Buscar líneas relevantes
    for i, line in enumerate(lines):
        if "MacroRotation" in line or "rotation" in line and "=" in line:
            print(f"   Línea {i}: {line.strip()}")
        if "from" in line and "import" in line:
            print(f"   ⚠️ Import local en línea {i}: {line.strip()}")

# 2. Crear versión corregida de set_macro_rotation
print("\n2️⃣ Creando versión corregida...")

with open("fix_set_macro_rotation_complete.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""Reemplazar completamente set_macro_rotation con versión funcional"""

from pathlib import Path

print("🔧 Reemplazando set_macro_rotation...")

engine_path = Path("trajectory_hub/core/enhanced_trajectory_engine.py")
content = engine_path.read_text()

# Buscar el método actual
start = content.find("def set_macro_rotation")
if start == -1:
    print("❌ No se encontró set_macro_rotation")
    exit(1)

# Encontrar el siguiente método
next_method = content.find("\\n    def ", start + 1)
if next_method == -1:
    next_method = content.find("\\nclass ", start)
    if next_method == -1:
        next_method = len(content)

# Nuevo método corregido
new_method = """    def set_macro_rotation(self, macro_name, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        \"\"\"Configura rotación algorítmica para un macro con sistema de deltas\"\"\"
        if macro_name not in self._macros:
            print(f"❌ Macro '{macro_name}' no existe")
            return False
            
        macro = self._macros[macro_name]
        source_ids = list(macro.source_ids)
        
        # Centro por defecto es el centroide del macro
        if center is None:
            positions = []
            for sid in source_ids:
                if sid < len(self._positions):
                    positions.append(self._positions[sid].copy())
            if positions:
                center = np.mean(positions, axis=0)
            else:
                center = np.array([0.0, 0.0, 0.0])
        
        # Convertir center a array numpy si no lo es
        center = np.array(center, dtype=np.float32)
        
        # Configurar rotación para cada fuente del macro
        configured = 0
        for sid in source_ids:
            if sid in self.motion_states:
                motion = self.motion_states[sid]
                
                # Crear componente si no existe
                if 'macro_rotation' not in motion.active_components:
                    # Crear nueva instancia de MacroRotation
                    rotation = MacroRotation()
                    motion.active_components['macro_rotation'] = rotation
                else:
                    rotation = motion.active_components['macro_rotation']
                
                # Configurar velocidades directamente (MacroRotation tiene properties)
                rotation.speed_x = speed_x
                rotation.speed_y = speed_y
                rotation.speed_z = speed_z
                rotation.center = center
                
                # Habilitar si alguna velocidad es significativa
                rotation.enabled = (
                    abs(float(speed_x)) > 0.001 or
                    abs(float(speed_y)) > 0.001 or
                    abs(float(speed_z)) > 0.001
                )
                
                configured += 1
        
        if configured > 0:
            print(f"✅ Rotación configurada para '{macro_name}'")
            print(f"   Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
            print(f"   Velocidades: X={float(speed_x):.2f}, Y={float(speed_y):.2f}, Z={float(speed_z):.2f} rad/s")
            print(f"   Fuentes: {configured}/{len(source_ids)}")
            return True
        
        return False
"""

# Reemplazar
content = content[:start] + new_method + content[next_method:]

# Guardar
engine_path.write_text(content)
print("✅ set_macro_rotation reemplazado completamente")
print("   Ahora configura las propiedades directamente sin usar set_rotation()")
''')

print("\n3️⃣ Script de corrección creado")
print("\n📝 Ejecuta:")
print("  1. python fix_set_macro_rotation_complete.py")
print("  2. python test_rotation_final_working.py")