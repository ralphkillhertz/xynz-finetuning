# === fix_update_signatures_smart.py ===
# 🔧 Fix: Corregir llamadas a update() detectando la firma correcta
# ⚡ Solución inteligente que maneja diferentes firmas

def fix_source_motion_update():
    """Corregir SourceMotion.update() para manejar diferentes firmas"""
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        lines = f.readlines()
    
    # Primero, revertir el cambio anterior (líneas 128 y 136)
    print("🔄 Revirtiendo cambio anterior...")
    for i in range(len(lines)):
        if 'component.update(current_time, dt, self.state)' in lines[i]:
            lines[i] = lines[i].replace(
                'component.update(current_time, dt, self.state)',
                'component.update(self.state, current_time, dt)'
            )
            print(f"   Línea {i+1}: Revertido a orden estándar")
    
    # Ahora, buscar el método update() de SourceMotion y hacerlo más inteligente
    in_source_motion_update = False
    indent_level = ""
    
    for i in range(len(lines)):
        # Detectar inicio de SourceMotion.update()
        if 'def update(self, current_time: float, dt: float) -> MotionState:' in lines[i] and i > 100 and i < 200:
            in_source_motion_update = True
            indent_level = lines[i][:lines[i].index('def')]
            print(f"\n📍 Encontrado SourceMotion.update() en línea {i+1}")
            continue
        
        # Detectar fin del método
        if in_source_motion_update and lines[i].strip() and not lines[i].startswith(indent_level + ' '):
            in_source_motion_update = False
            continue
        
        # Dentro del método, buscar las llamadas a component.update
        if in_source_motion_update and 'component.update(' in lines[i]:
            # Reemplazar con código más inteligente
            spaces = lines[i][:lines[i].index('new_state')]
            
            # Crear el código inteligente
            smart_code = f"""{spaces}# Llamar update con la firma correcta
{spaces}if component.__class__.__name__ in ['ManualMacroRotation', 'ManualIndividualRotation']:
{spaces}    # Estos componentes esperan (current_time, dt, state)
{spaces}    new_state = component.update(current_time, dt, self.state)
{spaces}elif component.__class__.__name__ == 'IndividualRotation':
{spaces}    # Este componente espera solo (current_time, dt)
{spaces}    component.update(current_time, dt)
{spaces}    new_state = self.state
{spaces}else:
{spaces}    # La mayoría espera (state, current_time, dt)
{spaces}    new_state = component.update(self.state, current_time, dt)
"""
            
            # Reemplazar la línea original
            lines[i] = smart_code
            print(f"   Línea {i+1}: Reemplazada con detección inteligente de firma")
    
    # Guardar cambios
    with open('trajectory_hub/core/motion_components.py', 'w') as f:
        f.writelines(lines)
    
    print("\n✅ SourceMotion.update() ahora maneja diferentes firmas inteligentemente!")

if __name__ == "__main__":
    fix_source_motion_update()
    print("\n🚀 Ejecuta: python test_7_deltas_final.py")