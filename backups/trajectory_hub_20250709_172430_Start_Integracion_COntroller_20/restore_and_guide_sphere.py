import os
import shutil
from datetime import datetime
import json

def execute_option_1():
    """Ejecutar opción 1: Restaurar y guiar para sphere"""
    print("🔄 EJECUTANDO OPCIÓN 1: RESTAURAR + GUÍA SPHERE")
    print("="*60)
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # 1. Encontrar mejor backup
    print("\n1️⃣ BUSCANDO MEJOR BACKUP...")
    
    import glob
    backups = glob.glob(f"{engine_file}.backup_*")
    backups.sort()
    
    # Buscar backup funcional antes de cambios de sphere
    selected_backup = None
    
    # Priorizar backups específicos que sabemos que funcionan
    preferred_backups = [
        "backup_macro_fix_20250708",
        "backup_20250708",
        "backup_20250707"
    ]
    
    for backup in backups:
        basename = os.path.basename(backup)
        
        # Buscar por patrones preferidos
        for preferred in preferred_backups:
            if preferred in basename:
                selected_backup = backup
                print(f"✅ Encontrado backup preferido: {basename}")
                break
        
        if selected_backup:
            break
    
    # Si no hay preferido, buscar uno sin sphere/fix
    if not selected_backup:
        for backup in reversed(backups):  # Más reciente primero
            basename = os.path.basename(backup)
            if not any(word in basename.lower() for word in ['sphere', 'fix', 'emergency', '162']):
                selected_backup = backup
                print(f"✅ Seleccionado: {basename}")
                break
    
    if not selected_backup:
        print("❌ No se encontró backup adecuado")
        return False
    
    # 2. Crear backup actual
    print("\n2️⃣ CREANDO BACKUP DEL ESTADO ACTUAL...")
    current_backup = f"{engine_file}.backup_broken_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_file, current_backup)
    print(f"✅ Backup creado: {os.path.basename(current_backup)}")
    
    # 3. Restaurar
    print("\n3️⃣ RESTAURANDO...")
    shutil.copy(selected_backup, engine_file)
    print(f"✅ Restaurado desde: {os.path.basename(selected_backup)}")
    
    # 4. Verificar
    print("\n4️⃣ VERIFICANDO...")
    try:
        # Intentar importar
        import sys
        if 'trajectory_hub' in sys.modules:
            del sys.modules['trajectory_hub']
        
        import trajectory_hub
        print("✅ El sistema puede importarse correctamente")
    except Exception as e:
        print(f"❌ Error al importar: {e}")
        return False
    
    # 5. Guía para sphere
    print("\n5️⃣ GUÍA PARA AÑADIR SPHERE MANUALMENTE:")
    print("="*60)
    
    print("\n📋 INSTRUCCIONES (según ADN del proyecto):")
    print("\n1. Abrir trajectory_hub/core/enhanced_trajectory_engine.py")
    print("\n2. Buscar los imports al inicio (líneas 1-50)")
    print("   Añadir DESPUÉS de los otros imports de trajectory_hub:")
    print("   from trajectory_hub.control.managers.formation_manager import FormationManager")
    
    print("\n3. Buscar donde están los casos de formation")
    print("   (buscar 'elif formation == \"random\"')")
    print("\n4. DESPUÉS del último elif, añadir:")
    print("""
        elif formation == "sphere":
            # Usar FormationManager para sphere 3D real (solución temporal)
            if not hasattr(self, '_fm'):
                self._fm = FormationManager()
            positions = self._fm.calculate_formation("sphere", self.config['n_sources'])
            print(f"🌐 Sphere 3D: {len(positions)} posiciones calculadas")
""")
    
    print("\n5. Guardar el archivo")
    
    print("\n6. Verificar OSC en spat_osc_bridge.py:")
    print("   - send_source_position debe aceptar x, y, z")
    print("   - Debe enviar [x, y, z] no solo [x, y]")
    
    # 6. Crear script helper
    create_sphere_helper_script()
    
    return True

def create_sphere_helper_script():
    """Crear script que ayude a verificar sphere"""
    
    helper_content = '''#!/usr/bin/env python3
"""
Helper script para verificar sphere después de añadirlo manualmente
"""

def check_sphere():
    """Verificar que sphere funciona"""
    print("🧪 VERIFICANDO SPHERE...")
    
    try:
        # 1. Verificar FormationManager
        from trajectory_hub.control.managers.formation_manager import FormationManager
        fm = FormationManager()
        positions = fm.calculate_formation("sphere", 5)
        
        print("\\n✅ FormationManager funciona:")
        for i, pos in enumerate(positions):
            print(f"   {i}: {pos}")
        
        # 2. Verificar que es 3D
        z_values = [p[2] for p in positions]
        if len(set(z_values)) > 1:
            print("\\n✅ Las posiciones son 3D (variación en Z)")
        else:
            print("\\n❌ Las posiciones son 2D (sin variación en Z)")
        
        # 3. Verificar imports en engine
        import trajectory_hub.core.enhanced_trajectory_engine as engine
        
        if hasattr(engine, 'FormationManager'):
            print("\\n✅ Engine puede acceder a FormationManager")
        else:
            print("\\n⚠️ Engine podría no tener acceso a FormationManager")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    if check_sphere():
        print("\\n🎯 Todo listo para probar sphere en el programa")
        print("\\nEjecuta:")
        print("python -m trajectory_hub.interface.interactive_controller")
    else:
        print("\\n❌ Hay problemas que resolver")
'''
    
    with open("check_sphere_helper.py", 'w') as f:
        f.write(helper_content)
    
    os.chmod("check_sphere_helper.py", 0o755)
    print("\n✅ Script helper creado: check_sphere_helper.py")

def save_restoration_log():
    """Guardar log de la restauración"""
    log = {
        "timestamp": datetime.now().isoformat(),
        "action": "restoration_to_working_state",
        "reason": "syntax_errors_from_sphere_implementation",
        "notes": [
            "Sistema restaurado a versión funcional",
            "Sphere debe añadirse manualmente siguiendo el ADN",
            "La arquitectura actual viola los principios pero es funcional"
        ],
        "next_steps": [
            "Añadir sphere manualmente según instrucciones",
            "Probar con check_sphere_helper.py",
            "Considerar refactorización completa según roadmap"
        ]
    }
    
    with open(f"restoration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(log, f, indent=2)

if __name__ == "__main__":
    success = execute_option_1()
    
    if success:
        save_restoration_log()
        
        print("\n\n" + "="*60)
        print("✅ RESTAURACIÓN COMPLETADA")
        print("="*60)
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Sigue las instrucciones para añadir sphere manualmente")
        print("2. Ejecuta: python check_sphere_helper.py")
        print("3. Prueba: python -m trajectory_hub.interface.interactive_controller")
        
        print("\n📋 IMPORTANTE:")
        print("- El sistema ahora debería funcionar (sin sphere)")
        print("- Añade sphere con cuidado siguiendo las instrucciones")
        print("- Respeta siempre el ADN del proyecto")
    else:
        print("\n❌ La restauración falló")
        print("Considera restaurar manualmente desde un backup conocido")