#!/usr/bin/env python3
"""
🔄 Restaurar versión limpia funcional
⚡ Volver a estado estable sin sphere
"""

import os
import shutil
from datetime import datetime

def restore_clean_state():
    """Restaura el sistema a un estado funcional conocido"""
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # 1. Buscar backups disponibles
    print("🔍 Buscando backups disponibles...")
    backups = []
    
    directory = os.path.dirname(engine_path)
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.startswith("enhanced_trajectory_engine.py.backup"):
                backups.append(os.path.join(directory, file))
    
    if backups:
        print(f"\n📦 Backups encontrados:")
        for i, backup in enumerate(sorted(backups)):
            print(f"  {i+1}. {os.path.basename(backup)}")
        
        # Usar el backup de macro_fix si existe
        macro_fix_backup = None
        for backup in backups:
            if "macro_fix" in backup:
                macro_fix_backup = backup
                break
        
        if macro_fix_backup:
            print(f"\n✅ Usando backup macro_fix: {os.path.basename(macro_fix_backup)}")
            
            # Hacer backup del estado actual roto
            broken_backup = f"{engine_path}.backup_broken_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(engine_path, broken_backup)
            print(f"📦 Estado roto guardado en: {os.path.basename(broken_backup)}")
            
            # Restaurar
            shutil.copy2(macro_fix_backup, engine_path)
            print("✅ Restaurado a versión funcional")
            
            return True
        else:
            print("⚠️  No se encontró backup macro_fix")
            if backups:
                latest = sorted(backups)[-1]
                print(f"\n🔄 Usando backup más reciente: {os.path.basename(latest)}")
                shutil.copy2(latest, engine_path)
                return True
    
    print("❌ No se encontraron backups")
    return False

def create_sphere_implementation_guide():
    """Crea guía para implementar sphere correctamente más tarde"""
    
    guide = """# 🌐 GUÍA PARA IMPLEMENTAR SPHERE CORRECTAMENTE

## ⚠️ IMPORTANTE
NO implementar sphere hasta que:
1. El sistema esté 100% estable
2. Se haya iniciado la refactorización del CommandProcessor
3. Se tenga una sesión dedicada solo para esto

## 📋 PASOS CORRECTOS:

### 1. Preparación
```bash
# Crear backup antes de cualquier cambio
cp trajectory_hub/core/enhanced_trajectory_engine.py \\
   trajectory_hub/core/enhanced_trajectory_engine.py.backup_before_sphere
```

### 2. Verificar FormationManager
```python
# test_sphere_formation.py
from trajectory_hub.control.managers.formation_manager import FormationManager

fm = FormationManager()
positions = fm.calculate_formation("sphere", 8)
print(f"Sphere test: {len(positions)} positions")
for i, pos in enumerate(positions[:3]):
    print(f"  {i}: {pos}")
```

### 3. Implementación CUIDADOSA en Engine

**LOCALIZAR EXACTAMENTE** dónde añadir sphere:
- Debe ir DESPUÉS de spiral
- ANTES del else final
- Con la MISMA indentación que otros elif

```python
# En create_macro(), después del bloque spiral:
elif formation == "sphere":
    # Import al inicio del archivo si no está
    from trajectory_hub.control.managers.formation_manager import FormationManager
    
    # Usar FormationManager
    if not hasattr(self, '_fm'):
        self._fm = FormationManager()
    
    positions = self._fm.calculate_formation("sphere", len(sources))
    
    # Aplicar posiciones como en otras formaciones
    for i, pos in enumerate(positions):
        if i < len(sources):
            sources[i]['x'] = pos[0]
            sources[i]['y'] = pos[1]
            sources[i]['z'] = pos[2]
```

### 4. Verificación
1. Python syntax check: `python -m py_compile trajectory_hub/core/enhanced_trajectory_engine.py`
2. Import test: `python -c "from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine"`
3. Run system: `python -m trajectory_hub.interface.interactive_controller`

## 🎯 CUANDO IMPLEMENTAR
Solo cuando:
- [ ] Sistema funciona perfectamente sin sphere
- [ ] Se completó sesión de trabajo actual
- [ ] Se tiene tiempo dedicado (30-60 min)
- [ ] Se puede hacer con calma y verificando cada paso
"""
    
    with open("SPHERE_IMPLEMENTATION_GUIDE.md", 'w') as f:
        f.write(guide)
    
    print("\n📄 Creada guía: SPHERE_IMPLEMENTATION_GUIDE.md")

if __name__ == "__main__":
    print("🔄 RESTAURACIÓN A VERSIÓN ESTABLE")
    print("=" * 50)
    
    if restore_clean_state():
        create_sphere_implementation_guide()
        
        print("\n✅ SISTEMA RESTAURADO")
        print("\n🎯 Próximos pasos:")
        print("1. Verificar que el sistema funcione:")
        print("   python -m trajectory_hub.interface.interactive_controller")
        print("\n2. Continuar con refactorización CommandProcessor")
        print("\n3. Implementar sphere SOLO cuando todo esté estable")
        print("   (ver SPHERE_IMPLEMENTATION_GUIDE.md)")
    else:
        print("\n❌ No se pudo restaurar")
        print("Necesitamos el archivo de backup o una versión funcional")