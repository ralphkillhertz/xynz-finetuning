#!/usr/bin/env python3
"""Test macro visible en Spat"""

from trajectory_hub import EnhancedTrajectoryEngine
import time

print("🧪 TEST MACRO VISIBLE EN SPAT")
print("="*60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=20, fps=30)
print("✅ Engine creado")

# Stats iniciales
stats_before = engine.osc_bridge.get_stats()
print(f"📊 Mensajes antes: {stats_before['messages_sent']}")

# Crear macro
macro = engine.create_macro("visible_test", 10, formation="spiral")
print(f"✅ Macro '{macro.name}' creado con {len(macro.source_ids)} fuentes")

# Stats después
stats_after = engine.osc_bridge.get_stats()
print(f"📊 Mensajes después: {stats_after['messages_sent']}")
print(f"📡 Diferencia: {stats_after['messages_sent'] - stats_before['messages_sent']} mensajes")

# Ejecutar algunos updates
print("\n🔄 Ejecutando updates...")
for i in range(5):
    engine.update()
    time.sleep(0.1)
    
    if i % 2 == 0:
        stats = engine.osc_bridge.get_stats()
        print(f"   Frame {i}: {stats['messages_sent']} total, {stats['parameters_sent']['positions']} posiciones")

# Resumen final
final_stats = engine.osc_bridge.get_stats()
print(f"\n📊 RESUMEN FINAL:")
print(f"   - Total mensajes: {final_stats['messages_sent']}")
print(f"   - Posiciones enviadas: {final_stats['parameters_sent']['positions']}")
print(f"   - Nombres enviados: {final_stats['parameters_sent']['names']}")
print(f"   - Errores: {final_stats['messages_failed']}")

print("\n✅ TEST COMPLETADO")
print("💡 Verifica en Spat:")
print("   1. Deberías ver 10 fuentes nuevas")
print("   2. Con nombres visible_test_0 a visible_test_9")
print("   3. En formación espiral")