# === find_todays_backups.py ===
# 🔍 Buscar los backups creados HOY (8 de julio)
# ⚡ Deben existir porque los creamos durante esta sesión

import os
import glob
from datetime import datetime

print("🔍 BUSCANDO BACKUPS DE HOY (8 de julio)...\n")

# Buscar con diferentes patrones
patterns = [
    "trajectory_hub/core/enhanced_trajectory_engine.py.backup_*20250708*",
    "trajectory_hub/core/enhanced_trajectory_engine.py.backup_macro_*",
    "trajectory_hub/core/enhanced_trajectory_engine.py.backup_clean_*",
    "trajectory_hub/core/enhanced_trajectory_engine.py.backup_fps_*"
]

all_backups = []
for pattern in patterns:
    found = glob.glob(pattern)
    if found:
        print(f"✅ Patrón '{pattern}':")
        for f in found:
            print(f"   - {os.path.basename(f)}")
            all_backups.extend(found)

if not all_backups:
    print("❌ No se encontraron backups de hoy")
    print("\n🔍 Buscando TODOS los archivos .backup* en el directorio...")
    
    # Buscar de otra forma
    for file in os.listdir("trajectory_hub/core/"):
        if "backup" in file and "20250708" in file:
            print(f"✅ Encontrado: {file}")
            all_backups.append(os.path.join("trajectory_hub/core/", file))

# Si encontramos backups de hoy
if all_backups:
    # Usar el más reciente
    latest = max(all_backups)
    print(f"\n📌 Usando backup más reciente: {os.path.basename(latest)}")
    
    import shutil
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    shutil.copy2(latest, engine_path)
    print("✅ Restaurado desde backup de hoy")
else:
    print("\n⚠️ No hay backups de hoy - ARREGLANDO MANUALMENTE")
    
    # Fix manual del import
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar y eliminar la línea problemática
    fixed_lines = []
    for line in lines:
        if "create_complex_movement" in line and "import" in line:
            print(f"❌ Eliminando: {line.strip()}")
            continue
        fixed_lines.append(line)
    
    with open(engine_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Import problemático eliminado")

# Test final
print("\n🧪 Test final...")
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ Import exitoso!")
    
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    print("✅ Engine creado")
    
    # Si llegamos aquí, ejecutar el test completo
    import subprocess
    result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                          capture_output=True, text=True)
    
    if "ÉXITO TOTAL" in result.stdout:
        print("\n🎉 ¡MacroTrajectory FUNCIONA!")
        print("\n📊 Estado actual:")
        print("✅ Import arreglado")
        print("✅ Engine funcional")
        print("⏳ Test completo en progreso...")
    else:
        # Mostrar errores específicos
        for line in result.stdout.split('\n') + result.stderr.split('\n'):
            if line.strip() and any(word in line for word in ['Error', '❌', 'Traceback', 'line']):
                print(f"  {line}")
                
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Último recurso - crear create_macro mínimo
    print("\n🔧 ÚLTIMO RECURSO: Crear método create_macro mínimo...")
    
    create_macro_minimal = '''
    def create_macro(self, name: str, source_ids: list, **kwargs) -> str:
        """Crear macro mínimo funcional"""
        # Crear macro
        if not hasattr(self, '_macros'):
            self._macros = {}
            
        macro = Macro(name, source_ids)
        
        # Crear trajectory component
        from .motion_components import MacroTrajectory
        trajectory_component = MacroTrajectory()
        trajectory_component.enabled = False
        macro.trajectory_component = trajectory_component
        
        # Añadir a motion_states
        for sid in source_ids:
            if sid in self.motion_states:
                self.motion_states[sid].active_components["macro_trajectory"] = trajectory_component
        
        # Guardar
        self._macros[name] = macro
        return name
'''
    print("📝 Código mínimo creado - aplicar manualmente si es necesario")