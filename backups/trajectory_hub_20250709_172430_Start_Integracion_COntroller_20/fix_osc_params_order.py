# 🔧 Fix: Corregir orden de parámetros en OSCTarget
# ⚡ Problema: Orden incorrecto (name, host, port) vs (host, port, name)

print("🔧 Arreglando orden de parámetros OSCTarget...")

# Leer archivo
with open("trajectory_hub/interface/interactive_controller.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Corregir el orden: host, port, name
content = content.replace(
    'target = OSCTarget("Spat_Local", "127.0.0.1", int(9000))',
    'target = OSCTarget(host="127.0.0.1", port=9000, name="Spat_Local")'
)

# Guardar
with open("trajectory_hub/interface/interactive_controller.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Orden de parámetros corregido")
print("  Antes: OSCTarget(name, host, port)")
print("  Ahora: OSCTarget(host=..., port=..., name=...)")
print("\n🚀 Prueba de nuevo:")
print("   python -m trajectory_hub.interface.interactive_controller")