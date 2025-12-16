from os import name
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QLabel, QComboBox, QMessageBox,
    QDialog, QPushButton, QTabWidget, QHBoxLayout, 
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from services.database_manager import DatabaseManager
from services.solver import solve
from services.optics_calculations import (
    compute_px_per_mm,
    compute_min_detectable_defect,
    compute_fov,
    compute_distance,
    compute_focal,
    compute_motion_blur
)
from pathlib import Path
import json

DATA_DIR = Path(__file__).parent.parent / "data"
CAMERA_FILE = DATA_DIR / "cameras.json"
OBJECTIVE_FILE = DATA_DIR / "objectives.json"

class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
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
            with open(CAMERA_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"cameras": []}

        data["cameras"].append(cam)
        with open(CAMERA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(self, "Success", f"Caméra '{cam['name']}' ajoutée !")
        self.accept()

class AddLensDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
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
            with open(OBJECTIVE_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"objectives": []}

        data["objectives"].append(lens)
        with open(OBJECTIVE_FILE, "w") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(self, "Success", f"Objectif '{lens['name']}' ajoutée !")
        self.accept()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optical Configurator - v0.3")
        self.setMinimumSize(800, 480)

        # DB
        self.db = DatabaseManager()
        self.cameras = self.db.load_cameras()
        self.objectives = self.db.load_objectives()

        # state
        self.updating = False
        self.current_camera = None
        self.current_objective = None

        # Header
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        self.setCentralWidget(container)
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        self.reset_btn = QPushButton("reset")


        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("logo.jpeg").scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        header_layout.addWidget(logo_label)

        title_label = QLabel("Optical Configurator")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #F1C749 ; padding-left: 10px;")
        header_layout.addWidget(title_label)

        header_layout.addWidget(self.reset_btn)

        header_layout.addStretch()  

        container_layout.addWidget(header)



        # --------------------------
        #        TAB 1
        # --------------------------
        tabs = QTabWidget()
        container_layout.addWidget(tabs)
        self.tab_optics = QWidget()
        tabs.addTab(self.tab_optics, "Optical Calculator")

        # Layout principal de l'onglet optique
        main_layout = QVBoxLayout()
        self.tab_optics.setLayout(main_layout)

        form = QFormLayout()
        main_layout.addLayout(form)


        #  Camera selector
        self.camera_combo = QComboBox()
        camera_names = list(self.cameras.keys())
        self.camera_combo.addItems(camera_names)
        self.camera_combo.currentTextChanged.connect(self.on_camera_selected)
        form.addRow(QLabel("Camera:"), self.camera_combo)

        self.add_camera_btn = QPushButton("Add Camera")
        form.addRow(" ", self.add_camera_btn)


        #  Objective selector

        self.objective_combo = QComboBox()
        objective_names = list(self.objectives.keys())
        self.objective_combo.addItems(objective_names)
        self.objective_combo.currentTextChanged.connect(self.on_objective_selected)
        form.addRow(QLabel("Lens:"), self.objective_combo)

        self.add_lens_btn = QPushButton("Add Lens")
        form.addRow(" ", self.add_lens_btn)

        # sensor info
        self.pixel_size_edit = QLineEdit()
        self.pixel_size_edit.setReadOnly(True)
        form.addRow("Pixel size (µm):", self.pixel_size_edit)

        self.resolution_edit = QLineEdit()
        self.resolution_edit.setReadOnly(True)
        form.addRow("Resolution (px):", self.resolution_edit)

        self.sensor_size_edit = QLineEdit()
        self.sensor_size_edit.setReadOnly(True)
        form.addRow("Sensor size (mm):", self.sensor_size_edit)

        # optical inputs

        self.wd_edit = QLineEdit("200")
        self.wd_lock = QCheckBox("lock")
        form.addRow("WD (mm):", self.wd_edit)
        form.addRow("", self.wd_lock)

        self.focal_edit = QLineEdit("16")
        self.focal_lock = QCheckBox("lock")
        form.addRow("Focal length (mm):", self.focal_edit)
        form.addRow("", self.focal_lock)

        self.fov_edit = QLineEdit("")
        self.fov_lock = QCheckBox("lock")
        form.addRow("FOV (mm):", self.fov_edit)
        form.addRow("", self.fov_lock)

        #  results
        self.px_per_mm_label = QLabel("-")
        form.addRow("px/mm:", self.px_per_mm_label)

        self.min_defect_label = QLabel("-")
        form.addRow("Min defect (3 px):", self.min_defect_label)

        # Connections
        self.wd_edit.editingFinished.connect(self.on_user_edit)
        self.focal_edit.editingFinished.connect(self.on_user_edit)
        self.fov_edit.editingFinished.connect(self.on_user_edit)

        self.wd_lock.stateChanged.connect(self.on_lock_changed)
        self.focal_lock.stateChanged.connect(self.on_lock_changed)
        self.fov_lock.stateChanged.connect(self.on_lock_changed)

        self.add_camera_btn.clicked.connect(self.open_add_camera_dialog)
        self.add_lens_btn.clicked.connect(self.open_add_lens_dialog)
        self.reset_btn.clicked.connect(self.reset)


        # --------------------------
        #   Tab 2 - Motion Blur
        # --------------------------
        self.tab_extra = QWidget()
        tabs.addTab(self.tab_extra, "Motion Blur")

        blur_layout = QFormLayout()
        self.tab_extra.setLayout(blur_layout)

        self.speed_edit = QLineEdit("1.0")
        blur_layout.addRow("Object speed (m/s):", self.speed_edit)

        self.exposure_edit = QLineEdit("0.001")
        blur_layout.addRow("Exposure time (s):", self.exposure_edit)

        self.blur_object_label = QLabel("-")
        blur_layout.addRow("Blur on object (mm):", self.blur_object_label)

        self.blur_sensor_label = QLabel("-")
        blur_layout.addRow("Blur on sensor (µm):", self.blur_sensor_label)

        self.blur_px_label = QLabel("-")
        blur_layout.addRow("Blur (px):", self.blur_px_label)

        self.speed_edit.editingFinished.connect(self.update_motion_blur)
        self.exposure_edit.editingFinished.connect(self.update_motion_blur)

        # --------------------------
        #   Starting 
        # --------------------------
        if camera_names:
            self.camera_combo.setCurrentIndex(0)
        
        self.setStyleSheet("""
    QWidget {
        background-color: #000000;
        color: white;
        font-size: 14px;
    }
    QLineEdit, QComboBox, QPushButton {
        background-color: #111111;
        color: white;
        border: 1px solid #444;
        padding: 4px;
    }
    QTabWidget::pane {
        border: 1px solid #333;
    }
    QTabBar::tab {
        background: #111111;
        padding: 8px;
    }
    QTabBar::tab:selected {
        background: #222222;
    }
""")


    def on_camera_selected(self, name):
        if not name:
            return
        cam = self.cameras.get(name)
        if cam is None:
            return

        self.current_camera = cam


        px = cam.get("pixel_size_um")
        rx = cam.get("resolution_x")
        ry = cam.get("resolution_y")
        # compute physical sensor size (mm) from px
        self.sensor_width_mm = (px * rx) / 1000.
        self.sensor_height_mm = (px * ry) / 1000.

        # update fields
        self.updating = True
        self.pixel_size_edit.setText(f"{px:.3f}")
        self.resolution_edit.setText(f"{rx} × {ry}")
        self.sensor_size_edit.setText(f"{self.sensor_width_mm:.3f} × {self.sensor_height_mm:.3f}")
        self.updating = False

        # trigger recalcul (use current wd/focal/fov)
        self.recalculate_from_state()

    def on_objective_selected(self,name):
        if not name:
            return
        lens = self.objectives.get(name)
        if lens is None:
            return
        
        self.current_objective = lens
        focal = lens.get("focal_length")

        self.updating = True
        self.focal_edit.setText(f"{focal:.3f}")
        self.focal_lock.setChecked(True)

        self.updating = False
        self.recalculate_from_state()

        return


    def open_add_camera_dialog(self):
        dialog = AddCameraDialog(self)
        if dialog.exec():
            self.load_material()
    
    def open_add_lens_dialog(self):
        dialog = AddLensDialog(self)
        if dialog.exec():
            self.load_material


    def on_user_edit(self):
        if self.updating:
            return
        self.recalculate_from_state()

    def on_lock_changed(self):
        if self.updating:
            return
        self.recalculate_from_state()


    def recalculate_from_state(self):
        if self.current_camera is None:
            return

        try:
            wd = float(self.wd_edit.text())
        except Exception:
            wd = float(self.wd_edit.text() or 0.0)

        try:
            focal = float(self.focal_edit.text())
        except Exception:
            focal = float(self.focal_edit.text() or 0.0)

        try:
            fov = float(self.fov_edit.text())
        except Exception:
            fov = float(self.fov_edit.text() or 0.0)

        params = {"wd": wd, "focal": focal, "fov": fov}
        locks = {
            "wd": self.wd_lock.isChecked(),
            "focal": self.focal_lock.isChecked(),
            "fov": self.fov_lock.isChecked()
        }


        solved = solve(params, locks,self.sensor_width_mm)
        self.updating = True
        self.wd_edit.setText(f"{solved['wd']:.3f}")
        self.focal_edit.setText(f"{solved['focal']:.3f}")
        self.fov_edit.setText(f"{solved['fov']:.3f}")
        self.updating = False


        px = self.current_camera["pixel_size_um"]
        rx = self.current_camera["resolution_x"]
        self.sensor_width_mm = (px * rx) / 1000.0

        # assume fov in mm is horizontal FOV
        fov_mm = solved["fov"]
        if fov_mm <= 0.0:
            self.px_per_mm_label.setText("N/A")
            self.min_defect_label.setText("N/A")
            return

        px_per_mm = compute_px_per_mm(rx, fov_mm)  # resolution_x per fov_mm
        min_def = compute_min_detectable_defect(px_per_mm, required_pixels=3)

        self.px_per_mm_label.setText(f"{px_per_mm:.3f}")
        self.min_defect_label.setText(f"{min_def*1000:.1f} µm") 

    def load_material(self):
        self.db.load_cameras()
        self.db.load_objectives()

        

    def update_motion_blur(self):
        if self.current_camera is None:
            return

        try:
            speed = float(self.speed_edit.text())
            exposure = float(self.exposure_edit.text())
        except ValueError:
            return

        try:
            fov_mm = float(self.fov_edit.text())
        except ValueError:
            return

        if fov_mm <= 0:
            return

        rx = self.current_camera["resolution_x"]
        px_size = self.current_camera["pixel_size_um"]

        px_per_mm = compute_px_per_mm(rx, fov_mm)



        blur_obj_mm, blur_sensor_um, blur_px = compute_motion_blur(
            speed_m_s=speed,
            exposure_time_s=exposure,
            px_per_mm=px_per_mm,
            pixel_size_um=px_size,
        )

        self.blur_object_label.setText(f"{blur_obj_mm:.3f}")
        self.blur_sensor_label.setText(f"{blur_sensor_um:.2f}")
        self.blur_px_label.setText(f"{blur_px:.2f}")
    
    def reset(self):
        self.updating = True

        self.current_camera = None
        self.current_objective = None

        if self.camera_combo.count() > 0:
            self.camera_combo.setCurrentIndex(0)

        if self.objective_combo.count() > 0:
            self.objective_combo.setCurrentIndex(0)

        self.wd_edit.setText("200")
        self.focal_edit.setText("")
        self.fov_edit.setText("")

        self.wd_lock.setChecked(False)
        self.focal_lock.setChecked(False)
        self.fov_lock.setChecked(False)

        self.pixel_size_edit.clear()
        self.resolution_edit.clear()
        self.sensor_size_edit.clear()

        self.px_per_mm_label.setText("-")
        self.min_defect_label.setText("-")

        self.speed_edit.setText("1.0")
        self.exposure_edit.setText("0.001")
        self.blur_object_label.setText("-")
        self.blur_sensor_label.setText("-")
        self.blur_px_label.setText("-")

        self.updating = False

        if self.camera_combo.count() > 0:
            self.on_camera_selected(self.camera_combo.currentText())
