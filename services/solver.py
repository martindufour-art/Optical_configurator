# services/solver.py

from services.optics_calculations import (
    compute_fov,
    compute_distance,
    compute_focal
)

SENSOR_SIZE_MM = 8.4  # temporaire, configurable plus tard


def solve(params, locks):
    """
    params = {
        "wd": float,
        "focal": float,
        "fov": float
    }

    locks = {
        "wd": bool,
        "focal": bool,
        "fov": bool
    }
    """

    wd = params["wd"]
    focal = params["focal"]
    fov = params["fov"]

    # CAS 1 : 2 locked → résoudre la 3e
    if locks["wd"] and locks["focal"] and not locks["fov"]:
        fov = compute_fov(SENSOR_SIZE_MM, focal, wd)

    elif locks["wd"] and locks["fov"] and not locks["focal"]:
        focal = compute_focal(SENSOR_SIZE_MM, wd, fov)

    elif locks["focal"] and locks["fov"] and not locks["wd"]:
        wd = compute_distance(fov, SENSOR_SIZE_MM, focal)

    # CAS 2 : 1 locked → l’utilisateur choisit ce qu’il modifie → rien à faire
    # CAS 3 : rien locked → laisser l’utilisateur mettre ce qu’il veut

    return {
        "wd": wd,
        "focal": focal,
        "fov": fov
    }
