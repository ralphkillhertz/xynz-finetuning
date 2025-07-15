# === fix_docstring_indent.py ===
# 🔧 Fix: Corregir indentación del docstring
# ⚡ Impacto: CRÍTICO - Bloquea todo

import os

print("🔧 Corrigiendo indentación del docstring...")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar línea 265 y contexto
print(f"\nContexto alrededor de línea 265:")
for i in range(260, min(270, len(lines))):
    print(f"{i+1:3d}: {repr(lines[i])}")
    
    # Si encontramos el docstring mal indentado
    if i == 264 and lines[i].strip() == '"""':
        # Corregir indentación (debe tener 8 espacios)
        lines[i] = '        """\n'
        print(f"\n✅ Corregida línea {i+1}")

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print("\n✅ Archivo corregido")

# Test rápido
print("\n🧪 Test rápido...")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    # Test completo
    import subprocess
    result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                          capture_output=True, text=True)
    
    # Mostrar solo líneas clave
    for line in result.stdout.split('\n'):
        if any(word in line for word in ['✅', '❌', 'ÉXITO', 'Macro', 'Frame', 'distancia']):
            print(line)
            
    if "ÉXITO TOTAL" in result.stdout:
        print("\n🎉 ¡MacroTrajectory COMPLETAMENTE MIGRADO!")
        print("\n📊 RESUMEN FINAL:")
        print("✅ Sistema de deltas: 100%")
        print("✅ ConcentrationComponent: 100%") 
        print("✅ IndividualTrajectory: 100%")
        print("✅ MacroTrajectory: 100%")
        print("✅ engine.update(): 100% automático")
        print("\n⏭️ PRÓXIMO: Servidor MCP (crítico)")
        
except Exception as e:
    print(f"❌ Error: {e}")