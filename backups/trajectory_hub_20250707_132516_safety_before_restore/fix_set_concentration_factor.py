# === fix_set_concentration_factor.py ===
# 🔧 Fix: Asegurar que concentration_factor se guarde en el macro
# ⚡ Impacto: CRÍTICO - Sin esto no hay movimiento

import os
import re

def fix_set_concentration():
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar set_macro_concentration y reemplazarlo
    pattern = r'def set_macro_concentration\([^)]+\):[^}]+?(?=\n    def|\nclass|\Z)'
    
    replacement = '''def set_macro_concentration(self, macro_id: str, factor: float):
        """Establecer factor de concentración para un macro."""
        if macro_id not in self._macros:
            print(f"❌ Macro '{macro_id}' no existe")
            return
            
        # CRÍTICO: Guardar el factor en el macro
        macro = self._macros[macro_id]
        macro.concentration_factor = max(0.0, min(1.0, factor))
        
        print(f"✅ Concentración de '{macro_id}' establecida a {macro.concentration_factor:.2f}")
        
        # Actualizar estado
        if hasattr(self, '_update_macro_states'):
            self._update_macro_states()'''
    
    # Reemplazar
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Si no se encontró, buscar una versión más simple
    if new_content == content:
        # Buscar después de create_macro
        insert_pos = content.find('def create_macro')
        if insert_pos > 0:
            next_def = content.find('\n    def ', insert_pos + 100)
            method = '''
    def set_macro_concentration(self, macro_id: str, factor: float):
        """Establecer factor de concentración para un macro."""
        if macro_id not in self._macros:
            print(f"❌ Macro '{macro_id}' no existe")
            return
            
        # CRÍTICO: Guardar el factor en el macro
        macro = self._macros[macro_id]
        macro.concentration_factor = max(0.0, min(1.0, factor))
        
        print(f"✅ Concentración de '{macro_id}' establecida a {macro.concentration_factor:.2f}")
'''
            new_content = content[:next_def] + method + content[next_def:]
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(new_content)
    
    print("✅ set_macro_concentration arreglado")
    print("   Ahora SÍ guarda concentration_factor en el macro")

if __name__ == "__main__":
    fix_set_concentration()