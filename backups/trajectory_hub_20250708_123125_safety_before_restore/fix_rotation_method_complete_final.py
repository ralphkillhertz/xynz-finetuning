# === fix_rotation_method_complete_final.py ===
# 🔧 Fix: Reescribir método set_macro_rotation completamente
# ⚡ Impacto: CRÍTICO - Solución definitiva

import os
import re

def fix_rotation_method_complete():
    """Reescribe completamente el método set_macro_rotation"""
    
    print("🔧 REESCRIBIENDO set_macro_rotation COMPLETAMENTE\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Método completo y correcto
    correct_method = '''    def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):
        """Configura rotación algorítmica para un macro alrededor de su centro"""
        if macro_name not in self._macros:
            print(f"❌ Macro '{macro_name}' no existe")
            return
            
        macro = self._macros[macro_name]
        
        # Calcular centro del macro
        positions = []
        for sid in macro.source_ids:
            if sid < len(self._positions):
                positions.append(self._positions[sid])
        
        if not positions:
            print("❌ No hay posiciones válidas")
            return
            
        center = np.mean(positions, axis=0)
        
        # Importar MacroRotation
        from .motion_components import MacroRotation
        
        # Configurar rotación para cada fuente
        configured = 0
        for sid in macro.source_ids:
            if sid in self.motion_states:
                state = self.motion_states[sid]
                
                # Crear componente de rotación si no existe
                if not hasattr(state, 'active_components'):
                    state.active_components = {}
                    
                if 'macro_rotation' not in state.active_components:
                    rotation = MacroRotation()
                    state.active_components['macro_rotation'] = rotation
                else:
                    rotation = state.active_components['macro_rotation']
                
                # Configurar rotación
                rotation.update_center(center)
                rotation.set_rotation(speed_x, speed_y, speed_z)
                configured += 1
                
        print(f"✅ Rotación configurada para '{macro_name}'")
        print(f"   Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
        print(f"   Velocidades: X={speed_x}, Y={speed_y}, Z={speed_z} rad/s")
        print(f"   Fuentes: {configured}/{len(macro.source_ids)}")
'''
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar el método completo
    print("🔍 Buscando método existente...")
    
    # Patrón para encontrar el método mal formateado
    pattern = r'def set_macro_rotation\(.*?\):\s*\n.*?(?=\n    def |\n\nclass |\Z)'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print("✅ Método encontrado, reemplazando...")
        content = re.sub(pattern, correct_method.strip(), content, flags=re.DOTALL)
    else:
        print("❌ Método no encontrado, añadiendo al final de la clase...")
        # Buscar el último método de la clase
        last_method = content.rfind('\n    def ')
        if last_method > 0:
            # Buscar el final de ese método
            next_class = content.find('\nclass ', last_method)
            if next_class > 0:
                insert_pos = next_class
            else:
                insert_pos = len(content) - 1
            
            content = content[:insert_pos] + '\n\n' + correct_method + content[insert_pos:]
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo guardado")
    
    # Verificar sintaxis
    print("\n🧪 Verificando sintaxis...")
    import py_compile
    try:
        py_compile.compile(engine_path, doraise=True)
        print("✅ ¡Sintaxis correcta!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_rotation_method_complete()
    print("\n🚀 Ejecutando test final...")
    os.system("python test_rotation_ms_final.py")