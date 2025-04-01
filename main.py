from flask import Flask, render_template, redirect
import pandas as pd
import matplotlib.pyplot as plt


import matplotlib

matplotlib.use('agg')  # Evita problemas con hilos en Matplotlib

# URL de datos en formato CSV
URLs = [
    'https://thingspeak.com/channels/870845/feeds.csv?results=8000',


]

app = Flask(__name__)

def descargar(url):
    try:
        # Descarga el CSV en un DataFrame
        df = pd.read_csv(url)

        # Convertir la columna 'created_at' a formato de fecha
        df['created_at'] = pd.to_datetime(df['created_at'])

        # Seleccionar solo las columnas necesarias (ajustado a los datos disponibles)
        df = df[['created_at', 'field1', 'field2', 'field3']]

        # Renombrar las columnas
        df.columns = ['fecha', 'temperatura', 'humedad', 'presion']

        return df
    except Exception as e:
        print(f"Error descargando datos: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío si hay error

def graficar(i, df):
    lista = []
    for columna in df.columns[1:]:  # Omitimos la columna de fecha
        plt.figure(figsize=(8, 5))
        plt.plot(df['fecha'], df[columna], label=columna)
        plt.title(f"Historial de {columna} - Estación #{i}")
        plt.xlabel("Fecha")
        plt.ylabel(columna)
        plt.legend()
        plt.xticks(rotation=45)

        # Guardar la imagen
        file_name = f"static/g{i}_{columna}.png"
        plt.savefig(file_name)
        lista.append(file_name)
        plt.close()

    return lista

def actualizar():

    nombres = []
    for i, url in enumerate(URLs):
        df = descargar(url)
        if not df.empty:
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


if __name__ == '__main__':

    nombres = actualizar()


    app.run(host='0.0.0.0', debug=True)
