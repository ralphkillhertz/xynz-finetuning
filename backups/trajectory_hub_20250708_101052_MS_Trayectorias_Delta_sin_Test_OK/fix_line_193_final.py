# === fix_line_193_final.py ===
# 🔧 Fix: Arreglar solo la línea 193 que tiene mala indentación
# ⚡ Última corrección para que todo funcione

import os

print("🔧 ARREGLANDO LÍNEA 193 (última vez)...\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar y corregir línea 193
if len(lines) > 192:
    print(f"Línea 193 actual: {repr(lines[192])}")
    
    # Si contiene _macros, corregir indentación
    if '_macros' in lines[192]:
        lines[192] = '        self._macros = {}  # Almacén de macros\n'
        print("✅ Línea 193 corregida")
        
        # Si hay duplicados, eliminarlos
        if len(lines) > 193 and '_macros' in lines[193]:
            print("❌ Eliminando duplicado en línea 194")
            lines.pop(193)

# Guardar
with open(file_path, 'w') as f:
    f.writelines(lines)

print("\n✅ Archivo corregido")

# TEST FINAL DEFINITIVO
print("\n🧪 TEST FINAL DEFINITIVO...")
import subprocess
result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                      capture_output=True, text=True)

if result.returncode == 0:
    print("\n✅ IMPORT EXITOSO")
    
    # Mostrar progreso del test
    for line in result.stdout.split('\n'):
        if any(word in line for word in ['✅', '❌', 'ÉXITO', 'TEST', 'Verificando', 'Creando', 'Frame', 'distancia']):
            print(line)
    
    if "ÉXITO TOTAL" in result.stdout:
        print("\n" + "="*70)
        print("🎉 ¡MACROTRAJECTORY COMPLETAMENTE MIGRADO A DELTAS!")
        print("="*70)
        print("\n📊 ESTADO FINAL:")
        print("✅ Sistema de deltas: 100%")
        print("✅ ConcentrationComponent: 100%")
        print("✅ IndividualTrajectory: 100%")
        print("✅ MacroTrajectory: 100%")
        print("✅ engine.update(): 100% automático")
        
        # Guardar estado
        import json
        state = {
            "session_id": "20250708_macro_trajectory_complete",
            "timestamp": "2025-07-08T10:00:00",
            "phase": "delta_migrations_75_percent",
            "status": "✅ MacroTrajectory migrado exitosamente",
            
            "trabajo_realizado": {
                "macro_trajectory_migration": "100%",
                "calculate_delta_added": True,
                "create_macro_fixed": True,
                "motion_states_integration": True
            },
            
            "sistema_deltas": {
                "arquitectura": "100%",
                "concentration": "100%",
                "individual_trajectory": "100%",
                "macro_trajectory": "100%",
                "engine_automation": "100%"
            },
            
            "pendiente_proxima_sesion": [
                "1. CRÍTICO: Servidor MCP (0%)",
                "2. Migrar rotaciones algorítmicas MS",
                "3. Migrar rotaciones manuales MS",
                "4. Integrar modulador 3D",
                "5. Completar lista TO-DO"
            ],
            
            "comando_siguiente": "Iniciar implementación MCP Server"
        }
        
        with open("PROYECTO_STATE.json", "w") as f:
            json.dump(state, f, indent=2)
        
        print("\n📝 Estado guardado en PROYECTO_STATE.json")
        print("\n🚀 PRÓXIMO: Servidor MCP (objetivo principal del proyecto)")
else:
    print(f"\n❌ Error: {result.stderr}")