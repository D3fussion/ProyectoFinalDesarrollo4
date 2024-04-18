import os
import re
import csv
import requests
from bs4 import BeautifulSoup


def crear_scrapper(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def web_crawling(scrapper, url):
    pagina = scrapper.find_all(class_='pagination_buttons')[0].find_all('a')[-1].get('href').split('?')[1].split('&')
    numero_paginas = int((int(pagina[1].split('=')[1]) / 50) + 1)
    for i in range(1, numero_paginas + 1):
        url = f'{url}&page={i}'
        scrapper = crear_scrapper(url)
        scrapear_datos_general(scrapper)


def scrapear_datos_general(scrapper):
    lista_revistas = []
    for i in scrapper.find_all('tbody')[0].find_all('tr'):
        lista_texto = ([j for j in i.find_all('td')])
        lista_revistas.append(scrapear_datos_revista(lista_texto))
    crear_csv(lista_revistas)


def scrapear_datos_revista(lista_texto):
    scrapper_revista = crear_scrapper(f"https://www.scimagojr.com/{lista_texto[1].find_all('a')[0].get('href')}")
    divs = scrapper_revista.find(class_='journalgrid').find_all('div')
    return {lista_texto[1].text: {
        "type": lista_texto[2].text,
        "sjr": lista_texto[3].text.split(" ")[0],
        "q": lista_texto[3].text.split(" ")[1],
        "h_index": lista_texto[4].text,
        "total_docs": lista_texto[5].text,
        "total_docs_3_years": lista_texto[6].text,
        "total_refs": lista_texto[7].text,
        "total_cites_3_years": lista_texto[8].text,
        "citable_docs_3_years": lista_texto[9].text,
        "cites_doc_2_years": lista_texto[10].text,
        "ref_doc": lista_texto[11].text,
        "country": lista_texto[12].find("img").get('title'),
        "subject": divs[1].find('a').text,
        "publisher": divs[2].find('a').text,
        "ISSN": divs[5].find('p').text,
        "coverage": divs[6].find('p').text,
        "scope": re.sub(r'\s+', ' ', ''.join(divs[9].find_all(string=True, recursive=False)).strip()),
        "url": f"https://www.scimagojr.com/{lista_texto[1].find_all('a')[0].get('href')}",
        "graph": scrapper_revista.find(id='embed_code').get("value")
    }}


def crear_csv(lista_revistas):
    # En verdad no lo crea la mayoria del tiempo, pero me gusto el nombre asi
    # Verifica si el archivo ya existe
    if os.path.exists('revistas.csv'):
        modo_apertura = 'a'  # Si ya existe, se abre en modo append
    else:
        modo_apertura = 'w'  # Si no existe, se abre en modo write

    with open('revistas.csv', modo_apertura, encoding="utf-8") as archivo:
        if modo_apertura == 'w':
            archivo.write(
                'Nombre;Tipo;SJR;Q;H_index;Total_docs;Total_docs_3_years;Total_refs;Total_cites_3_years;'
                'Citable_docs_3_years;Cites_doc_2_years;Ref_doc;Country;Subject;Publisher;ISSN;Coverage;Scope;url;graph\n')

        # Escribe los contenidos de las revistas
        for revista in lista_revistas:
            for nombre, datos in revista.items():
                archivo.write(
                    f"{nombre.strip()};{datos['type']};{datos['sjr']};{datos['q']};{datos['h_index']};{datos['total_docs']};" +
                    f"{datos['total_docs_3_years']};{datos['total_refs']};{datos['total_cites_3_years']};" +
                    f"{datos['citable_docs_3_years']};{datos['cites_doc_2_years']};{datos['ref_doc']};" +
                    f"{datos['country']};{datos['subject']};{datos['publisher']};{datos['ISSN']};{datos['coverage']};" +
                    f'{datos['scope'].replace(";", ".")};{datos["url"]};"{datos["graph"]}"\n'
                )


def revistas_por_anio():
    for i in range(2016, 2024):
        url = f'https://www.scimagojr.com/journalrank.php?year={i}'
        scrapper = crear_scrapper(url)
        web_crawling(scrapper, url)


def comprobar_existencia_csv():
    if os.path.exists('revistas.csv'):
        datos = {}
        with open("revistas.csv", newline='', encoding='utf-8') as archivo_csv:
            lector_csv = csv.DictReader(archivo_csv, delimiter=";", quotechar="'")
            for fila in lector_csv:
                datos[dict(fila)['Nombre']] = dict(fila)
        return datos
    else:
        # Ahora mismo esta para que solo lea el año 2023 y la primera pagina,
        # pero si se usa el metodo revistas_por_anio() ya lee todos los años y paginas
        # revistas_por_anio()
        url = f'https://www.scimagojr.com/journalrank.php?year={2023}'
        scrapper = crear_scrapper(url)
        scrapear_datos_general(scrapper)
        return comprobar_existencia_csv()


def crear_diccionario_palabras(diccionario: dict):
    # Crea un diccionario con cada palabra de cada nombre de las revistas,
    # donde la key es la palabra y el value es los nombres de las revistas que contienen esa palabra
    diccionario_palabras = {}
    for nombre, datos in diccionario.items():
        for palabra in nombre.split():
            if palabra not in diccionario_palabras:
                diccionario_palabras[palabra.capitalize()] = [nombre]
            else:
                diccionario_palabras[palabra.capitalize()].append(nombre)
    return diccionario_palabras


def crear_diccionario_letras(diccionario: dict):
    # Crea un diccionario con cada letra de cada nombre de las revistas,
    # donde la key es la letra con la que inicia y el value es los nombres de las revistas que contienen esa letra
    diccionario_letras = {}
    for nombre, datos in diccionario.items():
        for letra in nombre[0].upper():
            if letra not in diccionario_letras:
                diccionario_letras[letra] = [nombre.capitalize()]
            else:
                diccionario_letras[letra].append(nombre.capitalize())
    return diccionario_letras


def ordenar_diccionario(diccionario: dict):
    llaves_ordenadas = sorted(diccionario.keys(), key=lambda x: x.lower())
    diccionario_ordenado = {key: diccionario[key] for key in llaves_ordenadas}
    return diccionario_ordenado


if __name__ == '__main__':
    print(ordenar_diccionario(comprobar_existencia_csv()))
