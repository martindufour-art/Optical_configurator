
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QLabel, QComboBox, QMessageBox,
    QDialog, QPushButton, QTabWidget, QHBoxLayout, 
)
import json
from PyQt6.QtCore import QTimer

class AddCameraDialog(QDialog):
    def __init__(self, camera_file : str, parent=None):
        super().__init__(parent)
        self.CAMERA_FILE = camera_file
        self.setWindowTitle("Add Camera")
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit()
        self.res_x_input = QLineEdit()
        self.res_y_input = QLineEdit()
        self.pixel_input = QLineEdit()
        self.shutter_input = QLineEdit()
        self.notes_input = QLineEdit()

        self.layout.addRow("Name:", self.name_input)
        self.layout.addRow("Resolution X:", self.res_x_input)
        self.layout.addRow("Resolution Y:", self.res_y_input)
        self.layout.addRow("Pixel size (µm):", self.pixel_input)
        self.layout.addRow("Shutter type:", self.shutter_input)
        self.layout.addRow("Notes:", self.notes_input)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.add_camera)
        self.layout.addRow(self.ok_button)

    def add_camera(self):
        try:
            cam = {
                "name": self.name_input.text(),
                "resolution_x": int(self.res_x_input.text()),
                "resolution_y": int(self.res_y_input.text()),
                "pixel_size_um": float(self.pixel_input.text()),
                "shutter": self.shutter_input.text(),
                "notes": self.notes_input.text()
            }
        except ValueError:
            QMessageBox.warning(self, "Error", "Vérifie les valeurs numériques")
            return

        try:
            with open(self.CAMERA_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"cameras": []}

        data["cameras"].append(cam)
        with open(self.CAMERA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(self, "Success", f"Caméra '{cam['name']}' ajoutée !")
        self.accept()
        QTimer.singleShot(500, self.parent().reset)