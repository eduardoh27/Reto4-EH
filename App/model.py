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
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
assert cf
import haversine as hs
from DISClib.ADT import minpq as pq
"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

def newCatalog():
    """ Inicializa el catálogo

    Crea un diccionario cuyos valores serán las estructuras de datos.
    Se crea un Ordered Map para cada característica de contenido utilizada.
    Además, se crea un Map para las pistas y otro Map los hashtags.

    Retorna el catálogo inicializado.
    """
    catalog = {"conexiones":None,
                "points":None,
                "ciudades":None,
                "countries":None,
                "cables":None,
                "ancho":None,
                "anchos_landing":None}

    catalog["conexiones"] = gr.newGraph(datastructure='ADJ_LIST',
                                            directed=False,
                                            size=4000
                                            )

    catalog["points"] = mp.newMap(numelements=100, maptype="PROBING", loadfactor=0.4)
    catalog["ciudades"] = mp.newMap(numelements=1500, maptype="PROBING", loadfactor=0.4)

    catalog["countries_capitales"] = mp.newMap(numelements=300, maptype="PROBING", loadfactor=0.4)

    catalog["cables"] = mp.newMap(numelements=200, maptype="PROBING", loadfactor=0.4)
    catalog["ancho"] = mp.newMap(numelements=2000, maptype="PROBING", loadfactor=0.4)
    catalog["anchos_landing"] = mp.newMap(numelements=2000, maptype="PROBING", loadfactor=0.4)

    catalog["countries"] = mp.newMap(numelements=300, maptype="PROBING", loadfactor=0.4)


    return catalog


def addPoint(catalog, point):
    
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





def addConexion(catalog, conexion):

    point_salida = conexion["origin"]
    point_llegada = conexion["destination"]

    vertice_salida = conexion["origin"]+"-"+conexion["cable_name"]
    vertice_llegada = conexion["destination"]+"-"+conexion["cable_name"]

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

def addCountry(catalog, country):

    vertice_capital = country["capital"]+"-CAPITAL"
    mp.put(catalog["countries_capitales"], country["country"], country["capital"])
    gr.insertVertex(catalog["conexiones"], vertice_capital)
    ConectarConCapital(catalog, vertice_capital, country["country"], country["latitude"], country["longitude"])

def CalcularPeso(latitud1, longitud1, latitud2, longitud2):

    loc1=(latitud1, longitud1)
    loc2=(latitud2, longitud2)

    return hs.haversine(loc1,loc2)

def ConectarPointsIguales(catalog):

    for point in lt.iterator(mp.keySet(catalog["points"])):
        #Se obtiene la lista de [lista_vertices, pais, latitud, long]
        valor_point = me.getValue(mp.get(catalog["points"], point))
        mapa_vertices = lt.firstElement(valor_point)
        lista_vertices = mp.keySet(mapa_vertices)
        tamaño = lt.size(lista_vertices)
        i = 1
        while i < tamaño:
            vertice = lt.getElement(lista_vertices, i)
            j = i+1
            while j <= tamaño:
                vertice1 = lt.getElement(lista_vertices, j)
                gr.addEdge(catalog["conexiones"], vertice, vertice1, weight=0.1)
                cola = me.getValue(mp.get(catalog["anchos_landing"], point))
                ancho = pq.min(cola)
                llave_ancho= vertice+"/"+vertice1
                llave_ancho1=vertice1+"/"+vertice
                mp.put(catalog["ancho"],llave_ancho,ancho)
                mp.put(catalog["ancho"],llave_ancho1,ancho)
                j += 1
            i += 1
    

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

def cmpfunction_minPQ (p1, p2):
    return p1 > p2


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
"""