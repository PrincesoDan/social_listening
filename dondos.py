import urllib.request
import json

# Consulta con un término de búsqueda general
url = 'https://datos.gob.cl/api/3/action/datastore_search?resource_id=20188fa9-5852-4db4-9bfb-97baf49d3310&q=fondo&limit=10'
response = urllib.request.urlopen(url)
data = json.loads(response.read())

# Mostrar los datos
print(json.dumps(data, indent=4))
