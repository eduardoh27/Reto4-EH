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
from DISClib.ADT import graph as gr
from DISClib.Utils import error as error
from DISClib.DataStructures import mapentry as me
from DISClib.DataStructures import edge as e
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import prim 
import math
assert cf
import haversine as hs
from DISClib.ADT import minpq as pq
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
                "paths": None}

    catalog["connections"] = gr.newGraph(datastructure='ADJ_LIST',
                                            directed=False,
                                            size=1733
                                            )

    catalog["points"] = mp.newMap(numelements=1283, maptype="PROBING", loadfactor=0.4)
    # Las llaves son cada Landing Point y los valores son mapas con la información necesario de cada LD
    # {"1020(id de Bogotá)":{"country": Colombia,
    #                       "city": Bogotá, 
    #                       "Long": 1.01, 
    #                       "Lat": -2.95,
    #                       "mapa_vertices": {"Bog-2africa": None, "Bog-ALBA1": None, ...}}},
    # "2929":...}

    catalog["ciudades"] = mp.newMap(numelements=1283, maptype="PROBING", loadfactor=0.4)
    # Identifica a una ciudad ("Bogotá") con su landing_point_id (1020)
    # {"Bogotá": 1020, "Londres": 2929, ...}

    catalog["countries_capitales"] = mp.newMap(numelements=300, maptype="PROBING", loadfactor=0.4)
    # Identifica un país con su CapitalLatitude
    # {"Colombia": "Bogotá", "Canadá": Ottawa, ...}    

    # Identifica un cable con los vértices de ese cable
    catalog["cables"] = mp.newMap(numelements=200, maptype="PROBING", loadfactor=0.4)
    # {"2africa": {"1020-2africa": None, "2929-2africa": None, ...}, 
    #   "east-west": {"2783-east-west": None, "1020-east-west": None, ...},
    #  ...}

    # Grafo "duplicado" de connections, pero tiene como peso al ancho en esa conexión     
    catalog["connections_ancho"] = gr.newGraph(datastructure='ADJ_LIST',
                                                directed=False,
                                                size=1733
                                                )

    # Como llaves está el landing point y como valor una MinPQ con los anchos de este point
    catalog["anchos_landing"] = mp.newMap(numelements=2000, maptype="PROBING", loadfactor=0.4)
    # {"1020": [1, 2, 4, 10], "2929": [3, 4, 6], ...}

    # Como llaves está el país y como valor un mapa de vértices asociados a dicho país
    catalog["countries"] = mp.newMap(numelements=300, maptype="PROBING", loadfactor=0.4)
    # {"Colombia": {"2929-2africa": None, "1020-ALBA1": None, ...}, 
    #  "Canadá": {...},
    # ...}

    return catalog


def addPoint(catalog, point):
    
    # Se crea una mapa donde se guardarán los datos del Landing Point
    mapa_info_point = mp.newMap(numelements=5, maptype="PROBING", loadfactor=0.4)

    ciudad = point["location"][0]
    pais = point["location"][-1].lstrip()
    latitud = point["latitude"]
    longitud = point["longitude"]
    # Se crea un mapa donde se guardarán los múltiples vértices de un mismo Landing Point
    mapa_vertices = mp.newMap(numelements=13, maptype="PROBING", loadfactor=0.4)


    # Se añaden los datos al mapa de datos
    mp.put(mapa_info_point, "country", pais)
    mp.put(mapa_info_point, "city", ciudad)
    mp.put(mapa_info_point, "latitude", latitud)
    mp.put(mapa_info_point, "longitude", longitud)
    mp.put(mapa_info_point, "mapa_vertices", mapa_vertices)

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

    mapa_info_point1 = me.getValue(mp.get(catalog["points"], point_salida))
    latitud1 = me.getValue(mp.get(mapa_info_point1, "latitude"))
    longitud1 = me.getValue(mp.get(mapa_info_point1, "longitude"))
    mapa_info_point2 = me.getValue(mp.get(catalog["points"], point_llegada))
    latitud2 = me.getValue(mp.get(mapa_info_point2, "latitude"))
    longitud2 = me.getValue(mp.get(mapa_info_point2, "longitude"))
    distancia = CalcularPeso(latitud1, longitud1, latitud2, longitud2)
    #2. Se añade la conexión al grafo normal (de distancia)
    addDistance(catalog, vertice_salida, vertice_llegada, distancia)

    #3. Se añaden a la MinPQ asociada a cada Landing_Point
    addAnchoQueue(catalog, point_salida, ancho)
    addAnchoQueue(catalog, point_llegada, ancho)

    #4. Añade el vertice a la lista de vertices del mapa de points
    mapa_vertices1 = me.getValue(mp.get(mapa_info_point1, "mapa_vertices"))
    mp.put(mapa_vertices1, vertice_salida, None)
    mapa_vertices2 = me.getValue(mp.get(mapa_info_point2, "mapa_vertices"))
    mp.put(mapa_vertices2, vertice_llegada, None)

    #5. Añade los vértices al mapa de vértices para un cable dado dentro del mapa de cables  
    addCable(catalog, conexion["cable_name"], vertice_salida, vertice_llegada)

    #6. Añade los vértices al mapa de vértices dado un país
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
        cola = pq.newMinPQ(cmpfunction_minPQ)
        pq.insert(cola, ancho)
        mp.put(catalog["anchos_landing"], point, cola)

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
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(catalog[graph], origin, destination)
    if edge is None:
        gr.addEdge(catalog[graph], origin, destination, weight)
        #gr.addEdge(catalog[graph], destination, origin, weight)
    return catalog

def CalcularPeso(latitud1, longitud1, latitud2, longitud2):

    loc1=(latitud1, longitud1)
    loc2=(latitud2, longitud2)

    return hs.haversine(loc1,loc2)




def addCountry(catalog, country):

    nombre_capital = country["capital"]
    # Se añade la pareja {country: capital} al mapa de países
    mp.put(catalog["countries_capitales"], country["country"], country["capital"])

    # Se conectan las ciudades del pais con la capital
    ConectarConCapital(catalog, nombre_capital, country["country"], country["latitude"], country["longitude"])


def ConectarConCapital(catalog, vertice_capital, pais, latitud_capital, longitud_capital):
    """
    El vertice capital es el nombre de la capital. Ej: "Bogotá" 
    UPDATE: SI el vértice de capital ya está como número Ej: 1923, ese se deja
    como el vértice_capital. Si no está, se usa el nombre de la capital Ej: Bogotá
    UPDATE: SE CONECTA A LA CAPITAL CON LOS VERTICES DEL PAIS EN AMBOS GRAFOS
    se podrían añadir los nuevos vertices a las otras estructuras. En específico a
    catalog["points"], catalog["ciudades"], catalog["countries"] quizá tmb a catalog["anchos_landing"]
    """

    existe_pais = mp.get(catalog["countries"], pais)

    if existe_pais == None:
        menor = math.inf
        point_menor = None
        for point in lt.iterator(mp.keySet(catalog["points"])):
            mapa_info_point = me.getValue(mp.get(catalog["points"], point))
            latitud_point = me.getValue(mp.get(mapa_info_point, "latitude"))
            longitud_point = me.getValue(mp.get(mapa_info_point, "longitude"))
            distancia = CalcularPeso(latitud_point, longitud_point, latitud_capital, longitud_capital)
            if distancia < menor:
                menor = distancia   
                point_menor = point
        lista_vertices = mp.keySet(me.getValue(mp.get(me.getValue(mp.get(catalog["points"], point_menor)), "mapa_vertices")))
    else:
        #if mp.contains(catalog["ciudades"], vertice_capital):
        #    vertice_capital = mp.get(catalog["ciudades"], vertice_capital)["value"]
        lista_vertices = mp.keySet(me.getValue(existe_pais))

    for vertice in lt.iterator(lista_vertices):
        point = getLandingPoint(vertice)
        mapa_info_point = me.getValue(mp.get(catalog["points"], point))
        ancho = pq.min(me.getValue(mp.get(catalog["anchos_landing"], point)))
        # conecta dos vertices por ancho
        addAncho(catalog, vertice, vertice_capital, ancho)


def getLandingPoint(vertice):

    if "-" in vertice:
        indice = vertice.index("-")
        vertice = vertice[:indice]

    return vertice
    

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
            addDistance(catalog, point, vertice, 0)
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



############################
# Funciones de comparación #
############################

def cmpfunction_minPQ (p1, p2):
    return p1 > p2

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
    catalog["components"] = scc.KosarajuSCC(catalog["connections"])
    return scc.connectedComponents(catalog["components"])

def sameComponent(catalog, vert1, vert2):
    return scc.stronglyConnected(catalog["components"], vert1, vert2)
########################################### 1 #################################################





########################################### 4 #################################################
def minExpansion(catalog):
    # numelements debería ser la mitad???
    # Se crea un mapa {"#componente": {v1: None, v2:None, ...}, ...}
    mapa_componentes = mp.newMap(numelements=113, maptype="PROBING", loadfactor=0.4)

    for vertice in lt.iterator(mp.keySet(catalog["components"]["idscc"])):
        numero_componente = mp.get(catalog["components"]["idscc"], vertice)["value"]
        addComponente(mapa_componentes, numero_componente, vertice)

    mayor = None
    conteo_mayor = 0
    for componente in lt.iterator(mp.keySet(mapa_componentes)):
        mapa_vertices = mp.get(mapa_componentes, componente)["value"]
        numero_vertices = mp.size(mapa_vertices)
        #print(componente, numero_vertices)
        if numero_vertices > conteo_mayor:
        #if numero_vertices == 10:
            mayor = componente
            conteo_mayor = numero_vertices
    #mayor = 106, conteo_mayor=1983
    #print(type(mayor))

    lista_vertices_mayor = mp.keySet(mp.get(mapa_componentes, mayor)["value"])
    #verts_mayor = mp.keySet(mp.get(mapa_componentes, 82)["value"])
    tamaño = lt.size(lista_vertices_mayor)
    tamaño, subgrafo = crearSubGrafo(catalog, lista_vertices_mayor, tamaño)
    
    search = prim.PrimMST(subgrafo)
    #print(search)
    
    peso = prim.weightMST(subgrafo, search)
    #print("peso",peso)

    mayor = buscarMayor(search)
    #print("mayor",mayor)

    menor = buscarMenor(search)
    #print("menor",menor)

    return tamaño, peso, mayor, menor

def addComponente(mapa_componentes, componente, vertice):
    exist_componente = mp.contains(mapa_componentes, componente)
    if exist_componente:
        mapa_vertices = me.getValue(mp.get(mapa_componentes, componente))
        mp.put(mapa_vertices, vertice, None)
    else:
        nuevo_mapa = mp.newMap(numelements=31, maptype="PROBING", loadfactor=0.4)
        mp.put(nuevo_mapa, vertice, None)
        mp.put(mapa_componentes, componente, nuevo_mapa)

def crearSubGrafo(catalog, lista_vertices, tamaño):
    # Con los vértices del SCC más grande, se crea un subgrafo, obteniendo las 
    # conexiones del grafo original
    catalog_sub = {"connections": None}
    catalog_sub["connections"] = gr.newGraph(size=2017)

    i = 1
    while i < tamaño:
        vertice = lt.getElement(lista_vertices, i)
        lista_arcos_adyacentes = gr.adjacentEdges(catalog["connections"], vertice)
        for arco in lt.iterator(lista_arcos_adyacentes):
            #print(arco)
            vertice1 = arco["vertexA"]
            vertice2 = arco["vertexB"]
            distancia = arco["weight"] 
            addDistance(catalog_sub, vertice1, vertice2, distancia)    
        i+=1
    subgrafo = catalog_sub["connections"]
    return tamaño, subgrafo

def buscarMenor(search):
    buscar = math.inf
    edges = search["mst"]
    #dicc = {}
    for edge in lt.iterator(edges):
        peso = float(e.weight(edge))
        #dicc[peso] = None
        if peso != 1 and peso != 0 and peso < buscar:
            buscar = peso
    #print(dicc.keys())
    return buscar

def buscarMayor(search):
    buscar = 0
    edges = search["mst"]
    for edge in lt.iterator(edges):
        peso = e.weight(edge)
        if peso > buscar:
            buscar = peso
    return buscar
########################################### 4 #################################################


########################################### 5 #################################################
def affectedCountries(catalog, point):
    # Mapa para que no se repitan los países que se guardan
    mapa_paises = mp.newMap(numelements=13, maptype="PROBING", loadfactor=0.4)

    lista_vertices_point = mp.keySet(mp.get(mp.get(catalog["points"], point)["value"], "mapa_vertices")["value"])

    for vertice_point in lt.iterator(lista_vertices_point):
        vertices_adyacentes = gr.adjacents(catalog["connections"], vertice_point)
        for adyacente in lt.iterator(vertices_adyacentes):

            point_adyacente = getLandingPoint(adyacente)
            pais_adyacente = mp.get(mp.get(catalog["points"], point_adyacente)["value"], "country")["value"]
            mp.put(mapa_paises, pais_adyacente, None)

    tamaño = mp.size(mapa_paises)
    lista_paises = mp.keySet(mapa_paises)

    return tamaño, lista_paises
########################################### 5 #################################################




"""
BORRADOR:

def getLandingPoint(vertice):
    indice = vertice.index("-")
    return vertice[:indice]

def foo(catalog):   
    mapa_vertices = lt.firstElement(me.getValue(mp.get(catalog["points"], "3012")))
    print(mp.size(mapa_vertices))
    lista_vertices = mp.keySet(mapa_vertices)
    print(lt.size(lista_vertices))

def foo1():
    cola = pq.newMinPQ(cmpfunction_minPQ)
    pq.insert(cola, 12)
    pq.insert(cola, 3)
    pq.insert(cola, 324213)
    pq.insert(cola, 123)
    pq.insert(cola, 1)
    pq.insert(cola, 345)
    print(pq.min(cola))

#Nota: getElement(lista, 0) es igual a lastElement
#getElement(lista, -1) es como [-2], obtiene la penúltima pos

#Revisar las repeticiones en los mapas

#PROBAR CARGA 
#PROBAR MINPQ







def addConexion(catalog, conexion):

    point_salida = conexion["origin"]
    point_llegada = conexion["destination"]
    vertice_salida = point_salida + "-" + conexion["cable_name"]
    vertice_llegada = point_llegada + "-" + conexion["cable_name"]
    ancho = conexion["capacityTBPS"]
    llave_ancho= vertice_llegada+"/"+vertice_salida
    llave_ancho1=vertice_salida+"/"+vertice_llegada
    mp.put(catalog["ancho"],llave_ancho,ancho)
    mp.put(catalog["ancho"],llave_ancho1,ancho)

    if mp.contains(catalog["anchos_landing"],point_salida):
        cola = me.getValue(mp.get(catalog["anchos_landing"], point_salida))
        pq.insert(cola,ancho)
    else:
        cola = pq.newMinPQ(cmpfunction_minPQ)
        pq.insert(cola,ancho)
        mp.put(catalog["anchos_landing"],point_salida,cola)


    if mp.contains(catalog["anchos_landing"],point_llegada):
        cola = me.getValue(mp.get(catalog["anchos_landing"], point_llegada))
        pq.insert(cola,ancho)
    else:
        cola = pq.newMinPQ(cmpfunction_minPQ)
        pq.insert(cola,ancho)
        mp.put(catalog["anchos_landing"],point_llegada,cola)



    #Añade el vertice a la lista de vertices del mapa de points

    lista_pais_lati_long_listavertices = me.getValue(mp.get(catalog["points"], point_salida))
    mapa_vertices = lt.firstElement((lista_pais_lati_long_listavertices))
    mp.put(mapa_vertices, vertice_salida, None)

    lista_pais_lati_long_listavertices1 = me.getValue(mp.get(catalog["points"], point_llegada))
    mapa_vertices1 = lt.firstElement((lista_pais_lati_long_listavertices1))
    mp.put(mapa_vertices1, vertice_llegada, None)


    #Añade el vertice al mapa de cables
    exist_cable = mp.contains(catalog["cables"], conexion["cable_name"])
    
    if exist_cable:
        mapa_vertices2 = me.getValue(mp.get(catalog["cables"], conexion["cable_name"]))
        mp.put(mapa_vertices2, vertice_llegada, None)
        mp.put(mapa_vertices2, vertice_salida, None)
    
    else:
        nuevo_mapa = mp.newMap(numelements=100, maptype="PROBING", loadfactor=0.4)
        mp.put(nuevo_mapa, vertice_llegada, None)
        mp.put(nuevo_mapa, vertice_salida, None)
        mp.put(catalog["cables"], conexion["cable_name"], nuevo_mapa)

    gr.insertVertex(catalog["conexiones"], vertice_salida)
    gr.insertVertex(catalog["conexiones"], vertice_llegada)

    latitud1 = lt.getElement((me.getValue(mp.get(catalog["points"], conexion["origin"]))),-1)
    longitud1 = lt.lastElement(me.getValue(mp.get(catalog["points"], conexion["origin"])))

    latitud2 = lt.getElement((me.getValue(mp.get(catalog["points"], conexion["destination"]))),-1)
    longitud2 = lt.lastElement(me.getValue(mp.get(catalog["points"], conexion["destination"])))

    distancia = CalcularPeso(latitud1, longitud1, latitud2, longitud2)

    gr.addEdge(catalog["conexiones"], vertice_salida, vertice_llegada, weight=distancia)





def ConectarConCapital(catalog, vertice_capital, pais, latitud_capital, longitud_capital):
    existe_pais = mp.get(catalog["countries"], pais)

    if existe_pais == None:
        menor = 10000000
        point_menor = None
        for point in lt.iterator(mp.keySet(catalog["points"])):
            latitud_point = lt.getElement((me.getValue(mp.get(catalog["points"], point))),-1)
            longitud_point = lt.lastElement(me.getValue(mp.get(catalog["points"], point)))
            distancia = CalcularPeso(latitud_point, longitud_point, latitud_capital, longitud_capital)
            if distancia < menor:
                menor = distancia   
                point_menor = point

        cola = me.getValue(mp.get(catalog["anchos_landing"], point_menor))
        ancho = pq.min(cola)

        mapa_vertices = lt.firstElement(me.getValue(mp.get(catalog["points"], point_menor))) 
        for vertice in lt.iterator(mp.keySet(mapa_vertices)):
            gr.addEdge(catalog["conexiones"], vertice, vertice_capital, weight=distancia)
            llave_ancho= vertice+"/"+vertice_capital
            llave_ancho1=vertice_capital+"/"+vertice
            mp.put(catalog["ancho"],llave_ancho,ancho)
            mp.put(catalog["ancho"],llave_ancho1,ancho)


    else:
        lista_points = me.getValue(mp.get(catalog["countries"], pais))

        for point in lt.iterator(lista_points):
            mapa_vertices = lt.firstElement(me.getValue(mp.get(catalog["points"], point_salida)))
            latitud_point = lt.getElement((me.getValue(mp.get(catalog["points"], point))),-1)
            longitud_point = lt.lastElement(me.getValue(mp.get(catalog["points"], point)))
            distancia = CalcularPeso(latitud_point, longitud_point, latitud_capital, longitud_capital)
            cola = me.getValue(mp.get(catalog["anchos_landing"], point))
            ancho = pq.min(cola)


            for vertice in lt.iterator(mp.keySet(mapa_vertices)):
                gr.addEdge(catalog["conexiones"], vertice, vertice_capital, weight=distancia)
                llave_ancho= vertice+"/"+vertice_capital
                llave_ancho1=vertice_capital+"/"+vertice
                mp.put(catalog["ancho"],llave_ancho,ancho)
                mp.put(catalog["ancho"],llave_ancho1,ancho)



def addPoint(catalog, point):
    
    #Se crea una lista donde se guardarán los datos de Landing Point
    lista_ubicacion = lt.newList(datastructure="ARRAY_LIST")
    ciudad = point["location"][0]
    pais = point["location"][-1]
    mapa_vertices = mp.newMap(numelements=2, maptype="PROBING", loadfactor=0.4)
    lt.addLast(lista_ubicacion, mapa_vertices)
    lt.addLast(lista_ubicacion, pais)
    lt.addLast(lista_ubicacion, point["latitude"])
    lt.addLast(lista_ubicacion, point["longitude"])
    #[mapa_vertices, pais, latitud, longitud]

    #Se agrega a un mapa
    mp.put(catalog["points"], point["landing_point_id"], lista_ubicacion)
    
    #Se agrega a otro mapa otra info
    mp.put(catalog["ciudades"], ciudad, point["landing_point_id"])






#NO SE USA
def ConectarCablesIguales(catalog):

    for cable in lt.iterator(mp.keySet(catalog["cables"])):
        #Se obtiene el mapa de vertices de la llave "cable"
        mapa_vertices = me.getValue(mp.get(catalog["cables"], cable))
        lista_vertices = mp.keySet(mapa_vertices)
        tamaño = lt.size(lista_vertices)
        i = 1
        while i < tamaño:
            vertice = lt.getElement(lista_vertices, i)
            j = i+1
            while j <= tamaño:
                vertice1 = lt.getElement(lista_vertices, j)
                gr.addEdge(catalog["conexiones"], vertice, vertice1, weight=0.1)
                j += 1
            i += 1
"""