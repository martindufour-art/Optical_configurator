
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QLabel, QComboBox, QMessageBox,
    QDialog, QPushButton, QTabWidget, QHBoxLayout, 
)
import json
from PyQt6.QtCore import QTimer

class AddLensDialog(QDialog):
    def __init__(self, lens_file : str , parent=None):
        super().__init__(parent)
        self.OBJECTIVE_FILE = lens_file
        self.setWindowTitle("Add Lens")
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit()
        self.focal_input = QLineEdit()
        self.mount_input = QLineEdit()
        self.max_image_circle_input = QLineEdit()
        self.aperture_input = QLineEdit()
      


        self.layout.addRow("Name:", self.name_input)
        self.layout.addRow("Focal length:", self.focal_input)
        self.layout.addRow("mount:", self.mount_input)
        self.layout.addRow("Maximum image circle:", self.max_image_circle_input)
        self.layout.addRow("Aperture:", self.aperture_input)
 

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.add_lens)
        self.layout.addRow(self.ok_button)

    def add_lens(self):
        try:
            lens = {
                "name": self.name_input.text(),
                "focal_length": float(self.focal_input.text()),
                "mount": self.mount_input.text(),
                "max_image_cirle": float(self.max_image_circle_input.text()),
                "aperture": self.aperture_input.text()

            }
        except ValueError:
            QMessageBox.warning(self, "Error", "Vérifie les valeurs numériques")
            return

        try:
            with open(self.OBJECTIVE_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"objectives": []}

        data["objectives"].append(lens)
        with open(self.OBJECTIVE_FILE, "w") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(self, "Success", f"Objectif '{lens['name']}' ajoutée !")
        self.accept()
        QTimer.singleShot(500, self.parent().reset)