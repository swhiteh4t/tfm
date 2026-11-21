"""Runtime configuration.

Every value can be overridden through an environment variable so that no
credentials need to be hard-coded or committed. See ``.env.example``.
"""
import os

# Tor SOCKS5 proxy
CONFIG_IP = os.getenv("TOR_SOCKS_HOST", "127.0.0.1")
CONFIG_PORT = int(os.getenv("TOR_SOCKS_PORT", "9050"))

# Tor control port (used to request a new circuit / identity)
TOR_CONTROL_PORT = int(os.getenv("TOR_CONTROL_PORT", str(CONFIG_PORT + 1)))
TOR_CONTROL_PASSWORD = os.getenv("TOR_CONTROL_PASSWORD", "")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "DarkNetScraper")

# Fine-tuned BERT checkpoint used by --predict
MODEL_PATH = os.getenv(
    "DARKNET_MODEL_PATH",
    os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "..", "models", "finetuned_BERT_epoch_1.model")),
)
