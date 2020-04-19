# -*- coding: utf-8 -*-
"""
Created on Apr 15 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial en bruto en el que
ya se dispone de la distancia acumulada por puntos.
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


def calculos_distancia(df):
    # Creacion de campos auxiliares
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))

    # Seleccion de la frecuencia de muestreo
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()

    # Creacion de campos auxiliares
    df['DistanciaAnterior'] = df['Distancia'].shift().fillna(df['Distancia'])

    """
        CALCULOS INICIALES
        En este bloque se realiazan los calculos iniciales a partir de los datos brutos.
        Estos datos son susceptibles de sufrir variaciones importantes ya que la frecuencia de muestreo de los datos puede ser muy elevada 
        para poder registrar valores instantaneos de coordenadas o altitud con precision.
        Para poder afinar estos datos a valores mas cercanos a la realidad sera necesario un paso posterior en el que se calculen las diferencias
        de distancia o altitud con una frecuencia de muestreo mas baja.
    """
    DistanciaBloque = 0
    DeltaDistancia = 0
    
    for index, row in df.iterrows():
        # Calculo de la diferencia de distancia entre 2 coordenadas
        if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
            DeltaDistancia = row['Distancia'] - row['DistanciaAnterior']
            DistanciaBloque = DistanciaBloque + DeltaDistancia
        elif row['DeltaTiempo'].total_seconds() > FrecuenciaMuestreo:
            DeltaDistancia = 0
            DistanciaBloque = 0
        else:
            DeltaDistancia = 0

        # Asignacion de los valores calculados en el DataFrame
        df.at[index,'DeltaDistancia'] = DeltaDistancia
        df.at[index,'DistanciaBloque'] = DistanciaBloque 
    df = df.drop('DistanciaAnterior', 1)
    df['Distancia'] = df['Distancia'].fillna(method='ffill')
    df['DeltaDistancia'] = df['DeltaDistancia'].fillna(0)
    df['DistanciaBloque'] = df['DistanciaBloque'].fillna(0)
    
    return df