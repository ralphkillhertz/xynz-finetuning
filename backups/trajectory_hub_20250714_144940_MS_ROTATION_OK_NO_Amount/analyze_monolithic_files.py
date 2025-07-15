#!/usr/bin/env python3
"""
Analizador de Archivos Monolíticos
Ayuda a entender y dividir archivos grandes de forma segura
"""

import ast
import os
from typing import Dict, List, Tuple
import json


class MonolithicAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None
        self.functions = {}
        self.classes = {}
        self.dependencies = {}
        
    def analyze(self):
        """Analiza estructura completa del archivo"""
        with open(self.file_path, 'r') as f:
            content = f.read()
            
        self.tree = ast.parse(content)
        self._extract_components()
        self._analyze_dependencies()
        return self.generate_report()
        
    def _extract_components(self):
        """Extrae todas las funciones y clases"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self.functions[node.name] = {
                    'line_start': node.lineno,
                    'line_end': node.end_lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [d.id for d in node.decorator_list if hasattr(d, 'id')],
                    'calls': self._extract_calls(node)
                }
            elif isinstance(node, ast.ClassDef):
                self.classes[node.name] = {
                    'line_start': node.lineno,
                    'line_end': node.end_lineno,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    'bases': [b.id for b in node.bases if hasattr(b, 'id')]
                }
                
    def _extract_calls(self, node):
        """Extrae todas las llamadas a funciones dentro de un nodo"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id'):
                    calls.append(child.func.id)
                elif hasattr(child.func, 'attr'):
                    calls.append(f"{child.func.value.id if hasattr(child.func.value, 'id') else 'self'}.{child.func.attr}")
        return calls
        
    def _analyze_dependencies(self):
        """Analiza dependencias entre componentes"""
        for func_name, func_data in self.functions.items():
            deps = set()
            for call in func_data['calls']:
                if call in self.functions or call.startswith('self.'):
                    deps.add(call)
            self.dependencies[func_name] = list(deps)
            
    def generate_report(self) -> Dict:
        """Genera reporte completo"""
        total_lines = 0
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                total_lines = len(f.readlines())
                
        return {
            'file': self.file_path,
            'total_lines': total_lines,
            'total_functions': len(self.functions),
            'total_classes': len(self.classes),
            'functions': self.functions,
            'classes': self.classes,
            'dependencies': self.dependencies,
            'complexity_score': self._calculate_complexity()
        }
        
    def _calculate_complexity(self) -> int:
        """Calcula complejidad ciclomática aproximada"""
        complexity = 0
        for func_data in self.functions.values():
            # Aproximación: más llamadas = más complejidad
            complexity += len(func_data['calls'])
        return complexity
        
    def suggest_splits(self) -> List[Dict]:
        """Sugiere cómo dividir el archivo"""
        suggestions = []
        
        # Agrupar por funcionalidad (basado en nombres)
        groups = {}
        for func_name in self.functions:
            prefix = func_name.split('_')[0]
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(func_name)
            
        for group_name, funcs in groups.items():
            if len(funcs) > 3:  # Grupo significativo
                suggestions.append({
                    'module_name': f"{group_name}_module",
                    'functions': funcs,
                    'reason': f"Agrupa {len(funcs)} funciones relacionadas con '{group_name}'"
                })
                
        return suggestions


def analyze_project_files(directory: str):
    """Analiza todos los archivos Python grandes del proyecto"""
    results = {}
    problem_files = []
    
    for root, dirs, files in os.walk(directory):
        # Ignorar directorios de caché
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py') and not file.endswith('_backup.py'):
                file_path = os.path.join(root, file)
                
                # Verificar tamaño
                size = os.path.getsize(file_path)
                if size > 50000:  # Archivos > 50KB
                    try:
                        analyzer = MonolithicAnalyzer(file_path)
                        report = analyzer.analyze()
                        
                        if report['total_lines'] > 500:  # Archivos problemáticos
                            problem_files.append({
                                'file': file_path,
                                'lines': report['total_lines'],
                                'functions': report['total_functions'],
                                'complexity': report['complexity_score'],
                                'suggestions': analyzer.suggest_splits()
                            })
                            
                        results[file_path] = report
                    except Exception as e:
                        print(f"Error analizando {file_path}: {e}")
                        
    return results, problem_files


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Analizar archivo específico
        file_path = sys.argv[1]
        analyzer = MonolithicAnalyzer(file_path)
        report = analyzer.analyze()
        
        print(f"\n📊 Análisis de {os.path.basename(file_path)}")
        print(f"{'='*60}")
        print(f"Total líneas: {report['total_lines']}")
        print(f"Total funciones: {report['total_functions']}")
        print(f"Total clases: {report['total_classes']}")
        print(f"Complejidad: {report['complexity_score']}")
        
        print(f"\n🔧 Sugerencias de división:")
        for suggestion in analyzer.suggest_splits():
            print(f"\n  • {suggestion['module_name']}.py")
            print(f"    Razón: {suggestion['reason']}")
            print(f"    Funciones: {', '.join(suggestion['functions'][:5])}")
            if len(suggestion['functions']) > 5:
                print(f"    ... y {len(suggestion['functions']) - 5} más")
    else:
        # Analizar todo el proyecto
        results, problems = analyze_project_files('trajectory_hub')
        
        print("\n🚨 ARCHIVOS PROBLEMÁTICOS (Monolíticos)")
        print("="*80)
        
        for problem in sorted(problems, key=lambda x: x['lines'], reverse=True):
            print(f"\n📄 {problem['file']}")
            print(f"   Líneas: {problem['lines']}")
            print(f"   Funciones: {problem['functions']}")
            print(f"   Complejidad: {problem['complexity']}")
            
        # Guardar reporte completo
        with open('monolithic_analysis_report.json', 'w') as f:
            json.dump(problems, f, indent=2)
            
        print(f"\n📊 Reporte completo guardado en 'monolithic_analysis_report.json'")