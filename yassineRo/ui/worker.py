from PyQt5.QtCore import QThread, pyqtSignal
from model.optimizer import TransportOptimizer


class OptimizationWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, nodes, arcs):
        super().__init__()
        self.nodes = nodes
        self.arcs = arcs
        self.optimizer = TransportOptimizer()

    def run(self):
        try:
            results = self.optimizer.solve(self.nodes, self.arcs)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))
