# === fix_rotation_arguments.py ===
# 🔧 Fix: Corregir argumentos del método set_macro_rotation
# ⚡ Impacto: CRÍTICO - Desbloquea test de rotación

import os
import re

def fix_rotation_arguments():
    """Arregla los argumentos del método set_macro_rotation"""
    
    print("🔧 ARREGLANDO ARGUMENTOS DE set_macro_rotation\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método actual
    print("🔍 Buscando método set_macro_rotation...")
    
    # Patrón para encontrar el método
    pattern = r'def set_macro_rotation\(self, macro_name: str\):'
    
    if re.search(pattern, content):
        print("❌ Método tiene firma incorrecta, corrigiendo...")
        
        # Reemplazar la firma
        new_signature = 'def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):'
        content = content.replace(
            'def set_macro_rotation(self, macro_name: str):',
            new_signature
        )
        
        # Guardar
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Firma del método corregida")
    else:
        # Buscar cualquier versión del método
        method_match = re.search(r'def set_macro_rotation\([^)]+\):', content)
        if method_match:
            current_sig = method_match.group(0)
            print(f"📋 Firma actual: {current_sig}")
            
            # Si no tiene los parámetros correctos, reemplazar
            if "speed_x" not in current_sig:
                new_sig = 'def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):'
                content = content.replace(current_sig, new_sig)
                
                with open(engine_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ Firma actualizada con parámetros correctos")
        else:
            print("❌ No se encontró el método, necesita ser añadido")
    
    # Crear test simplificado para debug
    print("\n📝 Creando test de debug...")
    
    debug_test = '''# === test_rotation_debug.py ===
# 🧪 Test debug de rotación MS

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\\n🔍 DEBUG: Rotación MS\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60)

# Crear macro
macro_id = engine.create_macro("test", 4)

# Posiciones manuales en cuadrado
positions = [[1,0,0], [-1,0,0], [0,1,0], [0,-1,0]]
for i, sid in enumerate(list(engine._macros[macro_id].source_ids)[:4]):
    if sid < len(engine._positions):
        engine._positions[sid] = np.array(positions[i])
        if sid in engine.motion_states:
            engine.motion_states[sid].position = engine._positions[sid].copy()

print("📍 Posiciones iniciales:")
for sid in list(engine._macros[macro_id].source_ids)[:4]:
    if sid < len(engine._positions):
        p = engine._positions[sid]
        print(f"   Fuente {sid}: {p}")

# Intentar configurar rotación
print("\\n🎯 Configurando rotación...")
try:
    # Verificar que el método existe
    if hasattr(engine, 'set_macro_rotation'):
        print("✅ Método existe")
        # Probar llamada
        engine.set_macro_rotation(macro_id, 0, 1.0, 0)
        print("✅ Rotación configurada")
    else:
        print("❌ Método no existe")
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Intentar sin keywords
    try:
        engine.set_macro_rotation(macro_id, 0, 1.0, 0)
        print("✅ Funciona sin keywords")
    except Exception as e2:
        print(f"❌ También falla sin keywords: {e2}")
'''
    
    with open("test_rotation_debug.py", "w") as f:
        f.write(debug_test)
    
    print("✅ Test de debug creado")

if __name__ == "__main__":
    fix_rotation_arguments()
    print("\n🚀 Ejecutando test de debug...")
    os.system("python test_rotation_debug.py")