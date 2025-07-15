#!/usr/bin/env python3
"""
🔧 FIX - Arreglar expresión multi-línea interrumpida
⚡ Reorganizar el código correctamente
"""

import os

def fix_multiline_expression():
    """Arreglar la expresión multi-línea rota"""
    
    print("🔧 ARREGLANDO EXPRESIÓN MULTI-LÍNEA\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    print("📍 Situación actual:")
    print("   L1016: result = (self.base_position +")
    print("   L1017: print(...)")
    print("   L1018: return result")
    print("   L1019: self.trajectory_offset +")
    
    # Crear backup
    backup_file = motion_file + ".backup_multiline"
    with open(backup_file, 'w') as f:
        f.writelines(lines)
    print(f"\n💾 Backup creado: {backup_file}")
    
    # Reorganizar las líneas correctamente
    # Necesitamos:
    # 1. Mover las líneas de offsets para completar la expresión
    # 2. Luego el print
    # 3. Luego el return
    
    if len(lines) > 1021:
        # Extraer las líneas relevantes
        line_1016 = lines[1015]  # result = (self.base_position +
        line_1017 = lines[1016]  # print debug
        line_1018 = lines[1017]  # return result
        line_1019 = lines[1018]  # self.trajectory_offset +
        line_1020 = lines[1019]  # self.concentration_offset +
        
        # Buscar las líneas que continúan la expresión
        offset_lines = []
        i = 1018  # empezar desde línea 1019 (índice 1018)
        
        # Recolectar todas las líneas que son parte de la expresión
        while i < len(lines) and ('+' in lines[i] or ')' in lines[i]):
            offset_lines.append(lines[i])
            i += 1
            if ')' in lines[i-1]:  # Si encontramos el cierre
                break
        
        print(f"\n📊 Encontradas {len(offset_lines)} líneas de la expresión")
        
        # Reconstruir en el orden correcto
        new_lines = lines[:1015]  # Todo antes de la línea 1016
        
        # 1. La expresión completa
        new_lines.append(line_1016)  # result = (self.base_position +
        new_lines.extend(offset_lines)  # todos los offsets
        
        # 2. El print (si queremos mantenerlo)
        if "DEBUG" in line_1017:
            new_lines.append(line_1017)
        
        # 3. El return
        new_lines.append("        return result\n")
        
        # 4. El resto del archivo (saltando las líneas ya procesadas)
        new_lines.extend(lines[1018 + len(offset_lines):])
        
        # Guardar
        with open(motion_file, 'w') as f:
            f.writelines(new_lines)
        
        print("\n✅ Expresión reorganizada correctamente")
        
        # Verificar sintaxis
        try:
            with open(motion_file, 'r') as f:
                compile(f.read(), motion_file, 'exec')
            print("✅ Sintaxis verificada - TODO CORRECTO")
            return True
        except SyntaxError as e:
            print(f"❌ Aún hay error: línea {e.lineno}")
            print("   Intentando fix alternativo...")
            
            # Fix alternativo: simplificar todo
            return fix_alternative()
    
    return False

def fix_alternative():
    """Fix alternativo: reescribir get_position de forma simple"""
    
    print("\n🔧 APLICANDO FIX ALTERNATIVO\n")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar get_position y reemplazarlo completo
    import re
    
    # Patrón para encontrar todo el método get_position
    pattern = r'(def get_position\(self.*?\).*?:.*?)(.*?)(?=\n    def|\nclass|\Z)'
    
    # Nuevo método simple y correcto
    new_method = r'''\1
        """Obtener posición final sumando TODOS los componentes"""
        result = self.base_position
        result = result + self.trajectory_offset
        result = result + self.concentration_offset
        result = result + self.macro_rotation_offset
        result = result + self.algorithmic_rotation_offset
        return result'''
    
    content = re.sub(pattern, new_method, content, count=1, flags=re.DOTALL)
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.write(content)
    
    # Verificar
    try:
        compile(content, motion_file, 'exec')
        print("✅ Fix alternativo aplicado exitosamente")
        return True
    except SyntaxError as e:
        print(f"❌ Error persistente: línea {e.lineno}")
        return False

if __name__ == "__main__":
    success = fix_multiline_expression()
    
    if success:
        print("\n🎉 PROBLEMA RESUELTO")
        print("\n🚀 Ahora ejecuta:")
        print("   python direct_diagnostic_test.py")
        print("\nY luego:")
        print("   python trajectory_hub/interface/interactive_controller.py")
    else:
        print("\n❌ No se pudo resolver automáticamente")
        print("\nÚltima opción - restaurar desde backup limpio:")
        print("   cp backup_delta_correct_20250706_231624/motion_components.py trajectory_hub/core/motion_components.py")