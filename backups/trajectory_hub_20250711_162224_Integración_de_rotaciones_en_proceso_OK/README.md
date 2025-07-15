# 🚀 Trajectory Hub - Sistema de Control de Trayectorias Espaciales

## 📋 Estado Actual: v0.87 (Julio 2025)

### ⚡ Descripción
Sistema de control en tiempo real para trayectorias espaciales 3D con comunicación OSC hacia Spat Revolution.

### 🎯 Características Actuales

#### ✅ Funcionales
- **Formaciones 2D**: circle, line, grid, spiral, random
- **Formaciones 3D**: ⚠️ sphere (pendiente de implementación estable)
- **Control OSC**: Comunicación completa con Spat
- **Macros**: Sistema de gestión de configuraciones
- **Deltas**: Sistema de cambios incrementales
- **Interface**: CLI interactivo funcional

#### 🚧 En Desarrollo
- CommandProcessor (arquitectura mejorada)
- MCP Server (Model Context Protocol)
- Gesture Control
- Timeline Engine
- Modulation System avanzado

### 📁 Estructura del Proyecto

```
trajectory_hub/
├── core/                      # Motor principal
│   ├── enhanced_trajectory_engine.py  # Engine principal
│   ├── spat_osc_bridge.py           # Comunicación OSC
│   └── motion_components.py          # Componentes de movimiento
├── interface/                 # Interfaces de usuario
│   ├── interactive_controller.py     # CLI interactivo
│   └── cli_interface.py             # CLI básico
├── control/                   # Control y gestión
│   ├── managers/
│   │   └── formation_manager.py     # Cálculo de formaciones
│   └── processors/
│       └── command_processor.py     # Procesador de comandos
├── utils/                     # Utilidades
│   └── osc_debug.py                 # Debug OSC
├── mcp/                       # Model Context Protocol
├── ai/                        # IA y procesamiento
└── gestures/                  # Control por gestos
```

### 🔧 Instalación

```bash
# 1. Clonar repositorio
git clone [repo-url]
cd trajectory_hub

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

### 🚀 Uso Básico

```bash
# Ejecutar sistema principal
python -m trajectory_hub.interface.interactive_controller

# Debug OSC
python -m trajectory_hub.utils.osc_debug

# Test formaciones
python test_formations.py
```

### 📊 Arquitectura Actual vs Objetivo

#### Estado Actual (Monolítico)
- CLI → Engine (directo) ❌
- Engine calcula formaciones ❌
- Interactive Controller: 122 métodos ❌

#### Estado Objetivo (Por Capas)
- UI → CommandProcessor → FormationManager → Engine ✅
- Separación estricta de responsabilidades ✅
- Interactive Controller: 25 métodos máx ✅

### ⚠️ Problemas Conocidos

1. **Import Errors**: Algunos imports pueden faltar (TrajectoryMovementMode, etc)
2. **Sphere Formation**: No implementada establemente
3. **Arquitectura**: Violaciones del principio de responsabilidad única
4. **Controller Monolítico**: Demasiadas responsabilidades en un solo archivo

### 🛣️ Roadmap

#### Fase 1: Estabilización (Actual)
- [ ] Resolver todos los errores de import
- [ ] Documentación completa
- [ ] Tests básicos funcionando

#### Fase 2: Sphere Implementation
- [ ] Implementar sphere correctamente
- [ ] Verificar comunicación OSC 3D
- [ ] Tests de formaciones 3D

#### Fase 3: Refactorización CommandProcessor
- [ ] Implementar SemanticCommand
- [ ] Conectar UI → CommandProcessor → Engine
- [ ] Reducir acoplamiento

#### Fase 4: Nuevas Interfaces
- [ ] MCP Server completo
- [ ] Gesture Handler
- [ ] Timeline Engine

### 🐛 Solución de Problemas

#### Error: "cannot import name 'X'"
```bash
# Verificar qué existe en el módulo
python -c "from trajectory_hub.core import motion_components; print(dir(motion_components))"
```

#### Error: "TrajectoryMovementMode not defined"
```bash
# Ejecutar fix
python fix_trajectory_movement_mode.py
```

#### Sistema no arranca
```bash
# Verificar imports
python check_imports.py

# Restaurar versión estable
python restore_clean_version.py
```

### 📝 Contribuir

1. Siempre hacer backup antes de cambios mayores
2. Seguir arquitectura objetivo (ver PROJECT_DNA_IMMUTABLE.json)
3. Documentar todos los cambios
4. Probar en entorno aislado primero

### 📞 Soporte

- Documentación técnica: `/docs`
- Estado del proyecto: `PROJECT_STATE_*.json`
- Guías específicas: `*_GUIDE.md`

---
Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}
