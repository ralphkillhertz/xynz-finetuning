from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
print("Stats antes:", engine.osc_bridge.get_stats()['messages_sent'])

# Crear macro debe enviar posiciones ahora
macro = engine.create_macro("test_osc_fix", 5, formation="circle")

stats = engine.osc_bridge.get_stats()
print(f"Stats después: {stats['messages_sent']} mensajes")
print(f"✅ Verifica en Spat que aparezcan 5 fuentes")
