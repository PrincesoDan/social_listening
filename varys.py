import schedule
import time
import subprocess
import os
import json
import requests
import hashlib

# Token del bot de Telegram y ID del grupo
TELEGRAM_BOT_TOKEN = '6856314126:AAFmtwNz5ihIRWHT4a7vnFyksM7Av9YVn1Y'
TELEGRAM_GROUP_ID = '-4197811136'

# Archivo de identificadores de noticias enviadas
enviados_guardados_file = 'identificadores_enviados.json'

# Función para generar un identificador único
def generate_id(article):
    hash_input = (article['titulo'] + article['contenido']).encode('utf-8')
    return hashlib.md5(hash_input).hexdigest()

# Función para cargar los identificadores guardados
def load_saved_links(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

# Función para guardar los identificadores nuevos
def save_new_links(filename, links):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(list(links), f)

def execute_scripts():
    try:
        print("Ejecutando rss3.py...")
        # Ejecutar rss.py
        result = subprocess.run(['python', 'rss3.py'], check=True)
        print(f"rss.py terminado con código de salida {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar rss.py: {e}")
        return

    try:
        print("Ejecutando buscador.py...")
        # Ejecutar buscador.py
        result = subprocess.run(['python', 'buscador2.py'], check=True)
        print(f"buscador.py terminado con código de salida {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar buscador.py: {e}")
        return

    # Obtener el archivo JSON más reciente generado por buscador.py
    json_directory = '.'  # Directorio actual
    print(f"Buscando archivos JSON en el directorio: {json_directory}")
    for root, dirs, files in os.walk(json_directory):
        dirs[:] = [d for d in dirs if d != '.venv']
        for name in files:
            print(f"Archivo encontrado: {name}")

    recent_files = sorted(
        [os.path.join(root, name)
         for root, dirs, files in os.walk(json_directory)
         for name in files if name.startswith('noticias_filtradas_') and name.endswith('.json')],
        key=lambda x: os.path.getmtime(x), reverse=True
    )

    if recent_files:
        latest_file = recent_files[0]
        print(f"Último archivo JSON encontrado: {latest_file}")
        with open(latest_file, 'r', encoding='utf-8') as f:
            news = json.load(f)
            f.close()  # Asegurarse de cerrar el archivo antes de eliminarlo
            if news:
                print(f"{len(news)} noticias encontradas. Filtrando noticias no enviadas...")
                # Filtrar y enviar las noticias no enviadas a Telegram
                send_news_to_telegram(news)
                # Eliminar archivos JSON de noticias filtradas
                delete_old_json_files(recent_files)
            else:
                print("No hay noticias nuevas para enviar.")
    else:
        print("No se encontraron archivos JSON recientes.")

def send_news_to_telegram(news):
    saved_links = load_saved_links(enviados_guardados_file)
    new_links = set()
    for article in news:
        article_id = generate_id(article)
        if article_id not in saved_links:
            message = f"**{article['medio']}**\n*{article['titulo']}*\n{article['contenido']}\n[Leer más]({article['enlace']})"
            send_telegram_message(message)
            new_links.add(article_id)

    if new_links:
        saved_links.update(new_links)
        save_new_links(enviados_guardados_file, saved_links)
        print(f"Noticias enviadas y guardadas.")
    else:
        print("No hay noticias nuevas para enviar.")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_GROUP_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Mensaje enviado a Telegram con éxito.")
    else:
        print(f"Error al enviar mensaje: {response.status_code} - {response.text}")

def delete_old_json_files(files):
    for file in files:
        try:
            os.remove(file)
            print(f"Archivo {file} eliminado.")
        except OSError as e:
            print(f"Error al eliminar el archivo {file}: {e}")

# Configurar la ejecución periódica cada 5 minutos
# Para pruebas puedes cambiar el intervalo a cada minuto
schedule.every(5).minutes.do(execute_scripts)
# schedule.every(1).minutes.do(execute_scripts)  # Descomentar para pruebas cada minuto

print("Iniciando el planificador...")

# Ejecutar la primera vez inmediatamente
execute_scripts()

# Ejecutar el planificador
while True:
    schedule.run_pending()
    time.sleep(1)
