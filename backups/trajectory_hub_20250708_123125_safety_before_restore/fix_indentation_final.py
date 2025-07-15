# === fix_indentation_final.py ===
# 🔧 Fix: Corrección definitiva de indentación
# ⚡ Impacto: CRÍTICO - Resuelve todos los errores

import os

def fix_indentation_final():
    """Corrección definitiva de la indentación"""
    
    print("🔧 FIX DEFINITIVO DE INDENTACIÓN\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer líneas
    with open(engine_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Corrigiendo líneas problemáticas...")
    
    # Correcciones específicas línea por línea
    corrections = {
        638: '        if macro_name not in self._macros:\n',
        639: '            print(f"❌ Macro \'{macro_name}\' no existe")\n',
        640: '            return\n',
        647: '            if sid < len(self._positions):\n',
        648: '                positions.append(self._positions[sid])\n',
        651: '            print("❌ No hay posiciones válidas")\n',
        652: '            return\n',
        661: '            if sid in self.motion_states:\n',
        664: '                if not hasattr(state, \'active_components\'):\n',
        667: '                if \'macro_rotation\' not in state.active_components:\n',
    }
    
    # Aplicar correcciones
    for line_num, correct_line in corrections.items():
        if line_num - 1 < len(lines):
            lines[line_num - 1] = correct_line
            print(f"✅ Línea {line_num} corregida")
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo guardado")
    
    # Verificar resultado
    print("\n📋 Verificación de líneas clave:")
    key_lines = [636, 637, 638, 639, 640, 646, 647, 648]
    for line_num in key_lines:
        if line_num - 1 < len(lines):
            line = lines[line_num - 1].rstrip()
            spaces = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
            print(f"L{line_num} ({spaces:2d} espacios): {line[:60]}")

if __name__ == "__main__":
    fix_indentation_final()
    print("\n🚀 Ejecutando test...")
    os.system("python test_rotation_ms_final.py")