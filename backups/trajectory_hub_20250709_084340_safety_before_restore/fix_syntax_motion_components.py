# === fix_syntax_motion_components.py ===
# 🔧 Fix: Corregir error de sintaxis en motion_components.py
# ⚡ Solución rápida para SyntaxError

import os

def fix_syntax_error():
    """Arreglar error de sintaxis en línea 1401"""
    
    file_path = 'trajectory_hub/core/motion_components.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_syntax_fix', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # Buscar alrededor de la línea 1401
    for i in range(max(0, 1395), min(len(lines), 1410)):
        if i < len(lines):
            print(f"Línea {i+1}: {lines[i].rstrip()}")
    
    # Arreglar línea problemática
    if 1400 < len(lines):
        line_1401 = lines[1400]  # índice 1400 = línea 1401
        
        if 'neighbors: List[MotionState] = None) -> MotionState:' in line_1401:
            print(f"\n🔍 Encontrado problema en línea 1401")
            
            # Buscar la definición completa del método
            # Retroceder para encontrar el def
            j = 1400
            while j > 0 and not lines[j].strip().startswith('def '):
                j -= 1
            
            if lines[j].strip().startswith('def '):
                print(f"📍 Método empieza en línea {j+1}: {lines[j].strip()}")
                
                # Reconstruir la firma completa
                method_start = j
                method_lines = []
                k = j
                while k < len(lines) and not lines[k].rstrip().endswith(':'):
                    method_lines.append(lines[k].rstrip())
                    k += 1
                if k < len(lines):
                    method_lines.append(lines[k].rstrip())
                
                print("\n📋 Firma actual (rota):")
                for ml in method_lines:
                    print(f"  {ml}")
                
                # Arreglar - asegurar que sea def update(self, state, current_time, dt):
                indent = len(lines[j]) - len(lines[j].lstrip())
                new_line = ' ' * indent + 'def update(self, state, current_time, dt):\n'
                
                # Reemplazar todas las líneas del método con la nueva firma
                lines[j:k+1] = [new_line]
                
                print(f"\n✅ Firma corregida a: {new_line.strip()}")
    
    # Buscar otros posibles errores de sintaxis
    print("\n🔍 Buscando otros errores de sintaxis...")
    
    for i, line in enumerate(lines):
        # Buscar líneas que terminan con parámetros colgando
        if line.strip().endswith('= None) -> MotionState:'):
            print(f"⚠️ Línea {i+1} sospechosa: {line.strip()}")
            # Verificar si es parte de una definición rota
            if i > 0 and 'def ' not in lines[i-1]:
                # Buscar el def más cercano
                j = i - 1
                while j > 0 and not lines[j].strip().startswith('def '):
                    j -= 1
                if lines[j].strip().startswith('def update'):
                    # Corregir
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    lines[j] = ' ' * indent + 'def update(self, state, current_time, dt):\n'
                    # Eliminar líneas extras
                    del lines[j+1:i+1]
                    print(f"✅ Corregido método en línea {j+1}")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Sintaxis corregida")

def verify_fix():
    """Verificar que el import funciona"""
    
    print("\n🧪 Verificando import...")
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        print("✅ Import exitoso")
        return True
    except SyntaxError as e:
        print(f"❌ Todavía hay error de sintaxis: {e}")
        print(f"   Archivo: {e.filename}")
        print(f"   Línea: {e.lineno}")
        return False
    except Exception as e:
        print(f"❌ Otro error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 FIXING SYNTAX ERROR")
    print("=" * 60)
    
    fix_syntax_error()
    
    if verify_fix():
        print("\n📋 Ejecutar: python test_delta_100.py")
    else:
        print("\n⚠️ Todavía hay errores, revisando...")