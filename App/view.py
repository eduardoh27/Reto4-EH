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
    print("\nBienvenido")
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


def initCatalog():
    """
    Inicializa el catálogo de eventos
    """
    return controller.initCatalog()

def loadData(catalog):
    """
    Carga los datos en la estructura de datos
    """
    controller.loadData(catalog)


catalog = None

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        print("\nInicializando....")
        catalog = initCatalog()

    elif int(inputs[0]) == 2:
        print("Cargando información de los archivos ....")
        loadData(catalog)
    
    elif int(inputs[0]) == 3:
        g = gr.newGraph(directed=True)
        v1 = "v1"
        gr.insertVertex(g, v1)
        v2 = "v2"
        gr.insertVertex(g, v2)

        v3 = "v3"
        gr.insertVertex(g, v3)
        v4 = "v4"
        gr.insertVertex(g, v4)
        v5 = "v5"
        gr.insertVertex(g, v5)

        gr.addEdge(g, v1, v2)
        gr.addEdge(g, v2, v1)
        gr.addEdge(g, v1, v3)
        print(gr.degree(g, v1))

    else:
        sys.exit(0)
sys.exit(0)
