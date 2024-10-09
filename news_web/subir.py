import ftplib
import os
from dotenv import load_dotenv
import logging

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las credenciales desde las variables de entorno
FTP_SERVER = 'ftp.epizy.com'
FTP_USERNAME = os.getenv('FTP_USERNAME')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
FTP_PORT = 21
REMOTE_DIRECTORY = 'teorica.cl/htdocs'
LOCAL_FILE = 'titulares_enviar.json'  # Nombre actualizado del archivo

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def subir_archivo_ftp():
    # Obtener el directorio padre del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    # Ruta a la carpeta 'titulares_web' en el directorio padre
    titulares_web_dir = os.path.join(parent_dir, 'titulares_web')
    
    # Ruta completa al archivo JSON
    local_file_path = os.path.join(titulares_web_dir, LOCAL_FILE)

    if not os.path.isfile(local_file_path):
        logger.error(f"El archivo '{LOCAL_FILE}' no existe en '{titulares_web_dir}'.")
        return

    try:
        with ftplib.FTP() as ftp:
            ftp.connect(FTP_SERVER, FTP_PORT, timeout=30)
            ftp.login(FTP_USERNAME, FTP_PASSWORD)
            ftp.set_pasv(True)
            logger.info(f"Conectado a {FTP_SERVER}")

            ftp.cwd(REMOTE_DIRECTORY)
            logger.info(f"Directorio cambiado a {REMOTE_DIRECTORY}")

            with open(local_file_path, 'rb') as file:
                ftp.storbinary(f'STOR {LOCAL_FILE}', file)
            logger.info(f"'{LOCAL_FILE}' subido exitosamente desde '{titulares_web_dir}'.")

    except ftplib.all_errors as e:
        logger.error(f"Error FTP: {e}")

if __name__ == "__main__":
    subir_archivo_ftp()
