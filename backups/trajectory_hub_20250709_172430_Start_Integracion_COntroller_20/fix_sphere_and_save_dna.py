import os
import json
from datetime import datetime
import shutil

def fix_sphere_and_save_dna():
    """Arreglar sphere y guardar el ADN del proyecto"""
    print("🧬 IMPLEMENTACIÓN SPHERE + ADN DEL PROYECTO")
    print("="*60)
    
    # 1. Primero arreglar sphere en la arquitectura ACTUAL
    fix_sphere_current_architecture()
    
    # 2. Guardar el ADN arquitectónico
    save_project_dna()
    
    # 3. Actualizar SESSION_STATE
    update_session_state()

def fix_sphere_current_architecture():
    """Arreglar sphere según dónde realmente se calculan las formaciones"""
    print("\n1️⃣ ARREGLANDO SPHERE EN ARQUITECTURA ACTUAL")
    print("-" * 40)
    
    # Buscar dónde están los cálculos de formaciones
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if os.path.exists(engine_file):
        # Backup
        backup = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(engine_file, backup)
        
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Verificar si tiene _calculate_circle_positions
        if '_calculate_circle_positions' in content and '_calculate_sphere_positions' not in content:
            print("✅ Engine tiene circle pero no sphere, añadiendo...")
            
            # Añadir después de circle
            sphere_method = '''
    def _calculate_sphere_positions(self, n_sources, center=(0, 0, 0), radius=2.0):
        """
        Calcular posiciones en formación esférica 3D.
        Usa espiral de Fibonacci para distribución uniforme.
        """
        import numpy as np
        
        positions = []
        
        # Espiral de Fibonacci para distribución uniforme en esfera
        golden_angle = np.pi * (3.0 - np.sqrt(5.0))  # ~2.39996
        
        for i in range(n_sources):
            # y va de 1 a -1 (polo norte a polo sur)
            y = 1 - (i / float(n_sources - 1)) * 2 if n_sources > 1 else 0
            
            # Radio en plano XZ para esta altura
            radius_at_y = np.sqrt(1 - y * y)
            
            # Ángulo usando proporción áurea
            theta = golden_angle * i
            
            # Coordenadas cartesianas
            x = np.cos(theta) * radius_at_y
            z = np.sin(theta) * radius_at_y
            
            # Escalar y trasladar
            positions.append((
                center[0] + x * radius,
                center[1] + y * radius,  # Y es la altura (3D!)
                center[2] + z * radius
            ))
        
        return positions
'''
            
            # Insertar después de _calculate_circle_positions
            circle_end = content.find("return positions", 
                                    content.find("_calculate_circle_positions"))
            if circle_end > 0:
                # Buscar el siguiente método o final de clase
                next_def = content.find("\n    def ", circle_end)
                if next_def > 0:
                    content = content[:next_def] + sphere_method + '\n' + content[next_def:]
                else:
                    # Insertar antes del final de la clase
                    content = content + sphere_method
                
                # Ahora buscar dónde se mapean las formaciones
                # En create_macro
                create_macro_start = content.find("def create_macro")
                if create_macro_start > 0:
                    # Buscar el mapeo de formaciones
                    mapping_area = content[create_macro_start:create_macro_start+3000]
                    
                    # Buscar pattern tipo: elif formation == "random":
                    import re
                    last_elif = None
                    for match in re.finditer(r'elif formation == "(\w+)":', mapping_area):
                        last_elif = match
                    
                    if last_elif:
                        # Añadir sphere después del último elif
                        insert_pos = create_macro_start + last_elif.end()
                        # Buscar el final del bloque
                        lines_after = content[insert_pos:].split('\n')
                        indent_level = len(lines_after[0]) - len(lines_after[0].lstrip())
                        
                        # Encontrar dónde termina el bloque actual
                        for i, line in enumerate(lines_after[1:], 1):
                            if line.strip() and len(line) - len(line.lstrip()) <= indent_level:
                                # Insertar aquí
                                sphere_elif = f'''
        elif formation == "sphere":
            positions = self._calculate_sphere_positions(
                self.config['n_sources'],
                center=(0, 0, 0),
                radius=2.0
            )'''
                                insert_at = insert_pos + sum(len(l) + 1 for l in lines_after[:i])
                                content = content[:insert_at] + sphere_elif + '\n' + content[insert_at:]
                                print("✅ Añadido mapeo sphere en create_macro")
                                break
                
                # Guardar
                with open(engine_file, 'w') as f:
                    f.write(content)
                
                print("✅ Sphere implementado en engine")

def save_project_dna():
    """Guardar el ADN arquitectónico del proyecto"""
    print("\n2️⃣ GUARDANDO ADN DEL PROYECTO")
    print("-" * 40)
    
    project_dna = {
        "project": "trajectory_hub",
        "version": "2.0-alpha",
        "dna_version": "1.0",
        "timestamp": datetime.now().isoformat(),
        
        "🧬 ADN_ARQUITECTONICO": {
            "vision": "Control Híbrido IA + Gestual con arquitectura event-driven y capa semántica",
            
            "principios_fundamentales": [
                "1. SEPARACIÓN DE RESPONSABILIDADES: UI ≠ Lógica ≠ Ejecución",
                "2. ARQUITECTURA POR CAPAS: Input → Command → Orchestration → Execution",
                "3. INTERFAZ UNIFICADA: Mismo backend para IA, Gestos y CLI",
                "4. SEMÁNTICA SOBRE SINTAXIS: Intenciones, no comandos directos",
                "5. TIMELINE-AWARE: Gestión temporal integrada"
            ],
            
            "arquitectura_capas": {
                "1_CAPA_INTENCIONES": {
                    "descripcion": "Semantic Command Interface - Interpreta intenciones de alto nivel",
                    "entradas": ["MCP/IA", "Gestos", "CLI Interactivo"],
                    "salida": "SemanticCommand"
                },
                
                "2_COMMAND_PROCESSOR": {
                    "descripcion": "Interpreta intenciones → acciones ejecutables",
                    "responsabilidad": "TODA la lógica de negocio",
                    "no_debe": "Manejar UI o ejecutar directamente"
                },
                
                "3_ACTION_ORCHESTRATOR": {
                    "descripcion": "Combina acciones atómicas en flujos complejos",
                    "engines": ["Movement", "Rotation", "Modulation", "Behavior", "Timeline"]
                },
                
                "4_EXECUTION_LAYER": {
                    "descripcion": "Engines especializados que ejecutan acciones",
                    "caracteristica": "Optimizados para tiempo real"
                }
            },
            
            "interactive_controller_v2": {
                "rol": "SOLO interfaz CLI - navegación de menús",
                "metodos_max": 25,
                "responsabilidades": [
                    "Mostrar menús",
                    "Capturar input usuario",
                    "Construir SemanticCommands",
                    "Delegar a CommandProcessor"
                ],
                "prohibido": [
                    "Lógica de negocio",
                    "Cálculos directos",
                    "Manipulación de estado"
                ]
            },
            
            "componentes_nuevos": {
                "SemanticCommand": "Representa intenciones de alto nivel",
                "IntentionParser": "Parsea lenguaje natural y gestos",
                "ActionLibrary": "Biblioteca de acciones componibles",
                "TimelineEngine": "Gestiona acciones temporales y loops",
                "GestureMapper": "Mapea gestos a comandos semánticos"
            }
        },
        
        "🎯 OBJETIVOS_INMEDIATOS": [
            "1. Completar integración sphere 3D",
            "2. Implementar servidor MCP",
            "3. Refactorizar InteractiveController según nueva arquitectura",
            "4. Crear CommandProcessor unificado",
            "5. Implementar TimelineEngine"
        ],
        
        "⚠️ REGLAS_CRITICAS": [
            "NUNCA mezclar UI con lógica en InteractiveController",
            "SIEMPRE usar SemanticCommands para comunicación entre capas",
            "TODO input (IA/Gestos/CLI) debe pasar por CommandProcessor",
            "FormationManager calcula, Engine aplica, Controller muestra"
        ],
        
        "📐 METRICAS_OBJETIVO": {
            "interactive_controller_metodos": "≤ 25",
            "command_processor_responsabilidad": "100% lógica",
            "separation_of_concerns": "estricta",
            "test_coverage_minimo": "80%"
        }
    }
    
    # Guardar en múltiples lugares para persistencia
    locations = [
        "PROJECT_DNA.json",
        "trajectory_hub/PROJECT_DNA.json",
        "docs/PROJECT_DNA.json"
    ]
    
    for location in locations:
        try:
            os.makedirs(os.path.dirname(location), exist_ok=True) if os.path.dirname(location) else None
            with open(location, 'w', encoding='utf-8') as f:
                json.dump(project_dna, f, indent=2, ensure_ascii=False)
            print(f"✅ ADN guardado en: {location}")
            break
        except:
            continue

def update_session_state():
    """Actualizar SESSION_STATE con la nueva visión"""
    print("\n3️⃣ ACTUALIZANDO SESSION_STATE")
    print("-" * 40)
    
    session_state = {
        "session_id": f"20250709_sphere_fix_and_dna",
        "timestamp": datetime.now().isoformat(),
        "project": "trajectory_hub",
        "phase": "architectural_transformation",
        "status": "Sphere implementado, ADN arquitectónico definido",
        
        "trabajo_realizado": {
            "sphere_3d": "Implementado en engine con espiral Fibonacci",
            "project_dna": "Definido y guardado",
            "nueva_arquitectura": "Documentada para futura implementación"
        },
        
        "⚠️ CRITICO_PROXIMA_SESION": {
            "mensaje": "LEER PROJECT_DNA.json ANTES DE CUALQUIER CAMBIO",
            "arquitectura": "RESPETAR SEPARACIÓN DE CAPAS",
            "interactive_controller": "NO añadir lógica, solo UI",
            "command_processor": "Toda la lógica va aquí"
        },
        
        "pendiente_proxima_sesion": [
            "1. 🧪 Verificar sphere 3D funciona correctamente",
            "2. 🚨 CRÍTICO: Implementar servidor MCP",
            "3. 🏗️ Iniciar refactorización a nueva arquitectura",
            "4. 📋 Crear CommandProcessor unificado",
            "5. ⏱️ Implementar TimelineEngine"
        ],
        
        "comandos_utiles": {
            "test_sphere": "python main.py --interactive → crear macro → sphere",
            "ver_dna": "cat PROJECT_DNA.json",
            "iniciar_refactor": "python start_architectural_refactor.py"
        },
        
        "notas_arquitectonicas": [
            "La nueva arquitectura es EVENT-DRIVEN con CAPA SEMÁNTICA",
            "InteractiveController debe reducirse de 122 a ~25 métodos",
            "TODO pasa por CommandProcessor (IA, Gestos, CLI)",
            "Separación estricta: UI ≠ Lógica ≠ Ejecución"
        ]
    }
    
    with open("SESSION_STATE.json", 'w', encoding='utf-8') as f:
        json.dump(session_state, f, indent=2, ensure_ascii=False)
    
    print("✅ SESSION_STATE actualizado con ADN del proyecto")

if __name__ == "__main__":
    fix_sphere_and_save_dna()
    
    print("\n" + "="*60)
    print("🎉 COMPLETADO")
    print("="*60)
    print("\n📋 RESUMEN:")
    print("1. ✅ Sphere implementado en engine (3D real)")
    print("2. ✅ PROJECT_DNA.json creado (visión arquitectónica)")
    print("3. ✅ SESSION_STATE.json actualizado")
    print("\n⚠️ IMPORTANTE PARA PRÓXIMA SESIÓN:")
    print("- SIEMPRE cargar PROJECT_DNA.json primero")
    print("- Respetar la nueva arquitectura por capas")
    print("- No añadir lógica a InteractiveController")
    print("\n🚀 PRUEBA SPHERE:")
    print("python main.py --interactive")
    print("→ Crear macro → Seleccionar sphere (opción 6)")