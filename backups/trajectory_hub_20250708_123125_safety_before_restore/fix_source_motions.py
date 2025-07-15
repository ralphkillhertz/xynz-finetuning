# === fix_source_motions.py ===
# 🔧 Fix: Añadir atributo _source_motions y arreglar create_macro
# ⚡ Impacto: CRÍTICO - Habilita creación de macros

import os
import re

def fix_source_motions():
    """Añade _source_motions al constructor y arregla create_macro"""
    
    print("🔧 ARREGLANDO _source_motions Y create_macro\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Añadir _source_motions al __init__
    print("1️⃣ Añadiendo _source_motions al constructor...")
    
    # Buscar donde añadir en el __init__
    init_pattern = r'(self\.motion_states = \{\})'
    if re.search(init_pattern, content):
        # Añadir después de motion_states
        replacement = r'\1\n        self._source_motions = {}'
        content = re.sub(init_pattern, replacement, content)
        print("✅ _source_motions añadido al constructor")
    
    # 2. Arreglar create_macro para que funcione correctamente
    print("\n2️⃣ Arreglando método create_macro...")
    
    # Buscar el método create_macro
    create_macro_pattern = r'def create_macro\(self, name: str, num_sources: int.*?\).*?:'
    
    if re.search(create_macro_pattern, content):
        # Reemplazar el método completo
        new_create_macro = '''    def create_macro(self, name: str, num_sources: int, 
                     formation: str = "line", **kwargs) -> str:
        """Crea un nuevo macro con las fuentes especificadas"""
        # Generar ID único
        macro_id = f"macro_{self._macro_counter}_{name}"
        self._macro_counter += 1
        
        # Encontrar fuentes disponibles
        used_sources = set()
        for macro in self._macros.values():
            used_sources.update(macro.source_ids)
        
        # Asignar nuevas fuentes
        source_ids = []
        for i in range(self.max_sources):
            if i not in used_sources and len(source_ids) < num_sources:
                source_ids.append(i)
                
                # Crear SourceMotion si no existe
                if i not in self.motion_states:
                    state = MotionState(source_id=i)
                    state.position = self._positions[i].copy()
                    motion = SourceMotion(state)
                    self.motion_states[i] = motion
                    self._source_motions[i] = motion  # Mantener compatibilidad
                    
                    # Crear nombre de fuente
                    source_name = f"{name}_{i}"
                    print(f"✅ Fuente {i} creada: {source_name}")
        
        if len(source_ids) < num_sources:
            print(f"⚠️ Solo se pudieron asignar {len(source_ids)} de {num_sources} fuentes")
        
        # Crear el macro
        from .macro_behaviors import MacroBehavior
        macro = MacroBehavior(macro_id, source_ids)
        self._macros[macro_id] = macro
        
        # Aplicar formación
        self.apply_formation(macro_id, formation, **kwargs)
        
        # Crear moduladores si están habilitados
        if self.enable_modulator:
            for sid in source_ids:
                if sid not in self.orientation_modulators:
                    try:
                        modulator = self.create_orientation_modulator(sid)
                    except:
                        print(f"No se puede crear modulador para fuente inexistente {sid}")
        
        print(f"✅ Macro '{macro_id}' creado")
        return macro_id'''
        
        # Buscar y reemplazar el método completo
        method_pattern = r'def create_macro\(.*?\).*?:.*?(?=\n    def|\n\nclass|\Z)'
        content = re.sub(method_pattern, new_create_macro, content, flags=re.DOTALL)
        print("✅ create_macro actualizado")
    
    # 3. Añadir imports necesarios
    print("\n3️⃣ Verificando imports...")
    
    if "from .motion_components import" in content and "MotionState" not in content:
        content = content.replace(
            "from .motion_components import",
            "from .motion_components import MotionState, SourceMotion,"
        )
        print("✅ Imports de MotionState y SourceMotion añadidos")
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Archivo actualizado")

if __name__ == "__main__":
    fix_source_motions()
    print("\n🚀 Ejecutando test...")
    os.system("python test_rotation_working.py")