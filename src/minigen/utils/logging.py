import logging

logger = logging.getLogger("minigen")
logger.setLevel(logging.INFO) 

if not logger.handlers:
    handler = logging.StreamHandler() 
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)