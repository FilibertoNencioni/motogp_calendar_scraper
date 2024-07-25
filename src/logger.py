import os
from enum import Enum
from datetime import datetime

class LogType(Enum):
    INFO = 1
    WARN = 2
    ERROR = 3

class Logger:
    log_path:str
    log_file_suffix:str

    def __init__(self) -> None:
        #Controllo prima se è stato fornito il path
        tmp_path = os.getenv("LOG_PATH")
        if tmp_path is None:
            raise Exception("ERROR! Missing LOG_PATH env variable")
        
        #Controllo inoltre se il path che è stato fornito esiste e se è una directory
        #nel caso in cui non esiste lo creo
        if os.path.exists(tmp_path):
            #Controllo se è una cartella
            if not os.path.isdir(tmp_path):
                raise Exception(f"ERROR! The path given in LOG_PATH env variable ({tmp_path}) is not a directory")
        else:
            #creo la directory
            os.makedirs(tmp_path)

        self.log_path = tmp_path
        self.log_file_suffix = os.getenv("LOG_FILE_SUFFIX","MotoGpCalendarScraper")


    def log(self, message: str, type: LogType = LogType.INFO):
        current_time = datetime.now()
        log_file_name = f"{current_time.strftime("%Y-%m-%d")}-{self.log_file_suffix}.log"
        full_path = os.path.join(self.log_path, log_file_name)

        msg_line = f"{current_time.strftime("%H:%M:%S")} - {type.name}: {message}\n"

        with open(full_path, "a") as myfile:
            myfile.write(msg_line)
