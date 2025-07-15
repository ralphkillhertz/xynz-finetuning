# 🛡️ Plantilla de Edición Segura

## Para Solicitar Ediciones a Claude:

### 1. Funciones Individuales
```
ARCHIVO: [nombre_archivo.py]
FUNCIÓN: [nombre_función]
LÍNEA ACTUAL: [número]

CONTEXTO:
- [Descripción de qué hace la función]
- [Qué error está ocurriendo]
- [Qué debería hacer]

CÓDIGO ACTUAL:
```python
[pegar solo la función actual con números de línea]
```

SOLICITUD:
"Por favor, proporciona SOLO el código de reemplazo para esta función, 
manteniendo la misma indentación base (X espacios)"
```

### 2. Nuevas Funciones
```
ARCHIVO: [nombre_archivo.py]
INSERTAR DESPUÉS DE: [nombre_función_anterior] (línea X)

NECESITO:
- Función que [descripción]
- Parámetros: [lista]
- Retorna: [tipo]
- Indentación base: [X espacios]

EJEMPLO DE USO:
```python
[cómo se usará la función]
```
```

### 3. Imports y Dependencias
```
ARCHIVO: [nombre_archivo.py]
SECCIÓN DE IMPORTS ACTUAL (líneas 1-20):
```python
[pegar imports actuales]
```

NECESITO AGREGAR:
- [nuevo import necesario]
- Razón: [por qué lo necesitamos]
```

## Verificación Post-Edición:

1. **Validar Sintaxis**
   ```bash
   python validate_and_fix.py trajectory_hub/ruta/archivo.py
   ```

2. **Ver Diferencias**
   ```bash
   git diff trajectory_hub/ruta/archivo.py
   ```

3. **Test Rápido**
   ```bash
   python -m trajectory_hub.interface.interactive_controller
   ```

## Reglas de Oro:

1. ✅ **Una función a la vez**
2. ✅ **Verificar después de cada cambio**
3. ✅ **Mantener backups numerados**
4. ❌ **No editar múltiples archivos simultáneamente**
5. ❌ **No hacer cambios estructurales grandes de una vez**

## En Caso de Error:

1. **Syntax Error**
   ```bash
   # Intentar auto-fix
   python validate_and_fix.py archivo.py
   
   # Si no funciona, restaurar último backup
   python safe_edit_system.py --restore archivo.py
   ```

2. **Import Error**
   ```bash
   # Verificar qué existe en el módulo
   python -c "import trajectory_hub.core.motion_components; print(dir(trajectory_hub.core.motion_components))"
   ```

3. **Indentation Error**
   ```bash
   # Auto-fix de indentación
   python validate_and_fix.py archivo.py --fix-indent
   ```