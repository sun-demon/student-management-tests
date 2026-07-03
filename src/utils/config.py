import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
DEFAULT_TIMEOUT = int(os.getenv("WEBDRIVER_TIMEOUT", "10"))
POLL_FREQUENCY = float(os.getenv("WEBDRIVER_POLL", "0.5"))
HEADLESS = os.getenv("HEADLESS", "true").lower() in {"1", "true", "yes"}
