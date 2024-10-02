import os
from enum import Enum
from datetime import datetime, timedelta

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

    def clear_logs(self):
        try:
            self.log("Managing old logs file...", LogType.INFO)

            #Clear, based on what is saved in the ".env" file, the old logs
            days_retention = os.getenv("LOG_DAYS_RETENTION", None)
            max_logs = os.getenv("LOG_MAX_FILES", None)

            #Check if at least one of those two is setted, otherwise the user don't want to delete the old logs
            if days_retention is None and max_logs is None:
                #NO LOGS POLICY SPECIFIED
                self.log("No logs to delete (No retention policy setted in the env file)", LogType.INFO)

            else:
                #get all the logs files in the directory specified that ends with the suffix provided in the env file (soarted descending)
                all_logs = sorted([f for f in os.listdir(self.log_path) if os.path.isfile(os.path.join(self.log_path, f)) and f.endswith(f"{self.log_file_suffix}.log")], reverse=True)

                if days_retention is not None:
                    self.__clear_logs_delete_log_older_than(all_logs, datetime.now(), int(days_retention))    

                if max_logs is not None:
                    #getting again the logs (if the prev step deleted some file it may interfere)
                    all_logs = sorted([f for f in os.listdir(self.log_path) if os.path.isfile(os.path.join(self.log_path, f)) and f.endswith(f"{self.log_file_suffix}.log")], reverse=True)
                    self.__clear_logs_delete_log_older_than(all_logs, int(max_logs))

            self.log("Ended process (Managing old logs file)", LogType.INFO)

        except:
            self.log("Error during the cleaning process of logs files", LogType.ERROR)
            raise



    def __clear_logs_delete_log_older_than(self, all_logs: list[str], date: datetime, days_to_keep: int) -> None:
        try:
            logs_to_keep: list[str]=[]
            
            #I'm going to cycle, starting from "date" param all the days backwards, if this exists in the logs i'm going to append this date in the "logs_to_keep" array
            #After that i'm going to delete all the logs that are not in the "logs_to_keep" array.

            tmp_days_added = 0
            tmp_date = date

            #cycling all the dates until "tmp_days_added" = 0
            while tmp_days_added != days_to_keep:
                tmp_date += timedelta(days=tmp_days_added)
                formatted_string = tmp_date.strftime("%Y-%m-%d")

                for log in all_logs:
                    if log.startswith(formatted_string):
                        logs_to_keep.append(log)

                tmp_days_added += 1
            
            #deleting all the logs
            for log in all_logs:
                if not any(item == log for item in logs_to_keep):
                    path_to_delete = os.path.join(self.log_path, log)
                    os.remove(path=path_to_delete)

                    self.log(f"\tDeleted log {log} in {path_to_delete}", LogType.INFO)

        except:
            msg = "Error getting the logs file older than n days.\n"
            msg += f"\t\tall_logs: {", ".join(all_logs)}\n"
            msg += f"\t\tdate: {date.strftime("%Y-%m-%d")}\n"
            msg += f"\t\tdays_to_keep: {days_to_keep}"
            self.log(msg, LogType.ERROR)
            raise
        

    def __clear_logs_delete_log_older_than(self, all_logs: list[str], max_files:int) -> None:
        try:
            logs_len = len(all_logs)
            if logs_len <= max_files:
                #NO LOGS TO DELETE
                return

            #Get logs to delete
            num_files_to_delete = logs_len - max_files
            logs_to_delete = all_logs[-num_files_to_delete:]

            for log in logs_to_delete:
                path_to_delete = os.path.join(self.log_path, log)
                os.remove(path=path_to_delete)

                self.log(f"\tDeleted log {log} in {path_to_delete}", LogType.INFO)

        except:
            msg = "Error getting the logs file older than n days.\n"
            msg += f"\t\tall_logs: {", ".join(all_logs)}\n"
            msg += f"\t\tmax_files: {max_files}"
            self.log(msg, LogType.ERROR)
            raise
        