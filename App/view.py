"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
import sys
import controller
import threading
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import stack
assert cf
from DISClib.ADT import graph as gr
"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("1- Inicializar Analizador")
    print("2- Cargar información en el catálogo")
    print("3- Req. 1: Identificar los clústeres de comunicación")
    print("4- Req. 2: Identificar los puntos de conexión críticos de la red")
    print("5- Req. 3: La ruta de menor distancia")
    print("6- Req. 4: Identificar la Infraestructura Crítica de la Red")
    print("7- Req. 5: Análisis de fallas ")
    print("8- Req. 6: Los mejores canales para transmitir")
    print("9- Req. 7: La mejor ruta para comunicarme ")
    print("10- Req. 8: Graficando los Grafos ")
    print("0- Salir")
    print("*******************************************")


def initCatalog():
    """
    Inicializa el catálogo de eventos
    """
    return controller.initCatalog()

def loadData(catalog):
    """
    Carga los datos en la estructura de datos
    """
    return controller.loadData(catalog)


def printCarga(catalog, primer_point, ultimo_country):
    print("Total de landing points: ", controller.TotalVertices(catalog))
    print("Total de conexiones entre landing points: ", controller.TotalEdges(catalog))
    print("Total de países con al menos un landing point: ", controller.TotalCountries(catalog))
    point1 = primer_point
    print("\nPrimer landing point cargado: "
        +"\nLanding Point id: "+str(point1["landing_point_id"])
        +"\nNombre: "+str(point1["location"][0])
        +"\nLatitud: "+str(point1["latitude"])
        +"\nLongitud: "+str(point1["longitude"]))
    pais235 = ultimo_country
    print("\nÚltimo país cargado: "
        +"\nPoblación: "+str(pais235["population"])
        +"\nNúmero de usuarios de internet: "+str(pais235["users"]))

def printReq1(numero_clusteres, mismo_cluster):
    print('\nEl número de clústeres es: ' +
        str(numero_clusteres))
    if mismo_cluster:
        print('Los landing points se encuentran en el mismo clúster')
    else:
        print('Los landing points no se encuentran en el mismo clúster')

def printReq2(puntos_interconexion):
    #lista_llaves = mp.keySet(respuesta)
    print("La lista de landing points que sirven como punto de interconexión "+
        "a más cables en la red es: ")
    i = 1
    for cada_mapa in lt.iterator(puntos_interconexion):
        ciudad = mp.get(cada_mapa, "city")["value"]
        pais = mp.get(cada_mapa, "country")["value"]
        lp = mp.get(cada_mapa, "id")["value"]
        lista_cables = mp.keySet(mp.get(cada_mapa, "mapa_cables")["value"])

        print(str(i)+". "+ciudad+" - "+pais+" - "+lp)
        print("\nLos cables que se conectan a "+ciudad+" son: ")
        i += 1
        j = 1
        for cable in lt.iterator(lista_cables):
            print(str(j)+". "+cable)
            j += 1


def printReq3(respuesta, pais1, pais2):
    if respuesta[0]:
        i = 1
        print("\nLa ruta mínima en distancia es: ")
        for mapa_recorrido in lt.iterator(respuesta[1]):
            vertice1 = mp.get(mapa_recorrido, "vertice1")["value"]
            vertice2 = mp.get(mapa_recorrido, "vertice2")["value"]
            peso = round(mp.get(mapa_recorrido, "peso")["value"],1)
            print(str(i)+". "+vertice1+" --> "+vertice2+ " con una distancia de "+str(peso)+" km")
            i += 1
        print("\nLa distancia total recorrida fue: "+str(round(respuesta[2],1))+" km")

    else:
        print("No existe un camino entre "+pais1+" y "+pais2+" :'(")

def printReq4(respuesta):
    print("El número de nodos conectados a la red de expansión mínima del SCC mayor es: "
        +str(respuesta[0]))
    print("El costo total de la red de expansión mínima es: "
        +str(round(respuesta[1],1))+" km")
    print("La conexión más larga que hace parte de la red de expansión mínima es: "
        +str(round(respuesta[2],1))+" km")
    print("La conexión más corta que hace parte de la red de expansión mínima es: "
        +str(round(respuesta[3],4))+" km"   )
    
def printReq5(respuesta):
    print("\nEl número de países afectados es: "+str(respuesta[0]))
    print("\nLa lista de los países afectados es: ")
    i = 1
    for lista_pais in lt.iterator(respuesta[1]):
        pais = lt.firstElement(lista_pais)
        distancia = lt.lastElement(lista_pais)
        print(str(i)+". "+str(pais)+" a una distancia de "+str(round(distancia,1))+" km")
        i+=1

def printReq6(esta_pais, mapa_paises, pais, cable):
    if esta_pais:
        print("\nLa lista de países conectados a "+pais+" por "+cable+" es:")
        for cada_pais in lt.iterator(mp.keySet(mapa_paises)):
            ancho_maximo = mp.get(mapa_paises, cada_pais)["value"]
            print("-"+cada_pais+": se puede asegurar un ancho de banda de "+str(round(ancho_maximo,3))+" Mbps")
    else:
        print("El cable "+cable+" no conecta a "+pais)
        
def printReq7(hay_camino, camino, ip1, ip2):
    if hay_camino:
        print("\nLa ruta mínima en número de saltos de "+ip1+" a "+ip2+" es:")
        for i in range(stack.size(camino)):
            top = stack.pop(camino)
            if i >= 1:
                print(str(i)+". "+memoria+" --> "+top)
            memoria = top

        print("\nEl total de pasos es: "+str(i))

    else:
        print("No existe una ruta entre "+ip1+" y "+ip2)


catalog = None

"""
Menu principal
"""
def thread_cycle():
    while True:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n')
        if int(inputs) == 1:
            print("\nInicializando....")
            catalog = initCatalog()
            #controller.BogBquilla()

        elif int(inputs) == 2:
            print("Cargando información de los archivos ....")
            tiempo, memoria, primer_point, ultimo_country = loadData(catalog)

            printCarga(catalog, primer_point, ultimo_country)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe han cargado los datos")

        elif int(inputs) == 3:
            landing_point1 = input("Ingrese el primer landing point: ")
            landing_point2 = input("Ingrese el segundo landing point: ")
            landing_point1, landing_point2 = "Accra", "Aden"
            #landing_point1, landing_point2 = "Accra", "Bishkek"
            #landing_point1, landing_point2 = "Bishkek", "Astana"
            point_id1 = controller.getPointID(catalog, landing_point1) # 1121
            point_id2 = controller.getPointID(catalog, landing_point2)
            vert1 = controller.getPrimerVertice(catalog, point_id1) # 1121-africa
            vert2 = controller.getPrimerVertice(catalog, point_id2)

            tiempo, memoria, numero_clusteres, mismo_cluster = controller.requerimiento1(catalog, vert1, vert2)
            
            printReq1(numero_clusteres, mismo_cluster)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe ejecutó el requerimiento 1\n")

        elif int(inputs) == 4:
            tiempo, memoria, puntos_interconexion = controller.requerimiento2(catalog)
            printReq2(puntos_interconexion)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe ejecutó el requerimiento 2\n")

        elif int(inputs) == 5:
            pais1 = input("Ingrese el país de origen: ")
            pais2 = input("Ingrese el país de destino: ")
            pais1 = "Ireland"
            pais2 = "Portugal"
            tiempo, memoria, ruta_min = controller.requerimiento3(catalog, pais1, pais2)
            printReq3(ruta_min, pais1, pais2)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe ejecutó el requerimiento 3\n")

        elif int(inputs) == 6:
            tiempo, memoria, respuesta = controller.requerimiento4(catalog)
            printReq4(respuesta)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe ejecutó el requerimiento 4\n")

        elif int(inputs) == 7:
            landing_point = input("Ingrese el landing point: ")
            landing_point = "Barranquilla"
            point_id = controller.getPointID(catalog, landing_point)
            tiempo, memoria, lista_paises = controller.requerimiento5(catalog, point_id)
            printReq5(lista_paises)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe ejecutó el requerimiento 5\n")

        elif int(inputs) == 8:
            pais = input("Ingrese el país: ")
            cable = input("Ingrese el nombre del cable: ")
            pais, cable = "Cuba", "ALBA-1"
            tiempo, memoria, esta_pais, mapa_paises = controller.requerimiento6(catalog, pais, cable)
            printReq6(esta_pais, mapa_paises, pais, cable)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe ejecutó el requerimiento 6\n")

        elif int(inputs) == 9:
            ip1 = input("Ingrese la primera dirección IP: ")
            ip2 = input("Ingrese la segunda dirección IP: ")
            ip1, ip2 = "24.48.0.1", "20.48.0.1"
            tiempo, memoria, hay_camino, camino = controller.requerimiento7(catalog, ip1, ip2)
            printReq7(hay_camino, camino, ip1, ip2)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe ejecutó el requerimiento 7\n")

        elif int(inputs) == 10:
            tiempo, memoria = controller.requerimiento8(catalog)
            print("\nTiempo [ms]: ", f"{tiempo:.3f}", "  ||  ",
                "Memoria [kB]: ", f"{memoria:.3f}")
            print("\nSe ejecutó el requerimiento 8\n")

        else:
            sys.exit(0)
    sys.exit(0)

if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()