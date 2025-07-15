# === fix_send_osc_complete.py ===
# 🔧 Fix: Corregir toda la función _send_osc_update
# ⚡ Impacto: CRÍTICO - Arregla sintaxis

import os

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# Buscar el método y corregir toda su indentación
search_str = 'def _send_osc_update(self):'
pos = content.find(search_str)

if pos != -1:
    # Encontrar el final del método anterior
    prev_method_end = content.rfind('\n\n', 0, pos)
    
    # Reemplazar con versión correctamente indentada
    fixed_method = '''
    def _send_osc_update(self):
        """Enviar actualizaciones de posición vía OSC"""
        if not self.osc_bridge:
            return
            
        # Solo enviar las posiciones actuales
        positions = []
        orientations = []
        apertures = []
        names = {}
        
        active_sources = sorted(self.motion_states.keys())
        
        for sid in active_sources:
            if sid < len(self._positions):
                positions.append(self._positions[sid])
                
                if hasattr(self, '_orientations') and sid < len(self._orientations):
                    orientations.append(self._orientations[sid])
                else:
                    orientations.append([0.0, 0.0, 0.0])
                    
                if hasattr(self, '_apertures') and sid < len(self._apertures):
                    apertures.append(self._apertures[sid])
                else:
                    apertures.append(0.5)
                
                if hasattr(self, '_source_info') and sid in self._source_info:
                    if hasattr(self._source_info[sid], 'name'):
                        names[sid] = self._source_info[sid].name
        
        if positions and hasattr(self.osc_bridge, 'send_full_state'):
            import numpy as np
            self.osc_bridge.send_full_state(
                positions=np.array(positions),
                orientations=np.array(orientations),
                apertures=np.array(apertures),
                names=names
            )
'''
    
    # Encontrar el siguiente método
    next_method_pos = content.find('\n    def ', pos + 1)
    if next_method_pos == -1:
        next_method_pos = len(content)
    
    # Reemplazar
    new_content = content[:prev_method_end] + fixed_method + '\n' + content[next_method_pos:]
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print("✅ _send_osc_update corregido completamente")

# Test
print("\n🚀 Test final...")
import subprocess
result = subprocess.run(['python', 'debug_engine_update.py'], 
                      capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(f"❌ Error: {result.stderr}")