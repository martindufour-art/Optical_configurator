# services/solver.py

from services.optics_calculations import (
    compute_fov,
    compute_distance,
    compute_focal
)




def solve(params, locks, SENSOR_SIZE_MM):

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


    return {
        "wd": wd,
        "focal": focal,
        "fov": fov
    }
