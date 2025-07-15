# === diagnose_structure.py ===
# 🔍 Diagnóstico: Ver la estructura completa alrededor del error

file_path = "trajectory_hub/core/motion_components.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

print("🔍 Analizando estructura alrededor de línea 108...")
print("\nContexto extendido (líneas 95-120):")

for i in range(max(0, 94), min(len(lines), 120)):
    line = lines[i]
    indent = len(line) - len(line.lstrip())
    
    # Marcar líneas importantes
    marker = ""
    if "class " in line:
        marker = " ← CLASE"
    elif line.strip().startswith("def "):
        marker = " ← MÉTODO"
    elif i == 107:  # Línea 108
        marker = " ← PROBLEMA AQUÍ"
    
    print(f"L{i+1:3d} ({indent:2d}sp): {line.rstrip()[:60]}{marker}")

# Buscar dónde DEBERÍA estar update_with_deltas
print("\n🔍 Buscando SourceMotion y sus métodos...")
source_motion_found = False
for i, line in enumerate(lines):
    if "class SourceMotion" in line:
        source_motion_found = True
        print(f"\n✅ SourceMotion encontrado en línea {i+1}")
        print("Métodos de SourceMotion:")
        
        # Mostrar estructura de la clase
        class_end = i + 100  # Ver los siguientes 100 líneas
        for j in range(i, min(class_end, len(lines))):
            line = lines[j]
            indent = len(line) - len(line.lstrip())
            
            if line.strip().startswith("class ") and j > i:
                print(f"\n❌ Siguiente clase encontrada en línea {j+1}")
                break
                
            if line.strip().startswith("def "):
                print(f"  L{j+1} ({indent}sp): {line.strip()[:60]}")

# Buscar update_with_deltas original
print("\n🔍 Buscando todas las ocurrencias de update_with_deltas...")
for i, line in enumerate(lines):
    if "update_with_deltas" in line:
        indent = len(line) - len(line.lstrip())
        print(f"  L{i+1} ({indent}sp): {line.strip()[:70]}")

# Analizar el problema específico
print("\n⚠️ ANÁLISIS DEL PROBLEMA:")
print("El método update_with_deltas está mal ubicado.")
print("Está dentro de otro método o bloque if, cuando debería estar al nivel de clase.")
print("\nNecesitamos:")
print("1. Eliminar el update_with_deltas mal ubicado (línea 108)")
print("2. Encontrar el update_with_deltas original o añadirlo en el lugar correcto")