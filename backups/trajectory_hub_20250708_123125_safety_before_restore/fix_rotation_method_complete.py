# === fix_rotation_method_complete.py ===
# 🔧 Fix: Reemplazar método set_macro_rotation completo
# ⚡ Impacto: CRÍTICO - Implementa rotación correctamente

import os
import re

def fix_rotation_method():
    """Reemplaza el método set_macro_rotation completo"""
    
    print("🔧 REEMPLAZANDO MÉTODO set_macro_rotation COMPLETO\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Método completo y funcional
    new_method = '''    def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):
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
            print("❌ No hay posiciones válidas para calcular centro")
            return
            
        center = np.mean(positions, axis=0)
        
        # Importar MacroRotation si es necesario
        from .motion_components import MacroRotation
        
        # Configurar rotación para cada fuente del macro
        configured = 0
        for sid in macro.source_ids:
            if sid in self.motion_states:
                state = self.motion_states[sid]
                
                # Crear componente de rotación si no existe
                if 'macro_rotation' not in state.active_components:
                    rotation = MacroRotation()
                    state.active_components['macro_rotation'] = rotation
                else:
                    rotation = state.active_components['macro_rotation']
                
                # Configurar rotación
                rotation.update_center(center)
                rotation.set_rotation(speed_x, speed_y, speed_z)
                configured += 1
                
        print(f"✅ Rotación configurada para macro '{macro_name}'")
        print(f"   Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
        print(f"   Velocidades (rad/s): X={speed_x:.2f}, Y={speed_y:.2f}, Z={speed_z:.2f}")
        print(f"   Fuentes configuradas: {configured}/{len(macro.source_ids)}")'''
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar el método completo
    pattern = r'def set_macro_rotation\(.*?\):\s*\n(?:.*?\n)*?(?=\n    def|\n\nclass|\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_method + '\n', content, flags=re.DOTALL)
        print("✅ Método reemplazado completamente")
    else:
        print("❌ No se encontró el método, añadiendo...")
        # Buscar dónde insertar
        insert_after = "def set_macro_trajectory"
        pos = content.find(insert_after)
        if pos > 0:
            # Buscar el siguiente def
            next_def = content.find("\n    def ", pos + 1)
            if next_def > 0:
                content = content[:next_def] + "\n" + new_method + "\n" + content[next_def:]
                print("✅ Método añadido")
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verificar sintaxis
    print("\n🧪 Verificando sintaxis...")
    try:
        import py_compile
        py_compile.compile(engine_path, doraise=True)
        print("✅ Sintaxis correcta")
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")

if __name__ == "__main__":
    fix_rotation_method()
    print("\n🚀 Ejecutando test completo...")
    os.system("python test_macro_rotation_fixed.py")