import datetime
import os
import traceback

logger_directory = os.path.dirname(__file__) + "/user_files/logs/"
current_epoch_time_ms_str = str(int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp() * 1000))
logger_filepath = logger_directory + "output_log_" + current_epoch_time_ms_str

def ensure_logger_directory() -> None:
    os.makedirs(logger_directory, exist_ok=True)

def error_log(message: str, error: str = "") -> None:
    try:
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        ensure_logger_directory()
        with open(logger_filepath + "_error.log", "a", encoding="utf8") as log_file:
            log_file.write(utc_time + ", " + str(message).replace("\r", r"\r").replace("\n", r"\n") + ", " + str(error).replace("\r", r"\r").replace("\n", r"\n") + "\n")
    except Exception:
        try_print("Could not write to error log:")
        try_print(traceback.format_exc())

def log(message: str) -> None:
    try:
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        ensure_logger_directory()
        with open(logger_filepath + "_log.log", "a", encoding="utf8") as log_file:
            log_file.write(utc_time + ", " + str(message).replace("\r", r"\r").replace("\n", r"\n") + "\n")
    except Exception:
        try_print("Could not write to log:")
        try_print(traceback.format_exc())

def try_print(input_string: str) -> None:
    try:
        print(input_string)
    except Exception:
        pass
