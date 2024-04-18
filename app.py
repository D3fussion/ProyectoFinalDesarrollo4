from flask import Flask, request, render_template
from funciones import comprobar_existencia_csv, crear_diccionario_palabras, crear_diccionario_letras, \
    ordenar_diccionario

app = Flask(__name__)

diccionario = ordenar_diccionario(comprobar_existencia_csv())
diccionario_palabras = ordenar_diccionario(crear_diccionario_palabras(diccionario))
diccionario_letras = ordenar_diccionario(crear_diccionario_letras(diccionario_palabras))

print(diccionario_palabras)
print(diccionario_letras)
print(diccionario)


@app.route('/')
def inicio():
    return render_template('Inicio.html')


@app.route('/Explorar.html')
def explorar():
    return render_template('Explorar.html', diccionario_letras=diccionario_letras)


@app.route('/ExplorarPalabras/<id>')
def explorar_palabras(id):
    diccionario_enviar = {}
    for i in diccionario_palabras[id]:
        diccionario_enviar[i] = diccionario[i]
    return render_template('ExplorarPalabras.html', diccionario_palabras=diccionario_enviar, titulo=id)


if __name__ == '__main__':
    app.run(Debug=True)
