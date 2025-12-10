"""
Formulaires CRUD PyQt5
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                             QPushButton, QCheckBox, QGroupBox, QRadioButton,
                             QButtonGroup, QLabel, QMessageBox)
from PyQt5.QtCore import Qt

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Truck, TruckType, Driver, Order, OrderType


class TruckFormDialog(QDialog):
    """Formulaire pour ajouter/modifier un camion"""
    
    def __init__(self, parent=None, truck=None):
        super().__init__(parent)
        self.truck = truck
        self.setWindowTitle("Ajouter un Camion" if truck is None else "Modifier un Camion")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
        
        if truck:
            self.load_truck_data()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Formulaire
        form = QFormLayout()
        
        # ID
        self.id_edit = QLineEdit()
        form.addRow("ID:", self.id_edit)
        
        # Nom
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems([t.value for t in TruckType])
        form.addRow("Type:", self.type_combo)
        
        # Capacité
        self.capacity_spin = QDoubleSpinBox()
        self.capacity_spin.setRange(0.1, 100.0)
        self.capacity_spin.setSuffix(" t")
        form.addRow("Capacité:", self.capacity_spin)
        
        # Coût/km
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0.0, 10.0)
        self.cost_spin.setSingleStep(0.1)
        self.cost_spin.setSuffix(" TND")
        form.addRow("Coût/km:", self.cost_spin)
        
        # Max commandes
        self.max_orders_spin = QSpinBox()
        self.max_orders_spin.setRange(1, 10)
        form.addRow("Max Commandes:", self.max_orders_spin)
        
        layout.addLayout(form)
        
        # Types compatibles
        compat_group = QGroupBox("Types de Commandes Compatibles")
        compat_layout = QVBoxLayout(compat_group)
        
        self.compat_checks = {}
        for order_type in OrderType:
            check = QCheckBox(order_type.value)
            self.compat_checks[order_type.value] = check
            compat_layout.addWidget(check)
        
        layout.addWidget(compat_group)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("✅ Enregistrer")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_truck_data(self):
        """Charge les données du camion"""
        self.id_edit.setText(self.truck.id)
        self.name_edit.setText(self.truck.name)
        self.type_combo.setCurrentText(self.truck.truck_type.value)
        self.capacity_spin.setValue(self.truck.capacity)
        self.cost_spin.setValue(self.truck.cost_per_km)
        self.max_orders_spin.setValue(self.truck.max_orders)
        
        for order_type in self.truck.compatible_order_types:
            if order_type in self.compat_checks:
                self.compat_checks[order_type].setChecked(True)
    
    def get_truck(self):
        """Retourne le camion créé/modifié"""
        compatible_types = [
            order_type for order_type, check in self.compat_checks.items()
            if check.isChecked()
        ]
        
        return Truck(
            id=self.id_edit.text(),
            name=self.name_edit.text(),
            capacity=self.capacity_spin.value(),
            truck_type=TruckType(self.type_combo.currentText()),
            compatible_order_types=compatible_types,
            cost_per_km=self.cost_spin.value(),
            max_orders=self.max_orders_spin.value()
        )


class DriverFormDialog(QDialog):
    """Formulaire pour ajouter/modifier un chauffeur"""
    
    def __init__(self, parent=None, driver=None):
        super().__init__(parent)
        self.driver = driver
        self.setWindowTitle("Ajouter un Chauffeur" if driver is None else "Modifier un Chauffeur")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
        
        if driver:
            self.load_driver_data()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Formulaire
        form = QFormLayout()
        
        # ID
        self.id_edit = QLineEdit()
        form.addRow("ID:", self.id_edit)
        
        # Nom
        self.name_edit = QLineEdit()
        form.addRow("Nom:", self.name_edit)
        
        # Max heures
        self.max_hours_spin = QDoubleSpinBox()
        self.max_hours_spin.setRange(1.0, 24.0)
        self.max_hours_spin.setSuffix(" h")
        form.addRow("Max Heures/jour:", self.max_hours_spin)
        
        # Tarif horaire
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0.0, 100.0)
        self.rate_spin.setSuffix(" TND")
        form.addRow("Tarif Horaire:", self.rate_spin)
        
        # Disponibilité
        self.available_check = QCheckBox("Disponible")
        self.available_check.setChecked(True)
        form.addRow("", self.available_check)
        
        layout.addLayout(form)
        
        # Types de permis
        license_group = QGroupBox("Types de Permis")
        license_layout = QVBoxLayout(license_group)
        
        self.license_checks = {}
        for license_type in ['B', 'C', 'CE', 'D']:
            check = QCheckBox(f"Permis {license_type}")
            self.license_checks[license_type] = check
            license_layout.addWidget(check)
        
        layout.addWidget(license_group)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("✅ Enregistrer")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_driver_data(self):
        """Charge les données du chauffeur"""
        self.id_edit.setText(self.driver.id)
        self.name_edit.setText(self.driver.name)
        self.max_hours_spin.setValue(self.driver.max_hours)
        self.rate_spin.setValue(self.driver.hourly_rate)
        self.available_check.setChecked(self.driver.available)
        
        for license_type in self.driver.license_types:
            if license_type in self.license_checks:
                self.license_checks[license_type].setChecked(True)
    
    def get_driver(self):
        """Retourne le chauffeur créé/modifié"""
        license_types = [
            license_type for license_type, check in self.license_checks.items()
            if check.isChecked()
        ]
        
        return Driver(
            id=self.id_edit.text(),
            name=self.name_edit.text(),
            license_types=license_types,
            max_hours=self.max_hours_spin.value(),
            hourly_rate=self.rate_spin.value(),
            available=self.available_check.isChecked()
        )


class OrderFormDialog(QDialog):
    """Formulaire pour ajouter/modifier une commande"""
    
    def __init__(self, parent=None, order=None):
        super().__init__(parent)
        self.order = order
        self.setWindowTitle("Ajouter une Commande" if order is None else "Modifier une Commande")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
        
        if order:
            self.load_order_data()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Formulaire
        form = QFormLayout()
        
        # ID
        self.id_edit = QLineEdit()
        form.addRow("ID:", self.id_edit)
        
        # Origine
        self.origin_edit = QLineEdit()
        form.addRow("Origine:", self.origin_edit)
        
        # Destination
        self.destination_edit = QLineEdit()
        form.addRow("Destination:", self.destination_edit)
        
        # Poids
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.1, 100.0)
        self.weight_spin.setSuffix(" t")
        form.addRow("Poids:", self.weight_spin)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems([t.value for t in OrderType])
        form.addRow("Type:", self.type_combo)
        
        # Distance
        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(1.0, 10000.0)
        self.distance_spin.setSuffix(" km")
        form.addRow("Distance:", self.distance_spin)
        
        layout.addLayout(form)
        
        # Priorité
        priority_group = QGroupBox("Priorité")
        priority_layout = QHBoxLayout(priority_group)
        
        self.priority_group = QButtonGroup()
        for i in range(1, 6):
            radio = QRadioButton(str(i))
            self.priority_group.addButton(radio, i)
            priority_layout.addWidget(radio)
            if i == 3:
                radio.setChecked(True)
        
        layout.addWidget(priority_group)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("✅ Enregistrer")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_order_data(self):
        """Charge les données de la commande"""
        self.id_edit.setText(self.order.id)
        self.origin_edit.setText(self.order.origin)
        self.destination_edit.setText(self.order.destination)
        self.weight_spin.setValue(self.order.weight)
        self.type_combo.setCurrentText(self.order.order_type.value)
        self.distance_spin.setValue(self.order.distance)
        
        button = self.priority_group.button(self.order.priority)
        if button:
            button.setChecked(True)
    
    def get_order(self):
        """Retourne la commande créée/modifiée"""
        return Order(
            id=self.id_edit.text(),
            origin=self.origin_edit.text(),
            destination=self.destination_edit.text(),
            weight=self.weight_spin.value(),
            order_type=OrderType(self.type_combo.currentText()),
            distance=self.distance_spin.value(),
            priority=self.priority_group.checkedId()
        )
