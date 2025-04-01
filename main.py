from flask import Flask, render_template, redirect
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('agg')  # Quita el warning de main thread

URLs = [
    'https://thingspeak.com/channels/870845/feeds.csv?results=8000',
    # Añade aquí las otras URLs de los canales si quieres graficarlos
    # 'https://thingspeak.com/channels/1293177/feeds.csv?results=8000',
    # 'https://thingspeak.com/channels/12397/feeds.csv?results=8000'
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
    remaining_columns = len(df.columns)
    if url == 'https://thingspeak.com/channels/870845/feeds.csv?results=8000' and remaining_columns >= 3:
        # Asignamos nombres basados en la información de ThingSpeak
        nombres_columnas = ['fecha', 'temperatura', 'humedad']
        if remaining_columns > 3:
            nombres_columnas.append('presion') # Usando 'presion' para coincidir con tu código
        df = df.iloc[:, :len(nombres_columnas)] # Seleccionamos las primeras N columnas
        df.columns = nombres_columnas
    elif remaining_columns == 5:
        df.columns = ['fecha', 'temperatura_exterior', 'temperatura_interior', 'presion_atmosferica', 'humedad']
    elif url == 'https://thingspeak.com/channels/1293177/feeds.csv?results=8000' and remaining_columns == 6:
        df = df[['created_at', 'field1', 'field2', 'field3', 'field4']]
        df.columns = ['fecha', 'temperatura', 'humedad', 'presion', 'otro'] # Tentative
        print("Advertencia: Se asumió la correspondencia de columnas para el canal 1293177. ¡Verificar!")
    elif url == 'https://thingspeak.com/channels/12397/feeds.csv?results=8000' and remaining_columns == 6:
        df = df[['created_at', 'field1', 'field2', 'field3', 'field4']]
        df.columns = ['fecha', 'temperatura', 'humedad', 'presion', 'otro'] # Tentative
        print("Advertencia: Se asumió la correspondencia de columnas para el canal 12397. ¡Verificar!")
    elif remaining_columns == 5:
        df.columns = ['fecha', 'temperatura', 'humedad', 'presion', 'otro'] # Genérico para 5 columnas
    else:
        print(f"Advertencia: Número inesperado de columnas ({remaining_columns}) en el DataFrame de {url}")
        print(f"Columnas encontradas: {df.columns.tolist()}")
        # Aquí podrías decidir qué hacer si no hay suficientes columnas

    return df

def graficar(i, df):
    lista = []
    columnas_a_graficar = ['temperatura', 'humedad', 'presion']
    for columna in columnas_a_graficar:
        if columna in df.columns:
            # Creación de la figura
            fig = plt.figure(figsize=(8, 5))
            # Se hace la gráfica
            plt.plot(df['fecha'], df[columna], label=columna)
            # Se ponen los títulos
            plt.title(f"Historia sobre la {columna} - estacion #{i}")
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