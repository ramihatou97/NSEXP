"""
Enhanced Logging Utility for Neurosurgical Knowledge System
Provides structured logging with JSON format and rotation
"""
import logging
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
import traceback


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format for better parsing
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable formatter for console output with colors (if supported)
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        level_color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"]

        # Format: timestamp - level - module:function:line - message
        formatted = (
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - "
            f"{level_color}{record.levelname:8}{reset} - "
            f"{record.module}:{record.funcName}:{record.lineno} - "
            f"{record.getMessage()}"
        )

        # Add exception info if present
        if record.exc_info:
            formatted += "\n" + "".join(traceback.format_exception(*record.exc_info))

        return formatted


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_logs: bool = False,
    rotate_logs: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 7,  # Keep 7 days of logs
) -> logging.Logger:
    """
    Setup comprehensive logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path (default: logs/app.log)
        json_logs: Use JSON format for file logs (better for parsing)
        rotate_logs: Enable log rotation
        max_bytes: Maximum size of each log file
        backup_count: Number of backup log files to keep

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("neurosurgical_knowledge")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Console handler (human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(ConsoleFormatter())
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file or json_logs:
        log_file = log_file or "logs/app.log"
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if rotate_logs:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
        else:
            file_handler = logging.FileHandler(log_file)

        file_handler.setLevel(getattr(logging, log_level.upper()))

        # Use JSON formatter for file logs if requested
        if json_logs:
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )

        logger.addHandler(file_handler)

    # Separate error log file
    if log_file:
        error_log_path = Path(log_file).parent / "error.log"
        error_handler = RotatingFileHandler(
            error_log_path, maxBytes=max_bytes, backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            StructuredFormatter() if json_logs else
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(exc_info)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(error_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a child logger with the specified name

    Args:
        name: Logger name (usually __name__)

    Returns:
        Child logger instance
    """
    return logging.getLogger(f"neurosurgical_knowledge.{name}")


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context: Any
) -> None:
    """
    Log message with additional context

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **context: Additional context as keyword arguments
    """
    log_func = getattr(logger, level.lower())
    log_func(message, extra=context)


# Default logger instance
default_logger = setup_logging()


# Export convenience functions
__all__ = [
    "setup_logging",
    "get_logger",
    "log_with_context",
    "StructuredFormatter",
    "ConsoleFormatter",
    "default_logger",
]
