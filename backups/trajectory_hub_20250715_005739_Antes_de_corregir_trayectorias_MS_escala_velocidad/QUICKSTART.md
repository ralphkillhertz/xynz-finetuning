# 🚀 TRAJECTORY HUB - GUÍA RÁPIDA

## 1. Verificar Estado
```bash
python check_system_status.py
```

## 2. Arreglar Errores Comunes
```bash
# Si hay errores de import:
python fix_imports_definitively.py

# Si TrajectoryMovementMode no está definido:
python fix_trajectory_movement_mode.py
```

## 3. Ejecutar Sistema
```bash
python -m trajectory_hub.interface.interactive_controller
```

## 4. Crear un Macro
1. Seleccionar: `1` (Macro Management)
2. Seleccionar: `1` (Create Macro)
3. Nombre: `test`
4. Sources: `8`
5. Formation: `1` (circle)

## 5. Verificar OSC
```bash
# En otra terminal:
python -m trajectory_hub.utils.osc_debug
```

## ⚠️ Si Algo Falla
1. Revisar `PROJECT_STATE_CURRENT.json`
2. Ejecutar `python restore_clean_version.py`
3. Consultar `README.md` sección "Solución de Problemas"
