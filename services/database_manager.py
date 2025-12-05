# services/database_manager.py
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CAMERA_FILE = DATA_DIR / "cameras.json"
OBJECTIVE_FILE = DATA_DIR / "objectives.json"

class DatabaseManager:
    def __init__(self, camera_file: Path = CAMERA_FILE,objective_file: Path = OBJECTIVE_FILE):
        self.camera_file = camera_file
        self.objective_file = objective_file
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.camera_file.exists():
            self.camera_file.write_text('{"cameras": []}')
        if not self.objective_file.exists():
            self.objective_file.write_text('{"objectives": []}')

    def load_cameras(self):
        with open(self.camera_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # return dict keyed by name for convenience
        cams = {cam["name"]: cam for cam in data.get("cameras", [])}
        return cams

    def save_cameras(self, cams_dict):
        # cams_dict: {name: camdict}
        data = {"cameras": list(cams_dict.values())}
        with open(self.camera_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_objectives(self):
        with open(self.objective_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # return dict keyed by name for convenience
        objs = {obj["name"]: obj for obj in data.get("objectives", [])}
        return objs

    def save_objective(self, obj_dict):
        # cams_dict: {name: camdict}
        data = {"objectives": list(obj_dict.values())}
        with open(self.objective_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)