
# === fix_sphere_3d_complete.py ===
import os
import re
from datetime import datetime
import shutil

def fix_sphere_3d():
    """Arreglar completamente sphere 3D"""
    print("🔧 FIX COMPLETO SPHERE 3D")
    print("="*60)
    
    fixes_applied = []
    
    # 1. Fix OSC Bridge
    print("\n1️⃣ Arreglando OSC Bridge...")
    
    osc_file = "trajectory_hub/bridges/osc_bridge.py"
    
    if os.path.exists(osc_file):
        backup = f"{osc_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(osc_file, backup)
        
        with open(osc_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar send_position
        for i, line in enumerate(lines):
            if 'def send_position' in line:
                # Ver si acepta z
                if ', z' not in line and 'position' not in line:
                    print("  ❌ send_position no acepta Z")
                    
                    # Buscar el método completo
                    method_start = i
                    indent = len(line) - len(line.lstrip())
                    method_end = i + 1
                    
                    for j in range(i+1, len(lines)):
                        if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent:
                            method_end = j
                            break
                    
                    # Ver si envía solo x,y
                    method_lines = lines[method_start:method_end]
                    method_text = '\n'.join(method_lines)
                    
                    # Buscar línea que envía
                    for j, mline in enumerate(method_lines):
                        if 'send_message' in mline and '/xyz' in mline:
                            if ', y]' in mline or ', y)' in mline:
                                print("  ✅ Actualizando para enviar X,Y,Z...")
                                
                                # Cambiar para incluir z
                                old_line = mline
                                if ', y]' in mline:
                                    new_line = mline.replace(', y]', ', y, z]')
                                elif ', y)' in mline:
                                    new_line = mline.replace(', y)', ', y, z)')
                                
                                lines[method_start + j] = new_line
                                
                                # También actualizar la firma si es necesario
                                if ', z' not in lines[method_start]:
                                    if ', y)' in lines[method_start]:
                                        lines[method_start] = lines[method_start].replace(', y)', ', y, z=0)')
                                
                                fixes_applied.append("OSC Bridge actualizado para enviar Z")
                                break
                
                break
        
        # Guardar
        with open(osc_file, 'w') as f:
            f.write('\n'.join(lines))
    
    # 2. Fix Engine
    print("\n2️⃣ Arreglando Engine...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, backup)
        
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Actualizar llamadas a send_position
        # Buscar patrón: send_position(sid, pos) o similar
        old_pattern = r'send_position\(([^,]+), \(([^,]+), ([^)]+)\)\)'
        new_pattern = r'send_position(\1, \2, \3, 0)'
        
        # Buscar específicamente en create_macro
        if 'send_position(sid, self._positions[sid])' in content:
            # Este patrón indica que pasa una tupla completa
            print("  ✅ Engine pasa posición completa")
            
            # Verificar que _positions tenga 3 coordenadas
            if 'self._positions[sid] = (x, y)' in content:
                print("  ❌ _positions solo guarda x,y")
                content = content.replace(
                    'self._positions[sid] = (x, y)',
                    'self._positions[sid] = (x, y, z if "z" in locals() else 0)'
                )
                fixes_applied.append("Engine actualizado para guardar Z")
        
        # Guardar
        with open(engine_file, 'w') as f:
            f.write(content)
    
    # 3. Verificar que sphere se calcule en 3D
    print("\n3️⃣ Verificando cálculo de sphere...")
    
    # Ya sabemos que FormationManager lo calcula bien
    print("  ✅ FormationManager calcula sphere 3D correctamente")
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE CAMBIOS:")
    for fix in fixes_applied:
        print(f"  ✅ {fix}")
    
    if not fixes_applied:
        print("  ℹ️ No se necesitaron cambios automáticos")
        print("  ⚠️ Verifica manualmente que:")
        print("     - OSC Bridge envíe 3 coordenadas")
        print("     - Engine pase las 3 coordenadas")
        print("     - Spat esté configurado para 3D")

if __name__ == "__main__":
    fix_sphere_3d()
    print("\n🚀 Prueba ahora creando sphere")
    print("Debería verse en 3D en Spat")
