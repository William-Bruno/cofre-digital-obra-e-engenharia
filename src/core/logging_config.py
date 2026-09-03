import logging
import logging.config
from pathlib import Path
from core.config_loader import config


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR.parent / config["paths"]["log_path"]
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging_config= config["logging"]
logging_config["handlers"]["file"]["filename"] = str(LOG_PATH)
logging.config.dictConfig(logging_config)
logger = logging.getLogger("cofre_digital")