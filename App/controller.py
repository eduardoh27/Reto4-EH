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

    loadPoints(catalog)
    loadConexiones(catalog)
    ConectarPointsIguales(catalog)
    ConectarCablesIguales(catalog)

def loadPoints(catalog):
    """
    Carga los eventos del archivo. Por cada evento se toma los datos necesarios:
    instrumentalness,  danceability, tempo, energy, id del artista, id de la pista, 
    y fecha de publicación.
    """
    videosfile = cf.data_dir + 'landing_points.csv'
    
    input_file = csv.DictReader(open(videosfile, encoding='utf-8'))
    for point in input_file:
        cada_point = {"landing_point_id": point["landing_point_id"],
                    "location": point["name"].split(","),
                    "latitude": float(point["latitude"]),
                    "longitude": float(point["longitude"])
                  }       

        model.addPoint(catalog, cada_point)

def loadConexiones(catalog):
    """
    Carga los eventos del archivo. Por cada evento se toma los datos necesarios:
    instrumentalness,  danceability, tempo, energy, id del artista, id de la pista, 
    y fecha de publicación.
    """
    videosfile = cf.data_dir + 'connections.csv'
    
    input_file = csv.DictReader(open(videosfile, encoding='utf-8-sig'))
    i = 1
    for conexion in input_file:
        if i%2 != 0:
            cada_conexion = {"origin": conexion["origin"],
                        "destination": conexion["destination"],
                        "cable_name": conexion["cable_name"]
                    }       
            i += 1
            model.addConexion(catalog, cada_conexion)


def loadCountries(catalog):
    """
    Carga los eventos del archivo. Por cada evento se toma los datos necesarios:
    instrumentalness,  danceability, tempo, energy, id del artista, id de la pista, 
    y fecha de publicación.
    """
    videosfile = cf.data_dir + 'countries.csv'
    
    input_file = csv.DictReader(open(videosfile, encoding='utf-8-sig'))
    for country in input_file:
        cada_country = {"country": conexion["Country Name"],
                    "capital": conexion["Capital Name"]
                  }       

        model.addCountry(catalog, cada_country)

def ConectarPointsIguales(catalog):
    model.ConectarPointsIguales(catalog)

def ConectarCablesIguales(catalog):
    model.ConectarCablesIguales(catalog)