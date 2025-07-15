# === diagnose_line_257_context.py ===
# 🔍 Ver el contexto completo alrededor de línea 257
# ⚡ Entender el problema real

import os

print("🔍 DIAGNÓSTICO COMPLETO: Línea 257 y contexto\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Mostrar líneas 250-265 con detalle
print("📝 Contexto (líneas 250-265):")
print("="*60)
for i in range(249, min(265, len(lines))):
    line = lines[i]
    # Mostrar espacios como puntos
    visible = line.replace(' ', '·').replace('\t', '→→→→')
    print(f"{i+1:3d}: {visible}", end='')
    
    # Marcar líneas importantes
    if i == 255:
        print("     ^^^ Línea antes del def")
    elif i == 256:
        print("     ^^^ LÍNEA 257 CON ERROR")
print("="*60)

# Analizar el problema
print("\n🔍 ANÁLISIS:")
if lines[255].strip().endswith(':'):
    print("✅ Línea 256 termina con ':' - espera bloque indentado")
    indent_256 = len(lines[255]) - len(lines[255].lstrip())
    indent_257 = len(lines[256]) - len(lines[256].lstrip())
    print(f"  Indentación línea 256: {indent_256} espacios")
    print(f"  Indentación línea 257: {indent_257} espacios")
    print(f"  Necesita: {indent_256 + 4} espacios")

# Fix automático basado en análisis
print("\n🔧 APLICANDO FIX CORRECTO...")

# Encontrar la indentación correcta
for i in range(250, 260):
    if 'def create_macro' in lines[i]:
        def_indent = len(lines[i]) - len(lines[i].lstrip())
        docstring_indent = def_indent + 4
        
        # Corregir línea 257 y siguientes del docstring
        for j in range(256, min(270, len(lines))):
            if lines[j].strip().startswith('"""') or lines[j].strip().startswith('Parameters') or lines[j].strip().startswith('Returns'):
                lines[j] = ' ' * docstring_indent + lines[j].lstrip()
                print(f"✅ Corregida línea {j+1}")
            elif lines[j].strip() and j < 265:  # Parte del docstring
                # Mantener indentación relativa
                if not lines[j].startswith(' ' * docstring_indent):
                    lines[j] = ' ' * docstring_indent + lines[j].lstrip()
        break

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print("\n✅ Archivo corregido")

# Test final
print("\n🧪 TEST FINAL:")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
    engine.create_macro("test", 3)
    
    if hasattr(engine, '_macros') and "test" in engine._macros:
        print("✅ Macro creado y guardado")
        print("\n🎉 ¡PROBLEMA RESUELTO!")
    else:
        print("❌ Macro no se guardó")
        
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Si sigue fallando, mostrar más contexto
    if "line 257" in str(e):
        print("\n🔍 Contenido actual línea 257:")
        with open(file_path, 'r') as f:
            lines = f.readlines()
        if len(lines) > 256:
            print(f"  {repr(lines[256])}")