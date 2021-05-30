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


def printCarga(catalog, respuesta):
    print("Total de landing points: ", controller.TotalVertices(catalog))
    print("Total de conexiones entre landing points: ", controller.TotalEdges(catalog))
    print("Total de países con al menos un landing point: ", controller.TotalCountries(catalog))
    point1 = respuesta[0]
    print("\nPrimer landing point cargado: "
        +"\nLanding Point id: "+str(point1["landing_point_id"])
        +"\nNombre: "+str(point1["location"][0])
        +"\nLatitud: "+str(point1["latitude"])
        +"\nLongitud: "+str(point1["longitude"]))
    pais235 = respuesta[1]
    print("\nÚltimo país cargado: "
        +"\nPoblación: "+str(pais235["population"])
        +"\nNúmero de usuarios de internet: "+str(pais235["users"]))

def printReq1(numero_clusteres, mismo_componente):
    print('\nEl número de componentes conectados es: ' +
        str(numero_clusteres))
    if mismo_componente:
        print('Los landing points no se encuentran en el mismo componente')
    else:
        print('Los landing points se encuentran en el mismo componente')


def printReq4(respuesta):
    print("El número de nodos conectados a la red de expansión mínima es: "
        +str(respuesta[0]))
    print("El costo total de la red de expansión mínima es: "
        +str(round(respuesta[1],1)))
    print("La conexión más larga que hace parte de la red de expansión mínima es: "
        +str(round(respuesta[2],1)))
    print("La conexión más corta que hace parte de la red de expansión mínima es: "
        +str(round(respuesta[3],5)))
    
def printReq5(respuesta):
    print("\nEl número de países afectados es: "+str(respuesta[0]))
    print("La lista de los países afectados es: ")
    i = 1
    for pais in lt.iterator(respuesta[1]):
        print(str(i)+". "+str(pais))
        i+=1

catalog = None

"""
Menu principal
"""
def thread_cycle():
    while True:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n')
        if int(inputs[0]) == 1:
            print("\nInicializando....")
            catalog = initCatalog()

        elif int(inputs[0]) == 2:
            print("Cargando información de los archivos ....")
            respuesta = loadData(catalog)
            printCarga(catalog, respuesta)
            #for i in lt.iterator(gr.vertices(catalog["connections"])):
                #print(i)
            print("\nSe han cargado los datos")

        elif int(inputs[0]) == 3:
            landing_point1 = input("Ingrese el primer landing point: ")
            landing_point2 = input("Ingrese el segundo landing point: ")
            landing_point1, landing_point2 = "Accra", "Aden"
            point_id1 = controller.getPointID(catalog, landing_point1)
            point_id2 = controller.getPointID(catalog, landing_point2)
            numero_clusteres = controller.connectedComponents(catalog)
            mismo_componente = controller.sameComponent(catalog, point_id1, point_id2)
            printReq1(numero_clusteres, mismo_componente)
            print("\nSe ejecutó el requerimiento 1\n")

        elif int(inputs[0]) == 4:
            pass

        elif int(inputs[0]) == 5:
            pass

        elif int(inputs[0]) == 6:
            respuesta = controller.minExpansion(catalog)
            printReq4(respuesta)
            print("\nSe ejecutó el requerimiento 4\n")

        elif int(inputs[0]) == 7:
            landing_point = input("Ingrese el landing point: ")
            landing_point = "Barranquilla"
            point_id = controller.getPointID(catalog, landing_point)
            respuesta = controller.affectedCountries(catalog, point_id)
            printReq5(respuesta)
            print("\nSe ejecutó el requerimiento 5\n")

        else:
            sys.exit(0)
    sys.exit(0)

if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()