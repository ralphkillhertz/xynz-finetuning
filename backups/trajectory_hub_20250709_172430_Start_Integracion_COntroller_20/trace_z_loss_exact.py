import os
import re

def trace_z_loss_exact():
    """Rastrear exactamente dónde se pierde la coordenada Z"""
    print("🔍 RASTREO EXACTO DE PÉRDIDA DE Z")
    print("="*60)
    
    # 1. FormationManager - ¿Calcula Z?
    print("\n1️⃣ FORMATION MANAGER")
    fm_file = "trajectory_hub/control/managers/formation_manager.py"
    
    if os.path.exists(fm_file):
        with open(fm_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar código sphere
        for i, line in enumerate(lines):
            if 'formation == "sphere"' in line:
                print(f"✅ Sphere encontrado en línea {i+1}")
                
                # Ver si calcula z
                for j in range(i, min(len(lines), i+20)):
                    if 'append' in lines[j] and '(' in lines[j]:
                        print(f"L{j+1}: {lines[j].strip()}")
                        
                        # Contar elementos en la tupla
                        if lines[j].count(',') >= 2:
                            print("  ✅ Añade 3 coordenadas")
                        else:
                            print("  ❌ Solo añade 2 coordenadas")
                break
    
    # 2. CommandProcessor - ¿Recibe las posiciones?
    print("\n\n2️⃣ COMMAND PROCESSOR")
    cp_file = "trajectory_hub/control/processors/command_processor.py"
    
    if os.path.exists(cp_file):
        with open(cp_file, 'r') as f:
            content = f.read()
        
        # Buscar cómo maneja formations
        if 'formation_manager' in content:
            print("✅ Usa FormationManager")
            
            # Ver cómo pasa las posiciones
            if 'calculate_formation' in content:
                pattern = r'calculate_formation.*\n.*positions'
                match = re.search(pattern, content)
                if match:
                    print(f"  Código: {match.group(0)}")
    
    # 3. Engine - ¿Qué hace con las posiciones?
    print("\n\n3️⃣ ENGINE - CRÍTICO")
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar create_macro
        for i, line in enumerate(lines):
            if 'def create_macro' in line:
                print(f"\n✅ create_macro en línea {i+1}")
                
                # Buscar cómo procesa sphere
                for j in range(i, min(len(lines), i+200)):
                    if 'sphere' in lines[j]:
                        print(f"\nL{j+1}: {lines[j].strip()}")
                        
                        # Si es el caso sphere, ver qué hace
                        if 'elif formation == "sphere"' in lines[j]:
                            print("\n⚠️ ENGINE TIENE SU PROPIO CÁLCULO DE SPHERE!")
                            
                            # Ver las siguientes líneas
                            for k in range(j+1, min(len(lines), j+15)):
                                if 'positions' in lines[k] or 'calculate' in lines[k]:
                                    print(f"L{k+1}: {lines[k]}")
                                    
                                    if '_calculate_circle' in lines[k]:
                                        print("\n❌ PROBLEMA ENCONTRADO!")
                                        print("Engine está usando _calculate_circle para sphere!")
                                        print("Por eso sale como círculo 2D")
                                        return engine_file, k
                break
    
    # 4. OSC Bridge - ¿Envía Z?
    print("\n\n4️⃣ OSC BRIDGE")
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    if os.path.exists(bridge_file):
        with open(bridge_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Buscar send_source_position
        for i, line in enumerate(lines):
            if 'def send_source_position' in line:
                print(f"\n✅ send_source_position en línea {i+1}")
                print(f"  Firma: {line.strip()}")
                
                # Ver si acepta z
                if ', z' in line:
                    print("  ✅ Acepta parámetro z")
                else:
                    print("  ❌ NO acepta parámetro z")
                
                # Ver qué envía
                for j in range(i+1, min(len(lines), i+10)):
                    if 'xyz' in lines[j] and '[' in lines[j]:
                        print(f"  L{j+1}: {lines[j].strip()}")
                        
                        if ', z]' in lines[j]:
                            print("    ✅ Envía [x, y, z]")
                        elif ', y]' in lines[j]:
                            print("    ❌ Solo envía [x, y]")
                break

def create_definitive_fix():
    """Crear fix definitivo"""
    print("\n\n🔧 CREANDO FIX DEFINITIVO")
    
    fix_content = '''
# === fix_sphere_3d_definitive.py ===
import os
import re
from datetime import datetime
import shutil

def fix_sphere_definitively():
    """Fix definitivo para sphere 3D"""
    print("🔧 FIX DEFINITIVO SPHERE 3D")
    print("="*60)
    
    # El problema principal: Engine usa _calculate_circle para sphere
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, backup)
        
        with open(engine_file, 'r') as f:
            content = f.read()
            lines = content.split('\\n')
        
        print("\\n1️⃣ Arreglando cálculo de sphere en engine...")
        
        # Buscar el caso sphere
        for i, line in enumerate(lines):
            if 'elif formation == "sphere"' in line:
                print(f"✅ Encontrado sphere en línea {i+1}")
                
                # Ver si usa _calculate_circle
                for j in range(i+1, min(len(lines), i+10)):
                    if '_calculate_circle' in lines[j]:
                        print("❌ Usa _calculate_circle (2D)")
                        
                        # Cambiar para usar FormationManager
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        
                        # Reemplazar con código que use FormationManager
                        new_code = [
                            lines[i],  # elif formation == "sphere":
                            ' ' * indent + '# Usar FormationManager para sphere 3D real',
                            ' ' * indent + 'from trajectory_hub.control.managers.formation_manager import FormationManager',
                            ' ' * indent + 'fm = FormationManager()',
                            ' ' * indent + 'positions = fm.calculate_formation("sphere", self.config["n_sources"])',
                            ' ' * indent + '# Convertir a lista si es necesario',
                            ' ' * indent + 'if isinstance(positions, list):',
                            ' ' * (indent+4) + 'pass  # Ya es lista',
                            ' ' * indent + 'else:',
                            ' ' * (indent+4) + 'positions = list(positions)'
                        ]
                        
                        # Encontrar el final del bloque elif
                        end_j = j + 1
                        current_indent = len(lines[i]) - len(lines[i].lstrip())
                        
                        for k in range(j+1, len(lines)):
                            if lines[k].strip() and len(lines[k]) - len(lines[k].lstrip()) <= current_indent:
                                end_j = k
                                break
                        
                        # Reemplazar
                        lines[i:end_j] = new_code
                        print("✅ Actualizado para usar FormationManager (3D)")
                        break
                break
        
        # Guardar
        with open(engine_file, 'w') as f:
            f.write('\\n'.join(lines))
        
        print("\\n✅ Engine actualizado")
    
    # Verificar OSC Bridge también
    print("\\n2️⃣ Verificando OSC Bridge...")
    
    bridge_file = "trajectory_hub/core/spat_osc_bridge.py"
    
    if os.path.exists(bridge_file):
        with open(bridge_file, 'r') as f:
            content = f.read()
        
        # Ya debería estar arreglado, pero verificar
        if 'def send_source_position(self, source_id: int, x: float, y: float)' in content:
            print("❌ OSC Bridge todavía no acepta Z")
            # Aplicar fix anterior...
        elif 'def send_source_position(self, source_id: int, x: float, y: float, z: float' in content:
            print("✅ OSC Bridge ya acepta Z")

if __name__ == "__main__":
    fix_sphere_definitively()
    print("\\n🚀 Prueba ahora - sphere debería ser 3D")
'''
    
    with open("fix_sphere_3d_definitive.py", 'w') as f:
        f.write(fix_content)
    
    print("✅ Fix creado: fix_sphere_3d_definitive.py")

if __name__ == "__main__":
    problem_file, problem_line = trace_z_loss_exact()
    create_definitive_fix()
    
    print("\n\n💡 PROBLEMA IDENTIFICADO:")
    print("Engine tiene su propio cálculo de sphere")
    print("Y está usando _calculate_circle (2D) en lugar de 3D")
    print("\n🔧 EJECUTA:")
    print("python fix_sphere_3d_definitive.py")