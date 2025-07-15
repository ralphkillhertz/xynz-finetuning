# === fix_motion_state_update.py ===
# 🔧 Fix: Corregir motion.state que se convierte en float
# ⚡ El problema es que motion.update() retorna un estado, no debe asignarse

def fix_update_method():
    """Corregir el método update en enhanced_trajectory_engine.py"""
    
    # Leer el archivo
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar y corregir el problema
    fixed = False
    for i in range(len(lines)):
        # Buscar líneas donde motion.update() se asigna a motion.state
        if 'motion.state = motion.update(' in lines[i]:
            print(f"❌ Encontrado problema en línea {i+1}: {lines[i].strip()}")
            # Cambiar a solo llamar update sin asignar
            lines[i] = lines[i].replace('motion.state = motion.update(', 'motion.update(')
            print(f"✅ Corregido a: {lines[i].strip()}")
            fixed = True
        
        # También buscar variantes
        elif 'state = motion.update(' in lines[i] and 'motion.state' not in lines[i]:
            print(f"⚠️ Posible problema en línea {i+1}: {lines[i].strip()}")
    
    if fixed:
        # Guardar cambios
        with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'w') as f:
            f.writelines(lines)
        print("\n✅ Archivo corregido!")
    else:
        print("\n🔍 No se encontró la asignación problemática")
        print("📋 Buscando otros patrones...")
        
        # Buscar donde motion se actualiza
        for i in range(1900, min(len(lines), 1950)):
            if 'motion' in lines[i] and 'update' in lines[i]:
                print(f"   Línea {i+1}: {lines[i].strip()}")

if __name__ == "__main__":
    fix_update_method()
    print("\n🚀 Ejecuta: python test_7_deltas_final.py")