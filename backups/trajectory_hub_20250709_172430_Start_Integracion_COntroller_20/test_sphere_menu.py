# Test rápido de sphere en menú
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController

engine = EnhancedTrajectoryEngine(max_sources=20, fps=30)
controller = InteractiveController(engine)

# Verificar que sphere está disponible
print("🔍 Verificando formaciones disponibles...")

# Simular creación directa
print("\n🧪 Creando macro con sphere directamente:")
macro = engine.create_macro("test_sphere", 10, formation="sphere")
print(f"✅ Macro creado: {macro.name}")

stats = engine.osc_bridge.get_stats()
print(f"📡 OSC: {stats['messages_sent']} mensajes enviados")
