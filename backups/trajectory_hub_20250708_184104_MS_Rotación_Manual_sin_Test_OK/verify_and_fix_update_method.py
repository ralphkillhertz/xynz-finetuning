# verify_and_fix_update_method.py
# Verifica y corrige el método update_with_deltas

def verify_and_fix():
    print("🔍 Verificando el método update_with_deltas actual...")
    
    # Leer el archivo
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    # Buscar el método update_with_deltas
    lines = content.split('\n')
    
    # Primero, encontrar dónde está el método
    method_start = -1
    for i, line in enumerate(lines):
        if 'def update_with_deltas(self, current_time, dt):' in line:
            method_start = i
            print(f"✅ Encontrado update_with_deltas en línea {i + 1}")
            break
    
    if method_start == -1:
        print("❌ No se encontró el método update_with_deltas")
        return
    
    # Mostrar las líneas actuales del método
    print("\n📋 Contenido actual del método:")
    method_indent = len(lines[method_start]) - len(lines[method_start].lstrip())
    print(f"Indentación del método: {method_indent} espacios")
    
    # Encontrar el final del método
    method_end = method_start + 1
    for i in range(method_start + 1, len(lines)):
        if lines[i].strip() == '':
            continue
        line_indent = len(lines[i]) - len(lines[i].lstrip())
        if line_indent <= method_indent and lines[i].strip():
            method_end = i
            break
    else:
        method_end = len(lines)
    
    # Mostrar el método actual
    for i in range(method_start, min(method_end, method_start + 20)):
        print(f"{i+1:4d}: {lines[i]}")
    
    # Verificar si retorna state o deltas
    method_content = '\n'.join(lines[method_start:method_end])
    if 'return self.state' in method_content:
        print("\n❌ El método está retornando self.state (incorrecto)")
        print("🔧 Corrigiendo...")
        
        # Reemplazar el método completo
        new_method = [
            lines[method_start],  # def update_with_deltas...
            ' ' * (method_indent + 4) + '"""Actualiza el estado y retorna lista de deltas."""',
            ' ' * (method_indent + 4) + 'deltas = []',
            ' ' * (method_indent + 4) + '',
            ' ' * (method_indent + 4) + '# Procesar cada componente activo',
            ' ' * (method_indent + 4) + 'for comp_name, component in self.active_components.items():',
            ' ' * (method_indent + 8) + 'if hasattr(component, "enabled") and component.enabled:',
            ' ' * (method_indent + 12) + 'if hasattr(component, "calculate_delta"):',
            ' ' * (method_indent + 16) + 'delta = component.calculate_delta(self.state, current_time, dt)',
            ' ' * (method_indent + 16) + 'if delta and (abs(delta.position).sum() > 0.001 or abs(delta.orientation).sum() > 0.001):',
            ' ' * (method_indent + 20) + 'deltas.append(delta)',
            ' ' * (method_indent + 4) + '',
            ' ' * (method_indent + 8) + '# Actualizar componente si tiene update',
            ' ' * (method_indent + 8) + 'if hasattr(component, "update"):',
            ' ' * (method_indent + 12) + 'component.update(current_time, dt, self.state)',
            ' ' * (method_indent + 4) + '',
            ' ' * (method_indent + 4) + '# Actualizar tiempo',
            ' ' * (method_indent + 4) + 'self.state.last_update = current_time',
            ' ' * (method_indent + 4) + '',
            ' ' * (method_indent + 4) + '# IMPORTANTE: Retornar lista de deltas, no el state',
            ' ' * (method_indent + 4) + 'return deltas'
        ]
        
        # Reconstruir el archivo
        new_lines = lines[:method_start] + new_method + lines[method_end:]
        
        # Guardar
        with open('trajectory_hub/core/motion_components.py', 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Método corregido para retornar lista de deltas")
        
    elif 'return deltas' in method_content:
        print("\n✅ El método ya retorna deltas (correcto)")
    else:
        print("\n⚠️ No está claro qué retorna el método")
    
    # También buscar si hay un método update() que esté interfiriendo
    print("\n🔍 Buscando otros métodos update en SourceMotion...")
    in_source_motion = False
    for i, line in enumerate(lines):
        if 'class SourceMotion' in line:
            in_source_motion = True
        elif in_source_motion and line.strip() and not line.startswith(' '):
            in_source_motion = False
        elif in_source_motion and 'def update(' in line and 'update_with_deltas' not in line:
            print(f"⚠️ Encontrado otro método update en línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    verify_and_fix()
    
    print("\n📝 Próximo paso:")
    print("python debug_rotation_final.py")