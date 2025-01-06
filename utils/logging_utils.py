import inspect
import logging
import os
import time
from functools import wraps
from uuid import uuid4

logging_enabled = True


def setup_logging(
    logger_name="step_by_step",
    logs_folder="logs/",
    log_filename="step_by_step.log",
    level=logging.INFO,
):
    """Set up logging configuration."""
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    log_path = os.path.join(logs_folder, log_filename)

    # Configure the root logger
    # Set the root logger to WARNING level
    logging.basicConfig(level=logging.WARNING)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Remove all handlers associated with the logger object.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create a file handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    disable_all_loggers_except(["step_by_step", "speed", "testing"])

    return logger


def disable_all_loggers_except(logger_names=["step_by_step"]):
    if isinstance(logger_names, str):
        logger_names = [logger_names]
    for name, logger in logging.root.manager.loggerDict.items():
        if name not in logger_names and isinstance(logger, logging.Logger):
            logger.setLevel(logging.WARNING)
            logger.propagate = False


def log_message(logger, level, class_instance, message, user_id=None):

    if logging_enabled:
        """Log a message with the given level on the provided logger."""
        current_frame = inspect.currentframe()
        # print(f"current_frame: {current_frame}\n")
        frame_info = inspect.getframeinfo(current_frame.f_back)
        # print(f"frame_info: {frame_info}\n")

        # Get only the base filename, not the full path
        file_name = os.path.basename(frame_info.filename)
        line_number = frame_info.lineno
        class_name = (
            class_instance
            if isinstance(class_instance, str)
            else (
                class_instance.__class__.__name__
                if hasattr(class_instance, "__class__")
                else class_instance.__name__
            )
        )
        # print(f"class_name: {class_name}\n")

        func_name = current_frame.f_back.f_code.co_name
        # if isinstance(class_name, str):
        #     func_name = ''
        # else:
        #     func_name = current_frame.f_back.f_code.co_name

        # print(f"func_name: {func_name}\n")
        # print(f"current_frame.f_back.f_code.co_name: {current_frame.f_back.f_code.co_name}\n")

        # Check if the logging level is valid
        if level not in ["debug", "info", "warning", "error", "critical"]:
            level = "info"

        log_func = getattr(logger, level)

        timestamp = time.strftime("%y%m%d-%H%M")
        log_message = f"{timestamp} - {file_name}:{line_number} - {class_name}{
            ' - ' + func_name if func_name else ''} - {message}"

        # Add user ID to the log message if it's provided
        if user_id is not None:
            log_message += f" - user {user_id}"

        log_func(log_message)


def enable_logging(enable=True):
    """Enable or disable logging."""
    global logging_enabled
    logging_enabled = enable


# Function to log time and update averages


def time_spent(start_time, output_type="str") -> str | float:
    end_time = time.time()
    elapsed_time = end_time - start_time
    if output_type == "str":
        return f"{elapsed_time:.2f} seconds"
    else:
        return elapsed_time


# Decorator that logs the start and end of the execution of a function
def log_execution(logger, logger_speed):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            exec_id = uuid4()
            # the name of the function being wrapped
            func_name = str(func.__name__)
            instance = args[0]  # Assuming the first argument is 'self'
            class_name = instance.__class__.__name__  # Get the class name dynamically

            cls_and_func_str = str(class_name) + ":" + func_name

            log_message(logger, "info", cls_and_func_str, f"START ({exec_id})")
            func_start_time = time.time()

            result = func(*args, **kwargs)

            func_time_spent_str = time_spent(func_start_time)
            log_message(
                logger,
                "info",
                cls_and_func_str,
                f"END ({exec_id}, spent {func_time_spent_str})",
            )
            log_message(
                logger_speed,
                "info",
                cls_and_func_str,
                f"({exec_id}, spent {func_time_spent_str})",
            )

            return result

        return wrapper

    return decorator
