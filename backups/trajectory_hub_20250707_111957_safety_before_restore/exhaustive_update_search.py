#!/usr/bin/env python3
"""
🔍 BÚSQUEDA EXHAUSTIVA - Encontrar cómo se actualiza el sistema
⚡ Rastrear desde el controller hasta las fuentes
"""

import os
import re

def exhaustive_search():
    """Búsqueda completa del flujo de actualización"""
    
    print("🔍 BÚSQUEDA EXHAUSTIVA DEL SISTEMA DE ACTUALIZACIÓN\n")
    
    # 1. Buscar en el controller
    print("1️⃣ ANALIZANDO EL CONTROLLER...")
    
    controller_file = "trajectory_hub/interface/interactive_controller.py"
    if os.path.exists(controller_file):
        with open(controller_file, 'r') as f:
            controller_content = f.read()
        
        # Buscar dónde dice engine.step
        step_calls = []
        lines = controller_content.split('\n')
        
        for i, line in enumerate(lines):
            if 'engine.step' in line or 'self.engine.step' in line:
                # Contexto
                context_start = max(0, i-5)
                context_end = min(len(lines), i+5)
                
                step_calls.append({
                    'line_no': i+1,
                    'line': line.strip(),
                    'context': lines[context_start:context_end]
                })
        
        if step_calls:
            print(f"   ✅ Encontradas {len(step_calls)} llamadas a engine.step()")
            
            for call in step_calls[:2]:  # Primeras 2
                print(f"\n   Línea {call['line_no']}: {call['line']}")
                print("   Contexto:")
                for ctx_line in call['context']:
                    print(f"      {ctx_line.rstrip()}")
        else:
            print("   ❌ No se encontraron llamadas a engine.step()")
    
    # 2. Ver si el controller tiene su propio step
    print("\n2️⃣ BUSCANDO step() EN EL CONTROLLER...")
    
    if 'controller_content' in locals():
        controller_methods = re.findall(r'def (step[^(]*)\(self[^)]*\):', controller_content)
        
        if controller_methods:
            print(f"   ✅ El controller tiene: {controller_methods}")
            
            # Ver qué hace el step del controller
            for method in controller_methods:
                pattern = rf'def {method}\(self[^)]*\):\s*\n(.*?)(?=\n    def|\nclass|\Z)'
                match = re.search(pattern, controller_content, re.DOTALL)
                
                if match:
                    body = match.group(1)
                    print(f"\n   📍 {method}() hace:")
                    
                    # Buscar llamadas al engine
                    engine_calls = re.findall(r'self\.engine\.(\w+)\(', body)
                    if engine_calls:
                        print(f"      Llama a engine.{set(engine_calls)}")
    
    # 3. Buscar en el engine qué métodos públicos tiene
    print("\n3️⃣ MÉTODOS PÚBLICOS DEL ENGINE...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            engine_content = f.read()
        
        # Buscar todos los métodos públicos
        public_methods = re.findall(r'def ([^_]\w*)\(self[^)]*\):', engine_content)
        
        # Filtrar los que podrían ser de actualización
        update_candidates = []
        for method in public_methods:
            if any(word in method.lower() for word in ['update', 'tick', 'step', 'process', 'run']):
                update_candidates.append(method)
        
        if update_candidates:
            print(f"   Candidatos de actualización: {update_candidates}")
            
            # Para cada candidato, ver si actualiza _source_motions
            for method in update_candidates:
                pattern = rf'def {method}\(self[^)]*\):\s*\n(.*?)(?=\n    def|\nclass|\Z)'
                match = re.search(pattern, engine_content, re.DOTALL)
                
                if match:
                    body = match.group(1)
                    if '_source_motions' in body:
                        print(f"\n   ✅ {method}() SÍ usa _source_motions")
                        
                        # Ver si actualiza
                        if '.update(' in body:
                            print(f"      ✅ Y llama a .update()")
                        else:
                            print(f"      ❌ Pero NO llama a .update()")
    
    # 4. Buscar el método update del engine que vimos antes
    print("\n4️⃣ ANALIZANDO engine.update()...")
    
    if 'engine_content' in locals():
        update_pattern = r'def update\(self[^)]*\):\s*\n(.*?)(?=\n    def|\nclass|\Z)'
        update_match = re.search(update_pattern, engine_content, re.DOTALL)
        
        if update_match:
            update_body = update_match.group(1)
            
            print("   ✅ engine.update() existe")
            
            # Ver qué hace
            if '_source_motions' in update_body:
                print("   ✅ Menciona _source_motions")
                
                # Ver si itera sobre ellas
                if 'for' in update_body and '_source_motions' in update_body:
                    print("   ✅ Itera sobre _source_motions")
                    
                    # Extraer el bucle
                    for_pattern = r'for\s+(\w+)(?:,\s*(\w+))?\s+in\s+[^:]+_source_motions[^:]+:(.*?)(?=\n\s*for|\n\s*if|\n\s*return|\Z)'
                    for_match = re.search(for_pattern, update_body, re.DOTALL)
                    
                    if for_match:
                        loop_body = for_match.group(3)
                        print("\n   📍 Dentro del bucle:")
                        
                        # Primeras líneas del bucle
                        loop_lines = loop_body.strip().split('\n')[:5]
                        for line in loop_lines:
                            print(f"      {line.strip()}")
                        
                        if '.update(' in loop_body:
                            print("\n      ✅ LLAMA A .update()!")
                        else:
                            print("\n      ❌ NO llama a .update()")
            else:
                print("   ❌ NO menciona _source_motions")
    
    # 5. Crear script de prueba directo
    print("\n5️⃣ CREANDO SCRIPT DE PRUEBA DIRECTO...")
    
    test_script = '''#!/usr/bin/env python3
"""
🧪 Test directo - Llamar update() del engine
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST DIRECTO DE ENGINE.UPDATE()\\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=3, formation="line", spacing=2.0)
    
    print("✅ Macro creado")
    
    # Verificar qué métodos tiene
    print("\\n📊 Métodos de actualización disponibles:")
    for method in ['update', 'step', 'tick', 'process']:
        if hasattr(engine, method):
            print(f"   ✅ engine.{method}() existe")
    
    # Posiciones iniciales
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        
        print(f"\\n📍 Posiciones iniciales ({len(motions)} fuentes):")
        pos_before = {}
        for sid, motion in motions.items():
            pos = motion.state.position.copy()
            pos_before[sid] = pos
            print(f"   Fuente {sid}: {pos}")
        
        # Aplicar concentración
        print("\\n🎯 Aplicando concentración 0.1...")
        engine.set_macro_concentration(macro_id, 0.1)
        
        # Probar update()
        print("\\n🔄 Llamando engine.update()...")
        result = engine.update()
        
        if isinstance(result, dict):
            print(f"   update() devolvió: {type(result).__name__} con {len(result)} claves")
        
        # Ver si cambió algo
        print("\\n📍 Posiciones después de update():")
        any_moved = False
        for sid, motion in motions.items():
            pos = motion.state.position
            if not np.allclose(pos, pos_before[sid]):
                print(f"   Fuente {sid}: {pos} ✅ CAMBIÓ")
                any_moved = True
            else:
                print(f"   Fuente {sid}: {pos} ❌ igual")
        
        if not any_moved:
            print("\\n⚠️  update() no movió las fuentes")
            print("\\n🔄 Intentando actualización manual...")
            
            # Update manual
            for motion in motions.values():
                motion.update(0.1)
            
            print("\\n📍 Después de update manual:")
            for sid, motion in motions.items():
                pos = motion.state.position
                if not np.allclose(pos, pos_before[sid]):
                    print(f"   Fuente {sid}: {pos} ✅ CAMBIÓ")
                    any_moved = True
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("test_direct_update.py", 'w') as f:
        f.write(test_script)
    
    print("   ✅ Script creado: test_direct_update.py")

if __name__ == "__main__":
    exhaustive_search()
    
    print("\n" + "="*60)
    print("📊 CONCLUSIONES")
    print("="*60)
    
    print("\n🚀 EJECUTA EL TEST:")
    print("   python test_direct_update.py")
    
    print("\n💡 Esto nos dirá:")
    print("   1. Si engine.update() mueve las fuentes")
    print("   2. Si necesitamos modificar update() o crear step()")
    print("   3. Cómo conectar todo correctamente")