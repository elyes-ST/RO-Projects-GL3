from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QMessageBox,
    QHeaderView,
    QSplitter,
    QFrame,
    QGroupBox,
    QScrollArea,
    QProgressBar,
    QMenu,
    QAction,
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from ui.worker import OptimizationWorker
from ui.visualization import NetworkCanvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transport Network Optimizer")
        self.setWindowIcon(QIcon())  # Add icon if available
        self.resize(1400, 900)
        self.setMinimumSize(1500, 1100)

        self.nodes_data = []
        self.arcs_data = []

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("Transport Network Design Optimization")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont("Segoe UI", 16, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                margin-bottom: 10px;
                padding: 10px;
            }
        """)
        main_layout.addWidget(header_label)

        # Main content splitter
        content_splitter = QSplitter(Qt.Vertical)

        # Input section
        input_section = self.create_input_section()
        content_splitter.addWidget(input_section)

        # Results section
        results_section = self.create_results_section()
        content_splitter.addWidget(results_section)

        content_splitter.setSizes([400, 500])
        main_layout.addWidget(content_splitter)

        # Status bar
        self.create_status_bar()

        self.load_default_data()

    def create_input_section(self):
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setSpacing(20)

        # Nodes section
        nodes_group = QGroupBox("Network Nodes")
        nodes_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: rgba(33, 150, 243, 0.1);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #2196F3;
            }
        """)
        nodes_layout = QVBoxLayout(nodes_group)

        self.node_table = self.create_modern_table(["Node ID", "Supply/Demand"])
        self.node_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.node_table.customContextMenuRequested.connect(self.show_node_context_menu)

        button_layout = QHBoxLayout()
        self.add_node_btn = self.create_modern_button("Add Node", "#2196F3")
        self.add_node_btn.clicked.connect(self.add_node_row)
        self.add_node_btn.setToolTip("Add a new network node")

        self.delete_node_btn = self.create_modern_button("Delete Selected", "#f44336")
        self.delete_node_btn.clicked.connect(lambda: self.delete_selected_row(self.node_table))
        self.delete_node_btn.setToolTip("Delete selected node")

        button_layout.addWidget(self.add_node_btn)
        button_layout.addWidget(self.delete_node_btn)

        nodes_layout.addWidget(self.node_table)
        nodes_layout.addLayout(button_layout)

        # Arcs section
        arcs_group = QGroupBox("Possible Routes")
        arcs_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: rgba(255, 152, 0, 0.1);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #FF9800;
            }
        """)
        arcs_layout = QVBoxLayout(arcs_group)

        self.arc_table = self.create_modern_table(["From", "To", "Fixed Cost", "Var Cost", "Capacity"])
        self.arc_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.arc_table.customContextMenuRequested.connect(self.show_arc_context_menu)

        button_layout2 = QHBoxLayout()
        self.add_arc_btn = self.create_modern_button("Add Route", "#FF9800")
        self.add_arc_btn.clicked.connect(self.add_arc_row)
        self.add_arc_btn.setToolTip("Add a new possible route")

        self.delete_arc_btn = self.create_modern_button("Delete Selected", "#f44336")
        self.delete_arc_btn.clicked.connect(lambda: self.delete_selected_row(self.arc_table))
        self.delete_arc_btn.setToolTip("Delete selected route")

        button_layout2.addWidget(self.add_arc_btn)
        button_layout2.addWidget(self.delete_arc_btn)

        arcs_layout.addWidget(self.arc_table)
        arcs_layout.addLayout(button_layout2)

        input_layout.addWidget(nodes_group)
        input_layout.addWidget(arcs_group)

        return input_widget

    def create_results_section(self):
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)

        # Control buttons
        control_layout = QHBoxLayout()

        self.solve_btn = self.create_modern_button("Optimize Network", "#4CAF50", large=True)
        self.solve_btn.clicked.connect(self.run_optimization)
        self.solve_btn.setToolTip("Run optimization to find optimal network design")

        self.clear_btn = self.create_modern_button("Clear Data", "#f44336")
        self.clear_btn.clicked.connect(self.clear_data)
        self.clear_btn.setToolTip("Clear all input data")

        control_layout.addWidget(self.solve_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addStretch()

        results_layout.addLayout(control_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 8px;
                text-align: center;
                background-color: #2D2D2D;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #21CBF3);
                border-radius: 6px;
            }
        """)
        results_layout.addWidget(self.progress_bar)

        # Results display splitter
        results_splitter = QSplitter(Qt.Horizontal)

        # Visualization
        viz_group = QGroupBox("Network Visualization")
        viz_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9C27B0;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: rgba(156, 39, 176, 0.1);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #9C27B0;
            }
        """)
        viz_layout = QVBoxLayout(viz_group)
        self.canvas = NetworkCanvas(self, width=6, height=4, dpi=100)
        viz_layout.addWidget(self.canvas)
        results_splitter.addWidget(viz_group)

        # Results text
        results_group = QGroupBox("Optimization Results")
        results_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #607D8B;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: rgba(96, 125, 139, 0.1);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #607D8B;
            }
        """)
        results_layout_inner = QVBoxLayout(results_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2D2D2D;
                border-radius: 5px;
            }
        """)

        self.result_text = QLabel("Results will appear here after optimization...")
        self.result_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.result_text.setWordWrap(True)
        self.result_text.setStyleSheet("""
            QLabel {
                background-color: #2D2D2D;
                color: #FFFFFF;
                padding: 15px;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                line-height: 1.5;
            }
        """)

        scroll_area.setWidget(self.result_text)
        results_layout_inner.addWidget(scroll_area)

        results_splitter.addWidget(results_group)
        results_splitter.setSizes([600, 400])

        results_layout.addWidget(results_splitter)

        return results_widget

    def create_modern_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #555;
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #555;
                border-radius: 8px;
                selection-background-color: #2196F3;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
                border-right: 1px solid #444;
            }
            QTableWidget::item:selected {
                background-color: rgba(33, 150, 243, 0.3);
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #424242;
                color: #FFFFFF;
                padding: 10px;
                border: 1px solid #555;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #424242;
                border: 1px solid #555;
            }
        """)
        table.setMinimumHeight(250)
        return table

    def create_modern_button(self, text, color, large=False):
        btn = QPushButton(text)
        size = 14 if large else 12
        btn.setFont(QFont("Segoe UI", size, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: {"15px 30px" if large else "12px 24px"};
                font-weight: bold;
                min-width: {"180px" if large else "140px"};
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:disabled {{
                background-color: #666;
                color: #999;
            }}
        """)
        return btn

    def lighten_color(self, color):
        # Simple color lightening for hover effect
        if color == "#4CAF50":
            return "#66BB6A"
        elif color == "#FF9800":
            return "#FFB74D"
        elif color == "#f44336":
            return "#EF5350"
        elif color == "#2196F3":
            return "#42A5F5"
        elif color == "#9C27B0":
            return "#AB47BC"
        elif color == "#607D8B":
            return "#78909C"
        return color

    def darken_color(self, color):
        # Simple color darkening for pressed effect
        if color == "#4CAF50":
            return "#388E3C"
        elif color == "#FF9800":
            return "#F57C00"
        elif color == "#f44336":
            return "#D32F2F"
        elif color == "#2196F3":
            return "#1976D2"
        elif color == "#9C27B0":
            return "#7B1FA2"
        elif color == "#607D8B":
            return "#455A64"
        return color

    def create_status_bar(self):
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-weight: bold;
                padding: 5px;
            }
        """)
        self.statusBar().addWidget(self.status_label)

    def show_node_context_menu(self, position):
        menu = QMenu()
        add_action = QAction("Add Node", self)
        add_action.triggered.connect(self.add_node_row)
        delete_action = QAction("Delete Selected", self)
        delete_action.triggered.connect(lambda: self.delete_selected_row(self.node_table))
        edit_action = QAction("Edit Selected", self)
        edit_action.triggered.connect(lambda: self.edit_selected_row(self.node_table))

        menu.addAction(add_action)
        menu.addAction(delete_action)
        menu.addAction(edit_action)

        menu.exec_(self.node_table.mapToGlobal(position))

    def show_arc_context_menu(self, position):
        menu = QMenu()
        add_action = QAction("Add Route", self)
        add_action.triggered.connect(self.add_arc_row)
        delete_action = QAction("Delete Selected", self)
        delete_action.triggered.connect(lambda: self.delete_selected_row(self.arc_table))
        edit_action = QAction("Edit Selected", self)
        edit_action.triggered.connect(lambda: self.edit_selected_row(self.arc_table))

        menu.addAction(add_action)
        menu.addAction(delete_action)
        menu.addAction(edit_action)

        menu.exec_(self.arc_table.mapToGlobal(position))

    def delete_selected_row(self, table):
        current_row = table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(self, 'Delete Row',
                                       f'Are you sure you want to delete row {current_row + 1}?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                table.removeRow(current_row)
                self.status_label.setText(f"Row {current_row + 1} deleted")
        else:
            QMessageBox.information(self, "No Selection", "Please select a row to delete.")

    def edit_selected_row(self, table):
        current_row = table.currentRow()
        if current_row >= 0:
            # Enable editing for the selected row
            for col in range(table.columnCount()):
                item = table.item(current_row, col)
                if item:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                else:
                    # Create item if it doesn't exist
                    table.setItem(current_row, col, QTableWidgetItem(""))
            table.editItem(table.item(current_row, 0))
            self.status_label.setText(f"Editing row {current_row + 1}")
        else:
            QMessageBox.information(self, "No Selection", "Please select a row to edit.")

    def clear_data(self):
        reply = QMessageBox.question(self, 'Clear Data',
                                   'Are you sure you want to clear all input data?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.node_table.setRowCount(0)
            self.arc_table.setRowCount(0)
            self.result_text.setText("Results will appear here after optimization...")
            self.canvas.axes.clear()
            self.canvas.draw()
            self.status_label.setText("Data cleared")

    def add_node_row(self, id_val="", demand=""):
        row = self.node_table.rowCount()
        self.node_table.insertRow(row)
        self.node_table.setItem(row, 0, QTableWidgetItem(str(id_val)))
        self.node_table.setItem(row, 1, QTableWidgetItem(str(demand)))

    def add_arc_row(self, src="", dst="", fixed="", var="", cap=""):
        row = self.arc_table.rowCount()
        self.arc_table.insertRow(row)
        self.arc_table.setItem(row, 0, QTableWidgetItem(str(src)))
        self.arc_table.setItem(row, 1, QTableWidgetItem(str(dst)))
        self.arc_table.setItem(row, 2, QTableWidgetItem(str(fixed)))
        self.arc_table.setItem(row, 3, QTableWidgetItem(str(var)))
        self.arc_table.setItem(row, 4, QTableWidgetItem(str(cap)))

    def add_node_row(self, id_val="", demand=""):
        row = self.node_table.rowCount()
        self.node_table.insertRow(row)
        self.node_table.setItem(row, 0, QTableWidgetItem(str(id_val)))
        self.node_table.setItem(row, 1, QTableWidgetItem(str(demand)))

    def add_arc_row(self, src="", dst="", fixed="", var="", cap=""):
        row = self.arc_table.rowCount()
        self.arc_table.insertRow(row)
        self.arc_table.setItem(row, 0, QTableWidgetItem(str(src)))
        self.arc_table.setItem(row, 1, QTableWidgetItem(str(dst)))
        self.arc_table.setItem(row, 2, QTableWidgetItem(str(fixed)))
        self.arc_table.setItem(row, 3, QTableWidgetItem(str(var)))
        self.arc_table.setItem(row, 4, QTableWidgetItem(str(cap)))

    def load_default_data(self):
        # More realistic default data
        nodes = [
            ("Warehouse A", 150),
            ("Warehouse B", 200),
            ("Customer X", -120),
            ("Customer Y", -180),
            ("Customer Z", -50)
        ]
        for n in nodes:
            self.add_node_row(*n)

        arcs = [
            ("Warehouse A", "Customer X", 5000, 3.5, 150),
            ("Warehouse A", "Customer Y", 4500, 4.2, 180),
            ("Warehouse A", "Customer Z", 6000, 2.8, 100),
            ("Warehouse B", "Customer X", 4800, 3.8, 120),
            ("Warehouse B", "Customer Y", 4200, 4.5, 200),
            ("Warehouse B", "Customer Z", 5500, 3.1, 80),
            ("Warehouse A", "Warehouse B", 1200, 1.2, 100),
        ]
        for a in arcs:
            self.add_arc_row(*a)

    def get_data_from_ui(self):
        nodes = []
        for r in range(self.node_table.rowCount()):
            try:
                nid = self.node_table.item(r, 0).text()
                dem = float(self.node_table.item(r, 1).text())
                nodes.append({"id": nid, "demand": dem})
            except:
                pass

        arcs = []
        for r in range(self.arc_table.rowCount()):
            try:
                src = self.arc_table.item(r, 0).text()
                dst = self.arc_table.item(r, 1).text()
                fc = float(self.arc_table.item(r, 2).text())
                vc = float(self.arc_table.item(r, 3).text())
                cap = float(self.arc_table.item(r, 4).text())
                arcs.append(
                    {
                        "source": src,
                        "target": dst,
                        "fixed_cost": fc,
                        "var_cost": vc,
                        "capacity": cap,
                    }
                )
            except:
                pass
        return nodes, arcs

    def run_optimization(self):
        # Validate input data
        if self.node_table.rowCount() == 0 or self.arc_table.rowCount() == 0:
            QMessageBox.warning(self, "Input Error", "Please add at least one node and one route before optimizing.")
            return

        self.solve_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Optimizing network...")
        self.status_label.setStyleSheet("QLabel { color: #FF9800; font-weight: bold; padding: 5px; }")

        nodes, arcs = self.get_data_from_ui()

        self.worker = OptimizationWorker(nodes, arcs)
        self.worker.finished.connect(self.on_optimization_finished)
        self.worker.error.connect(self.on_optimization_error)
        self.worker.start()

    def on_optimization_finished(self, results):
        self.solve_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if results['status'] == 'Optimal':
            self.status_label.setText("Optimization completed successfully")
            self.status_label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; padding: 5px; }")
        else:
            self.status_label.setText("Optimization completed with issues")
            self.status_label.setStyleSheet("QLabel { color: #FF9800; font-weight: bold; padding: 5px; }")

        # Format results with modern styling
        txt = f"""
        <div style='font-family: Segoe UI; line-height: 1.6;'>
            <h3 style='color: #2196F3; margin-bottom: 15px;'>Optimization Results</h3>
            <div style='background-color: #424242; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid {"#4CAF50" if results["status"] == "Optimal" else "#FF9800"};'>
                <strong>Status:</strong> <span style='color: {"#4CAF50" if results["status"] == "Optimal" else "#FF9800"}; font-size: 14px;'>{results['status']}</span><br>
                <strong>Total Minimum Cost:</strong> <span style='color: #4CAF50; font-size: 20px; font-weight: bold;'>€{results['obj_val']:.2f}</span>
            </div>
        """

        if results.get('built_arcs'):
            txt += "<h4 style='color: #FF9800;'>Built Routes:</h4><div style='background-color: #333; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
            for arc in results['built_arcs']:
                utilization = (arc['flow'] / arc['capacity']) * 100 if arc['capacity'] > 0 else 0
                color = "#4CAF50" if utilization < 80 else "#FF9800" if utilization < 100 else "#f44336"
                txt += f"<div style='margin-bottom: 8px; padding: 5px; background-color: #2D2D2D; border-radius: 3px;'><strong>{arc['source']} → {arc['target']}</strong>: Flow {arc['flow']:.0f} / Capacity {arc['capacity']} <span style='color: {color}; font-weight: bold;'>({utilization:.1f}% utilized)</span></div>"
            txt += "</div>"

        txt += "</div>"

        self.result_text.setText(txt)

        nodes, _ = self.get_data_from_ui()
        self.canvas.plot_solution(nodes, results)

        # Animate the results section
        self.animate_results()

    def animate_results(self):
        # Simple animation to draw attention to results
        animation = QPropertyAnimation(self.result_text, b"styleSheet")
        animation.setDuration(1000)
        start_style = self.result_text.styleSheet()
        highlight_style = start_style.replace("#2D2D2D", "#424242")
        animation.setKeyValueAt(0, start_style)
        animation.setKeyValueAt(0.5, highlight_style)
        animation.setKeyValueAt(1, start_style)
        animation.start()

    def on_optimization_error(self, error_msg):
        self.solve_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Optimization failed")
        self.status_label.setStyleSheet("QLabel { color: #f44336; font-weight: bold; padding: 5px; }")

        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Optimization Error")
        error_dialog.setText("An error occurred during optimization:")
        error_dialog.setDetailedText(error_msg)
        error_dialog.setStyleSheet("""
            QMessageBox {
                background-color: #424242;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
        """)
        error_dialog.exec_()
