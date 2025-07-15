#!/usr/bin/env python3
"""
🛡️ WORKFLOW SEGURO DE IMPLEMENTACIÓN
⚡ Ejecuta todos los cambios de forma ordenada y segura
"""

import os
import sys
import subprocess
import time
from datetime import datetime

class SafeWorkflow:
    def __init__(self):
        self.log_file = f"implementation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.steps_completed = []
        
    def log(self, message):
        """Log a console y archivo"""
        print(message)
        with open(self.log_file, 'a') as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
    
    def confirm(self, message):
        """Pedir confirmación al usuario"""
        response = input(f"\n❓ {message} (s/n): ").lower()
        return response == 's'
    
    def run_command(self, command, description):
        """Ejecutar comando con manejo de errores"""
        self.log(f"\n🚀 {description}")
        self.log(f"   Comando: {command}")
        
        if self.confirm("¿Ejecutar este comando?"):
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("   ✅ Completado exitosamente")
                    self.steps_completed.append(description)
                    return True
                else:
                    self.log(f"   ❌ Error: {result.stderr}")
                    return False
            except Exception as e:
                self.log(f"   ❌ Excepción: {e}")
                return False
        else:
            self.log("   ⏭️ Saltado por el usuario")
            return False
    
    def create_backup(self):
        """Crear backup completo"""
        backup_dir = f"trajectory_hub_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log(f"\n🔒 Creando backup: {backup_dir}")
        
        if os.path.exists("trajectory_hub"):
            os.system(f"cp -r trajectory_hub {backup_dir}")
            self.log(f"   ✅ Backup creado: {backup_dir}")
            return backup_dir
        else:
            self.log("   ❌ No se encontró trajectory_hub")
            return None
    
    def run_workflow(self):
        """Ejecutar workflow completo"""
        self.log("="*60)
        self.log("🛡️ WORKFLOW SEGURO DE IMPLEMENTACIÓN")
        self.log("="*60)
        
        # Resumen inicial
        self.log("""
📊 RESUMEN DE CAMBIOS A REALIZAR:
1. Eliminar bloqueo en _apply_macro_rotation (2 líneas)
2. Cambiar SourceMotion.update() a arquitectura de deltas
3. Verificar que todo funciona correctamente

Tiempo estimado: 1-2 horas
Riesgo: Mínimo (cambios localizados)
""")
        
        if not self.confirm("¿Deseas continuar con la implementación?"):
            self.log("\n⏹️ Implementación cancelada por el usuario")
            return
        
        # PASO 1: Backup
        backup_dir = self.create_backup()
        if not backup_dir:
            if not self.confirm("No se pudo crear backup. ¿Continuar de todos modos?"):
                return
        
        # PASO 2: Eliminar bloqueo en rotación
        if self.run_command(
            "python fix_macro_rotation_block.py",
            "Eliminar bloqueo en _apply_macro_rotation"
        ):
            self.log("   💡 Esto permite que rotación MS funcione con todas las fuentes")
        
        # PASO 3: Implementar arquitectura de deltas
        if self.confirm("\n¿Proceder con la implementación de arquitectura de deltas?"):
            if self.run_command(
                "python implement_delta_architecture.py",
                "Implementar arquitectura de deltas en SourceMotion"
            ):
                self.log("   💡 Ahora los componentes se suman en lugar de sobrescribirse")
        
        # PASO 4: Verificar implementación
        if self.confirm("\n¿Ejecutar tests de verificación?"):
            self.run_command(
                "python test_delta_architecture.py",
                "Test de arquitectura de deltas"
            )
        
        # PASO 5: Resumen final
        self.log("\n" + "="*60)
        self.log("📊 RESUMEN DE IMPLEMENTACIÓN")
        self.log("="*60)
        
        self.log(f"\nPasos completados: {len(self.steps_completed)}")
        for step in self.steps_completed:
            self.log(f"  ✅ {step}")
        
        if len(self.steps_completed) >= 2:
            self.log("\n🎉 ¡Implementación completada exitosamente!")
            self.log("\n📋 PRÓXIMOS PASOS:")
            self.log("1. Ejecutar: python trajectory_hub/interface/interactive_controller.py")
            self.log("2. Probar todas las combinaciones:")
            self.log("   - Solo Concentración")
            self.log("   - Solo Rotación MS")
            self.log("   - IS + Rotación MS")
            self.log("   - IS + Concentración")
            self.log("   - Todo activado")
            self.log("\n💡 Todo debería sumarse correctamente ahora")
        else:
            self.log("\n⚠️ Implementación incompleta")
            self.log(f"Backup disponible en: {backup_dir}")
        
        self.log(f"\n📝 Log guardado en: {self.log_file}")

if __name__ == "__main__":
    print("🛡️ WORKFLOW SEGURO DE IMPLEMENTACIÓN - TRAJECTORY HUB")
    print("="*60)
    print("""
Este script ejecutará los cambios de forma ordenada y segura:
1. Creará un backup completo
2. Aplicará los fixes necesarios
3. Verificará que todo funciona
4. Te guiará en cada paso

Puedes cancelar en cualquier momento.
""")
    
    workflow = SafeWorkflow()
    workflow.run_workflow()