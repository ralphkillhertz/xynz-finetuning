# === diagnose_macro_rotation_creation.py ===
# 🔍 Debug: Ver qué se crea cuando se configura macro_rotation
# ⚡ El componente no tiene calculate_delta

import os
import re

def find_set_macro_rotation():
    """Encontrar cómo se crea el componente macro_rotation"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando set_macro_rotation...")
    
    # Buscar el método
    pattern = r'def set_macro_rotation\s*\([^)]*\):(.*?)(?=\n    def|\n\s{0,4}def|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        method_content = match.group(0)
        print("\n📋 Método set_macro_rotation:")
        print("-" * 60)
        
        lines = method_content.split('\n')
        for i, line in enumerate(lines[:30]):  # Primeras 30 líneas
            print(f"{i+1:3d}: {line}")
            
            # Buscar dónde se crea el componente
            if 'macro_rotation' in line and '=' in line:
                print(f"\n⚠️ LÍNEA CLAVE: {line.strip()}")
                
                # Ver qué se está asignando
                if 'dict(' in line or '{}' in line:
                    print("   ❌ Se está creando un dict vacío!")
                elif 'MacroRotation(' in line:
                    print("   ✅ Se está creando MacroRotation correctamente")
                else:
                    print("   ⚠️ No está claro qué se está creando")
    
    # Buscar MacroRotation import
    print("\n🔍 Verificando imports de MacroRotation...")
    if 'from' in content and 'MacroRotation' in content:
        for line in content.split('\n'):
            if 'import' in line and 'MacroRotation' in line:
                print(f"✅ Import encontrado: {line.strip()}")
    else:
        print("❌ No se encontró import de MacroRotation")
    
    # Sugerir fix
    print("\n💡 El problema parece ser que se crea un dict vacío")
    print("   en lugar de una instancia de MacroRotation")

if __name__ == "__main__":
    find_set_macro_rotation()