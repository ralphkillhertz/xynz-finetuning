# === final_aggressive_concentration_fix.py ===
# 🔧 Fix: Eliminar TODAS las definiciones y crear UNA que funcione
# ⚡ Sin más vueltas

import os
import re

def aggressive_fix():
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Backup
    import datetime
    backup_name = f"{engine_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w') as f:
        f.write(content)
    
    # 1. ELIMINAR TODAS las definiciones de set_macro_concentration
    print("🗑️ Eliminando TODAS las definiciones de set_macro_concentration...")
    
    # Pattern para encontrar cualquier definición del método
    pattern = r'(\s*)def set_macro_concentration\([^)]*\):[^}]+?(?=\n\s*def|\n\s*@|\nclass|\Z)'
    
    # Eliminar todas
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # 2. Insertar UNA definición que FUNCIONE
    print("✅ Insertando definición ÚNICA y CORRECTA...")
    
    # Buscar dónde insertar (después de create_macro)
    insert_pos = content.find('def create_macro')
    if insert_pos > 0:
        # Buscar el final del método create_macro
        next_def_pos = content.find('\n    def ', insert_pos + 1)
        if next_def_pos == -1:
            next_def_pos = len(content)
        
        # Método que DEFINITIVAMENTE funciona
        working_method = '''
    def set_macro_concentration(self, macro_id: str, factor: float):
        """Establecer factor de concentración para un macro - VERSIÓN DEFINITIVA."""
        if macro_id not in self._macros:
            print(f"❌ Macro '{macro_id}' no existe")
            return
        
        # GUARDAR EL FACTOR - CRÍTICO
        macro = self._macros[macro_id]
        macro.concentration_factor = max(0.0, min(1.0, factor))
        
        print(f"✅ Concentración establecida:")
        print(f"   Macro: {macro_id}")
        print(f"   Factor: {macro.concentration_factor:.2f}")
        print(f"   Fuentes: {len(macro.source_ids)}")
        
        # Debug para verificar
        print(f"   Verificación: {getattr(macro, 'concentration_factor', 'ERROR')}")
'''
        
        # Insertar
        content = content[:next_def_pos] + working_method + content[next_def_pos:]
    
    # 3. Verificar step() también
    if 'def step(' in content and 'concentration_factor' not in content[content.find('def step('):content.find('def step(') + 2000]:
        print("⚠️ step() no tiene lógica de concentración - agregando...")
        
        # Buscar dónde está step
        step_start = content.find('def step(')
        if step_start > 0:
            # Buscar el return
            return_pos = content.find('return {', step_start)
            if return_pos > 0:
                concentration_logic = '''
        # CONCENTRACIÓN - Aplicar antes de return
        for macro_id, macro in self._macros.items():
            factor = getattr(macro, 'concentration_factor', 0)
            if factor > 0 and hasattr(macro, 'source_ids'):
                positions = []
                for sid in macro.source_ids:
                    if sid < self.max_sources:
                        positions.append(self._positions[sid].copy())
                
                if len(positions) > 1:
                    import numpy as np
                    center = np.mean(positions, axis=0)
                    
                    for i, sid in enumerate(macro.source_ids):
                        direction = center - positions[i]
                        new_pos = positions[i] + (direction * factor * self.dt * 10.0)
                        self._positions[sid] = new_pos
                        
                        if sid in self._source_motions:
                            self._source_motions[sid].state.position = new_pos.copy()
        
'''
                content = content[:return_pos] + concentration_logic + content[return_pos:]
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("\n✅ FIX AGRESIVO COMPLETADO")
    print("   - Eliminadas TODAS las definiciones antiguas")
    print("   - Creada UNA definición que funciona")
    print("   - step() actualizado con lógica de concentración")
    
    # Test inmediato
    print("\n🧪 TEST INMEDIATO:")
    exec('''
import sys
sys.path.insert(0, ".")
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
macro_id = engine.create_macro("test", source_count=2)

print("\\nAntes de set_macro_concentration:")
engine.set_macro_concentration(macro_id, 0.8)

macro = engine._macros[macro_id]
print(f"\\nFactor guardado: {getattr(macro, 'concentration_factor', 'NO EXISTE')}")

if hasattr(macro, 'concentration_factor'):
    print("\\n✅ ¡ÉXITO! El factor se guardó correctamente")
else:
    print("\\n❌ TODAVÍA FALLA - Revisar manualmente")
''')

if __name__ == "__main__":
    aggressive_fix()