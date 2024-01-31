import mysql.connector, os, time, psutil, win32serviceutil, subprocess, shutil #Modulos y bibliotecas

class Restart_Sara:
    # Atributos de la clase:

    #Configuracion a Base de Datos (apuntar a pruebas o produccion)
    DB_CONFIG = {
        "user": "",
        "password": "",
        "host": "",
        "database": "",} 

    #Querys para manejo de informacion en la tabla coreiser
    READ_QUERY_ESTADO = "SELECT estado FROM coreiser WHERE id = %s LIMIT 1"
    UPDATE_QUERY_MONITOREO = "UPDATE coreiser SET monitoreo = %s WHERE id = %s"
    UPDATE_QUERY_ESTADO = "UPDATE coreiser SET estado = %s WHERE id = %s"
    UPDATE_QUERY_FLUJO = "UPDATE coreiser SET flujo = %s WHERE id = %s"

    # Método constructor de la clase
    def __init__(self, value, name_service, folders_path, deployed_path, isdeploying_path, failed_path):
        # Atributos de la instancia
        self.value = value #id registro
        self.name_service = name_service #nombre servicio (WILDFLYSARA - WILDFLYPORTAL)
        self.folders_path = folders_path #ruta a carpeta standalone
        self.deployed_path = deployed_path #archivo "Funcionando"
        self.isdeploying_path = isdeploying_path #Archivo "Reiniciando"
        self.failed_path = failed_path #Archivo "Infuncional"
        self.conexion, self.cursor = self.db_conexion() # Conexión y cursor con la base de datos

    # Paso 1. Método para establecer la conexión con la base de datos
    def db_conexion(self):
        try:
            conexion = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conexion.cursor()
            return conexion, cursor
        except Exception as e:
            print(f"Error en conexion a Base de Datos: {e}")

    # Paso 2. Método para actualizar el monitoreo en la base de datos
    def update_mon(self, mon):
        self.cursor.execute(self.UPDATE_QUERY_MONITOREO, (mon, value))
        self.conexion.commit()
        print(mon)
        time.sleep(3)

    # Paso 3. método para leer el estado del servicio
    def read_service(self):
        try: 
            mon = "Consultando estado del servicio"
            self.update_mon(mon)
            for service in psutil.win_service_iter():
                if self.name_service.lower() == service.name().lower():
                    if service.status() == psutil.STATUS_STOPPED:
                        mon = "El servicio esta detenido"
                        self.update_mon(mon)
                        self.update_estado(3)
                        self.start_service()
                    else:
                        mon = "El servicio esta Ejecutandose"
                        self.update_mon(mon)
                        time.sleep(3)
                        break
        except Exception as e:
            mon = f"Error al consultar el estado del servicio: {e}"
            self.update_mon(mon)

    # Paso 4. Método para leer la existencia de los archivos (failed, isdeploying, deployed)
    def read_files(self, file_path):
        try:
            return os.path.exists(file_path)
        except Exception as e:
            mon = f"Error al consultar existencia de archivos deployment: {e}"
            self.update_mon(mon)

    # Paso 5. Método para leer el estado de la tabla en la base de datos
    def read_table_estado(self):
        self.cursor.execute(self.READ_QUERY_ESTADO, (value,))
        result = self.cursor.fetchone()
        if result:
            return int(result[0])
        time.sleep(3)

    # Paso 6. Método para verificar los archivos (failed, isdeploying, deployed)
    def verify_files(self):
        try:
            mon = "Verificando transicion de archivos deployment"
            self.update_flujo(7) 
            self.update_mon(mon)
            
            while True:
                if self.read_files(failed_path) and self.read_files(isdeploying_path): #Existencia de Failed
                    mon = "Archivo failed existe"
                    self.update_mon(mon)
                    win32serviceutil.StopService(name_service)
                    mon = "Intentando reiniciar nuevamente"
                    self.update_estado(3)
                    self.update_flujo(2) 
                    self.erase_folders(folders_path)
                    self.update_mon(mon)
                    break
                if self.read_files(isdeploying_path): #Existencia de Isdeploying
                    mon = "Archivo isdeploying existe"
                    self.update_flujo(8)
                    self.update_estado(2)
                    self.update_mon(mon)
                if self.read_files(deployed_path): #Existencia Deployed
                    self.update_estado(4)
                    self.update_flujo(9)
                    mon = "Archivo deployed existe"
                    self.update_mon(mon)
                    mon = "Iniciando Openoffice"
                    self.update_mon(mon)
                    subprocess.run(["C:\\US\\OpenOficce\\OOServiceBat.bat"], shell=True)
                    self.update_flujo(10)
                    time.sleep(3)
                    mon = "Reinicio completado"
                    self.update_mon(mon)
                    self.update_estado(1)
                    self.update_flujo(0)
                    break
                time.sleep(5)
        except Exception as e:
            mon = f"Error al verfificar archivos deployment: {e}"
            self.update_mon(mon)

    # Paso 7. Método para actualizar el flujo de reinicio en el servicio en la base de datos (%)
    def update_flujo(self, fj):
        self.cursor.execute(self.UPDATE_QUERY_FLUJO, (fj, value))
        self.conexion.commit()

    #Paso 8. Metodo para borrar carpetas (log, data, tmp):
    def erase_folders(self, folders_path):
        try: 
            mon = "Borrando carpetas log, data, tmp"
            self.update_mon(mon)
            while True:
                log = "log"
                data = "data"
                tmp = "tmp"
                folder_path_log = os.path.join(folders_path, log)
                if os.path.exists(folder_path_log):
                    shutil.rmtree(folder_path_log)
                    self.update_flujo(3)
                    self.update_estado(3)
                    mon = "Carpeta log borrada"
                    self.update_mon(mon)
                else:
                    folder_path_data = os.path.join(folders_path, data)
                    if os.path.exists(folder_path_data):
                        shutil.rmtree(folder_path_data)
                        self.update_flujo(4)
                        self.update_estado(3)
                        mon = "Carpeta data borrada"
                        self.update_mon(mon)
                    else: 
                        folder_path_tmp = os.path.join(folders_path, tmp)
                        if os.path.exists(folder_path_tmp):
                            shutil.rmtree(folder_path_tmp)
                            self.update_estado(2) #Paso 10
                            self.update_flujo(5)
                            mon = "Carpeta tmp borrada"
                            self.update_mon(mon)
                            break
                        else:
                            break
        except Exception as e:
            mon = f"Error al borrar carpetas: {e}"
            self.update_mon(mon)
            self.update_estado(2)
            self.update_flujo(5)

    # Paso 9. Método para iniciar el servicio
    def start_service(self):
        try:
            mon = "Iniciando servicio"
            self.update_mon(mon)
            win32serviceutil.StartService(name_service)
            self.update_estado(2)
            self.update_flujo(6)
            time.sleep(30)
            self.verify_files()
        except Exception as e:
            mon = f"Error al iniciar servicio: {e}"
            self.update_mon(mon)

    # Paso 10. Metodo para actualizar el estado del servicio en la base de datos
    def update_estado(self, state): 
        self.cursor.execute(self.UPDATE_QUERY_ESTADO, (state, value))
        self.conexion.commit()

#<-------------------------------------------------------------------------------->
        
    # Paso 11. Método para reiniciar el servicio
    def restart_service(self):
        try:
            self.db_conexion() #Paso 1.
            mon = "Conexion a BD abierta"
            self.update_mon(mon) #Paso 2.
            self.read_service() #Paso 3.
            mon = "Consultando Existencia de archivos deployment"
            self.update_mon(mon)
            if self.read_files(deployed_path): #Paso 4
                mon = "Archivo deployed Existe"
                self.update_mon(mon)
                state = self.read_table_estado() #Paso 5.
                if state == 1:
                    mon = "Funcionando correctamente"
                    self.update_mon(mon)
                if state == 2:
                    mon = "Reiniciando"
                    self.update_mon(mon)
                    self.verify_files() #Paso 6.
                if state == 3: 
                    mon = "Aceptando peticion de reinicio" 
                    self.update_mon(mon)
                    win32serviceutil.StopService(name_service)
                    self.update_flujo(2) #Paso 7.
                    mon = "Deteniendo servicio"
                    self.update_mon(mon)
                    self.erase_folders(folders_path) #Paso 8
                    self.start_service()  #Paso 9

        except Exception as e:
            print(f"Error al reiniciar {name_service}: {e}")

        finally:
            mon = "Conexion a BD cerrada"
            self.update_mon(mon)
            self.cursor.close()
            self.conexion.close()
            
while True:
    #Reinicio SaraWeb
    value = 1
    name_service = "WILDFLYSARA"
    folders_path = r"C:\US\Wildfly_Sara\standalone"
    deployed_path =  r"C:\US\Wildfly_Sara\standalone\deployments\SaraEAR.ear.deployed"
    isdeploying_path = r"C:\US\Wildfly_Sara\standalone\deployments\SaraEAR.ear.isdeploying"
    failed_path = r"C:\US\Wildfly_Sara\standalone\deployments\SaraEAR.ear.failed"
    sara_web = Restart_Sara(value, name_service, folders_path, deployed_path, isdeploying_path, failed_path)
    sara_web.restart_service() #Paso 11

    #Reinicio SaraPortal
    value = 2
    name_service = "WILDFLYPORTAL" 
    folders_path = r"C:\US\wildfly_Portal\standalone"
    deployed_path =  r"C:\US\wildfly_Portal\standalone\deployments\PortalSaraEAR.ear.deployed"
    isdeploying_path = r"C:\US\wildfly_Portal\standalone\deployments\PortalSaraEAR.ear.isdeploying"
    failed_path = r"C:\US\wildfly_Portal\standalone\deployments\PortalSaraEAR.ear.failed"
    sara_portal = Restart_Sara(value, name_service, folders_path, deployed_path, isdeploying_path, failed_path)
    sara_portal.restart_service() #Paso 11

    time.sleep(3)