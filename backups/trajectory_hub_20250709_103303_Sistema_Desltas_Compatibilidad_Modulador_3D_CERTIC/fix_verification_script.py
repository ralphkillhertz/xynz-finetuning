# === fix_verification_script.py ===
# 🔧 Fix: Corregir nombres de macros en script de verificación
# ⚡ Arreglar el problema con macro.name vs macro_id real

def fix_verification():
    """Corregir el script de verificación"""
    
    with open('comprehensive_system_verification.py', 'r') as f:
        content = f.read()
    
    # Correcciones necesarias
    fixes = [
        # Test 1 - usar el ID completo del macro
        ('engine.set_macro_trajectory(macro.name,', 
         'engine.set_macro_trajectory(f"macro_0_{macro.name}",'),
        
        ('engine.set_macro_rotation(macro.name,',
         'engine.set_macro_rotation(f"macro_0_{macro.name}",'),
         
        ('engine.set_individual_trajectory(macro.name,',
         'engine.set_individual_trajectory(f"macro_0_{macro.name}",'),
         
        # Test 2
        ('engine.set_macro_concentration(macro.name,',
         'engine.set_macro_concentration(f"macro_0_{macro.name}",'),
    ]
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Guardar cambios
    with open('comprehensive_system_verification.py', 'w') as f:
        f.write(content)
    
    print("✅ Script de verificación corregido!")
    print("   - Ahora usa el ID completo del macro (macro_0_xxx)")

if __name__ == "__main__":
    fix_verification()
    print("\n🚀 Ejecuta: python comprehensive_system_verification.py")