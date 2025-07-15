# 🔧 Fix: Corregir parámetros del engine
# ⚡ Línea modificada: 632

print("🔧 Arreglando inicialización del engine...")

# Leer archivo
with open("trajectory_hub/interface/interactive_controller.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Corregir el parámetro n_sources → max_sources
content = content.replace(
    "engine = EnhancedTrajectoryEngine(\n        n_sources=100,",
    "engine = EnhancedTrajectoryEngine(\n        max_sources=100,"
)

# También corregir update_rate → fps
content = content.replace(
    "update_rate=60,",
    "fps=60,"
)

# Guardar
with open("trajectory_hub/interface/interactive_controller.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Parámetros del engine corregidos")
print("  - n_sources → max_sources")
print("  - update_rate → fps")
print("\n🚀 Prueba de nuevo:")
print("   python -m trajectory_hub.interface.interactive_controller")