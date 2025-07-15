# === fix_syntax_line_1401.py ===
# 🔧 Fix: Eliminar línea problemática 1401
# ⚡ Solución directa para error de sintaxis persistente

import os

def fix_line_1401():
    """Eliminar o corregir línea 1401 problemática"""
    
    file_path = 'trajectory_hub/core/motion_components.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_line_1401', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"📋 Total de líneas en el archivo: {len(lines)}")
    
    # Mostrar contexto alrededor de línea 1401
    print("\n🔍 Contexto alrededor de línea 1401:")
    for i in range(max(0, 1395), min(len(lines), 1410)):
        if i < len(lines):
            marker = ">>>" if i == 1400 else "   "
            print(f"{marker} Línea {i+1}: {lines[i].rstrip()}")
    
    # Eliminar línea 1401 si contiene el error
    if 1400 < len(lines):
        if 'neighbors: List[MotionState] = None) -> MotionState:' in lines[1400]:
            print(f"\n❌ Línea 1401 contiene error de sintaxis")
            print(f"   Contenido: {lines[1400].strip()}")
            print("✅ Eliminando línea problemática...")
            del lines[1400]
            
            # Guardar
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("✅ Línea eliminada")
            return True
    
    # Si no se encontró, buscar en todo el archivo
    print("\n🔍 Buscando la línea problemática en todo el archivo...")
    
    for i, line in enumerate(lines):
        if 'neighbors: List[MotionState] = None) -> MotionState:' in line:
            print(f"❌ Encontrada en línea {i+1}")
            print("✅ Eliminando...")
            del lines[i]
            
            # Guardar
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("✅ Línea eliminada")
            return True
    
    print("⚠️ No se encontró la línea problemática")
    return False

def check_behavior_component():
    """Verificar y arreglar BehaviorComponent si es necesario"""
    
    file_path = 'trajectory_hub/core/motion_components.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n🔍 Buscando BehaviorComponent...")
    
    in_behavior = False
    behavior_start = -1
    
    for i, line in enumerate(lines):
        if 'class BehaviorComponent' in line:
            in_behavior = True
            behavior_start = i
            print(f"✅ Encontrado BehaviorComponent en línea {i+1}")
        
        if in_behavior and 'def update' in line:
            print(f"📍 Método update en línea {i+1}")
            
            # Verificar si el método está bien formado
            j = i
            method_lines = []
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith(' ') or 'def update' in lines[j]):
                method_lines.append(lines[j])
                if lines[j].rstrip().endswith(':'):
                    break
                j += 1
            
            print("\n📋 Método update actual:")
            for ml in method_lines[:5]:  # Mostrar solo primeras 5 líneas
                print(f"   {ml.rstrip()}")
            
            # Si el método parece tener parámetros extra, corregirlo
            if any('neighbors' in line for line in method_lines):
                print("\n⚠️ El método update parece tener parámetros de neighbors")
                print("ℹ️ BehaviorComponent probablemente necesita manejar neighbors de forma diferente")
            
            in_behavior = False

def run_test():
    """Ejecutar test después de fix"""
    
    print("\n🧪 Verificando import...")
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        print("✅ Import exitoso!")
        
        # Ejecutar test completo
        print("\n🚀 Ejecutando test completo...")
        import subprocess
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True)
        
        # Mostrar resultado
        if "100%" in result.stdout:
            print("\n🎉 ¡ÉXITO! Sistema de deltas 100% funcional")
        else:
            # Mostrar solo resumen
            lines = result.stdout.split('\n')
            show = False
            for line in lines:
                if 'RESUMEN FINAL' in line or show:
                    show = True
                    print(line)
        
        if result.stderr:
            print("\nERRORES:")
            print(result.stderr[-1000:])  # Últimos 1000 chars
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 FIXING LINE 1401 SYNTAX ERROR")
    print("=" * 60)
    
    if fix_line_1401():
        check_behavior_component()
        run_test()
    else:
        print("\n⚠️ Intentando verificación de todas formas...")
        run_test()