# fix_manual_rotation_return_type.py
# Corrige el método update_with_deltas para que retorne lista de deltas

import ast

def fix_update_with_deltas():
    print("🔧 Corrigiendo update_with_deltas para retornar lista de deltas...")
    
    # Leer motion_components.py
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    # Buscar el método update_with_deltas en SourceMotion
    lines = content.split('\n')
    in_update_method = False
    method_indent = 0
    new_lines = []
    fixed = False
    
    for i, line in enumerate(lines):
        # Buscar el método
        if 'def update_with_deltas(self, current_time, dt):' in line and not fixed:
            in_update_method = True
            method_indent = len(line) - len(line.lstrip())
            new_lines.append(line)
            
            # Reemplazar todo el método con la versión correcta
            indent = ' ' * (method_indent + 4)
            new_lines.extend([
                f'{indent}"""Actualiza el estado y retorna lista de deltas."""',
                f'{indent}deltas = []',
                f'{indent}',
                f'{indent}# Procesar cada componente activo',
                f'{indent}for comp_name, component in self.active_components.items():',
                f'{indent}    if hasattr(component, "enabled") and component.enabled:',
                f'{indent}        if hasattr(component, "calculate_delta"):',
                f'{indent}            delta = component.calculate_delta(self.state, current_time, dt)',
                f'{indent}            if delta and (abs(delta.position).sum() > 0.001 or ',
                f'{indent}                         abs(delta.orientation).sum() > 0.001):',
                f'{indent}                deltas.append(delta)',
                f'{indent}',
                f'{indent}    # Actualizar componente si tiene update',
                f'{indent}    if hasattr(component, "update"):',
                f'{indent}        component.update(current_time, dt, self.state)',
                f'{indent}',
                f'{indent}# Actualizar tiempo',
                f'{indent}self.state.last_update = current_time',
                f'{indent}',
                f'{indent}# IMPORTANTE: Retornar lista de deltas, no el state',
                f'{indent}return deltas',
                ''
            ])
            
            # Saltar las líneas del método original
            j = i + 1
            while j < len(lines):
                line_indent = len(lines[j]) - len(lines[j].lstrip())
                if lines[j].strip() and line_indent <= method_indent:
                    break
                j += 1
            
            # Continuar desde donde terminó el método
            in_update_method = False
            fixed = True
            i = j - 1
            
        elif not in_update_method:
            new_lines.append(line)
    
    # Guardar
    with open('trajectory_hub/core/motion_components.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ update_with_deltas corregido para retornar lista de deltas")
    
    # También verificar que engine.update() maneje correctamente la lista
    print("\n🔍 Verificando engine.update()...")
    
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        engine_content = f.read()
    
    if 'for delta in deltas:' in engine_content:
        print("✅ engine.update() ya maneja correctamente la lista de deltas")
    else:
        print("⚠️ engine.update() podría necesitar ajustes")

if __name__ == "__main__":
    fix_update_with_deltas()
    
    print("\n📝 Próximo paso:")
    print("python debug_rotation_final.py")
    print("\nSi las rotaciones funcionan, el sistema de deltas estará 100% completo!")