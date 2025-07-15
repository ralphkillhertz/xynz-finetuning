import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 DIAGNÓSTICO PROFUNDO OSC")
print("="*60)

# 1. Crear engine con debug
engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)

# 2. Verificar OSC bridge
print("\n📡 Estado OSC Bridge:")
print(f"   - Existe: {engine.osc_bridge is not None}")
print(f"   - Targets: {engine.osc_bridge.targets}")
print(f"   - Auto-reconnect: {engine.osc_bridge.auto_reconnect}")

# 3. Test envío directo
print("\n🧪 Test envío directo:")
try:
    pos = np.array([1.0, 2.0, 3.0])
    engine.osc_bridge.send_position(0, pos)
    stats = engine.osc_bridge.get_stats()
    print(f"   ✅ Envío directo OK: {stats['messages_sent']} mensajes")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Verificar _send_osc_update
print("\n🔍 Verificando _send_osc_update:")
if hasattr(engine, '_send_osc_update'):
    print("   ✅ Método existe")
    # Llamar manualmente
    try:
        engine._send_osc_update()
        stats = engine.osc_bridge.get_stats()
        print(f"   📊 Después de _send_osc_update: {stats['messages_sent']} mensajes")
    except Exception as e:
        print(f"   ❌ Error al llamar: {e}")
else:
    print("   ❌ Método NO existe")

# 5. Verificar update loop
print("\n🔍 Verificando update loop:")
print(f"   - running: {getattr(engine, 'running', 'NO EXISTE')}")
print(f"   - _update_thread: {hasattr(engine, '_update_thread')}")

# 6. Buscar en create_macro si envía OSC
print("\n🔍 Verificando create_macro:")
import inspect
source = inspect.getsource(engine.create_macro)
if "send_position" in source:
    print("   ✅ create_macro SÍ envía posiciones")
else:
    print("   ❌ create_macro NO envía posiciones")

# 7. Crear macro y verificar
print("\n🧪 Creando macro y verificando:")
before = engine.osc_bridge.get_stats()['messages_sent']
macro = engine.create_macro("test_debug", 3)
after = engine.osc_bridge.get_stats()['messages_sent']
print(f"   Mensajes antes: {before}")
print(f"   Mensajes después: {after}")
print(f"   Diferencia: {after - before}")

# 8. Forzar envío manual
print("\n🔧 Forzando envío manual:")
for i, sid in enumerate(macro.source_ids):
    if sid in engine._positions:
        engine.osc_bridge.send_position(sid, engine._positions[sid])
        print(f"   ✅ Enviada posición de fuente {sid}")

final_stats = engine.osc_bridge.get_stats()
print(f"\n📊 Stats finales: {final_stats['messages_sent']} mensajes totales")