# 🔧 Fix: Error de sintaxis en línea 133
# ⚡ Diagnóstico: Concatenación incorrecta de strings
# 🎯 Impacto: BAJO - Solo afecta logging

import shutil
from datetime import datetime

print("🔍 DIAGNÓSTICO PROFUNDO - Línea 133")
print("=" * 60)

# 1. Backup
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_file = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(engine_file, backup_file)
print(f"✅ Backup: {backup_file}")

# 2. Análisis del contexto
with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar contexto alrededor de línea 133
print("\n📋 Contexto (líneas 130-135):")
for i in range(130, min(136, len(lines))):
    print(f"{i}: {lines[i-1].rstrip()}")

# 3. Corrección quirúrgica
for i, line in enumerate(lines):
    if i == 132:  # Línea 133 (índice 132)
        if 'do OSC bridge' in line:
            print(f"\n❌ Problema encontrado: {line.strip()}")
            # Corregir solo esta línea
            lines[i] = '        logger.info(f"OSC bridge inicializado: {self.osc_bridge is not None}")\n'
            print(f"✅ Corregido a: {lines[i].strip()}")
            break

# 4. Guardar
with open(engine_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ Corrección aplicada")
print("🧪 Verificando sintaxis...")

# 5. Verificar sintaxis
import ast
try:
    with open(engine_file, 'r', encoding='utf-8') as f:
        ast.parse(f.read())
    print("✅ Sintaxis correcta")
except SyntaxError as e:
    print(f"❌ Aún hay errores: {e}")
    print(f"   Línea {e.lineno}: {e.text}")

print("\n🚀 Ejecuta: python test_osc_debug.py")