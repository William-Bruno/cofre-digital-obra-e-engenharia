from pathlib import Path
import yaml
from error import FileConfigError

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "config.yaml"

try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
        config = yaml.safe_load(arquivo)
except (OSError, IOError) as erro:
    raise FileConfigError("Probema ao abrir arquivo de configuração YAML")

