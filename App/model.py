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
                "cables":None}

    catalog["conexiones"] = gr.newGraph(datastructure='ADJ_LIST',
                                            directed=False,
                                            size=4000
                                            )

    catalog["points"] = mp.newMap(numelements=1500, maptype="PROBING", loadfactor=0.4)
    catalog["ciudades"] = mp.newMap(numelements=1500, maptype="PROBING", loadfactor=0.4)

    catalog["countries"] = mp.newMap(numelements=300, maptype="PROBING", loadfactor=0.4)

    catalog["cables"] = mp.newMap(numelements=200, maptype="PROBING", loadfactor=0.4)

    return catalog


def addPoint(catalog, point):
    
    lista_ubicacion = lt.newList(datastructure="ARRAY_LIST")
    ciudad = point["location"][0]
    pais = point["location"][-1]
    mapa_vertices = mp.newMap(numelements=200, maptype="PROBING", loadfactor=0.4)
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

    vertice_salida = conexion["origin"]+"-"+conexion["cable_id"]
    vertice_llegada = conexion["destination"]+"-"+conexion["cable_id"]

    #Añade el vertice a la lista de vertices del mapa de points
    lista_pais_lati_long_listavertices = me.getValue(mp.get(catalog["points"], point_salida))
    mapa_vertices = lt.firstElement((lista_pais_lati_long_listavertices))
    mp.put(mapa_vertices, vertice_salida, None)

    lista_pais_lati_long_listavertices1 = me.getValue(mp.get(catalog["points"], point_llegada))
    mapa_vertices1 = lt.firstElement((lista_pais_lati_long_listavertices1))
    mp.put(mapa_vertices1, vertice_llegada, None)

    #Añade el vertice al mapa de cables
    exist_cable = mp.contains(catalog["cables"], conexion["cable_id"])
    
    if exist_cable:
        mapa_vertices2 = me.getValue(mp.get(catalog["cables"], conexion["cable_id"]))
        mp.put(mapa_vertices2, vertice_llegada, None)
        mp.put(mapa_vertices2, vertice_salida, None)
    
    else:
        nuevo_mapa = mp.newMap(numelements=100, maptype="PROBING", loadfactor=0.4)
        mp.put(nuevo_mapa, vertice_llegada, None)
        mp.put(nuevo_mapa, vertice_salida, None)
        mp.put(catalog["cables"], conexion["cable_id"], nuevo_mapa)

    gr.insertVertex(catalog["conexiones"], vertice_salida)
    gr.insertVertex(catalog["conexiones"], vertice_llegada)

    latitud1 = lt.getElement((me.getValue(mp.get(catalog["points"], conexion["origin"]))),-1)
    longitud1 = lt.lastElement(me.getValue(mp.get(catalog["points"], conexion["origin"])))

    latitud2 = lt.getElement((me.getValue(mp.get(catalog["points"], conexion["destination"]))),-1)
    longitud2 = lt.lastElement(me.getValue(mp.get(catalog["points"], conexion["destination"])))

    distancia = CalcularPeso(latitud1, longitud1, latitud2, longitud2)

    gr.addEdge(catalog["conexiones"], vertice_salida, vertice_llegada, weight=distancia)

def addCountry(catalog, country):

    mp.put(catalog["countries"], country["country"], country["capital"])

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



#Nota: getElement(lista, 0) es igual a lastElement
#getElement(lista, -1) es como [-2], obtiene la penúltima pos

#Revisar las repeticiones en los mapas