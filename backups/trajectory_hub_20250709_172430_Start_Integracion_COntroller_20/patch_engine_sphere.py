# === patch_engine_sphere.py ===
import re

def patch_engine():
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar donde están las formaciones
    if 'formation == "sphere"' not in content:
        # Añadir después de random
        random_block = re.search(r'(elif formation == "random":.*?self\._positions\[sid\] = np\.array\(\[x, y, z\]\)\s*\n)', content, re.DOTALL)
        
        if random_block:
            sphere_code = """        elif formation == "sphere":
            # Usar FormationManager si está disponible
            try:
                from trajectory_hub.control.managers.formation_manager import FormationManager
                positions = FormationManager.calculate_formation("sphere", len(source_ids), spacing)
                for i, (sid, pos) in enumerate(zip(source_ids, positions)):
                    self._positions[sid] = np.array(pos)
            except ImportError:
                # Fallback: distribución simple
                for i, sid in enumerate(source_ids):
                    self._positions[sid] = np.random.randn(3) * spacing
"""
            
            new_content = content[:random_block.end()] + sphere_code + content[random_block.end():]
            
            # Backup y escribir
            import shutil
            from datetime import datetime
            backup = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(file_path, backup)
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            print("✅ Engine parchado para sphere")

if __name__ == "__main__":
    patch_engine()
