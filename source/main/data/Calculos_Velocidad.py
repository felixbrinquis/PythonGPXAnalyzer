# -*- coding: utf-8 -*-
"""
Created on Apr 14 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe en el que ya se han extraido
las variables que defnen el espacio y el tiempo.

La metrica principal que se obtiene de estos calculos es la velocidad, obteniendo tambien
el ritmo instantaneo.
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


def calculos_velocidad(df):
    # Creacion de campos auxiliares
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))
    if 'DeltaDistancia' not in df.columns and 'Distancia' in df.columns:
        df['DeltaDistancia'] = (df['Distancia']-df['Distancia'].shift()).fillna(0)
        
    # Seleccion de la frecuencia de muestreo
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()

    if 'Velocidad' not in df.columns:
        """
            CALCULOS INICIALES
            En este bloque se realiazan los calculos iniciales a partir de los datos brutos.
            Estos datos son susceptibles de sufrir variaciones importantes ya que la frecuencia de muestreo de los datos puede ser muy elevada 
            para poder registrar valores instantaneos de coordenadas o altitud con precision.
            Para poder afinar estos datos a valores mas cercanos a la realidad sera necesario un paso posterior en el que se calculen las diferencias
            de distancia o altitud con una frecuencia de muestreo mas baja.
        """
        Velocidad_i = np.nan

        for index, row in df.iterrows():
            # Calculo de la velocidad instantanea en [m/s] entre puntos
            if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
                Velocidad_i = np.divide(row['DeltaDistancia'], row['DeltaTiempo'].total_seconds())
            
            # Asignacion de los valores calculados en el DataFrame
            df.at[index,'Velocidad_i'] = Velocidad_i
        df['Velocidad_i'] = df['Velocidad_i'].fillna(method='bfill')


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
        MuestrasVel = 31

        # El metodo Savitzky-Golay solo se aplicara si la actividad tiene una duracion minima
        df['Velocidad_SAVGOL'] = np.nan
        if df.shape[0] >= MuestrasVel:
            # Seleccion de bloques con numero de muestras superior al necesario por dato
            VectorMuestrasMinimas = df.groupby('Bloque')['Bloque'].count()

            BloquesMuestreablesVel = []

            for i, muestras in enumerate(VectorMuestrasMinimas):
                Bloque = i+1
                if muestras >= MuestrasVel:
                    BloquesMuestreablesVel.append(Bloque)   
                    
            # Velocidad SAVGOL
            df['Velocidad_SAVGOL_Bloque'] = np.nan
            df['Velocidad_SAVGOL_Bloque'] = np.nan
            df['Velocidad_SAVGOL_Total'] = df.loc[df['Bloque'].isin(BloquesMuestreablesVel)][['Bloque', 'Velocidad_i']].groupby('Bloque').transform(lambda x: savgol_filter(tuple(x), MuestrasVel, 3))
            df['Velocidad_SAVGOL_Total'] = df['Velocidad_i'].transform(lambda x: savgol_filter(tuple(x), MuestrasVel, 3))
            df['Velocidad_SAVGOL'] = df.Velocidad_SAVGOL_Bloque.combine_first(df.Velocidad_SAVGOL_Total) 

        # Calculo de medias moviles dependientes de la frecuencia de muestreo por bloque
        df['Velocidad_5'] = df.groupby('Bloque')['Velocidad_i'].transform(lambda x: x.rolling(VMM_5, VMM_5).mean().bfill())

        # Seleccion de un valor calculado
        df['VelocidadCalculada'] = round(df.Velocidad_SAVGOL.combine_first(df.Velocidad_5), 2)

        # Correccion de valores atipicos
        for index, row in df.iterrows():    
            if row.VelocidadCalculada <= 0:
                VelocidadCorregida = np.nan
            else:
                VelocidadCorregida = row.VelocidadCalculada       
            df.at[index,'VelocidadCalculada'] = VelocidadCorregida     
        df['VelocidadCalculada'] = df['VelocidadCalculada'].fillna(method='ffill').fillna(0)

        # Eliminacion de datos auxiliares
        df = df.drop(['Velocidad_i'], axis=1)
    else:
        df['VelocidadCalculada'] = df['Velocidad']
        df = df.drop(['Velocidad'], axis=1)
    
    """
        RITMO [MIN/KM]
        Calculo del ritmo en min/km
    """
    for index, row in df.iterrows():
        # Calculo del ritmo equivalente    
        if row['VelocidadCalculada'] >= 0.5:
            Ritmo = datetime.timedelta(seconds=1000/row['VelocidadCalculada'])
        else:
            Ritmo = np.nan

        # Asignacion de los valores calculados en el DataFrame
        df.at[index,'Ritmo'] = Ritmo
    df['Ritmo'] = df['Ritmo'].fillna(method='bfill')

    # Eliminacion de datos auxiliares segun el patron definido
    df = df.drop(df.filter(regex='\B_SAVGOL|_([0-9][0-9]?)$').columns, axis=1)
 
    return df