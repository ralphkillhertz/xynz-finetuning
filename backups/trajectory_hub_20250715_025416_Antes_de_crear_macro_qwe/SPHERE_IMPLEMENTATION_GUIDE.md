# 🌐 GUÍA PARA IMPLEMENTAR SPHERE CORRECTAMENTE

## ⚠️ IMPORTANTE
NO implementar sphere hasta que:
1. El sistema esté 100% estable
2. Se haya iniciado la refactorización del CommandProcessor
3. Se tenga una sesión dedicada solo para esto

## 📋 PASOS CORRECTOS:

### 1. Preparación
```bash
# Crear backup antes de cualquier cambio
cp trajectory_hub/core/enhanced_trajectory_engine.py \
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
