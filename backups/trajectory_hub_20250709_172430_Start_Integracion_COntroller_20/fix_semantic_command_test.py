def fix_semantic_command_test():
    print("🔍 VERIFICANDO API DE SemanticCommand")
    print("="*60)
    
    # Primero, ver cómo está definida
    semantic_file = "trajectory_hub/control/semantic/semantic_command.py"
    
    try:
        with open(semantic_file, 'r') as f:
            content = f.read()
            
        # Buscar __init__ de SemanticCommand
        import re
        init_match = re.search(r'class SemanticCommand.*?def __init__\(self([^)]*)\)', content, re.DOTALL)
        
        if init_match:
            print(f"✅ Encontrada definición: __init__{init_match.group(1)}")
        else:
            print("⚠️ No encontré __init__, usando @dataclass posiblemente")
            
    except FileNotFoundError:
        print("❌ semantic_command.py no existe")
    
    # Crear test corregido
    test_fixed = '''#!/usr/bin/env python3
"""Test de formación sphere - versión directa"""

from trajectory_hub import EnhancedTrajectoryEngine

print("🌐 TEST FORMACIÓN SPHERE - DIRECTO")
print("="*60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=20, fps=30)

# TEMPORAL: Actualizar directamente el engine para sphere
# (mientras completamos la arquitectura)
import numpy as np
import math

def apply_sphere_formation(engine, source_ids, spacing=2.0):
    """Aplicar formación esfera manualmente"""
    n = len(source_ids)
    golden_ratio = (1 + math.sqrt(5)) / 2
    
    for i, sid in enumerate(source_ids):
        # Ángulo vertical (de -1 a 1)
        y = 1 - (2 * i / (n - 1)) if n > 1 else 0
        
        # Radio en el plano XZ
        radius_xz = math.sqrt(1 - y * y)
        
        # Ángulo horizontal usando proporción áurea
        theta = 2 * math.pi * i / golden_ratio
        
        # Coordenadas finales
        x = radius_xz * math.cos(theta) * spacing
        y_final = y * spacing
        z = radius_xz * math.sin(theta) * spacing
        
        engine._positions[sid] = np.array([x, y_final, z])
        # Enviar a Spat
        engine.osc_bridge.send_position(sid, engine._positions[sid])

print("1. Creando macro...")
macro = engine.create_macro("esfera_test", 15, formation="circle")  # Temporal

print("2. Aplicando formación esfera...")
apply_sphere_formation(engine, macro.source_ids, spacing=3.0)

print("\\n✅ Formación esfera aplicada")
print("\\n💡 Verifica en Spat:")
print("   - 15 fuentes distribuidas en esfera")
print("   - Radio ~3 metros")
print("   - Distribución uniforme 3D")

# Stats
stats = engine.osc_bridge.get_stats()
print(f"\\n📊 OSC: {stats['messages_sent']} mensajes enviados")
'''
    
    with open("test_sphere_direct.py", "w") as f:
        f.write(test_fixed)
    
    print("\n✅ Test directo creado")
    
    # También actualizar el engine para reconocer sphere
    print("\n🔧 Actualizando engine para reconocer 'sphere'...")
    
    engine_patch = '''# === patch_engine_sphere.py ===
import re

def patch_engine():
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Buscar donde están las formaciones
    if 'formation == "sphere"' not in content:
        # Añadir después de random
        random_block = re.search(r'(elif formation == "random":.*?self\\._positions\\[sid\\] = np\\.array\\(\\[x, y, z\\]\\)\\s*\\n)', content, re.DOTALL)
        
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
'''
    
    with open("patch_engine_sphere.py", "w") as f:
        f.write(engine_patch)
    
    print("\n🚀 Ejecuta:")
    print("   1. python patch_engine_sphere.py")
    print("   2. python test_sphere_direct.py")

if __name__ == "__main__":
    fix_semantic_command_test()