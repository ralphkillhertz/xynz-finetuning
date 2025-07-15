import json
import os
from datetime import datetime
import shutil

def review_project_dna():
    """Revisar el ADN del proyecto documentado"""
    print("📋 REVISANDO ADN DEL PROYECTO")
    print("="*60)
    
    # 1. Cargar PROJECT_DNA_IMMUTABLE.json
    if os.path.exists("PROJECT_DNA_IMMUTABLE.json"):
        with open("PROJECT_DNA_IMMUTABLE.json", 'r') as f:
            dna = json.load(f)
        
        print("\n✅ PROJECT_DNA_IMMUTABLE.json cargado")
        
        # Mostrar información clave
        project_dna = dna.get("🧬 TRAJECTORY_HUB_DNA_v2", {})
        
        print("\n1️⃣ ESTADO ACTUAL DOCUMENTADO:")
        estado_actual = project_dna.get("📊 ESTADO_ACTUAL_REAL", {})
        
        # Flujo actual
        flujo = estado_actual.get("flujo_creacion_macros", {})
        print("\n   Flujo de creación de macros:")
        for paso in flujo.get("pasos", []):
            print(f"   • {paso['componente']}: {paso['accion']}")
            if paso.get("problema"):
                print(f"     ❌ Problema: {paso['problema']}")
        
        # Responsabilidades
        print("\n   Responsabilidades por componente:")
        responsabilidades = estado_actual.get("responsabilidades", {})
        for comp, info in responsabilidades.items():
            print(f"\n   {comp}:")
            print(f"     Métodos: {info['metodos']}")
            print(f"     Responsabilidades: {', '.join(info['responsabilidades'])}")
            if info.get("viola_arquitectura"):
                print(f"     ❌ Violaciones: {', '.join(info['viola_arquitectura'])}")
        
        print("\n2️⃣ VIOLACIONES ARQUITECTÓNICAS:")
        violaciones = project_dna.get("❌ VIOLACIONES_ACTUALES", [])
        for v in violaciones:
            print(f"\n   [{v['tipo']}] {v['componente']}")
            print(f"   Problema: {v['problema']}")
            print(f"   Solución: {v['solucion']}")
        
        print("\n3️⃣ SOLUCIÓN PARA SPHERE:")
        sphere_fix = project_dna.get("🔧 PARA_ARREGLAR_SPHERE", {})
        print(f"   Problema: {sphere_fix.get('problema')}")
        print(f"   Solución temporal: {sphere_fix.get('solucion_temporal')}")
        print(f"   Solución correcta: {sphere_fix.get('solucion_correcta')}")
        
        return project_dna
    else:
        print("❌ No se encuentra PROJECT_DNA_IMMUTABLE.json")
        return None

def restore_to_known_working_state():
    """Restaurar a un estado conocido que funcione"""
    print("\n\n🔄 RESTAURACIÓN A ESTADO FUNCIONAL CONOCIDO")
    print("="*60)
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Buscar backup antes de los cambios de sphere
    import glob
    backups = glob.glob(f"{engine_file}.backup_*")
    backups.sort()
    
    # Filtrar backups problemáticos
    good_backups = []
    for backup in backups:
        basename = os.path.basename(backup)
        # Evitar backups con sphere, fix, o muy recientes
        if not any(word in basename.lower() for word in ['sphere', 'fix', 'emergency', '20250709_16']):
            good_backups.append(backup)
    
    if good_backups:
        print(f"\n✅ Encontrados {len(good_backups)} backups potencialmente buenos")
        
        # Usar el más reciente de los buenos
        selected_backup = good_backups[-1]
        print(f"\n📋 Seleccionado: {os.path.basename(selected_backup)}")
        
        # Crear backup del estado actual antes de restaurar
        current_backup = f"{engine_file}.backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, current_backup)
        print(f"📦 Backup del estado actual: {os.path.basename(current_backup)}")
        
        # Restaurar
        shutil.copy(selected_backup, engine_file)
        print(f"✅ Restaurado desde: {os.path.basename(selected_backup)}")
        
        return True
    else:
        print("❌ No se encontraron backups buenos")
        return False

def apply_sphere_respecting_architecture(dna):
    """Aplicar sphere respetando la arquitectura documentada"""
    print("\n\n🔧 APLICANDO SPHERE SEGÚN ARQUITECTURA DOCUMENTADA")
    print("="*60)
    
    if not dna:
        print("❌ No hay ADN del proyecto para guiar")
        return
    
    # Según el ADN, Engine NO debe calcular formaciones
    # Pero la arquitectura actual lo hace así
    # Solución temporal: hacer que Engine use FormationManager
    
    print("\n📋 Según PROJECT_DNA_IMMUTABLE:")
    print("   • Engine actualmente calcula formaciones (MAL)")
    print("   • Solución temporal: Engine debe usar FormationManager")
    print("   • Solución correcta: Refactorizar todo el flujo")
    
    print("\n⚠️ Aplicaremos la solución TEMPORAL documentada")
    
    # Esta es la implementación documentada en el ADN
    # NO la ejecutamos automáticamente
    
    print("\n📄 Código a aplicar (según ADN del proyecto):")
    print("-" * 40)
    print("""
1. Añadir import (AL INICIO con otros imports):
   from trajectory_hub.control.managers.formation_manager import FormationManager

2. Añadir caso sphere (después del último elif formation):
   elif formation == "sphere":
       # Usar FormationManager para sphere 3D real
       if not hasattr(self, '_fm'):
           self._fm = FormationManager()
       positions = self._fm.calculate_formation("sphere", self.config['n_sources'])
       print(f"🌐 Sphere 3D: {len(positions)} posiciones calculadas")

3. Verificar que OSC envíe x,y,z
""")
    
    print("\n⚠️ IMPORTANTE:")
    print("   Este cambio es TEMPORAL")
    print("   La solución correcta requiere refactorización completa")

def main():
    """Proceso principal"""
    # 1. Revisar ADN del proyecto
    dna = review_project_dna()
    
    # 2. Preguntar qué hacer
    print("\n\n" + "="*60)
    print("💡 OPCIONES BASADAS EN EL ADN DEL PROYECTO:")
    print("="*60)
    print("\n1. Restaurar a versión funcional anterior (sin sphere)")
    print("2. Ver instrucciones para aplicar sphere manualmente")
    print("3. No hacer nada")
    
    print("\n⚠️ RECOMENDACIÓN:")
    print("   Opción 1: Restaurar y luego aplicar sphere manualmente")
    print("   siguiendo las instrucciones del ADN del proyecto")

if __name__ == "__main__":
    main()
    
    print("\n\n📋 RECORDATORIO:")
    print("El ADN del proyecto está en PROJECT_DNA_IMMUTABLE.json")
    print("SIEMPRE debe respetarse esa arquitectura")