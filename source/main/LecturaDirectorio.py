# -*- coding: utf-8 -*-
"""
Created on Mar 9 2019

@author: Felix Brinquis

Description: este programa es el programa principal. 
A partir de las variables que definimos inicialmente lee un fichero o varios, los cuales procesa de manera secuencial.

******************************************** WARNING ***********************************************
En la actualidad no es posible el procesamiento simultaneo de varios ficheros debido a problemas con
la libreria de visualizacion Bokeh.
****************************************************************************************************
"""

import glob, os
import pandas as pd
from sys import exit


"""
Definicion del entorno de ejecucion:

DirectorioBase: ubicacion del proyecto dentro del equipo en el que se ejecuta
Actividades: carpeta dentro del proyecto desde donde se leen los fcheros de entrada GPX
Informes: carpeta dentro del proyecto donde se depositan los resultados de la ejecucion
BBDD: carpeta dentro del proyecto donde se almacena un historial con datos de ejecuciones previas 

LecturaIndividual: [S/N] S: El programa solo buscara el fichero demandado N: El programa procesara todos los 
inputs que no hayan sido previamente ejecutados segun la BBDD de actividades
fichero: en caso de lectura individual sera el nombre del fichero GPX a procesar
"""
DirectorioBase = r'C:\Users\Felix\Desktop\PythonGPXAnalyzer'
Actividades = 'input'
Informes = 'output'
BBDD = 'library'

LecturaIndividual = 'S'
fichero = 'activity_3358982300.gpx'


# Comprobacion de la existencia de la estructura de directorios definida
os.chdir(os.path.join(DirectorioBase))
from source.common.funciones import CreacionDirectoriosProyecto
CreacionDirectoriosProyecto(DirectorioBase)

# Selecion de lectura masiva o individual de ficheros
if LecturaIndividual.upper() == 'S':
    if os.path.exists(os.path.join(DirectorioBase, Actividades, fichero)):
        FicherosCarga = [fichero]
    else:
        exit('No existe un fichero como el solicitado en el directorio de trabajo')
else:
    # Lectura del listado de ficheros ya procesados
    if os.path.exists(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv')):
            DataFrameBBDDFicheros = pd.read_csv(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv'), sep= ';', encoding = 'utf-8',usecols=[0])
    else:
            DataFrameBBDDFicheros = pd.DataFrame(columns=['NombreFichero'])
        
    # Seleccion de los ficheros que no se hayan procesado anteriormente
    os.chdir(os.path.join(DirectorioBase, Actividades))
    FicherosCarga = [x for x in list(glob.glob('*.gpx')) if x not in list(DataFrameBBDDFicheros['NombreFichero'])]


os.chdir(DirectorioBase)
from source.main.LecturaGPX import LecturaGPX
from source.common.funciones import LecturaBBDDActividades, AnalisisActividadActual, EscrituraBBDDActividades
from source.main.CalculosFuncion import CalculosDataframe
from source.main.CreacionHTML import CreacionHTML

for fichero in FicherosCarga:
    NombreFichero = fichero.rsplit('.', 1)[0].rsplit('\\', 1)[len(fichero.rsplit('.', 1)[0].rsplit('\\', 1))-1]

    # Lectura del fichero GPX
    NombreActividad, TipoActividad, df = LecturaGPX(os.path.join(DirectorioBase, Actividades, fichero))
    
    # Calculos en el DataFrame
    df = CalculosDataframe(df)

    # Visualizacion de la actividad
    CreacionHTML(DirectorioBase, Informes, NombreFichero, df)
    
    # Analisis y actualizacion de la BBDD de actividades
    DataFrameBBDDActividades = LecturaBBDDActividades(DirectorioBase, BBDD)
    DataFrameActividadActual = AnalisisActividadActual(fichero, NombreActividad, TipoActividad, df)
    EscrituraBBDDActividades(DirectorioBase, BBDD, DataFrameActividadActual, DataFrameBBDDActividades)
    os.replace(os.path.join(DirectorioBase, Actividades, fichero), os.path.join(DirectorioBase, Actividades, 'processed', fichero))