import math
from services.optics_calculations import (
    compute_fov,
    compute_distance,
    compute_focal,
    compute_px_per_mm,
    compute_min_detectable_defect,
    compute_magnification,
    compute_dof,
    is_sensor_compatible
)

def almost_equal(a, b, eps=1e-6):
    return abs(a - b) < eps


def test_fov():
    # sensor = 6 mm, focal = 12 mm, WD = 400 mm
    fov = compute_fov(6, 12, 400)
    assert almost_equal(fov, 200)  # FOV = 6 * 400 / 12 = 200 mm


def test_distance():
    # Inverse: FOV 200 mm, sensor 6 mm, focal 12 mm
    dist = compute_distance(200, 6, 12)
    assert almost_equal(dist, 400)


def test_focal():
    f = compute_focal(6, 400, 200)
    assert almost_equal(f, 12)


def test_px_per_mm():
    # 2048 px, FOV 200 mm
    pxmm = compute_px_per_mm(2048, 200)
    assert almost_equal(pxmm, 10.24)


def test_min_defect():
    pxmm = 10
    defect = compute_min_detectable_defect(pxmm)
    assert almost_equal(defect, 0.3)  # 3 px / 10 px/mm = 0.3 mm


def test_magnification():
    m = compute_magnification(6, 200)
    assert almost_equal(m, 0.03)


def test_dof():
    # DOF ≈ 2 * N * CoC * (1 + m) / m²
    N = 8
    CoC = 0.015  # mm
    m = 0.1
    dof = compute_dof(N, CoC, m)

    expected = 2 * N * CoC * (1 + m) / (m * m)
    assert almost_equal(dof, expected)


def test_sensor_compatibility():
    assert is_sensor_compatible(22, 16)  # ok : 22 >= 16
    assert not is_sensor_compatible(12, 16)  # trop petit


if __name__ == "__main__":
    print("Running optics calculation tests...")
    test_fov()
    test_distance()
    test_focal()
    test_px_per_mm()
    test_min_defect()
    test_magnification()
    test_dof()
    test_sensor_compatibility()
    print("All tests passed successfully!")
