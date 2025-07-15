"""
interface_utils.py - Utilidades compartidas para la interfaz interactiva
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class InputValidator:
    """Validador de entrada de datos"""
    
    @staticmethod
    def validate_macro_name(name: str) -> bool:
        """Validar nombre de macro"""
        if not name or not name.strip():
            return False
        if len(name) > 50:
            return False
        # Evitar caracteres especiales problemáticos
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return not any(char in name for char in invalid_chars)
    
    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float) -> bool:
        """Validar que un valor esté en un rango"""
        return min_val <= value <= max_val


class AsyncInputHandler:
    """Manejador asíncrono de entrada de datos"""
    
    @staticmethod
    async def get_input(prompt: str) -> str:
        """Obtener input del usuario de forma asíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)
    
    @staticmethod
    async def get_int(prompt: str, min_val: int, max_val: int, max_attempts: int = 3) -> Optional[int]:
        """Obtener entero validado con intentos limitados"""
        for attempt in range(max_attempts):
            try:
                response = await AsyncInputHandler.get_input(prompt)
                val = int(response)
                if InputValidator.validate_range(val, min_val, max_val):
                    return val
                print(f"⚠️  Por favor, ingrese un número entre {min_val} y {max_val}")
            except ValueError:
                print("⚠️  Por favor, ingrese un número válido")
            except KeyboardInterrupt:
                print("\n⚠️  Operación cancelada")
                return None
                
            if attempt < max_attempts - 1:
                print(f"   Intentos restantes: {max_attempts - attempt - 1}")
                
        print("❌ Máximo número de intentos alcanzado")
        return None
    
    @staticmethod
    async def get_float(prompt: str, min_val: float, max_val: float, max_attempts: int = 3) -> Optional[float]:
        """Obtener float validado con intentos limitados"""
        for attempt in range(max_attempts):
            try:
                response = await AsyncInputHandler.get_input(prompt)
                val = float(response)
                if InputValidator.validate_range(val, min_val, max_val):
                    return val
                print(f"⚠️  Por favor, ingrese un número entre {min_val} y {max_val}")
            except ValueError:
                print("⚠️  Por favor, ingrese un número válido")
            except KeyboardInterrupt:
                print("\n⚠️  Operación cancelada")
                return None
                
            if attempt < max_attempts - 1:
                print(f"   Intentos restantes: {max_attempts - attempt - 1}")
                
        print("❌ Máximo número de intentos alcanzado")
        return None
    
    @staticmethod
    async def get_bool(prompt: str, default: Optional[bool] = None) -> bool:
        """Obtener booleano con valor por defecto opcional"""
        try:
            if default is not None:
                default_str = "S" if default else "N"
                prompt_with_default = f"{prompt} [{default_str}]: "
            else:
                prompt_with_default = f"{prompt} (s/n): "
                
            response = await AsyncInputHandler.get_input(prompt_with_default)
            
            # Si no hay respuesta y hay default, usar default
            if not response.strip() and default is not None:
                return default
                
            return response.lower() in ['s', 'si', 'sí', 'y', 'yes', '1', 'true']
        except KeyboardInterrupt:
            print("\n⚠️  Operación cancelada")
            return False if default is None else default


class MenuFormatter:
    """Formateador de menús y texto"""
    
    @staticmethod
    def format_title(title: str, width: int = 60) -> str:
        """Formatear título con bordes"""
        border = "=" * width
        centered_title = title.center(width)
        return f"\n{border}\n{centered_title}\n{border}"
    
    @staticmethod
    def format_subtitle(subtitle: str, width: int = 40) -> str:
        """Formatear subtítulo"""
        border = "-" * width
        return f"\n{border}\n{subtitle}\n{border}"
    
    @staticmethod
    def format_status(message: str, status: str = "info") -> str:
        """Formatear mensaje de estado con emoji"""
        status_icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️",
            "loading": "⏳",
            "question": "❓"
        }
        icon = status_icons.get(status, "•")
        return f"{icon} {message}"


class ErrorHandler:
    """Manejador de errores con contexto"""
    
    @staticmethod
    def handle_exception(e: Exception, context: str = "", user_friendly: bool = True) -> str:
        """Manejar excepción y devolver mensaje apropiado"""
        error_msg = str(e)
        
        if user_friendly:
            # Mapear errores comunes a mensajes amigables
            friendly_messages = {
                "KeyError": "No se encontró el elemento solicitado",
                "ValueError": "Valor inválido proporcionado",
                "TypeError": "Tipo de dato incorrecto",
                "AttributeError": "Operación no disponible",
                "FileNotFoundError": "Archivo no encontrado",
                "PermissionError": "Sin permisos suficientes",
                "ConnectionError": "Error de conexión",
                "TimeoutError": "Operación expiró"
            }
            
            error_type = type(e).__name__
            friendly_msg = friendly_messages.get(error_type, "Error desconocido")
            
            if context:
                return f"Error en {context}: {friendly_msg}"
            else:
                return friendly_msg
        else:
            if context:
                return f"Error en {context}: {error_msg}"
            else:
                return error_msg
    
    @staticmethod
    def log_error(e: Exception, context: str = "", level: str = "error"):
        """Registrar error en log"""
        log_methods = {
            "debug": logger.debug,
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
            "critical": logger.critical
        }
        
        log_method = log_methods.get(level, logger.error)
        
        if context:
            log_method(f"Error en {context}: {e}", exc_info=True)
        else:
            log_method(f"Error: {e}", exc_info=True)


# Funciones de conveniencia
async def safe_input(prompt: str) -> str:
    """Input seguro con manejo de excepciones"""
    try:
        return await AsyncInputHandler.get_input(prompt)
    except KeyboardInterrupt:
        print("\n⚠️  Operación cancelada")
        return ""
    except Exception as e:
        print(f"❌ Error en input: {e}")
        return ""

async def safe_int_input(prompt: str, min_val: int, max_val: int, default: Optional[int] = None) -> Optional[int]:
    """Input de entero seguro"""
    try:
        if default is not None:
            prompt = f"{prompt} [{default}]: "
            
        result = await AsyncInputHandler.get_int(prompt, min_val, max_val)
        
        if result is None and default is not None:
            return default
            
        return result
    except Exception as e:
        ErrorHandler.log_error(e, "safe_int_input")
        return default

async def safe_float_input(prompt: str, min_val: float, max_val: float, default: Optional[float] = None) -> Optional[float]:
    """Input de float seguro"""
    try:
        if default is not None:
            prompt = f"{prompt} [{default}]: "
            
        result = await AsyncInputHandler.get_float(prompt, min_val, max_val)
        
        if result is None and default is not None:
            return default
            
        return result
    except Exception as e:
        ErrorHandler.log_error(e, "safe_float_input")
        return default

async def confirm_action(message: str, default: bool = False) -> bool:
    """Confirmar acción con el usuario"""
    try:
        return await AsyncInputHandler.get_bool(f"¿{message}?", default)
    except Exception:
        return default

def format_success(message: str) -> str:
    """Formatear mensaje de éxito"""
    return MenuFormatter.format_status(message, "success")

def format_error(message: str) -> str:
    """Formatear mensaje de error"""
    return MenuFormatter.format_status(message, "error")

def format_warning(message: str) -> str:
    """Formatear mensaje de advertencia"""
    return MenuFormatter.format_status(message, "warning")

def format_info(message: str) -> str:
    """Formatear mensaje informativo"""
    return MenuFormatter.format_status(message, "info")


# Configuración del módulo
__all__ = [
    'InputValidator',
    'AsyncInputHandler', 
    'MenuFormatter',
    'ErrorHandler',
    'safe_input',
    'safe_int_input',
    'safe_float_input',
    'confirm_action',
    'format_success',
    'format_error',
    'format_warning',
    'format_info'
]