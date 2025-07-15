# === fix_update_with_deltas_str.py ===
# 🔧 Fix: Corregir update_with_deltas para manejar objetos correctamente
# ⚡ QUICK FIX

import os
import re

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

print("🔍 Buscando método update_with_deltas...")

# Buscar el método
pattern = r'(def update_with_deltas.*?)((?=\n    def |\n\nclass |\Z))'
match = re.search(pattern, content, re.DOTALL)

if match:
    print("✅ Encontrado, reemplazando...")
    
    # Método corregido
    new_method = '''def update_with_deltas(self, current_time: float, dt: float) -> List[MotionDelta]:
        """Actualiza y retorna lista de deltas de todos los componentes activos"""
        deltas = []
        
        for name, component in self.active_components.items():
            # Solo procesar si es un objeto MotionComponent
            if hasattr(component, 'calculate_delta'):
                try:
                    delta = component.calculate_delta(self.state, current_time, dt)
                    if delta and (np.any(delta.position != 0) or 
                                 delta.orientation or 
                                 delta.aperture != 0 or 
                                 delta.distance != 0):
                        deltas.append(delta)
                except Exception as e:
                    print(f"❌ Error en {name}: {e}")
                    
        return deltas'''
    
    # Encontrar límites exactos del método
    start = content.find('def update_with_deltas', match.start())
    
    # Buscar el siguiente def o class
    next_def = content.find('\n    def ', start + 1)
    next_class = content.find('\nclass ', start + 1)
    next_decorator = content.find('\n@', start + 1)
    
    candidates = [x for x in [next_def, next_class, next_decorator, len(content)] if x > start]
    end = min(candidates)
    
    # Reemplazar
    content = content[:start] + '    ' + new_method + '\n' + content[end:]
    
    # Guardar
    with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Método update_with_deltas corregido")
else:
    print("❌ No se encontró el método")

print("\n🚀 Ejecutando test...")
os.system("python test_rotation_ms_final.py")