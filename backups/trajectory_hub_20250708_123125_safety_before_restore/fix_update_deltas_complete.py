# === fix_update_deltas_complete.py ===
# 🔧 Fix: Reescribir update_with_deltas correctamente
# ⚡ COMPLETE FIX

import os
import re

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Reescribiendo update_with_deltas completamente...")

# Nuevo método corregido
new_method = '''    def update_with_deltas(self, current_time: float, dt: float) -> List[MotionDelta]:
        """Actualiza y retorna lista de deltas de todos los componentes activos"""
        deltas = []
        
        for name, component in self.active_components.items():
            # Solo procesar si es un objeto MotionComponent
            if hasattr(component, 'calculate_delta'):
                try:
                    delta = component.calculate_delta(self.state, current_time, dt)
                    if delta is not None:
                        # Verificar si el delta tiene cambios significativos
                        has_position_change = np.any(np.abs(delta.position) > 0.0001)
                        has_orientation_change = bool(delta.orientation)
                        has_aperture_change = abs(delta.aperture) > 0.0001
                        has_distance_change = abs(delta.distance) > 0.0001
                        
                        if has_position_change or has_orientation_change or has_aperture_change or has_distance_change:
                            deltas.append(delta)
                except Exception as e:
                    print(f"❌ Error en {name}: {e}")
                    
        return deltas'''

# Buscar y reemplazar el método
pattern = r'def update_with_deltas\(.*?\).*?:.*?(?=\n    def |\nclass |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Reemplazar el método completo
    start = content.find('def update_with_deltas')
    
    # Buscar el siguiente def o class
    next_def = content.find('\n    def ', start + 1)
    next_class = content.find('\nclass ', start + 1)
    candidates = [x for x in [next_def, next_class, len(content)] if x > start]
    end = min(candidates)
    
    # Reemplazar
    content = content[:start] + new_method + '\n' + content[end:]
    
    print("✅ Método update_with_deltas reescrito")
else:
    print("❌ No se encontró el método")

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Archivo actualizado")
print("🚀 Ejecutando test final...")
os.system("python test_rotation_ms_final.py")