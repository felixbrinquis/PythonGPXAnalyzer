# -*- coding: utf-8 -*-
"""
Created on Apr 12 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial leido en 
bruto e invoca a cada uno de los subprocesos de calculo segun la existencia de 
las metricas de origen necesarias en los datos leidos.
"""


"""
    DEFINICION DEL ENTORNO
"""
# Importacion de librerias
import pandas as pd
import numpy as np
import geopy.distance
import datetime
from math import ceil
from scipy.signal import savgol_filter

from source.main.data.Calculos_Tiempo import calculos_tiempo

from source.main.data.Calculos_Velocidad import calculos_velocidad
from source.main.data.Calculos_FrecuenciaCardiaca import calculos_frecuenciacardiaca
from source.main.data.Calculos_Altitud import calculos_altitud
from source.main.data.Calculos_Temperatura import calculos_temperatura
from source.main.data.Calculos_Cadencia import calculos_cadencia

def CalculosDataframe(df):
    """
        TIEMPO
        La referencia temporal es basica para la realizacion de todos los calculos. Ademas su presencia
        en el fichero de origen esta garantizada, por lo que sirve como indice y sus calculos son los
        primeros en realizarse.
    """
    df = calculos_tiempo(df)


    """
        ESPACIO
        El segundo dato que es necesario calcular frecuentemente es la distancia recorrida. 
        En actividades Outdoor esta se obtiene a partir de las coordenadas GPS.
        En actividades Indoor existiran otros metodos de obtencion si fuera necesario.
    """
    if 'Latitud' in df.columns and 'Longitud' in df.columns:
        from source.main.data.Calculos_Coordenadas import calculos_coordenadas
        df = calculos_coordenadas(df)
    elif 'Distancia' in df.columns:
        from source.main.data.Calculos_Distancia import calculos_distancia
        df = calculos_distancia(df)

    """
        El resto de metricas son secundarias o dependientes de las anteriores.
    """
    if 'Distancia' in df.columns or 'Velocidad' in df.columns:
        df = calculos_velocidad(df)
    
    if 'FrecuenciaCardiaca' in df.columns:
        df = calculos_frecuenciacardiaca(df)
    
    if 'Altitud' in df.columns:
        df = calculos_altitud(df)
    
    if 'TemperaturaAmbiente' in df.columns:
        df = calculos_temperatura(df)
    
    if 'CadenciaBraceo' in df.columns:
        df = calculos_cadencia(df)

    """
        Renombrado de campos calculados existentes
    """
    campos_rename = {'VelocidadCalculada':'Velocidad',
                     'FrecuenciaCardiacaCalculada':'FrecuenciaCardiaca',
                     'AltitudCalculada':'Altitud',
                     'PendienteCalculada':'Pendiente',
                     'CadenciaCalculada':'Cadencia'}
    
    dict_rename = {}
    for Column in df.columns:
        for key in campos_rename:
            if Column == key:
                dict_rename.update({key : campos_rename[key]})

    df.rename(columns = dict_rename, inplace = True)


    """
        Una vez finalzados los calculos se pueden eliminar los deltas si existieran
    """
    df = df.drop(['DeltaTiempo', 'DeltaDistancia'], axis=1, errors='ignore')

    return df