import os
import json
from datetime import datetime

# Obtener el directorio donde está el script actualmente
script_directory = os.path.dirname(os.path.abspath(__file__))

# Archivos de entrada y salida
input_file = os.path.join(script_directory, 'titulares_web.json')
output_file = os.path.join(script_directory, 'titulares_enviar.json')

def select_last_100_headlines():
    # Verificar si el archivo de titulares existe
    if not os.path.exists(input_file):
        print(f"No se encontró el archivo {input_file}")
        return
    
    # Leer el archivo de titulares
    with open(input_file, 'r', encoding='utf-8') as f:
        titulares = json.load(f)

    # Ordenar los titulares por timestamp (más recientes primero)
    # Si hay varios titulares con el mismo timestamp, se mantiene el orden de escritura (es decir, el orden en el archivo)
    titulares.sort(key=lambda x: x['timestamp'], reverse=True)

    # Seleccionar los últimos 100 titulares (o menos si hay menos de 100)
    selected_headlines = titulares[:100]

    # Guardar los titulares seleccionados en el archivo de salida
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(selected_headlines, f, ensure_ascii=False, indent=4)
    
    print(f"Se han guardado {len(selected_headlines)} titulares en {output_file}")

# Ejecutar el script una vez
select_last_100_headlines()
