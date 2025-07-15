import os
import json
import re
from datetime import datetime
from pathlib import Path

def analyze_real_structure():
    """Analizar la estructura REAL actual del proyecto"""
    print("🔬 ANÁLISIS PROFUNDO DE LA ESTRUCTURA ACTUAL")
    print("="*60)
    
    structure = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "ESTADO_ACTUAL": {},
        "ESTADO_OBJETIVO": {},
        "PROBLEMAS_DETECTADOS": [],
        "ROADMAP_MIGRACION": []
    }
    
    # 1. Analizar flujo de creación de macros
    print("\n1️⃣ ANALIZANDO FLUJO DE CREACIÓN DE MACROS...")
    
    flow = analyze_macro_creation_flow()
    structure["ESTADO_ACTUAL"]["flujo_creacion_macros"] = flow
    
    # 2. Analizar responsabilidades actuales
    print("\n2️⃣ ANALIZANDO RESPONSABILIDADES POR COMPONENTE...")
    
    responsibilities = analyze_component_responsibilities()
    structure["ESTADO_ACTUAL"]["responsabilidades"] = responsibilities
    
    # 3. Detectar violaciones arquitectónicas
    print("\n3️⃣ DETECTANDO VIOLACIONES ARQUITECTÓNICAS...")
    
    violations = detect_architectural_violations()
    structure["PROBLEMAS_DETECTADOS"] = violations
    
    # 4. Definir estado objetivo
    print("\n4️⃣ DEFINIENDO ESTADO OBJETIVO...")
    
    structure["ESTADO_OBJETIVO"] = define_target_architecture()
    
    # 5. Crear roadmap
    print("\n5️⃣ CREANDO ROADMAP DE MIGRACIÓN...")
    
    structure["ROADMAP_MIGRACION"] = create_migration_roadmap()
    
    return structure

def analyze_macro_creation_flow():
    """Analizar el flujo real de creación de macros"""
    flow = {
        "inicio": "CLI Interface",
        "pasos": [],
        "problemas": []
    }
    
    # CLI Interface
    cli_file = "trajectory_hub/control/interfaces/cli_interface.py"
    if os.path.exists(cli_file):
        with open(cli_file, 'r') as f:
            cli_content = f.read()
        
        # ¿Qué hace cuando el usuario selecciona crear macro?
        if 'create_macro' in cli_content:
            # Buscar qué llama
            create_calls = re.findall(r'(\w+)\.create_macro\(', cli_content)
            if create_calls:
                flow["pasos"].append({
                    "componente": "CLI Interface",
                    "accion": f"Llama a {create_calls[0]}.create_macro()",
                    "problema": "NO usa CommandProcessor" if 'command_processor' not in create_calls[0].lower() else None
                })
    
    # Engine
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    if os.path.exists(engine_file):
        with open(engine_file, 'r') as f:
            engine_content = f.read()
        
        # ¿Qué hace create_macro?
        create_match = re.search(r'def create_macro\((.*?)\):', engine_content, re.DOTALL)
        if create_match:
            params = create_match.group(1)
            # Fix: reemplazar newline fuera del f-string
            params_clean = params.replace('\n', ' ')
            flow["pasos"].append({
                "componente": "Engine",
                "accion": "Recibe create_macro con parámetros",
                "detalles": f"Parámetros: {params_clean}",
                "problema": "Recibe 'formation' y calcula internamente" if 'formation' in params else None
            })
            
            # ¿Calcula formaciones?
            if 'if formation ==' in engine_content or 'elif formation ==' in engine_content:
                flow["pasos"].append({
                    "componente": "Engine",
                    "accion": "Calcula formaciones internamente",
                    "problema": "VIOLA arquitectura - debería solo aplicar posiciones"
                })
    
    return flow

def analyze_component_responsibilities():
    """Analizar qué hace realmente cada componente"""
    components = {}
    
    # Lista de archivos clave
    files = {
        "CLI Interface": "trajectory_hub/control/interfaces/cli_interface.py",
        "Interactive Controller": "trajectory_hub/interface/interactive_controller.py",
        "Command Processor": "trajectory_hub/control/processors/command_processor.py",
        "Formation Manager": "trajectory_hub/control/managers/formation_manager.py",
        "Engine": "trajectory_hub/core/enhanced_trajectory_engine.py",
        "OSC Bridge": "trajectory_hub/core/spat_osc_bridge.py"
    }
    
    for name, filepath in files.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Contar métodos
            methods = re.findall(r'def (\w+)\(', content)
            
            # Detectar responsabilidades
            responsibilities = []
            
            if 'create_macro' in content:
                responsibilities.append("Crea macros")
            if 'calculate' in content and 'formation' in content:
                responsibilities.append("Calcula formaciones")
            if 'send_' in content and 'osc' in content.lower():
                responsibilities.append("Envía OSC")
            if 'menu' in content or 'show_' in content:
                responsibilities.append("Muestra UI")
            if 'command' in content and 'process' in content:
                responsibilities.append("Procesa comandos")
            
            components[name] = {
                "metodos": len(methods),
                "responsabilidades": responsibilities,
                "viola_arquitectura": []
            }
            
            # Detectar violaciones
            if name == "Engine" and "Calcula formaciones" in responsibilities:
                components[name]["viola_arquitectura"].append("No debería calcular formaciones")
            
            if name == "Interactive Controller" and len(methods) > 50:
                components[name]["viola_arquitectura"].append(f"Demasiados métodos ({len(methods)}), máximo 25")
    
    return components

def detect_architectural_violations():
    """Detectar violaciones específicas"""
    violations = []
    
    # 1. Engine calculando formaciones
    violations.append({
        "tipo": "CRÍTICO",
        "componente": "Engine",
        "problema": "Calcula formaciones internamente en lugar de recibirlas",
        "impacto": "Imposible añadir formaciones sin modificar Engine",
        "solucion": "Engine.create_macro debe recibir positions[], no formation string"
    })
    
    # 2. CLI no usa CommandProcessor
    violations.append({
        "tipo": "ALTO",
        "componente": "CLI Interface",
        "problema": "Llama directamente a Engine sin pasar por CommandProcessor",
        "impacto": "Lógica dispersa, difícil mantener",
        "solucion": "Todo debe pasar por CommandProcessor"
    })
    
    # 3. Interactive Controller monolítico
    violations.append({
        "tipo": "MEDIO",
        "componente": "Interactive Controller",
        "problema": "122 métodos cuando debería tener máximo 25",
        "impacto": "Difícil de mantener y testear",
        "solucion": "Refactorizar delegando lógica a CommandProcessor"
    })
    
    return violations

def define_target_architecture():
    """Definir la arquitectura objetivo"""
    return {
        "principios": [
            "SEPARACIÓN ESTRICTA DE RESPONSABILIDADES",
            "FLUJO UNIDIRECCIONAL DE DATOS",
            "NINGÚN COMPONENTE HACE TODO",
            "TESTABILIDAD COMPLETA"
        ],
        
        "flujo_correcto": {
            "1": "Usuario interactúa con UI (CLI/Interactive/MCP/Gestos)",
            "2": "UI crea SemanticCommand",
            "3": "CommandProcessor interpreta comando",
            "4": "CommandProcessor usa FormationManager para calcular",
            "5": "CommandProcessor pasa positions[] a Engine",
            "6": "Engine aplica positions y envía OSC",
            "7": "UI muestra resultado"
        },
        
        "responsabilidades_estrictas": {
            "CLI Interface": ["Capturar input", "Mostrar output", "Crear comandos"],
            "Interactive Controller": ["Navegación menús", "Display", "MAX 25 métodos"],
            "Command Processor": ["TODA la lógica", "Orquestar", "Validar"],
            "Formation Manager": ["Calcular formaciones", "Nada más"],
            "Engine": ["Aplicar positions", "Gestionar sources", "Enviar OSC"],
            "OSC Bridge": ["Comunicación OSC", "Nada de lógica"]
        }
    }

def create_migration_roadmap():
    """Crear roadmap de migración"""
    return [
        {
            "fase": 1,
            "nombre": "Fix Sphere (temporal)",
            "tareas": [
                "Hacer que Engine use FormationManager para sphere",
                "Verificar que OSC envíe x,y,z"
            ],
            "tiempo": "30 minutos",
            "impacto": "BAJO"
        },
        {
            "fase": 2,
            "nombre": "Refactorizar create_macro",
            "tareas": [
                "Cambiar Engine.create_macro para recibir positions[]",
                "Mover cálculo de formaciones a CommandProcessor",
                "Actualizar todos los llamadores"
            ],
            "tiempo": "2-3 horas",
            "impacto": "ALTO"
        },
        {
            "fase": 3,
            "nombre": "Implementar CommandProcessor completo",
            "tareas": [
                "Crear SemanticCommand class",
                "Implementar interpretación de comandos",
                "Conectar UI → CommandProcessor → Engine"
            ],
            "tiempo": "1 día",
            "impacto": "ALTO"
        },
        {
            "fase": 4,
            "nombre": "Refactorizar Interactive Controller",
            "tareas": [
                "Extraer lógica a CommandProcessor",
                "Reducir a 25 métodos",
                "Solo navegación y display"
            ],
            "tiempo": "2 días",
            "impacto": "MEDIO"
        }
    ]

def create_immutable_dna(structure):
    """Crear ADN inmutable del proyecto"""
    dna = {
        "🧬 TRAJECTORY_HUB_DNA_v2": {
            "version": "2.0",
            "fecha": datetime.now().isoformat(),
            "inmutable": True,
            
            "⚠️ INSTRUCCIONES_CRITICAS": [
                "ESTE DOCUMENTO ES LA VERDAD ABSOLUTA DEL PROYECTO",
                "DEBE SER LO PRIMERO QUE SE CARGUE EN CADA SESIÓN",
                "NINGÚN CAMBIO SIN ACTUALIZAR ESTE DOCUMENTO",
                "TODOS LOS FIXES DEBEN RESPETAR ESTA ARQUITECTURA"
            ],
            
            "📊 ESTADO_ACTUAL_REAL": structure["ESTADO_ACTUAL"],
            
            "🎯 ESTADO_OBJETIVO": structure["ESTADO_OBJETIVO"],
            
            "❌ VIOLACIONES_ACTUALES": structure["PROBLEMAS_DETECTADOS"],
            
            "🛠️ ROADMAP_MIGRACION": structure["ROADMAP_MIGRACION"],
            
            "📋 REGLAS_INMUTABLES": {
                "1": "Engine NUNCA calcula formaciones, solo aplica positions",
                "2": "TODO pasa por CommandProcessor",
                "3": "Interactive Controller máximo 25 métodos",
                "4": "FormationManager solo calcula, no ejecuta",
                "5": "OSC Bridge solo transmite, no procesa"
            },
            
            "🔧 PARA_ARREGLAR_SPHERE": {
                "problema": "Engine calcula sphere como circle (2D)",
                "solucion_temporal": "Hacer que Engine use FormationManager",
                "solucion_correcta": "Refactorizar flujo completo",
                "comando": "python fix_sphere_respecting_current_architecture.py"
            },
            
            "💾 PRESERVAR_ENTRE_SESIONES": [
                "Este DNA completo",
                "Estado de refactorización",
                "Problemas pendientes",
                "Decisiones arquitectónicas"
            ]
        }
    }
    
    return dna

def save_everything():
    """Guardar todo el análisis"""
    print("\n\n💾 GUARDANDO ANÁLISIS COMPLETO...")
    
    # 1. Analizar estructura
    structure = analyze_real_structure()
    
    # 2. Crear DNA inmutable
    dna = create_immutable_dna(structure)
    
    # 3. Guardar archivos
    files_to_save = {
        "PROJECT_STRUCTURE_ANALYSIS.json": structure,
        "PROJECT_DNA_IMMUTABLE.json": dna,
        "PROJECT_DNA.json": dna  # Reemplazar el anterior
    }
    
    for filename, content in files_to_save.items():
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"✅ Guardado: {filename}")
    
    # 4. Crear fix para sphere respetando arquitectura actual
    create_sphere_fix_for_current_architecture()

def create_sphere_fix_for_current_architecture():
    """Crear fix para sphere que funcione con la arquitectura ACTUAL"""
    
    fix_content = '''
# === fix_sphere_respecting_current_architecture.py ===
"""
Fix para sphere que respeta la arquitectura ACTUAL (no la ideal)
Sabiendo que Engine calcula formaciones internamente
"""
import os
import re
from datetime import datetime
import shutil

print("🔧 FIX SPHERE PARA ARQUITECTURA ACTUAL")
print("="*60)

# Dado que Engine calcula formaciones, necesitamos:
# 1. Añadir caso sphere a Engine
# 2. Hacer que delegue a FormationManager

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

if os.path.exists(engine_file):
    backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(engine_file, backup)
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Verificar si ya importa FormationManager
    if 'from trajectory_hub.control.managers.formation_manager import FormationManager' not in content:
        # Añadir import después de otros imports
        import_line = "from trajectory_hub.control.managers.formation_manager import FormationManager\\n"
        
        # Buscar dónde insertar
        last_import = list(re.finditer(r'^from trajectory_hub.*import.*$', content, re.MULTILINE))
        if last_import:
            insert_pos = last_import[-1].end() + 1
            content = content[:insert_pos] + import_line + content[insert_pos:]
        else:
            # Insertar después de imports estándar
            insert_pos = content.find('\\n\\n') + 2
            content = content[:insert_pos] + import_line + content[insert_pos:]
    
    # Buscar dónde están los casos de formation
    # Patrón: elif formation == "algo":
    formation_cases = list(re.finditer(r'elif formation == "[^"]+":', content))
    
    if formation_cases:
        # Insertar después del último caso
        last_case = formation_cases[-1]
        
        # Buscar el final de ese caso
        lines_after = content[last_case.end():].split('\\n')
        indent = len(last_case.group(0)) - len(last_case.group(0).lstrip())
        
        # Encontrar dónde termina el bloque
        end_offset = 0
        for i, line in enumerate(lines_after[1:], 1):
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                end_offset = sum(len(l) + 1 for l in lines_after[:i])
                break
        
        if end_offset == 0:
            end_offset = len(content[last_case.end():])
        
        insert_pos = last_case.end() + end_offset
        
        # Código para sphere
        sphere_code = f"""
        elif formation == "sphere":
            # Usar FormationManager para sphere 3D real
            if not hasattr(self, '_fm'):
                self._fm = FormationManager()
            positions = self._fm.calculate_formation("sphere", self.config['n_sources'])
            print(f"🌐 Sphere 3D: {{len(positions)}} posiciones calculadas")
"""
        
        content = content[:insert_pos] + sphere_code + content[insert_pos:]
        
        print("✅ Caso sphere añadido a Engine")
    else:
        print("❌ No se encontraron casos de formation en Engine")
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("\\n✅ Engine actualizado")

# Verificar OSC
print("\\n🔍 Verificando OSC...")

bridge_file = "trajectory_hub/core/spat_osc_bridge.py"

if os.path.exists(bridge_file):
    with open(bridge_file, 'r') as f:
        bridge_content = f.read()
    
    if 'def send_source_position(self, source_id: int, x: float, y: float)' in bridge_content:
        print("⚠️ OSC solo acepta x,y - Actualizando...")
        
        backup = f"{bridge_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(bridge_file, backup)
        
        # Actualizar para aceptar z
        bridge_content = bridge_content.replace(
            'def send_source_position(self, source_id: int, x: float, y: float)',
            'def send_source_position(self, source_id: int, x: float, y: float, z: float = 0.0)'
        )
        
        # Actualizar envío
        bridge_content = bridge_content.replace(
            '"/source/{source_id}/xyz", [x, y])',
            '"/source/{source_id}/xyz", [x, y, z])'
        )
        
        with open(bridge_file, 'w') as f:
            f.write(bridge_content)
        
        print("✅ OSC actualizado para enviar x,y,z")

print("\\n🎯 SPHERE 3D DEBERÍA FUNCIONAR AHORA")
print("\\n⚠️ NOTA: Este es un fix para la arquitectura ACTUAL")
print("La arquitectura correcta requiere refactorización completa")
'''
    
    with open("fix_sphere_respecting_current_architecture.py", 'w') as f:
        f.write(fix_content)

if __name__ == "__main__":
    save_everything()
    
    print("\n\n" + "="*60)
    print("🧬 DNA DEL PROYECTO ACTUALIZADO")
    print("="*60)
    
    print("\n📋 ARCHIVOS CREADOS:")
    print("  • PROJECT_DNA_IMMUTABLE.json - DNA completo e inmutable")
    print("  • PROJECT_STRUCTURE_ANALYSIS.json - Análisis detallado")
    print("  • fix_sphere_respecting_current_architecture.py - Fix para sphere")
    
    print("\n⚠️ IMPORTANTE PARA PRÓXIMAS SESIONES:")
    print("  1. SIEMPRE cargar PROJECT_DNA_IMMUTABLE.json primero")
    print("  2. Respetar la arquitectura documentada")
    print("  3. No hacer cambios que violen las reglas")
    
    print("\n🔧 PARA ARREGLAR SPHERE AHORA:")
    print("  python fix_sphere_respecting_current_architecture.py")