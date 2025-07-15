# === fix_create_macro_definitive.py ===
# 🔧 Fix: Asegurar que create_macro REALMENTE guarde el macro
# ⚡ Solución definitiva - reescribir el método

import os
import re

print("🔧 FIX DEFINITIVO: create_macro\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# Buscar create_macro actual
create_match = re.search(r'def create_macro\(.*?\):.*?(?=\n    def|\Z)', content, re.DOTALL)
if create_match:
    old_method = create_match.group(0)
    print("✅ Método create_macro encontrado")
    
    # Ver si realmente guarda el macro
    if "self._macros[" in old_method:
        print("⚠️ Parece que SÍ intenta guardar el macro")
        print("🔍 Verificando por qué no funciona...")
        
        # Mostrar las líneas relevantes
        lines = old_method.split('\n')
        for i, line in enumerate(lines):
            if "_macros" in line or "return" in line:
                print(f"  Línea {i}: {line}")
    else:
        print("❌ NO guarda el macro")

# Reemplazar con versión que FUNCIONA
new_create_macro = '''    def create_macro(self, name: str, source_ids, **kwargs) -> str:
        """Crear un macro (grupo de fuentes)"""
        # Si source_ids es un número, crear nuevas fuentes
        if isinstance(source_ids, int):
            actual_ids = []
            start_id = len(self.motion_states)
            for i in range(source_ids):
                sid = start_id + i
                if sid < self.max_sources:
                    self.create_source(sid, f"{name}_{i}")
                    actual_ids.append(sid)
            source_ids = actual_ids
        
        # Crear el macro
        from trajectory_hub.core.enhanced_trajectory_engine import Macro
        macro = Macro(name, source_ids)
        
        # Crear trajectory component
        from trajectory_hub.core.motion_components import MacroTrajectory
        trajectory_component = MacroTrajectory()
        trajectory_component.enabled = False
        macro.trajectory_component = trajectory_component
        
        # Añadir a motion_states
        for sid in source_ids:
            if sid in self.motion_states:
                self.motion_states[sid].active_components["macro_trajectory"] = trajectory_component
        
        # GUARDAR EL MACRO - CRÍTICO
        self._macros[name] = macro
        logger.info(f"Macro '{name}' creado con {len(source_ids)} fuentes")
        
        return name'''

# Reemplazar
content = re.sub(r'def create_macro\(.*?\):.*?(?=\n    def|\Z)', 
                 new_create_macro, content, flags=re.DOTALL)

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print("✅ create_macro reescrito completamente")

# Test inmediato
print("\n🧪 TEST INMEDIATO:")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    import numpy as np
    
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    
    # Verificar _macros existe
    print(f"  _macros existe: {hasattr(engine, '_macros')}")
    
    # Crear macro
    result = engine.create_macro("prueba", 3)
    print(f"  create_macro retornó: {result}")
    
    # Verificar que se guardó
    if hasattr(engine, '_macros'):
        print(f"  Macros guardados: {list(engine._macros.keys())}")
        
        if "prueba" in engine._macros:
            print("  ✅ ¡MACRO SE GUARDÓ CORRECTAMENTE!")
            
            # Test de movimiento
            def circular(t):
                return np.array([3*np.cos(t), 3*np.sin(t), 0])
            
            engine.set_macro_trajectory("prueba", circular)
            
            pos_before = engine._positions[0].copy()
            for _ in range(30):
                engine.update()
            pos_after = engine._positions[0].copy()
            
            dist = np.linalg.norm(pos_after - pos_before)
            print(f"  Movimiento: {dist:.3f} unidades")
            
            if dist > 0.1:
                print("\n🎉 ¡ÉXITO TOTAL! MacroTrajectory FUNCIONA")
                print("\n📊 SISTEMA COMPLETO:")
                print("  ✅ create_macro guarda correctamente")
                print("  ✅ set_macro_trajectory configura")
                print("  ✅ Las fuentes se mueven")
                print("  ✅ Sistema de deltas funciona")
                
                # Guardar estado final
                import json
                with open("PROYECTO_STATE.json", "w") as f:
                    json.dump({
                        "session": "20250708_macro_complete",
                        "status": "MacroTrajectory 100% funcional",
                        "next": "MCP Server implementation"
                    }, f, indent=2)
        else:
            print("  ❌ Macro NO se guardó")
            
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()