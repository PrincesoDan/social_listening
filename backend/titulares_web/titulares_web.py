import os
import json
from datetime import datetime

# Obtener el directorio donde está el script actualmente
script_directory = os.path.dirname(os.path.abspath(__file__))

# Directorio de noticias que está "un paso atrás" (directorio padre)
noticias_directory = os.path.join(script_directory, '..', 'noticias')
# Archivo donde se guardarán los titulares extraídos en la carpeta actual del script
output_file = os.path.join(script_directory, 'titulares_web.json')

def list_recent_json_file(directory):
    # Recorremos las carpetas de meses y días para encontrar el JSON más reciente
    recent_files = []
    for month in os.listdir(directory):
        month_path = os.path.join(directory, month)
        if os.path.isdir(month_path):  # Asegurarse de que es una carpeta
            for day in os.listdir(month_path):
                day_path = os.path.join(month_path, day)
                if os.path.isdir(day_path):  # Asegurarse de que es una carpeta
                    for file in os.listdir(day_path):
                        if file.endswith('.json'):
                            file_path = os.path.join(day_path, file)
                            recent_files.append(file_path)

    if not recent_files:
        return None

    # Ordenamos los archivos por la fecha de modificación y obtenemos el más reciente
    recent_files.sort(key=os.path.getmtime, reverse=True)
    return recent_files[0]

def extract_headlines():
    # Obtener el archivo JSON más reciente
    latest_file = list_recent_json_file(noticias_directory)
    
    if not latest_file:
        print("No se encontraron archivos recientes.")
        return
    
    print(f"Procesando el archivo: {latest_file}")
    
    # Leer el archivo JSON y extraer los titulares
    with open(latest_file, 'r', encoding='utf-8') as f:
        noticias = json.load(f)
    
    titulares = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp que se asignará a cada titular
    
    for noticia in noticias:
        if 'titulo' in noticia:
            # Asignamos el mismo timestamp a cada titular individualmente
            titulares.append({
                'timestamp': timestamp,
                'titulo': noticia['titulo']
            })
    
    if not titulares:
        print("No se encontraron titulares en el archivo.")
        return
    
    # Cargar el archivo de salida si existe
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    # Agregar los nuevos titulares al archivo de salida
    data.extend(titulares)
    
    # Guardar el archivo actualizado
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Titulares guardados correctamente en {output_file}.")

# Ejecutar el script una vez
extract_headlines()
