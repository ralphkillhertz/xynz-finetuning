# === fix_phase_argument.py ===
# 🔧 Fix: Pasar el argumento 'phase' correctamente
# ⚡ Error: _calculate_position_on_trajectory() missing 1 required positional argument: 'phase'
# 🎯 Impacto: CRÍTICO - Último error antes de funcionar

import os
import re

def fix_calculate_position_call():
    """Arregla la llamada a _calculate_position_on_trajectory"""
    
    motion_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    print("🔧 Corrigiendo llamada a _calculate_position_on_trajectory...")
    
    # Leer el archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar la llamada incorrecta
    # De: new_position = self._calculate_position_on_trajectory()
    # A: new_position = self._calculate_position_on_trajectory(self.position_on_trajectory)
    
    old_call = "new_position = self._calculate_position_on_trajectory()"
    new_call = "new_position = self._calculate_position_on_trajectory(self.position_on_trajectory)"
    
    if old_call in content:
        content = content.replace(old_call, new_call)
        print("✅ Llamada corregida")
    else:
        print("⚠️ No se encontró la llamada exacta, buscando variantes...")
        
        # Buscar con regex
        pattern = r'new_position = self\._calculate_position_on_trajectory\(\)'
        replacement = 'new_position = self._calculate_position_on_trajectory(self.position_on_trajectory)'
        content = re.sub(pattern, replacement, content)
    
    # Hacer backup
    import shutil
    from datetime import datetime
    backup_name = f"{motion_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(motion_path, backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    # Escribir el archivo corregido
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ motion_components.py actualizado")
    
    # Verificar que la corrección se aplicó
    with open(motion_path, 'r', encoding='utf-8') as f:
        content_check = f.read()
    
    if "self._calculate_position_on_trajectory(self.position_on_trajectory)" in content_check:
        print("✅ Verificación: la corrección se aplicó correctamente")
    else:
        print("⚠️ Advertencia: la corrección puede no haberse aplicado")
    
    return True

def quick_test():
    """Test rápido para verificar que funciona"""
    
    test_code = '''# === quick_test.py ===
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

# Test rápido
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60, enable_modulator=False)
macro_name = engine.create_macro("test", source_count=1)
sid = list(engine._macros[macro_name].source_ids)[0]

# Configurar trayectoria
engine.set_individual_trajectory(
    macro_name, sid,
    shape="circle",
    shape_params={'radius': 2.0},
    movement_mode="fix",
    speed=1.0
)

# Posición inicial
initial_pos = engine._positions[sid].copy()
print(f"Posición inicial: {initial_pos}")

# 10 updates
for i in range(10):
    engine.update()

# Posición final
final_pos = engine._positions[sid]
distance = np.linalg.norm(final_pos - initial_pos)

print(f"Posición final: {final_pos}")
print(f"Distancia: {distance:.3f}")
print(f"\\n{'✅ ¡FUNCIONA!' if distance > 0.01 else '❌ No se mueve'}")
'''
    
    with open("quick_test.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test rápido creado")

if __name__ == "__main__":
    print("🔧 FIX ARGUMENTO PHASE")
    print("=" * 50)
    
    if fix_calculate_position_call():
        quick_test()
        print("\n✅ Fix aplicado")
        print("\n📝 Ejecuta:")
        print("python quick_test.py")
        print("\n¡Debería funcionar ahora! 🎉")