# === fix_create_macro_clean.py ===
# 🔧 Fix: Limpiar create_macro - eliminar duplicados y usar clase correcta
# ⚡ Impacto: CRÍTICO - Sin esto no funcionan los macros

import os
import re
from datetime import datetime

print("🔧 LIMPIANDO Y ARREGLANDO create_macro...\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Backup
import shutil
shutil.copy2(file_path, backup_path)
print(f"📦 Backup: {backup_path}")

with open(file_path, 'r') as f:
    content = f.read()

# Reemplazar create_macro con versión limpia
new_create_macro = '''    def create_macro(
        self, 
        name: str, 
        source_count: int, 
        behavior: str = "flock",
        formation: str = "circle",
        spacing: float = 2.0,
        **kwargs
    ) -> str:
        """
        Crear un macro (grupo de fuentes)
        
        Parameters
        ----------
        name : str
            Nombre del macro
        source_count : int o List[int]
            Número de fuentes o lista de IDs específicos
        behavior : str
            Tipo de comportamiento (flock, rigid, orbit, etc.)
        formation : str
            Formación inicial (circle, line, grid, spiral)
        spacing : float
            Espaciado entre fuentes
            
        Returns
        -------
        str
            ID del macro creado
        """
        # Flexibilidad para source_count
        if isinstance(source_count, list):
            # Lista de IDs específicos
            source_ids = source_count
            actual_source_count = len(source_count)
            macro_id = f"{name}_custom"
        else:
            # Crear nuevas fuentes
            actual_source_count = source_count
            macro_id = name
            
            # Crear conjunto de fuentes
            source_ids = []
            start_id = len(self.motion_states)
            
            for i in range(actual_source_count):
                sid = start_id + i
                if sid < self.max_sources:
                    self.create_source(sid, f"{name}_{i}")
                    source_ids.append(sid)
        
        # Crear el macro usando la clase Macro simple
        macro = Macro(name, source_ids)
        macro.formation = formation
        macro.behavior = behavior
        
        # Crear componente de trayectoria compartido
        from trajectory_hub.core.motion_components import MacroTrajectory
        trajectory_component = MacroTrajectory()
        trajectory_component.enabled = False  # Se activa al configurar trayectoria
        macro.trajectory_component = trajectory_component
        
        # Añadir trajectory_component a cada fuente
        for sid in source_ids:
            if sid in self.motion_states:
                self.motion_states[sid].active_components["macro_trajectory"] = trajectory_component
        
        # Aplicar formación inicial si existe el método
        if hasattr(self, '_apply_formation'):
            self._apply_formation(source_ids, formation, spacing)
        
        # Guardar el macro
        self._macros[macro_id] = macro
        
        logger.info(f"Macro '{name}' creado con {len(source_ids)} fuentes")
        
        # Crear moduladores de orientación si está habilitado
        if self.enable_modulator:
            for i, sid in enumerate(source_ids):
                try:
                    modulator = self.create_orientation_modulator(sid)
                    if modulator:
                        modulator.time_offset = i * 0.05
                except:
                    pass  # Ignorar si falla
        
        return macro_id'''

# Buscar y reemplazar create_macro
pattern = r'def create_macro\(.*?\):.*?(?=\n    def|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content.replace(match.group(0), new_create_macro)
    print("✅ create_macro reemplazado con versión limpia")
else:
    print("❌ No se encontró create_macro")

# Guardar
with open(file_path, 'w') as f:
    f.write(content)

print("\n✅ Archivo actualizado")

# Test final
print("\n🧪 Ejecutando test...")
import subprocess
result = subprocess.run(['python', 'test_macro_system_fixed.py'], 
                      capture_output=True, text=True)

# Mostrar resultados
for line in result.stdout.split('\n'):
    if any(word in line for word in ['✅', '❌', 'ÉXITO', 'TEST', 'Verificando', 'Creando', 'Frame', 'distancia', 'Macro']):
        print(line)

if result.stderr:
    print(f"\n❌ Error: {result.stderr}")
    
    # Si hay error de import, arreglarlo
    if "cannot import name 'Macro'" in result.stderr:
        print("\n🔧 Añadiendo import de Macro...")
        
        # Añadir import
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Buscar sección de imports locales
        import_pos = content.find("from .motion_components import")
        if import_pos != -1:
            # Añadir Macro a imports si no está
            line_end = content.find('\n', import_pos)
            import_line = content[import_pos:line_end]
            
            if "Macro" not in import_line:
                # Buscar dónde está definido Macro
                print("📝 Nota: Macro está definido en este mismo archivo")
                
        with open(file_path, 'w') as f:
            f.write(content)