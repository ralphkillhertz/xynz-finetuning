#!/usr/bin/env python3
"""
Sistema de Backups Confiable para Trajectory Hub
Diseñado para ser simple, robusto y funcional
"""

import os
import shutil
import json
import datetime
from pathlib import Path
import argparse
import sys

class BackupSystem:
    def __init__(self, backup_dir="backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.config_file = self.backup_dir / "backup_config.json"
        self.load_config()
        
    def load_config(self):
        """Cargar configuración del sistema"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "max_backups": 20,
                "exclude_patterns": [
                    "__pycache__",
                    "*.pyc",
                    ".git",
                    ".DS_Store",
                    "*.log",
                    ".pytest_cache",
                    ".env"
                ]
            }
            self.save_config()
    
    def save_config(self):
        """Guardar configuración"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def create_backup(self, description=""):
        """Crear un nuevo backup"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"trajectory_hub_{timestamp}"
        if description:
            safe_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_desc = safe_desc.replace(' ', '_')[:50]
            backup_name += f"_{safe_desc}"
        
        backup_path = self.backup_dir / backup_name
        
        print(f"🔄 Creando backup: {backup_name}")
        
        # Crear el backup
        try:
            # Copiar todo excepto los patrones excluidos
            shutil.copytree(
                ".",
                backup_path,
                ignore=shutil.ignore_patterns(*self.config["exclude_patterns"], "backups", "SAFETY_BACKUPS")
            )
            
            # Crear archivo de información
            info = {
                "timestamp": timestamp,
                "description": description,
                "date": datetime.datetime.now().isoformat(),
                "files_count": sum(1 for _ in backup_path.rglob("*") if _.is_file()),
                "size_mb": sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file()) / (1024*1024)
            }
            
            with open(backup_path / "backup_info.json", 'w') as f:
                json.dump(info, f, indent=2)
            
            print(f"✅ Backup creado exitosamente")
            print(f"📁 Ubicación: {backup_path}")
            print(f"📊 Archivos: {info['files_count']}")
            print(f"💾 Tamaño: {info['size_mb']:.2f} MB")
            
            # Limpiar backups antiguos
            self.cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            return None
    
    def list_backups(self):
        """Listar todos los backups disponibles"""
        backups = []
        
        for item in self.backup_dir.iterdir():
            if item.is_dir() and item.name.startswith("trajectory_hub_"):
                info_file = item / "backup_info.json"
                if info_file.exists():
                    with open(info_file, 'r') as f:
                        info = json.load(f)
                else:
                    # Información básica si no hay archivo info
                    info = {
                        "timestamp": item.name.split('_')[2],
                        "description": "",
                        "date": datetime.datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    }
                
                backups.append({
                    "name": item.name,
                    "path": item,
                    "info": info
                })
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda x: x["info"]["date"], reverse=True)
        
        return backups
    
    def restore_backup(self, backup_name, create_safety_backup=True):
        """Restaurar un backup específico"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Error: No se encuentra el backup '{backup_name}'")
            return False
        
        print(f"🔄 Restaurando backup: {backup_name}")
        
        # Crear backup de seguridad del estado actual
        if create_safety_backup:
            print("📦 Creando backup de seguridad del estado actual...")
            safety_backup = self.create_backup("safety_before_restore")
            if not safety_backup:
                print("⚠️  No se pudo crear backup de seguridad, pero continuando...")
        
        # Limpiar directorio actual (excepto backups y este script)
        print("🧹 Limpiando directorio actual...")
        for item in Path(".").iterdir():
            if item.name not in ["backups", "SAFETY_BACKUPS", "backup_system.py", ".git"]:
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception as e:
                    print(f"⚠️  No se pudo eliminar {item}: {e}")
        
        # Restaurar archivos
        print("📥 Copiando archivos del backup...")
        restored_count = 0
        
        for item in backup_path.iterdir():
            if item.name not in ["backup_info.json"]:
                try:
                    if item.is_dir():
                        shutil.copytree(item, Path(item.name))
                    else:
                        shutil.copy2(item, Path(item.name))
                    restored_count += 1
                except Exception as e:
                    print(f"⚠️  Error copiando {item.name}: {e}")
        
        print(f"✅ Restauración completada")
        print(f"📊 {restored_count} elementos restaurados")
        
        # Mostrar información del backup
        info_file = backup_path / "backup_info.json"
        if info_file.exists():
            with open(info_file, 'r') as f:
                info = json.load(f)
                print(f"📅 Backup del: {info.get('date', 'Desconocido')}")
                if info.get('description'):
                    print(f"📝 Descripción: {info['description']}")
        
        return True
    
    def cleanup_old_backups(self):
        """Eliminar backups antiguos según la configuración"""
        backups = self.list_backups()
        
        if len(backups) > self.config["max_backups"]:
            to_delete = backups[self.config["max_backups"]:]
            
            print(f"\n🧹 Limpiando {len(to_delete)} backups antiguos...")
            for backup in to_delete:
                try:
                    shutil.rmtree(backup["path"])
                    print(f"   ✓ Eliminado: {backup['name']}")
                except Exception as e:
                    print(f"   ✗ Error eliminando {backup['name']}: {e}")
    
    def interactive_restore(self):
        """Modo interactivo para restaurar backups"""
        backups = self.list_backups()
        
        if not backups:
            print("❌ No hay backups disponibles")
            return
        
        print("\n📚 BACKUPS DISPONIBLES:")
        print("-" * 80)
        
        for i, backup in enumerate(backups, 1):
            info = backup["info"]
            desc = info.get("description", "")
            date = info.get("date", "")
            
            if date:
                try:
                    dt = datetime.datetime.fromisoformat(date)
                    date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    date_str = date[:19]
            else:
                date_str = "Fecha desconocida"
            
            print(f"{i:2d}. {backup['name']}")
            print(f"    📅 {date_str}")
            if desc:
                print(f"    📝 {desc}")
            print()
        
        # Selección
        while True:
            try:
                choice = input("\n🔢 Seleccione el número del backup a restaurar (0 para cancelar): ")
                choice = int(choice)
                
                if choice == 0:
                    print("❌ Operación cancelada")
                    return
                
                if 1 <= choice <= len(backups):
                    selected = backups[choice - 1]
                    break
                else:
                    print("❌ Número inválido, intente de nuevo")
            except ValueError:
                print("❌ Por favor ingrese un número válido")
        
        # Confirmación
        print(f"\n⚠️  ATENCIÓN: Se va a restaurar '{selected['name']}'")
        print("Esto reemplazará todos los archivos actuales.")
        
        confirm = input("\n¿Está seguro? (escriba 'SI' para confirmar): ")
        
        if confirm.upper() == "SI":
            self.restore_backup(selected["name"])
        else:
            print("❌ Operación cancelada")


def main():
    parser = argparse.ArgumentParser(description="Sistema de Backups para Trajectory Hub")
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando: create
    create_parser = subparsers.add_parser("create", help="Crear un nuevo backup")
    create_parser.add_argument("-d", "--description", default="", help="Descripción del backup")
    
    # Comando: list
    list_parser = subparsers.add_parser("list", help="Listar backups disponibles")
    
    # Comando: restore
    restore_parser = subparsers.add_parser("restore", help="Restaurar un backup")
    restore_parser.add_argument("name", nargs="?", help="Nombre del backup a restaurar")
    
    # Comando: clean
    clean_parser = subparsers.add_parser("clean", help="Limpiar backups antiguos")
    
    # Comando: config
    config_parser = subparsers.add_parser("config", help="Configurar el sistema")
    config_parser.add_argument("--max-backups", type=int, help="Número máximo de backups")
    
    args = parser.parse_args()
    
    # Crear instancia del sistema
    backup_system = BackupSystem()
    
    # Ejecutar comando
    if args.command == "create":
        backup_system.create_backup(args.description)
        
    elif args.command == "list":
        backups = backup_system.list_backups()
        if backups:
            print("\n📚 BACKUPS DISPONIBLES:")
            print("-" * 80)
            for backup in backups:
                info = backup["info"]
                print(f"\n📁 {backup['name']}")
                print(f"   📅 {info.get('date', 'Desconocido')[:19]}")
                if info.get('description'):
                    print(f"   📝 {info['description']}")
                if 'size_mb' in info:
                    print(f"   💾 {info['size_mb']:.2f} MB")
        else:
            print("❌ No hay backups disponibles")
            
    elif args.command == "restore":
        if args.name:
            backup_system.restore_backup(args.name)
        else:
            backup_system.interactive_restore()
            
    elif args.command == "clean":
        backup_system.cleanup_old_backups()
        
    elif args.command == "config":
        if args.max_backups:
            backup_system.config["max_backups"] = args.max_backups
            backup_system.save_config()
            print(f"✅ Configuración actualizada: max_backups = {args.max_backups}")
        else:
            print("\n⚙️  CONFIGURACIÓN ACTUAL:")
            print(json.dumps(backup_system.config, indent=2))
            
    else:
        # Sin comando - mostrar ayuda
        parser.print_help()
        print("\n💡 EJEMPLOS DE USO:")
        print("  python backup_system.py create -d 'antes de cambios importantes'")
        print("  python backup_system.py list")
        print("  python backup_system.py restore")
        print("  python backup_system.py restore trajectory_hub_20250624_130425")


if __name__ == "__main__":
    main()