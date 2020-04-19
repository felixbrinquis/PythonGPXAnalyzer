# -*- coding: utf-8 -*-
"""
Created on Apr 12 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial en bruto y realiza 
todos los calculos necesarios para obtener la informacion dependiente de la altitud de 
manera comprensible y representable.

La metrica principal que se obtiene de estos calculos es la altitud, obteniendo ademas 
el desnivel positivo y negativo acumulado y la pendiente instantanea.
Para obtener esta ultima metrica secundaria es necesario disponer de la variable 'DistanciaAcumulada'.
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


def calculos_altitud(df):
    # Creacion de campos auxiliares
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))
    if 'DeltaDistancia' not in df.columns and 'Distancia' in df.columns:
        df['DeltaDistancia'] = (df['Distancia']-df['Distancia'].shift()).fillna(0)
    
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
    AltitudInicio, AltitudFin = df.loc[df.index.min() == df.index, ['Altitud']].min()[0], df.loc[df.index.max() == df.index, ['Altitud']].min()[0]
    AltitudAnterior = AltitudInicio

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
    MuestrasAlt = 21

    # El metodo Savitzky-Golay solo se aplicara si la actividad tiene una duracion minima
    df['Altitud_SAVGOL'] = np.nan

    if df.shape[0] >= MuestrasAlt:
        # Seleccion de bloques con numero de muestras superior al necesario por dato
        VectorMuestrasMinimas = df.groupby('Bloque')['Bloque'].count()
        BloquesMuestreablesAlt = []
        for i, muestras in enumerate(VectorMuestrasMinimas):
            Bloque = i+1
            if muestras >= MuestrasAlt:
                BloquesMuestreablesAlt.append(Bloque)
      
        # Altitud SAVGOL
        df['Altitud_SAVGOL_Bloque'] = np.nan
        df['Altitud_SAVGOL_Bloque'] = np.nan
        df['Altitud_SAVGOL_Total'] = df.loc[df['Bloque'].isin(BloquesMuestreablesAlt)][['Bloque', 'Altitud']].groupby('Bloque').transform(lambda x: savgol_filter(tuple(x), MuestrasAlt, 3))
        df['Altitud_SAVGOL_Total'] = df['Altitud'].transform(lambda x: savgol_filter(tuple(x), MuestrasAlt, 3))
        df['Altitud_SAVGOL'] = df.Altitud_SAVGOL_Bloque.combine_first(df.Altitud_SAVGOL_Total)

    # Calculo de medias moviles dependientes de la frecuencia de muestreo por bloque
    df['Altitud_20'] = df.groupby('Bloque')['Altitud'].transform(lambda x: x.rolling(VMM_20, VMM_20).median().bfill())

    # Seleccion de un valor calculado
    df['AltitudCalculada'] = round(df.Altitud_SAVGOL.combine_first(df.Altitud_20), 1)

    """
        CALCULOS SUAVIZADOS    
        Para minimizar los errores generados por la precision de los sensores realizamos una reduccion de la frecuencia de calculo.
        El valor de altitud que mejores resultados de desnivel acumulado ha arrojado es la media movil agrupada por bloques sin pausas
        con una ventana movil de 20 observaciones, reiniciando la posicion inicial de altitud a la medida real en cada pausa.
    """
    # Los calculos de pendiente estan condicionados a al movimiento en el espacio
    if 'Distancia' in df.columns:
        ContadorDesnivel = 0
        Pendiente = 0
        DesnivelPositivoAcumulado = 0
        DesnivelNegativoAcumulado = 0

        for index, row in df.iterrows(): 
            # Calculo del desnivel acumulado
            if row['DeltaTiempo'].total_seconds() == 0:
                # Inicializacion en la primera lectura
                AltitudAnterior = row['AltitudCalculada']
                AltitudPendiente = row['AltitudCalculada']
                DistanciaAnterior = row ['Distancia']
                Pendiente = 0
                DesnivelPositivoAcumulado = 0
                DesnivelNegativoAcumulado = 0
            else:
                # Se mide solo el desnivel en funcionamiento
                if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
                    # Diferencia de altitud instantanea
                    DeltaAltitud = row['AltitudCalculada'] - AltitudAnterior
                    DeltaDistancia = row['Distancia'] - DistanciaAnterior
                    # El conteo del desnivel cada segundo da un error del 25%. Hay que reducir la frecencia de captura del dato
                    if ContadorDesnivel < 10/FrecuenciaMuestreo:
                        # Si el desnivel es superior a 2 metros se contabiliza, sino se añade un retraso
                        if DeltaAltitud >= 2:
                            if DeltaDistancia > 0:
                                DesnivelPositivoAcumulado = DesnivelPositivoAcumulado + DeltaAltitud
                                AltitudAnterior = row['AltitudCalculada']
                                if row['NumeroMuestrasPorBloque'] > 10:
                                    Pendiente = (row['AltitudCalculada'] - AltitudPendiente)/DeltaDistancia*100
                                    AltitudPendiente = row['AltitudCalculada']
                                DistanciaAnterior = row ['Distancia']
                                ContadorDesnivel = 0
                        elif DeltaAltitud <= -2: 
                            if DeltaDistancia > 0:
                                DesnivelNegativoAcumulado = DesnivelNegativoAcumulado + abs(DeltaAltitud)
                                AltitudAnterior = row['AltitudCalculada']
                                if row['NumeroMuestrasPorBloque'] > 10:
                                    Pendiente = (row['AltitudCalculada'] - AltitudPendiente)/DeltaDistancia*100
                                    AltitudPendiente = row['AltitudCalculada']
                                DistanciaAnterior = row ['Distancia']
                                ContadorDesnivel = 0
                        else:
                            ContadorDesnivel+=1
                    else:
                        # Si transcurren 10 segundos sin contabilizar una diferenca, se añade
                        if DeltaAltitud > 0:
                            if DeltaDistancia > 0:
                                DesnivelPositivoAcumulado = DesnivelPositivoAcumulado + DeltaAltitud
                                AltitudAnterior = row['AltitudCalculada']
                                if row['NumeroMuestrasPorBloque'] > 10:
                                    Pendiente = (row['AltitudCalculada'] - AltitudPendiente)/DeltaDistancia*100
                                    AltitudPendiente = row['AltitudCalculada']
                                DistanciaAnterior = row ['Distancia']
                                ContadorDesnivel = 0
                        elif DeltaAltitud < 0:
                            if DeltaDistancia > 0:
                                DesnivelNegativoAcumulado = DesnivelNegativoAcumulado + abs(DeltaAltitud)
                                AltitudAnterior = row['AltitudCalculada']
                                if row['NumeroMuestrasPorBloque'] > 10:
                                    Pendiente = (row['AltitudCalculada'] - AltitudPendiente)/DeltaDistancia*100
                                    AltitudPendiente = row['AltitudCalculada']
                                DistanciaAnterior = row ['Distancia']
                                ContadorDesnivel = 0
                        else:
                            ContadorDesnivel = 0
                else:
                    # Correccion de valores en las pausas
                    AltitudAnterior = row['AltitudCalculada']
                    AltitudPendiente = row['AltitudCalculada']
                    DistanciaAnterior = row ['Distancia']
            
            # Asignacion de los valores calculados en el DataFrame
            df.at[index,'PendienteCalculada'] = Pendiente
            df.at[index,'DesnivelPositivoAcumulado'] = DesnivelPositivoAcumulado
            df.at[index,'DesnivelNegativoAcumulado'] = DesnivelNegativoAcumulado
        df['PendienteCalculada'] = df['PendienteCalculada'].transform(lambda x: x.rolling(VMM_20, VMM_20).mean().bfill())
    
    # Eliminacion de datos auxiliares segun el patron definido
    df = df.drop(['Altitud'], axis=1)
    df = df.drop(df.filter(regex='\B_SAVGOL|_([0-9][0-9]?)$').columns, axis=1)
 
    return df