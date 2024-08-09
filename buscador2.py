import os
import json
import string
import unicodedata
from datetime import datetime, timedelta
import pytz

# Directorio donde se almacenan los JSON
json_directory = './noticias'

# Palabras clave a buscar
keywords = [' FA ', 'Frente Amplio', 'ñuñoa', 'sichel', "emilia rios"]

# Zona horaria de Chile
chile_tz = pytz.timezone('America/Santiago')

# Rango de horas hacia atrás desde la hora actual
search_hours = 24

# Función para listar archivos JSON creados en el rango de horas especificado
def list_recent_json_files(directory, hours=24):
    now = datetime.now(chile_tz)
    cutoff = now - timedelta(hours=hours)
    recent_files = []
    for month in os.listdir(directory):
        month_path = os.path.join(directory, month)
        if os.path.isdir(month_path):
            for day in os.listdir(month_path):
                day_path = os.path.join(month_path, day)
                if os.path.isdir(day_path):
                    for filename in os.listdir(day_path):
                        if filename.endswith('.json'):
                            filepath = os.path.join(day_path, filename)
                            file_time = datetime.fromtimestamp(os.path.getmtime(filepath)).astimezone(chile_tz)
                            if file_time > cutoff:
                                recent_files.append(filepath)
    return recent_files

# Función para normalizar el texto (elimina acentos)
def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# Función para convertir la fecha de publicación a datetime
def parse_publication_date(date_str):
    try:
        return chile_tz.localize(datetime.strptime(date_str, '%d de %B del %Y - %H:%M'))
    except ValueError:
        return None

# Función para buscar palabras clave en las publicaciones
def search_keywords_in_files(files, keywords):
    normalized_keywords = [normalize_text(keyword) for keyword in keywords]
    matched_articles = []
    now = datetime.now(chile_tz)
    cutoff = now - timedelta(hours=search_hours)
    
    print(f"Fecha y hora actual: {now}")
    print(f"Fecha y hora de corte: {cutoff}")

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
            for article in articles:
                publication_date = parse_publication_date(article['fecha_publicacion'])
                if publication_date:
                    print(f"Fecha de publicación del artículo: {publication_date}")
                    if publication_date > cutoff:
                        normalized_content = normalize_text(article['contenido'])
                        normalized_title = normalize_text(article['titulo'])
                        combined_text = normalized_content + ' ' + normalized_title
                        if any(keyword in combined_text for keyword in normalized_keywords):
                            matched_articles.append(article)
    return matched_articles

# Función para guardar publicaciones encontradas en un nuevo JSON
def save_matched_articles(articles, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

# Función principal
def main():
    recent_files = list_recent_json_files(json_directory, search_hours)
    matched_articles = search_keywords_in_files(recent_files, keywords)
    
    if matched_articles:
        now_str = datetime.now(chile_tz).strftime('%Y%m%d_%H%M%S')
        output_file = f'noticias_filtradas_{now_str}.json'
        save_matched_articles(matched_articles, output_file)
        print(f"Archivo '{output_file}' creado con éxito.")
    else:
        print("No se encontraron noticias que coincidan con los términos de búsqueda.")

if __name__ == "__main__":
    main()
