# === run_all_tests.py ===
# 🚀 Ejecutar TODOS los tests del sistema
# ⚡ Verificación completa del proyecto

import subprocess
import sys
import time
from datetime import datetime

print("🚀 EJECUTANDO SUITE COMPLETA DE TESTS")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Lista de tests a ejecutar
tests = [
    {
        "name": "Test Sistema Completo",
        "file": "test_sistema_completo.py",
        "description": "Verifica todos los componentes del sistema de deltas"
    },
    {
        "name": "Test Modos de Reproducción",
        "file": "test_modos_reproduccion.py", 
        "description": "Verifica modos Fix, Random, etc."
    },
    {
        "name": "Test Concentración Individual",
        "file": "test_concentration_working.py",
        "description": "Verifica ConcentrationComponent"
    },
    {
        "name": "Test Trayectorias Individuales",
        "file": "test_individual_final_fixed.py",
        "description": "Verifica IndividualTrajectory"
    },
    {
        "name": "Test Rotación Manual IS",
        "file": "test_manual_rotation_complete.py",
        "description": "Verifica ManualIndividualRotation"
    }
]

results = []

for i, test in enumerate(tests):
    print(f"\n{'='*60}")
    print(f"📋 TEST {i+1}/{len(tests)}: {test['name']}")
    print(f"   Archivo: {test['file']}")
    print(f"   Descripción: {test['description']}")
    print(f"{'='*60}")
    
    try:
        # Ejecutar test
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, test['file']], 
            capture_output=True, 
            text=True,
            timeout=30  # 30 segundos máximo por test
        )
        
        duration = time.time() - start_time
        
        # Verificar resultado
        if result.returncode == 0:
            # Buscar indicadores de éxito en la salida
            output = result.stdout
            if "✅" in output and "100%" in output:
                status = "✅ PASÓ"
            elif "ERROR" in output or "FAILED" in output:
                status = "❌ FALLÓ"
            else:
                status = "⚠️ COMPLETÓ (verificar salida)"
        else:
            status = "❌ ERROR"
            
        results.append({
            "test": test['name'],
            "status": status,
            "duration": f"{duration:.2f}s",
            "return_code": result.returncode
        })
        
        # Mostrar resumen
        print(f"\n🏁 Resultado: {status}")
        print(f"⏱️  Duración: {duration:.2f} segundos")
        
        # Mostrar últimas líneas de salida
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            print("\n📄 Últimas líneas de salida:")
            for line in lines[-5:]:
                print(f"   {line}")
                
    except subprocess.TimeoutExpired:
        results.append({
            "test": test['name'],
            "status": "⏱️ TIMEOUT",
            "duration": "30.00s+",
            "return_code": -1
        })
        print(f"\n⏱️ TIMEOUT: Test excedió 30 segundos")
        
    except FileNotFoundError:
        results.append({
            "test": test['name'],
            "status": "📁 NO ENCONTRADO",
            "duration": "0.00s",
            "return_code": -2
        })
        print(f"\n📁 ERROR: Archivo {test['file']} no encontrado")
        
    except Exception as e:
        results.append({
            "test": test['name'],
            "status": "💥 EXCEPCIÓN",
            "duration": "0.00s",
            "return_code": -3
        })
        print(f"\n💥 ERROR: {str(e)}")

# Resumen final
print("\n" + "="*80)
print("📊 RESUMEN FINAL DE TESTS")
print("="*80)

passed = sum(1 for r in results if "✅" in r['status'])
failed = sum(1 for r in results if "❌" in r['status'])
warnings = sum(1 for r in results if "⚠️" in r['status'])

print(f"\n📈 Estadísticas:")
print(f"   Total tests: {len(results)}")
print(f"   ✅ Pasados: {passed}")
print(f"   ❌ Fallados: {failed}")
print(f"   ⚠️ Advertencias: {warnings}")

print(f"\n📋 Detalle:")
for r in results:
    print(f"   {r['test']:.<40} {r['status']} ({r['duration']})")

print(f"\n🎯 VEREDICTO:")
if failed == 0 and warnings == 0:
    print("   ✅ TODOS LOS TESTS PASARON - SISTEMA 100% FUNCIONAL")
elif failed == 0:
    print("   ⚠️ Sistema funcional con advertencias")
else:
    print("   ❌ Sistema con fallos - revisar tests marcados")

# Guardar reporte
import json
report = {
    "timestamp": datetime.now().isoformat(),
    "results": results,
    "summary": {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "warnings": warnings
    }
}

with open("all_tests_report.json", "w") as f:
    json.dump(report, f, indent=2)
    
print(f"\n💾 Reporte guardado en: all_tests_report.json")