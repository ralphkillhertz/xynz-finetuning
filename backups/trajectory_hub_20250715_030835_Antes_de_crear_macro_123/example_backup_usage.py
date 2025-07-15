#!/usr/bin/env python3
"""
Ejemplo de uso del sistema de backup automático y notificaciones
"""
from trajectory_hub.tools import (
    backup_before_changes, 
    create_safety_backup,
    notify_success, 
    notify_error,
    notify_completion
)

# Ejemplo 1: Usar decorador para backup automático
@backup_before_changes("Modificando configuración de trayectorias")
def modificar_trayectorias():
    """Función que modifica trayectorias importantes"""
    print("Modificando trayectorias...")
    # Aquí iría el código que modifica archivos
    return "Cambios aplicados"

# Ejemplo 2: Backup manual antes de operación crítica
def operacion_critica():
    """Operación que requiere backup manual"""
    try:
        # Crear backup antes de empezar
        backup_path = create_safety_backup("Antes de operación crítica")
        
        # Realizar operación
        print("Ejecutando operación crítica...")
        # ... código de la operación ...
        
        # Notificar éxito
        notify_success("Operación completada exitosamente")
        
    except Exception as e:
        # Notificar error
        notify_error(f"Error en operación: {e}")
        raise

# Ejemplo 3: Integración con el flujo de trabajo
def flujo_trabajo_completo():
    """Ejemplo de flujo de trabajo completo"""
    
    # Inicio del proceso
    print("=== Iniciando proceso de actualización ===")
    
    # Paso 1: Backup inicial
    create_safety_backup("Inicio de actualización de trayectorias")
    
    # Paso 2: Modificaciones con decorador
    resultado = modificar_trayectorias()
    print(f"Resultado: {resultado}")
    
    # Paso 3: Operación crítica
    operacion_critica()
    
    # Paso 4: Notificación final
    notify_completion("Proceso completado - Todas las actualizaciones aplicadas")

if __name__ == "__main__":
    # Ejecutar ejemplo
    flujo_trabajo_completo()