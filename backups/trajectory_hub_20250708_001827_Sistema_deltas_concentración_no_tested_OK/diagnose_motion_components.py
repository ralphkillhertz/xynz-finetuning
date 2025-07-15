#!/usr/bin/env python3
"""
🔧 Diagnóstico: Análisis completo de motion_components.py
⚡ Objetivo: Identificar TODOS los problemas
🎯 Solución: Proponer fix completo o reconstrucción
"""

import ast
import re

def diagnose_file():
    """Diagnóstico completo del archivo"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("🔍 DIAGNÓSTICO COMPLETO DE MOTION_COMPONENTS.PY\n")
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    print(f"📊 Estadísticas del archivo:")
    print(f"   Total líneas: {len(lines)}")
    
    # 1. Buscar errores de sintaxis
    print("\n1️⃣ Análisis de sintaxis:")
    syntax_errors = []
    
    try:
        with open(motion_file, 'r') as f:
            content = f.read()
        ast.parse(content)
        print("   ✅ No hay errores de sintaxis detectados por AST")
    except SyntaxError as e:
        print(f"   ❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
        syntax_errors.append((e.lineno, e.msg))
        
        # Intentar encontrar más errores
        current_line = e.lineno
        while current_line < len(lines):
            try:
                # Parsear desde la siguiente línea
                partial_content = '\n'.join(lines[current_line:])
                ast.parse(partial_content)
                break
            except SyntaxError as e2:
                actual_line = current_line + e2.lineno
                print(f"   ❌ Error adicional en línea {actual_line}: {e2.msg}")
                syntax_errors.append((actual_line, e2.msg))
                current_line = actual_line
    
    # 2. Análisis de indentación
    print("\n2️⃣ Análisis de indentación:")
    indentation_issues = []
    
    expected_indent = 0
    class_indent = 0
    in_class = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
            
        actual_indent = len(line) - len(line.lstrip())
        
        # Detectar clases
        if stripped.startswith('class '):
            in_class = True
            class_indent = actual_indent
            expected_indent = class_indent + 4
            
        # Detectar métodos
        elif stripped.startswith('def ') and in_class:
            if actual_indent != class_indent + 4:
                indentation_issues.append((i+1, f"Método con indentación incorrecta: {actual_indent} en vez de {class_indent + 4}"))
                
        # Detectar fin de bloque
        elif actual_indent < class_indent and in_class:
            in_class = False
    
    if indentation_issues:
        print(f"   ❌ {len(indentation_issues)} problemas de indentación encontrados:")
        for line_num, issue in indentation_issues[:5]:  # Mostrar solo los primeros 5
            print(f"      Línea {line_num}: {issue}")
        if len(indentation_issues) > 5:
            print(f"      ... y {len(indentation_issues) - 5} más")
    else:
        print("   ✅ No se detectaron problemas obvios de indentación")
    
    # 3. Buscar bloques problemáticos
    print("\n3️⃣ Bloques problemáticos:")
    
    # Buscar líneas alrededor del error reportado (línea 106)
    error_line = 105  # índice
    print(f"\n   Contexto alrededor de línea 106:")
    for i in range(max(0, error_line - 10), min(len(lines), error_line + 5)):
        marker = ">>>" if i == error_line else "   "
        print(f"   {marker} {i+1}: {repr(lines[i][:60])}")
    
    # 4. Buscar patrones problemáticos
    print("\n4️⃣ Patrones problemáticos:")
    
    # Docstrings mal ubicados
    docstring_issues = 0
    for i in range(len(lines) - 1):
        if lines[i].strip().endswith(':') and lines[i+1].strip().startswith('"""'):
            # Verificar indentación
            expected = len(lines[i]) - len(lines[i].lstrip()) + 4
            actual = len(lines[i+1]) - len(lines[i+1].lstrip())
            if actual != expected:
                docstring_issues += 1
    
    if docstring_issues > 0:
        print(f"   ⚠️ {docstring_issues} docstrings con indentación incorrecta")
    
    # 5. Proponer solución
    print("\n5️⃣ PROPUESTA DE SOLUCIÓN:")
    
    if syntax_errors:
        print("\n   🔴 Errores críticos de sintaxis detectados")
        print("   Recomendación: Reconstruir las clases problemáticas")
        
        # Identificar qué clases tienen problemas
        problematic_classes = set()
        for line_num, _ in syntax_errors:
            # Buscar la clase más cercana
            for i in range(line_num - 1, -1, -1):
                if lines[i].strip().startswith('class '):
                    class_name = lines[i].strip().split()[1].rstrip(':')
                    problematic_classes.add(class_name)
                    break
        
        if problematic_classes:
            print(f"   Clases afectadas: {', '.join(problematic_classes)}")
            
            if 'OrientationModulation' in problematic_classes:
                print("\n   ⚡ OrientationModulation necesita reconstrucción")
            if 'ConcentrationComponent' in problematic_classes:
                print("   ⚡ ConcentrationComponent necesita reconstrucción")
        
        return True  # Necesita reconstrucción
    
    return False  # Se puede arreglar

def create_reconstruction_script():
    """Crea script para reconstruir las clases problemáticas"""
    
    script = '''#!/usr/bin/env python3
"""
🔧 Reconstrucción: Rebuild de clases problemáticas
⚡ Objetivo: Reemplazar clases corruptas con versiones limpias
🎯 Foco: OrientationModulation y ConcentrationComponent
"""

def rebuild_orientation_modulation():
    """Reconstruye la clase OrientationModulation"""
    
    code = """
class OrientationModulation(MotionComponent):
    \"\"\"Modulación de orientación con formas predefinidas\"\"\"
    
    def __init__(self):
        super().__init__()
        self.yaw_func = None
        self.pitch_func = None
        self.roll_func = None
        self.aperture_func = None
        self.time = 0.0
        
    def set_functions(self, 
                      yaw: Optional[Callable] = None,
                      pitch: Optional[Callable] = None,
                      roll: Optional[Callable] = None):
        \"\"\"Configurar funciones de modulación\"\"\"
        if yaw:
            self.yaw_func = yaw
        if pitch:
            self.pitch_func = pitch
        if roll:
            self.roll_func = roll
            
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        \"\"\"Actualizar orientación\"\"\"
        self.time += dt
        
        if self.yaw_func:
            state.orientation[2] = self.yaw_func(self.time)
        if self.pitch_func:
            state.orientation[0] = self.pitch_func(self.time)
        if self.roll_func:
            state.orientation[1] = self.roll_func(self.time)
            
        return state
"""
    return code

def rebuild_concentration_component():
    """Reconstruye ConcentrationComponent con sistema de deltas"""
    
    code = """
class ConcentrationComponent(MotionComponent):
    \"\"\"Componente para concentrar/dispersar fuentes\"\"\"
    
    def __init__(self, macro=None):
        super().__init__()
        self.macro = macro
        self.concentration_factor = 0.0
        self.enabled = False
        self.macro_center = np.zeros(3)
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        \"\"\"Calcula delta para concentración\"\"\"
        if not self.enabled or self.concentration_factor == 0:
            return MotionDelta(source="concentration")
        
        # Calcular centro
        center = self.macro_center
        
        # Vector hacia el centro
        to_center = center - state.position
        distance = np.linalg.norm(to_center)
        
        if distance > 0.001:
            direction = to_center / distance
            movement = direction * distance * self.concentration_factor * dt
            
            return MotionDelta(
                position=movement,
                weight=abs(self.concentration_factor),
                source="concentration"
            )
        
        return MotionDelta(source="concentration")
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        \"\"\"Versión legacy - actualiza estado directamente\"\"\"
        if not self.enabled or self.concentration_factor == 0:
            return state
            
        delta = self.calculate_delta(state, current_time, dt)
        state.position += delta.position
        
        return state
        
    def set_factor(self, factor: float):
        \"\"\"Establecer factor de concentración\"\"\"
        self.concentration_factor = max(0.0, min(1.0, factor))
        
    def update_macro_center(self, positions: List[np.ndarray]):
        \"\"\"Actualizar centro del macro\"\"\"
        if positions:
            self.macro_center = np.mean(positions, axis=0)
"""
    return code

if __name__ == "__main__":
    print("🔧 SCRIPTS DE RECONSTRUCCIÓN GENERADOS")
    
    with open("rebuild_classes.py", "w") as f:
        f.write(__doc__)
        f.write("\\n\\n")
        f.write("# CÓDIGO PARA REEMPLAZAR:\\n\\n")
        f.write(rebuild_orientation_modulation())
        f.write("\\n\\n")
        f.write(rebuild_concentration_component())
    
    print("✅ Archivo creado: rebuild_classes.py")
    print("\\nPasos siguientes:")
    print("1. Revisar rebuild_classes.py")
    print("2. Reemplazar las clases problemáticas manualmente")
    print("3. O usar un script automatizado para el reemplazo")
'''
    
    with open("create_rebuild_script.py", 'w') as f:
        f.write(script)
    
    print("\n✅ Script de reconstrucción creado: create_rebuild_script.py")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 DIAGNÓSTICO COMPLETO DE MOTION_COMPONENTS")
    print("=" * 60)
    
    needs_rebuild = diagnose_file()
    
    if needs_rebuild:
        print("\n🔴 CONCLUSIÓN: El archivo necesita reconstrucción parcial")
        create_reconstruction_script()
        
        print("\n📋 PASOS RECOMENDADOS:")
        print("1. Ejecutar: python create_rebuild_script.py")
        print("2. Revisar el código generado")
        print("3. Reemplazar las clases problemáticas")
        print("4. Probar nuevamente")
    else:
        print("\n🟡 CONCLUSIÓN: Se puede intentar arreglar con fixes menores")
        print("\n📋 Alternativa: Restaurar desde backup")
        print("$ ls trajectory_hub/core/motion_components.py.backup*")