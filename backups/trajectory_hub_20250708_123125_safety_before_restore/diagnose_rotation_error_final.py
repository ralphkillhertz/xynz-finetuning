# === diagnose_rotation_error_final.py ===
# 🎯 Diagnóstico definitivo del error de rotación
# ⚡ Con imports y parámetros correctos

import numpy as np
import traceback
import sys

# Agregar el directorio al path
sys.path.insert(0, '.')

# Imports correctos
from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from core.motion_components import MacroRotation, MotionState

print("🔧 Diagnóstico del error de rotación MS\n")

# 1. Test del constructor
print("1️⃣ Verificando constructor del engine...")
try:
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado correctamente")
except Exception as e:
    print(f"❌ Error creando engine: {e}")
    print("   Intentando con parámetros por defecto...")
    try:
        engine = EnhancedTrajectoryEngine()
        print("✅ Engine creado con parámetros por defecto")
    except Exception as e2:
        print(f"❌ Error fatal: {e2}")
        sys.exit(1)

# 2. Crear macro y aplicar rotación
print("\n2️⃣ Creando macro con rotación...")
try:
    engine.create_macro("test", [0, 1, 2])
    print("✅ Macro creado")
    
    # Verificar que set_macro_rotation existe
    if hasattr(engine, 'set_macro_rotation'):
        engine.set_macro_rotation("test", "circular", speed=1.0)
        print("✅ Rotación aplicada")
    else:
        print("❌ Método set_macro_rotation no encontrado")
        print("   Métodos disponibles:")
        for method in dir(engine):
            if 'rotation' in method.lower():
                print(f"     - {method}")
except Exception as e:
    print(f"❌ Error en setup: {e}")
    traceback.print_exc()

# 3. Ejecutar update con análisis detallado
print("\n3️⃣ Ejecutando engine.update() con análisis...")

# Interceptar comparaciones problemáticas
class ArrayChecker:
    """Helper para detectar comparaciones de arrays"""
    @staticmethod
    def check_value(name, value):
        if isinstance(value, np.ndarray):
            print(f"⚠️  {name} es un array numpy: shape={value.shape}, dtype={value.dtype}")
            if value.shape != ():  # No es escalar
                print(f"    Contenido: {value}")
                return True
        return False

# Inspeccionar antes del update
print("\n🔍 Estado antes del update:")
if hasattr(engine, 'motion_states'):
    for sid, motion in engine.motion_states.items():
        if hasattr(motion, 'active_components'):
            for comp_name, comp in motion.active_components.items():
                if comp_name == 'macro_rotation' and comp:
                    print(f"\n  Componente {comp_name} en source {sid}:")
                    # Verificar atributos críticos
                    for attr in ['enabled', 'speed', 'phase', 'rotation_type']:
                        if hasattr(comp, attr):
                            val = getattr(comp, attr)
                            ArrayChecker.check_value(f"{attr}", val)

# Ejecutar update
print("\n🔄 Ejecutando update...")
try:
    # Primer intento - capturar el error exacto
    engine.update()
    print("✅ Update ejecutado sin errores (!)")
    
except ValueError as e:
    if "ambiguous" in str(e):
        print(f"\n❌ ERROR DE ARRAY AMBIGUO DETECTADO!")
        print(f"   Mensaje: {e}")
        
        # Análisis post-error
        print("\n📍 Análisis post-error:")
        
        # Buscar en el código de update_with_deltas
        print("\n   Revisando SourceMotion.update_with_deltas...")
        if hasattr(engine, 'motion_states'):
            for sid, motion in engine.motion_states.items():
                if hasattr(motion, 'active_components'):
                    print(f"\n   Source {sid} componentes activos:")
                    for name, comp in motion.active_components.items():
                        if comp:
                            print(f"     - {name}: {type(comp).__name__}")
                            if hasattr(comp, 'enabled'):
                                enabled_val = getattr(comp, 'enabled')
                                if ArrayChecker.check_value(f"{name}.enabled", enabled_val):
                                    print(f"       🔴 PROBLEMA: enabled es un array!")
        
        # Mostrar traceback
        print("\n📋 Traceback completo:")
        traceback.print_exc()
        
except Exception as e:
    print(f"\n❌ Error diferente: {type(e).__name__}: {e}")
    traceback.print_exc()

# 4. Test aislado de MacroRotation
print("\n\n4️⃣ Test aislado de MacroRotation:")
try:
    rotation = MacroRotation()
    state = MotionState()
    state.position = np.array([1.0, 0.0, 0.0])
    
    # Verificar enabled
    print(f"✓ rotation.enabled = {rotation.enabled} (tipo: {type(rotation.enabled)})")
    
    # Test calculate_delta
    delta = rotation.calculate_delta(state, 0.0, 0.016)
    print(f"✓ calculate_delta funciona: delta.position = {delta.position}")
    
    # Verificar que enabled no se haya convertido en array
    print(f"✓ rotation.enabled después = {rotation.enabled} (tipo: {type(rotation.enabled)})")
    
except Exception as e:
    print(f"❌ Error en test aislado: {e}")
    traceback.print_exc()

print("\n✅ Diagnóstico completado")