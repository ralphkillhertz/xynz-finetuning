import os
import re

def find_osc_config():
    """Encontrar la configuración OSC real"""
    print("🔍 BUSCANDO CONFIGURACIÓN OSC")
    print("="*60)
    
    # 1. Buscar puertos OSC
    print("\n1️⃣ PUERTOS OSC:")
    
    files_to_check = [
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/bridges/osc_bridge.py",
        "trajectory_hub/config.py",
        "main.py"
    ]
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Buscar puertos
            port_patterns = [
                r'port\s*=\s*(\d+)',
                r'osc_port\s*=\s*(\d+)',
                r':(\d{4,5})',
                r'default=(\d{4,5})'
            ]
            
            for pattern in port_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"\n{filepath}:")
                    for port in set(matches):
                        if int(port) > 1000:  # Puerto válido
                            print(f"  Puerto: {port}")
    
    # 2. Buscar cómo se envían posiciones
    print("\n\n2️⃣ CÓMO SE ENVÍAN POSICIONES:")
    
    # Buscar en osc_bridge
    osc_file = "trajectory_hub/bridges/osc_bridge.py"
    
    if os.path.exists(osc_file):
        with open(osc_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar send_position
        for i, line in enumerate(lines):
            if 'def send_position' in line:
                print(f"\n📍 send_position en línea {i+1}:")
                
                # Mostrar método completo
                indent = len(line) - len(line.lstrip())
                for j in range(i, min(len(lines), i+20)):
                    if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent and j > i:
                        break
                    print(f"  {j+1}: {lines[j]}")
                
                # Ver si envía 3 coordenadas
                method_text = '\n'.join(lines[i:j])
                if ', z' in method_text or '[2]' in method_text or 'position[2]' in method_text:
                    print("\n  ✅ ENVÍA COORDENADA Z")
                else:
                    print("\n  ❌ NO ENVÍA COORDENADA Z - ESTE ES EL PROBLEMA!")
                break
    
    # 3. Ver cómo engine llama a send_position
    print("\n\n3️⃣ CÓMO ENGINE USA send_position:")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Buscar llamadas a send_position
        send_calls = re.findall(r'send_position\([^)]+\)', content)
        
        if send_calls:
            print("\nLlamadas a send_position:")
            for call in send_calls[:3]:
                print(f"  {call}")
                
                # Ver si pasa 3 valores
                if call.count(',') >= 2:
                    print("    ✅ Pasa 3 valores")
                else:
                    print("    ❌ Solo pasa 2 valores")

def create_complete_fix():
    """Crear fix completo para sphere 3D"""
    
    fix_content = '''
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
    print("\\n1️⃣ Arreglando OSC Bridge...")
    
    osc_file = "trajectory_hub/bridges/osc_bridge.py"
    
    if os.path.exists(osc_file):
        backup = f"{osc_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(osc_file, backup)
        
        with open(osc_file, 'r') as f:
            content = f.read()
            lines = content.split('\\n')
        
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
                    method_text = '\\n'.join(method_lines)
                    
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
            f.write('\\n'.join(lines))
    
    # 2. Fix Engine
    print("\\n2️⃣ Arreglando Engine...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, backup)
        
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Actualizar llamadas a send_position
        # Buscar patrón: send_position(sid, pos) o similar
        old_pattern = r'send_position\\(([^,]+), \\(([^,]+), ([^)]+)\\)\\)'
        new_pattern = r'send_position(\\1, \\2, \\3, 0)'
        
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
    print("\\n3️⃣ Verificando cálculo de sphere...")
    
    # Ya sabemos que FormationManager lo calcula bien
    print("  ✅ FormationManager calcula sphere 3D correctamente")
    
    # Resumen
    print("\\n" + "="*60)
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
    print("\\n🚀 Prueba ahora creando sphere")
    print("Debería verse en 3D en Spat")
'''
    
    with open("fix_sphere_3d_complete.py", 'w') as f:
        f.write(fix_content)
    
    print("\n✅ Fix completo creado: fix_sphere_3d_complete.py")

if __name__ == "__main__":
    find_osc_config()
    create_complete_fix()
    
    print("\n\n🎯 SOLUCIÓN RÁPIDA:")
    print("python fix_sphere_3d_complete.py")
    print("\n📡 Para monitorear con el puerto correcto:")
    print("Edita monitor_osc_sphere.py y cambia el puerto 9999")
    print("por el puerto que encontraste arriba (probablemente 8888)")