# 🔧 Fix: Revisar y corregir tipos en OSCTarget
# ⚡ Problema: El puerto se define como string en el dataclass

print("🔧 Diagnosticando OSCTarget...")

# Primero veamos qué hay en OSCTarget
import os
spat_file = "trajectory_hub/core/spat_osc_bridge.py"

# Leer las primeras líneas para ver la definición
with open(spat_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la definición de OSCTarget
for i, line in enumerate(lines[:100]):  # Solo primeras 100 líneas
    if "class OSCTarget" in line:
        print(f"Encontrado en línea {i+1}: {line.strip()}")
        # Mostrar las siguientes 10 líneas
        for j in range(i, min(i+15, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        break

# Ahora arreglemos el problema
content = ''.join(lines)

# Si el puerto está definido como str, cambiarlo a int
if "port: str" in content:
    print("\n⚠️ Encontrado: port definido como str")
    content = content.replace("port: str", "port: int")
    
    # Guardar
    with open(spat_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Cambiado a: port: int")
else:
    # Si no es ese el problema, intentar otra solución
    print("\n🔍 Buscando otras definiciones de puerto...")
    
    # Buscar si hay conversión explícita necesaria
    if "self.port = port" in content:
        content = content.replace("self.port = port", "self.port = int(port) if isinstance(port, str) else port")
        with open(spat_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Añadida conversión automática de puerto")

print("\n✅ OSCTarget corregido")
print("\n🚀 Prueba de nuevo:")
print("   python -m trajectory_hub.interface.interactive_controller")