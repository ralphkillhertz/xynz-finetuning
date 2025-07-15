# === fix_delta_system_complete.py ===
# 🔧 Fix: Solución completa para el sistema de deltas
# ⚡ Impacto: CRÍTICO - Completa sistema de deltas

import os

def fix_delta_system():
    """Arregla completamente el sistema de deltas"""
    
    # Primero verificar que MotionDelta tenga source_id
    print("1️⃣ Verificando MotionDelta...")
    
    file_path = "trajectory_hub/core/motion_components.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar MotionDelta y verificar/añadir source_id
    if "class MotionDelta:" in content and "self.source_id" not in content:
        # Añadir source_id al __init__ de MotionDelta
        content = content.replace(
            "class MotionDelta:\n    def __init__(self):",
            "class MotionDelta:\n    def __init__(self):\n        self.source_id = None"
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ source_id añadido a MotionDelta")
    
    # Ahora arreglar el problema en engine
    print("\n2️⃣ Arreglando procesamiento de deltas en engine...")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Crear una versión corregida del método update
    update_method = '''    def update(self):
        """Actualiza el sistema con procesamiento de deltas"""
        current_time = time.time()
        dt = 1.0 / self.fps
        
        # Actualizar todos los motion states y recoger deltas
        all_deltas = []
        for source_id, motion in self.motion_states.items():
            if motion and hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(current_time, dt)
                if deltas:
                    # Si es un solo delta, convertir a lista
                    if hasattr(deltas, 'position'):
                        deltas = [deltas]
                    # Asignar source_id a cada delta
                    for delta in deltas:
                        delta.source_id = source_id
                        all_deltas.append(delta)
        
        # Aplicar todos los deltas a las posiciones
        for delta in all_deltas:
            if delta.source_id < len(self._positions):
                self._positions[delta.source_id] += delta.position
                
                # Actualizar estado con nueva posición
                if delta.source_id in self.motion_states:
                    state = self.motion_states[delta.source_id] 
                    if hasattr(state, 'position'):
                        state.position = self._positions[delta.source_id].copy()
        
        # Actualizar contadores
        self._frame_count += 1
        self._time += dt
        
        # Enviar actualizaciones OSC
        self._send_osc_update()
'''
    
    # Leer el archivo del engine
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    # Reemplazar el método update
    import re
    pattern = r'def update\(self\):.*?(?=\n    def|\n\nclass|\Z)'
    engine_content = re.sub(pattern, update_method.strip(), engine_content, flags=re.DOTALL)
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(engine_content)
    
    print("✅ Método update corregido con procesamiento de deltas")
    
    # Importar time si no está
    if "import time" not in engine_content:
        with open(engine_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Añadir import time después de otros imports
        for i, line in enumerate(lines):
            if line.startswith("import") or line.startswith("from"):
                continue
            else:
                lines.insert(i, "import time\n")
                break
        
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    print("✅ Sistema de deltas completamente arreglado")

if __name__ == "__main__":
    fix_delta_system()
    print("\n🚀 Ejecutando test final...")
    os.system("python test_macro_final_working.py")