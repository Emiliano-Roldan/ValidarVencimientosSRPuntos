import time
import requests
import win32serviceutil
from logger import logger
import win32event
import schedule
import datetime
import win32service
import servicemanager  # Importa servicemanager
import sys

#pyinstaller --onefile --noconsole --hidden-import=win32timezone --hidden-import=win32service --hidden-import=win32event main.py

class MyWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PuntosVencimientosSvc"
    _svc_display_name_ = "Servicio Puntos Vencimientos"
    _svc_description_ = "Sistema automatizado de validación de puntos"

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.log = logger()

    def http_request(self):
        """Realiza la solicitud HTTP."""
        url = "http://delivery.emestudio.com.uy:3586/php/validarvencimiento.php"  # Cambiá esto por tu URL real
        payload = {"grupoid": 2}
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            self.log.write_to_log(f"[{datetime.datetime.now()}] Respuesta: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            self.log.write_to_log(f"[{datetime.datetime.now()}] Error en la solicitud: {e}")

    def schedule_tasks(self):
        """Elimina la tarea existente si ya está programada y la vuelve a crear con la nueva hora."""
        self.log.write_to_log("Reprogramando tarea de validación de vencimientos.")

        # Buscar y eliminar la tarea si ya existe
        for job in schedule.get_jobs():
            if job.job_func == self.http_request:
                schedule.cancel_job(job)
                self.log.write_to_log("Tarea anterior eliminada.")

        # Crear la nueva tarea con la hora actualizada
        nueva_hora = "08:00"  # Podrías hacer que esta hora sea configurable
        schedule.every().day.at(nueva_hora).do(self.http_request)
        self.log.write_to_log(f"Tarea de validación reprogramada para las {nueva_hora}.")

    def SvcStop(self):
        """Detiene el servicio."""
        self.log.write_to_log("Deteniendo servicio...")
        self.running = False
        # Notifica al SCM que el servicio se está deteniendo
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        # Notifica al SCM que el servicio se ha detenido
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        self.log.write_to_log("Servicio detenido correctamente.")

    def SvcDoRun(self):
        """Ejecuta el servicio."""
        try:
            # Notifica al SCM que el servicio se está iniciando
            self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
            self.log.write_to_log("Iniciando servicio...")

            # Programa las tareas
            self.schedule_tasks()

            # Notifica al SCM que el servicio se ha iniciado correctamente
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log.write_to_log("Servicio iniciado correctamente.")

            # Bucle principal del servicio
            while self.running:
                self.log.write_to_log("Ejecutando tareas programadas...")
                schedule.run_pending()
                time.sleep(30)  # Evita uso excesivo de CPU

        except Exception as e:
            self.log.write_to_log(f"Error en el servicio: {e}")
            # Notifica al SCM que el servicio se ha detenido debido a un error
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            return

        # Notifica al SCM que el servicio se ha detenido correctamente
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        self.log.write_to_log("Servicio detenido correctamente.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Si no se pasan argumentos, ejecuta el servicio
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Si se pasan argumentos (install, start, stop, etc.), maneja el comando
        win32serviceutil.HandleCommandLine(MyWindowsService)