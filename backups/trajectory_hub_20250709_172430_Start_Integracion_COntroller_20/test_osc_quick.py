# === test_osc_quick.py ===
# Test rápido de comunicación OSC

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import OSCTarget
import time

print("🧪 TEST RÁPIDO DE OSC")
print("=" * 50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)

# Configurar OSC
target = OSCTarget(host="127.0.0.1", port=9000, name="Spat_Test")
engine.osc_bridge.add_target(target)

print(f"✅ Target OSC configurado: {target.name}")

# Crear un macro simple
engine.create_macro("test", source_count=3)
print("✅ Macro 'test' creado con 3 fuentes")

# Mover las fuentes
print("\n📡 Enviando posiciones...")
for i in range(10):
    # Actualizar engine
    engine.update()
    
    # Mostrar progreso
    print(f"  Frame {i+1}/10 enviado")
    time.sleep(0.1)

stats = engine.osc_bridge.get_stats()
print(f"\n📊 Mensajes enviados: {stats.get('messages_sent', 0)}")
print("\n✅ Test completado - Verifica en Spat")
