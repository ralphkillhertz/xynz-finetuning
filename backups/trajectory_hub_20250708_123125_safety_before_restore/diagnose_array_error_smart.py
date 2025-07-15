# === diagnose_array_error_smart.py ===
# 🎯 Diagnóstico inteligente del error array ambiguous
# ⚡ Wrapper de componentes para detectar comparaciones

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import MacroRotation
import traceback

class DiagnosticWrapper:
    """Wrapper que intercepta operaciones problemáticas"""
    def __init__(self, obj, name):
        self._obj = obj
        self._name = name
        
    def __getattr__(self, attr):
        value = getattr(self._obj, attr)
        if attr in ['enabled', 'active', '__eq__', '__bool__']:
            print(f"\n🔍 {self._name}.{attr} accedido")
            print(f"   Tipo: {type(value)}")
            if isinstance(value, np.ndarray):
                print(f"   ⚠️ ES UN ARRAY! Shape: {value.shape}")
                print(f"   Contenido: {value}")
        return value
        
    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            super().__setattr__(attr, value)
        else:
            setattr(self._obj, attr, value)

# Test con wrapper
print("🔧 Iniciando diagnóstico inteligente...\n")

try:
    engine = EnhancedTrajectoryEngine(n_sources=10, fps=60)
    
    # Crear macro
    engine.create_macro("test", [0, 1, 2])
    
    # Aplicar rotación
    engine.set_macro_rotation("test", "circular", speed=1.0)
    
    # Wrappear el componente de rotación para debugging
    for sid in [0, 1, 2]:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components') and 'macro_rotation' in motion.active_components:
                original = motion.active_components['macro_rotation']
                motion.active_components['macro_rotation'] = DiagnosticWrapper(original, f"MacroRotation[{sid}]")
    
    # Ejecutar update con try/except detallado
    print("\n🔄 Ejecutando engine.update()...\n")
    
    try:
        engine.update()
    except Exception as e:
        print(f"\n❌ ERROR CAPTURADO: {type(e).__name__}")
        print(f"   Mensaje: {e}")
        print("\n📍 Traceback completo:")
        traceback.print_exc()
        
        # Inspeccionar estado
        print("\n🔍 Inspeccionando estado de los componentes:")
        for sid in [0, 1, 2]:
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                print(f"\n  Source {sid}:")
                if hasattr(motion, 'active_components'):
                    for comp_name, comp in motion.active_components.items():
                        if hasattr(comp, 'enabled'):
                            print(f"    {comp_name}.enabled = {comp.enabled} (tipo: {type(comp.enabled)})")
                            
except Exception as e:
    print(f"\n💥 Error durante setup: {e}")
    traceback.print_exc()

# Test específico de MacroRotation
print("\n\n🧪 Test directo de MacroRotation:")
try:
    from trajectory_hub.core.types import MotionState
    
    # Crear instancia limpia
    rotation = MacroRotation()
    state = MotionState()
    state.position = np.array([1.0, 0.0, 0.0])
    
    # Probar calculate_delta directamente
    print("✅ Probando calculate_delta...")
    delta = rotation.calculate_delta(state, 0.0, 0.016)
    print(f"   Delta: {delta}")
    print(f"   Tipo delta.position: {type(delta.position)}")
    
    # Verificar atributos
    print("\n🔍 Atributos de MacroRotation:")
    for attr in ['enabled', 'rotation_type', 'speed', 'phase']:
        if hasattr(rotation, attr):
            value = getattr(rotation, attr)
            print(f"   {attr} = {value} (tipo: {type(value)})")
            
except Exception as e:
    print(f"❌ Error en test directo: {e}")
    traceback.print_exc()