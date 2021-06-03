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


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""
# Inicialización del Catálogo de libros

def initCatalog():
    """
    Llama la función de inicialización  del modelo.
    """
    # catalog es utilizado para interactuar con el modelo
    catalog = model.newCatalog()
    return catalog


# Funciones para la carga de datos

def loadData(catalog):

    primer_point = loadPoints(catalog)
    loadConexiones(catalog)
    ultimo_country = loadCountries(catalog)
    ConectarPointsIguales(catalog)

    return primer_point, ultimo_country

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
                    "capital": country["CapitalName"],
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

def connectedComponents(catalog):
    """
    Numero de componentes conectados
    """
    return model.connectedComponents(catalog)

def sameComponent(catalog, vert1, vert2):
    return model.sameComponent(catalog, vert1, vert2)

def getPointID(catalog, landing_point):
    return model.getPointID(catalog, landing_point)

def minExpansion(catalog):
    return model.minExpansion(catalog)

def affectedCountries(catalog, point):
    return model.affectedCountries(catalog, point)