#!/usr/bin/env python3
"""
⚡ VERIFICACIÓN RÁPIDA DEL ESTADO ACTUAL
📊 Confirma que estamos en configuración pre-paralela
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_current_state():
    """Verificar estado actual del sistema"""
    print("🔍 VERIFICACIÓN RÁPIDA DEL ESTADO")
    print("="*60)
    
    checks = {
        'files_exist': True,
        'concentration_depends_on_is': None,
        'ms_rotation_blocked': None,
        'test_results': {}
    }
    
    # 1. Verificar archivos clave
    print("\n1️⃣ Verificando archivos clave...")
    key_files = [
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/core/motion_components.py", 
        "trajectory_hub/core/rotation_system.py",
        "interactive_controller.py"
    ]
    
    for file in key_files:
        exists = os.path.exists(file) or os.path.exists(f"trajectory_hub/{file}")
        print(f"  {'✅' if exists else '❌'} {file}")
        if not exists:
            checks['files_exist'] = False
    
    # 2. Test rápido de concentración
    print("\n2️⃣ Test rápido de concentración...")
    try:
        # Intentar importar y crear macro
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        engine = EnhancedTrajectoryEngine()
        
        # Crear macro sin trayectorias IS
        macro_id = engine.create_macro("test_concentration", 5)
        
        # Intentar aplicar concentración
        try:
            engine.set_concentration_factor(macro_id, 0.0)
            print("  ✅ Concentración se puede configurar")
            
            # Verificar si realmente funciona sin IS
            engine.update()
            checks['concentration_depends_on_is'] = False
            print("  ✅ Concentración parece funcionar sin IS")
        except Exception as e:
            print(f"  ❌ Error al aplicar concentración: {e}")
            checks['concentration_depends_on_is'] = True
            
    except Exception as e:
        print(f"  ⚠️ No se pudo hacer test: {e}")
    
    # 3. Verificar problema conocido de velocity
    print("\n3️⃣ Verificando modo de movimiento...")
    try:
        from trajectory_hub.core.motion_components import TrajectoryMovementMode
        modes = [mode.value for mode in TrajectoryMovementMode]
        if 'velocity' in modes:
            print("  ❌ Modo 'velocity' existe (no debería)")
        else:
            print("  ✅ Modo 'velocity' no existe (correcto, usar 'fix')")
            print(f"  Modos disponibles: {modes}")
    except Exception as e:
        print(f"  ⚠️ Error verificando modos: {e}")
    
    # RESUMEN
    print("\n" + "="*60)
    print("📊 RESUMEN DEL ESTADO")
    print("="*60)
    
    if checks['files_exist']:
        print("✅ Archivos principales presentes")
    else:
        print("❌ Faltan archivos clave")
        
    if checks['concentration_depends_on_is'] is False:
        print("✅ Concentración parece independiente")
    elif checks['concentration_depends_on_is'] is True:
        print("❌ Concentración depende de IS (problema confirmado)")
    else:
        print("⚠️ Estado de concentración no determinado")
    
    print("\n💡 CONCLUSIÓN:")
    if checks['concentration_depends_on_is']:
        print("El sistema está en estado pre-paralelo con problemas conocidos")
        print("Listo para ejecutar diagnóstico profundo")
    else:
        print("El sistema puede tener cambios parciales aplicados")
        print("Se recomienda verificar con diagnóstico completo")

if __name__ == "__main__":
    check_current_state()
    
    print("\n\n🚀 PRÓXIMO PASO RECOMENDADO:")
    print("python deep_diagnostic_system.py")