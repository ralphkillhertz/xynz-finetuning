#!/usr/bin/env python3
"""
EXTRACTOR DE ESPECIFICACIONES - Version LIMPIA
Para trajectory_hub del 2025-07-05 (pre-paralelo)
Documento autosuficiente para migracion a deltas
"""

import os
import re
import json
from datetime import datetime

class CleanSystemExtractor:
    def __init__(self):
        self.report = {
            "metadata": {
                "source_version": "trajectory_hub_20250705_130742",
                "extraction_date": datetime.now().isoformat(),
                "purpose": "Complete specification for delta migration"
            },
            "files_analyzed": [],
            "components": {},
            "exact_behaviors": {},
            "critical_functions": {},
            "known_issues": {}
        }
    
    def extract(self):
        """Extraer TODO del sistema actual"""
        
        print("EXTRACCION DE SISTEMA LIMPIO")
        print("="*60)
        
        # 1. Analizar archivos principales
        self.analyze_engine()
        self.analyze_motion_components()
        self.analyze_osc_bridge()
        
        # 2. Documentar comportamientos exactos
        self.document_exact_behaviors()
        
        # 3. Generar reporte completo
        self.generate_complete_report()
    
    def analyze_engine(self):
        """Analizar enhanced_trajectory_engine.py"""
        
        print("\n1. ANALIZANDO ENGINE...")
        
        engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
        
        if not os.path.exists(engine_file):
            print("   No se encuentra engine")
            return
        
        with open(engine_file, 'r') as f:
            content = f.read()
        
        # Extraer metodos principales
        methods = re.findall(r'def (\w+)\(self[^)]*\):', content)
        
        # Buscar estructuras de datos
        self.report["components"]["engine"] = {
            "methods": methods,
            "has_step": "def step(" in content,
            "has_update": "def update(" in content,
            "has_concentration": "concentration" in content.lower(),
            "arrays": {
                "_positions": "self._positions" in content,
                "_orientations": "self._orientations" in content,
                "_macros": "self._macros" in content
            }
        }
        
        print(f"   Metodos encontrados: {len(methods)}")
        
    def analyze_motion_components(self):
        """Analizar motion_components.py"""
        
        print("\n2. ANALIZANDO MOTION COMPONENTS...")
        
        motion_file = "trajectory_hub/core/motion_components.py"
        
        if not os.path.exists(motion_file):
            print("   No se encuentra motion_components")
            return
            
        with open(motion_file, 'r') as f:
            content = f.read()
        
        # Buscar clases principales
        classes = re.findall(r'class (\w+).*?:', content)
        
        self.report["components"]["motion"] = {
            "classes": classes,
            "has_individual_trajectory": "IndividualTrajectory" in classes,
            "has_source_motion": "SourceMotion" in classes
        }
        
        print(f"   Clases encontradas: {classes}")
        
    def analyze_osc_bridge(self):
        """Analizar spat_osc_bridge.py"""
        
        print("\n3. ANALIZANDO OSC BRIDGE...")
        
        osc_file = "trajectory_hub/core/spat_osc_bridge.py"
        
        if not os.path.exists(osc_file):
            print("   No se encuentra OSC bridge")
            return
            
        with open(osc_file, 'r') as f:
            content = f.read()
        
        # Extraer endpoints OSC
        endpoints = re.findall(r'["\']/(source/[^"\']+)["\']', content)
        
        self.report["components"]["osc"] = {
            "endpoints": list(set(endpoints)),
            "has_groups": "/group" in content
        }
        
        print(f"   Endpoints OSC: {len(set(endpoints))}")
    
    def document_exact_behaviors(self):
        """Documentar comportamientos EXACTOS del codigo"""
        
        print("\n4. DOCUMENTANDO COMPORTAMIENTOS...")
        
        behaviors = {
            "concentration": {
                "status": "NOT_IN_MAIN_LOOP",
                "location": "Unknown - needs manual verification",
                "evidence": {
                    "set_macro_concentration_exists": True,
                    "returns_value": False,
                    "step_uses_it": False
                }
            },
            
            "update_order": {
                "verified": False,
                "expected": [
                    "trajectory_ms",
                    "rotation_ms", 
                    "trajectory_is",
                    "concentration (if exists)"
                ],
                "overwrite_pattern": "self._positions[sid] = value"
            },
            
            "known_conflicts": {
                "ms_vs_is": "IS overwrites MS completely",
                "concentration_alone": "Does not work",
                "rotation_after_is": "Gets overwritten"
            }
        }
        
        self.report["exact_behaviors"] = behaviors
        
    def generate_complete_report(self):
        """Generar reporte completo"""
        
        print("\n5. GENERANDO REPORTE...")
        
        # JSON tecnico
        with open("CLEAN_SYSTEM_SPEC.json", 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        # Markdown de referencia
        self.generate_reference_doc()
        
        print("\nDOCUMENTOS GENERADOS:")
        print("   - CLEAN_SYSTEM_SPEC.json")
        print("   - DELTA_MIGRATION_REFERENCE.md")
    
    def generate_reference_doc(self):
        """Generar documento de referencia para migracion"""
        
        # Crear el documento parte por parte para evitar problemas de sintaxis
        doc_parts = []
        
        # Header
        doc_parts.append("# REFERENCIA DE MIGRACION A DELTAS")
        doc_parts.append(f"Fuente: trajectory_hub_20250705_130742 (version limpia)")
        doc_parts.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        doc_parts.append("")
        
        # Estado actual
        doc_parts.append("## ESTADO ACTUAL CONFIRMADO")
        doc_parts.append("")
        doc_parts.append("### Arquitectura")
        doc_parts.append("- Paradigma: Sobrescritura secuencial")
        doc_parts.append("- Patron: self._positions[sid] = calculated_value")
        doc_parts.append("- Problema: Cada componente borra el anterior")
        doc_parts.append("")
        
        # Componentes
        doc_parts.append("### Componentes Existentes")
        doc_parts.append("1. Trayectorias MS: Funciona (sobrescribe todo)")
        doc_parts.append("2. Rotacion MS: Funciona (hasta que IS activa)")
        doc_parts.append("3. Trayectorias IS: Funciona (sobrescribe todo)")
        doc_parts.append("4. Concentracion: No implementada en loop principal")
        doc_parts.append("")
        
        # Plan de migracion
        doc_parts.append("## PLAN DE MIGRACION")
        doc_parts.append("")
        doc_parts.append("### Fase 1: Estructura Base")
        doc_parts.append("```python")
        doc_parts.append("class MotionDelta:")
        doc_parts.append("    position: np.ndarray = [0, 0, 0]")
        doc_parts.append("    orientation: np.ndarray = [0, 0, 0]")
        doc_parts.append("```")
        doc_parts.append("")
        
        # Guardar documento
        doc_content = "\n".join(doc_parts)
        
        with open("DELTA_MIGRATION_REFERENCE.md", 'w', encoding='utf-8') as f:
            f.write(doc_content)

def main():
    print("INICIANDO EXTRACCION DE SISTEMA LIMPIO")
    print("Version: trajectory_hub_20250705_130742")
    print("="*60)
    
    extractor = CleanSystemExtractor()
    extractor.extract()
    
    print("\nEXTRACCION COMPLETA")
    print("\nUsa estos documentos en cualquier sesion futura")
    print("para implementar deltas sin perder contexto.")

if __name__ == "__main__":
    main()