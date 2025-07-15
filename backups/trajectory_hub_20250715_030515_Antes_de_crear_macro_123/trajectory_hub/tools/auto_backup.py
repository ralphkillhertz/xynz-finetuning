"""
Sistema de Backup Automático para Trajectory Hub
Proporciona backups automáticos antes de cambios críticos
"""
import os
import sys
import functools
import datetime
from pathlib import Path
from typing import Optional, Callable
import logging

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Importar el sistema de backup existente
from backup_system import BackupSystem
from trajectory_hub.tools.notifications import notify_backup, notify_error, notify_info

logger = logging.getLogger(__name__)

class AutoBackupSystem:
    """Sistema de backup automático con hooks"""
    
    def __init__(self):
        self.backup_system = BackupSystem()
        self.enabled = True
        self.last_backup_time = None
        self.min_backup_interval = 300  # 5 minutos mínimo entre backups
        
    def should_backup(self) -> bool:
        """Determinar si se debe hacer un backup"""
        if not self.enabled:
            return False
            
        if self.last_backup_time is None:
            return True
            
        elapsed = (datetime.datetime.now() - self.last_backup_time).total_seconds()
        return elapsed >= self.min_backup_interval
    
    def create_auto_backup(self, description: str = "Auto-backup") -> Optional[Path]:
        """Crear un backup automático"""
        if not self.should_backup():
            logger.debug(f"Saltando backup (último hace {(datetime.datetime.now() - self.last_backup_time).total_seconds():.0f}s)")
            return None
            
        try:
            notify_info(f"Creando backup automático: {description}")
            backup_path = self.backup_system.create_backup(description)
            
            if backup_path:
                self.last_backup_time = datetime.datetime.now()
                notify_backup(f"Backup creado: {backup_path.name}")
                return backup_path
            else:
                notify_error("Error al crear backup")
                return None
                
        except Exception as e:
            logger.error(f"Error en backup automático: {e}")
            notify_error(f"Error en backup: {str(e)}")
            return None
    
    def backup_before_function(self, description: str = ""):
        """Decorador para crear backup antes de ejecutar una función"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Crear descripción del backup
                backup_desc = description or f"Antes de {func.__name__}"
                
                # Crear backup
                self.create_auto_backup(backup_desc)
                
                # Ejecutar función
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Instancia global
auto_backup = AutoBackupSystem()

# Decorador de conveniencia
def backup_before_changes(description: str = ""):
    """Decorador para crear backup automático antes de cambios"""
    return auto_backup.backup_before_function(description)

# Funciones de conveniencia
def create_safety_backup(description: str = "Safety backup"):
    """Crear un backup de seguridad manual"""
    return auto_backup.create_auto_backup(description)

def enable_auto_backup():
    """Habilitar backups automáticos"""
    auto_backup.enabled = True
    notify_info("Backups automáticos habilitados")

def disable_auto_backup():
    """Deshabilitar backups automáticos"""
    auto_backup.enabled = False
    notify_info("Backups automáticos deshabilitados")

# Hook para integración con el engine
def install_engine_hooks(engine):
    """Instalar hooks en el engine para backups automáticos"""
    
    # Backup antes de crear macros
    original_create_macro = engine.create_macro
    @functools.wraps(original_create_macro)
    def create_macro_with_backup(*args, **kwargs):
        if len(args) > 1:
            macro_name = args[1] if isinstance(args[1], str) else "nuevo_macro"
        else:
            macro_name = kwargs.get('name', 'nuevo_macro')
        create_safety_backup(f"Antes de crear macro {macro_name}")
        return original_create_macro(*args, **kwargs)
    engine.create_macro = create_macro_with_backup
    
    # Backup antes de cambios de trayectoria
    if hasattr(engine, 'set_macro_trajectory'):
        original_set_trajectory = engine.set_macro_trajectory
        @functools.wraps(original_set_trajectory)
        def set_trajectory_with_backup(*args, **kwargs):
            create_safety_backup("Antes de cambiar trayectoria")
            return original_set_trajectory(*args, **kwargs)
        engine.set_macro_trajectory = set_trajectory_with_backup
    
    logger.info("Hooks de backup automático instalados en el engine")

if __name__ == "__main__":
    # Test del sistema
    print("Probando sistema de backup automático...")
    
    # Test 1: Backup manual
    print("\n1. Creando backup manual...")
    path = create_safety_backup("Test manual")
    print(f"   Resultado: {path}")
    
    # Test 2: Decorador
    print("\n2. Probando decorador...")
    @backup_before_changes("Test de función decorada")
    def funcion_test():
        print("   Ejecutando función de prueba")
        return "OK"
    
    resultado = funcion_test()
    print(f"   Resultado: {resultado}")
    
    # Test 3: Control de intervalo
    print("\n3. Probando control de intervalo (debe saltar)...")
    path2 = create_safety_backup("Test intervalo")
    print(f"   Resultado: {path2}")
    
    print("\n✅ Tests completados")