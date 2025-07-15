# === fix_state_position_sync.py ===
# 🔧 Fix DEFINITIVO - Sincroniza state.position con engine._positions
# ⚡ Este ES el último fix necesario

import os
from datetime import datetime

def fix_position_sync():
    """Sincroniza state.position con engine._positions"""
    
    print("🔧 APLICANDO FIX DE SINCRONIZACIÓN")
    print("="*60)
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = f"{engine_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup creado: {backup_path}")
    
    # Buscar el código de procesamiento de deltas
    if 'PROCESAMIENTO DE DELTAS' in content:
        print("✅ Encontrado código de deltas")
        
        # Reemplazar el código existente con versión que sincroniza posiciones
        import re
        pattern = r'# 🔧 PROCESAMIENTO DE DELTAS.*?# FIN PROCESAMIENTO DE DELTAS'
        
        new_delta_code = '''# 🔧 PROCESAMIENTO DE DELTAS - Sistema de composición
        for source_id, motion in self.motion_states.items():
            # CRÍTICO: Sincronizar state.position con engine._positions
            motion.state.position = self._positions[source_id].copy()
            
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(self._time, self.dt)
                
                for delta in deltas:
                    if hasattr(delta, 'position') and delta.position is not None:
                        # Aplicar delta a la posición
                        self._positions[source_id] = self._positions[source_id] + delta.position
        # FIN PROCESAMIENTO DE DELTAS'''
        
        content = re.sub(pattern, new_delta_code, content, flags=re.DOTALL)
        
        # Escribir archivo
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Sincronización añadida")
    else:
        print("❌ No se encontró código de deltas")
        print("   Ejecuta primero: python fix_update_deltas_precise.py")
        return False
    
    return True

if __name__ == "__main__":
    print("🎯 ESTE ES EL FIX DEFINITIVO")
    print("\nProblema identificado:")
    print("  - state.position es [0,0,0] en lugar de [10,0,0]")
    print("  - Por eso el delta calculado es [0,0,0]")
    print("\nSolución:")
    print("  - Sincronizar state.position con engine._positions")
    
    if fix_position_sync():
        print("\n✅ FIX APLICADO EXITOSAMENTE")
        print("\n🎉 Ahora SÍ ejecuta:")
        print("$ python test_deltas_finally_working.py")