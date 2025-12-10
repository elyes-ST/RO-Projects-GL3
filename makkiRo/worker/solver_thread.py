from PyQt5.QtCore import QThread, pyqtSignal
from models.shortest_path import solve_shortest_path

class SolverThread(QThread):
    result_ready = pyqtSignal(float, list, dict)  # obj, edges, details
    log = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, nodes, edges, source, target, checkpoints):
        super().__init__()
        self.nodes = nodes
        self.edges = edges
        self.source = source
        self.target = target
        self.checkpoints = checkpoints
        self._stop_requested = False

    def request_stop(self):
        self._stop_requested = True
        self.log.emit('Arrêt demandé...')

    def run(self):
        self.log.emit('Démarrage du solveur Gurobi...')
        try:
            obj, chosen_edges, details = solve_shortest_path(
                self.nodes, 
                self.edges, 
                self.source, 
                self.target, 
                self.checkpoints, 
                stop_flag=lambda: self._stop_requested, 
                log=self.log
            )
            
            if self._stop_requested:
                self.log.emit('Solveur arrêté par l\'utilisateur')
                return
                
            self.result_ready.emit(obj, chosen_edges, details)
            self.log.emit('✓ Résolution terminée avec succès')
            
        except Exception as e:
            self.error.emit(str(e))
            self.log.emit(f'✗ Erreur: {e}')
