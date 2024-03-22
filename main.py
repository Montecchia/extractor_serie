from bs4 import BeautifulSoup
import cloudscraper


def completar_link(link_base, link):
    link_correcto = ""
    cont = 2
    for letra in link_base:
        if letra != "/" or cont != 0:
            link_correcto += letra
            cont -= 1
    if not link.startswith("http"):
        link = link_correcto + link
    return link


def limpiar_nombre(nombre):
    nombre_limpio = ""
    for letra in nombre:
        if letra == "[":
            break
        nombre_limpio += letra
    print(nombre_limpio)
    return nombre_limpio.strip()


def extraer_serie(anime_url, archivo, cant_paginas, formato):
    scraper = cloudscraper.create_scraper()
    print('Iniciando extracción...')
    contador = 0
    url_page = anime_url + "page/"
    for i in range(1, cant_paginas):
        web = scraper.get(anime_url)
        soup = BeautifulSoup(web.text, "html5lib").find_all(formato)
        for link in soup:
            anime = link.find("a", href=True)
            if anime is not None:
                nombre = anime.get_text()
                if len(nombre) > 10:
                    archivo.write(limpiar_nombre(nombre) + ": " + completar_link(anime_url, anime["href"]) + "\n")
                    contador += 1
                    print("Procesando ", contador, "animes, página:", i)
        anime_url = url_page + str(i + 1) + "/"
    print("Encontrados", contador, "animes")


if __name__ == '__main__':

    nombre_txt = input("Ingrese el nombre de la página: ")
    url = input("Ingrese la dirección del listado de series: ")
    cantidad_paginas = int(input("Ingrese la cantidad de páginas a escanear: "))
    formato = input("Ingrese el formato de la etiqueta html para los títulos: ")
    f = open(nombre_txt + ".txt", "w", encoding="utf-8")
    extraer_serie(url, f, cantidad_paginas, formato)
    f.close()
