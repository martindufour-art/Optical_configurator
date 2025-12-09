import math

"""
Module : optics_calculations
Fonctions de base pour un configurateur optique dans l'approximation de Gauss :
- FOV(Field of View) ⇄ WD(working distance) ⇄ focale
- résolution px/mm
"""


# ------------------------------------------------------------
# 1. Relations géométriques optiques
# ------------------------------------------------------------

def compute_fov(sensor_mm: float, focal_mm: float, distance_mm: float) -> float:
    """
    FOV = sensor_size * WD / focal
    """
    if focal_mm == 0:
        raise ValueError("Focal length cannot be zero.")
    return sensor_mm*(distance_mm/focal_mm)


def compute_distance(fov_mm: float, sensor_mm: float, focal_mm: float) -> float:
    """
    Distance de travail :
    WD = FOV * focal / sensor
    """
    if sensor_mm == 0:
        raise ValueError("Sensor size cannot be zero.")
    return fov_mm*(focal_mm/sensor_mm)


def compute_focal(sensor_mm: float, distance_mm: float, fov_mm: float) -> float:
    """
    Focale :
    focal = sensor * WD / FOV
    """
    if fov_mm == 0:
        raise ValueError("FOV cannot be zero.")
    return sensor_mm*(distance_mm/fov_mm)


# ------------------------------------------------------------
# 2. Résolution px/mm
# ------------------------------------------------------------

def compute_px_per_mm(resolution_px: int, fov_mm: float) -> float:
    """
    px/mm = resolution_px / FOV_mm
    """
    if fov_mm == 0:
        raise ValueError("FOV cannot be zero.")
    return resolution_px / fov_mm


def compute_min_detectable_defect(px_per_mm: float, required_pixels: int = 3) -> float:
    """
    Taille minimale de défaut détectable
    Par défaut : 3 pixels par défaut (règle industrielle standard)
    defect_size_mm = required_pixels / (px/mm)
    """
    if px_per_mm == 0:
        raise ValueError("px_per_mm cannot be zero.")
    return required_pixels / px_per_mm


# # ------------------------------------------------------------
# # 3. Profondeur de champ (approximation basique)
# # ------------------------------------------------------------

# def compute_dof(f_number: float, coc_mm: float, magnification: float) -> float:
#     """
#     DOF approximée pour imaging indus.
#     DOF ~ 2*N*CoC*(1+m)/m^2  
#     """
#     if magnification == 0:
#         raise ValueError("Magnification cannot be zero.")
#     return 2 *f_number*coc_mm*(1+magnification)/(magnification**2)


# def compute_magnification(sensor_mm: float, fov_mm: float) -> float:
#     """
#     m = sensor/FOV
#     """
#     if fov_mm == 0:
#         raise ValueError("FOV cannot be zero.")
#     return sensor_mm/fov_mm


# # ------------------------------------------------------------
# # 4. Compatibilité capteur / objectif
# # ------------------------------------------------------------

# def is_sensor_compatible(image_circle_mm: float, sensor_diagonal_mm: float) -> bool:
#     """
#     Un objectif est compatible si son cercle d'image >= diagonale du capteur
#     """
#     return image_circle_mm >= sensor_diagonal_mm
