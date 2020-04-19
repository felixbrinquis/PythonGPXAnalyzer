# -*- coding: utf-8 -*-
"""
Created on Apr 12 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial en bruto y realiza 
todos los calculos necesarios para obtener la informacion dependiente de la cadencia de
braceo de manera comprensible y representable.

La metrica principal que se obtiene de estos calculos es la cadencia, obteniendo
ademas la longitud de zancada a partir de la distancia acumulada.
Para obtener esta metrica secundaria es necesario disponer de la variable 'DistanciaAcumulada'.
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


def calculos_cadencia(df):
    # Creacion de campos auxiliares
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))
    if 'DeltaDistancia' not in df.columns and 'Distancia' in df.columns:
        df['DeltaDistancia'] = (df['Distancia']-df['Distancia'].shift()).fillna(0)
    
    # Seleccion de la frecuencia de muestreo
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()

    # Si la actividad no tuviera alguno de estos campos lo completamos con 0
    df['CadenciaBraceo'] = df['CadenciaBraceo'].fillna(0)

    """
        CALCULOS INICIALES
        En este bloque se realiazan los calculos iniciales a partir de los datos brutos.
        Estos datos son susceptibles de sufrir variaciones importantes ya que la frecuencia de muestreo de los datos puede ser muy elevada 
        para poder registrar valores instantaneos de coordenadas o altitud con precision.
        Para poder afinar estos datos a valores mas cercanos a la realidad sera necesario un paso posterior en el que se calculen las diferencias
        de distancia o altitud con una frecuencia de muestreo mas baja.
    """
    for index, row in df.iterrows():
        # Calculo de la cadencia
        Cadencia = row['CadenciaBraceo']*2 # El dato de cadencia registrado es solo de 1 braceo  
        # Asignacion de los valores calculados en el DataFrame
        df.at[index,'Cadencia'] = Cadencia
    df = df.drop('CadenciaBraceo', 1)


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
    MuestrasCad = 5

    # El metodo Savitzky-Golay solo se aplicara si la actividad tiene una duracion minima
    df['Cadencia_SAVGOL'] = np.nan
    if df.shape[0] >= MuestrasCad:

        # Seleccion de bloques con numero de muestras superior al necesario por dato
        VectorMuestrasMinimas = df.groupby('Bloque')['Bloque'].count()
        BloquesMuestreablesCad = []
        for i, muestras in enumerate(VectorMuestrasMinimas):
            Bloque = i+1
            if muestras >= MuestrasCad:
                BloquesMuestreablesCad.append(Bloque)    

        # Cadencia SAVGOL
        df['Cadencia_SAVGOL_Bloque'] = np.nan
        df['Cadencia_SAVGOL_Bloque'] = np.nan
        df['Cadencia_SAVGOL_Total'] = df.loc[df['Bloque'].isin(BloquesMuestreablesCad)][['Bloque', 'Cadencia']].groupby('Bloque').transform(lambda x: savgol_filter(tuple(x), MuestrasCad, 3))
        df['Cadencia_SAVGOL_Total'] = df['Cadencia'].transform(lambda x: savgol_filter(tuple(x), MuestrasCad, 3))
        df['Cadencia_SAVGOL'] = df.Cadencia_SAVGOL_Bloque.combine_first(df.Cadencia_SAVGOL_Total)

    # Calculo de medias moviles dependientes de la frecuencia de muestreo por bloque
    df['Cadencia_10'] = df.groupby('Bloque')['Cadencia'].transform(lambda x: x.rolling(VMM_10, VMM_10).mean().bfill())

    # Seleccion de un valor calculado
    df['CadenciaCalculada'] = round(df.Cadencia_SAVGOL.combine_first(df.Cadencia_10))

    # Correccion de valores atipicos
    for index, row in df.iterrows():
        if row.CadenciaCalculada <= 0:
            CadenciaCorregida = np.nan
        else:
            CadenciaCorregida = row.CadenciaCalculada  
        df.at[index,'CadenciaCalculada'] = CadenciaCorregida           
    df['CadenciaCalculada'] = df['CadenciaCalculada'].fillna(method='ffill').fillna(0).astype(int)
        
    """
        CALCULOS SUAVIZADOS    
        Para minimizar los errores generados por la precision de los sensores realizamos una reduccion de la frecuencia de calculo.
        El valor de altitud que mejores resultados de desnivel acumulado ha arrojado es la media movil agrupada por bloques sin pausas
        con una ventana movil de 20 observaciones, reiniciando la posicion inicial de altitud a la medida real en cada pausa.
    """
    # Los calculos de longitud de zancada estan condicionados a al movimiento en el espacio
    if 'Distancia' in df.columns:
        MuestrasCadencia = 0
        SumaCadencia = 0
        DistanciaAnteriorCadencia = 0
        LongitudZancada = float('NaN')
        CadenciaAnterior = df[df.index.min()==df.index]['Cadencia'].min()

        for index, row in df.iterrows(): 
            # Calculo de la longitud de zancada
            if row.CadenciaCalculada > 0:
                if row['DeltaTiempo'].total_seconds() == 0:
                    LongitudZancada = float('NaN')
                    DistanciaAnteriorCadencia = row['Distancia']
                    MuestrasCadencia = 1
                    SumaCadencia = row['Cadencia']
                    CadenciaAnterior = row['Cadencia']
                else:
                    if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
                        MuestrasCadencia+=1
                        SumaCadencia = SumaCadencia + row['Cadencia'] 
                        # Si se aprecia una variacion sustancial en la cadencia se registra
                        if MuestrasCadencia < 5/FrecuenciaMuestreo:
                            if row['Cadencia'] < 0.8*CadenciaAnterior or row['Cadencia'] > 1.2*CadenciaAnterior:
                                try:
                                    LongitudZancada = (row['Distancia']-DistanciaAnteriorCadencia)/((SumaCadencia)/60)
                                except:
                                    LongitudZancada = 0
                                DistanciaAnteriorCadencia = row['Distancia']
                                MuestrasCadencia = 0
                                SumaCadencia = 0
                        else:
                            try:
                                LongitudZancada = (row['Distancia']-DistanciaAnteriorCadencia)/((SumaCadencia)/60)
                            except:
                                LongitudZancada = 0
                            DistanciaAnteriorCadencia = row['Distancia']
                            MuestrasCadencia = 0
                            SumaCadencia = 0
                        CadenciaAnterior = row['Cadencia'] 
                    else:
                        LongitudZancada = float('NaN')
                        DistanciaAnteriorCadencia = row['Distancia']
                        MuestrasCadencia = 1
                        SumaCadencia = row['Cadencia']
                        CadenciaAnterior = row['Cadencia']
            else:
                LongitudZancada = 0

            # Asignacion de los valores calculados en el DataFrame
            df.at[index,'LongitudZancada'] = LongitudZancada

        df['LongitudZancada'] = df['LongitudZancada'].fillna(method='bfill')
    
    # Eliminacion de datos auxiliares segun el patron definido
    df = df.drop(df.filter(regex='\B_SAVGOL|_([0-9][0-9]?)$').columns, axis=1)
    
    df = df.drop('Cadencia', 1)

    return df