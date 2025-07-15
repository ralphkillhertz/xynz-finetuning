# === fix_individual_trajectory_macro.py ===
# 🔧 Fix: Añadir macro_id a set_individual_trajectory
# ⚡ Corrección del parámetro faltante

def fix_test_file():
    """Corregir el archivo de test"""
    with open('test_7_deltas_final.py', 'r') as f:
        content = f.read()
    
    # Corregir la línea problemática
    old_line = 'engine.set_individual_trajectory(source_id=test_source, shape="spiral", speed=1.0)'
    new_line = 'engine.set_individual_trajectory(macro_id="macro_0_test_group_1", source_id=test_source, shape="spiral", speed=1.0)'
    
    content = content.replace(old_line, new_line)
    
    with open('test_7_deltas_final.py', 'w') as f:
        f.write(content)
    
    print("✅ Archivo corregido - añadido macro_id!")

if __name__ == "__main__":
    fix_test_file()
    print("\n🚀 Ejecuta: python test_7_deltas_final.py")