"""
Sistema de funciones personalizadas para movimiento
Permite definir movimientos complejos mediante expresiones matemáticas
"""

import numpy as np
import ast
import operator
from typing import Dict, Callable, Optional, Any, Tuple
import math

class SafeMathParser:
    """Parser seguro para expresiones matemáticas"""
    
    # Operadores permitidos
    ALLOWED_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Funciones matemáticas permitidas
    ALLOWED_FUNCTIONS = {
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'exp': np.exp,
        'log': np.log,
        'sqrt': np.sqrt,
        'abs': abs,
        'min': min,
        'max': max,
        'pi': math.pi,
        'e': math.e,
    }
    
    def __init__(self):
        self.variables = {}
    
    def parse(self, expression: str, variables: Dict[str, float]) -> float:
        """
        Parsea y evalúa una expresión matemática de forma segura
        
        Parameters
        ----------
        expression : str
            Expresión matemática a evaluar
        variables : dict
            Variables disponibles para la expresión
            
        Returns
        -------
        float
            Resultado de la evaluación
        """
        self.variables = variables
        
        try:
            # Parse la expresión
            tree = ast.parse(expression, mode='eval')
            
            # Validar que solo contiene operaciones permitidas
            self._validate_ast(tree)
            
            # Evaluar
            return self._eval_node(tree.body)
            
        except Exception as e:
            raise ValueError(f"Error evaluando expresión: {str(e)}")
    
    def _validate_ast(self, node):
        """Valida recursivamente que el AST solo contiene operaciones permitidas"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if not (isinstance(child.func, ast.Name) and 
                       child.func.id in self.ALLOWED_FUNCTIONS):
                    raise ValueError(f"Función no permitida: {ast.dump(child.func)}")
            elif isinstance(child, (ast.Import, ast.ImportFrom, ast.FunctionDef, 
                                  ast.ClassDef, ast.For, ast.While, ast.If)):
                raise ValueError(f"Construcción no permitida: {type(child).__name__}")
    
    def _eval_node(self, node):
        """Evalúa recursivamente un nodo del AST"""
        if isinstance(node, ast.Constant):
            return node.value
            
        elif isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id]
            elif node.id in self.ALLOWED_FUNCTIONS:
                return self.ALLOWED_FUNCTIONS[node.id]
            else:
                raise ValueError(f"Variable no definida: {node.id}")
                
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_func = self.ALLOWED_OPS.get(type(node.op))
            if op_func:
                return op_func(left, right)
            else:
                raise ValueError(f"Operador no permitido: {type(node.op).__name__}")
                
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_func = self.ALLOWED_OPS.get(type(node.op))
            if op_func:
                return op_func(operand)
            else:
                raise ValueError(f"Operador unario no permitido: {type(node.op).__name__}")
                
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.ALLOWED_FUNCTIONS:
                func = self.ALLOWED_FUNCTIONS[node.func.id]
                args = [self._eval_node(arg) for arg in node.args]
                return func(*args)
            else:
                raise ValueError(f"Llamada a función no permitida")
                
        else:
            raise ValueError(f"Tipo de nodo no soportado: {type(node).__name__}")


class CustomMotionFunction:
    """Función de movimiento personalizada definida por el usuario"""
    
    def __init__(self, name: str, expression_x: str, expression_y: str, expression_z: str,
                 description: str = "", parameters: Optional[Dict[str, float]] = None):
        """
        Crea una función de movimiento personalizada
        
        Parameters
        ----------
        name : str
            Nombre de la función
        expression_x, expression_y, expression_z : str
            Expresiones para cada componente del movimiento
        description : str
            Descripción de la función
        parameters : dict
            Parámetros adicionales con valores por defecto
        """
        self.name = name
        self.expression_x = expression_x
        self.expression_y = expression_y
        self.expression_z = expression_z
        self.description = description
        self.parameters = parameters or {}
        self.parser = SafeMathParser()
    
    def evaluate(self, t: float, **kwargs) -> np.ndarray:
        """
        Evalúa la función en el tiempo t
        
        Parameters
        ----------
        t : float
            Tiempo normalizado [0, 1] o tiempo en segundos
        **kwargs
            Parámetros adicionales para la evaluación
            
        Returns
        -------
        np.ndarray
            Vector [x, y, z] del movimiento
        """
        # Variables disponibles para las expresiones
        variables = {
            't': t,
            'time': t,
            'theta': t * 2 * np.pi,  # Ángulo en radianes
            'phase': t,
            **self.parameters,
            **kwargs
        }
        
        # Evaluar cada componente
        x = self.parser.parse(self.expression_x, variables)
        y = self.parser.parse(self.expression_y, variables)
        z = self.parser.parse(self.expression_z, variables)
        
        return np.array([x, y, z], dtype=np.float32)
    
    def preview(self, num_points: int = 100) -> np.ndarray:
        """
        Genera una previsualización del movimiento
        
        Returns
        -------
        np.ndarray
            Array de puntos (num_points, 3) representando la trayectoria
        """
        t_values = np.linspace(0, 1, num_points)
        points = []
        
        for t in t_values:
            try:
                point = self.evaluate(t)
                points.append(point)
            except:
                points.append(np.zeros(3))
                
        return np.array(points)


class MotionFunctionLibrary:
    """Biblioteca de funciones de movimiento predefinidas y personalizadas"""
    
    def __init__(self):
        self.functions = {}
        self._init_presets()
    
    def _init_presets(self):
        """Inicializa funciones de movimiento predefinidas"""
        
        # Estrella de 5 puntas
        self.add_function(CustomMotionFunction(
            name="star_5",
            expression_x="(1 + 0.3 * cos(5 * theta)) * cos(theta)",
            expression_y="(1 + 0.3 * cos(5 * theta)) * sin(theta)",
            expression_z="0",
            description="Estrella de 5 puntas en el plano XY"
        ))
        
        # Espiral 3D
        self.add_function(CustomMotionFunction(
            name="spiral_3d",
            expression_x="(1 - t) * cos(t * 6 * pi)",
            expression_y="(1 - t) * sin(t * 6 * pi)",
            expression_z="t * 2",
            description="Espiral ascendente en 3D"
        ))
        
        # Figura de Lissajous
        self.add_function(CustomMotionFunction(
            name="lissajous",
            expression_x="sin(3 * theta + pi/2)",
            expression_y="sin(2 * theta)",
            expression_z="0.5 * sin(4 * theta)",
            description="Figura de Lissajous 3D",
            parameters={"amplitude": 1.0}
        ))
        
        # Infinito (figura 8)
        self.add_function(CustomMotionFunction(
            name="infinity",
            expression_x="cos(theta)",
            expression_y="sin(2 * theta) / 2",
            expression_z="0",
            description="Símbolo de infinito en el plano XY"
        ))
        
        # Mariposa
        self.add_function(CustomMotionFunction(
            name="butterfly",
            expression_x="sin(theta) * (exp(cos(theta)) - 2 * cos(4 * theta))",
            expression_y="cos(theta) * (exp(cos(theta)) - 2 * cos(4 * theta))",
            expression_z="0",
            description="Curva de mariposa"
        ))
        
        # Hélice toroidal
        self.add_function(CustomMotionFunction(
            name="toroidal_helix",
            expression_x="(2 + cos(8 * theta)) * cos(theta)",
            expression_y="(2 + cos(8 * theta)) * sin(theta)",
            expression_z="sin(8 * theta)",
            description="Hélice sobre un toro"
        ))
        
        # Rosa de 4 pétalos
        self.add_function(CustomMotionFunction(
            name="rose_4",
            expression_x="cos(2 * theta) * cos(theta)",
            expression_y="cos(2 * theta) * sin(theta)",
            expression_z="0",
            description="Rosa de 4 pétalos"
        ))
        
        # Onda sinusoidal amortiguada
        self.add_function(CustomMotionFunction(
            name="damped_wave",
            expression_x="t * 4 - 2",
            expression_y="exp(-t * 2) * sin(t * 10 * pi)",
            expression_z="0",
            description="Onda sinusoidal con amortiguamiento exponencial"
        ))
    
    def add_function(self, function: CustomMotionFunction):
        """Añade una función a la biblioteca"""
        self.functions[function.name] = function
    
    def get_function(self, name: str) -> Optional[CustomMotionFunction]:
        """Obtiene una función por nombre"""
        return self.functions.get(name)
    
    def list_functions(self) -> Dict[str, str]:
        """Lista todas las funciones disponibles con sus descripciones"""
        return {name: func.description for name, func in self.functions.items()}
    
    def create_from_expression(self, name: str, expression: str, 
                              coordinate_system: str = "cartesian") -> CustomMotionFunction:
        """
        Crea una función desde una expresión simple
        
        Parameters
        ----------
        name : str
            Nombre de la función
        expression : str
            Expresión matemática (se aplicará a X e Y, Z será 0)
        coordinate_system : str
            'cartesian' o 'polar'
        """
        if coordinate_system == "polar":
            # Convertir expresión polar a cartesiana
            expr_x = f"({expression}) * cos(theta)"
            expr_y = f"({expression}) * sin(theta)"
            expr_z = "0"
        else:
            # Asumir movimiento circular modificado por la expresión
            expr_x = f"cos(theta) * ({expression})"
            expr_y = f"sin(theta) * ({expression})"
            expr_z = "0"
            
        return CustomMotionFunction(
            name=name,
            expression_x=expr_x,
            expression_y=expr_y,
            expression_z=expr_z,
            description=f"Función personalizada: {expression}"
        )


# Instancia global de la biblioteca
motion_library = MotionFunctionLibrary()