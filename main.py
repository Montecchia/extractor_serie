import toga
from toga.style import Pack
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW
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


def iniciar_proceso(nombre_archivo, url, url_page, cant_paginas, formato, table):
    archivo = open(nombre_archivo, "w+", encoding="utf-8")
    scraper = cloudscraper.create_scraper()
    print('Iniciando extracción...')
    contador = 0
    for i in range(1, cant_paginas + 1):
        web = scraper.get(url)
        soup = BeautifulSoup(web.text, "html5lib").find_all(formato)
        for link in soup:
            serie = link.find("a", href=True)
            if serie is not None:
                nombre = serie.get_text().strip()
                if len(nombre) > 10:
                    nombre_limpio = limpiar_nombre(nombre)
                    url_completo = completar_link(url, serie["href"])
                    archivo.write(nombre_limpio + " : " + url_completo + "\n")
                    table.data.append([nombre_limpio, url_completo])
                    contador += 1
        url = url_page + str(i + 1)
        print("Procesando ", contador, "series, página:", i)
    print("Encontradas", contador, "series")
    archivo = limpiar_archivo(archivo)
    archivo.close()


class ExtractorSeries (toga.App):
    def startup(self):

        main_box = toga.Box(style=Pack(direction=COLUMN))

        box_nombre = toga.Box(style=Pack(direction=ROW, padding=5))
        input_nombre = toga.TextInput(value="ejemplo.txt", style=Pack(flex=1))
        label_nombre = toga.Label("Nombre del archivo:                    ")
        box_nombre.add(label_nombre)
        box_nombre.add(input_nombre)

        box_url = toga.Box(style=Pack(direction=ROW, padding=5))
        input_url = toga.TextInput(value="https://test.com/series/", style=Pack(flex=1))
        label_url = toga.Label("URL del listado de series:             ")
        box_url.add(label_url)
        box_url.add(input_url)

        box_url2 = toga.Box(style=Pack(direction=ROW, padding=5))
        input_url2 = toga.TextInput(value="https://test.com/series/page/", style=Pack(flex=1))
        label_url2 = toga.Label("URL del listado de páginas:         ")
        box_url2.add(label_url2)
        box_url2.add(input_url2)

        box_cantp = toga.Box(style=Pack(direction=ROW, padding=5))
        input_cantp = toga.TextInput(value="0", style=Pack(flex=1))
        label_cantp = toga.Label("Cantidad de páginas a analizar:  ")
        box_cantp.add(label_cantp)
        box_cantp.add(input_cantp)

        box_label = toga.Box(style=Pack(direction=ROW, padding=5))
        input_label = toga.TextInput(value="div", style=Pack(flex=1))
        label_label = toga.Label("Etiqueta HTML a buscar:             ")
        box_label.add(label_label)
        box_label.add(input_label)

        box_campos = toga.Box(style=Pack(direction=COLUMN))
        box_campos.add(box_nombre)
        box_campos.add(box_url)
        box_campos.add(box_url2)
        box_campos.add(box_cantp)
        box_campos.add(box_label)

        table = toga.Table(headings=["Nombre", "Dirección"], style=Pack(flex=1))

        def iniciar():
            def on_press(input_button):
                try:
                    return iniciar_proceso(input_nombre.value,
                                           input_url.value,
                                           input_url2.value,
                                           int(input_cantp.value),
                                           input_label.value,
                                           table)
                except Exception as e:
                    print(str(e))
            return on_press



        input_button = toga.Button("Iniciar", on_press=iniciar())

        main_box.add(input_button)
        main_box.add(box_campos)
        main_box.add(table)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return ExtractorSeries(formal_name="Extractor de series",
                           app_name="extractor_series",
                           app_id="extractor_series",
                           icon="icono",
                           author="Eduardo Montecchia",
                           description="Versión 0.1.1")


if __name__ == '__main__':
    main().main_loop()
