import os
from datetime import datetime

class logger:
    def __init__(self):
        self.log_folder = "C:\\nationalsoft\\log_vencimientos\\" #C:\\nationalsoft\\EnvioVentaDisco\\
        self.log_filename = f"{self.log_folder}/Vencimientos_puntos{datetime.now().strftime('%Y-%m-%d')}.log"
        self.create_log_folder()
        self.create_log_file()

    def create_log_folder(self):
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

    def create_log_file(self):
        if not os.path.exists(self.log_filename):
            with open(self.log_filename, 'w') as file:
                file.write(f"Log creado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def write_to_log(self, message):
        with open(self.log_filename, 'a') as file:
            file.write(f"=============================================================\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")