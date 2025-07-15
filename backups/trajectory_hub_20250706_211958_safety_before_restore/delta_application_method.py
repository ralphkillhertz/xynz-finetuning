#!/usr/bin/env python3
"""
🔧 Método auxiliar para aplicar deltas
Agregar a EnhancedTrajectoryEngine si es necesario
"""

def _apply_accumulated_deltas(self):
    """Aplica todos los deltas acumulados a las posiciones"""
    try:
        from trajectory_hub.core.compatibility_v2 import compat_v2 as compat
        
        applied_count = 0
        for i in range(self.num_sources):
            # Obtener source_id
            if hasattr(self._source_motions[i], 'source_id'):
                source_id = self._source_motions[i].source_id
            else:
                source_id = i
            
            # Obtener delta acumulado
            delta = compat.get_accumulated_delta(source_id)
            
            if delta is not None:
                # Aplicar delta
                old_pos = self._positions[i].copy()
                self._positions[i] += delta
                
                # Log para debug
                if compat.config.get('LOG_DELTAS', False):
                    movement = np.linalg.norm(delta)
                    print(f"   [APPLIED] Source {source_id}: moved {movement:.4f}")
                
                # Limpiar delta aplicado
                compat.clear_deltas(source_id)
                applied_count += 1
        
        if applied_count > 0 and compat.config.get('LOG_DELTAS', False):
            print(f"   ✅ Applied deltas to {applied_count} sources")
            
    except Exception as e:
        print(f"   ❌ Error applying deltas: {e}")

# Agregar este método a tu clase EnhancedTrajectoryEngine
