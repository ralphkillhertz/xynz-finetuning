#!/usr/bin/env python3
"""
reorganize_project.py - Script para reorganizar y corregir el proyecto
"""
import os
import shutil
import sys
from pathlib import Path

def create_directory_structure():
    """Crear la estructura de directorios necesaria"""
    print("🏗️  Creando estructura de directorios...")
    
    directories = [
        "trajectory_hub/interface",
        "trajectory_hub/presets", 
        "trajectory_hub/demos",
        "trajectory_hub/core",
        "trajectory_hub/tools"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")
        
        # Crear __init__.py si no existe
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Módulo del sistema de trayectorias"""\n')

def create_init_files():
    """Crear archivos __init__.py con imports apropiados"""
    print("\n📝 Creando archivos __init__.py...")
    
    # trajectory_hub/__init__.py principal
    main_init = Path("trajectory_hub/__init__.py")
    main_init_content = '''"""
Trajectory Hub v2.0 - Sistema de Trayectorias 3D Inteligentes
"""

from .core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from .core.spat_osc_bridge import SpatOSCBridge, OSCTarget
from .core.motion_components import TrajectoryMovementMode, TrajectoryDisplacementMode
from .core.trajectory_deformers import CompositeDeformer, BlendMode

__version__ = "2.0.0"
__author__ = "Ralph Killhertz (XYNZ)"
__email__ = "ralph@xynz.org"

__all__ = [
    "EnhancedTrajectoryEngine",
    "SpatOSCBridge", 
    "OSCTarget",
    "TrajectoryMovementMode",
    "TrajectoryDisplacementMode", 
    "CompositeDeformer",
    "BlendMode"
]
'''
    main_init.write_text(main_init_content)
    print("   ✓ trajectory_hub/__init__.py")
    
    # trajectory_hub/interface/__init__.py
    interface_init = Path("trajectory_hub/interface/__init__.py")
    interface_init_content = '''"""
Interfaces de usuario para el sistema
"""

from .interactive_controller import InteractiveController
from .interface_utils import (
    AsyncInputHandler, MenuFormatter, ErrorHandler, 
    safe_input, safe_int_input, safe_float_input, confirm_action
)

__all__ = [
    "InteractiveController",
    "AsyncInputHandler", 
    "MenuFormatter",
    "ErrorHandler",
    "safe_input",
    "safe_int_input", 
    "safe_float_input",
    "confirm_action"
]
'''
    interface_init.write_text(interface_init_content)
    print("   ✓ trajectory_hub/interface/__init__.py")
    
    # trajectory_hub/presets/__init__.py
    presets_init = Path("trajectory_hub/presets/__init__.py")
    presets_init_content = '''"""
Presets y configuraciones artísticas
"""

from .artistic_presets import (
    ARTISTIC_PRESETS, TRAJECTORY_FUNCTIONS, 
    TEMPORAL_COMPOSITIONS, STYLE_CONFIGS,
    get_available_presets, validate_preset
)

__all__ = [
    "ARTISTIC_PRESETS",
    "TRAJECTORY_FUNCTIONS",
    "TEMPORAL_COMPOSITIONS", 
    "STYLE_CONFIGS",
    "get_available_presets",
    "validate_preset"
]
'''
    presets_init.write_text(presets_init_content)
    print("   ✓ trajectory_hub/presets/__init__.py")

def copy_and_fix_files():
    """Copiar archivos existentes a las nuevas ubicaciones"""
    print("\n📁 Reorganizando archivos...")
    
    # Mapeo de archivos origen -> destino
    file_moves = {
        # Archivos que ya existen (si están en ubicaciones incorrectas)
        "interactive_control.py": "trajectory_hub/interface/interactive_controller.py",
        "artistic_presets.py": "trajectory_hub/presets/artistic_presets.py",
        
        # Archivos core (si no están en core/)
        "enhanced_trajectory_engine.py": "trajectory_hub/core/enhanced_trajectory_engine.py",
        "spat_osc_bridge.py": "trajectory_hub/core/spat_osc_bridge.py",
        "motion_components.py": "trajectory_hub/core/motion_components.py",
        "trajectory_deformers.py": "trajectory_hub/core/trajectory_deformers.py",
        "macro_behaviors.py": "trajectory_hub/core/macro_behaviors.py",
        "distance_controller.py": "trajectory_hub/core/distance_controller.py",
        
        # Demos
        "demo_enhanced_system.py": "trajectory_hub/demos/demo_enhanced_system.py",
        "comprehensive_test.py": "trajectory_hub/demos/comprehensive_test.py",
        
        # Tools
        "update_imports.py": "trajectory_hub/tools/update_imports.py",
        "scale_adjuster.py": "trajectory_hub/tools/scale_adjuster.py"
    }
    
    for source, dest in file_moves.items():
        source_path = Path(source)
        dest_path = Path(dest)
        
        # Buscar archivo en varias ubicaciones posibles
        possible_locations = [
            source_path,
            Path("trajectory_hub") / source,
            Path("trajectory_hub/demos") / source,
            Path("trajectory_hub/core") / source,
            Path(".") / source
        ]
        
        source_found = None
        for location in possible_locations:
            if location.exists():
                source_found = location
                break
                
        if source_found:
            # Crear directorio de destino si no existe
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                if source_found != dest_path:
                    shutil.copy2(source_found, dest_path)
                    print(f"   ✓ {source_found} → {dest_path}")
                else:
                    print(f"   = {dest_path} (ya en ubicación correcta)")
            except Exception as e:
                print(f"   ✗ Error copiando {source_found}: {e}")
        else:
            print(f"   ? {source} no encontrado")

def update_imports_in_file(file_path: Path, import_mappings: dict):
    """Actualizar imports en un archivo específico"""
    if not file_path.exists():
        return False
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Aplicar cada mapeo
        for old_import, new_import in import_mappings.items():
            content = content.replace(old_import, new_import)
            
        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"   ✗ Error actualizando {file_path}: {e}")
        
    return False

def fix_imports():
    """Corregir todos los imports del proyecto"""
    print("\n🔧 Corrigiendo imports...")
    
    # Mapeo de imports antiguos a nuevos
    import_mappings = {
        # Imports desde demos/
        'from trajectory_hub.presets.artistic_presets import': 'from trajectory_hub.presets.artistic_presets import',
        'from trajectory_hub.presets import artistic_presets': 'from trajectory_hub.presets from trajectory_hub.presets import artistic_presets',
        
        # Imports desde trajectory_hub.demos (para compatibilidad)
        'from trajectory_hub.presets.artistic_presets import': 'from trajectory_hub.presets.artistic_presets import',
        
        # Core modules 
        'from trajectory_hub.core.enhanced_trajectory_engine import': 'from trajectory_hub.core.enhanced_trajectory_engine import',
        'from trajectory_hub.core.spat_osc_bridge import': 'from trajectory_hub.core.spat_osc_bridge import',
        'from trajectory_hub.core.motion_components import': 'from trajectory_hub.core.motion_components import',
        'from trajectory_hub.core.trajectory_deformers import': 'from trajectory_hub.core.trajectory_deformers import',
        'from trajectory_hub.core.macro_behaviors import': 'from trajectory_hub.core.macro_behaviors import',
        'from trajectory_hub.core.distance_controller import': 'from trajectory_hub.core.distance_controller import',
        
        # Imports directos (sin from)
        'from trajectory_hub.core import enhanced_trajectory_engine': 'from trajectory_hub.core from trajectory_hub.core import enhanced_trajectory_engine',
        'from trajectory_hub.core import spat_osc_bridge': 'from trajectory_hub.core from trajectory_hub.core import spat_osc_bridge',
        'from trajectory_hub.core import motion_components': 'from trajectory_hub.core from trajectory_hub.core import motion_components',
        'from trajectory_hub.core import trajectory_deformers': 'from trajectory_hub.core from trajectory_hub.core import trajectory_deformers',
        
        # Imports desde trajectory_hub (simplificar)
        'from trajectory_hub import EnhancedTrajectoryEngine, SpatOSCBridge, OSCTarget': 'from trajectory_hub import EnhancedTrajectoryEngine, SpatOSCBridge, OSCTarget',
        'from trajectory_hub.core import': 'from trajectory_hub.core import'
    }
    
    # Archivos a actualizar
    files_to_update = []
    
    # Buscar todos los archivos Python
    for root in ["trajectory_hub", "."]:
        root_path = Path(root)
        if root_path.exists():
            for py_file in root_path.rglob("*.py"):
                files_to_update.append(py_file)
    
    updated_count = 0
    for file_path in files_to_update:
        if update_imports_in_file(file_path, import_mappings):
            print(f"   ✓ {file_path}")
            updated_count += 1
            
    print(f"\n   Total archivos actualizados: {updated_count}")

def create_main_entry_point():
    """Crear punto de entrada principal"""
    print("\n🚀 Creando punto de entrada principal...")
    
    main_py_content = '''#!/usr/bin/env python3
"""
main.py - Punto de entrada principal para Trajectory Hub
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Añadir el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from trajectory_hub.interface.interactive_controller import InteractiveController
from trajectory_hub.demos.demo_enhanced_system import EnhancedDemo


async def run_interactive():
    """Ejecutar modo interactivo"""
    controller = InteractiveController()
    await controller.start()

async def run_demo():
    """Ejecutar demo"""
    demo = EnhancedDemo()
    await demo.run_all_demos()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Trajectory Hub v2.0 - Sistema de Trayectorias 3D",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --interactive          # Modo interactivo completo
  python main.py --demo                 # Ejecutar demos
  python main.py --interactive --debug  # Con debug habilitado
        """
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Ejecutar en modo interactivo"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true", 
        help="Ejecutar demos automáticos"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Habilitar modo debug"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Nivel de logging"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    log_level = getattr(logging, args.log_level)
    if args.debug:
        log_level = logging.DEBUG
        
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Información de bienvenida
    print("\\n" + "="*60)
    print("TRAJECTORY HUB v2.0")
    print("Sistema de Trayectorias 3D Inteligentes para Spat Revolution")
    print("="*60)
    print("Ralph Killhertz (XYNZ) - ralph@xynz.org")
    
    # Ejecutar modo seleccionado
    try:
        if args.interactive:
            print("\\n🎮 Iniciando modo interactivo...")
            asyncio.run(run_interactive())
        elif args.demo:
            print("\\n🎯 Ejecutando demos...")
            asyncio.run(run_demo())
        else:
            # Sin argumentos, mostrar ayuda y preguntar qué hacer
            parser.print_help()
            print("\\n¿Qué deseas hacer?")
            print("1. Modo interactivo")
            print("2. Ejecutar demos")
            print("3. Salir")
            
            try:
                choice = input("\\nSelección (1-3): ").strip()
                if choice == "1":
                    asyncio.run(run_interactive())
                elif choice == "2":
                    asyncio.run(run_demo())
                else:
                    print("\\n👋 ¡Hasta luego!")
            except KeyboardInterrupt:
                print("\\n\\n⚠️ Operación cancelada")
                
    except KeyboardInterrupt:
        print("\\n\\n⚠️ Programa interrumpido por usuario")
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    main_file = Path("main.py")
    main_file.write_text(main_py_content)
    print("   ✓ main.py creado")

def create_requirements_file():
    """Crear archivo requirements.txt actualizado"""
    print("\n📦 Creando requirements.txt...")
    
    requirements_content = '''# Trajectory Hub v2.0 - Requirements
# Core dependencies
numpy>=1.21.0
scipy>=1.7.0

# OSC Communication
python-osc>=1.8.0

# Optional performance enhancements
numba>=0.56.0  # JIT compilation for performance

# Development dependencies (install with: pip install -e ".[dev]")
# pytest>=7.0.0
# black>=22.0.0
# mypy>=0.950
# flake8>=4.0.0

# Optional ML dependencies (install with: pip install -e ".[ml]")
# scikit-learn>=1.0.0
# tensorflow>=2.8.0

# Optional visualization (install with: pip install -e ".[viz]")
# matplotlib>=3.5.0
# plotly>=5.0.0
'''
    
    req_file = Path("requirements.txt")
    req_file.write_text(requirements_content)
    print("   ✓ requirements.txt creado")

def create_setup_py():
    """Crear setup.py para instalación"""
    print("\n⚙️ Creando setup.py...")
    
    setup_content = '''"""
Setup.py para Trajectory Hub v2.0
"""
from setuptools import setup, find_packages
from pathlib import Path

# Leer README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Leer requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines() 
        if line.strip() and not line.startswith("#")
    ]
else:
    requirements = ["numpy>=1.21.0", "scipy>=1.7.0", "python-osc>=1.8.0"]

setup(
    name="trajectory-hub",
    version="2.0.0",
    description="Sistema de Trayectorias 3D Inteligentes para Spat Revolution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ralph Killhertz",
    author_email="ralph@xynz.org",
    url="https://github.com/xynz/trajectory-hub",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0", 
            "mypy>=0.950",
            "flake8>=4.0.0"
        ],
        "numba": ["numba>=0.56.0"],
        "ml": ["scikit-learn>=1.0.0", "tensorflow>=2.8.0"],
        "viz": ["matplotlib>=3.5.0", "plotly>=5.0.0"]
    },
    entry_points={
        "console_scripts": [
            "trajectory-hub=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)
'''
    
    setup_file = Path("setup.py")
    setup_file.write_text(setup_content)
    print("   ✓ setup.py creado")

def create_gitignore():
    """Crear .gitignore apropiado"""
    print("\n📋 Creando .gitignore...")
    
    gitignore_content = '''# Trajectory Hub .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Cache
.cache/
.pytest_cache/

# Coverage
.coverage
htmlcov/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Jupyter
.ipynb_checkpoints

# Environment variables
.env
.env.local

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Audio files (large)
*.wav
*.aiff
*.flac
*.mp3

# Project specific
config/local_*.json
presets/custom_*.py
outputs/
recordings/
'''
    
    gitignore_file = Path(".gitignore")
    gitignore_file.write_text(gitignore_content)
    print("   ✓ .gitignore creado")

def validate_structure():
    """Validar que la estructura final es correcta"""
    print("\n✅ Validando estructura final...")
    
    expected_files = [
        "trajectory_hub/__init__.py",
        "trajectory_hub/interface/__init__.py",
        "trajectory_hub/interface/interactive_controller.py",
        "trajectory_hub/presets/__init__.py", 
        "trajectory_hub/presets/artistic_presets.py",
        "trajectory_hub/core/__init__.py",
        "trajectory_hub/demos/__init__.py",
        "main.py",
        "requirements.txt",
        "setup.py",
        ".gitignore"
    ]
    
    missing_files = []
    for file_path in expected_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"   ✓ {file_path}")
            
    if missing_files:
        print("\\n⚠️ Archivos faltantes:")
        for file_path in missing_files:
            print(f"   ✗ {file_path}")
    else:
        print("\\n🎉 ¡Estructura validada correctamente!")

def main():
    """Función principal del script de reorganización"""
    print("🔧 REORGANIZACIÓN DEL PROYECTO TRAJECTORY HUB")
    print("="*60)
    
    try:
        # Paso 1: Crear estructura de directorios
        create_directory_structure()
        
        # Paso 2: Crear archivos __init__.py
        create_init_files()
        
        # Paso 3: Reorganizar archivos existentes
        copy_and_fix_files()
        
        # Paso 4: Corregir imports
        fix_imports()
        
        # Paso 5: Crear punto de entrada principal
        create_main_entry_point()
        
        # Paso 6: Crear archivos de configuración
        create_requirements_file()
        create_setup_py()
        create_gitignore()
        
        # Paso 7: Validar estructura final
        validate_structure()
        
        print("\\n" + "="*60)
        print("✅ REORGANIZACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\\n🚀 Próximos pasos:")
        print("   1. Verificar que todos los archivos están en su lugar")
        print("   2. Ejecutar: python main.py --interactive")
        print("   3. Probar que todo funciona correctamente")
        print("   4. Instalar en modo desarrollo: pip install -e .")
        print("\\n💡 El proyecto ahora tiene una estructura modular y escalable")
        
    except Exception as e:
        print(f"\\n❌ Error durante la reorganización: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)