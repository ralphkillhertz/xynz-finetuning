#!/usr/bin/env python3
"""
🚨 DIAGNÓSTICO CRÍTICO - Rastrear qué se ejecuta realmente
⚡ Inyectar prints para ver el flujo real
"""

import os
import shutil
from datetime import datetime

def inject_debug_traces():
    """Inyectar trazas de debug en puntos críticos"""
    
    print("🚨 INYECTANDO TRAZAS DE DEBUG\n")
    
    # Backup
    backup_dir = f"backup_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. Enhanced Trajectory Engine
    print("1️⃣ MODIFICANDO enhanced_trajectory_engine.py...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        shutil.copy2(engine_file, os.path.join(backup_dir, "enhanced_trajectory_engine.py"))
        
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Inyectar en set_macro_concentration
        if 'def set_macro_concentration' in content:
            content = content.replace(
                'def set_macro_concentration(self',
                '''def set_macro_concentration(self'''
            )
            
            # Agregar print al inicio
            content = content.replace(
                'def set_macro_concentration(self, macro_id: str, factor: float',
                '''def set_macro_concentration(self, macro_id: str, factor: float'''
            )
            
            # Buscar el inicio del método y agregar print
            import re
            pattern = r'(def set_macro_concentration\(self.*?\).*?:\s*\n)(.*?)(?=\n    def|\nclass|\Z)'
            
            def add_print(match):
                method_def = match.group(1)
                method_body = match.group(2)
                
                # Agregar print al inicio
                new_body = '        print(f"🔍 DEBUG: set_macro_concentration llamado - macro_id={macro_id}, factor={factor}")\n' + method_body
                
                return method_def + new_body
            
            content = re.sub(pattern, add_print, content, count=1, flags=re.DOTALL)
        
        # Inyectar en update
        update_pattern = r'(def update\(self.*?\).*?:\s*\n)(.*?)(?=\n    def|\nclass|\Z)'
        
        def add_update_print(match):
            method_def = match.group(1)
            method_body = match.group(2)
            
            new_body = '        print("🔍 DEBUG: EnhancedTrajectoryEngine.update() llamado")\n' + method_body
            
            # También agregar print cuando se envían posiciones
            if 'send_position' in method_body:
                new_body = new_body.replace(
                    'send_position(',
                    'send_position(  # DEBUG\n                print(f"🔍 DEBUG: Enviando posición {source_id}: {position}")\n                self.osc_bridge.'
                )
            
            return method_def + new_body
        
        content = re.sub(update_pattern, add_update_print, content, count=1, flags=re.DOTALL)
        
        with open(engine_file, 'w') as f:
            f.write(content)
        
        print("   ✅ Trazas agregadas")
    
    # 2. Motion Components
    print("\n2️⃣ MODIFICANDO motion_components.py...")
    
    motion_file = "trajectory_hub/core/motion_components.py"
    if os.path.exists(motion_file):
        shutil.copy2(motion_file, os.path.join(backup_dir, "motion_components.py"))
        
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Buscar SourceMotion
        if 'class SourceMotion' in content:
            # Inyectar en update
            update_pattern = r'(class SourceMotion.*?def update\(self.*?\).*?:\s*\n)(.*?)(?=\n    def|\nclass|\Z)'
            
            def add_motion_debug(match):
                before = match.group(1)
                method_body = match.group(2)
                
                new_body = '        print(f"🔍 DEBUG: SourceMotion.update() - time={self.time:.2f}")\n' + method_body
                
                # Agregar prints para offsets
                if 'concentration_offset' in method_body:
                    new_body = new_body.replace(
                        'self.concentration_offset =',
                        'self.concentration_offset =  # DEBUG\n        print(f"🔍 DEBUG: concentration_offset = {self.concentration_offset}")\n        self.concentration_offset ='
                    )
                
                return before + new_body
            
            content = re.sub(update_pattern, add_motion_debug, content, count=1, flags=re.DOTALL)
            
            # Inyectar en get_position
            if 'def get_position' in content:
                get_pos_pattern = r'(def get_position\(self.*?\).*?:\s*\n)(.*?)(?=\n    def|\nclass|\Z)'
                
                def add_getpos_debug(match):
                    method_def = match.group(1)
                    method_body = match.group(2)
                    
                    # Agregar print al inicio
                    new_body = '        print(f"🔍 DEBUG: SourceMotion.get_position() llamado")\n' + method_body
                    
                    # Agregar print antes del return
                    new_body = re.sub(
                        r'(return.*)',
                        r'print(f"🔍 DEBUG: Retornando posición: {result}")\n        \1',
                        new_body
                    )
                    
                    # Cambiar el return para guardar el resultado primero
                    new_body = re.sub(
                        r'return (.*)',
                        r'result = \1\n        print(f"🔍 DEBUG: Posición final = {result}")\n        return result',
                        new_body
                    )
                    
                    return method_def + new_body
                
                content = re.sub(get_pos_pattern, add_getpos_debug, content, count=1, flags=re.DOTALL)
        
        with open(motion_file, 'w') as f:
            f.write(content)
        
        print("   ✅ Trazas agregadas")
    
    # 3. Script de prueba
    print("\n3️⃣ CREANDO SCRIPT DE PRUEBA...")
    
    test_script = '''#!/usr/bin/env python3
"""
🧪 Script de prueba con debug habilitado
"""

import sys
import os

# Setup path
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

# Deshabilitar OSC para evitar errores
os.environ['DISABLE_OSC'] = '1'

print("🧪 INICIANDO PRUEBA DE CONCENTRACIÓN CON DEBUG\\n")
print("="*60)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine
    print("1️⃣ Creando engine...")
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro
    print("\\n2️⃣ Creando macro...")
    macro_id = engine.create_macro("debug_test", source_count=3, formation="line", spacing=2.0)
    print(f"   Macro creado: {macro_id}")
    
    # Aplicar concentración
    print("\\n3️⃣ Aplicando concentración...")
    engine.set_macro_concentration(macro_id, 0.1)
    
    # Update
    print("\\n4️⃣ Llamando update...")
    engine.update()
    
    print("\\n" + "="*60)
    print("✅ Prueba completada - revisa los mensajes DEBUG arriba")
    
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("test_with_debug.py", 'w') as f:
        f.write(test_script)
    
    print("   ✅ Script creado: test_with_debug.py")
    
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    print("\n✅ Trazas de debug inyectadas en:")
    print("   • enhanced_trajectory_engine.py")
    print("   • motion_components.py")
    
    print(f"\n📁 Backup en: {backup_dir}")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("\n1. Ejecutar el test con debug:")
    print("   python test_with_debug.py")
    print("\n2. Ver qué métodos se llaman realmente")
    print("\n3. Ejecutar el controller y ver los mensajes:")
    print("   python trajectory_hub/interface/interactive_controller.py")
    print("\n⚠️  IMPORTANTE: Los mensajes DEBUG aparecerán en la consola")

if __name__ == "__main__":
    inject_debug_traces()