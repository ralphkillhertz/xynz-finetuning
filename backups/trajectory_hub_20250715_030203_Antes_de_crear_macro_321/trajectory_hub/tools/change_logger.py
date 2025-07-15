"""
change_logger.py - Sistema de logging de cambios y tareas para Claude Code
Mantiene un historial detallado de todas las modificaciones y tareas ejecutadas
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading

class ChangeLogger:
    """Registra cambios, tareas y progreso del proyecto"""
    
    def __init__(self, log_dir: str = ".claude"):
        self.log_dir = log_dir
        self.changes_file = os.path.join(log_dir, "changes_history.json")
        self.tasks_file = os.path.join(log_dir, "tasks_history.json")
        self.session_file = os.path.join(log_dir, "current_session.json")
        self.lock = threading.Lock()
        
        # Crear directorio si no existe
        os.makedirs(log_dir, exist_ok=True)
        
        # Inicializar sesión actual
        self._init_session()
    
    def _init_session(self):
        """Inicializa nueva sesión"""
        session_data = {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "changes": [],
            "tasks": [],
            "status": "active"
        }
        self._save_json(self.session_file, session_data)
    
    def log_change(self, 
                   file_path: str,
                   change_type: str,
                   description: str,
                   old_content: Optional[str] = None,
                   new_content: Optional[str] = None,
                   context: Optional[Dict] = None):
        """
        Registra un cambio en el código
        
        Args:
            file_path: Ruta del archivo modificado
            change_type: Tipo de cambio (edit, create, delete, etc.)
            description: Descripción del cambio
            old_content: Contenido anterior (opcional)
            new_content: Contenido nuevo (opcional)
            context: Contexto adicional (líneas, razón, etc.)
        """
        with self.lock:
            change_entry = {
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path,
                "change_type": change_type,
                "description": description,
                "context": context or {}
            }
            
            # Añadir a historial general
            self._append_to_history(self.changes_file, change_entry)
            
            # Añadir a sesión actual
            self._append_to_session("changes", change_entry)
    
    def log_task(self,
                 task_id: str,
                 task_description: str,
                 status: str,
                 priority: str = "medium",
                 context: Optional[Dict] = None):
        """
        Registra una tarea del todo list
        
        Args:
            task_id: ID único de la tarea
            task_description: Descripción de la tarea
            status: Estado (pending, in_progress, completed)
            priority: Prioridad (high, medium, low)
            context: Contexto adicional
        """
        with self.lock:
            task_entry = {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "description": task_description,
                "status": status,
                "priority": priority,
                "context": context or {}
            }
            
            # Añadir a historial general
            self._append_to_history(self.tasks_file, task_entry)
            
            # Añadir a sesión actual
            self._append_to_session("tasks", task_entry)
    
    def log_session_summary(self, summary: str, achievements: List[str]):
        """Registra resumen de la sesión"""
        with self.lock:
            session_data = self._load_json(self.session_file)
            session_data.update({
                "end_time": datetime.now().isoformat(),
                "summary": summary,
                "achievements": achievements,
                "status": "completed"
            })
            self._save_json(self.session_file, session_data)
    
    def get_recent_changes(self, limit: int = 10) -> List[Dict]:
        """Obtiene los cambios más recientes"""
        changes = self._load_json(self.changes_file, default=[])
        return changes[-limit:] if changes else []
    
    def get_pending_tasks(self) -> List[Dict]:
        """Obtiene tareas pendientes de la sesión actual"""
        session = self._load_json(self.session_file, default={})
        tasks = session.get("tasks", [])
        return [t for t in tasks if t.get("status") == "pending"]
    
    def get_session_progress(self) -> Dict:
        """Obtiene progreso de la sesión actual"""
        session = self._load_json(self.session_file, default={})
        tasks = session.get("tasks", [])
        
        total = len(tasks)
        completed = len([t for t in tasks if t.get("status") == "completed"])
        in_progress = len([t for t in tasks if t.get("status") == "in_progress"])
        pending = len([t for t in tasks if t.get("status") == "pending"])
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }
    
    def search_changes(self, 
                      file_pattern: Optional[str] = None,
                      change_type: Optional[str] = None,
                      days_back: int = 7) -> List[Dict]:
        """Busca cambios con filtros"""
        changes = self._load_json(self.changes_file, default=[])
        
        # Filtrar por fecha
        cutoff_date = datetime.now().timestamp() - (days_back * 24 * 3600)
        filtered = []
        
        for change in changes:
            change_time = datetime.fromisoformat(change["timestamp"]).timestamp()
            if change_time < cutoff_date:
                continue
                
            if file_pattern and file_pattern not in change.get("file_path", ""):
                continue
                
            if change_type and change.get("change_type") != change_type:
                continue
                
            filtered.append(change)
        
        return filtered
    
    def generate_report(self) -> str:
        """Genera reporte de la sesión actual"""
        session = self._load_json(self.session_file, default={})
        progress = self.get_session_progress()
        recent_changes = self.get_recent_changes(5)
        
        report = f"""
# Reporte de Sesión Claude Code
**Sesión ID:** {session.get('session_id', 'N/A')}
**Inicio:** {session.get('start_time', 'N/A')}

## Progreso de Tareas
- **Total:** {progress['total']}
- **Completadas:** {progress['completed']} ({progress['completion_rate']:.1f}%)
- **En progreso:** {progress['in_progress']}
- **Pendientes:** {progress['pending']}

## Cambios Recientes
"""
        
        for change in recent_changes[-5:]:
            report += f"- **{change['change_type']}** en `{change['file_path']}`: {change['description']}\n"
        
        return report
    
    def _append_to_history(self, file_path: str, entry: Dict):
        """Añade entrada al historial"""
        history = self._load_json(file_path, default=[])
        history.append(entry)
        
        # Mantener solo últimas 1000 entradas
        if len(history) > 1000:
            history = history[-1000:]
        
        self._save_json(file_path, history)
    
    def _append_to_session(self, key: str, entry: Dict):
        """Añade entrada a la sesión actual"""
        session = self._load_json(self.session_file, default={})
        if key not in session:
            session[key] = []
        session[key].append(entry)
        self._save_json(self.session_file, session)
    
    def _load_json(self, file_path: str, default: Any = None) -> Any:
        """Carga archivo JSON con manejo de errores"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error cargando {file_path}: {e}")
        
        return default if default is not None else {}
    
    def _save_json(self, file_path: str, data: Any):
        """Guarda archivo JSON con manejo de errores"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error guardando {file_path}: {e}")


# Instancia global para uso fácil
logger = ChangeLogger()

# Funciones de conveniencia
def log_edit(file_path: str, description: str, lines_changed: Optional[List[int]] = None):
    """Registra una edición de archivo"""
    context = {"lines_changed": lines_changed} if lines_changed else {}
    logger.log_change(file_path, "edit", description, context=context)

def log_create(file_path: str, description: str):
    """Registra creación de archivo"""
    logger.log_change(file_path, "create", description)

def log_task_update(task_id: str, description: str, status: str, priority: str = "medium"):
    """Registra actualización de tarea"""
    logger.log_task(task_id, description, status, priority)

def get_session_report() -> str:
    """Obtiene reporte de la sesión actual"""
    return logger.generate_report()