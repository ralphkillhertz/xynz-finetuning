
# === fix_sphere_respecting_current_architecture.py ===
"""
Fix para sphere que respeta la arquitectura ACTUAL (no la ideal)
Sabiendo que Engine calcula formaciones internamente
"""
import os
import re
from datetime import datetime
import shutil

print("🔧 FIX SPHERE PARA ARQUITECTURA ACTUAL")
print("="*60)

# Dado que Engine calcula formaciones, necesitamos:
# 1. Añadir caso sphere a Engine
# 2. Hacer que delegue a FormationManager

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

if os.path.exists(engine_file):
    backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_file, backup)
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Verificar si ya importa FormationManager
    if 'from trajectory_hub.control.managers.formation_manager import FormationManager' not in content:
        # Añadir import después de otros imports
        import_line = "from trajectory_hub.control.managers.formation_manager import FormationManager\n"
        
        # Buscar dónde insertar
        last_import = list(re.finditer(r'^from trajectory_hub.*import.*$', content, re.MULTILINE))
        if last_import:
            insert_pos = last_import[-1].end() + 1
            content = content[:insert_pos] + import_line + content[insert_pos:]
        else:
            # Insertar después de imports estándar
            insert_pos = content.find('\n\n') + 2
            content = content[:insert_pos] + import_line + content[insert_pos:]
    
    # Buscar dónde están los casos de formation
    # Patrón: elif formation == "algo":
    formation_cases = list(re.finditer(r'elif formation == "[^"]+":', content))
    
    if formation_cases:
        # Insertar después del último caso
        last_case = formation_cases[-1]
        
        # Buscar el final de ese caso
        lines_after = content[last_case.end():].split('\n')
        indent = len(last_case.group(0)) - len(last_case.group(0).lstrip())
        
        # Encontrar dónde termina el bloque
        end_offset = 0
        for i, line in enumerate(lines_after[1:], 1):
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                end_offset = sum(len(l) + 1 for l in lines_after[:i])
                break
        
        if end_offset == 0:
            end_offset = len(content[last_case.end():])
        
        insert_pos = last_case.end() + end_offset
        
        # Código para sphere
        sphere_code = f"""
        elif formation == "sphere":
            # Usar FormationManager para sphere 3D real
            if not hasattr(self, '_fm'):
                self._fm = FormationManager()
            positions = self._fm.calculate_formation("sphere", self.config['n_sources'])
            print(f"🌐 Sphere 3D: {{len(positions)}} posiciones calculadas")
"""
        
        content = content[:insert_pos] + sphere_code + content[insert_pos:]
        
        print("✅ Caso sphere añadido a Engine")
    else:
        print("❌ No se encontraron casos de formation en Engine")
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("\n✅ Engine actualizado")

# Verificar OSC
print("\n🔍 Verificando OSC...")

bridge_file = "trajectory_hub/core/spat_osc_bridge.py"

if os.path.exists(bridge_file):
    with open(bridge_file, 'r') as f:
        bridge_content = f.read()
    
    if 'def send_source_position(self, source_id: int, x: float, y: float)' in bridge_content:
        print("⚠️ OSC solo acepta x,y - Actualizando...")
        
        backup = f"{bridge_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(bridge_file, backup)
        
        # Actualizar para aceptar z
        bridge_content = bridge_content.replace(
            'def send_source_position(self, source_id: int, x: float, y: float)',
            'def send_source_position(self, source_id: int, x: float, y: float, z: float = 0.0)'
        )
        
        # Actualizar envío
        bridge_content = bridge_content.replace(
            '"/source/{source_id}/xyz", [x, y])',
            '"/source/{source_id}/xyz", [x, y, z])'
        )
        
        with open(bridge_file, 'w') as f:
            f.write(bridge_content)
        
        print("✅ OSC actualizado para enviar x,y,z")

print("\n🎯 SPHERE 3D DEBERÍA FUNCIONAR AHORA")
print("\n⚠️ NOTA: Este es un fix para la arquitectura ACTUAL")
print("La arquitectura correcta requiere refactorización completa")
