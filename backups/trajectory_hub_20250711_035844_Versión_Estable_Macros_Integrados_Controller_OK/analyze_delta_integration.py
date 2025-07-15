#!/usr/bin/env python3
"""
Analizador de Integración Delta-Controller
Examina cómo están integrados los deltas con el controller
"""

import ast
import re
from typing import Dict, List, Set


class DeltaIntegrationAnalyzer:
    def __init__(self):
        self.delta_methods = set()
        self.delta_calls = []
        self.integration_points = []
        
    def analyze_file(self, filepath: str) -> Dict:
        """Analiza un archivo buscando integración con deltas"""
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Buscar métodos relacionados con delta
        delta_pattern = r'def\s+(\w*delta\w*|.*_delta.*)\s*\('
        self.delta_methods = set(re.findall(delta_pattern, content, re.IGNORECASE))
        
        # Buscar llamadas a delta
        call_patterns = [
            r'\.calculate_delta\s*\(',
            r'\.apply_delta\s*\(',
            r'\.update_with_deltas\s*\(',
            r'MotionDelta\s*\(',
            r'delta\s*=',
            r'deltas\s*\.',
            r'self\.delta'
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            for pattern in call_patterns:
                if re.search(pattern, line):
                    self.delta_calls.append({
                        'line': i + 1,
                        'code': line.strip(),
                        'pattern': pattern
                    })
                    
        # Buscar puntos de integración específicos
        integration_patterns = [
            (r'_show_delta_menu', 'Menu de deltas'),
            (r'_process_delta_choice', 'Procesamiento de opciones delta'),
            (r'ConcentrationComponent', 'Componente de concentración'),
            (r'MacroTrajectory', 'Trayectoria macro'),
            (r'IndividualTrajectory', 'Trayectoria individual'),
            (r'MacroRotation', 'Rotación macro'),
            (r'IndividualRotation', 'Rotación individual')
        ]
        
        for pattern, desc in integration_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.integration_points.append({
                    'component': desc,
                    'line': line_num,
                    'context': self._get_context(lines, line_num - 1)
                })
                
        return self.generate_report()
        
    def _get_context(self, lines: List[str], line_idx: int) -> str:
        """Obtiene contexto alrededor de una línea"""
        start = max(0, line_idx - 2)
        end = min(len(lines), line_idx + 3)
        return '\n'.join(lines[start:end])
        
    def generate_report(self) -> Dict:
        """Genera reporte de análisis"""
        return {
            'delta_methods': list(self.delta_methods),
            'delta_calls': self.delta_calls,
            'integration_points': self.integration_points,
            'summary': {
                'total_methods': len(self.delta_methods),
                'total_calls': len(self.delta_calls),
                'total_integrations': len(self.integration_points)
            }
        }


def analyze_delta_system():
    """Analiza el sistema completo de deltas"""
    analyzer = DeltaIntegrationAnalyzer()
    
    files_to_analyze = [
        "/Volumes/RK Work/Ralph Killhertz/XYNZ/XYNZ-SPAT/trajectory_hub/trajectory_hub/interface/interactive_controller.py",
        "/Volumes/RK Work/Ralph Killhertz/XYNZ/XYNZ-SPAT/trajectory_hub/trajectory_hub/core/enhanced_trajectory_engine.py",
        "/Volumes/RK Work/Ralph Killhertz/XYNZ/XYNZ-SPAT/trajectory_hub/trajectory_hub/core/motion_components.py"
    ]
    
    print("🔍 ANÁLISIS DE INTEGRACIÓN DELTA-CONTROLLER")
    print("="*70)
    
    all_reports = {}
    
    for filepath in files_to_analyze:
        try:
            report = analyzer.analyze_file(filepath)
            all_reports[filepath] = report
            
            filename = filepath.split('/')[-1]
            print(f"\n📄 {filename}")
            print(f"   Métodos delta: {report['summary']['total_methods']}")
            print(f"   Llamadas delta: {report['summary']['total_calls']}")
            print(f"   Puntos de integración: {report['summary']['total_integrations']}")
            
            if report['delta_methods']:
                print(f"\n   Métodos encontrados:")
                for method in sorted(report['delta_methods']):
                    print(f"     • {method}")
                    
            if report['integration_points']:
                print(f"\n   Componentes integrados:")
                components = set(p['component'] for p in report['integration_points'])
                for comp in sorted(components):
                    print(f"     • {comp}")
                    
        except Exception as e:
            print(f"\n❌ Error analizando {filepath}: {e}")
            
    # Análisis cruzado
    print("\n\n📊 ANÁLISIS CRUZADO")
    print("="*70)
    
    # Verificar flujo completo
    controller_report = all_reports.get(files_to_analyze[0], {})
    engine_report = all_reports.get(files_to_analyze[1], {})
    components_report = all_reports.get(files_to_analyze[2], {})
    
    # Verificar cadena de integración
    print("\n🔗 Cadena de Integración:")
    
    # Controller → Engine
    if '_show_delta_menu' in str(controller_report.get('delta_methods', [])):
        print("✅ Controller tiene menú de deltas")
    else:
        print("❌ Controller no tiene menú de deltas")
        
    # Engine → Components
    engine_delta_calls = engine_report.get('summary', {}).get('total_calls', 0)
    if engine_delta_calls > 0:
        print(f"✅ Engine realiza {engine_delta_calls} llamadas a deltas")
    else:
        print("❌ Engine no parece usar deltas")
        
    # Components delta implementation
    component_delta_methods = components_report.get('summary', {}).get('total_methods', 0)
    if component_delta_methods > 0:
        print(f"✅ Components tiene {component_delta_methods} métodos delta implementados")
    else:
        print("❌ Components no tiene métodos delta")
        
    print("\n💡 RECOMENDACIONES:")
    
    # Generar recomendaciones basadas en el análisis
    recommendations = []
    
    if engine_delta_calls < 5:
        recommendations.append("• Verificar que el engine esté procesando deltas en el update loop")
        
    if '_process_delta_choice' not in str(controller_report.get('delta_methods', [])):
        recommendations.append("• El controller tiene _process_delta_choice pero puede no estar conectado")
        
    if component_delta_methods < 5:
        recommendations.append("• Verificar que todos los componentes tengan calculate_delta() implementado")
        
    if not recommendations:
        recommendations.append("• La integración delta parece estar completa")
        
    for rec in recommendations:
        print(rec)
        

if __name__ == "__main__":
    analyze_delta_system()