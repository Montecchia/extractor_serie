import toga
from toga.style import Pack
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW
from bs4 import BeautifulSoup
import cloudscraper
import re
import os


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
    archivo.seek(0)
    lineas = list(set(archivo.readlines()))
    print("Encontradas", len(lineas), "series")
    nombre_archivo = os.path.basename(archivo.name)
    archivo.close()
    archivo = open(nombre_archivo, "w+", encoding="utf-8")
    for linea in lineas:
        if re.match(".*:.*", linea) is not None:
            archivo.write(linea)
    return archivo


def tiene_html(url):
    if url.endswith(".html"):
        return ".html"
    else:
        return ""


def cargar_tabla(archivo, tabla):
    archivo.seek(0)
    lineas = archivo.readlines()
    for linea in lineas:
        nombre_serie = " ".join(linea.split()[0:-2])
        url_serie = linea.split()[-1]
        tabla.data.append([nombre_serie, url_serie])


def crear_archivo(nombre):
    if nombre.endswith(".txt"):
        nombre_archivo = nombre
    else:
        nombre_archivo = nombre + ".txt"
    return open(nombre_archivo, "w+", encoding="utf-8")


def iniciar_proceso(nombre_archivo, url, url_page, cant_paginas, formato, tabla, progress_bar):
    archivo = crear_archivo(nombre_archivo)
    scraper = cloudscraper.create_scraper()
    print('Iniciando extracción...')
    contador = 0
    ultimo_contador = 0
    for i in range(1, cant_paginas + 1):
        web = scraper.get(url)
        soup = BeautifulSoup(web.text, "html5lib").find_all(formato)
        for link in soup:
            serie = link.find("a", href=True)
            if serie is not None:
                nombre = serie.get_text().strip()
                if len(nombre) > 5:
                    nombre_limpio = limpiar_nombre(nombre)
                    url_completo = completar_link(url, serie["href"])
                    archivo.write(nombre_limpio + " : " + url_completo + "\n")
                    contador += 1
        if contador - ultimo_contador < 2:
            print("Última página alcanzada, abortando proceso")
            progress_bar.value = cant_paginas
            break
        ultimo_contador = contador
        progress_bar.value = i+1
        url = url_page + str(i + 1) + tiene_html(url)

        print("Procesando ", contador, "enlaces, página:", i)
    archivo = limpiar_archivo(archivo)
    cargar_tabla(archivo, tabla)
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
        input_cantp = toga.NumberInput(min=1, step=1, value = 1, style=Pack(flex=1))
        label_cantp = toga.Label("Cantidad de páginas a analizar:  ")
        box_cantp.add(label_cantp)
        box_cantp.add(input_cantp)

        box_label = toga.Box(style=Pack(direction=ROW, padding=5))
        input_label = toga.TextInput(value="div", style=Pack(flex=1))
        label_label = toga.Label("Etiqueta HTML a buscar:             ")
        box_label.add(label_label)
        box_label.add(input_label)

        box_info = toga.Box()
        progress_bar = toga.ProgressBar(max=input_cantp.value, style=Pack(flex=1))
        box_info.add(progress_bar)



        box_campos = toga.Box(style=Pack(direction=COLUMN))
        box_campos.add(box_nombre)
        box_campos.add(box_url)
        box_campos.add(box_url2)
        box_campos.add(box_cantp)
        box_campos.add(box_label)
        box_campos.add(box_info)

        table = toga.Table(headings=["Nombre", "Dirección"], style=Pack(flex=1))

        def iniciar():
            def on_press(input_button):
                try:
                    progress_bar.max = input_cantp.value
                    return iniciar_proceso(input_nombre.value,
                                           input_url.value,
                                           input_url2.value,
                                           int(input_cantp.value),
                                           input_label.value,
                                           table,
                                           progress_bar)
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
                           description="Versión 0.1.2")


if __name__ == '__main__':
    main().main_loop()
