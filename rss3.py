import feedparser
import json
from datetime import datetime
import pytz
import os
import hashlib
import requests
from io import BytesIO

# URLs de los RSS feeds de los diarios
rss_feeds = [
    'https://www.cooperativa.cl/noticias/site/tax/port/all/rss_3___1.xml',
    'https://www.df.cl/noticias/site/list/port/rss.xml',
    'https://www.latercera.com/arcio/rss/',
    'https://www.publimetro.cl/arc/outboundfeeds/rss/?outputType=xml',
    'https://www.theclinic.cl/feed',
    'https://eldesconcierto.cl/feed',
    'https://www.ex-ante.cl/feed',

    #Para El Líbero funcionó con feed por un rato y empezó a pedir suscripción 'https://ellibero.cl/feed', habría que hacer scrapt especial.
    #Para El Ciudadano no está descargando bien el archivo y revisándolo, ademas se debe agregar un filtro en "categoría"
    # para que agarre solo las noticias de Chile'https://www.elciudadano.com/feed',
    #Para El Mostrador hay que adaptar como lee el xml para que reconozca ese formato 'https://www.elmostrador.cl/sitemap_news.xml'
    #EMOL tiene un proceso de scraping propio por separado, falta incorporarlo.

    #otros pendientes:
    #https://www.cnnchile.com/_files/sitemaps/sitemap_news.xml
    #https://www.ciperchile.cl/feed
    #https://www.biobiochile.cl/static/google-news-sitemap.xml
    #https://www.lacuarta.com/arc/outboundfeeds/news-sitemap/?outputType=xml
    #https://www.chilevision.cl/chilevision/site/sitemap_news_chvn.xml


]

# Zona horaria de Chile
chile_tz = pytz.timezone('America/Santiago')

# Función para crear la estructura de carpetas
def create_directory_structure(base_dir):
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    current_date = datetime.now(chile_tz)
    month_str = current_date.strftime('%B')
    today_str = current_date.strftime('%d-%m-%Y')
    monthly_dir = os.path.join(base_dir, month_str)
    if not os.path.exists(monthly_dir):
        os.makedirs(monthly_dir)
    daily_dir = os.path.join(monthly_dir, today_str)
    if not os.path.exists(daily_dir):
        os.makedirs(daily_dir)
    return daily_dir

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

# Función para obtener y parsear los feeds
def fetch_rss_feeds(rss_feeds):
    all_articles = []
    for feed_url in rss_feeds:
        try:
            # Intentar descargar el contenido de la URL
            response = requests.get(feed_url)
            content_type = response.headers.get('Content-Type', '')
            
            # Comprobar si el contenido es un archivo (por ejemplo, application/octet-stream)
            if 'application/octet-stream' in content_type or response.headers.get('Content-Disposition'):
                # Usar el contenido descargado para parsear el XML
                feed = feedparser.parse(BytesIO(response.content))
            else:
                # Si es un feed normal, parsearlo directamente desde la URL
                feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                # Convertir la fecha de publicación a la zona horaria de Chile
                published_time = entry.published_parsed
                published_datetime = datetime(*published_time[:6], tzinfo=pytz.utc).astimezone(chile_tz)
                formatted_date = published_datetime.strftime('%d de %B del %Y - %H:%M')
                article = {
                    'medio': feed.feed.title,
                    'titulo': entry.title,
                    'contenido': entry.description,
                    'fecha_publicacion': formatted_date,
                    'enlace': entry.link
                }
                all_articles.append(article)

        except Exception as e:
            print(f"Error al procesar el feed {feed_url}: {e}")

    return all_articles

# Función para guardar las noticias nuevas
def save_articles(articles, daily_dir, saved_links, identificadores_guardados_file):
    new_articles = []
    for article in articles:
        article_id = generate_id(article)
        if article_id not in saved_links:
            new_articles.append(article)
            saved_links.add(article_id)
    
    if new_articles:
        formatted_time = datetime.now(chile_tz).strftime('%H-%M-%S')
        daily_file = os.path.join(daily_dir, f'noticias_{formatted_time}.json')
        with open(daily_file, 'w', encoding='utf-8') as f:
            json.dump(new_articles, f, ensure_ascii=False, indent=4)
        
        # Actualizar el archivo de identificadores guardados
        save_new_links(identificadores_guardados_file, saved_links)
        print(f"Noticias guardadas en {daily_file}")
    else:
        print("No hay noticias nuevas.")

# Función principal para el procesamiento
def main():
    base_dir = './noticias'
    daily_dir = create_directory_structure(base_dir)
    
    identificadores_guardados_file = os.path.join(base_dir, 'identificadores_guardados.json')
    saved_links = load_saved_links(identificadores_guardados_file)
    
    articles = fetch_rss_feeds(rss_feeds)
    save_articles(articles, daily_dir, saved_links, identificadores_guardados_file)

if __name__ == "__main__":
    main()
