import json
from datetime import datetime
import os

def save_complete_project_state():
    """Guardar estado completo del proyecto con toda la información crítica"""
    
    # Cargar ADN actual
    dna = {}
    if os.path.exists("PROJECT_DNA_IMMUTABLE.json"):
        with open("PROJECT_DNA_IMMUTABLE.json", 'r') as f:
            dna = json.load(f)
    
    state = {
        "🔴 ESTADO_CRÍTICO": {
            "timestamp": datetime.now().isoformat(),
            "session_id": "20250709_sphere_restoration_architecture_documented",
            "project": "trajectory_hub",
            "version": "0.87",
            "status": "Sistema restaurado sin sphere, arquitectura documentada",
            
            "⚠️ ADVERTENCIA": [
                "EL SISTEMA NO RESPETA LA ARQUITECTURA IDEAL",
                "FIXES TEMPORALES HASTA REFACTORIZACIÓN COMPLETA",
                "SIEMPRE CARGAR ESTE DOCUMENTO PRIMERO"
            ]
        },
        
        "🏗️ ARQUITECTURA_ACTUAL": {
            "descripción": "Arquitectura monolítica con violaciones múltiples",
            
            "flujo_actual": {
                "1": "Usuario selecciona crear macro en CLI/Interactive",
                "2": "CLI llama DIRECTAMENTE a Engine.create_macro() ❌",
                "3": "Engine recibe 'formation' string y calcula internamente ❌",
                "4": "Engine calcula posiciones (debería solo aplicarlas) ❌",
                "5": "Engine envía a OSC Bridge",
                "6": "OSC Bridge envía a Spat"
            },
            
            "responsabilidades_actuales": {
                "CLI_Interface": {
                    "hace": ["Muestra menús", "Captura input", "Llama a Engine directamente"],
                    "problemas": ["NO usa CommandProcessor", "Acceso directo a Engine"]
                },
                "Interactive_Controller": {
                    "hace": ["TODO - 122 métodos", "UI + Lógica + Procesamiento"],
                    "problemas": ["Monolítico", "Debería tener máx 25 métodos"]
                },
                "Engine": {
                    "hace": ["Crea macros", "CALCULA formaciones", "Gestiona sources", "Envía OSC"],
                    "problemas": ["NO debería calcular formaciones", "Demasiadas responsabilidades"]
                },
                "FormationManager": {
                    "hace": ["Calcula formaciones correctamente"],
                    "problemas": ["NO es usado por el flujo principal"]
                },
                "CommandProcessor": {
                    "hace": ["Existe pero no se usa en flujo principal"],
                    "problemas": ["Bypassed por CLI"]
                }
            },
            
            "problemas_críticos": [
                "Engine calcula formaciones en lugar de recibirlas",
                "CLI no usa CommandProcessor",
                "FormationManager existe pero no se integra",
                "Interactive Controller es monolítico"
            ]
        },
        
        "🎯 ARQUITECTURA_DESEADA": {
            "descripción": "Arquitectura por capas con separación estricta",
            
            "flujo_correcto": {
                "1": "Usuario interactúa con UI (CLI/Interactive/MCP/Gestos)",
                "2": "UI crea SemanticCommand con intención",
                "3": "CommandProcessor interpreta comando",
                "4": "CommandProcessor usa FormationManager para calcular",
                "5": "CommandProcessor pasa positions[] a Engine",
                "6": "Engine SOLO aplica positions y envía OSC",
                "7": "UI muestra resultado"
            },
            
            "responsabilidades_estrictas": {
                "UI_Layer": {
                    "incluye": ["CLI_Interface", "Interactive_Controller", "MCP_Server", "Gesture_Handler"],
                    "responsabilidades": ["SOLO captura input", "SOLO muestra output", "Crea SemanticCommands"],
                    "prohibido": ["Lógica de negocio", "Cálculos", "Acceso directo a Engine"]
                },
                "Command_Layer": {
                    "incluye": ["CommandProcessor", "IntentionParser"],
                    "responsabilidades": ["TODA la lógica de negocio", "Interpretación semántica", "Orquestación"],
                    "prohibido": ["UI", "Cálculos directos", "Comunicación OSC"]
                },
                "Calculation_Layer": {
                    "incluye": ["FormationManager", "TrajectoryCalculator", "ModulationEngine"],
                    "responsabilidades": ["Cálculos matemáticos", "Algoritmos", "Transformaciones"],
                    "prohibido": ["Lógica de negocio", "UI", "Estado"]
                },
                "Execution_Layer": {
                    "incluye": ["Engine", "OSC_Bridge"],
                    "responsabilidades": ["Aplicar estados", "Comunicación externa", "Gestión de sources"],
                    "prohibido": ["Cálculos", "Lógica de negocio", "UI"]
                }
            },
            
            "principios_arquitectónicos": [
                "SEPARACIÓN DE RESPONSABILIDADES: Cada capa una función",
                "FLUJO UNIDIRECCIONAL: UI → Command → Calc → Execution",
                "INMUTABILIDAD: Estados no se modifican, se reemplazan",
                "TESTABILIDAD: Cada capa independently testeable",
                "EXTENSIBILIDAD: Nuevas features sin tocar capas existentes"
            ]
        },
        
        "🔧 INSTRUCCIONES_SPHERE": {
            "problema_actual": "Engine usa _calculate_circle para sphere, resultando en 2D",
            
            "solución_temporal": {
                "descripción": "Hacer que Engine use FormationManager para sphere",
                "pasos": [
                    "1. Añadir import FormationManager en Engine",
                    "2. Añadir caso elif formation == 'sphere'",
                    "3. Delegar cálculo a FormationManager",
                    "4. Verificar que OSC envíe x,y,z"
                ],
                "código": """
elif formation == "sphere":
    # Solución temporal - Engine usa FormationManager
    if not hasattr(self, '_fm'):
        self._fm = FormationManager()
    positions = self._fm.calculate_formation("sphere", self.config['n_sources'])
    print(f"🌐 Sphere 3D: {len(positions)} posiciones calculadas")
"""
            },
            
            "solución_correcta": {
                "descripción": "Refactorizar para que Engine reciba positions",
                "requiere": "Implementación completa del CommandProcessor",
                "beneficios": ["Separación de responsabilidades", "Fácil añadir formaciones", "Testeable"]
            }
        },
        
        "📊 MÉTRICAS_ESTADO": {
            "funcionalidades": {
                "formaciones_2D": "5/5 ✅",
                "formaciones_3D": "0/1 ❌ (sphere pendiente)",
                "osc_comunicación": "100% ✅",
                "sistema_deltas": "100% ✅"
            },
            "arquitectura": {
                "separación_responsabilidades": "20% ❌",
                "uso_command_processor": "10% ❌",
                "modularidad": "30% ❌",
                "testabilidad": "25% ❌"
            },
            "deuda_técnica": {
                "interactive_controller_métodos": "122 (objetivo: 25)",
                "engine_responsabilidades": "4 (objetivo: 2)",
                "flujo_directo_ui_engine": "Sí (objetivo: No)"
            }
        },
        
        "🛣️ ROADMAP_MIGRACIÓN": {
            "fase_0_actual": {
                "nombre": "Fixes temporales",
                "estado": "En progreso",
                "tareas": ["Sphere con FormationManager en Engine", "Mantener funcionalidad"]
            },
            "fase_1": {
                "nombre": "Implementar CommandProcessor",
                "duración": "1 semana",
                "tareas": [
                    "Crear SemanticCommand class",
                    "Implementar IntentionParser",
                    "Conectar CLI → CommandProcessor"
                ]
            },
            "fase_2": {
                "nombre": "Refactorizar Engine",
                "duración": "3-4 días",
                "tareas": [
                    "Engine.create_macro recibe positions[]",
                    "Eliminar cálculos de Engine",
                    "Usar solo FormationManager"
                ]
            },
            "fase_3": {
                "nombre": "Reducir InteractiveController",
                "duración": "1 semana",
                "tareas": [
                    "Extraer lógica a CommandProcessor",
                    "Dejar solo UI (25 métodos)",
                    "Crear tests"
                ]
            },
            "fase_4": {
                "nombre": "Implementar MCP + Gestos",
                "duración": "2 semanas",
                "tareas": [
                    "MCP Server",
                    "Gesture Handler",
                    "Timeline Engine"
                ]
            }
        },
        
        "⚠️ REGLAS_INMUTABLES": [
            "1. Engine NUNCA debe calcular formaciones, solo aplicar positions",
            "2. TODO input debe pasar por CommandProcessor",
            "3. InteractiveController máximo 25 métodos",
            "4. FormationManager solo calcula, no ejecuta",
            "5. OSC Bridge solo transmite, no procesa",
            "6. UI nunca accede directamente a Engine"
        ],
        
        "💾 ARCHIVOS_CLAVE": {
            "documentación": [
                "PROJECT_DNA_IMMUTABLE.json - ADN completo del proyecto",
                "PROJECT_STRUCTURE_ANALYSIS.json - Análisis arquitectónico",
                "SESSION_STATE_*.json - Estados de sesión"
            ],
            "configuración": [
                "trajectory_hub/config.py - Configuración general",
                "docs/ARQUITECTURA_VISIONARIA.md - Visión futura"
            ],
            "para_modificar": {
                "sphere": "trajectory_hub/core/enhanced_trajectory_engine.py",
                "formaciones": "trajectory_hub/control/managers/formation_manager.py",
                "osc": "trajectory_hub/core/spat_osc_bridge.py"
            }
        },
        
        "🚨 ESTADO_ACTUAL_SISTEMA": {
            "funciona": True,
            "sphere_implementado": False,
            "errores_conocidos": [
                "Sistema no arranca si se añade sphere incorrectamente",
                "Import FormationManager debe ir con otros imports trajectory_hub"
            ],
            "último_backup_funcional": "enhanced_trajectory_engine.py.backup_macro_fix_20250708_093056"
        },
        
        "📝 NOTAS_PRÓXIMA_SESIÓN": [
            "CARGAR PROJECT_DNA_IMMUTABLE.json PRIMERO",
            "Verificar estado con diagnose_current_state.py",
            "NO hacer cambios automáticos sin entender contexto",
            "Sphere debe añadirse manualmente siguiendo instrucciones",
            "Considerar iniciar Fase 1 del roadmap (CommandProcessor)"
        ],
        
        "🎯 COMANDOS_ÚTILES": {
            "verificar_sistema": "python -m trajectory_hub.interface.interactive_controller",
            "test_formaciones": "python check_sphere_helper.py",
            "ver_estructura": "cat PROJECT_DNA_IMMUTABLE.json",
            "diagnosticar": "python diagnose_current_state.py"
        }
    }
    
    # Añadir el ADN completo si existe
    if dna:
        state["🧬 PROJECT_DNA_EMBEDDED"] = dna
    
    # Guardar con timestamp
    filename = f"PROJECT_STATE_COMPLETE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    # También guardar como LATEST
    with open("PROJECT_STATE_LATEST.json", 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Estado completo guardado: {filename}")
    print("✅ También guardado como: PROJECT_STATE_LATEST.json")
    
    return state

def print_summary(state):
    """Imprimir resumen del estado guardado"""
    print("\n" + "="*60)
    print("📊 RESUMEN DEL ESTADO GUARDADO")
    print("="*60)
    
    print("\n🏗️ ARQUITECTURA:")
    print("  Actual: Monolítica con violaciones")
    print("  Deseada: Por capas con separación estricta")
    
    print("\n📈 PROGRESO:")
    metrics = state["📊 MÉTRICAS_ESTADO"]["funcionalidades"]
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n⚠️ PROBLEMAS PRINCIPALES:")
    for problema in state["🏗️ ARQUITECTURA_ACTUAL"]["problemas_críticos"]:
        print(f"  • {problema}")
    
    print("\n🛣️ PRÓXIMOS PASOS:")
    print("  1. Añadir sphere manualmente (instrucciones en el estado)")
    print("  2. Iniciar Fase 1: Implementar CommandProcessor")
    print("  3. Seguir roadmap de migración")
    
    print("\n💡 IMPORTANTE PARA PRÓXIMA SESIÓN:")
    for nota in state["📝 NOTAS_PRÓXIMA_SESIÓN"]:
        print(f"  • {nota}")

if __name__ == "__main__":
    print("💾 GUARDANDO ESTADO COMPLETO DEL PROYECTO")
    print("="*60)
    
    state = save_complete_project_state()
    print_summary(state)
    
    print("\n\n✅ ESTADO GUARDADO EXITOSAMENTE")
    print("\n📋 Este archivo contiene:")
    print("  • Arquitectura actual (con problemas)")
    print("  • Arquitectura deseada (objetivo)")
    print("  • Instrucciones para sphere")
    print("  • ADN del proyecto")
    print("  • Roadmap de migración")
    print("  • Reglas inmutables")
    print("\n🚀 Úsalo como referencia en cada sesión")