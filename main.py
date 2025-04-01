from flask import Flask, render_template, redirect
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

import matplotlib

matplotlib.use('agg')  # Quita el warning de main thread

# Buscar en ThingSpeak estaciones meteorológicas:
# https://thingspeak.mathworks.com/channels/public
# Ejemplos:
# https://thingspeak.mathworks.com/channels/870845
# https://thingspeak.mathworks.com/channels/1293177
# https://thingspeak.mathworks.com/channels/12397

URLs = [
    'https://thingspeak.mathworks.com/channels/870845/feeds.json?results=8000',
    'https://thingspeak.mathworks.com/channels/1293177/feeds.json?results=8000',
    'https://thingspeak.mathworks.com/channels/12397/feeds.json?results=8000',
]

app = Flask(__name__)

def descargar(url):
    # descarga el json en un dataframe desde el url
    headers = {'User-Agent': 'MiAplicacionPython/1.0'}  # Agrega un encabezado User-Agent
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Lanza una excepción si la petición falla (status code != 200)
    data = response.json()  # Obtiene los datos JSON de la respuesta
    feeds = data['feeds']  # Los datos de las lecturas suelen estar en la lista 'feeds'
    df = pd.DataFrame(feeds)

    # Renombrar y seleccionar columnas (esto puede necesitar ajuste según la estructura del JSON)
    df.rename(columns={'created_at': 'fecha',
                       'field1': 'temperatura_exterior',
                       'field2': 'temperatura_interior',
                       'field3': 'presion_atmosferica',
                       'field4': 'humedad'}, inplace=True)

    # Convertir la columna 'fecha' a datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Manejar valores nulos reemplazándolos con 0
    df['temperatura_exterior'].fillna(0, inplace=True)
    df['temperatura_interior'].fillna(0, inplace=True)
    df['presion_atmosferica'].fillna(0, inplace=True)
    df['humedad'].fillna(0, inplace=True)

    # Eliminar columnas 'entry_id' y otras 'field' que no se renombraron
    columns_to_drop = [col for col in df.columns if col.startswith('field') and col not in ['field1', 'field2', 'field3', 'field4']]
    columns_to_drop.append('entry_id')
    df.drop(columns=columns_to_drop, errors='ignore', inplace=True)

    return df

def graficar(i, df):
    lista = []
    for columna in df.columns[1:]:
        # Creación de la figura
        fig = plt.figure(figsize=(8, 5))
        # Se hace la gráfica
        plt.plot(df['fecha'], df[columna], label=columna)
        # Se ponen los títulos
        plt.title(f"Historia sobre {columna} - estacion #{i}")
        # Graba la imagen
        plt.savefig(f"static/g{i}_{columna}.png")
        lista.append(f"g{i}_{columna}.png")
        plt.close()
    return lista

def actualizar():
    # Descarga los datos y crea las gráficas
    nombres = []
    for i, url in enumerate(URLs):
        df = descargar(url)
        nombres.extend(graficar(i, df))
    return nombres

@app.route('/')
def index():
    return render_template('index.html', nombres=nombres)

@app.route('/actualizar')
def actualizar_datos():
    global nombres
    nombres = actualizar()
    return redirect('/')

# Programa Principal
if __name__ == '__main__':
    # Descarga los datos y crea las gráficas
    nombres = actualizar()

    # Ejecuta la app
    app.run(host='0.0.0.0', debug=True)