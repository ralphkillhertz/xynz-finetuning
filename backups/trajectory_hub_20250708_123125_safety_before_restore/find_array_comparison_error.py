# === find_array_comparison_error.py ===
# 🎯 Encontrar la línea exacta del error array ambiguous
# ⚡ Diagnóstico profundo con monkey patching

import numpy as np
import sys
import traceback
from trajectory_hub import EnhancedTrajectoryEngine

# Guardar el __bool__ original de numpy
original_bool = np.ndarray.__bool__

def debug_bool(self):
    """Interceptar cuando se intenta usar un array como bool"""
    print("\n🔴 ARRAY USADO COMO BOOL DETECTADO!")
    print(f"Array shape: {self.shape}")
    print(f"Array content: {self}")
    print("\n📍 TRACEBACK:")
    traceback.print_stack()
    print("\n" + "="*50 + "\n")
    
    # Llamar al original para mantener el error
    return original_bool(self)

# Monkey patch para debugging
np.ndarray.__bool__ = debug_bool

try:
    # Reproducir el error con información detallada
    print("🔧 Creando engine con debug activado...")
    engine = EnhancedTrajectoryEngine(n_sources=10, fps=60)
    
    print("✅ Creando macro...")
    engine.create_macro("test", [0, 1, 2])
    
    print("✅ Aplicando rotación algorítmica...")
    engine.set_macro_rotation("test", "circular", speed=1.0)
    
    print("🔄 Ejecutando update (aquí debe aparecer el error)...")
    for i in range(3):
        print(f"\n--- Frame {i} ---")
        engine.update()
        
except Exception as e:
    print(f"\n❌ Error capturado: {type(e).__name__}: {e}")
    
finally:
    # Restaurar comportamiento normal
    np.ndarray.__bool__ = original_bool
    
print("\n✅ Debug completado - revisa el traceback arriba")