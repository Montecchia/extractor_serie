from bs4 import BeautifulSoup
import cloudscraper
import re


def completar_link(link_base, link):
    link_correcto = ""
    cont = 2
    for letra in link_base:
        if letra != "/":
            link_correcto += letra
        else:
            if cont == 0:
                break
            else:
                cont -= 1

    if not link.startswith("http") and re.match(".*\\..*", link) is None:
        link = link_correcto + link
    return link


def limpiar_nombre(nombre):
    nombre_limpio = ""
    for letra in nombre:
        if letra == "[":
            break
        nombre_limpio += letra
    nombre_limpio = re.sub(" {2}|\n", '', nombre_limpio.strip())
    print(nombre_limpio)
    return nombre_limpio


def limpiar_archivo(archivo):
    temp = open("temp.txt", "w", encoding="utf-8")
    lineas = archivo.readlines()
    for linea in lineas:
        if re.match(".*:.*", linea) is not None:
            temp.write(linea)
    archivo.close()
    return temp


def extraer_serie(url, url_page, archivo, cant_paginas, formato):
    scraper = cloudscraper.create_scraper()
    print('Iniciando extracción...')
    contador = 0
    for i in range(1, cant_paginas+1):
        web = scraper.get(url)
        soup = BeautifulSoup(web.text, "html5lib").find_all(formato)
        for link in soup:
            serie = link.find("a", href=True)
            if serie is not None:
                nombre = serie.get_text().strip()
                if len(nombre) > 10:
                    archivo.write(limpiar_nombre(nombre) + " : " + completar_link(url, serie["href"]) + "\n")
                    contador += 1
        url = url_page + str(i + 1)
        print("Procesando ", contador, "series, página:", i)
    print("Encontradas", contador, "series")


if __name__ == '__main__':

    nombre_txt = input("Ingrese el nombre de la página: ")
    url1 = input("Ingrese la dirección de la primera página del listado: ")  # pagina.xyz/series/
    url2 = input("ingrese la dirección del listado de páginas sin el número: ")  # pagina.xyz/series/page/
    cantidad_paginas = int(input("Ingrese la cantidad de páginas a escanear: "))  # 2 para páginas únicas
    formato = input("Ingrese el formato de la etiqueta html para los títulos: ")  # "p", "h2", "li", etc
    f = open(nombre_txt + ".txt", "w+", encoding="utf-8")
    extraer_serie(url1, url2, f, cantidad_paginas, formato)
    f = limpiar_archivo(f)
    f.close()
