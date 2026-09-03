from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "config.yaml"

with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
    config = yaml.safe_load(arquivo)

