# -*- coding: utf-8 -*-
"""
Created on Apr 12 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial en bruto y realiza
todos los calculos necesarios para obtener la informacion dependiente de la referencia
temporal de manera comprensible y representable.

Las metricas principales que se obtienen de estos calculos son el tiempo total transcurrido
desde el inicio de la actividad y el tiempo total activo, obteniendo tambien el numero de
bloques temporales definidos por las pausas de la actividad y el numero de muestras por
cada uno de estos bloques.
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



def calculos_tiempo(df):
    # Creacion de campos auxiliares
    df['HoraMuestra'] = df.index
    df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))

    # Seleccion de la frecuencia de muestreo
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()


    """
        CALCULOS INICIALES
        En este bloque se realiazan los calculos iniciales a partir de los datos brutos.
        Estos datos son susceptibles de sufrir variaciones importantes ya que la frecuencia de muestreo de los datos puede ser muy elevada
        para poder registrar valores instantaneos de coordenadas o altitud con precision.
        Para poder afinar estos datos a valores mas cercanos a la realidad sera necesario un paso posterior en el que se calculen las diferencias
        de distancia o altitud con una frecuencia de muestreo mas baja.
    """
    HoraInicioActiviad = df.index.min()
    HoraFinActiviad = df.index.max()
    df['TiempoTotal'] = df['HoraMuestra'] - HoraInicioActiviad
    TiempoActividad = datetime.timedelta(seconds=0)

    Bloque = 1
    NumeroMuestrasPorBloque = 1

    for index, row in df.iterrows():
        # Calculo de la diferencia de distancia entre 2 coordenadas
        if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
            TiempoActividad = TiempoActividad + row['DeltaTiempo']
            NumeroMuestrasPorBloque+=1
        elif row['DeltaTiempo'].total_seconds() > FrecuenciaMuestreo:
            Bloque+=1
            NumeroMuestrasPorBloque = 1
        else:
            NumeroMuestrasPorBloque+=1

        # Asignacion de los valores calculados en el DataFrame
        df.at[index,'TiempoActividad'] = TiempoActividad
        df.at[index,'Bloque'] = Bloque
        df.at[index,'NumeroMuestrasPorBloque'] = NumeroMuestrasPorBloque
    df = df.drop('HoraMuestra', 1)

    return df