# check_update_with_deltas.py
# Verifica el método update_with_deltas completo

def check_method():
    print("🔍 Examinando el método update_with_deltas completo...")
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar el método update_with_deltas
    method_start = -1
    for i, line in enumerate(lines):
        if 'def update_with_deltas(self, current_time: float, dt: float)' in line:
            method_start = i
            break
    
    if method_start == -1:
        print("❌ No se encontró update_with_deltas")
        return
    
    print(f"✅ Encontrado en línea {method_start + 1}")
    
    # Encontrar el final del método
    method_indent = len(lines[method_start]) - len(lines[method_start].lstrip())
    method_lines = [lines[method_start]]
    
    for i in range(method_start + 1, len(lines)):
        if lines[i].strip() == '':
            method_lines.append(lines[i])
            continue
        
        line_indent = len(lines[i]) - len(lines[i].lstrip())
        if line_indent <= method_indent and lines[i].strip():
            break
        
        method_lines.append(lines[i])
    
    print("\n📋 Contenido actual del método:")
    for i, line in enumerate(method_lines):
        print(f"{method_start + i + 1:4d}: {line}")
    
    # Buscar qué retorna
    method_content = '\n'.join(method_lines)
    if 'return self.state' in method_content:
        print("\n❌ ERROR: El método está retornando self.state")
        print("🔧 Necesita corregirse para retornar la lista de deltas")
    elif 'return deltas' in method_content:
        print("\n✅ CORRECTO: El método retorna deltas")
    else:
        print("\n⚠️ No está claro qué retorna el método")
    
    # Verificar también qué método llama engine.update()
    print("\n🔍 Verificando qué llama engine.update()...")
    
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        engine_content = f.read()
    
    # Buscar en engine.update()
    engine_lines = engine_content.split('\n')
    in_update = False
    
    for i, line in enumerate(engine_lines):
        if 'def update(self' in line:
            in_update = True
            print(f"\n📌 Encontrado engine.update() en línea {i + 1}")
            continue
        
        if in_update:
            if 'motion.update' in line:
                print(f"   Línea {i + 1}: {line.strip()}")
                
                # Mostrar contexto
                for j in range(max(0, i-2), min(i+3, len(engine_lines))):
                    print(f"   {j + 1:4d}: {engine_lines[j]}")
                
            if line.strip() and not line.startswith(' '):
                break

if __name__ == "__main__":
    check_method()
    
    print("\n💡 Si el método retorna self.state, necesitamos corregirlo.")