"""
Sistema de Notificaciones Sonoras para Trajectory Hub
Proporciona feedback auditivo para diferentes eventos
"""
import subprocess
import platform
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SoundNotification:
    """Sistema de notificaciones sonoras multiplataforma"""
    
    def __init__(self):
        self.system = platform.system()
        self.sound_player = self._detect_sound_player()
        self.enabled = True
        
        # Sonidos del sistema para macOS
        self.sounds = {
            'success': '/System/Library/Sounds/Glass.aiff',
            'error': '/System/Library/Sounds/Basso.aiff',
            'warning': '/System/Library/Sounds/Pop.aiff',
            'info': '/System/Library/Sounds/Tink.aiff',
            'backup': '/System/Library/Sounds/Morse.aiff',
            'complete': '/System/Library/Sounds/Hero.aiff'
        }
    
    def _detect_sound_player(self) -> Optional[str]:
        """Detectar el reproductor de sonido disponible"""
        if self.system == 'Darwin':  # macOS
            return 'afplay'
        elif self.system == 'Linux':
            # Intentar diferentes reproductores
            for player in ['aplay', 'paplay', 'play']:
                try:
                    subprocess.run(['which', player], capture_output=True, check=True)
                    return player
                except:
                    continue
        elif self.system == 'Windows':
            return 'powershell'
        return None
    
    def play(self, sound_type: str = 'info'):
        """Reproducir un sonido según el tipo de evento"""
        if not self.enabled or not self.sound_player:
            return
        
        try:
            if self.system == 'Darwin':
                sound_file = self.sounds.get(sound_type, self.sounds['info'])
                subprocess.run([self.sound_player, sound_file], 
                             capture_output=True, check=False)
            
            elif self.system == 'Linux':
                # Para Linux, usar sonidos del sistema si están disponibles
                if self.sound_player == 'paplay':
                    # PulseAudio
                    sound_map = {
                        'success': '/usr/share/sounds/freedesktop/stereo/complete.oga',
                        'error': '/usr/share/sounds/freedesktop/stereo/dialog-error.oga',
                        'warning': '/usr/share/sounds/freedesktop/stereo/dialog-warning.oga',
                        'info': '/usr/share/sounds/freedesktop/stereo/message.oga'
                    }
                    sound_file = sound_map.get(sound_type)
                    if sound_file:
                        subprocess.run([self.sound_player, sound_file], 
                                     capture_output=True, check=False)
                        
            elif self.system == 'Windows':
                # Windows PowerShell beep
                frequency_map = {
                    'success': 800,
                    'error': 300,
                    'warning': 500,
                    'info': 600
                }
                freq = frequency_map.get(sound_type, 600)
                subprocess.run(['powershell', '-c', f'[console]::beep({freq},300)'], 
                             capture_output=True, check=False)
                
        except Exception as e:
            logger.debug(f"No se pudo reproducir sonido: {e}")
    
    def disable(self):
        """Desactivar notificaciones sonoras"""
        self.enabled = False
    
    def enable(self):
        """Activar notificaciones sonoras"""
        self.enabled = True

# Instancia global
notifier = SoundNotification()

# Funciones de conveniencia
def notify_success(message: str = ""):
    """Notificación de éxito"""
    if message:
        logger.info(f"✅ {message}")
    notifier.play('success')

def notify_error(message: str = ""):
    """Notificación de error"""
    if message:
        logger.error(f"❌ {message}")
    notifier.play('error')

def notify_warning(message: str = ""):
    """Notificación de advertencia"""
    if message:
        logger.warning(f"⚠️ {message}")
    notifier.play('warning')

def notify_info(message: str = ""):
    """Notificación informativa"""
    if message:
        logger.info(f"ℹ️ {message}")
    notifier.play('info')

def notify_backup(message: str = ""):
    """Notificación de backup"""
    if message:
        logger.info(f"💾 {message}")
    notifier.play('backup')

def notify_completion(message: str = ""):
    """Notificación de tarea completada"""
    if message:
        logger.info(f"🎉 {message}")
    notifier.play('complete')

# Para que Claude Code emita un sonido al terminar tareas
def task_completed():
    """Llamar al completar una tarea en Claude Code"""
    notify_success("Tarea completada")

if __name__ == "__main__":
    # Test de sonidos
    import time
    print("Probando notificaciones sonoras...")
    
    print("Success...")
    notify_success()
    time.sleep(1)
    
    print("Error...")
    notify_error()
    time.sleep(1)
    
    print("Warning...")
    notify_warning()
    time.sleep(1)
    
    print("Info...")
    notify_info()
    time.sleep(1)
    
    print("Backup...")
    notify_backup()
    time.sleep(1)
    
    print("Complete...")
    notify_completion()