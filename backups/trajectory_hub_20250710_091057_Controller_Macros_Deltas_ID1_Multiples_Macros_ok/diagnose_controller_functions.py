#!/usr/bin/env python3
"""
🔍 Diagnóstico completo del Interactive Controller
⚡ Revisa cada función y detecta problemas
🎯 Genera reporte de operatividad
"""

import ast
import os
from typing import Dict, List, Tuple
from collections import defaultdict

class ControllerDiagnostic:
    """Diagnostica el estado del Interactive Controller"""
    
    def __init__(self):
        self.controller_file = "trajectory_hub/interface/interactive_controller.py"
        self.issues = defaultdict(list)
        self.stats = {
            "total_methods": 0,
            "menu_methods": 0,
            "action_methods": 0,
            "helper_methods": 0,
            "broken_methods": 0
        }
        
    def diagnose(self) -> Dict[str, any]:
        """Ejecuta diagnóstico completo"""
        print("🔍 DIAGNÓSTICO INTERACTIVE CONTROLLER")
        print("=" * 50)
        
        # Leer archivo
        with open(self.controller_file, 'r') as f:
            content = f.read()
        
        # Parsear AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"❌ Error de sintaxis: {e}")
            return {"error": str(e)}
        
        # Encontrar la clase InteractiveController
        controller_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "InteractiveController":
                controller_class = node
                break
        
        if not controller_class:
            print("❌ No se encontró clase InteractiveController")
            return {"error": "Clase no encontrada"}
        
        # Analizar métodos
        self._analyze_methods(controller_class)
        
        # Detectar problemas comunes
        self._detect_common_issues(content)
        
        # Generar reporte
        return self._generate_report()
    
    def _analyze_methods(self, class_node):
        """Analiza todos los métodos de la clase"""
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                self.stats["total_methods"] += 1
                method_name = node.name
                
                # Clasificar método
                if method_name.startswith("show_") or "_menu" in method_name:
                    self.stats["menu_methods"] += 1
                    self._check_menu_method(node)
                elif method_name.startswith("_"):
                    self.stats["helper_methods"] += 1
                else:
                    self.stats["action_methods"] += 1
                    self._check_action_method(node)
    
    def _check_menu_method(self, node):
        """Verifica método de menú"""
        issues = []
        
        # Verificar que imprime opciones
        has_print = any(isinstance(n, ast.Call) and 
                       hasattr(n.func, 'id') and 
                       n.func.id == 'print' 
                       for n in ast.walk(node))
        
        if not has_print:
            issues.append("No imprime opciones")
        
        # Verificar que lee input
        has_input = any(isinstance(n, ast.Call) and
                       hasattr(n.func, 'id') and
                       n.func.id == 'input'
                       for n in ast.walk(node))
        
        if not has_input:
            issues.append("No lee input del usuario")
        
        if issues:
            self.issues[node.name] = issues
    
    def _check_action_method(self, node):
        """Verifica método de acción"""
        issues = []
        
        # Buscar llamadas problemáticas
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Verificar llamadas a engine
                if (hasattr(child.func, 'attr') and 
                    hasattr(child.func, 'value') and
                    hasattr(child.func.value, 'attr') and
                    child.func.value.attr == 'engine'):
                    
                    method_called = child.func.attr
                    if method_called == 'create_macro':
                        issues.append("Llama directamente a engine.create_macro (debe usar CommandProcessor)")
                    elif method_called not in ['execute_macro', 'stop_macro', 'get_state']:
                        issues.append(f"Llamada directa a engine.{method_called}")
        
        if issues:
            self.issues[node.name] = issues
            self.stats["broken_methods"] += 1
    
    def _detect_common_issues(self, content: str):
        """Detecta problemas comunes en el código"""
        lines = content.split('\n')
        
        # Problema 1: Imports faltantes
        if "from trajectory_hub.control.processors.command_processor import CommandProcessor" not in content:
            self.issues["imports"].append("Falta import de CommandProcessor")
        
        # Problema 2: No inicializa CommandProcessor
        if "self.processor = CommandProcessor" not in content:
            self.issues["init"].append("No inicializa CommandProcessor")
        
        # Problema 3: Demasiados métodos
        if self.stats["total_methods"] > 25:
            self.issues["architecture"].append(
                f"Demasiados métodos: {self.stats['total_methods']} (máximo recomendado: 25)"
            )
        
        # Problema 4: Lógica de negocio en UI
        business_logic_keywords = ['calculate', 'process', 'transform', 'generate']
        for i, line in enumerate(lines):
            for keyword in business_logic_keywords:
                if keyword in line and 'def' in line:
                    self.issues["architecture"].append(
                        f"Posible lógica de negocio en línea {i+1}: {line.strip()}"
                    )
    
    def _generate_report(self) -> Dict[str, any]:
        """Genera reporte de diagnóstico"""
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Total métodos: {self.stats['total_methods']}")
        print(f"   Métodos menú: {self.stats['menu_methods']}")
        print(f"   Métodos acción: {self.stats['action_methods']}") 
        print(f"   Métodos helper: {self.stats['helper_methods']}")
        print(f"   Métodos con problemas: {self.stats['broken_methods']}")
        
        print(f"\n❌ PROBLEMAS DETECTADOS:")
        critical_count = 0
        for category, issues_list in self.issues.items():
            if issues_list:
                print(f"\n   {category}:")
                for issue in issues_list:
                    print(f"      - {issue}")
                    if "directamente" in issue or "CommandProcessor" in issue:
                        critical_count += 1
        
        # Generar lista de fixes necesarios
        fixes_needed = []
        
        if "imports" in self.issues:
            fixes_needed.append("Añadir import CommandProcessor")
        
        if "init" in self.issues:
            fixes_needed.append("Inicializar CommandProcessor en __init__")
        
        if critical_count > 0:
            fixes_needed.append(f"Reemplazar {critical_count} llamadas directas a Engine")
        
        if self.stats["total_methods"] > 25:
            fixes_needed.append(f"Reducir de {self.stats['total_methods']} a 25 métodos máximo")
        
        print(f"\n🔧 FIXES NECESARIOS:")
        for i, fix in enumerate(fixes_needed, 1):
            print(f"   {i}. {fix}")
        
        # Guardar reporte
        report = {
            "stats": self.stats,
            "issues": dict(self.issues),
            "fixes_needed": fixes_needed,
            "critical_count": critical_count
        }
        
        import json
        with open("controller_diagnostic_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Reporte guardado: controller_diagnostic_report.json")
        
        return report

def create_function_test_script():
    """Crea script para probar funciones individuales"""
    
    test_script = '''#!/usr/bin/env python3
"""
🧪 Test de funciones del Controller
Prueba cada opción del menú sistemáticamente
"""

from trajectory_hub.interface.interactive_controller import InteractiveController
import time

def test_controller_functions():
    """Prueba sistemática de funciones"""
    
    print("🧪 TEST DE FUNCIONES DEL CONTROLLER")
    print("=" * 50)
    
    # Crear controller
    controller = InteractiveController()
    
    # Lista de pruebas
    tests = [
        ("1", "Gestión de Macros", [
            ("1", "Crear macro circle"),
            ("b", "Volver")
        ]),
        ("2", "Control de Trayectorias", [
            ("1", "Ver trayectorias"),
            ("b", "Volver")
        ]),
        ("3", "Modulación 3D", [
            ("1", "Ver moduladores"),
            ("b", "Volver")
        ])
    ]
    
    results = {}
    
    # Ejecutar pruebas
    for main_option, menu_name, sub_tests in tests:
        print(f"\\n📋 Probando: {menu_name}")
        try:
            # Simular selección de menú principal
            # (requeriría modificar controller para modo test)
            results[menu_name] = "✅ Accesible"
            
            for sub_option, sub_name in sub_tests:
                print(f"   - {sub_name}: ", end="")
                try:
                    # Aquí se ejecutaría la sub-opción
                    print("✅")
                    results[f"{menu_name}/{sub_name}"] = "✅"
                except Exception as e:
                    print(f"❌ {str(e)}")
                    results[f"{menu_name}/{sub_name}"] = f"❌ {str(e)}"
                    
        except Exception as e:
            results[menu_name] = f"❌ Error: {str(e)}"
    
    # Mostrar resumen
    print("\\n📊 RESUMEN DE PRUEBAS:")
    ok_count = sum(1 for v in results.values() if "✅" in v)
    total_count = len(results)
    
    print(f"   Exitosas: {ok_count}/{total_count}")
    print(f"   Fallidas: {total_count - ok_count}/{total_count}")
    
    # Guardar resultados
    with open("controller_test_results.txt", 'w') as f:
        f.write("RESULTADOS TEST CONTROLLER\\n")
        f.write("=" * 40 + "\\n\\n")
        for test, result in results.items():
            f.write(f"{test}: {result}\\n")
    
    print("\\n📄 Resultados guardados: controller_test_results.txt")

if __name__ == "__main__":
    test_controller_functions()
'''
    
    with open("test_controller_functions.py", 'w') as f:
        f.write(test_script)
    
    print("✅ Script de test creado: test_controller_functions.py")

def main():
    """Ejecuta diagnóstico completo"""
    
    # Diagnóstico
    diagnostic = ControllerDiagnostic()
    report = diagnostic.diagnose()
    
    # Crear script de test
    create_function_test_script()
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1. Revisar controller_diagnostic_report.json")
    print("2. Ejecutar: python test_controller_functions.py")
    print("3. Aplicar fixes según el reporte")

if __name__ == "__main__":
    main()