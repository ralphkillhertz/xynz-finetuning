import inspect
from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge

print("🔍 DIAGNÓSTICO API OSC")
print("="*60)

# Crear instancia
bridge = SpatOSCBridge()

# Métodos disponibles
print("\n📋 Métodos de SpatOSCBridge:")
for name, method in inspect.getmembers(bridge, inspect.ismethod):
    if not name.startswith('_'):
        sig = inspect.signature(method)
        print(f"  - {name}{sig}")

# Atributos
print("\n📋 Atributos:")
for attr in dir(bridge):
    if not attr.startswith('_') and not callable(getattr(bridge, attr)):
        val = getattr(bridge, attr)
        print(f"  - {attr}: {type(val).__name__} = {val}")

# Test directo
print("\n🧪 Test directo:")
try:
    # Ver targets existentes
    print(f"Targets actuales: {bridge.targets}")
    
    # Si add_target necesita OSCTarget
    from trajectory_hub.core.spat_osc_bridge import OSCTarget
    target = OSCTarget("Test", "127.0.0.1", 9000)
    print(f"OSCTarget creado: {target}")
    
except Exception as e:
    print(f"Error: {e}")