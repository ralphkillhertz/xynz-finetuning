#!/usr/bin/env python3
"""
view_progress.py - Script para ver el progreso y historial de cambios
"""
import sys
import os
sys.path.append('.')

from trajectory_hub.tools.change_logger import logger

def main():
    if len(sys.argv) < 2:
        print("Uso: python view_progress.py [report|changes|tasks|search]")
        return
    
    command = sys.argv[1]
    
    if command == "report":
        print(logger.generate_report())
    
    elif command == "changes":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        changes = logger.get_recent_changes(limit)
        print(f"\n=== Últimos {len(changes)} cambios ===")
        for change in changes:
            print(f"[{change['timestamp']}] {change['change_type'].upper()}: {change['file_path']}")
            print(f"  → {change['description']}")
            print()
    
    elif command == "tasks":
        pending = logger.get_pending_tasks()
        progress = logger.get_session_progress()
        print(f"\n=== Progreso de Tareas ===")
        print(f"Total: {progress['total']} | Completadas: {progress['completed']} | Pendientes: {progress['pending']}")
        print(f"Progreso: {progress['completion_rate']:.1f}%")
        
        if pending:
            print(f"\n=== Tareas Pendientes ({len(pending)}) ===")
            for task in pending:
                print(f"- [{task['priority'].upper()}] {task['description']}")
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Uso: python view_progress.py search <patrón_archivo>")
            return
        pattern = sys.argv[2]
        changes = logger.search_changes(file_pattern=pattern)
        print(f"\n=== Cambios en archivos con '{pattern}' ===")
        for change in changes:
            print(f"[{change['timestamp']}] {change['file_path']}: {change['description']}")
    
    else:
        print("Comando no reconocido. Use: report, changes, tasks, o search")

if __name__ == "__main__":
    main()