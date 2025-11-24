from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QLabel
)
from PyQt6.QtCore import Qt

from services.solver import solve


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Optical Configurator - AutoSolve")
        self.setMinimumSize(600, 400)

        central = QWidget()
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        form = QFormLayout()

        # ---- Fields ----
        self.wd_edit = QLineEdit("400")
        self.focal_edit = QLineEdit("12")
        self.fov_edit = QLineEdit("200")

        # ---- Locks ----
        self.wd_lock = QCheckBox("lock")
        self.focal_lock = QCheckBox("lock")
        self.fov_lock = QCheckBox("lock")

        self.focal_lock.setChecked(True)
        self.wd_lock.setChecked(True)

        # ---- Add rows ----
        form.addRow("WD (mm):", self.wd_edit)
        form.addRow("", self.wd_lock)

        form.addRow("Focale (mm):", self.focal_edit)
        form.addRow("", self.focal_lock)

        form.addRow("FOV (mm):", self.fov_edit)
        form.addRow("", self.fov_lock)

        main_layout.addLayout(form)

                # connect fields
        self.wd_edit.editingFinished.connect(self.on_user_edit)
        self.focal_edit.editingFinished.connect(self.on_user_edit)
        self.fov_edit.editingFinished.connect(self.on_user_edit)



        # prevent feedback loops
        self.updating = False

        # Flag pour éviter les boucles infinies
        self.updating_lock = False

        # Connecte chaque checkbox
        self.wd_lock.stateChanged.connect(self.on_lock_changed)
        self.focal_lock.stateChanged.connect(self.on_lock_changed)
        self.fov_lock.stateChanged.connect(self.on_lock_changed)

    def on_lock_changed(self):
        if self.updating_lock:
            return

        self.updating_lock = True

        # Exemple : si wd_lock décochée, coche les deux autres
        if not self.wd_lock.isChecked():
            self.focal_lock.setChecked(True)
            self.fov_lock.setChecked(True)

        # Si focal_lock décochée, coche les deux autres
        elif not self.focal_lock.isChecked():
            self.wd_lock.setChecked(True)
            self.fov_lock.setChecked(True)

        # Si fov_lock décochée, coche les deux autres
        elif not self.fov_lock.isChecked():
            self.wd_lock.setChecked(True)
            self.focal_lock.setChecked(True)

        self.updating_lock = False


    def on_user_edit(self):
        if self.updating:
            return

        # read values
        try:
            params = {
                "wd": float(self.wd_edit.text()),
                "focal": float(self.focal_edit.text()),
                "fov": float(self.fov_edit.text())
            }
        except ValueError:
            return

        locks = {
            "wd": self.wd_lock.isChecked(),
            "focal": self.focal_lock.isChecked(),
            "fov": self.fov_lock.isChecked()
        }

        # solve
        new_vals = solve(params, locks)

        # update fields without triggering signals
        self.updating = True
        self.wd_edit.setText(f"{new_vals['wd']:.3f}")
        self.focal_edit.setText(f"{new_vals['focal']:.3f}")
        self.fov_edit.setText(f"{new_vals['fov']:.3f}")
        self.updating = False
