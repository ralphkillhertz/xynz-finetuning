# === fix_active_sources_final.py ===
# 🔧 Fix: Verificar y corregir _active_sources definitivamente
# ⚡ Impacto: CRÍTICO - Desbloquea creación de macros

import os
import re

def fix_active_sources():
    """Verifica y corrige el problema con _active_sources"""
    
    print("🔧 FIX DEFINITIVO PARA _active_sources\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Verificar si _active_sources está en el __init__
    print("1️⃣ Buscando _active_sources en __init__...")
    
    # Buscar el __init__ completo
    init_pattern = r'(def __init__\(.*?\):\s*\n)(.*?)(?=\n    def|\n\nclass|\Z)'
    match = re.search(init_pattern, content, re.DOTALL)
    
    if match:
        init_header = match.group(1)
        init_body = match.group(2)
        
        # Verificar si _active_sources está ahí
        if 'self._active_sources' in init_body:
            print("✅ _active_sources encontrado en __init__")
            
            # Verificar la indentación
            lines = init_body.split('\n')
            for i, line in enumerate(lines):
                if '_active_sources' in line:
                    indent = len(line) - len(line.lstrip())
                    print(f"   Línea {i}: indentación={indent} espacios")
                    if indent != 8:
                        print("❌ Indentación incorrecta, corrigiendo...")
                        lines[i] = '        self._active_sources = set()'
            
            # Reconstruir
            init_body = '\n'.join(lines)
        else:
            print("❌ _active_sources NO encontrado, añadiendo...")
            
            # Buscar dónde insertar (después de motion_states)
            lines = init_body.split('\n')
            for i, line in enumerate(lines):
                if 'self.motion_states = {}' in line:
                    # Insertar después
                    lines.insert(i+1, '        self._active_sources = set()')
                    print("✅ _active_sources añadido después de motion_states")
                    break
            
            init_body = '\n'.join(lines)
        
        # Reconstruir el método completo
        new_init = init_header + init_body
        
        # Reemplazar en el contenido
        content = re.sub(init_pattern, new_init, content, flags=re.DOTALL)
    
    # 2. También verificar que create_source funcione
    print("\n2️⃣ Verificando create_source...")
    
    # Si create_source no existe, crearlo
    if 'def create_source' not in content:
        print("❌ create_source no existe, creando...")
        
        create_source_method = '''
    def create_source(self, source_id: int, name: str = None):
        """Crea una nueva fuente"""
        if source_id >= self.max_sources:
            print(f"❌ ID {source_id} excede el máximo de {self.max_sources}")
            return
            
        if source_id in self._active_sources:
            print(f"⚠️ Fuente {source_id} ya existe")
            return
            
        # Crear motion state
        state = MotionState(source_id=source_id)
        state.position = self._positions[source_id].copy()
        
        # Crear source motion
        motion = SourceMotion(state)
        self.motion_states[source_id] = motion
        self._source_motions[source_id] = motion
        
        # Registrar
        self._active_sources.add(source_id)
        if name:
            self._source_names[source_id] = name
            self._name_to_id[name] = source_id
            
        return source_id
'''
        
        # Insertar antes de create_macro
        create_macro_pos = content.find('def create_macro')
        if create_macro_pos > 0:
            content = content[:create_macro_pos] + create_source_method + '\n' + content[create_macro_pos:]
            print("✅ create_source añadido")
    
    # 3. Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Archivo actualizado")
    
    # 4. Test simplificado
    print("\n📝 Creando test simplificado...")
    
    test_code = '''# === test_active_sources.py ===
# 🧪 Test específico para _active_sources

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\\n🔍 TEST: Verificación de _active_sources\\n")

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Verificar atributo
    if hasattr(engine, '_active_sources'):
        print(f"✅ _active_sources existe: {engine._active_sources}")
    else:
        print("❌ _active_sources NO EXISTE")
        
        # Añadirlo manualmente para continuar
        engine._active_sources = set()
        print("⚠️ Añadido manualmente")
    
    # Crear macro
    macro_id = engine.create_macro("test", 2)
    print(f"✅ Macro creado: {macro_id}")
    
    # Verificar fuentes activas
    print(f"\\n📊 Fuentes activas: {engine._active_sources}")
    
    # Test de rotación rápido
    positions = [[1,0,0], [-1,0,0]]
    macro = engine._macros[macro_id]
    
    for i, sid in enumerate(list(macro.source_ids)[:2]):
        if sid < len(engine._positions):
            engine._positions[sid] = np.array(positions[i])
    
    # Aplicar rotación
    engine.set_macro_rotation(macro_id, 0, 1.0, 0)
    
    # Simular
    for _ in range(30):
        engine.update()
    
    # Verificar movimiento
    if not np.allclose(engine._positions[0], [1,0,0]):
        print("\\n✅ ¡ROTACIÓN FUNCIONANDO!")
    else:
        print("\\n❌ Sin movimiento")
        
except Exception as e:
    print(f"\\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open("test_active_sources.py", "w") as f:
        f.write(test_code)
    
    print("✅ Test creado")

if __name__ == "__main__":
    fix_active_sources()
    print("\n🚀 Ejecutando test...")
    os.system("python test_active_sources.py")