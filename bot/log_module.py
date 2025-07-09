"""
log_module.py

Creates a basic logger with custom formatting that posts to the main stream and a file.

Use:
import log_module
logger = log_module.create_logger("filename.log", "logger_name")
logger.debug("message"), .info, .warning, .error, .critical
"""

import logging

def create_logger(filename="default.log", logger_name="default"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    format='%(asctime)s - %(name)s | %(levelname)s: %(message)s'
    formatter = logging.Formatter(format)

    file_handler = logging.FileHandler(filename, mode='a', encoding='utf-8') #appends to file in case main process restarts
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
   
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger