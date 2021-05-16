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
    delta_time = -1.0
    delta_memory = -1.0

    tracemalloc.start()
    start_time = getTime()
    start_memory = getMemory()

    loadEventos(catalog)
    loadTracks(catalog)
    loadHashtags(catalog)

    stop_memory = getMemory()
    stop_time = getTime()
    tracemalloc.stop()

    delta_time = stop_time - start_time
    delta_memory = deltaMemory(start_memory, stop_memory)

    return delta_time, delta_memory

def loadEventos(catalog):
    """
    Carga los eventos del archivo. Por cada evento se toma los datos necesarios:
    instrumentalness,  danceability, tempo, energy, id del artista, id de la pista, 
    y fecha de publicación.
    """
    videosfile = cf.data_dir + 'connections.csv'
    
    input_file = csv.DictReader(open(videosfile, encoding='utf-8'))
    for evento in input_file:
        cada_evento = {"instrumentalness": float(evento["instrumentalness"]),
                  "danceability": float(evento["danceability"]),
                  "tempo": float(evento["tempo"]),
                  "energy": float(evento["energy"]),
                  "artist_id": evento["artist_id"],
                  "track_id": evento["track_id"],
                  "time": datetime.datetime.strptime(evento["created_at"], '%Y-%m-%d %H:%M:%S').time(),
                  "user_id": evento["user_id"],
                  "id": evento["id"]
                  }       
        model.addEvento(catalog, cada_evento)