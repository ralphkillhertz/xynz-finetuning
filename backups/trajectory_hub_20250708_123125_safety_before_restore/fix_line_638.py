# === fix_line_638.py ===
# 🔧 Fix: Corregir específicamente la línea 638
# ⚡ Impacto: CRÍTICO - Resuelve IndentationError

import os

def fix_line_638():
    """Corrige el error de indentación en línea 638"""
    
    print("🔧 FIX ESPECÍFICO LÍNEA 638\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer líneas
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Total líneas: {len(lines)}")
    
    # Mostrar contexto alrededor de línea 638
    print("\n🔍 Contexto línea 638 (con espacios visibles):")
    for i in range(max(0, 635), min(len(lines), 645)):
        line = lines[i].rstrip()
        spaces = len(lines[i]) - len(lines[i].lstrip())
        # Mostrar espacios como puntos
        visual_line = '·' * spaces + lines[i].lstrip().rstrip()
        print(f"L{i+1} ({spaces:2d}): {visual_line[:70]}")
    
    # Identificar el problema
    print("\n🔍 Analizando problema...")
    
    # La línea 637 (índice 636) tiene la docstring mal indentada
    if len(lines) > 637:
        line_637 = lines[636]
        line_638 = lines[637]
        
        # Verificar el problema
        if '"""' in line_637 and 'if macro_name' in line_638:
            print("❌ Problema identificado: docstring y código mal alineados")
            
            # Corregir: todo el método debe tener indentación consistente
            print("\n🔨 Aplicando corrección...")
            
            # Buscar el inicio del método
            start_idx = None
            for i in range(636, max(0, 630), -1):
                if 'def set_macro_rotation' in lines[i]:
                    start_idx = i
                    break
            
            if start_idx:
                print(f"📍 Método comienza en línea {start_idx + 1}")
                
                # Corregir todas las líneas del método
                # El def debe tener 4 espacios, el contenido 8 espacios
                i = start_idx
                while i < len(lines):
                    line = lines[i]
                    
                    if i == start_idx:
                        # La línea del def
                        lines[i] = '    def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):\n'
                    elif i == start_idx + 1:
                        # La docstring
                        lines[i] = '        """Configura rotación algorítmica para un macro alrededor de su centro"""\n'
                    elif line.strip() and not line.strip().startswith('def ') and i > start_idx:
                        # Contenido del método
                        stripped = line.strip()
                        lines[i] = '        ' + stripped + '\n'
                    elif line.strip().startswith('def ') and i > start_idx:
                        # Otro método, terminamos
                        break
                    
                    i += 1
                    
                    # Límite de seguridad
                    if i > start_idx + 100:
                        break
                
                print("✅ Indentación corregida")
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo guardado")
    
    # Verificar de nuevo
    print("\n🔍 Verificación final:")
    for i in range(max(0, 635), min(len(lines), 645)):
        if i < len(lines):
            line = lines[i].rstrip()
            spaces = len(lines[i]) - len(lines[i].lstrip())
            print(f"L{i+1} ({spaces:2d}): {line[:60]}")

if __name__ == "__main__":
    fix_line_638()
    print("\n🚀 Ejecutando test...")
    os.system("python test_rotation_ms_final.py")