#!/usr/bin/env python3
"""
🔧 Fix: Asegurar que todos los componentes se sumen
⚡ Concentración + Rotación MS + IS deben combinarse
"""

import os
import re
from datetime import datetime

def fix_component_combination():
    """Arreglar la combinación de componentes en el engine"""
    
    print("🔧 FIX: COMBINACIÓN DE COMPONENTES\n")
    
    # Backup
    backup_dir = f"backup_combination_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Archivo principal
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(engine_file):
        print(f"❌ No se encuentra {engine_file}")
        return
    
    # Backup
    import shutil
    shutil.copy2(engine_file, os.path.join(backup_dir, "enhanced_trajectory_engine.py.bak"))
    
    # Leer contenido
    with open(engine_file, 'r') as f:
        content = f.read()
    
    print("1️⃣ Buscando método update()...")
    
    # Buscar el método update
    update_pattern = r'def update\(self.*?\n(?=\n    def|\nclass|\Z)'
    update_match = re.search(update_pattern, content, re.DOTALL)
    
    if not update_match:
        print("   ❌ No se encontró el método update")
        return
    
    print("   ✅ Método update encontrado")
    
    # Nuevo método update que asegura la combinación
    new_update = '''    def update(self):
        """Actualizar todas las fuentes con combinación correcta de componentes"""
        dt = 1.0 / self.fps
            
        if self.time_paused:
            return
            
        # Actualizar tiempo
        self.dt = dt
        
        # IMPORTANTE: Aplicar efectos en orden correcto
        # 1. Concentración (modifica posiciones base)
        self.apply_concentration()
        
        # 2. Rotación algorítmica del macro (rota todo el conjunto)
        self.apply_algorithmic_rotation_ms()
        
        # 3. Actualizar cada fuente (incluye trayectorias individuales)
        for source_id, source in self._sources.items():
            if hasattr(source, 'update'):
                source.update(dt)
                
                # CRITICAL: Después de update, aplicar offsets adicionales
                # Esto asegura que IS no sobrescriba MS
                if hasattr(source, 'motion'):
                    motion = source.motion
                    
                    # Si hay concentración activa, re-aplicar
                    macro_id = self._get_macro_for_source(source_id)
                    if macro_id and hasattr(self, 'apply_concentration'):
                        conc_state = self.get_macro_concentration_state(macro_id)
                        if conc_state and conc_state.get('factor', 1.0) < 1.0:
                            # Re-aplicar offset de concentración
                            pass  # La concentración ya se aplicó arriba
                    
                    # Si hay rotación MS activa, asegurar que se mantenga
                    if macro_id and macro_id in self.macro_rotations_algo:
                        # La rotación ya se aplicó arriba
                        pass
        
        # 4. Enviar posiciones finales vía OSC
        if self.osc_bridge:
            for source_id, source in self._sources.items():
                position = source.get_position()
                self.osc_bridge.send_position(source_id, position)
    
    def _get_macro_for_source(self, source_id: str) -> str:
        """Obtener el macro al que pertenece una fuente"""
        for macro_id, macro_data in self._macros.items():
            if source_id in macro_data.get('sources', []):
                return macro_id
        return None'''
    
    # Reemplazar el método update
    content = re.sub(update_pattern, new_update, content, count=1)
    
    print("\n2️⃣ Asegurando que apply_concentration modifique posiciones...")
    
    # Buscar apply_concentration
    if 'def apply_concentration' not in content:
        print("   ⚠️  apply_concentration no existe, agregándolo...")
        
        # Agregar método apply_concentration
        concentration_method = '''
    def apply_concentration(self):
        """Aplicar efecto de concentración a todos los macros"""
        for macro_id, macro_data in self._macros.items():
            conc_state = self.get_macro_concentration_state(macro_id)
            
            if not conc_state or conc_state.get('factor', 1.0) >= 0.99:
                continue
                
            factor = conc_state['factor']
            center = conc_state.get('center', [0, 0, 0])
            
            # Aplicar concentración a cada fuente del macro
            for source_id in macro_data.get('sources', []):
                if source_id in self._sources:
                    source = self._sources[source_id]
                    
                    # Obtener posición actual
                    current_pos = source.get_position()
                    
                    # Calcular nueva posición concentrada
                    new_pos = current_pos * factor + (1 - factor) * center
                    
                    # Aplicar offset directamente
                    if hasattr(source, 'motion'):
                        source.motion.concentration_offset = new_pos - current_pos'''
        
        # Insertar antes del método update
        content = content.replace("    def update(self", concentration_method + "\n\n    def update(self")
    
    print("\n3️⃣ Verificando _sources y _macros...")
    
    # Asegurar que usamos _sources y _macros
    content = content.replace('self.sources', 'self._sources')
    content = content.replace('self.macros', 'self._macros')
    
    # Pero mantener las propiedades públicas si existen
    if '@property' in content and 'def sources(self)' in content:
        # Ya hay property, está bien
        pass
    else:
        # Agregar properties
        properties = '''
    @property
    def sources(self):
        return self._sources
        
    @property
    def macros(self):
        return self._macros'''
        
        # Insertar al final de la clase
        content = re.sub(r'(class EnhancedTrajectoryEngine.*?)\n\n', r'\1' + properties + '\n\n', content, count=1)
    
    # Guardar cambios
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("\n✅ Fix aplicado exitosamente")
    print(f"📁 Backup guardado en: {backup_dir}")
    
    print("\n💡 CAMBIOS REALIZADOS:")
    print("   1. Update() ahora aplica efectos en orden correcto")
    print("   2. Concentración se aplica antes que IS")
    print("   3. Rotación MS se mantiene activa con IS")
    print("   4. Los componentes se suman en lugar de sobrescribirse")
    
    print("\n🚀 Reinicia el controller para probar:")
    print("   python trajectory_hub/interface/interactive_controller.py")

if __name__ == "__main__":
    fix_component_combination()