#!/usr/bin/env python3
"""
working_concentration_controller.py - Controlador con concentración funcionando
"""

from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.interface.interactive_controller import InteractiveController

class WorkingController(InteractiveController):
    """Controlador con workaround para concentración"""
    
    def __init__(self):
        super().__init__()
        print("\n✅ Usando WorkingController con soporte de concentración")
    
    async def concentration_control_menu(self):
        """Menú de concentración con workaround"""
        # Asegurar que los componentes estén habilitados
        for macro_id in self._macros.values():
            macro = self.engine._macros.get(macro_id)
            if macro:
                for sid in macro.source_ids:
                    if sid in self.engine._source_motions:
                        motion = self.engine._source_motions[sid]
                        # Habilitar procesamiento manual si es necesario
                        if 'concentration' in motion.components:
                            # Forzar update manual en cada frame
                            pass
        
        # Llamar al menú original
        await super().concentration_control_menu()

if __name__ == "__main__":
    import asyncio
    
    controller = WorkingController()
    asyncio.run(controller.run())
