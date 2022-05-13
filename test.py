import requests
import csv
import json
import datetime

"""
    Aplicación para consultas a la API de Mercado Libre:
    El programa solicita el id numérico y ubicación de registro 
    de uno o varios usuarios registrados en Mercado Libre.
    Los datos inválidos no serán admitidos y deberán ingresarse nuevamente.
    Luego, se emite un informe con formato a elección (.json, .csv, ambos 
    o ninguno) que será descargado en la misma carpeta dónde se ejecute el programa.
    El informe (indistinto el formato) contendrá los siguientes datos:
    - ID del usuario
    - Ítems publicados con sus correspondientes "id", "title" (título), 
      "category_id" (id de categoría), "name_category" (nombre de la categoría).
"""

# Infomación correspondiente al nombre del archivo de salida
def ahora():
    dia_hora = str(datetime.datetime.now())
    dia_hora = dia_hora.replace('-','').replace(':','').replace(' ','')
    dia_hora = dia_hora[0:14]
    return dia_hora

# Verifico que el usuario ingresado exista en https://api.mercadolibre.com/users
def verificar_vendedor(vendedor):
    while True:
        r = requests.get('https://api.mercadolibre.com/users/' + vendedor)
        user = r.json()
        if user['status'] == 404:
            print("Ingreso inválido, verifique.")
            vendedor = input("Ingrese /s // 0(cero) terminar: ")
        else:
            break
    return vendedor

# Verifico que la ubicación ingresada exista en https://api.mercadolibre.com/sites
def verificar_ubicacion(ubicacion):
    while True:
        r = requests.get('https://api.mercadolibre.com/sites/' + ubicacion.upper())
        site = r.json()
        if 'error' in site.keys():
            print("Ingreso inválido, verifique.")
            ubicacion = input("Ingrese ubicación: ")
            continue
        else:
            break
    return ubicacion.upper()
        
# Creo archivo LOG con los datos solicitados (id, title, category_id, name)
def salida(extension):
    # Consumo API según usuario/s y ubicación/es
    datos = []
    for seller in sellers:
        for site in sites:
            r = requests.get('https://api.mercadolibre.com/sites/'+ site.upper() +'/search?seller_id=' + seller)
            datos.append(r.json())

            if extension == 'json':
                with open('informe' + ahora() + '.' + extension, 'a', newline='') as archivo:
                    data = {}
                    for j in range(len(datos)):
                        data['id_seller'] = datos[j]['seller']['id']
                        data['items'] = []
                        for i in range(len(datos[j]['results'])):
                            id = datos[j]['results'][i]['id']
                            title = datos[j]['results'][i]['title']
                            category_id = datos[j]['results'][i]['category_id']
                            # Consumo nombre de la categoría según ubicación
                            r2 = requests.get('https://api.mercadolibre.com/categories/' + category_id)
                            cat_site = r2.json()
                            name_category = cat_site['name']
                            data['items'].append({"id": id, 
                                "title": title, 
                                "category_id": category_id, 
                                "name_category": name_category
                            })
                    json.dump(data, archivo, indent=4)
            elif extension == 'csv':
                with open('informe' + ahora() + '.' + extension, 'a', newline='') as archivo:
                    data = []
                    encabezado = ['id', 'title', 'category_id', 'name_category']
                    for j in range(len(datos)):
                        for i in range(len(datos[j]['results'])):
                            id = datos[j]['results'][i]['id']
                            title = datos[j]['results'][i]['title']
                            category_id = datos[j]['results'][i]['category_id']
                            # Consumo nombre de la categoría según ubicación
                            r2 = requests.get('https://api.mercadolibre.com/categories/' + category_id)
                            cat_site = r2.json()
                            name_category = cat_site['name']
                            data.append([id, title, category_id, name_category])
                    escritor = csv.writer(archivo)
                    escritor.writerow(encabezado)
                    escritor.writerows(data)
                
# Ingreso usuario/s (seller_id) y sus respectivas ubicación/es (site_id)
sellers = []
sites = []

while True:
    seller_id = input("Ingrese usuario/s // 0(cero) terminar: ")
    if seller_id == '0':
        break
    seller_id = verificar_vendedor(seller_id)
    site_id = input("Ingrese ubicacion: ")
    site_id = verificar_ubicacion(site_id.upper())
    sellers.append(seller_id)
    sites.append(site_id.upper())

# Selecciono el/los formato/s de salida
while True:
    print("""
        Seleccione formato de salida:
        1 ) JSON
        2 ) CSV
        3 ) Cancelar
        """)
    opc = input(">>> ")
    if opc == '1':
        salida('json')
        print("Procesado y finalizado.")
        continue
    elif opc == '2':
        salida('csv')
        print("Procesado y finalizado.")
        continue
    elif opc == '3':
        print("Finalizado.")
        break
    else:
        print("Opción inválida!!!")
        opc = input(">>> ")