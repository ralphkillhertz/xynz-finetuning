# Changelog - 11 de Julio de 2025

## Mejoras en el Sistema de Rotación MS (Macro)

### 1. **Error Corregido**
- **Problema**: Error "name 'choice' is not defined" al seleccionar rotación manual
- **Solución**: Eliminada referencia incorrecta a variable no definida en `_create_macro_rotation_command()`

### 2. **Presets de Rotación Algorítmica**
Implementados 8 presets de movimiento predefinidos:
- 🌀 Rotación suave
- 🌊 Oleaje flotante
- 🌪️ Vórtice dinámico
- 🎭 Péndulo teatral
- 🎪 Carrusel mágico
- 🎨 Espiral artística
- 🎯 Precisión robótica
- 🌌 Órbita galáctica

### 3. **Configuración Simplificada**
Nueva opción con solo 2 parámetros:
- **Velocidad**: Control general de rapidez (0.1 - 2.0)
- **Profundidad**: Complejidad del movimiento (0 - 100%)

### 4. **Edición de Rotaciones Activas**
- Nueva opción en menú: "✏️ Editar Rotaciones Activas"
- Permite modificar velocidades de rotación sin detener el movimiento
- Muestra valores actuales y permite cambios en tiempo real

### 5. **Corrección de Aplicación Repetida**
- **Problema**: Al aplicar nueva rotación, se acumulaban los ángulos anteriores
- **Solución**: Reset automático de ángulos al configurar nuevas velocidades

### 6. **Sistema de Funciones Personalizadas** ⭐ NUEVA FUNCIONALIDAD
Implementado sistema completo para definir movimientos mediante expresiones matemáticas:

#### Características:
- **Parser seguro** de expresiones matemáticas (previene código malicioso)
- **Biblioteca de funciones** predefinidas (estrella, espiral, Lissajous, etc.)
- **Editor de expresiones** para crear movimientos personalizados
- **Variables disponibles**: t (tiempo), theta (ángulo), pi, e
- **Funciones matemáticas**: sin, cos, tan, exp, log, sqrt, abs, min, max

#### Ejemplos de uso:
```python
# Estrella de 5 puntas
X: (1 + 0.3 * cos(5 * theta)) * cos(theta)
Y: (1 + 0.3 * cos(5 * theta)) * sin(theta)

# Espiral 3D
X: (1 - t) * cos(t * 6 * pi)
Y: (1 - t) * sin(t * 6 * pi)
Z: t * 2
```

## Archivos Modificados:
1. `trajectory_hub/interface/interactive_controller.py`
   - Corrección de error en rotación manual
   - Añadidos presets y configuración simplificada
   - Nueva función de edición de rotaciones activas
   - Integración con funciones personalizadas

2. `trajectory_hub/core/enhanced_trajectory_engine.py`
   - Reset de ángulos al aplicar nuevas velocidades

3. `trajectory_hub/core/custom_motion_functions.py` (NUEVO)
   - Sistema completo de funciones personalizadas
   - Parser seguro de expresiones
   - Biblioteca de movimientos predefinidos

## Próximos Pasos Sugeridos:
1. Integrar funciones personalizadas con trayectorias (no solo rotaciones)
2. Permitir guardar/cargar funciones personalizadas del usuario
3. Crear interfaz visual para previsualizar movimientos
4. Integración con LLM para traducir descripciones naturales a funciones

## Estado del Proyecto:
- ✅ Sistema de rotación MS completamente funcional
- ✅ Funciones personalizadas implementadas y listas para uso
- ✅ Todos los errores reportados corregidos
- 📁 Backup creado: `backups/trajectory_hub_20250711_102829_rotacion_ms_mejorada_funciones_custom`