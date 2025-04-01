from flask import Flask, render_template, redirect
import pandas as pd
import matplotlib.pyplot as plt


import matplotlib

# Buscar en ThingSpeak estaciones meteorológicas:
# https://thingspeak.mathworks.com/channels/public
# Ejemplos:
# https://thingspeak.mathworks.com/channels/870845
# https://thingspeak.mathworks.com/channels/1293177
# https://thingspeak.mathworks.com/channels/12397

matplotlib.use('agg')  # Quita el warning de main thread



URLs = [
    'https://thingspeak.com/channels/870845/feeds.csv?results=8000',
    'https://thingspeak.com/channels/1293177/feeds.csv?results=8000',
    'https://thingspeak.com/channels/12397/feeds.csv?results=8000',
    
]

app = Flask(__name__)

def descargar(url):
    #descarga el csv en un dataframe desde el url
    df = pd.read_csv(url)
    #hace la conversion de la caneda en una fecha real
    df['created_at'] = pd.to_datetime(df['created_at'])
#se borra las columnas inecesarias
    columns_to_drop = ['entry_id', 'field5', 'field6', 'field7']
    for col in columns_to_drop:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)

    # Renombre de columnas
    actual_columns = len(df.columns)
    if url == 'https://thingspeak.com/channels/870845/feeds.csv?results=8000' and actual_columns == 4:
        df.columns = ['fecha', 'temperatura_exterior', 'temperatura_interior', 'humedad']
    elif actual_columns == 5:
        expected_columns = ['fecha', 'temperatura_exterior', 'temperatura_interior', 'presion_atmosferica', 'humedad']
        df.columns = expected_columns
    else:
        print(f"Advertencia: Número inesperado de columnas ({actual_columns}) en el DataFrame de {url}")
        print(f"Columnas encontradas: {df.columns.tolist()}")
        # Aquí podrías decidir qué hacer si no hay suficientes columnas

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