"""
Logging configuration for DRL training and backtesting
"""
import logging
import os
from pathlib import Path
from datetime import datetime
import sys

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Define log levels
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

# Create formatters
detailed_formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

simple_formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def setup_logger(name: str, log_file: str = None, level=logging.DEBUG) -> logging.Logger:
    """
    Setup a logger with both file and console handlers
    
    Args:
        name: Logger name
        log_file: Log file name (if None, uses name-based default)
        level: Logging level
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"{name.replace('.', '_')}_{timestamp}.log"
    
    file_handler = logging.FileHandler(
        LOGS_DIR / log_file,
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    return logger


def setup_training_logger(job_id: str) -> logging.Logger:
    """
    Setup logger for a specific training job
    
    Args:
        job_id: Training job ID
    
    Returns:
        Job-specific logger
    """
    logger_name = f"training.{job_id[:8]}"
    log_file = f"training_{job_id}.log"
    return setup_logger(logger_name, log_file)


def setup_backtest_logger(job_id: str) -> logging.Logger:
    """
    Setup logger for a specific backtest job
    
    Args:
        job_id: Backtest job ID
    
    Returns:
    """
    logger_name = f"backtest.{job_id[:8]}"
    log_file = f"backtest_{job_id}.log"
    return setup_logger(logger_name, log_file)


# Global loggers for services
training_service_logger = setup_logger("app.training_service", "training_service.log")
backtest_service_logger = setup_logger("app.backtest_service", "backtest_service.log")
trainer_logger = setup_logger("app.trainer", "trainer.log")
environment_logger = setup_logger("app.environment", "environment.log")

