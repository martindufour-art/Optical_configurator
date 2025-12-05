# ui/main_window.py
from os import name
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QLabel, QComboBox, QMessageBox,
    QDialog, QPushButton,
)
from PyQt6.QtCore import Qt

from services.database_manager import DatabaseManager
from services.solver import solve  # solver returns dict with wd, focal, fov
from services.optics_calculations import (
    compute_px_per_mm,
    compute_min_detectable_defect,
    compute_fov,
    compute_distance,
    compute_focal
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
        self.cameras = self.db.load_cameras()  # dict keyed by name
        self.objectives = self.db.load_objectives()

        # state
        self.updating = False
        self.current_camera = None
        self.current_objective = None

        # UI
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        form = QFormLayout()

        # --- Camera selector ---
        self.camera_combo = QComboBox()
        camera_names = list(self.cameras.keys())
        self.camera_combo.addItems(camera_names)
        self.camera_combo.currentTextChanged.connect(self.on_camera_selected)
        form.addRow(QLabel("Camera:"), self.camera_combo)
        
        # --- add camera ---
        self.add_camera_btn = QPushButton("Add Camera")
        form.addRow(" ", self.add_camera_btn)

        # --- Objectives ---
        self.objective_combo = QComboBox()
        objective_names = list(self.objectives.keys())
        self.objective_combo.addItems(objective_names)
        self.objective_combo.currentTextChanged.connect(self.on_objective_selected)
        form.addRow(QLabel("Objectif:"), self.objective_combo)

        # --- add Objectives ---
        self.add_lens_btn = QPushButton("Add Objective")
        form.addRow(" ", self.add_lens_btn)

 

        # --- Sensor fields (read-only) ---
        self.pixel_size_edit = QLineEdit()
        self.pixel_size_edit.setReadOnly(True)
        form.addRow("Pixel size (µm):", self.pixel_size_edit)

        self.resolution_edit = QLineEdit()
        self.resolution_edit.setReadOnly(True)
        form.addRow("Resolution (px):", self.resolution_edit)

        self.sensor_size_edit = QLineEdit()
        self.sensor_size_edit.setReadOnly(True)
        form.addRow("Sensor size (mm):", self.sensor_size_edit)

        # --- Optical input fields that user can change ---
        self.wd_edit = QLineEdit("200")   # mm
        self.wd_lock = QCheckBox("lock")
        form.addRow("WD (mm):", self.wd_edit)
        form.addRow("", self.wd_lock)

        self.focal_edit = QLineEdit("16")  # mm
        self.focal_lock = QCheckBox("lock")
        form.addRow("Focale (mm):", self.focal_edit)
        form.addRow("", self.focal_lock)

        self.fov_edit = QLineEdit("")   # mm
        self.fov_lock = QCheckBox("lock")
        form.addRow("FOV (mm):", self.fov_edit)
        form.addRow("", self.fov_lock)

        # --- Results: px/mm and min defect ---
        self.px_per_mm_label = QLabel("-")
        form.addRow("px / mm (X):", self.px_per_mm_label)
        self.min_defect_label = QLabel("-")
        form.addRow("Min defect (3 px):", self.min_defect_label)

        main_layout.addLayout(form)

        # connect edits (use editingFinished so user can type)
        self.wd_edit.editingFinished.connect(self.on_user_edit)
        self.focal_edit.editingFinished.connect(self.on_user_edit)
        self.fov_edit.editingFinished.connect(self.on_user_edit)
        self.wd_lock.stateChanged.connect(self.on_lock_changed)
        self.focal_lock.stateChanged.connect(self.on_lock_changed)
        self.fov_lock.stateChanged.connect(self.on_lock_changed)
        self.add_camera_btn.clicked.connect(self.open_add_camera_dialog)
        self.add_lens_btn.clicked.connect(self.open_add_lens_dialog)

        # if DB non-empty, select first camera by default
        if camera_names:
            # will call on_camera_selected via signal
            self.camera_combo.setCurrentIndex(0)
        else:
            QMessageBox.information(self, "No camera", "No cameras found in data/cameras.json")

    # ----------------------------
    # Camera selection handler
    # ----------------------------
    def on_camera_selected(self, name):
        if not name:
            return
        cam = self.cameras.get(name)
        if cam is None:
            return

        self.current_camera = cam

        # fill sensor UI (read-only)
        px = cam.get("pixel_size_um")
        rx = cam.get("resolution_x")
        ry = cam.get("resolution_y")
        # compute physical sensor size (mm) from px
        sensor_width_mm = (px * rx) / 1000.0
        sensor_height_mm = (px * ry) / 1000.0

        # update fields
        self.updating = True
        self.pixel_size_edit.setText(f"{px:.3f}")
        self.resolution_edit.setText(f"{rx} × {ry}")
        self.sensor_size_edit.setText(f"{sensor_width_mm:.3f} × {sensor_height_mm:.3f}")
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
            self.db.load_cameras()
    
    def open_add_lens_dialog(self):
        dialog = AddLensDialog(self)
        if dialog.exec():
            self.db.load_objectives

    # ----------------------------
    # user edits / locks
    # ----------------------------
    def on_user_edit(self):
        if self.updating:
            return
        self.recalculate_from_state()

    def on_lock_changed(self):
        # simple guard: prevent all unlocked scenario by rechecking box logic if desired
        if self.updating:
            return
        self.recalculate_from_state()

    # ----------------------------
    # Core: build params, call solver, update derived values
    # ----------------------------
    def recalculate_from_state(self):
        if self.current_camera is None:
            return

        # read inputs (graceful parsing)
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

        # call the solver (returns dict)
        solved = solve(params, locks)
        # update UI fields with solver results (but avoid triggering editingFinished)
        self.updating = True
        self.wd_edit.setText(f"{solved['wd']:.3f}")
        self.focal_edit.setText(f"{solved['focal']:.3f}")
        self.fov_edit.setText(f"{solved['fov']:.3f}")
        self.updating = False

        # compute px/mm using sensor width
        px = self.current_camera["pixel_size_um"]
        rx = self.current_camera["resolution_x"]
        sensor_width_mm = (px * rx) / 1000.0

        # assume fov in mm is horizontal FOV
        fov_mm = solved["fov"]
        # guard division by zero
        if fov_mm <= 0.0:
            self.px_per_mm_label.setText("N/A")
            self.min_defect_label.setText("N/A")
            return

        px_per_mm = compute_px_per_mm(rx, fov_mm)  # resolution_x per fov_mm
        min_def = compute_min_detectable_defect(px_per_mm, required_pixels=3)

        self.px_per_mm_label.setText(f"{px_per_mm:.3f}")
        self.min_defect_label.setText(f"{min_def*1000:.1f} µm")  # show µm

