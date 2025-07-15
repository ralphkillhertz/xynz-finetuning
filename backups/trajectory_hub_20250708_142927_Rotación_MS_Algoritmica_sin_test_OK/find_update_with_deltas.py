# === find_update_with_deltas.py ===
# 🔍 Buscar: Localizar exactamente update_with_deltas
# ⚡ Para aplicar el fix correcto

import os

def find_update_with_deltas():
    """Encontrar el método update_with_deltas"""
    
    file_path = os.path.join("trajectory_hub", "core", "motion_components.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Buscando update_with_deltas...")
    
    # Buscar el método
    for i, line in enumerate(lines):
        if 'def update_with_deltas' in line:
            print(f"\n✅ Encontrado en línea {i+1}: {line.strip()}")
            
            # Determinar en qué clase está
            # Buscar hacia atrás para encontrar la clase
            for j in range(i, max(0, i-50), -1):
                if 'class ' in lines[j] and ':' in lines[j]:
                    print(f"   En clase: {lines[j].strip()}")
                    break
            
            # Mostrar el método completo
            print("\n📋 Método completo:")
            print("-" * 60)
            
            # Obtener indentación
            indent = len(line) - len(line.lstrip())
            
            # Mostrar desde def hasta return o siguiente método
            for j in range(i, min(i+50, len(lines))):
                current_line = lines[j]
                
                # Si es otro método al mismo nivel, parar
                if j > i and current_line.strip().startswith('def ') and len(current_line) - len(current_line.lstrip()) <= indent:
                    break
                
                print(f"{j+1:4d}: {current_line.rstrip()}")
                
                # Resaltar líneas importantes
                if 'component_order' in current_line:
                    print("      ^^^ ORDEN DE COMPONENTES")
                elif 'macro_rotation' in current_line:
                    print("      ^^^ MENCIONA macro_rotation")
                elif 'for comp_name in' in current_line:
                    print("      ^^^ BUCLE DE PROCESAMIENTO")
    
    # Buscar también component_order
    print("\n🔍 Buscando component_order...")
    for i, line in enumerate(lines):
        if 'component_order = [' in line:
            print(f"\nEncontrado en línea {i+1}")
            # Mostrar hasta el cierre
            j = i
            while j < len(lines) and ']' not in lines[j]:
                print(f"{j+1:4d}: {lines[j].rstrip()}")
                j += 1
            if j < len(lines):
                print(f"{j+1:4d}: {lines[j].rstrip()}")

if __name__ == "__main__":
    find_update_with_deltas()