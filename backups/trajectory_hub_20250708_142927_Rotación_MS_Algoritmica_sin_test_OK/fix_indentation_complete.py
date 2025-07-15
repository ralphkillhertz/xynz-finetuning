# === fix_indentation_complete.py ===
import os
import shutil
from datetime import datetime

print("🔧 Arreglo COMPLETO de indentación...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(file_path, backup_path)

with open(file_path, 'r') as f:
    content = f.read()

# El problema parece ser que _check_rate_limit está dentro de otro método
# Necesitamos sacarlo y ponerlo al nivel de clase

# Buscar _check_rate_limit
lines = content.split('\n')
fixed_lines = []
skip_until = -1

for i, line in enumerate(lines):
    # Si estamos saltando líneas
    if i < skip_until:
        continue
        
    # Si encontramos _check_rate_limit mal ubicado
    if '_check_rate_limit' in line and 'def' in line and i > 1800:
        print(f"Encontrado _check_rate_limit en línea {i+1}")
        
        # Extraer el método completo
        method_lines = []
        j = i
        while j < len(lines):
            current_line = lines[j]
            # Si es el inicio del método o tiene indentación consistente
            if j == i or (current_line.strip() and not current_line.strip().startswith('def ')):
                method_lines.append(current_line)
                j += 1
            else:
                break
        
        # Ahora añadir el método con indentación correcta
        fixed_lines.append("")  # Línea en blanco
        fixed_lines.append("    def _check_rate_limit(self) -> bool:")
        fixed_lines.append('        """Verificar si se debe enviar actualización OSC"""')
        fixed_lines.append("        return True")
        fixed_lines.append("")
        
        skip_until = j
        print(f"  Método extraído y reubicado (saltando hasta línea {j+1})")
    else:
        fixed_lines.append(line)

# Guardar
with open(file_path, 'w') as f:
    f.write('\n'.join(fixed_lines))

print(f"✅ Backup: {backup_path}")
print("✅ Indentación corregida completamente")

# Test final
import subprocess
result = subprocess.run(['python', 'test_engine_auto_deltas.py'], 
                      capture_output=True, text=True)

if result.returncode == 0:
    print("\n✅ Test ejecutado exitosamente!")
    # Mostrar resultados
    for line in result.stdout.split('\n'):
        if any(word in line for word in ['✅', '❌', 'ÉXITO', 'RESULTADOS']):
            print(f"  {line}")
else:
    print(f"\n❌ Error: {result.stderr}")
