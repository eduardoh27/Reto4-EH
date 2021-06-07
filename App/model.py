"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import orderedmap as om
from DISClib.ADT import graph as gr
from DISClib.ADT import stack
from DISClib.ADT import minpq as pq
from DISClib.Utils import error as error
from DISClib.Algorithms.Sorting import mergesort as mg
from DISClib.DataStructures import mapentry as me
from DISClib.DataStructures import edge as e
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import prim 
from DISClib.Algorithms.Graphs import bfs

import math
import requests
import folium
import matplotlib
import random
assert cf
import haversine as hs
"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, 
otra para las categorias de los mismos.
"""

def newCatalog():
    """ Inicializa el catálogo

    Crea un diccionario cuyos valores serán las estructuras de datos.
    Se crea un Ordered Map para cada característica de contenido utilizada.
    Además, se crea un Map para las pistas y otro Map los hashtags.

    Retorna el catálogo inicializado.
    """
    catalog = {"connections":None,
                "points":None,
                "ciudades":None,
                "countries":None,
                "countries_capitales": None,
                "cables":None,
                "ancho":None,
                "anchos_landing":None,
                "components": None,
                "paths": None,
                "mapas": None}

    catalog["connections"] = gr.newGraph(datastructure='ADJ_LIST',
                                            directed=False,
                                            size=1733
                                            )

    catalog["points"] = mp.newMap(numelements=1283, maptype="PROBING", loadfactor=0.4)
    # Las llaves son cada Landing Point y los valores son mapas con la información necesario de cada LD
    # {"1020(id de Bogotá)":{"id": 1020
    #                       "country": Colombia,
    #                       "city": Bogotá, 
    #                       "Long": 1.01, 
    #                       "Lat": -2.95,
    #                       "mapa_vertices": {"Bog-2africa": None, "Bog-ALBA1": None, ...}}}
    #                       "mapa_cables": {"2africa": None, "ALBA-1": None, ...},
    # "2929":...}

    catalog["ciudades"] = mp.newMap(numelements=1283, maptype="PROBING", loadfactor=0.4)
    # Identifica a una ciudad ("Bogotá") con su landing_point_id (1020)
    # {"Bogotá": 1020, "Londres": 2929, ...}  

    # Identifica un cable con los vértices de ese cable
    catalog["cables"] = mp.newMap(numelements=227, maptype="PROBING", loadfactor=0.4)
    # {"2africa": {"1020-2africa": None, "2929-2africa": None, ...}, 
    #   "east-west": {"2783-east-west": None, "1020-east-west": None, ...},
    #  ...}

    catalog["cables_ancho"] = mp.newMap(numelements=227, maptype="PROBING", loadfactor=0.4)
    # {"2africa": 290.1, "east-west": 1790.2, ...}
    
     
    # Grafo "duplicado" de connections, pero tiene como peso al ancho en esa conexión          
    catalog["connections_ancho"] = gr.newGraph(datastructure='ADJ_LIST',
                                                directed=False,
                                                size=1733
                                                )

    # Como llaves está el landing point y como valor una MinPQ con los anchos de este point
    catalog["anchos_landing"] = mp.newMap(numelements=2003, maptype="PROBING", loadfactor=0.4)
    # {"1020": [1, 2, 4, 10], "2929": [3, 4, 6], ...}

    # Como llaves está el país y como valor un mapa de vértices asociados a dicho país
    catalog["countries"] = mp.newMap(numelements=307, maptype="PROBING", loadfactor=0.4)
    # {"Colombia": {"2929-2africa": None, "1020-ALBA1": None, ...}, 
    #  "Canadá": {...},
    # ...}

    catalog["countries_capitales"] = mp.newMap(numelements=307, maptype="PROBING", loadfactor=0.4)
    # Identifica un país con su Capital
    # {"Colombia": "Bogotá", "Canadá": Ottawa, ...}  

    catalog["countries_users"] = mp.newMap(numelements=307, maptype="PROBING", loadfactor=0.4)
    # Identifica un país con su número de users
    # {"Colombia": 190040, "Canadá":  4535224, ...}  

    catalog["mapas"] = mp.newMap(numelements=11, maptype="PROBING", loadfactor=0.4)

    return catalog


def addPoint(catalog, point):
    
    # Se crea una mapa donde se guardarán los datos del Landing Point
    mapa_info_point = mp.newMap(numelements=5, maptype="PROBING", loadfactor=0.4)

    ld_id = point["landing_point_id"]
    ciudad = point["location"][0]
    pais = point["location"][-1].lstrip()
    latitud = point["latitude"]
    longitud = point["longitude"]
    # Se crea un mapa donde se guardarán los múltiples vértices de un mismo Landing Point
    mapa_vertices = mp.newMap(numelements=13, maptype="PROBING", loadfactor=0.4)
    mapa_cables = mp.newMap(numelements=101, maptype="PROBING", loadfactor=0.4)

    # Se añaden los datos al mapa de datos
    mp.put(mapa_info_point, "id", ld_id)
    mp.put(mapa_info_point, "country", pais)
    mp.put(mapa_info_point, "city", ciudad)
    mp.put(mapa_info_point, "latitude", latitud)
    mp.put(mapa_info_point, "longitude", longitud)
    mp.put(mapa_info_point, "mapa_vertices", mapa_vertices)
    mp.put(mapa_info_point, "mapa_cables", mapa_cables)

    #1. Se agrega el mapa con los datos al mapa de los Landing Points
    mp.put(catalog["points"], point["landing_point_id"], mapa_info_point)
    

    #2. Se agrega a un mapa identifica a una ciudad ("Bogotá") con su 
    # landing_point_id (1020)
    mp.put(catalog["ciudades"], ciudad, point["landing_point_id"])



def addConexion(catalog, conexion):

    point_salida = conexion["origin"]
    point_llegada = conexion["destination"]
    vertice_salida = point_salida + "-" + conexion["cable_name"]
    vertice_llegada = point_llegada + "-" + conexion["cable_name"]



    #1. Se añade la conexión al grafo de Ancho de banda
    ancho = conexion["capacityTBPS"]
    addAncho(catalog, vertice_salida, vertice_llegada, ancho)
    #2. Se añade el ancho al mapa del ancho de cada cable
    mp.put(catalog["cables_ancho"], conexion["cable_name"], ancho)


    mapa_info_point1 = me.getValue(mp.get(catalog["points"], point_salida))
    latitud1 = me.getValue(mp.get(mapa_info_point1, "latitude"))
    longitud1 = me.getValue(mp.get(mapa_info_point1, "longitude"))
    mapa_cables1 = mp.get(mapa_info_point1, "mapa_cables")["value"]
    mapa_info_point2 = me.getValue(mp.get(catalog["points"], point_llegada))
    latitud2 = me.getValue(mp.get(mapa_info_point2, "latitude"))
    longitud2 = me.getValue(mp.get(mapa_info_point2, "longitude"))
    mapa_cables2 = mp.get(mapa_info_point2, "mapa_cables")["value"]
    distancia = CalcularPeso(latitud1, longitud1, latitud2, longitud2)
    #3. Se añade la conexión al grafo normal (de distancia)
    addDistance(catalog, vertice_salida, vertice_llegada, distancia)

    mp.put(mapa_cables1, conexion["cable_name"], ancho)
    mp.put(mapa_cables2, conexion["cable_name"], ancho)

    #4. Se añaden a la MinPQ asociada a cada Landing_Point
    addAnchoQueue(catalog, point_salida, ancho)
    addAnchoQueue(catalog, point_llegada, ancho)

    #5. Añade el vertice a la lista de vertices del mapa de points
    mapa_vertices1 = me.getValue(mp.get(mapa_info_point1, "mapa_vertices"))
    mp.put(mapa_vertices1, vertice_salida, None)
    mapa_vertices2 = me.getValue(mp.get(mapa_info_point2, "mapa_vertices"))
    mp.put(mapa_vertices2, vertice_llegada, None)

    #6. Añade los vértices al mapa de vértices para un cable dado dentro del mapa de cables  
    addCable(catalog, conexion["cable_name"], vertice_salida, vertice_llegada)

    #7. Añade los vértices al mapa de vértices dado un país
    pais1 = me.getValue(mp.get(mapa_info_point1, "country"))
    addVertexToCountries(catalog, pais1, vertice_salida)
    pais2 = me.getValue(mp.get(mapa_info_point2, "country"))
    addVertexToCountries(catalog, pais2, vertice_llegada)

    

def addVertexToCountries(catalog, pais, vertice):
    exist_cable = mp.contains(catalog["countries"], pais)
    if exist_cable:
        mapa_vertices = me.getValue(mp.get(catalog["countries"], pais))
        mp.put(mapa_vertices, vertice, None)
    else:
        nuevo_mapa = mp.newMap(numelements=31, maptype="PROBING", loadfactor=0.4)
        mp.put(nuevo_mapa, vertice, None)
        mp.put(catalog["countries"], pais, nuevo_mapa)

def addCable(catalog, cable_name, vertice_salida, vertice_llegada):
    exist_cable = mp.contains(catalog["cables"], cable_name)
    if exist_cable:
        mapa_vertices = me.getValue(mp.get(catalog["cables"], cable_name))
        mp.put(mapa_vertices, vertice_salida, None)
        mp.put(mapa_vertices, vertice_llegada, None)
    else:
        nuevo_mapa = mp.newMap(numelements=53, maptype="PROBING", loadfactor=0.4)
        mp.put(nuevo_mapa, vertice_salida, None)
        mp.put(nuevo_mapa, vertice_llegada, None)
        mp.put(catalog["cables"], cable_name, nuevo_mapa)

def addAnchoQueue(catalog, point, ancho):
    if mp.contains(catalog["anchos_landing"], point):
        cola = me.getValue(mp.get(catalog["anchos_landing"], point))
        pq.insert(cola, ancho)
    else:
        nueva_cola = pq.newMinPQ(cmpfunction_minPQ)
        pq.insert(nueva_cola, ancho)
        mp.put(catalog["anchos_landing"], point, nueva_cola)

def addAncho(catalog, vertice_salida, vertice_llegada, ancho):
    addVertex(catalog, "connections_ancho", vertice_salida)
    addVertex(catalog, "connections_ancho", vertice_llegada)
    addConnection(catalog, "connections_ancho", vertice_salida, vertice_llegada, ancho)

def addDistance(catalog, vertice_salida, vertice_llegada, distance):
    addVertex(catalog, "connections", vertice_salida)
    addVertex(catalog, "connections", vertice_llegada)
    addConnection(catalog, "connections", vertice_salida, vertice_llegada, distance)

def addVertex(catalog, graph, vertice):
    """
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(catalog[graph], vertice):
            gr.insertVertex(catalog[graph], vertice)
        return catalog
    except Exception as exp:
        error.reraise(exp, 'model:addstop')

def addConnection(catalog, graph, origin, destination, weight):
   
    edge = gr.getEdge(catalog[graph], origin, destination)
    if edge is None:
        gr.addEdge(catalog[graph], origin, destination, weight)

    return catalog

def CalcularPeso(latitud1, longitud1, latitud2, longitud2):

    loc1=(latitud1, longitud1)
    loc2=(latitud2, longitud2)

    return hs.haversine(loc1,loc2)




def addCountry(catalog, country):

    nombre_capital = country["capital"]
    #1. Se añade la pareja {country: capital} al mapa de países
    mp.put(catalog["countries_capitales"], country["country"], nombre_capital)

    usuarios = country["users"]
    #2.Se añade la pareja {country: usuarios} al mapa de países
    mp.put(catalog["countries_users"], country["country"],usuarios)

    #3. Se conectan las ciudades del pais con la capital
    ConectarConCapital(catalog, nombre_capital, country["country"], country["latitude"], country["longitude"])


def ConectarConCapital(catalog, vertice_capital, pais, latitud_capital, longitud_capital):

    existe_pais = mp.get(catalog["countries"], pais)

    if existe_pais == None:
        # Si el país no existe (no tiene vértices), 
        # se busca entre todos los lp el que esté más cerca
        menor = math.inf
        point_menor = None
        for point in lt.iterator(mp.keySet(catalog["points"])):
            if point != vertice_capital:
                mapa_info_point = me.getValue(mp.get(catalog["points"], point))
                latitud_point = me.getValue(mp.get(mapa_info_point, "latitude"))
                longitud_point = me.getValue(mp.get(mapa_info_point, "longitude"))
                distancia = CalcularPeso(latitud_point, longitud_point, latitud_capital, longitud_capital)
                if distancia < menor:
                    menor = distancia   
                    point_menor = point

        # Teniendo el lp más cercano, se encuentran todos los vértices de dicho lp
        lista_vertices = mp.keySet(mp.get(mp.get(catalog["points"], point_menor)["value"], "mapa_vertices")["value"])
        # Se añade al vértice capital a todas las estructuras necesarias
        # catalog["ciudades"], catalog["countries"], catalog["points"],  tmb a catalog["anchos_landing"]
        
        # esto se hace en addPoint: mp.put(catalog["ciudades"], vertice_capital, vertice_capital)
        addVertexToCountries(catalog, pais, vertice_capital)
        addPoint(catalog, {"landing_point_id": vertice_capital, "location": [vertice_capital, pais],
                        "latitude": latitud_capital, "longitude": longitud_capital})
        mapa_info_point = me.getValue(mp.get(catalog["points"], vertice_capital))
        mapa_vertices = me.getValue(mp.get(mapa_info_point, "mapa_vertices"))
        mp.put(mapa_vertices, vertice_capital, None)
        #
        #vertice_capital = vertice_capital
        
    else:
        lista_vertices = mp.keySet(me.getValue(existe_pais))
        #
        if mp.contains(catalog["ciudades"], vertice_capital):
            vertice_capital = mp.get(catalog["ciudades"], vertice_capital)["value"]
        else:
            addVertexToCountries(catalog, pais, vertice_capital)
            #mp.put(catalog["ciudades"], vertice_capital, vertice_capital)
            addPoint(catalog, {"landing_point_id": vertice_capital, "location": [vertice_capital, pais],
                        "latitude": latitud_capital, "longitude": longitud_capital})
            mapa_info_point = me.getValue(mp.get(catalog["points"], vertice_capital))
            mapa_vertices = me.getValue(mp.get(mapa_info_point, "mapa_vertices"))
            mp.put(mapa_vertices, vertice_capital, None)           
           #vertice_capital = vertice_capital
        #

    for vertice in lt.iterator(lista_vertices):
        if vertice == vertice_capital or getLandingPoint(vertice) == vertice_capital:
            pass
        else:
            point = getLandingPoint(vertice)
            mapa_info_point = me.getValue(mp.get(catalog["points"], point))
            #
            latitud_point = me.getValue(mp.get(mapa_info_point, "latitude"))
            longitud_point = me.getValue(mp.get(mapa_info_point, "longitude"))
            distancia = CalcularPeso(latitud_capital, longitud_capital, latitud_point, longitud_point)
            addDistance(catalog, vertice, vertice_capital, distancia)
            if "-" in vertice:
                cable = getCable(vertice)
                lp_capital = getLandingPoint(vertice_capital)
                mapa_cables = mp.get(mp.get(catalog["points"], lp_capital)["value"], "mapa_cables")["value"]
                mp.put(mapa_cables, cable, None)

def ConectarConCapital1(catalog, capital, pais, latitud_capital, longitud_capital):
    existe_pais = mp.get(catalog["countries"], pais)

    if existe_pais:
        if mp.contains(catalog["ciudades"], capital):
            capital = mp.get(catalog["ciudades"], capital)["value"]
        else:
            addPoint(catalog, {"landing_point_id": capital, "location": [capital, pais],
            "latitude": latitud_capital, "longitude": longitud_capital})
        lista_vertices = mp.keySet(existe_pais["value"])
        
    else:
        menor = math.inf
        point_menor = None
        for point in lt.iterator(mp.keySet(catalog["points"])):
            if point != capital:
                mapa_info_point = mp.get(catalog["points"], point)["value"]
                latitud_point = mp.get(mapa_info_point, "latitude")["value"]
                longitud_point = mp.get(mapa_info_point, "longitude")["value"]
                distancia = CalcularPeso(latitud_point, longitud_point, latitud_capital, longitud_capital)
                if distancia < menor:
                    menor = distancia   
                    point_menor = point
        lista_vertices = mp.keySet(mp.get(mp.get(catalog["points"], point_menor)["value"], "mapa_vertices")["value"])

        addPoint(catalog, {"landing_point_id": capital, "location": [capital, pais],
                "latitude": latitud_capital, "longitude": longitud_capital})

    for vertice in lt.iterator(lista_vertices):
        if vertice == capital or getLandingPoint(vertice) == capital:
            pass
        else:
            point = getLandingPoint(vertice)
            #print(point)
            cable_menor, ancho_menor = getCableAnchoMenor(catalog, point)

            vertice_capital = capital+"-"+cable_menor
            addVertexToCountries(catalog, pais, vertice_capital)
            mapa_info_point = mp.get(catalog["points"], capital)["value"]
            mapa_vertices = mp.get(mapa_info_point, "mapa_vertices")["value"]
            mp.put(mapa_vertices, vertice_capital, None)
            mapa_cables = mp.get(mapa_info_point, "mapa_cables")["value"]
            mp.put(mapa_cables, cable_menor, ancho_menor)

            latitud_point = mp.get(mapa_info_point, "latitude")["value"]
            longitud_point = mp.get(mapa_info_point, "longitude")["value"]
            distancia = CalcularPeso(latitud_capital, longitud_capital, latitud_point, longitud_point)
            addDistance(catalog, vertice, vertice_capital, distancia)

def getCableAnchoMenor(catalog, lp):
    mapa_info_point = mp.get(catalog["points"], lp)["value"]
    mapa_cables = mp.get(mapa_info_point, "mapa_cables")["value"]
    ancho_menor = math.inf
    cable_menor = None
    for cable in lt.iterator(mp.keySet(mapa_cables)):
        ancho_cable = mp.get(mapa_cables, cable)["value"]
        if ancho_cable < ancho_menor:
            ancho_menor = ancho_cable
            cable_menor = cable
    return cable_menor, ancho_menor


def getLandingPoint(vertice):

    if "-" in vertice:
        indice = vertice.index("-")
        vertice = vertice[:indice]
    return vertice


def getCable(vertice):

    indice = vertice.index("-")
    return vertice[indice+1:]


def ConectarPointsIguales(catalog):

    for point in lt.iterator(mp.keySet(catalog["points"])):
        valor_point = me.getValue(mp.get(catalog["points"], point))
        mapa_vertices = me.getValue(mp.get(valor_point, "mapa_vertices"))
        #Se obtiene la el mapa de {mapa_vertices, country, lat, long, city}
        lista_vertices = mp.keySet(mapa_vertices)
        tamaño = lt.size(lista_vertices)
        i = 1
        while i < tamaño:
            vertice = lt.getElement(lista_vertices, i)
            #SOLO SE CONECTA AL LP CON CADA VERTICE DEL MISMO LD POR MEDIO DE LA DISTANCIA (no el ancho)
            # NO SEA CREA UN VÉRTICE DE SOLO LP
            #addDistance(catalog, point, vertice, 0)
            j = i+1
            while j <= tamaño:
                vertice1 = lt.getElement(lista_vertices, j)
                addDistance(catalog, vertice, vertice1, 0.1)
                cola = me.getValue(mp.get(catalog["anchos_landing"], point))
                ancho = pq.min(cola)
                addAncho(catalog, vertice, vertice1, ancho)
                j += 1
            i += 1

def getPointID(catalog, landing_point):
    point = me.getValue(mp.get(catalog["ciudades"], landing_point))
    return point

def getPrimerVertice(catalog, landing_point):
    mapa_info_point = mp.get(catalog["points"], landing_point)["value"]
    mapa_vertices = mp.get(mapa_info_point, "mapa_vertices")["value"]
    lista_vertices = mp.keySet(mapa_vertices)
    return lt.firstElement(lista_vertices)

############################
# Funciones de comparación #
############################

def cmpfunction_minPQ (p1, p2):
    return p1 > p2

def cmpfunction_maxPQ (p1, p2):
    return p1 < p2

#########################
# Funciones de consulta #
#########################

def TotalVertices(catalog):
    return gr.numVertices(catalog["connections"])

def TotalEdges(catalog):
    return gr.numEdges(catalog["connections"])

def TotalCountries(catalog):
    return mp.size(catalog["countries"])


########################################### 1 #################################################
def connectedComponents(catalog):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    # Se guarda en catalog el resultado de Kosaraju
    catalog["components"] = scc.KosarajuSCC(catalog["connections"])
    # Se busca el número de clústeres del grafo
    return scc.connectedComponents(catalog["components"])

def sameCluster(catalog, vert1, vert2):
    """
    Revisa si dos componentes están dentro de una misma SCC
    """
    # Se añaden los vértices al mapa de las gráficas
    mapa1 = mp.newMap(numelements = 3, maptype="PROBING", loadfactor = 0.4)
    mp.put(mapa1, "vertice1", vert1)
    mp.put(mapa1, "vertice2", vert2)
    mp.put(catalog["mapas"], 1, mapa1)

    # Se revisa si los dos vértices están en el mismo clúster
    return scc.stronglyConnected(catalog["components"], vert1, vert2)
########################################### 1 #################################################


########################################### 2 #################################################
def puntos_interconexion(catalog):
    # Mapa que tiene como llaves el número de cables y como valor una lista con los lp 
    # que tienen ese número
    mapa_ordenado = om.newMap()

    # Se recorren todos los landing point
    for lp in lt.iterator(mp.keySet(catalog["points"])):
        mapa_info_point = mp.get(catalog["points"], lp)["value"]
        # Se obtienen los datos necesarios del landing point: ciudad, país
        # y mapa con los cables de dicho lp
        mapa_cables = mp.get(mapa_info_point, "mapa_cables")["value"]
        num_cables = mp.size(mapa_cables)

        # Se añade al mapa ordenado por número de cables
        addToOM(mapa_ordenado, num_cables, mapa_info_point)

    cantidad_mayor = om.maxKey(mapa_ordenado)
    lista_mayores = om.get(mapa_ordenado, cantidad_mayor)["value"]
    # Se obtiene la lista con los lp con mayor número de cables

    mp.put(catalog["mapas"], 2, lista_mayores)

    return lista_mayores

def addToOM(mapa_ordenado, cantidad_vertices, mapa_lp):
    # {1: [{1121, Bogotá, Colombia, [cables]}, {3542, ...}], 2: [{}, ...]}
    existe_cantidad = om.contains(mapa_ordenado, cantidad_vertices)
    if existe_cantidad:
        lista = om.get(mapa_ordenado, cantidad_vertices)["value"]
        lt.addLast(lista, mapa_lp)
    else:
        lista_nueva = lt.newList("ARRAY_LIST")
        lt.addLast(lista_nueva, mapa_lp)
        om.put(mapa_ordenado, cantidad_vertices, lista_nueva) 
########################################### 2 #################################################



########################################### 3 #################################################
def rutaMinimaCountries(catalog, pais1, pais2):
    capital1 = mp.get(catalog["countries_capitales"], pais1)["value"]
    capital2 = mp.get(catalog["countries_capitales"], pais2)["value"]
    vertice_capital1 = mp.get(catalog["ciudades"], capital1)["value"]
    vertice_capital2 = mp.get(catalog["ciudades"], capital2)["value"]

    # Se ejecuta Dijkstra
    minimumCostPaths(catalog, vertice_capital1)
    # Se comprueba un camino a capital2
    hay_camino = hasPath(catalog, vertice_capital2)
    # Se halla ese camino
    recorrido = minimumCostPath(catalog, vertice_capital2)

    # Se guarda el camino en una lista (para view y gráfica)
    lista_camino = lt.newList("ARRAY_LIST")
    distancia_total = 0
    if hay_camino:
            for i in range(stack.size(recorrido)):
                top = stack.pop(recorrido)
                vertice1 = top["vertexA"]
                vertice2 = top["vertexB"]
                peso = top["weight"]
                distancia_total+= peso
                mapa_recorrido = mp.newMap(numelements = 3, maptype= "PROBING", loadfactor = 0.4)
                mp.put(mapa_recorrido, "vertice1", vertice1)
                mp.put(mapa_recorrido, "vertice2", vertice2)
                mp.put(mapa_recorrido, "peso", peso)
                lt.addLast(lista_camino, mapa_recorrido)

    mapa3 = mp.newMap(numelements=5, maptype="PROBING", loadfactor=0.4)
    mp.put(mapa3, "lista_camino", lista_camino)
    mp.put(mapa3, "vertice_capital1", vertice_capital1)
    mp.put(mapa3, "vertice_capital2", vertice_capital2)
    mp.put(mapa3, "hay_camino", hay_camino)
    mp.put(catalog["mapas"], 3, mapa3)

    return hay_camino, lista_camino, distancia_total

def minimumCostPaths(catalog, capital1):
    """
    Calcula los caminos de costo mínimo desde la capital1
    a todos los demas vertices del grafo
    """
    catalog['paths'] = djk.Dijkstra(catalog['connections'], capital1)
    return catalog


def hasPath(catalog, capital2):
    """
    Indica si existe un camino desde la capital1 a la capital2
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    return djk.hasPathTo(catalog['paths'], capital2)


def minimumCostPath(catalog, capital2):
    """
    Retorna el camino de costo minimo entre la capital1
    y la capital2
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    path = djk.pathTo(catalog['paths'], capital2)
    return path
########################################### 3 #################################################



########################################### 4 #################################################
def minExpansion(catalog):
    # Se hace Prim sobre el grafo
    search = prim.PrimMST(catalog["connections"])
    # Se halla el peso del MST
    peso = prim.weightMST(catalog["connections"], search)
    # Se halla el arco mayor y su peso 
    mayor, arco_mayor = buscarMayor(search)
    # Se halla el arco menor y su peso
    menor, arco_menor = buscarMenor(search)
    # Se halla en número de vértices en el clúster más grande
    tamaño_mayor = getVerticesMayorSCC(catalog)
    # Se obtiene el mst
    mst = search["mst"]

    mapa4 = mp.newMap(numelements=5, maptype="PROBING", loadfactor=0.4)
    mp.put(mapa4, "mst", mst)
    mp.put(mapa4, "arco_mayor", arco_mayor)
    mp.put(mapa4, "arco_menor", arco_menor)
    mp.put(catalog["mapas"], 4, mapa4)

    return tamaño_mayor, peso, mayor, menor

def getVerticesMayorSCC(catalog):
    # Se crea un mapa {"#componente": 2324, ...}
    mapa_componentes = mp.newMap(numelements=3, maptype="PROBING", loadfactor=0.4)
    for vertice in lt.iterator(mp.keySet(catalog["components"]["idscc"])):
        numero_componente = mp.get(catalog["components"]["idscc"], vertice)["value"]
        addComponente(mapa_componentes, numero_componente)

    mayor = None
    conteo_mayor = 0
    for componente in lt.iterator(mp.keySet(mapa_componentes)):
        numero_vertices = mp.get(mapa_componentes, componente)["value"]
        if numero_vertices > conteo_mayor:
            mayor = componente
            conteo_mayor = numero_vertices
    return conteo_mayor

def addComponente(mapa_componentes, componente):
    exist_componente = mp.contains(mapa_componentes, componente)
    if exist_componente:
        contador = mp.get(mapa_componentes, componente)["value"]
        contador += 1
        mp.put(mapa_componentes, componente, contador)

    else:
        contador = 1
        mp.put(mapa_componentes, componente, contador)

def buscarMenor(search):
    buscar = math.inf
    arco_menor = None
    edges = search["mst"]
    for edge in lt.iterator(edges):
        peso = float(e.weight(edge))
        if peso != 0.1 and peso < buscar:
            buscar = peso
            arco_menor = edge
        # if peso < 0.1:
        #     print("menor",edge)
    return buscar, arco_menor

def buscarMayor(search):
    buscar = 0
    arco_mayor = None
    edges = search["mst"]
    for edge in lt.iterator(edges):
        peso = e.weight(edge)
        if peso > buscar:
            buscar = peso
            arco_mayor = edge
        # if peso > 6000:
        #     print("mayor",edge)
    return buscar, arco_mayor
########################################### 4 #################################################


########################################### 5 #################################################
def affectedCountries(catalog, point):
    # Mapa para que no se repitan los países que se guardan
    mapa_paises = mp.newMap(numelements=13, maptype="PROBING", loadfactor=0.4)

    # Lista con todos los vértices de un lp dado
    lista_vertices_point = mp.keySet(mp.get(mp.get(catalog["points"], point)["value"], "mapa_vertices")["value"])

    # Se recorren los vertices adyacentes a los vertices del lp
    # Se agregan los adyacentes a la lista para la gráfica y al mapa para view
    lista_arcos = lt.newList("ARRAY_LIST")
    for vertice_point in lt.iterator(lista_vertices_point):
        arcos_adyacentes = gr.adjacentEdges(catalog["connections"], vertice_point)
        for arco_ady in lt.iterator(arcos_adyacentes):
            lt.addLast(lista_arcos, arco_ady)
            vertice_ady = arco_ady["vertexB"]
            dist_ady = arco_ady["weight"]
            point_ady = getLandingPoint(vertice_ady)
            pais_ady= mp.get(mp.get(catalog["points"], point_ady)["value"], "country")["value"]
            addCountryToMap(mapa_paises, pais_ady, dist_ady)

    # En esta lista se guarda listas ["country": dist, ...]
    lista_final = lt.newList("ARRAY_LIST")

    # Se crean listas por cada país, de la forma ["country": dist, ...], donde dist 
    # es la distancia menor al país desde el lp y se agregan a lista_final
    for pais in lt.iterator(mp.keySet(mapa_paises)):
        cola = mp.get(mapa_paises, pais)["value"]
        menor = pq.delMin(cola)
        lista_pais = lt.newList("ARRAY_LIST")
        lt.addLast(lista_pais, pais)
        lt.addLast(lista_pais, menor)

        lt.addLast(lista_final, lista_pais)

    # Se ordena descendentemente
    sortPaises(lista_final)
    tamaño = mp.size(lista_final)

    mp.put(catalog["mapas"], 5, lista_arcos)

    return tamaño, lista_final

def addCountryToMap(mapa_paises, pais, distancia):
    exist_pais = mp.contains(mapa_paises, pais)
    if exist_pais:
        cola = mp.get(mapa_paises, pais)["value"]
        pq.insert(cola, distancia)
    else:
        nueva_cola = pq.newMinPQ(cmpfunction_minPQ)
        pq.insert(nueva_cola, distancia)
        mp.put(mapa_paises, pais, nueva_cola)

def sortPaises(lista):
    """
    Toma la lista de listas [pais, distancia] y ordena 
    de mayor de a menor por distancia
    """
    return mg.sort(lista, cmpDistancias)

def cmpDistancias (lista1, lista2):
    """
    Compara dos listas [pais, distancia] por distancia
    """
    return lt.lastElement(lista1) > lt.lastElement(lista2)  
########################################### 5 #################################################



########################################### 6 #################################################
def getPaisesAnchoMax (catalog, pais_solicitado, cable_solicitado):
    # Se obtiene el ancho del cable solicitado
    ancho_cable = mp.get(catalog["cables_ancho"], cable_solicitado)["value"]
    # Se obtienen los vértices del cable
    lista_vertices_cable = mp.keySet(mp.get(catalog["cables"], cable_solicitado)["value"])

    esta_pais_solicitado = False
    mapa_paises = mp.newMap(numelements=10, maptype="PROBING", loadfactor=0.4)
    # Se recorren los vértices del cable
    for vertice in lt.iterator(lista_vertices_cable):
        lp = getLandingPoint(vertice)
        pais = mp.get(mp.get(catalog["points"], lp)["value"], "country")["value"]
        # Se revisa si el cable llega al país solicitado
        if pais == pais_solicitado:
            esta_pais_solicitado = True
        # Se guarda en el mapa cada país con su ancho máximo
        else:
            users = mp.get(catalog["countries_users"], pais)["value"]
            ancho_maximo = float(ancho_cable) / float(users) * 1000000
            mp.put(mapa_paises, pais, ancho_maximo)

    return esta_pais_solicitado, mapa_paises
########################################### 6 #################################################



########################################### 7 #################################################
def rutaMinimaIP(catalog, ip1, ip2):
    country1, lat1, lon1 = requestAPI(ip1)
    country2, lat2, lon2 = requestAPI(ip2)
    # Se hallan los vértices más cercanos a las direcciones IP dadas
    vertice1 = get_vertice_cercano(catalog, country1, lat1, lon1)
    vertice2 = get_vertice_cercano(catalog, country2, lat2, lon2)

    # Se hace bfs desde el vertice1
    search = bfs.BreadhtFisrtSearch(catalog["connections"], vertice1)
    # Se comprueba si existe un camino al vertice2
    hay_camino = bfs.hasPathTo(search, vertice2)
    camino = None

    # Si existe camino, se encuentra. Este camino es el de menor arcos posible
    if hay_camino:
        camino = bfs.pathTo(search, vertice2)
    return hay_camino, camino

def requestAPI(ip):
    r = requests.get('http://ip-api.com/json/'+ip)
    info = r.json()
    return info["country"], info["lat"], info["lon"]

def get_vertice_cercano(catalog, country, lat, lon):
    lista_vertices_pais = mp.keySet(mp.get(catalog["countries"], country)["value"])
    menor = math.inf
    point_menor = None
    for vertice in lt.iterator(lista_vertices_pais):
        point = getLandingPoint(vertice)        
        mapa_info_point = me.getValue(mp.get(catalog["points"], point))
        latitud_point = me.getValue(mp.get(mapa_info_point, "latitude"))
        longitud_point = me.getValue(mp.get(mapa_info_point, "longitude"))
        distancia = CalcularPeso(latitud_point, longitud_point, lat, lon)
        if distancia < menor:
            menor = distancia   
            point_menor = point
    mapa_info_point = mp.get(catalog["points"], point_menor)["value"]
    mapa_vertices = mp.get(mapa_info_point, "mapa_vertices")["value"]
    vertice_menor = lt.firstElement(mp.keySet(mapa_vertices))
    return vertice_menor

"""
def ohCanada(catalog):
    lista_canada = mp.keySet(mp.get(catalog["countries"], "Canada")["value"])
    for vertice in lt.iterator(lista_canada):
        print("vertice: "+vertice)
        lp = getLandingPoint(vertice)
        ciudad = mp.get(mp.get(catalog["points"], lp)["value"], "city")["value"]
        print("ciudad: "+ciudad)"""
########################################### 7 #################################################



########################################### 8 #################################################
def mapaReq1(catalog):
    grafo = catalog["connections"]
    scc = catalog["components"]

    lista_colores = list(matplotlib.colors.cnames.values())
    m = folium.Map(location=[40, 20], tiles="Stamen Terrain", zoom_start=2)

    for vertice in lt.iterator(gr.vertices(grafo)):
        num_componente = mp.get(scc['idscc'], vertice)['value']
        color = lista_colores[num_componente*10]
        lat, lon = addVertexToMap(catalog, vertice, m, color)

        for adyacente in lt.iterator(gr.adjacents(grafo, vertice)):        
            lp1 = getLandingPoint(adyacente)
            lat1 = mp.get(mp.get(catalog["points"], lp1)["value"], "latitude")["value"]
            lon1 = mp.get(mp.get(catalog["points"], lp1)["value"], "longitude")["value"]
            folium.PolyLine(locations=[[lat, lon], [lat1, lon1]], 
                            color = lista_colores[num_componente*10],
                            ).add_to(m)
    
    vertice1 = mp.get(mp.get(catalog["mapas"], 1)["value"], "vertice1")["value"]
    addMarker(catalog, vertice1, m)
    vertice2 = mp.get(mp.get(catalog["mapas"], 1)["value"], "vertice2")["value"]
    addMarker(catalog, vertice2, m)

    print("\nCarga de Mapa 1 completada")
    m.save("mapaReq1.html")
    print("Se ha guardado el Mapa 1")


def mapaReq21(catalog):
    lista_mayores = mp.get(catalog["mapas"], 2)["value"]

    lista_colores = list(matplotlib.colors.cnames.values())
    color = lista_colores[-2]
    m = folium.Map(location=[40, 20], tiles="Stamen Terrain", zoom_start=2)

    for mapa_lp in lt.iterator(lista_mayores):
        lp = mp.get(mapa_lp, "id")["value"]
        ciudad = mp.get(mapa_lp, "ciudad")["value"]
        lista_adyacentes = mp.get(mapa_lp, "lista_adyacentes")["value"]

        addMarker(catalog, lp, m)
        lat1, lon1 = addVertexToMap(catalog, lp, m, color)
        for adyacente in lt.iterator(lista_adyacentes):
            cable = getCable(adyacente)
            lat2, lon2 = addVertexToMap(catalog, adyacente, m, color)
            folium.PolyLine(locations=[[lat1, lon1], [lat2, lon2]], 
                color = color,
                popup = cable
                ).add_to(m)

    print("\nCarga de Mapa 2 completada")
    m.save("mapaReq2.html")
    print("Se ha guardado el Mapa 2")



def mapaReq2(catalog):
    lista_mayores = mp.get(catalog["mapas"], 2)["value"]

    lista_colores = list(matplotlib.colors.cnames.values())
    color = lista_colores[-2]
    m = folium.Map(location=[40, 20], tiles="Stamen Terrain", zoom_start=2)

    for mapa_lp in lt.iterator(lista_mayores):
        lp = mp.get(mapa_lp, "id")["value"]
        mapa_vertices = mp.get(mapa_lp, "mapa_vertices")["value"]
        lista_vertices = mp.keySet(mapa_vertices)
        addMarker(catalog, lp, m)
        lat1, lon1 = addVertexToMap(catalog, lp, m, color)
        for vertice in lt.iterator(lista_vertices):
            lista_adyacentes = gr.adjacents(catalog["connections"], vertice)
            for adyacente in lt.iterator(lista_adyacentes):
                cable = getCable(adyacente)
                lat2, lon2 = addVertexToMap(catalog, adyacente, m, color)
                folium.PolyLine(locations=[[lat1, lon1], [lat2, lon2]], 
                    color = color,
                    popup = cable
                    ).add_to(m)

    print("\nCarga de Mapa 2 completada")
    m.save("mapaReq2.html")
    print("Se ha guardado el Mapa 2")

def mapaReq3(catalog):
    hay_camino = mp.get(mp.get(catalog["mapas"], 3)["value"], "hay_camino")["value"]
    if hay_camino:
        lista_camino = mp.get(mp.get(catalog["mapas"], 3)["value"], "lista_camino")["value"]
        vert_cap1 = mp.get(mp.get(catalog["mapas"], 3)["value"], "vertice_capital1")["value"]
        vert_cap2 = mp.get(mp.get(catalog["mapas"], 3)["value"], "vertice_capital2")["value"]
        
        m = folium.Map(location=[40, 20], tiles="Stamen Terrain", zoom_start=2)
        lista_colores = list(matplotlib.colors.cnames.values())
        color = lista_colores[75]

        addMarker(catalog, vert_cap1, m)
        addMarker(catalog, vert_cap2, m)
        for mapa_recorrido in lt.iterator(lista_camino):
            vertice1 = mp.get(mapa_recorrido, "vertice1")["value"]
            vertice2 = mp.get(mapa_recorrido, "vertice2")["value"]
            distancia = mp.get(mapa_recorrido, "peso")["value"]
            lat1, lon1 = addVertexToMap(catalog, vertice1, m, color)    
            lat2, lon2 = addVertexToMap(catalog, vertice2, m, color)
            folium.PolyLine(locations=[[lat1, lon1], [lat2, lon2]], 
                color = color,
                popup = round(distancia,1)
                ).add_to(m)
        
        print("\nCarga de Mapa 3 completada")
        m.save("mapaReq3.html")
        print("Se ha guardado el Mapa 3")  

    else:
        print("No es posible graficar dicho camino puesto que no existe :c")


def mapaReq4(catalog):
    mst = mp.get(mp.get(catalog["mapas"], 4)["value"],"mst")["value"]

    scc = catalog["components"]
    lista_colores = list(matplotlib.colors.cnames.values())
    m = folium.Map(location=[40, 20], tiles="Stamen Terrain", zoom_start=2)

    for arco in lt.iterator(mst):
        vertice1 = arco["vertexA"]
        vertice2 = arco["vertexB"]
        distancia = arco["weight"]
        num_componente = mp.get(scc['idscc'], vertice1)['value']
        color = lista_colores[num_componente*10]
        lat1, lon1 = addVertexToMap(catalog, vertice1, m, color)
        lat2, lon2 = addVertexToMap(catalog, vertice2, m, color)
        folium.PolyLine(locations=[[lat1, lon1], [lat2, lon2]], 
                color = color,
                popup = round(distancia,1)
                ).add_to(m)

    arco_menor = mp.get(mp.get(catalog["mapas"], 4)["value"],"arco_menor")["value"]
    addArco(catalog, arco_menor, m, "#ff0000", 4)
    arco_mayor = mp.get(mp.get(catalog["mapas"], 4)["value"],"arco_mayor")["value"]
    addArco(catalog, arco_mayor, m, "#008f39", 1)

    print("\nCarga de Mapa 4 completada")
    m.save("mapaReq4.html")
    print("Se ha guardado el Mapa 4")


def mapaReq5(catalog):
    lista_arcos = mp.get(catalog["mapas"], 5)["value"]
    negro = "#000000"
    rojo = "#ff0000"
    m = folium.Map(location=[40, 20], tiles="Stamen Terrain", zoom_start=2)

    for arco in lt.iterator(lista_arcos):
        vertice1 = arco["vertexA"]
        vertice2 = arco["vertexB"]
        distancia = arco["weight"]
        lat1, lon1 = addVertexToMap(catalog, vertice1, m, negro)
        lat2, lon2 = addVertexToMap(catalog, vertice2, m, rojo)
        pais2 = mp.get(mp.get(catalog["points"], getLandingPoint(vertice2))["value"], "country")["value"]
        addMarker(catalog, vertice2, m, con_pais=True)
        folium.PolyLine(locations=[[lat1, lon1], [lat2, lon2]], 
                color = rojo,
                popup = round(distancia,1)
                ).add_to(m)

    print("\nCarga de Mapa 5 completada")
    m.save("mapaReq5.html")
    print("Se ha guardado el Mapa 5")



def addVertexToMap(catalog, vertice, m, color):
    lp = getLandingPoint(vertice)
    mapa_info_point = mp.get(catalog["points"], lp)["value"]
    lat = mp.get(mapa_info_point, "latitude")["value"]
    lon = mp.get(mp.get(catalog["points"], lp)["value"], "longitude")["value"]
    folium.Circle(radius = 10000,
                location=[lat, lon],
                color = color,
                fill = True
                ).add_to(m)
    return lat, lon

def addMarker(catalog, vertice, m, con_pais = False):
    tooltip = "Cliquéame"
    mapa_info_point = mp.get(catalog["points"], getLandingPoint(vertice))["value"]
    city = mp.get(mapa_info_point, "city")["value"] 
    pais = mp.get(mapa_info_point, "country")["value"]
    lat = mp.get(mapa_info_point, "latitude")["value"]
    lon = mp.get(mapa_info_point, "longitude")["value"]
    if con_pais:
        folium.Marker([lat, lon], popup="<i>"+city+", "+pais+"</i>", tooltip=tooltip
                ).add_to(m)
    else:
        folium.Marker([lat, lon], popup="<i>"+city+"</i>", tooltip=tooltip
            ).add_to(m)


def addArco(catalog, arco, m, color, decimales=1):
    v1 = arco["vertexA"]
    v2 = arco["vertexB"]
    dist = round(arco["weight"], decimales) 
    addMarker(catalog, v1, m)
    addMarker(catalog, v2, m)
    lat1, lon1 = addVertexToMap(catalog, v1, m, color)
    lat2, lon2 = addVertexToMap(catalog, v2, m, color)
    folium.PolyLine(locations=[[lat1, lon1], [lat2, lon2]], 
        color = color,
        popup = dist
        ).add_to(m)
########################################### 8 #################################################