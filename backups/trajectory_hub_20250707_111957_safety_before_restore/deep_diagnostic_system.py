#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO PROFUNDO DEL SISTEMA ACTUAL
📊 Análisis completo pre-implementación paralela
⚡ Identifica TODOS los bloqueos y dependencias
"""

import os
import re
import json
import ast
from datetime import datetime
from collections import defaultdict
import inspect

class DeepSystemDiagnostic:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': {},
            'dependencies': defaultdict(list),
            'blocking_patterns': [],
            'method_flows': {},
            'component_interactions': {},
            'issues_found': []
        }
        
    def find_project_files(self):
        """Localizar todos los archivos relevantes del proyecto"""
        print("🔍 FASE 1: LOCALIZACIÓN DE ARCHIVOS")
        print("="*60)
        
        files_found = {}
        patterns = {
            'engine': ['engine.py', 'enhanced_trajectory_engine.py', 'trajectory_engine.py'],
            'motion': ['motion_components.py', 'motion_system.py'],
            'rotation': ['rotation_system.py', 'rotation_components.py'],
            'concentration': ['concentration.py', 'advanced/concentration.py'],
            'controller': ['interactive_controller.py', 'controller.py'],
            'modulation': ['modulation_3d.py', 'orientation_modulation.py']
        }
        
        for category, filenames in patterns.items():
            for root, dirs, files in os.walk("trajectory_hub"):
                for file in files:
                    if file in filenames:
                        filepath = os.path.join(root, file)
                        files_found[category] = filepath
                        print(f"✅ {category}: {filepath}")
                        
        self.results['files_analyzed'] = files_found
        return files_found
    
    def analyze_update_flow(self, filepath):
        """Analizar el flujo del método update en un archivo"""
        print(f"\n📊 Analizando flujo de update en: {os.path.basename(filepath)}")
        
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Buscar métodos update
        update_methods = re.findall(r'def update\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', 
                                   content, re.DOTALL)
        
        flow_analysis = {
            'update_methods_count': len(update_methods),
            'component_calls': [],
            'blocking_conditions': [],
            'state_modifications': []
        }
        
        for method_body in update_methods:
            # Buscar llamadas a componentes
            component_calls = re.findall(r'(\w+)\.update\(|(\w+)\.apply\(', method_body)
            flow_analysis['component_calls'].extend(component_calls)
            
            # Buscar condiciones que bloquean
            if_blocks = re.findall(r'if\s+([^:]+):\s*\n\s*return', method_body)
            flow_analysis['blocking_conditions'].extend(if_blocks)
            
            # Buscar modificaciones de estado
            state_mods = re.findall(r'(position|orientation|state)\s*=(?!=)', method_body)
            flow_analysis['state_modifications'].extend(state_mods)
            
        return flow_analysis
    
    def trace_component_dependencies(self, files):
        """Rastrear dependencias entre componentes"""
        print("\n🔗 FASE 2: RASTREANDO DEPENDENCIAS")
        print("="*60)
        
        dependencies = defaultdict(lambda: {'depends_on': [], 'blocks': [], 'requires': []})
        
        for category, filepath in files.items():
            if not filepath or not os.path.exists(filepath):
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Buscar patrones de dependencia
            patterns = {
                'checks_is': r'if.*individual_trajectory.*enabled',
                'checks_ms': r'if.*macro.*trajectory.*enabled',
                'requires_is': r'assert.*individual_trajectory|raise.*individual.*required',
                'blocks_on_is': r'if.*individual_trajectory.*:\s*return',
                'blocks_on_ms': r'if.*macro.*trajectory.*:\s*return'
            }
            
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    dependencies[category][pattern_name] = len(matches)
                    print(f"  {category} → {pattern_name}: {len(matches)} ocurrencias")
                    
        self.results['dependencies'] = dict(dependencies)
        return dependencies
    
    def analyze_concentration_implementation(self, files):
        """Análisis específico de la implementación de concentración"""
        print("\n🎯 FASE 3: ANÁLISIS DE CONCENTRACIÓN")
        print("="*60)
        
        concentration_info = {
            'location': None,
            'depends_on_is': False,
            'can_work_alone': False,
            'implementation_details': []
        }
        
        # Buscar implementación de concentración
        for category, filepath in files.items():
            if not filepath or not os.path.exists(filepath):
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
                
            if 'concentration' in content.lower() or 'concentrate' in content.lower():
                # Buscar método set_concentration_factor
                if 'set_concentration_factor' in content:
                    concentration_info['location'] = filepath
                    
                    # Verificar si depende de IS
                    method_match = re.search(
                        r'def set_concentration_factor.*?\n(.*?)(?=\n    def|\nclass|\Z)',
                        content, re.DOTALL
                    )
                    
                    if method_match:
                        method_body = method_match.group(1)
                        if 'individual_trajectory' in method_body:
                            concentration_info['depends_on_is'] = True
                            print(f"  ❌ Concentración DEPENDE de IS en: {filepath}")
                        else:
                            concentration_info['can_work_alone'] = True
                            print(f"  ✅ Concentración puede funcionar sola")
                            
        self.results['concentration_analysis'] = concentration_info
        return concentration_info
    
    def analyze_rotation_blocking(self, files):
        """Analizar por qué la rotación MS se bloquea con IS"""
        print("\n🔄 FASE 4: ANÁLISIS DE BLOQUEO DE ROTACIÓN")
        print("="*60)
        
        rotation_blocking = {
            'ms_rotation_blocked_by_is': False,
            'blocking_locations': [],
            'blocking_code': []
        }
        
        # Buscar en archivos de rotación
        for category, filepath in files.items():
            if not filepath or not os.path.exists(filepath):
                continue
                
            if 'rotation' in filepath or 'engine' in filepath:
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                # Buscar patrones de bloqueo
                patterns = [
                    r'if.*individual.*trajectory.*:\s*\n.*?return',
                    r'if.*IS.*enabled.*:\s*\n.*?skip.*MS',
                    r'if.*source.*has.*trajectory.*:\s*\n.*?continue'
                ]
                
                for pattern in patterns:
                    matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))
                    for match in matches:
                        rotation_blocking['ms_rotation_blocked_by_is'] = True
                        rotation_blocking['blocking_locations'].append({
                            'file': filepath,
                            'pattern': pattern,
                            'code': match.group(0)
                        })
                        print(f"  ❌ Bloqueo encontrado en {os.path.basename(filepath)}")
                        print(f"     {match.group(0)[:50]}...")
                        
        self.results['rotation_blocking'] = rotation_blocking
        return rotation_blocking
    
    def generate_diagnostic_report(self):
        """Generar reporte completo del diagnóstico"""
        print("\n📋 GENERANDO REPORTE DE DIAGNÓSTICO")
        print("="*60)
        
        report = {
            'diagnostic_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': len(self.results['files_analyzed']),
                'blocking_patterns_found': len(self.results['blocking_patterns']),
                'dependencies_identified': sum(len(v) for v in self.results['dependencies'].values()),
                'critical_issues': []
            },
            'detailed_findings': self.results,
            'recommendations': []
        }
        
        # Identificar problemas críticos
        if self.results.get('concentration_analysis', {}).get('depends_on_is'):
            report['summary']['critical_issues'].append(
                "Concentración depende de IS - debe ser independiente"
            )
            
        if self.results.get('rotation_blocking', {}).get('ms_rotation_blocked_by_is'):
            report['summary']['critical_issues'].append(
                "Rotación MS bloqueada por IS - deben poder coexistir"
            )
            
        # Generar recomendaciones
        report['recommendations'] = [
            "1. Implementar arquitectura de deltas para suma de componentes",
            "2. Eliminar dependencias entre IS y MS",
            "3. Hacer concentración independiente de otros componentes",
            "4. Permitir que todos los componentes se ejecuten en paralelo"
        ]
        
        # Guardar reporte
        report_filename = f"DIAGNOSTIC_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n✅ Reporte guardado: {report_filename}")
        return report

# EJECUTAR DIAGNÓSTICO
if __name__ == "__main__":
    print("🔍 SISTEMA DE DIAGNÓSTICO PROFUNDO")
    print("="*80)
    
    diagnostic = DeepSystemDiagnostic()
    
    # 1. Encontrar archivos
    files = diagnostic.find_project_files()
    
    # 2. Analizar flujos de update
    print("\n📊 ANALIZANDO FLUJOS DE UPDATE")
    print("-"*60)
    for category, filepath in files.items():
        if filepath and os.path.exists(filepath):
            flow = diagnostic.analyze_update_flow(filepath)
            diagnostic.results['method_flows'][category] = flow
            if flow['blocking_conditions']:
                print(f"  ⚠️ {category}: {len(flow['blocking_conditions'])} condiciones de bloqueo")
    
    # 3. Rastrear dependencias
    dependencies = diagnostic.trace_component_dependencies(files)
    
    # 4. Analizar concentración
    concentration = diagnostic.analyze_concentration_implementation(files)
    
    # 5. Analizar bloqueo de rotación
    rotation_blocking = diagnostic.analyze_rotation_blocking(files)
    
    # 6. Generar reporte
    report = diagnostic.generate_diagnostic_report()
    
    # RESUMEN EJECUTIVO
    print("\n" + "="*80)
    print("📊 RESUMEN EJECUTIVO DEL DIAGNÓSTICO")
    print("="*80)
    
    print("\n🔴 PROBLEMAS CRÍTICOS ENCONTRADOS:")
    for issue in report['summary']['critical_issues']:
        print(f"  • {issue}")
        
    print("\n🟡 COMPONENTES AFECTADOS:")
    for comp, deps in diagnostic.results['dependencies'].items():
        if deps:
            print(f"  • {comp}: {len(deps)} dependencias problemáticas")
            
    print("\n🟢 SOLUCIÓN PROPUESTA:")
    for rec in report['recommendations']:
        print(f"  {rec}")
        
    print("\n💾 Diagnóstico completo guardado en:", report_filename)
    print("="*80)