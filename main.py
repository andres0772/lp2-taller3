from flask import Flask, render_template, redirect
import pandas as pd
import matplotlib.pyplot as ply
# Buscar en ThingSpeak estaciones meteorológicas:
# https://thingspeak.mathworks.com/channels/public
# Ejemplos:
# https://thingspeak.mathworks.com/channels/870845
# https://thingspeak.mathworks.com/channels/1293177
# https://thingspeak.mathworks.com/channels/12397

URLs = [
  'https://thingspeak.mathworks.com/channels/870845/feeds.CSV?results=8000',
   'https://thingspeak.mathworks.com/channels/1293177/feeds.CSV?results=8000',
    'https://thingspeak.mathworks.com/channels/12397/feeds.CSV?results=8000',
 
  
]

app = Flask(__name__)

def descargar(url):
  df = pd.read_csv(url)
  df['created_at'] = pd.to_datetime(df['created_at'])
  if 'field6' in df.columns:
  df.drop(['entry_id', 'field5', 'field6'], axis=1, implace=True)
  else:
    df.drop(['entry_id', 'field5', 'field7'], axis=1, implace=True)
    #renombre de columnas
    df.columns = ['fecha', 'temp_exterior', 'temp_interior', 'presion_atm','humedad']
    return df

def graficar(df):
  lista =[]
  for columna in df.columns[1:]

  #creacion de la figure
  fig = plt.figure(figsize=(8,5))
  #se hace la grafica
  plt.plot(df['fecha'], df[columna], label=columna)
  #se pone los titulos
  plt.tittle(f"historia sobre {columna}")
  #graba la imagen
  plt.savefig(f"static/{columna}.png")
  lista.append(f"{columna}.png")
  plt.close()
  return lista

@app.route('/')
def index():
    return render_template('index.html', nombres=nombres)


# Programa Principal
if __name__ == '__main__':
  #descarga los datos y crea las graficas
      for url in URLs:
        nombres =[]
        df= descargar(url)
        nombres.extend(graficar(dftemp))


  # Ejecuta la app
  app.run(host='0.0.0.0', debug=True)
