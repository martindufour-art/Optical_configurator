# services/database_manager.py
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CAMERA_FILE = DATA_DIR / "cameras.json"

class DatabaseManager:
    def __init__(self, camera_file: Path = CAMERA_FILE):
        self.camera_file = camera_file
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.camera_file.exists():
            self.camera_file.write_text('{"cameras": []}')

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
