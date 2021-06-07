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
 """

import config as cf
import model
import csv
import tracemalloc
import time

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""
# ======================================
# Función para inicializar el catálogo
# ======================================

def initCatalog():
    """
    Llama la función de inicialización  del modelo.
    """
    # catalog es utilizado para interactuar con el modelo
    catalog = model.newCatalog()
    return catalog


# =================================
# Funciones para la carga de datos
# =================================

def loadData(catalog):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()

    primer_point = loadPoints(catalog)
    loadConexiones(catalog)
    ConectarPointsIguales(catalog)
    ultimo_country = loadCountries(catalog)

    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)
    return delta_time, delta_memory, primer_point, ultimo_country

def loadPoints(catalog):
    """
    Carga los Landing Points del archivo. Por cada Landing Point se toma los datos
    necesarios: el id del Landing Point, la ubicación (ciudad y país), la latitud
    y la longitud.
    """
    videosfile = cf.data_dir + 'landing_points.csv'
    
    input_file = csv.DictReader(open(videosfile, encoding='utf-8'))
    i = 1
    for point in input_file:
        cada_point = {"landing_point_id": point["landing_point_id"],
                    "location": point["name"].split(","),
                    "latitude": float(point["latitude"]),
                    "longitude": float(point["longitude"]),       
                    }       
        if i == 1:
            primer_point = cada_point  
            model.addPoint(catalog, cada_point)
        else:
            model.addPoint(catalog, cada_point)
        i += 1
    return primer_point

def loadConexiones(catalog):
    """
    Carga cada conexión del archivo. Por cada conexión se toma los datos necesarios:
    origen, destino, cable_name y capacidad.
    """
    videosfile = cf.data_dir + 'connections.csv'
    
    input_file = csv.DictReader(open(videosfile, encoding='utf-8-sig'))
    i = 1
    for conexion in input_file:
        if i%2 != 0:
            cada_conexion = {"origin": conexion["origin"],
                        "destination": conexion["destination"],
                        "cable_name": conexion["cable_name"],
                        "capacityTBPS": float(conexion["capacityTBPS"])
                        }       
        i += 1
        model.addConexion(catalog, cada_conexion)

def loadCountries(catalog):
    """
    Carga los países del archivo. Por cada país se toma los datos necesarios:
    nombre del país, nombre de la capital, latitud de la capital y longitud de la capital
    """
    videosfile = cf.data_dir + 'countries.csv'
    input_file = csv.DictReader(open(videosfile, encoding='utf-8'))

    rows = list(input_file)
    size = len(rows)
    for i, country in enumerate(rows):
        cada_country = {"country": country["CountryName"],
                    "capital": country["CapitalName"].replace("-"," "),
                    "latitude": float(country["CapitalLatitude"]),
                    "longitude": float(country["CapitalLongitude"]),
                    "population": country["Population"],
                    "users": country["Internet users"]
                    }      
        if i == size-1:
            ultimo_country = cada_country
            model.addCountry(catalog, cada_country)
        else:
            model.addCountry(catalog, cada_country)

    return ultimo_country

# =====================
# Funciones auxiliares
# =====================

def ConectarPointsIguales(catalog):
    model.ConectarPointsIguales(catalog)

def ConectarCablesIguales(catalog):
    model.ConectarCablesIguales(catalog)

def TotalVertices(catalog):
    return model.TotalVertices(catalog)

def TotalEdges(catalog):
    return model.TotalEdges(catalog)

def TotalCountries(catalog):
    return model.TotalCountries(catalog)

def getPrimerVertice(catalog, landing_point):
    return model.getPrimerVertice(catalog, landing_point)

def getPointID(catalog, landing_point):
    return model.getPointID(catalog, landing_point)


# ===============
# Requerimientos
# ===============

def requerimiento1(catalog, vert1, vert2):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()

    numero_clusteres = model.connectedComponents(catalog)
    mismo_cluster = model.sameCluster(catalog, vert1, vert2)

    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)

    return delta_time, delta_memory, numero_clusteres, mismo_cluster 

def requerimiento2(catalog):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()

    puntos_interconexion = model.puntos_interconexion(catalog)

    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)  
    return delta_time, delta_memory, puntos_interconexion

def requerimiento3(catalog, pais1, pais2):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()

    ruta_min = model.rutaMinimaCountries(catalog, pais1, pais2)

    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)  
    return delta_time, delta_memory, ruta_min

def requerimiento4(catalog):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()

    respuesta = model.minExpansion(catalog)

    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)  
    return  delta_time, delta_memory, respuesta

def requerimiento5(catalog, point):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()

    lista_paises = model.affectedCountries(catalog, point)

    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)  
    return delta_time, delta_memory, lista_paises

def requerimiento6 (catalog, pais_solicitado, cable_solicitado):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()      

    esta_pais_solicitado, mapa_paises = model.getPaisesAnchoMax(catalog, pais_solicitado, cable_solicitado)
        
    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)  
    return delta_time, delta_memory, esta_pais_solicitado, mapa_paises

def requerimiento7(catalog, ip1, ip2):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()   

    hay_camino, camino = model.rutaMinimaIP(catalog, ip1, ip2)
    
    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)  
    return delta_time, delta_memory, hay_camino, camino

def requerimiento8(catalog):
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()   

    model.mapaReq1(catalog)
    model.mapaReq2(catalog)
    model.mapaReq3(catalog)
    model.mapaReq4(catalog)
    model.mapaReq5(catalog)

    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)  
    return delta_time, delta_memory

# ======================================
# Funciones para medir tiempo y memoria
# ======================================

def getTime():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)

def getMemory():
    """
    toma una muestra de la memoria alocada en instante de tiempo
    """
    return tracemalloc.take_snapshot()

def deltaMemory(start_memory, stop_memory):
    """
    calcula la diferencia en memoria alocada del programa entre dos
    instantes de tiempo y devuelve el resultado en bytes (ej.: 2100.0 B)
    """
    memory_diff = stop_memory.compare_to(start_memory, "filename")
    delta_memory = 0.0

    # suma de las diferencias en uso de memoria
    for stat in memory_diff:
        delta_memory = delta_memory + stat.size_diff
    # de Byte -> kByte
    delta_memory = delta_memory/1024.0
    return delta_memory
def BogBquilla():
    return model.BogBquilla()