import os
import re
from datetime import datetime
import shutil

def quick_fix_3d():
    """Fix rápido y directo para sphere 3D"""
    print("🚀 FIX RÁPIDO SPHERE 3D")
    print("="*60)
    
    # 1. Encontrar spat_osc_bridge.py
    print("\n1️⃣ Arreglando spat_osc_bridge.py...")
    
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    if os.path.exists(bridge_file):
        backup = f"{bridge_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(bridge_file, backup)
        
        with open(bridge_file, 'r') as f:
            content = f.read()
        
        # Buscar send_source_position o similar
        if 'def send_source_position' in content:
            print("✅ Encontrado send_source_position")
            
            # Ver si envía 3 coordenadas
            pattern = r'def send_source_position\(self, source_id: int, x: float, y: float\)'
            if re.search(pattern, content):
                print("❌ Solo acepta x, y - Actualizando...")
                
                # Cambiar firma para aceptar z
                content = re.sub(
                    r'def send_source_position\(self, source_id: int, x: float, y: float\)',
                    'def send_source_position(self, source_id: int, x: float, y: float, z: float = 0.0)',
                    content
                )
                
                # Cambiar el envío para incluir z
                content = re.sub(
                    r'"/source/\{source_id\}/xyz", \[x, y\]\)',
                    '"/source/{source_id}/xyz", [x, y, z])',
                    content
                )
                
                print("✅ Actualizado para enviar x, y, z")
        
        # Guardar
        with open(bridge_file, 'w') as f:
            f.write(content)
    
    # 2. Actualizar engine para pasar z
    print("\n2️⃣ Actualizando engine...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, backup)
        
        with open(engine_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar dónde se envían posiciones
        for i, line in enumerate(lines):
            # Buscar patrón: send_source_position(id, x, y)
            if 'send_source_position' in line and ', position[0], position[1])' in line:
                print(f"❌ Línea {i+1}: Solo envía x, y")
                
                # Cambiar para enviar z también
                new_line = line.replace(
                    ', position[0], position[1])',
                    ', position[0], position[1], position[2] if len(position) > 2 else 0)'
                )
                lines[i] = new_line
                print("✅ Actualizado para enviar x, y, z")
        
        # Guardar
        with open(engine_file, 'w') as f:
            f.write('\n'.join(lines))
    
    print("\n✅ FIX COMPLETADO")
    print("\n🎯 PRUEBA AHORA:")
    print("1. Ejecuta el programa normalmente")
    print("2. Crea un macro con sphere")
    print("3. Debería ser 3D en Spat")

def verify_3d_positions():
    """Verificar que las posiciones son 3D"""
    print("\n\n🧪 VERIFICACIÓN RÁPIDA:")
    
    # Test directo
    test_code = '''
from trajectory_hub.control.managers.formation_manager import FormationManager

fm = FormationManager()
positions = fm.calculate_formation("sphere", 5, scale=1.0)

print("\\nPosiciones sphere:")
for i, pos in enumerate(positions):
    print(f"  {i}: x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f}")

# Verificar variación en Y y Z
y_vals = [p[1] for p in positions]
z_vals = [p[2] for p in positions]

if len(set(y_vals)) > 1 and len(set(z_vals)) > 1:
    print("\\n✅ Confirmado: Posiciones 3D con variación en Y y Z")
else:
    print("\\n❌ Problema: Sin variación 3D")
'''
    
    try:
        exec(test_code)
    except Exception as e:
        print(f"Error en verificación: {e}")

if __name__ == "__main__":
    quick_fix_3d()
    verify_3d_positions()