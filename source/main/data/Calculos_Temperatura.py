# -*- coding: utf-8 -*-
"""
Created on Apr 12 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial en bruto y realiza 
todos los calculos necesarios para obtener la informacion dependiente de la temperatura
de manera comprensible y representable.
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

def calculos_temperatura(df):
    # Creacion de campos auxiliares
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))
    if 'DeltaDistancia' not in df.columns and 'Distancia' in df.columns:
        df['DeltaDistancia'] = (df['Distancia']-df['Distancia'].shift()).fillna(0)
    
    # Seleccion de la frecuencia de muestreo
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()

    # Si la actividad no tuviera alguno de estos campos lo completamos con 0
    df['TemperaturaAmbiente'] = df['TemperaturaAmbiente'].fillna(0)
    
    return df