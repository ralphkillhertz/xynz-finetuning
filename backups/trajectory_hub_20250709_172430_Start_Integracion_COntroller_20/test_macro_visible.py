# Test rápido
from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=10, fps=30)
macro = engine.create_macro("test_visible", 5, formation="circle")
print("✅ Macro creado - verifica en Spat")

# Forzar update para asegurar
engine.update(0.033)
print("✅ Update forzado")
