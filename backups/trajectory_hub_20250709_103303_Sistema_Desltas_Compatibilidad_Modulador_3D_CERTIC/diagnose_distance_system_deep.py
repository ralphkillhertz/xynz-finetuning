# === diagnose_distance_system_deep.py ===
# 🔍 Búsqueda exhaustiva del sistema de control de distancias
# ⚡ Rastrea el sistema de radio/proximidad/agrupamiento

import os
import re
import ast
from trajectory_hub.core import EnhancedTrajectoryEngine

def deep_distance_search():
    """Búsqueda exhaustiva del sistema de control de distancias"""
    
    print("🔍 BÚSQUEDA PROFUNDA - SISTEMA DE CONTROL DE DISTANCIAS")
    print("=" * 70)
    print("Buscando: control de radio, proximidad, agrupamiento, distancia al listener")
    print("=" * 70)
    
    # 1. Buscar en TODOS los archivos del proyecto
    print("\n1️⃣ RASTREANDO EN TODOS LOS ARCHIVOS...")
    
    search_terms = [
        'distance_control', 'distance_mode', 'distance_range',
        'set_distance', 'adjust_distance', 'control_distance',
        'proximity', 'radius', 'spacing', 'spread',
        'convergent', 'divergent', 'breathing',
        'listener', 'dispersion', 'grouping',
        'perceptual', 'physical', 'range_min', 'range_max'
    ]
    
    results = {}
    
    # Buscar en todos los archivos Python
    for root, dirs, files in os.walk('trajectory_hub'):
        # Saltar carpetas de backup
        if '__pycache__' in root or 'backup' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Buscar cada término
                    file_matches = []
                    for term in search_terms:
                        if term in content.lower():
                            # Buscar líneas específicas
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if term in line.lower():
                                    file_matches.append({
                                        'term': term,
                                        'line_num': i + 1,
                                        'line': line.strip()[:100]
                                    })
                    
                    if file_matches:
                        results[filepath] = file_matches
                
                except:
                    pass
    
    # Mostrar resultados organizados
    print("\n📋 RESULTADOS POR ARCHIVO:")
    
    for filepath, matches in results.items():
        if 'backup' not in filepath:  # Filtrar backups
            print(f"\n📄 {filepath}")
            
            # Agrupar por tipo de función
            methods = [m for m in matches if 'def ' in m['line']]
            calls = [m for m in matches if '(' in m['line'] and 'def ' not in m['line']]
            attrs = [m for m in matches if '=' in m['line'] or ':' in m['line']]
            
            if methods:
                print("   🔧 Métodos:")
                for m in methods[:5]:
                    print(f"      L{m['line_num']}: {m['line']}")
            
            if calls:
                print("   📞 Llamadas:")
                for c in calls[:3]:
                    print(f"      L{c['line_num']}: {c['line']}")
            
            if attrs:
                print("   📦 Atributos:")
                for a in attrs[:3]:
                    print(f"      L{a['line_num']}: {a['line']}")
    
    # 2. Buscar específicamente en distance_controller.py
    print("\n\n2️⃣ ANÁLISIS DE distance_controller.py...")
    
    dc_file = "trajectory_hub/core/distance_controller.py"
    if os.path.exists(dc_file):
        with open(dc_file, 'r') as f:
            dc_content = f.read()
        
        # Buscar clases principales
        classes = re.findall(r'class\s+(\w+).*?:\s*\n(.*?)(?=\nclass|\Z)', dc_content, re.DOTALL)
        
        for class_name, class_body in classes:
            print(f"\n   📦 Clase: {class_name}")
            
            # Buscar métodos
            methods = re.findall(r'def\s+(\w+)\s*\([^)]*\):', class_body)
            public_methods = [m for m in methods if not m.startswith('_')]
            
            print(f"      Métodos públicos: {public_methods}")
            
            # Buscar parámetros importantes
            if 'mode' in class_body:
                modes = re.findall(r'mode["\']?\s*[:=]\s*["\'](\w+)["\']', class_body)
                if modes:
                    print(f"      Modos encontrados: {list(set(modes))}")
    
    # 3. Ver cómo se conecta con el engine
    print("\n\n3️⃣ BUSCANDO INTEGRACIÓN CON ENGINE...")
    
    engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
    with open(engine_file, 'r') as f:
        engine_content = f.read()
    
    # Buscar importación de distance_controller
    if 'distance_controller' in engine_content.lower():
        print("   ✅ distance_controller está importado en engine")
        
        # Buscar dónde se usa
        import_match = re.search(r'from.*distance_controller.*import\s+(\w+)', engine_content)
        if import_match:
            imported_class = import_match.group(1)
            print(f"   📦 Importa: {imported_class}")
            
            # Buscar instanciación
            instance_match = re.search(rf'self\.(\w+)\s*=\s*{imported_class}', engine_content)
            if instance_match:
                instance_name = instance_match.group(1)
                print(f"   🔧 Instancia como: self.{instance_name}")
                
                # Buscar métodos que usen esta instancia
                usage_pattern = rf'self\.{instance_name}\.(\w+)'
                usages = re.findall(usage_pattern, engine_content)
                if usages:
                    print(f"   📞 Métodos usados: {list(set(usages))}")
    
    # 4. Verificar si está en __init__
    print("\n\n4️⃣ VERIFICANDO EN __init__ DEL ENGINE...")
    
    # Buscar en __init__
    init_match = re.search(r'def __init__.*?(?=\n    def|\Z)', engine_content, re.DOTALL)
    if init_match:
        init_body = init_match.group(0)
        
        # Buscar distance en init
        if 'distance' in init_body.lower():
            distance_lines = [line.strip() for line in init_body.split('\n') 
                            if 'distance' in line.lower()]
            
            print("   📋 Referencias a 'distance' en __init__:")
            for line in distance_lines[:5]:
                print(f"      {line}")
    
    # 5. Propuesta de solución
    print("\n\n5️⃣ PROPUESTA DE INTEGRACIÓN...")
    
    print("""
   🔧 PARECE QUE EL SISTEMA EXISTE PERO NO ESTÁ EXPUESTO
   
   Posibles soluciones:
   
   1. Añadir método wrapper en engine:
      def set_distance_control(self, macro_name, mode, **kwargs):
          if hasattr(self, 'distance_controller'):
              return self.distance_controller.adjust_macro_distance(...)
   
   2. O usar directamente el distance_controller:
      engine.distance_controller.adjust_macro_distance(...)
   
   3. O verificar si hay otro método que haga esto
   """)

if __name__ == "__main__":
    deep_distance_search()