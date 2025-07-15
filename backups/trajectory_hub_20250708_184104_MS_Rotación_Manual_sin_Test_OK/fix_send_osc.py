# === fix_send_osc.py ===
# 🔧 Fix: _send_osc_update no existe
# ⚡ Solución rápida al método update

import os
import re
from datetime import datetime

def fix_send_osc():
    """Corrige la llamada a _send_osc_update"""
    
    print("🔧 FIX: _send_osc_update no existe")
    print("=" * 60)
    
    # Ruta del archivo
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encuentra {file_path}")
        return False
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar el nombre correcto del método
    print("\n🔍 Buscando método OSC correcto...")
    
    # Buscar métodos OSC
    if 'send_osc_positions' in content:
        correct_method = 'send_osc_positions()'
        print("✅ Encontrado: send_osc_positions()")
    elif 'send_osc_update' in content:
        correct_method = 'send_osc_update()'
        print("✅ Encontrado: send_osc_update()")
    else:
        # Comentar la línea si no hay método OSC
        correct_method = None
        print("⚠️ No se encontró método OSC, se comentará la línea")
    
    # Reemplazar o comentar
    if correct_method:
        content = re.sub(r'self\._send_osc_update\(\)', f'self.{correct_method}', content)
        print(f"✅ Reemplazado con: self.{correct_method}")
    else:
        content = re.sub(r'(\s*)self\._send_osc_update\(\)', r'\1# self._send_osc_update()  # Comentado: método no existe', content)
        print("✅ Línea comentada")
    
    # Escribir el archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n🎯 TEST INLINE:")
    
    # Test directo
    test_code = '''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import math

# Test super rápido
try:
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    engine.create_macro("test", 2)
    macro_name = list(engine._macros.keys())[0]
    
    # Posiciones
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    engine._positions[1] = np.array([0.0, 3.0, 0.0])
    
    # Rotación
    engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, pitch=0, roll=0, interpolation_speed=0.1)
    
    # Update
    pos_before = engine._positions[0].copy()
    engine.update()
    pos_after = engine._positions[0].copy()
    
    # Verificar
    diff = np.linalg.norm(pos_after - pos_before)
    if diff > 0.0001:
        print(f"✅ ¡¡¡FUNCIONA!!! Movimiento detectado: {diff:.6f}")
        print(f"   Antes: {pos_before}")
        print(f"   Después: {pos_after}")
        print("\\n🎉 EL SISTEMA DE DELTAS ESTÁ FUNCIONANDO 🎉")
    else:
        print("❌ Sin movimiento todavía")
except Exception as e:
    print(f"Error: {e}")
'''
    
    exec(test_code)
    
    return True

if __name__ == "__main__":
    fix_send_osc()