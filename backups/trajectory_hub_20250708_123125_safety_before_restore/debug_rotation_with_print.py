# === debug_rotation_with_print.py ===
# 🎯 Usar el test existente pero con más debugging
# ⚡ Basado en test_rotation_ms_final.py del historial

import numpy as np
import sys
sys.path.append('.')

from enhanced_trajectory_engine import EnhancedTrajectoryEngine

# Interceptar print para ver TODO lo que pasa
original_print = print
call_count = 0

def debug_print(*args, **kwargs):
    global call_count
    call_count += 1
    # Solo mostrar las primeras 500 llamadas para no saturar
    if call_count < 500:
        original_print(f"[{call_count}]", *args, **kwargs)
    elif call_count == 500:
        original_print("... (suprimiendo más prints)")

# Activar debug print
print = debug_print

try:
    print("\n🔧 Test de rotación MS con debug completo\n")
    
    # Crear engine (usando parámetros correctos del historial)
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=120)
    
    # Crear macro
    engine.create_macro("test_rotation", source_ids=[0, 1, 2, 3, 4])
    
    # Aplicar rotación algorítmica
    engine.set_macro_rotation("test_rotation", rotation_type="circular", speed=1.0)
    
    # Ejecutar algunos frames
    print("\n🔄 Ejecutando frames...\n")
    for i in range(5):
        print(f"\n--- Frame {i} ---")
        try:
            engine.update()
            print(f"✅ Frame {i} completado")
        except ValueError as e:
            if "ambiguous" in str(e):
                print(f"\n❌ ERROR EN FRAME {i}: Array ambiguous")
                print(f"Call count cuando falló: {call_count}")
                # Buscar el último print antes del error
                break
            else:
                raise
                
except Exception as e:
    print(f"\n💥 Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Restaurar print normal
print = original_print

print(f"\n📊 Total de prints antes del error: {call_count}")
print("\n💡 El error ocurre cerca del print número indicado arriba")