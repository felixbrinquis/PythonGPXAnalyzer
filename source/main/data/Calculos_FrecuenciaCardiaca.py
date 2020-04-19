# -*- coding: utf-8 -*-
"""
Created on Apr 12 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial en bruto y realiza 
todos los calculos necesarios para obtener la informacion dependiente de la frecuencia
cardiaca de manera comprensible y representable.
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


def calculos_frecuenciacardiaca(df):
    # Creacion de campos auxiliares
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))
    if 'DeltaDistancia' not in df.columns and 'Distancia' in df.columns:
        df['DeltaDistancia'] = (df['Distancia']-df['Distancia'].shift()).fillna(0)
    
    # Seleccion de la frecuencia de muestreo
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()


    # Si la actividad no tuviera alguno de estos campos lo completamos con 0
    df['FrecuenciaCardiaca'] = df['FrecuenciaCardiaca'].fillna(0)

    """
       SUAVIZADO DE DATOS
       El suavizado de los datos a analizar lo realizaremos en primera instancia agrupado por bloques continuos debido a las discontinuidades
       que generan las pausas temporales. Si el tamaño del bloque no es superior al numero de muestras minimo del metodo Savitzky-Golay
       se tomara el valor calculado sobre el total de los datos para ese bloque. Si la actividad no tuviera un tamaño minimo, no se
       aplicaria este metodo.
       Tambien se realizan distintos suavizados por medias moviles con ventanas temporales dependientes de la frecuencia de muestreo que
       van desde los 5 segundos a los 30.
       Finalmente seleccionamos un unico valor calculado que será el que mejor se adapte a cada proposito. 
    """
    # Calculo de ventanas de medias moviles(VMM_n) dependientes de la frecuencia de muestreo de los datos
    VMM_5 = ceil(5/FrecuenciaMuestreo)
    VMM_10 = ceil(10/FrecuenciaMuestreo)
    VMM_15 = ceil(15/FrecuenciaMuestreo)
    VMM_20 = ceil(20/FrecuenciaMuestreo)
    VMM_30 = ceil(30/FrecuenciaMuestreo)

    # Suavizado de los datos por el metodo Savitzky-Golay
    MuestrasFC = 9

    # El metodo Savitzky-Golay solo se aplicara si la actividad tiene una duracion minima
    df['FrecuenciaCardiaca_SAVGOL'] = np.nan
    if df.shape[0] >= MuestrasFC:
        # Seleccion de bloques con numero de muestras superior al necesario por dato
        VectorMuestrasMinimas = df.groupby('Bloque')['Bloque'].count()
        BloquesMuestreablesFC = []
        for i, muestras in enumerate(VectorMuestrasMinimas):
            Bloque = i+1
            if muestras >= MuestrasFC:
                BloquesMuestreablesFC.append(Bloque) 
       
        # Frecuencia cardiaca SAVGOL
        df['FrecuenciaCardiaca_SAVGOL_Bloque'] = np.nan
        df['FrecuenciaCardiaca_SAVGOL_Bloque'] = np.nan
        df['FrecuenciaCardiaca_SAVGOL_Total'] = df.loc[df['Bloque'].isin(BloquesMuestreablesFC)][['Bloque','FrecuenciaCardiaca']].groupby('Bloque').transform(lambda x: savgol_filter(tuple(x), MuestrasFC, 3))
        df['FrecuenciaCardiaca_SAVGOL_Total'] = df['FrecuenciaCardiaca'].transform(lambda x: savgol_filter(tuple(x), MuestrasFC, 3))
        df['FrecuenciaCardiaca_SAVGOL'] = df.FrecuenciaCardiaca_SAVGOL_Bloque.combine_first(df.FrecuenciaCardiaca_SAVGOL_Total)

    # Calculo de medias moviles dependientes de la frecuencia de muestreo por bloque
    df['FrecuenciaCardiaca_10'] = df.groupby('Bloque')['FrecuenciaCardiaca'].transform(lambda x: x.rolling(VMM_10, VMM_10).mean().bfill())

    # Seleccion de un valor calculado
    df['FrecuenciaCardiacaCalculada'] = round(df.FrecuenciaCardiaca_SAVGOL.combine_first(df.FrecuenciaCardiaca_10))

    # Correccion de valores atipicos
    for index, row in df.iterrows():
        if row.FrecuenciaCardiacaCalculada <= 0:
            FrecuenciaCardiacaCorregida = np.nan        
        else:
            FrecuenciaCardiacaCorregida = row.FrecuenciaCardiacaCalculada 
        df.at[index,'FrecuenciaCardiacaCalculada'] = FrecuenciaCardiacaCorregida    
    df['FrecuenciaCardiacaCalculada'] = df['FrecuenciaCardiacaCalculada'].fillna(method='ffill').fillna(0).astype(int)

    # Eliminacion de datos auxiliares segun el patron definido
    df = df.drop(['FrecuenciaCardiaca'], axis=1)
    df = df.drop(df.filter(regex='\B_SAVGOL|_([0-9][0-9]?)$').columns, axis=1)
    
    return df