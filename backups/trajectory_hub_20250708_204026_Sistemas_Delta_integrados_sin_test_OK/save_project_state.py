import json
from datetime import datetime

state = {
    "session_id": "20250708_manual_rotation_is_debugging",
    "timestamp": datetime.now().isoformat(),
    "project": "trajectory_hub",
    "phase": "manual_individual_rotation_implementation",
    "status": "90% funcional - bug en calculate_delta",
    
    "modulos_modificados": [
        "trajectory_hub/core/motion_components.py",
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/interface/interactive_controller.py"
    ],
    
    "cambios_principales": [
        "Sistema de deltas 100% funcional para 6/7 componentes",
        "ManualIndividualRotation implementada pero con bug",
        "Corregido bug de iteración en SourceMotion.update()",
        "Corregida conversión de ángulos grados/radianes",
        "Añadido método update() a ManualIndividualRotation"
    ],
    
    "problema_actual": {
        "descripcion": "ManualIndividualRotation actualiza current_yaw correctamente pero la posición solo rota parcialmente",
        "sintomas": [
            "current_yaw llega a 90° en 4 frames",
            "Posición física solo llega a 6.8° de rotación",
            "El componente se desactiva cuando current_yaw = target_yaw",
            "calculate_delta parece no estar calculando el movimiento correcto"
        ],
        "diagnostico": "El problema está en calculate_delta que no traduce correctamente current_yaw a movimiento"
    },
    
    "pendiente_proxima_sesion": [
        "Ejecutar diagnose_calculate_delta.py para ver qué deltas se calculan",
        "Corregir el método calculate_delta en ManualIndividualRotation",
        "Verificar que la rotación llegue a 90° completos",
        "CRÍTICO: Implementar servidor MCP (0%)",
        "Actualizar controlador interactivo con todas las funcionalidades"
    ],
    
    "sistema_deltas_estado": {
        "ConcentrationComponent": "✅ 100% funcional",
        "IndividualTrajectory": "✅ 100% funcional",
        "MacroTrajectory": "✅ 100% funcional",
        "MacroRotation": "✅ 100% funcional",
        "ManualMacroRotation": "✅ 100% funcional",
        "IndividualRotation": "✅ 100% funcional",
        "ManualIndividualRotation": "⚠️ 90% - bug en calculate_delta"
    },
    
    "metricas_proyecto": {
        "sistema_deltas": "95% completo (6.9/7 componentes)",
        "core_engine": "95% funcional",
        "controlador_interactivo": "60% - necesita actualización",
        "servidor_mcp": "0% - NO INICIADO - OBJETIVO PRINCIPAL",
        "modulador_3d": "0% - Documentación disponible",
        "proyecto_total": "~85% (sin MCP), ~65% (con MCP)"
    },
    
    "archivos_backup": [
        "motion_components.py.backup_20250708_200609",
        "enhanced_trajectory_engine.py.backup_20250708_195941"
    ],
    
    "scripts_debug_creados": [
        "diagnose_rotation_movement.py",
        "diagnose_rotation_stop.py",
        "diagnose_calculate_delta.py",
        "fix_active_components_iteration.py",
        "fix_update_return_state.py"
    ],
    
    "comando_siguiente": "python diagnose_calculate_delta.py",
    
    "modulos_criticos": {
        "motion_components.py": "v2.1 - ManualIndividualRotation con bug en calculate_delta",
        "enhanced_trajectory_engine.py": "v1.8 - Sistema de deltas funcional",
        "interactive_controller.py": "v1.2 - Necesita actualización con nuevas funcionalidades"
    },
    
    "notas_importantes": [
        "El sistema de deltas está 100% funcional para la mayoría de componentes",
        "Solo falta corregir calculate_delta en ManualIndividualRotation",
        "MCP Server es el objetivo principal y está en 0%",
        "La rotación funciona pero se detiene prematuramente"
    ]
}

# Guardar estado
with open("PROYECTO_STATE.json", "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("✅ Estado guardado en PROYECTO_STATE.json")
print(f"\n📊 Resumen de la sesión:")
print(f"  - Sistema de deltas: 95% completo")
print(f"  - ManualIndividualRotation: 90% (bug en calculate_delta)")
print(f"  - Próximo comando: {state['comando_siguiente']}")
print(f"  - Problema actual: Rotación se detiene en 6.8° en lugar de 90°")
print(f"\n⚠️ CRÍTICO: Servidor MCP en 0% - objetivo principal del proyecto")