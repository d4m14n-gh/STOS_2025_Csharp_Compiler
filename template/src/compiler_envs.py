import os

class MissingEnvError(Exception):
    pass

REQUIRED_VARS = ["SRC", "LIB", "OUT", "BIN", "INF", "LOG"]
missing = [v for v in REQUIRED_VARS if v not in os.environ]
if missing:
    raise MissingEnvError(f"Required environment variables missing: {', '.join(missing)}")

SRC = os.environ["SRC"]
LIB = os.environ["LIB"]
OUT = os.environ["OUT"]
BIN = os.environ["BIN"]
INF = os.environ["INF"]
LOG = os.environ["LOG"]
MAINFILE = os.getenv("MAINFILE")
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 5 * 1024 * 1024))
