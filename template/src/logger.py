import logging
import compiler_envs
from logging.handlers import RotatingFileHandler


logger = logging.getLogger("compiler_logger")
logger.setLevel(logging.DEBUG) 

open(compiler_envs.LOG, "w").close()
file_handler = RotatingFileHandler(compiler_envs.LOG, maxBytes=compiler_envs.LOG_MAX_SIZE)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
