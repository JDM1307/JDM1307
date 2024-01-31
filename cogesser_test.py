import mysql.connector, subprocess, time
from colorama import init, Fore #Biblioteca para imprimir mensajes a color en consola
from datetime import datetime

init() #Inicializar Fore (colorama)
class Servers_gestion:
    #<--------------------------------------------------------------MÉTODOS---------------------------------------------------------------->
    # METODO CONSTRUCTOR DE LA CLASE
    def __init__(self):
        # Atributos de la instancia:
        self.DB_CONFIG = { #Configuracion a Base de Datos
            "user": "",
            "password": "",
            "host": "",
            "database": ""
        }    

        #Querys para gestion de informacion en las tablas:
        #cosequis_cogesbats
        self.RQ_MACHINE_ID_REQUEST = "SELECT id FROM cogesequis_cogesbats WHERE sol_equi = 1 OR sol_equi = 2" #Consultar id de registro que presente solicitud
        self.RQ_MACHINE_REQUEST_TYPE = "SELECT sol_equi FROM cogesequis_cogesbats WHERE id= %s LIMIT 1" #Consultar tipo de solicitud del registro (0:ninguna, 1:Maquina, 2:Servicio)
        self.RQ_MACHINE_ID = "SELECT cogesequis_id FROM cogesequis_cogesbats WHERE id= %s LIMIT 1" #Consultar id de equipo asociado a registro que presenta solicitud
        self.UQ_MACHINE_MON = "UPDATE cogesequis_cogesbats SET mon_equi = %s WHERE id = %s" #Actuualizar "mon_equi" en cogesequis_cogesbats
        self.UQ_MACHINE_REQUEST = "UPDATE cogesequis_cogesbats SET sol_equi = %s WHERE id = %s" #Actuualizar "sol_equi" en cogesequis_cogesbatss

        #cogesequis:
        self.RQ_MACHINE_STATUS = "SELECT est_equi FROM cogesequis WHERE id= %s LIMIT 1" #Consultar valor de "est_equi" en cogesequis (0:off, 1:on)
        self.RQ_MACHINE_1_PARAMETER = "SELECT param_1 FROM cogesequis WHERE id = %s LIMIT 1" #Consultar 1° parametro (IP) (recibe bat)
        self.RQ_MACHINE_2_PARAMETER = "SELECT param_2 FROM cogesequis WHERE id = %s LIMIT 1" #Consultar el 2° parametro (recibe bat)
        self.RQ_MACHINE_3_PARAMETER = "SELECT param_3 FROM cogesequis WHERE id = %s LIMIT 1" #Consultar el 3° parametro (recibe bat)
        self.RQ_MACHINE_4_PARAMETER = "SELECT param_4 FROM cogesequis WHERE id = %s LIMIT 1" #Consultar el 4° parametro (recibe bat)
        self.RQ_MACHINE_DES = "SELECT des_equi FROM cogesequis WHERE id = %s LIMIT 1" #Consultar descripcion maquina (requerido para monitoreo)
        self.UQ_MACHINE_STATUS = "UPDATE cogesequis SET est_equi = %s WHERE id = %s" #Actualizar la columna  "est_equi" en cogesequis (0:off, 1:on)
        
        #cogesbats:
        self.RQ_BAT_ID = "SELECT cogesbats_id FROM cogesequis_cogesbats WHERE id= %s LIMIT 1" #Consultar id de bat asignado al equipo 
        self.RQ_BAT_NAME = "SELECT nom_bat FROM cogesbats WHERE id = %s LIMIT 1" #Consultar la descripcion del bat a aplicar (requerido para el monitoreo)
        self.RQ_BAT_DES = "SELECT des_bat FROM cogesbats WHERE id = %s LIMIT 1" #Consultar la descripcion del bat a aplicar (requerido para el monitoreo)
        self.RQ_BAT_PATH = "SELECT rut_bat FROM cogesbats WHERE id = %s LIMIT 1" #Consultar la ruta del bat para acceder al archivo
        self.RQ_BAT_TYPE = "SELECT tip_bat FROM cogesbats WHERE id = %s LIMIT 1" #Consultar el tipo de bat para determinar el tipo de ejecucion
        self.RQ_NAME_SERVICE = "SELECT nom_serv_bat FROM cogesbats WHERE id = %s LIMIT 1" #Consultar el nombre del servicio asociado al bat de tipo servicio (parametro secundario)
        self.RQ_DES_SERVICE = "SELECT des_serv_bat FROM cogesbats WHERE id = %s LIMIT 1" #Consultar descripcion del servicio (requerido para monitoreo)

        #instancias locales:
        self.machine_id_request = None # -Instancia con el valor (id) de los registros (equipos) en cogesequis_cogesbats.
        self.machine_id = None # -Intancia con el valor (id) del equipo asociado al registro en cogesequis_cogesbats.
        self.bat_id = None # -Instancia con el valor (id) del bat asociado al equipo asociado en cogesequis_cogesbats.
        self.mon = "" # -Instancia vacia para almacenar valores en cadena (monitoreo).
    
    # 1. METODO PARA ESTABLECER LA CONEXION A BD
    def open_db_conexion(self):
        try:
            conexion = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conexion.cursor()
            return conexion, cursor
        except Exception as e:
            print(f"{Fore.RED}1. open_db_conexion() Error:{Fore.RESET} {e}")
            return None, None

    # 1. MÉTODO PARA CERRAR CONEXION A BD
    def close_db_conexion(self, conexion, cursor):
        try:
            cursor, conexion = self.open_db_conexion()
            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"{Fore.RED}1. close_db_conexion() Error:{Fore.RESET} {e}")

    # MÉTODO PARA CONSULTAR DESCRIPCION DE MAQUINA ASOCIADA
    def rq_machine_des(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.machine_id = self.rq_machine_id()
                cursor.execute(self.RQ_MACHINE_DES, (self.machine_id,))
                result = cursor.fetchone()
                if result:
                    machine_des = str(result[0])
                    return machine_des
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}rq_machine_des() Error:{Fore.RESET} {e}")
                moni = f"\nError al obtener descripcion del equipo asociado: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
              self.close_db_conexion(conexion, cursor) 

    # MÉTODO PARA CONSULTAR NOMBRE BAT ASOCIADO
    def rq_bat_name(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.bat_id = self.rq_bat_id()
                cursor.execute(self.RQ_BAT_NAME, (self.bat_id,))
                result = cursor.fetchone()
                if result:
                    bat_name = str(result[0])
                    return bat_name
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}rq_bat_name() Error:{Fore.RESET} {e}")
                moni = f"\nError al obtener nombre del bat asociado: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
              self.close_db_conexion(conexion, cursor)

    # MÉTODO PARA CONSULTAR DESCRIPCION DE BAT ASOCIADO
    def rq_bat_des(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.bat_id = self.rq_bat_id()
                cursor.execute(self.RQ_BAT_DES, (self.bat_id,))
                result = cursor.fetchone()
                if result:
                    bat_des = str(result[0])
                    return bat_des
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}rq_bat_des() Error:{Fore.RESET} {e}")
                moni = f"\nError al obtener descripcion del bat asociado: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
              self.close_db_conexion(conexion, cursor)

    # MÉTODO PARA CONSULTAR DESCRIPCION DE SERVICIO
    def rq_des_service(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.bat_id = self.rq_bat_id()
                cursor.execute(self.RQ_DES_SERVICE, (self.bat_id,))
                result = cursor.fetchone()
                if result:
                    serv_des = str(result[0])
                    return serv_des
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}rq_des_service() Error:{Fore.RESET} {e}")
                moni = f"\nError al obtener descripcion del servicio: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
              self.close_db_conexion(conexion, cursor)

    # METODO PARA ACTUALIZAR MONITOREO (COLUMNA: "mon_equi") EN TABLA "cogesequis_cogesbats"  
    def uq_machine_mon(self, mon):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.machine_id_request = self.rq_machine_id_request()
                cursor.execute(self.UQ_MACHINE_MON, (mon, self.machine_id_request))
                conexion.commit()
            except Exception as e:
                print(f"{Fore.RED}uq_machine_mon() Error:{Fore.RESET} {e}")
            finally:
                self.close_db_conexion(conexion, cursor)

    # MÉTODO PARA ACTUALIZAR ESTADO MAQUINA EN cogesequis "est_equi"
    def uq_machine_status(self, status):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.machine_id = self.rq_machine_id()
                cursor.execute(self.UQ_MACHINE_STATUS, (status, self.machine_id))
                conexion.commit()
            except Exception as e:
                print(f"{Fore.RED}uq_machine_status() Error:{Fore.RESET} {e}")
            finally:
                self.close_db_conexion(conexion, cursor)

    # MÉTODO PARA ACTUALIZAR LA SOLICITUD DEL REGISTRO (MAQUINA)
    def uq_machine_request(self, request):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.machine_id_request = self.rq_machine_id_request()
                cursor.execute(self.UQ_MACHINE_REQUEST, (request, self.machine_id_request))
                conexion.commit()
            except Exception as e:
                print(f"{Fore.RED}uq_machine_request() Error:{Fore.RESET} {e}")
            finally:
                self.close_db_conexion(conexion, cursor)

    # 2. METODO PARA CONSULTAR ID DE REGISTROS CON SOLICITUDES DISPONIBLES
    def rq_machine_id_request(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                cursor.execute(self.RQ_MACHINE_ID_REQUEST)
                row = cursor.fetchone()
                if row:
                    request_machine_id = row[0]
                    return request_machine_id
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}2.rq_machine_id_request() Error:{Fore.RESET} {e}")
            finally:
                self.close_db_conexion(conexion, cursor)

    # 3. METODO PARA VERIFICAR EL TIPO DE SOLICITUD (0: sin solicitud, 1: solicitud equipo, 2: solicitud servicio) DE LA MAQUINA.
    def rq_machine_request_type(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try: 
                self.machine_id_request = self.rq_machine_id_request()
                cursor.execute(self.RQ_MACHINE_REQUEST_TYPE, (self.machine_id_request,))
                result = cursor.fetchone()
                if result:
                    request = str(result[0])
                    return request
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}3. rq_machine_request_type Error:{Fore.RESET} {e}")
                moni = f"\n3. Error al aceptar la solicitud: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon) 
            finally:
              self.close_db_conexion(conexion, cursor)   

    # 4. METODO PARA CONSULTAR ID DE EQUIPO ASOCIADO A REGISTRO QUE PRESENTA SOLICITUD
    def rq_machine_id(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.machine_id_request = self.rq_machine_id_request()
                cursor.execute(self.RQ_MACHINE_ID, (self.machine_id_request,))
                result = cursor.fetchone()
                if result:
                    id_machine = result[0]
                    return id_machine
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}4. rq_machine_id() Error:{Fore.RESET} {e}")
                moni = f"\n4. Error al obtener el equipo asociado: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
              self.close_db_conexion(conexion, cursor) 

    # 5. MÉTODO PARA CONSULTAR ESTADO DE LA MAQUINA DESDE BAT
    def read_machine_status(self):
        try:
            # Parámetros
            parameter_1 = self.rq_machine_1_parameter()
            # Ruta del archivo bat
            bat_path = r"\\cobogfs01\Compartida\Sistemas\Temporal\bats_prueba\status_machine.bat" #Agregar la ruta al bata que consulta el estado de la maquina

            if bat_path:
                # Comando y parámetros
                command = [bat_path, parameter_1]
                # Ejecutar comando y capturar la salida
                run_command = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Verificar el código de retorno para determinar el estado de la máquina
                if run_command.returncode == 0:
                    status = "0"
                elif run_command.returncode == 1:
                    status = "1"
                else:
                    status = "0"

                # Actualizar el estado de la máquina
                self.uq_machine_status(status)

                # Retornar la salida y el objeto de la ejecución del comando
                return run_command
            else:
                print(f"{Fore.BLUE}5. Verificando estado de la maquina:{Fore.RESET} Error:", run_command.returncode)
                return None
        except Exception as e:
            print(f"{Fore.RED}5. read_machine_status() Error:{Fore.RESET} {e}")
            moni = f"\n5. Error al verificar el estado de la maquina: {e} "
            self.mon += moni
            self.uq_machine_mon(self.mon)
        
    # 6. METODO PARA CONSULTAR EL ESTADO (1:on, 0:off) DEL EQUIPO ASOCIADO EN cogesequis "est_equi"
    def rq_machine_status(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:  
                self.machine_id = self.rq_machine_id()
                cursor.execute(self.RQ_MACHINE_STATUS, (self.machine_id,))
                result = cursor.fetchone()
                if result:
                    status = str(result[0])
                    return status
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}6. rq_machine_status() Error:{Fore.RESET} {e}")
                moni = f"\n6. Error al consultar estado del equipo: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
                self.close_db_conexion(conexion, cursor) 

    #7. METODO PARA CONSULTAR EL ID  DEL BAT ASOCIADO AL EQUIPO ASOCIADO
    def rq_bat_id(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.machine_id_request = self.rq_machine_id_request()
                cursor.execute(self.RQ_BAT_ID, (self.machine_id_request,))
                result = cursor.fetchone()
                if result:
                    bat_id = result[0]
                    return bat_id
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}7. rq_bat_id() Error:{Fore.RESET} {e} ")
                moni = f"\n7. Error al obtener el id del Bat asociado: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
                self.close_db_conexion(conexion, cursor)

    #8. METODO PARA CONSULTAR EL TIPO DE BAT ASOCIADO
    def rq_bat_type(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:   
                self.bat_id = self.rq_bat_id()
                cursor.execute(self.RQ_BAT_TYPE, (self.bat_id,))
                result = cursor.fetchone()
                if result:
                    bat_type = str(result[0])
                    return bat_type
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}8. rq_bat_type() Error:{Fore.RESET} {e}")
                moni = f"\n8. Error al consultar el tipo de Bat: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
                self.close_db_conexion(conexion, cursor)
            
    #9. METODO PARA OBTENER PARAMETRO 1 QUE PERMITE CONECTAR CON MAQUINA REMOTA "IP" (RECIBE BAT)
    def rq_machine_1_parameter(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:
                self.machine_id = self.rq_machine_id()
                cursor.execute(self.RQ_MACHINE_1_PARAMETER, (self.machine_id,))
                result = cursor.fetchone()
                if result:
                    ip_machine = str(result[0])
                    return ip_machine
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}9. rq_machine_1_parameter() Error:{Fore.RESET} {e}")
                moni = f"9. Error al obtener parametro conexion maquina remota: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
                self.close_db_conexion(conexion, cursor)

    #9. METODO PARA OBTENER PARAMETRO 2 (RECIBE BAT)
    def rq_machine_2_parameter(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:   
                self.machine_id = self.rq_machine_id()
                cursor.execute(self.RQ_MACHINE_2_PARAMETER, (self.machine_id,))
                result = cursor.fetchone()
                if result:
                    prmtr_2 = str(result[0])
                    return prmtr_2
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}9. rq_machine_2_parameter() Error:{Fore.RESET} {e}")
                moni = f"9. Error al consultar parametro 2 de la maquina: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
                self.close_db_conexion(conexion, cursor)

    #9. METODO PARA OBTENER PARAMETRO 3 (RECIBE BAT)
    def rq_machine_3_parameter(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:   
                self.machine_id = self.rq_machine_id()
                cursor.execute(self.RQ_MACHINE_3_PARAMETER, (self.machine_id,))
                result = cursor.fetchone()
                if result:
                    prmtr_3 = str(result[0])
                    return prmtr_3
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}10. rq_machine_3_parameter() Error:{Fore.RESET} {e}")
                moni = f"10. Error al consultar parametro 3 de la maquina: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
                self.close_db_conexion(conexion, cursor)

     #10. METODO PARA OBTENER PARAMETRO "DIRECCION MAC" QUE RECIBE EL BAT
    
    #9. METODO PARA OBTENER PARAMETRO 4 (RECIBE BAT)
    def rq_machine_4_parameter(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:   
                self.machine_id = self.rq_machine_id()
                cursor.execute(self.RQ_MACHINE_4_PARAMETER, (self.machine_id,))
                result = cursor.fetchone()
                if result:
                    mac_machine = str(result[0])
                    return mac_machine
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}10. rq_machine_4_parameter() Error:{Fore.RESET} {e}")
                moni = f"10. Error al consultar parametro 4 de la maquina: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
                self.close_db_conexion(conexion, cursor)

    #9. MÉTODO PARA OBTNER PARAMETRO 5 (nombre servicio) (RECIBE BAT)
    def rq_name_service(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:   
                self.bat_id = self.rq_bat_id()
                cursor.execute(self.RQ_NAME_SERVICE, (self.bat_id,))
                result = cursor.fetchone()
                if result:
                    service_name = str(result[0])
                    return service_name
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}rq_name_service() Error:{Fore.RESET} {e}")
                moni = f"Error al consultar parametro 5 de la maquina: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon)
            finally:
                self.close_db_conexion(conexion, cursor)

    #10. METODO PARA OBTENER LA RUTA DEL BAT ASOCIADO
    def rq_bat_path(self):
        conexion, cursor = self.open_db_conexion()
        if conexion and cursor:
            try:   
                self.bat_id = self.rq_bat_id()
                cursor.execute(self.RQ_BAT_PATH, (self.bat_id,))
                result = cursor.fetchone()
                if result:
                    bat_path = str(result[0])
                    return bat_path
                else:
                    return None
            except Exception as e:
                print(f"{Fore.RED}10. rq_bat_path() Error:{Fore.RESET} {e}")
                moni = f"10. Error al consultar la ruta del archivo Bat asociado: {e} "
                self.mon += moni
                self.uq_machine_mon(self.mon) 
            finally:
                self.close_db_conexion(conexion, cursor)
            
    #11. METODO PARA EJECUTAR EL BAT EQUIPO ASOCIADO
    def run_bat_machine(self):
        try:
            #parametros:
            prmtr_1 = self.rq_machine_1_parameter()
            prmtr_2 = self.rq_machine_2_parameter()
            prmtr_3 = self.rq_machine_3_parameter()
            prmtr_4 = self.rq_machine_4_parameter()
            #ruta del bat
            bat_path = rf"{self.rq_bat_path()}"

            if bat_path:
                # Ruta del archivo .bat y parámetros
                command = [bat_path, prmtr_1, prmtr_2, prmtr_3, prmtr_4] #agregar: parameter_4
                print(f"{Fore.GREEN}11. Ejecutando archivo Bat:{Fore.RESET} '{self.rq_bat_des()}' Iniciado")
                moni = "\n11. Iniciando operacion... "
                self.mon += moni
                self.uq_machine_mon(self.mon)
                #Ejecutar comando y capturar la salida
                run_command = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                # Almacenar la salida en una variable
                console_output = run_command.stdout
                #condicionar ejecucion
                if run_command.returncode == 0:
                    print(f"{Fore.LIGHTCYAN_EX}<----Salida Consola Bat---->{Fore.RESET}\n{console_output}{Fore.LIGHTCYAN_EX}<------------------------->{Fore.RESET}")
                    moni = f"\n<----Salida Consola Bat---->\n{console_output}<-------------------------> "
                    self.mon += moni
                    self.uq_machine_mon(self.mon)
                else:
                    print(f"{Fore.LIGHTCYAN_EX}<----Salida Consola Bat---->\n{console_output}<------------------------->{Fore.RESET}")
                    moni = f"\n<----Salida Consola Bat---->\n{console_output}<-------------------------> "
                    self.mon += moni
                    self.uq_machine_mon(self.mon)
                # Retornar la salida y el objeto de la ejecución del comando
                return console_output, run_command  
            else:
                print(f"{Fore.BLUE}11. Hubo un error al ejecutar el archivo .bat. Codigo de retorno:{Fore.RESET}", run_command.returncode)
                moni = f"\nNo fue posible ejecutar el bat: {run_command.returncode}"
                self.mon += moni
                self.uq_machine_mon(self.mon)
                return None, None
        except Exception as e:
            print(f"{Fore.RED}11. run_bat_machine() Error verifique que la ruta, archivo bat y parametros sean correctos:{Fore.RESET} {e}")  #IMPORTANTE: LA RUTA DEL BAT NO DEBE SER LOCAL TANTO EN MAQUINA ADMIN COMO EN MAQUINA REMOTA usar: \\cobogfs01\Compartida\Sistemas\Temporal\bats_prueba
            moni = f"\n11. Error al ejecutar bat asociado, verifique que la ruta, archivo bat y parametros sean correctos: {e} "
            self.mon += moni
            self.uq_machine_mon(self.mon) 

    #11. METODO PARA EJECUTAR EL BAT SERVICIO ASOCIADO
    def run_bat_service(self):
        try:
            # Parámetros
            prmtr_1 = self.rq_machine_1_parameter()
            prmtr_2 = self.rq_machine_2_parameter()
            prmtr_3 = self.rq_machine_3_parameter()
            prmtr_4 = self.rq_name_service()
            # Ruta del bat
            bat_path = rf"{self.rq_bat_path()}"
            
            if bat_path:
                # Ruta del archivo .bat y parámetros
                command = [bat_path, prmtr_1, prmtr_2, prmtr_3, prmtr_4]
                print(f"{Fore.GREEN}11. Ejecutando archivo Bat:{Fore.RESET} '{self.rq_bat_des()}' Iniciado")
                moni = "\n11. Iniciando operacion... "
                self.mon += moni
                self.uq_machine_mon(self.mon)
                # Ejecutar comando y capturar la salida
                run_command = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                # Almacenar la salida en una variable
                console_output = run_command.stdout
                #condicionar ejecucion
                if run_command.returncode == 0:
                    print(f"{Fore.LIGHTCYAN_EX}<----Salida Consola Bat---->{Fore.RESET}\n{console_output}{Fore.LIGHTCYAN_EX}<------------------------->{Fore.RESET}")
                    moni = f"\n<----Salida Consola Bat---->\n{console_output}<-------------------------> "
                    self.mon += moni
                    self.uq_machine_mon(self.mon)
                else:
                    print(f"{Fore.LIGHTCYAN_EX}<----Salida Consola Bat---->\n{console_output}<------------------------->{Fore.RESET}")
                    moni = f"\n<----Salida Consola Bat---->\n{console_output}<-------------------------> "
                    self.mon += moni
                    self.uq_machine_mon(self.mon)
                # Retornar la salida y el objeto de la ejecución del comando
                return console_output, run_command
            else:
                print(f"{Fore.BLUE}11. Hubo un error al ejecutar el archivo .bat. Codigo de retorno:{Fore.RESET}", run_command.returncode)
                moni = f"\nNo fue posible ejecutar el bat: {run_command.returncode}"
                self.mon += moni
                self.uq_machine_mon(self.mon)
                return None, None
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}11. run_bat_machine() Error verifique que la ruta, archivo bat y parametros sean correctos:{Fore.RESET} {e}")  #IMPORTANTE: LA RUTA DEL BAT NO DEBE SER LOCAL TANTO EN MAQUINA ADMIN COMO EN MAQUINA REMOTA usar: \\cobogfs01\Compartida\Sistemas\Temporal\bats_prueba
            moni = f"\n11. Error al ejecutar bat asociado, verifique que la ruta, archivo bat y parametros sean correctos: {e} "
            self.mon += moni
            self.uq_machine_mon(self.mon) 
   
    #<--------------------------COGESSERVERS------------------------------------>
    # 12. MÉTODO PARA GESTIONAR SERVIDORES Y SERVICIOS
    def cogesserver_start(self):

        #PASO1. VERIFIQUE LA CONEXION A BD
        if self.open_db_conexion():
            dt = datetime.now()
            print(f"\n{Fore.LIGHTCYAN_EX}Fecha: {dt}{Fore.RESET}{Fore.GREEN}\n1. Conexion BD:{Fore.RESET} Establecida")

            #PASO2. OBTENGA EL REGISTRO CON SOLICITUD DISPONIBLE
            if self.rq_machine_id_request():
                print(f"{Fore.GREEN}2. ID registro con solicitud:{Fore.RESET} ({self.rq_machine_id_request()})")
                moni = f"Fecha: {dt} \n1. Conexion BD Establecida \n2. Aceptando Solcitud... "
                self.mon += moni
                self.uq_machine_mon(self.mon)

                #PASO3. VERIFIQUE EL TIPO DE SOLICITUD (1:MAQUINA - 2:SERVICIO - !=:DESCONOCIDO)
                #<-------SOLICITUD 1:MAQUINA------------->
                if self.rq_machine_request_type() == "1":
                    print(f"{Fore.GREEN}3. Tipo solicitud:{Fore.RESET} Maquina")
                    moni = "\n3. Solicitud 'Ejecutar en Maquina' "
                    self.mon += moni
                    self.uq_machine_mon(self.mon)

                    #PASO4. OBTENGA LA MAQUINA ASOCIADA
                    if self.rq_machine_id():
                        print(f"{Fore.GREEN}4. ID maquina asociada:{Fore.RESET} ({self.rq_machine_id()}) - {self.rq_machine_des()}")
                        moni = f"\n4. Conectando con maquina asociada ({self.rq_machine_des()})... "
                        self.mon += moni
                        self.uq_machine_mon(self.mon)

                        #PASO5. OBTENGA ESTADO DE MAQUINA Y ACTUALICE EN TABLA "cogesequis"
                        run_command = self.read_machine_status()
                        if run_command.returncode == 1:
                            print(f"{Fore.GREEN}5. Verificando estado de la maquina:{Fore.RESET} Encendida")
                        else:
                            print(f"{Fore.GREEN}5. Verificando estado de la maquina:{Fore.RESET} Apagada")
                        moni = f"\n5. Verificando estado de la maquina (0:off , 1:on): {run_command.returncode} "
                        self.mon += moni
                        self.uq_machine_mon(self.mon)
                        #PASO5 FIN

                        #PASO6. CONSULTE EL ESTADO DEL EQUIPO EN TABLA (0:APAGADO - 1:ENCENDIDO)
                        if self.rq_machine_status() == "0" or self.rq_machine_status() == "1":
                            print(f"{Fore.GREEN}6. Intentando acceder a la maquina...{Fore.RESET}")
                            moni = "\n6. Intentando acceder a la maquina... "
                            self.mon += moni
                            self.uq_machine_mon(self.mon)
                            
                            #PASO7. OBTENGA EL ID DEL BAT ASOCIADO AL EQUIPO
                            if self.rq_bat_id():
                                print(f"{Fore.GREEN}7. ID Bat asociado:{Fore.RESET} ({self.rq_bat_id()}) - {self.rq_bat_name()}")
                                moni = f"\n7. Bat asociado ({self.rq_bat_name()}), obtenido "
                                self.mon += moni
                                self.uq_machine_mon(self.mon)
                                
                                #PASO8. VALIDE EL TIPO DE BAT ASOCIADO CON EL TIPO DE SOLICITUD (1:EQUIPO - 2:SERVICIO)
                                if self.rq_bat_type() == self.rq_machine_request_type():
                                    print(f"{Fore.GREEN}8. Congruencia tipo Bat, tipo solicitud:{Fore.RESET}  Valido")
                                    moni = "\n8. Tipo Bat, maquina "
                                    self.mon += moni
                                    self.uq_machine_mon(self.mon)

                                    #<---------INICIO PRINT PARAMETROS, PARA VALIDAR VALORES OBTENIDOS-------->
                                    #PASO9. OBTENGA EL PARAMETRO DE CONEXION A MAQUINA REMOTA (IP) (RECIBE BAT)
                                    if self.rq_machine_1_parameter():
                                        print(f"{Fore.GREEN}9. Parametro conexion maquina remota:{Fore.RESET} {self.rq_machine_1_parameter()}")
                                        moni = "\n9. Parametro de conexion a maquina remota, obtenido "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    else:
                                        print(f"{Fore.BLUE}9. Parametro conexion maquina remota:{Fore.RESET} Null")
                                        moni = "\n9. Parametro de conexion a maquina remota, obtenido:Null "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                        
                                    #PASO9. OBTENGA EL PARAMETRO 2 (RECIBE BAT)
                                    if self.rq_machine_2_parameter():
                                        print(f"{Fore.GREEN}9. Parametro 2:{Fore.RESET} {self.rq_machine_2_parameter()}")
                                        moni = "\n9. Parametro 2, obtenido "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    else:
                                        print(f"{Fore.BLUE}9. Parametro 2:{Fore.RESET} {self.rq_machine_2_parameter()} Null")
                                        moni = "\n9. Parametro 2, obtenido:Null "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)

                                    #PASO9 CONSULTE EL PARAMETRO 3 (RECIBE BAT)
                                    if self.rq_machine_3_parameter():
                                        print(f"{Fore.GREEN}9. Parametro 3:{Fore.RESET} {self.rq_machine_3_parameter()}")
                                        moni = "\n9. Parametro 3, obtenido "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    else:
                                        print(f"{Fore.BLUE}9. Parametro 3:{Fore.RESET} {self.rq_machine_3_parameter()} Null")
                                        moni = "\n9. Parametro 3, obtenido:Null "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)

                                    #PASO9 CONSULTE EL PARAMETRO 4 (RECIBE BAT)
                                    if self.rq_machine_4_parameter():
                                        print(f"{Fore.GREEN}9. Parametro 4:{Fore.RESET} {self.rq_machine_4_parameter()}")
                                        moni = "\n9. Parametro 4, obtenido "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    else:
                                        print(f"{Fore.BLUE}9. Parametro 4:{Fore.RESET} {self.rq_machine_4_parameter()} Null")
                                        moni = "\n9. Parametro 4, obtenido:Null "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    
                                    #PASO9 FIN
                                    #<---------FIN PRINT PARAMETROS, PARA VALIDAR VALORES OBTENIDOS-------->

                                    #PASO10. OBTENGA LA RUTA DEL ARCHIVO BAT
                                    if self.rq_bat_path():
                                        print(f"{Fore.GREEN}10. Ruta Bat asociado:{Fore.RESET} {self.rq_bat_path()}")
                                        moni = "\n10. Ruta Bat asociado, obtenida "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)

                                        #PASO11. EJECUTE EL BAT ASOCIADO (MAQUINA)
                                        self.run_bat_machine()
                                        print(f"{Fore.GREEN}11. Ejecutando archivo Bat:{Fore.RESET} Finalizado")
                                        moni = "\n11. Operacion finalizada "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                        self.read_machine_status()
                                        request = "0"
                                        self.uq_machine_request(request)
                                        #PASO11 FIN

                                    else:
                                        print(f"{Fore.BLUE}10. Ruta Bat asociado:{Fore.RESET} {self.rq_bat_path()} Desconocida")
                                        moni = "\n10. Ruta Bat asociado, no obtenida "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    #PASO10 FIN

                                else:
                                    print(f"{Fore.BLUE}8. Congruencia tipo Bat, tipo solicitud:{Fore.RESET}  Invalido")
                                    moni = f"\n8. Tipo bat, invalido"
                                    self.mon += moni
                                    self.uq_machine_mon(self.mon)
                                #PASO8 FIN

                            else:
                                print(f"{Fore.BLUE}7. ID Bat asociado:{Fore.RESET} No se obtuvo Bat asociado")
                                moni = "\n7. Bat asociado, no obtenido "
                                self.mon += moni
                                self.uq_machine_mon(self.mon)
                            #PASO7 FIN
                                 
                        else:
                            print(f"{Fore.BLUE}6. Intentando acceder a maquina...{Fore.RESET} No Permitido: Estado de maquina desconocido")
                            moni = "\n6. Acceso a maquina, no accesible: Estado de maquina desconocido "
                            self.mon += moni
                            self.uq_machine_mon(self.mon)
                        #PASO6 FIN
                    
                    else:
                        print(f"{Fore.BLUE}4. ID maquina asociada:{Fore.RESET} No se obtuvo maquina asociada")
                        moni = "\n4. Conectando con maquina asociada, fallida "
                        self.mon += moni
                        self.uq_machine_mon(self.mon)
                    #PASO4 FIN
                        
                #<-------SOLICITUD SERVICIO------------->
                elif self.rq_machine_request_type() == "2":
                    print(f"{Fore.GREEN}3. Tipo solicitud:{Fore.RESET} Servicio")
                    moni = "\n3. Solicitud 'Ejecutar en Servicio' "
                    self.mon += moni
                    self.uq_machine_mon(self.mon)

                    #PASO4. OBTENGA LA MAQUINA
                    if self.rq_machine_id():
                        self.machine_id = self.rq_machine_id()
                        print(f"{Fore.GREEN}4. ID maquina asociada:{Fore.RESET} ({self.rq_machine_id()}) - {self.rq_machine_des()} ")
                        moni = f"\n4. Conectando con maquina asociada ({self.rq_machine_des()})...  "
                        self.mon += moni
                        self.uq_machine_mon(self.mon)
                        
                        #PASO5. OBTENGA ESTADO DE MAQUINA Y ACTUALICE EN TABLA "cogesequis"
                        run_command = self.read_machine_status()
                        if run_command.returncode == 1:
                            print(f"{Fore.GREEN}5. Verificando estado de la maquina:{Fore.RESET} Encendida")
                        else:
                            print(f"{Fore.GREEN}5. Verificando estado de la maquina:{Fore.RESET} Apagada")
                        moni = f"\n5. Verificando estado de la maquina (0:off , 1:on): {run_command.returncode} "
                        self.mon += moni
                        self.uq_machine_mon(self.mon)

                        #PASO5 FIN

                        #PASO6. CONSULTE EL ESTADO DEL EQUIPO EN TABLA (0:APAGADO - 1:ENCENDIDO)
                        if self.rq_machine_status() == "1": 
                            print(f"{Fore.GREEN}6.Intentando acceder a maquina...{Fore.RESET}")
                            moni = "\n6.Intentando acceder a maquina... "
                            self.mon += moni
                            self.uq_machine_mon(self.mon)
                            
                            #PASO7. OBTENGA EL ID DEL BAT ASOCIADO AL EQUIPO
                            if self.rq_bat_id():
                                print(f"{Fore.GREEN}7. ID Bat asociado:{Fore.RESET} ({self.rq_bat_id()}) - {self.rq_bat_name()}")
                                moni = f"\n7. Bat asociado ({self.rq_bat_name()}), obtenido "
                                self.mon += moni
                                self.uq_machine_mon(self.mon)
                                
                                #PASO8. VALIDE EL TIPO DE BAT ASOCIADO CON EL TIPO DE SOLICITUD (1:EQUIPO - 2:SERVICIO)
                                if self.rq_bat_type() == self.rq_machine_request_type():
                                    print(f"{Fore.GREEN}8. Congruencia tipo Bat, tipo solicitud:{Fore.RESET}  Valido")
                                    moni = "\n8. Tipo Bat, servicio "
                                    self.mon += moni
                                    self.uq_machine_mon(self.mon)

                                    #<---------INICIO PRINT PARAMETROS, PARA VALIDAR VALORES OBTENIDOS-------->
                                    #PASO9. OBTENGA EL PARAMETRO DE CONEXION A MAQUINA REMOTA (IP) (RECIBE BAT)
                                    if self.rq_machine_1_parameter():
                                        print(f"{Fore.GREEN}9. Parametro conexion maquina remota:{Fore.RESET} {self.rq_machine_1_parameter()}")
                                        moni = "\n9. Parametro de conexion a maquina remota, obtenido "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    else:
                                        print(f"{Fore.BLUE}9. Parametro conexion maquina remota:{Fore.RESET} Null")
                                        moni = "\n9. Parametro de conexion a maquina remota, obtenido:Null "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                         
                                    #PASO9. OBTENGA EL PARAMETRO 2 (RECIBE BAT)
                                    if self.rq_machine_2_parameter():
                                        print(f"{Fore.GREEN}9. Parametro 2:{Fore.RESET} {self.rq_machine_2_parameter()}")
                                        moni = "\n9. Parametro 2, obtenido "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    else:
                                        print(f"{Fore.BLUE}9. Parametro 2:{Fore.RESET} {self.rq_machine_2_parameter()} Null")
                                        moni = "\n9. Parametro 2, obtenido:Null "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                        
                                    #PASO9 CONSULTE EL PARAMETRO 3 (RECIBE BAT)
                                    if self.rq_machine_3_parameter():
                                        print(f"{Fore.GREEN}9. Parametro 3:{Fore.RESET} {self.rq_machine_3_parameter()}")
                                        moni = "\n9. Parametro 3, obtenido "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    else:
                                        print(f"{Fore.BLUE}9. Parametro 3:{Fore.RESET} {self.rq_machine_3_parameter()} Null")
                                        moni = "\n9. Parametro 3, obtenido:Null "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    
                                    #PASO9. CONSULTE EL PARAMETRO 4 (NOMBRE SERVICIO) QUE RECIBE EL BAT
                                    if self.rq_name_service():
                                        print(f"{Fore.GREEN}9. parametro 4 (Nombre servicio):{Fore.RESET} {self.rq_name_service()} - {self.rq_des_service()}")
                                        moni = f"\n9. Parametro 4 ({self.rq_des_service()}), obtenido "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    else:
                                        print(f"{Fore.BLUE}9. Parametro 4 (Nombre servicio):{Fore.RESET} {self.rq_name_service()} Null")
                                        moni = "\n9. Parametro 4, obtenido:Null "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                        
                                    #PASO9 FIN
                                    #<---------FIN PRINT PARAMETROS, PARA VALIDAR VALORES OBTENIDOS-------->

                                    #PASO10. OBTENGA LA RUTA DEL ARCHIVO BAT
                                    if self.rq_bat_path():
                                        print(f"{Fore.GREEN}10. Ruta Bat asociado:{Fore.RESET} {self.rq_bat_path()}")
                                        moni = "\n10. Ruta Bat asociado, obtenida "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)

                                        #PASO11. EJECUTE EL BAT ASOCIADO (SERVICIO)
                                        self.run_bat_service()
                                        print(f"{Fore.GREEN}11. Ejecutando archivo Bat:{Fore.RESET} Finalizado")
                                        moni = "\n11. Operacion finalizada "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                        self.read_machine_status()
                                        request = "0"
                                        self.uq_machine_request(request)
                                        #PASO11 FIN

                                    else:
                                        print(f"{Fore.BLUE}10. Ruta Bat asociado:{Fore.RESET} {self.rq_bat_path()} Desconocida")
                                        moni = "\n10. Ruta Bat asociado, no obtenida "
                                        self.mon += moni
                                        self.uq_machine_mon(self.mon)
                                    #PASO10 FIN

                                else:
                                    print(f"{Fore.BLUE}8. Congruencia tipo Bat, tipo solicitud:{Fore.RESET}  Invalido")
                                    moni = f"\n8. Tipo bat, invalido"
                                    self.mon += moni
                                    self.uq_machine_mon(self.mon)
                                #PASO8 FIN

                            else:
                                print(f"{Fore.BLUE}7. ID Bat asociado:{Fore.RESET} No se obtuvo Bat asociado")
                                moni = "\n7. Bat asociado, no obtenido "
                                self.mon += moni
                                self.uq_machine_mon(self.mon)
                            #PASO7 FIN
                            
                        elif self.rq_machine_status() == "0": #NOTA: NO EJECUTAR BATS DE TIPO SERVICIO SI LA MAQUINA ESTÁ APAGADA
                            print(f"{Fore.GREEN}6. Intentando acceder a maquina...{Fore.RESET} No Permitido: La maquina debe estar encendida para continuar")
                            moni = "\n6. Acceso a maquina, no accesible: La maquina debe estar encendida para continuar"
                            self.mon += moni
                            self.uq_machine_mon(self.mon)
                            status = "0"
                            self.uq_machine_request(status)
                            
                        else:
                            print(f"{Fore.BLUE}6. Intentando acceder a maquina...{Fore.RESET} No Permitido: Estado de maquina desconocido")
                            moni = "\n6. Acceso a maquina, no accesible: Estado de maquina desconocido "
                            self.mon += moni
                            self.uq_machine_mon(self.mon)
                        #PASO6 FIN  

                    else:
                        print(f"{Fore.BLUE}4. ID maquina asociada:{Fore.RESET} No se obtuvo maquina asociada")
                        moni = f"\n4. Conectando con maquina asociada {self.rq_machine_des()}, fallida "
                        self.mon += moni
                        self.uq_machine_mon(self.mon)   
                    #PASO4 FIN

                #<-------SOLICITUD DESCONOCIDA------------->
                else:
                    print(f"{Fore.BLUE}3. Tipo solicitud:{Fore.RESET} No valido")
                    moni = "\n3. Solicitud 'No valida' "
                    self.mon += moni
                    self.uq_machine_mon(self.mon)
                #PASO3 FIN

            else:
                print(F"{Fore.BLUE}2. ID registro con solicitud:{Fore.RESET} No se obtuvo registro con solicitud \n{Fore.GREEN}3. Consultando solictud nuevamente... {Fore.RESET}")
            #PASO2 FIN
                
        else:
            print(f"{Fore.BLUE}1. Conexion BD: Fallida{Fore.RESET}")
        #PASO1 FIN

while True:
    cogesser = Servers_gestion() #aplicacion de la clase 
    cogesser.cogesserver_start() #aplicacion de "método para gestionar servidores y servicios

    time.sleep(10) #tiempo de siguiente consulta