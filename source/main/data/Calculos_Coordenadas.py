# -*- coding: utf-8 -*-
"""
Created on Apr 12 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial en bruto y realiza 
todos los calculos necesarios para obtener la informacion posicional de las coordenadas GPS
de manera comprensible y representable.

La metrica principal que se obtiene de estos calculos es la distancia recorrida.
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


def calculos_coordenadas(df):
    # Creacion de campos auxiliares
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))

    # Seleccion de la frecuencia de muestreo
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()

    # Creacion de campos auxiliares
    df['LatitudAnterior'] = df['Latitud'].shift().fillna(df['Latitud'])
    df['LongitudAnterior'] = df['Longitud'].shift().fillna(df['Longitud'])


    """
        CALCULOS INICIALES
        En este bloque se realiazan los calculos iniciales a partir de los datos brutos.
        Estos datos son susceptibles de sufrir variaciones importantes ya que la frecuencia de muestreo de los datos puede ser muy elevada 
        para poder registrar valores instantaneos de coordenadas o altitud con precision.
        Para poder afinar estos datos a valores mas cercanos a la realidad sera necesario un paso posterior en el que se calculen las diferencias
        de distancia o altitud con una frecuencia de muestreo mas baja.
    """
    Distancia = 0
    DistanciaBloque = 0
    DeltaDistancia = 0
    
    for index, row in df.iterrows():
        # Calculo de la diferencia de distancia entre 2 coordenadas
        if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
            DeltaDistancia = geopy.distance.distance((row.Latitud, row.Longitud), (row.LatitudAnterior, row.LongitudAnterior)).m
            DistanciaBloque = DistanciaBloque + DeltaDistancia
        elif row['DeltaTiempo'].total_seconds() > FrecuenciaMuestreo:
            DeltaDistancia = 0
            DistanciaBloque = 0
        else:
            DeltaDistancia = 0

        # Calculo de distancia acumulada
        Distancia = Distancia + DeltaDistancia
        
        # Asignacion de los valores calculados en el DataFrame
        df.at[index,'DeltaDistancia'] = DeltaDistancia
        df.at[index,'Distancia'] = Distancia
        df.at[index,'DistanciaBloque'] = DistanciaBloque 
    df = df.drop('LatitudAnterior', 1)
    df = df.drop('LongitudAnterior', 1)
    df['DeltaDistancia'] = df['DeltaDistancia'].fillna(0)
    df['DistanciaBloque'] = df['DistanciaBloque'].fillna(0)
    df['Distancia'] = df['Distancia'].fillna(method='ffill')
    
    return df