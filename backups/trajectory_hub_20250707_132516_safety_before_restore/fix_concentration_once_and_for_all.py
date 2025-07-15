# === fix_concentration_once_and_for_all.py ===
# 🔧 Fix: Implementar la solución EXACTA que funcionó antes
# ⚡ Basado en SESSION_SUMMARY_20250707

import os

def fix_concentration_completely():
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Backup
    import datetime
    backup_name = f"{engine_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_name, 'w') as f:
        f.writelines(lines)
    
    # 1. Buscar TODAS las definiciones de set_macro_concentration
    print("🔍 Buscando todas las definiciones de set_macro_concentration...")
    found_defs = []
    for i, line in enumerate(lines):
        if 'def set_macro_concentration' in line:
            found_defs.append(i)
            print(f"   Encontrada en línea {i+1}")
    
    # 2. Comentar todas menos la última (o insertar si no hay)
    if found_defs:
        # Comentar todas menos la última
        for idx in found_defs[:-1]:
            print(f"   Comentando definición en línea {idx+1}")
            # Comentar desde def hasta el siguiente def
            j = idx
            while j < len(lines) and not (j > idx and lines[j].strip().startswith('def ')):
                lines[j] = '# ' + lines[j]
                j += 1
    
    # 3. Insertar el método correcto
    print("\n✅ Insertando método correcto...")
    
    # Buscar dónde insertar (después de create_macro)
    insert_line = -1
    for i, line in enumerate(lines):
        if 'def create_macro' in line:
            # Buscar el siguiente def
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('def '):
                j += 1
            insert_line = j
            break
    
    if insert_line > 0:
        correct_method = '''    def set_macro_concentration(self, macro_id: str, factor: float):
        """Establecer factor de concentración para un macro."""
        if macro_id not in self._macros:
            print(f"❌ Macro '{macro_id}' no existe")
            return
            
        macro = self._macros[macro_id]
        macro.concentration_factor = max(0.0, min(1.0, factor))
        
        print(f"✅ Concentración de '{macro_id}' establecida a {macro.concentration_factor:.2f}")
        
        # Actualizar estado de macros si existe el método
        if hasattr(self, '_update_macro_states'):
            self._update_macro_states()

'''
        lines.insert(insert_line, correct_method)
    
    # 4. Asegurar que step() tiene la implementación correcta
    print("\n🔍 Verificando step()...")
    step_found = False
    for i, line in enumerate(lines):
        if line.strip().startswith('def step('):
            step_found = True
            print(f"   step() encontrado en línea {i+1}")
            
            # Verificar si contiene la lógica de concentración
            has_concentration = False
            for j in range(i, min(i+50, len(lines))):
                if 'concentration_factor' in lines[j]:
                    has_concentration = True
                    break
            
            if not has_concentration:
                print("   ⚠️ step() no tiene lógica de concentración")
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo actualizado")
    
    # Test final
    with open("test_final_concentration.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST FINAL CONCENTRACIÓN\\n")

engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

print("1. Configurando concentración...")
engine.set_macro_concentration(macro_id, 0.8)

# Verificar que se guardó
macro = engine._macros[macro_id]
factor = getattr(macro, 'concentration_factor', None)
print(f"   Factor guardado: {factor}")

if factor is None:
    print("\\n❌ FALLO: concentration_factor no se guardó")
    print("   Revisa que set_macro_concentration esté bien implementado")
else:
    print("\\n2. Posiciones iniciales:")
    for i in range(2):
        print(f"   Fuente {i}: {engine._positions[i]}")
    
    print("\\n3. Ejecutando 20 frames...")
    for _ in range(20):
        engine.step()
    
    print("\\n4. Posiciones finales:")
    for i in range(2):
        print(f"   Fuente {i}: {engine._positions[i]}")
    
    # Verificar convergencia
    dist_inicial = 4.0
    dist_final = np.linalg.norm(engine._positions[0] - engine._positions[1])
    
    print(f"\\nDistancia inicial: {dist_inicial:.2f}")
    print(f"Distancia final: {dist_final:.2f}")
    print(f"Reducción: {(1 - dist_final/dist_inicial)*100:.1f}%")
    
    if dist_final < dist_inicial * 0.9:
        print("\\n✅ ¡CONCENTRACIÓN FUNCIONA!")
    else:
        print("\\n❌ No hay concentración suficiente")
''')

if __name__ == "__main__":
    fix_concentration_completely()