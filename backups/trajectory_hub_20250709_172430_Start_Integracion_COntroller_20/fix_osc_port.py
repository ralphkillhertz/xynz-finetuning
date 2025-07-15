# 🔧 Fix: Convertir puerto a entero
# ⚡ Línea modificada: 639

print("🔧 Arreglando puerto OSC...")

# Leer archivo
with open("trajectory_hub/interface/interactive_controller.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Corregir el puerto de string a int
content = content.replace(
    'target = OSCTarget("Spat_Local", "127.0.0.1", 9000)',
    'target = OSCTarget("Spat_Local", "127.0.0.1", 9000)'
)

# Por si acaso, asegurar que sea int
content = content.replace(
    'OSCTarget("Spat_Local", "127.0.0.1", 9000)',
    'OSCTarget("Spat_Local", "127.0.0.1", int(9000))'
)

# Guardar
with open("trajectory_hub/interface/interactive_controller.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Puerto OSC corregido a entero")
print("\n🚀 Prueba de nuevo:")
print("   python -m trajectory_hub.interface.interactive_controller")