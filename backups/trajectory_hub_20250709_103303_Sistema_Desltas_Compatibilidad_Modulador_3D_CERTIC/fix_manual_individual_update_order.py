# === fix_manual_individual_update_order.py ===
# 🔧 Fix: Corregir orden de parámetros en component.update()
# ⚡ El problema es que los parámetros están en orden incorrecto

def fix_source_motion_update():
    """Corregir el orden de parámetros en SourceMotion.update()"""
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar y corregir las llamadas a component.update
    fixed_count = 0
    for i in range(len(lines)):
        # Buscar la línea problemática
        if 'component.update(self.state, current_time, dt)' in lines[i]:
            print(f"❌ Encontrado orden incorrecto en línea {i+1}")
            print(f"   Antes: {lines[i].strip()}")
            
            # Corregir el orden: debe ser (current_time, dt, state)
            lines[i] = lines[i].replace(
                'component.update(self.state, current_time, dt)',
                'component.update(current_time, dt, self.state)'
            )
            
            print(f"   Después: {lines[i].strip()}")
            fixed_count += 1
        
        # También buscar variantes similares
        elif 'component.update(state, current_time, dt)' in lines[i]:
            print(f"❌ Encontrado orden incorrecto en línea {i+1}")
            lines[i] = lines[i].replace(
                'component.update(state, current_time, dt)',
                'component.update(current_time, dt, state)'
            )
            fixed_count += 1
    
    if fixed_count > 0:
        # Guardar cambios
        with open('trajectory_hub/core/motion_components.py', 'w') as f:
            f.writelines(lines)
        
        print(f"\n✅ Corregidas {fixed_count} llamadas a component.update()")
        print("   Orden correcto: (current_time, dt, state)")
    else:
        print("\n⚠️ No se encontraron las líneas problemáticas")

if __name__ == "__main__":
    fix_source_motion_update()
    print("\n🚀 Ejecuta: python test_7_deltas_final.py")