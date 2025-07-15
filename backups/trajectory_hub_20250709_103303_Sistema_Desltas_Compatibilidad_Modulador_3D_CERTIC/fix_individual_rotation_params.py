# === fix_individual_rotation_params.py ===
# 🔧 Fix: Corregir parámetros de set_individual_rotation
# ⚡ Cambiar speed_x/y/z por pitch/yaw/roll

def fix_test_file():
    """Corregir los parámetros en test_7_deltas_final.py"""
    with open('test_7_deltas_final.py', 'r') as f:
        content = f.read()
    
    # Corregir set_individual_rotation
    old_line = 'engine.set_individual_rotation(test_source, speed_x=0, speed_y=1.0, speed_z=0)'
    new_line = 'engine.set_individual_rotation(test_source, pitch=0, yaw=1.0, roll=0)'
    
    content = content.replace(old_line, new_line)
    
    # Guardar cambios
    with open('test_7_deltas_final.py', 'w') as f:
        f.write(content)
    
    print("✅ Corregido set_individual_rotation!")
    print("   - Cambiado: speed_x/y/z")
    print("   - Por: pitch/yaw/roll")

if __name__ == "__main__":
    fix_test_file()
    print("\n🚀 Ejecuta: python test_7_deltas_final.py")