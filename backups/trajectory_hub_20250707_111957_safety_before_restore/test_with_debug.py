#!/usr/bin/env python3
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

print("🧪 INICIANDO PRUEBA DE CONCENTRACIÓN CON DEBUG\n")
print("="*60)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine
    print("1️⃣ Creando engine...")
    engine = EnhancedTrajectoryEngine()
    
    # Crear macro
    print("\n2️⃣ Creando macro...")
    macro_id = engine.create_macro("debug_test", source_count=3, formation="line", spacing=2.0)
    print(f"   Macro creado: {macro_id}")
    
    # Aplicar concentración
    print("\n3️⃣ Aplicando concentración...")
    engine.set_macro_concentration(macro_id, 0.1)
    
    # Update
    print("\n4️⃣ Llamando update...")
    engine.update()
    
    print("\n" + "="*60)
    print("✅ Prueba completada - revisa los mensajes DEBUG arriba")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
