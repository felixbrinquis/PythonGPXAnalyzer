# -*- coding: utf-8 -*-
"""
Created on Apr 13 2019

@author: Felix Brinquis

Description: conjunto de funciones que podrian usarse recursivamente en varios programas.
"""


import pandas as pd
import numpy as np
from math import ceil, floor, radians, pi, log, tan
import datetime
import os

"""
    DEFINICION DE FUNCIONES
"""


# Generacion de coordenadas mercator
def ConversorCoordenadasMercator(lon, lat):
    """
    Funcion que convierte las coordenadas en radianes a mercator de modo que se pueda visualizar en el mapa
    """
    r_major = 6378137.000
    x = r_major * radians(lon)
    scale = x/lon
    y = 180.0/pi * log(tan(pi/4.0 + lat * (pi/180.0)/2.0)) * scale
    return (x, y)



# Formateo de tiempos como texto
def FormateoTiempos(Tiempo_TD, Formato= 'T'):
    """
      Funcion que recibe como parametros una variable en formato timedelta y la forma de mostrar los datos 
      y devuelve texto formateado.
      
      Z: 00:00:05 - 01:08:25
      T: 00:05 - 1:08:25
      R: 0:05 - 1:08:25
      MM: 00 - 68
      HMM: 0:00 - 1:08
          
    """
    DD, SS = Tiempo_TD.days, Tiempo_TD.seconds
    HH = DD * 24 + SS // 3600
    MM = (SS % 3600) // 60
    SS = SS % 60
    
    if Formato.upper() == 'T':
        if HH > 0:
            TiempoFormateado = str(HH)+':'+str(MM).zfill(2)+':'+str(SS).zfill(2)
        else:
            TiempoFormateado = str(MM).zfill(2)+':'+str(SS).zfill(2)
    elif Formato.upper() == 'R':
        if HH > 0:
            TiempoFormateado = str(HH)+':'+str(MM).zfill(2)+':'+str(SS).zfill(2)
        else:
            TiempoFormateado = str(MM)+':'+str(SS).zfill(2) 
    elif Formato.upper() == 'MM':
        TiempoFormateado = str(HH*60+MM).zfill(2)
    elif Formato.upper() == 'HMM':
        TiempoFormateado = str(HH)+':'+str(MM).zfill(2)
    else: # Por defecto format Z
        TiempoFormateado = str(HH).zfill(2)+':'+str(MM).zfill(2)+':'+str(SS).zfill(2) 
        
    return TiempoFormateado



def FormulaKarvonen(FCM, FCR, I):
    """
    Formula que devuelve unas pulsaciones en funcion de las pulsaciones maximas, minimas y el % de intensidad objetivo
    """
    FCO = ((FCM - FCR) * I) + FCR
    return FCO


# Reescalado de un valor para mostrar sobre otra medida
def Reescalado(Valor, RangoOrginal, RangoEscalado):
    Delta1 = RangoOrginal[1] - RangoOrginal[0]
    Delta2 = RangoEscalado[1] - RangoEscalado[0]
    return (Delta2 * (Valor - RangoOrginal[0]) / Delta1) + RangoEscalado[0]


def FormateoEjes(VariableDataFrame, PrecisionTick= 10, ReduccionEscala= 1, MargenInferior= 0.5, MargenSuperior= 0.5):
    """
        Funcion que recibe una variable de un DataFrame y devuelve un dicionario de valores y su correspondiente en formato texto 
        entre el minimo y el maximo valor con margenes inferior y superior, con una dstancia entre valores y reduccion de escala si fuera necesario
    """
    return {i: str(int(i/ReduccionEscala)) for i in range(int(floor(VariableDataFrame.min()*(1-MargenInferior) / PrecisionTick)) * PrecisionTick , int(ceil(VariableDataFrame.max()*(1+MargenSuperior) / PrecisionTick)) * PrecisionTick + PrecisionTick, PrecisionTick)}


"""
    MEDIAS, MAXIMOS Y MINIMOS
    Calculo de medias, maximos y minimos totales[0] y por bloques[i] de los valores calculados
"""
def CalculosVectoresAgregados(df):
    AVG_Altitud = []
    MAX_Altitud = []
    MIN_Altitud = []
    
    AVG_Velocidad = []
    MAX_Velocidad = []
    MIN_Velocidad = []
    
    AVG_Ritmo = []
    MAX_Ritmo = []
    MIN_Ritmo = []
    
    AVG_FrecuenciaCardiaca = []
    MAX_FrecuenciaCardiaca = []
    MIN_FrecuenciaCardiaca = []
    
    AVG_Cadencia = []
    MAX_Cadencia = []
    MIN_Cadencia = []
    
    AVG_Temperatura = []
    MAX_Temperatura = []
    MIN_Temperatura = []
    
    AVG_LongitudZancada = []
    MAX_LongitudZancada = []
    MIN_LongitudZancada = []
    
    AVG_Pendiente = []
    MAX_Pendiente = []
    MIN_Pendiente = []
    
    
    if 'AltitudCalculada' in df.columns:
        AVG_Altitud.append(df['AltitudCalculada'].mean())
        MAX_Altitud.append(df['AltitudCalculada'].max())
        MIN_Altitud.append(df['AltitudCalculada'].min())
    else:
        AVG_Altitud.append(np.nan)
        MAX_Altitud.append(np.nan)
        MIN_Altitud.append(np.nan)
            
    if 'VelocidadCalculada' in df.columns:
        AVG_Velocidad.append(df['VelocidadCalculada'].mean())
        MAX_Velocidad.append(df['VelocidadCalculada'].max())
        MIN_Velocidad.append(df['VelocidadCalculada'].min())
    else:
        AVG_Velocidad.append(np.nan)
        MAX_Velocidad.append(np.nan)
        MIN_Velocidad.append(np.nan)
        
    if 'Ritmo' in df.columns:
        AVG_Ritmo.append(df['Ritmo'].mean())
        MAX_Ritmo.append(df['Ritmo'].max())
        MIN_Ritmo.append(df['Ritmo'].min())
    else:
        AVG_Ritmo.append(np.nan)
        MAX_Ritmo.append(np.nan)
        MIN_Ritmo.append(np.nan)
        
    if 'FrecuenciaCardiacaCalculada' in df.columns:
        AVG_FrecuenciaCardiaca.append(df['FrecuenciaCardiacaCalculada'].mean())
        MAX_FrecuenciaCardiaca.append(df['FrecuenciaCardiacaCalculada'].max())
        MIN_FrecuenciaCardiaca.append(df['FrecuenciaCardiacaCalculada'].min())
    else:
        AVG_FrecuenciaCardiaca.append(np.nan)
        MAX_FrecuenciaCardiaca.append(np.nan)
        MIN_FrecuenciaCardiaca.append(np.nan)
            
    if 'CadenciaCalculada' in df.columns:
        AVG_Cadencia.append(df['CadenciaCalculada'].mean())
        MAX_Cadencia.append(df['CadenciaCalculada'].max())
        MIN_Cadencia.append(df['CadenciaCalculada'].min())
    else:
        AVG_Cadencia.append(np.nan)
        MAX_Cadencia.append(np.nan)
        MIN_Cadencia.append(np.nan)
            
    if 'TemperaturaAmbiente' in df.columns:
        AVG_Temperatura.append(df['TemperaturaAmbiente'].mean())
        MAX_Temperatura.append(df['TemperaturaAmbiente'].max())
        MIN_Temperatura.append(df['TemperaturaAmbiente'].min())
    else:
        AVG_Temperatura.append(np.nan)
        MAX_Temperatura.append(np.nan)
        MIN_Temperatura.append(np.nan)
       
    if 'LongitudZancada' in df.columns:
        AVG_LongitudZancada.append(df['LongitudZancada'].mean())
        MAX_LongitudZancada.append(df['LongitudZancada'].max())
        MIN_LongitudZancada.append(df['LongitudZancada'].min())
    else:
        AVG_LongitudZancada.append(np.nan)
        MAX_LongitudZancada.append(np.nan)
        MIN_LongitudZancada.append(np.nan)
        
    if 'Pendiente' in df.columns:
        AVG_Pendiente.append(df['Pendiente'].mean())
        MAX_Pendiente.append(df['Pendiente'].max())
        MIN_Pendiente.append(df['Pendiente'].min())
    else:
        AVG_Pendiente.append(np.nan)
        MAX_Pendiente.append(np.nan)
        MIN_Pendiente.append(np.nan)
        
        
    for i in range(int(df['Bloque'].min()), int(df['Bloque'].max())+1):
        if 'AltitudCalculada' in df.columns:
            AVG_Altitud.append(df[df['Bloque']==i]['AltitudCalculada'].mean())
            MAX_Altitud.append(df[df['Bloque']==i]['AltitudCalculada'].max())
            MIN_Altitud.append(df[df['Bloque']==i]['AltitudCalculada'].min())     
        else:
            AVG_Altitud.append(np.nan)
            MAX_Altitud.append(np.nan)
            MIN_Altitud.append(np.nan)
                
        if 'VelocidadCalculada' in df.columns:
            AVG_Velocidad.append(df[df['Bloque']==i]['VelocidadCalculada'].mean())
            MAX_Velocidad.append(df[df['Bloque']==i]['VelocidadCalculada'].max())
            MIN_Velocidad.append(df[df['Bloque']==i]['VelocidadCalculada'].min())
        else:
            AVG_Velocidad.append(np.nan)
            MAX_Velocidad.append(np.nan)
            MIN_Velocidad.append(np.nan)
            
        if 'Ritmo' in df.columns:
            AVG_Ritmo.append(df[df['Bloque']==i]['Ritmo'].mean())
            MAX_Ritmo.append(df[df['Bloque']==i]['Ritmo'].max())
            MIN_Ritmo.append(df[df['Bloque']==i]['Ritmo'].min())      
        else:
            AVG_Ritmo.append(np.nan)
            MAX_Ritmo.append(np.nan)
            MIN_Ritmo.append(np.nan)
            
        if 'FrecuenciaCardiacaCalculada' in df.columns:
            AVG_FrecuenciaCardiaca.append(df[df['Bloque']==i]['FrecuenciaCardiacaCalculada'].mean())
            MAX_FrecuenciaCardiaca.append(df[df['Bloque']==i]['FrecuenciaCardiacaCalculada'].max())
            MIN_FrecuenciaCardiaca.append(df[df['Bloque']==i]['FrecuenciaCardiacaCalculada'].min())      
        else:
            AVG_FrecuenciaCardiaca.append(np.nan)
            MAX_FrecuenciaCardiaca.append(np.nan)
            MIN_FrecuenciaCardiaca.append(np.nan)
                
        if 'CadenciaCalculada' in df.columns:
            AVG_Cadencia.append(df[df['Bloque']==i]['CadenciaCalculada'].mean())
            MAX_Cadencia.append(df[df['Bloque']==i]['CadenciaCalculada'].max())
            MIN_Cadencia.append(df[df['Bloque']==i]['CadenciaCalculada'].min())
        else:
            AVG_Cadencia.append(np.nan)
            MAX_Cadencia.append(np.nan)
            MIN_Cadencia.append(np.nan)
                
        if 'TemperaturaAmbiente' in df.columns:
            AVG_Temperatura.append(df[df['Bloque']==i]['TemperaturaAmbiente'].mean())
            MAX_Temperatura.append(df[df['Bloque']==i]['TemperaturaAmbiente'].max())
            MIN_Temperatura.append(df[df['Bloque']==i]['TemperaturaAmbiente'].min())        
        else:
            AVG_Temperatura.append(np.nan)
            MAX_Temperatura.append(np.nan)
            MIN_Temperatura.append(np.nan)
        
        if 'LongitudZancada' in df.columns:
            AVG_LongitudZancada.append(df[df['Bloque']==i]['LongitudZancada'].mean())
            MAX_LongitudZancada.append(df[df['Bloque']==i]['LongitudZancada'].max())
            MIN_LongitudZancada.append(df[df['Bloque']==i]['LongitudZancada'].min())        
        else:
            AVG_LongitudZancada.append(np.nan)
            MAX_LongitudZancada.append(np.nan)
            MIN_LongitudZancada.append(np.nan)    
    
        if 'Pendiente' in df.columns:
            AVG_Pendiente.append(df[df['Bloque']==i]['Pendiente'].mean())
            MAX_Pendiente.append(df[df['Bloque']==i]['Pendiente'].max())
            MIN_Pendiente.append(df[df['Bloque']==i]['Pendiente'].min())        
        else:
            AVG_Pendiente.append(np.nan)
            MAX_Pendiente.append(np.nan)
            MIN_Pendiente.append(np.nan) 
        
        return AVG_Altitud, MAX_Altitud, MIN_Altitud, \
                AVG_Velocidad, MAX_Velocidad, MIN_Velocidad, \
                AVG_Ritmo, MAX_Ritmo, MIN_Ritmo, \
                AVG_FrecuenciaCardiaca, MAX_FrecuenciaCardiaca, MIN_FrecuenciaCardiaca, \
                AVG_Cadencia, MAX_Cadencia, MIN_Cadencia, \
                AVG_Temperatura, MAX_Temperatura, MIN_Temperatura, \
                AVG_LongitudZancada, MAX_LongitudZancada, MIN_LongitudZancada, \
                AVG_Pendiente, MAX_Pendiente , MIN_Pendiente
                
                
    
def HitosKilometricos(df):
    """
        UBICACION DE HITOS KILOMETRICOS
        Para la representacion en graficas de los puntos de inicio, fin y kilometros se crean listas que almacenan las coordenadas, tiempo total
        transcurrido, tiempo sin pausas o distancia.
        La posicion [0] en las listas corresponde a el punto de inicio de la actividad.
        La posicion [n] en las listas corresponde a el punto de finalizacion de la actividad.
        Las posiciones [1] a [n-1] se corresponden con la ubicacion de los puntos kilometricos.
    """
    LatitudKm = []
    LongitudKm = []
    TiempoTotalKm = []
    TiempoActividadKm = []
    MinDistanciaKm = []
    LatitudKm.append(df.loc[df.index.min() == df.index, ['Latitud']].min()[0])
    LongitudKm.append(df.loc[df.index.min() == df.index, ['Longitud']].min()[0])
    TiempoTotalKm.append(df.loc[df.index.min() == df.index, ['TiempoTotal']].min()[0])
    TiempoActividadKm.append(df.loc[df.index.min() == df.index, ['TiempoActividad']].min()[0])
    MinDistanciaKm.append(df.loc[df.index.min() == df.index, ['DistanciaAcumulada']].min()[0])
    for km in range(1, floor(df['DistanciaAcumulada'].max()/1000)+1):
        LatitudKm.append(df.loc[df[df['DistanciaAcumulada'] >= km*1000].index.min() == df.index, ['Latitud']].min()[0])
        LongitudKm.append(df.loc[df[df['DistanciaAcumulada'] >= km*1000].index.min() == df.index, ['Longitud']].min()[0])
        TiempoTotalKm.append(df.loc[df[df['DistanciaAcumulada'] >= km*1000].index.min() == df.index, ['TiempoTotal']].min()[0])
        TiempoActividadKm.append(df.loc[df[df['DistanciaAcumulada'] >= km*1000].index.min() == df.index, ['TiempoActividad']].min()[0])
        MinDistanciaKm.append(df.loc[df[df['DistanciaAcumulada'] >= km*1000].index.min() == df.index, ['DistanciaAcumulada']].min()[0])
    LatitudKm.append(df.loc[df.index.max() == df.index, ['Latitud']].min()[0])
    LongitudKm.append(df.loc[df.index.max() == df.index, ['Longitud']].min()[0])
    TiempoTotalKm.append(df.loc[df.index.max() == df.index, ['TiempoTotal']].min()[0])
    TiempoActividadKm.append(df.loc[df.index.max() == df.index, ['TiempoActividad']].min()[0])
    MinDistanciaKm.append(df.loc[df.index.max() == df.index, ['DistanciaAcumulada']].min()[0])
    CoordenadasHitosKm = list(zip(LatitudKm, LongitudKm))

    return CoordenadasHitosKm, TiempoTotalKm, TiempoActividadKm, MinDistanciaKm



def HitosPausas(df):
    """
        UBICACION DE HITOS POR PAUSAS TEMPORALES
    """
    LatitudPausas = []
    LongitudPausas = []
    DistanciasPausas = []
    TiempoTotalPausas = []
    TiempoActividadPausas = []
    
    df['LatitudAnterior'] = df['Latitud'].shift().fillna(df['Latitud'])
    df['LongitudAnterior'] = df['Longitud'].shift().fillna(df['Longitud'])
    df['HoraMuestra'] = df.index
    df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(0)
    
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()
    
    for index, row in df.iterrows():
        if row['DeltaTiempo'].total_seconds() > FrecuenciaMuestreo:
            DistanciasPausas.append(row['DistanciaAcumulada'])
            TiempoTotalPausas.append(row['TiempoTotal']-row['DeltaTiempo'])
            TiempoActividadPausas.append(row['TiempoActividad'])
            LatitudPausas.append(row['LatitudAnterior'])
            LongitudPausas.append(row['LongitudAnterior'])
    CoordenadasPausas = list(zip(LatitudPausas, LongitudPausas))
    
    return CoordenadasPausas, TiempoTotalPausas, TiempoActividadPausas, DistanciasPausas



def TablaParcialesKilometricos(df):
    """
        PARCIALES KILOMETRICOS | Strava
        Calculo de valores medios por tramos predefinidos
    """
    TramoDistancia = 1000
    TramoParcial = []
    DistanciaTramo = []
    DistanciaTramoMin = []
    DistanciaTramoMax = []
    AVG_Velocidad_Tramo = []
    AVG_Ritmo_Tramo = []
    AVG_FrecuenciaCardiaca_Tramo = []
    AVG_Cadencia_Tramo = []
    SUM_DesnivelAcumulado_Tramo = []
    
    for index, row in df.iterrows():
        Tramo = ceil(row['DistanciaAcumulada']/TramoDistancia)
        df.at[index,'Tramo'] = Tramo
    
    for i in range(floor(df['DistanciaAcumulada'].max()/(df['DistanciaAcumulada'].max()-1)), ceil(df['DistanciaAcumulada'].max()/TramoDistancia)+1):
        TramoParcial.append(i)
        DistanciaTramo.append(df[df['Tramo']==i]['DistanciaAcumulada'].max()-df[df['Tramo']==i]['DistanciaAcumulada'].min())
        DistanciaTramoMin.append(df[df['Tramo']==i]['DistanciaAcumulada'].min())
        DistanciaTramoMax.append(df[df['Tramo']==i]['DistanciaAcumulada'].max())
        AVG_Velocidad_Tramo.append(round(df[df['Tramo']==i]['VelocidadCalculada'].mean(), 1))
        AVG_Ritmo_Tramo.append(df[df['Tramo']==i]['Ritmo'].mean())
        AVG_FrecuenciaCardiaca_Tramo.append(round(df[df['Tramo']==i]['FrecuenciaCardiaca'].mean()))
        AVG_Cadencia_Tramo.append(round(df[df['Tramo']==i]['Cadencia'].mean()))
        SUM_DesnivelAcumulado_Tramo.append(round(df[df[df['Tramo']==i].index.max()==df.index]['AltitudCalculada'][0]-df[df[df['Tramo']==i].index.min()==df.index]['AltitudCalculada'][0]))
    df = df.drop('Tramo', 1)
    
    dfTramosKm = pd.DataFrame.from_dict({'Tramo': TramoParcial,
                                         'TramoKm': None,
                                         'Distancia': DistanciaTramo,
                                         'DistanciaMin': DistanciaTramoMin,
                                         'DistanciaMax': DistanciaTramoMax,
                                         'Velocidad': AVG_Velocidad_Tramo,
                                         'Ritmo': AVG_Ritmo_Tramo,
                                         'FrecuenciaCardiaca': AVG_FrecuenciaCardiaca_Tramo,
                                         'Cadencia': AVG_Cadencia_Tramo,
                                         'DesnivelAcumulado': SUM_DesnivelAcumulado_Tramo})
    dfTramosKm['x'] = dfTramosKm['DistanciaMin'] + dfTramosKm['Distancia']/2
    dfTramosKm['y'] = dfTramosKm['Velocidad']/2    
    
    for index, row in dfTramosKm.iterrows(): 
        if row.Tramo == dfTramosKm.Tramo.max():
            if row.DistanciaMax < (row.Tramo * TramoDistancia)-(TramoDistancia/100):
                TramoKm = str(round(row.DistanciaMax/TramoDistancia, 2))
            else:
                TramoKm = str(row.Tramo)
        else:
            TramoKm = str(row.Tramo)
        dfTramosKm.at[index,'TramoKm'] = TramoKm
        
    return dfTramosKm


def TablaParcialesPausas(df):
    """
        PARCIALES POR PAUSAS
        Calculo de valores medios por pausas de la actividad
    """
    TramoPausa = []
    DistanciaPausa = []
    DistanciaPausaMin = []
    DistanciaPausaMax = []
    AVG_Velocidad_Pausa = []
    AVG_Ritmo_Pausa = []
    AVG_FrecuenciaCardiaca_Pausa = []
    AVG_Cadencia_Pausa = []
    SUM_DesnivelAcumulado_Pausa = []
    
    for i in range(int(df['Bloque'].min()), int(df['Bloque'].max())+1):
        TramoPausa.append(i)
        DistanciaPausa.append(df[df['Bloque']==i]['DistanciaAcumulada'].max()-df[df['Bloque']==i]['DistanciaAcumulada'].min())
        DistanciaPausaMin.append(df[df['Bloque']==i]['DistanciaAcumulada'].min())
        DistanciaPausaMax.append(df[df['Bloque']==i]['DistanciaAcumulada'].max())
        AVG_Velocidad_Pausa.append(round(df[df['Bloque']==i]['VelocidadCalculada'].mean(), 1))
        AVG_Ritmo_Pausa.append(df[df['Bloque']==i]['Ritmo'].mean())
        AVG_FrecuenciaCardiaca_Pausa.append(round(df[df['Bloque']==i]['FrecuenciaCardiaca'].mean()))
        AVG_Cadencia_Pausa.append(round(df[df['Bloque']==i]['Cadencia'].mean()))
        SUM_DesnivelAcumulado_Pausa.append(round(df[df[df['Bloque']==i].index.max()==df.index]['AltitudCalculada'][0]-df[df[df['Bloque']==i].index.min()==df.index]['AltitudCalculada'][0]))  
    
    dfTramosPausas = pd.DataFrame.from_dict({'Tramo': TramoPausa,
                                             'TramoKm': np.divide(DistanciaPausa, 1000).round(2).astype(str),
                                             'Distancia': DistanciaPausa,
                                             'DistanciaMin': DistanciaPausaMin,
                                             'DistanciaMax': DistanciaPausaMax,
                                             'Velocidad': AVG_Velocidad_Pausa,
                                             'Ritmo': AVG_Ritmo_Pausa,
                                             'FrecuenciaCardiaca': AVG_FrecuenciaCardiaca_Pausa,
                                             'Cadencia': AVG_Cadencia_Pausa,
                                             'DesnivelAcumulado': SUM_DesnivelAcumulado_Pausa})
    dfTramosPausas['x'] = dfTramosPausas['DistanciaMin'] + dfTramosPausas['Distancia']/2
    dfTramosPausas['y'] = dfTramosPausas['Velocidad']/2 
    
    return dfTramosPausas


def TablaZonasCardiacas(FCMax, FCRep, df):
    # Creacion de datos auxilares
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()
    df['HoraMuestra'] = df.index
    df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(0)

    """
        Definicion de 5 zonas cardiacas y calculo de %en cada zona
    """
    ZonasIntensidad = {'Z1':[0.5, 0.6], 'Z2':[0.6, 0.7], 'Z3':[0.7, 0.8], 'Z4':[0.8, 0.9], 'Z5':[0.9, 1]} #Intensidad
    
    # Creacion de un diccionario 
    ZonasCardiacas = {Z:[floor(FormulaKarvonen(FCMax, FCRep, ZonasIntensidad[Z][0])), floor(FormulaKarvonen(FCMax, FCRep, ZonasIntensidad[Z][1]))] for Z in ZonasIntensidad.keys()}
           
    for index, row in df.iterrows():
        for k, v in ZonasCardiacas.items():
            if row['FrecuenciaCardiacaCalculada'] >= v[0] and row['FrecuenciaCardiacaCalculada'] < v[1]:
                ZonaFC = k        
        if row['FrecuenciaCardiacaCalculada'] >= ZonasCardiacas['Z5'][1]:
            ZonaFC = 'Z5'
        if row['FrecuenciaCardiacaCalculada'] < ZonasCardiacas['Z1'][0]:
            ZonaFC = '-'    
        df.at[index,'ZonaFC'] = ZonaFC    
        
    dfTiempoZonasFC = df[df['DeltaTiempo'] == datetime.timedelta(seconds= FrecuenciaMuestreo)][['ZonaFC', 'DeltaTiempo']].groupby('ZonaFC').sum().reset_index()
    dfTiempoZonasFC['PorcentajeTiempo'] = (dfTiempoZonasFC['DeltaTiempo']/np.timedelta64(1, 's'))/(dfTiempoZonasFC['DeltaTiempo'].sum()/np.timedelta64(1, 's'))

    return dfTiempoZonasFC


def IdentificacionTipoActividad(df, Type='Actividad'):
    """
        Esta funcion recibe por parametros el tipo de actividad leido del fichero de origen GPX y el propio DataFrame.
        Si el tipo de actividad leido no aporta suficiente informacion como para saber a que deporte se corresponden los datos, se procede
        a analizar la informacion contenida en el DataFrame.
    """
    # Valores por defecto
    TipoActividad = 'NoIdentificada'
    SubTipoActividad = 'NoIdentificada'

    # Tipos de etiquetas de actividad Strava  
    CiclismoStrava = ['Ride', 'E-Bike Ride']
    RunningStrava = ['Run']
    TrailRunningStrava = []
    NatacionStrava = ['Swim']
    SenderismoStrava = ['Walk', 'Hike']
    ElipticaStrava = ['Elliptical']
    EscalerasStrava = ['Stair Stepper']
    OtrosStrava = ['Alpine Ski', 'Backcountry Ski', 'Canoe', 'Crossfit', 'Handcycle', 'Ice Skate', 'Inline Skate', \
                   'Kayak', 'Kitesurf Session', 'Nordic Ski', 'Rock Climb', 'Roller Ski', 'Row', 'Snowboard', 'Snowshoe', 'Stand Up Paddle', 'Surf', \
                   'Virtual Ride', 'Virtual Run', 'Weight Training', 'Windsurf Session', 'Wheelchair', 'Workout', 'Yoga']

    # Tipos de etiquetas de actividad Garmin
    CiclismoGarmin = []
    RunningGarmin = []
    TrailRunningGarmin = []
    NatacionGarmin = []
    SenderismoGarmin = []
    ElipticaGarmin = []
    EscalerasGarmin = []
    OtrosGarmin = []
    
    # Tipos de etiquetas de actividad genericos
    CiclismoGenerico = ['Ciclismo', 'MTB']
    RunningGenerico = ['Running']
    TrailRunningGenerico = ['Trail running']
    NatacionGenerico = []
    SenderismoGenerico = []
    ElipticaGenerico = []
    EscalerasGenerico = []
    OtrosGenerico = []
    
    # Tipos de etiquetas totales
    Ciclismo = CiclismoGenerico.upper() + CiclismoStrava.upper() + CiclismoGarmin.upper()
    Ciclismo = Ciclismo.unique()
    Running = RunningGenerico.upper() + RunningStrava.upper() + RunningGarmin.upper()
    Running = Running.unique()
    TrailRunning = TrailRunningGenerico.upper() + TrailRunningStrava.upper() + TrailRunningGarmin.upper()
    TrailRunning = TrailRunning.unique()
    Natacion = NatacionGenerico.upper() + NatacionStrava.upper() + NatacionGarmin.upper()
    Natacion = Natacion.unique()
    Senderismo = SenderismoGenerico.upper() + SenderismoStrava.upper() + SenderismoGarmin.upper()
    Senderismo = Senderismo.unique()
    Eliptica = ElipticaGenerico.upper() + ElipticaStrava.upper() + ElipticaGarmin.upper()
    Eliptica = Eliptica.unique()
    Escaleras = EscalerasGenerico.upper() + EscalerasStrava.upper() + EscalerasGarmin.upper()
    Escaleras = Escaleras.unique()
    Otros = OtrosGenerico.upper() + OtrosStrava.upper() + OtrosGarmin.upper()
    Otros = Otros.unique()

    # Calculo de las variables que definen el tipo y subtipo de actividad
    if not DeteccionVariables(df, 'Coordenadas'):
        TipoActividad = 'Indoor'
    else: 
        LatitudInicio, LongitudInicio = df.loc[df.index.min() == df.index, ['Latitud']].min()[0], df.loc[df.index.min() == df.index, ['Longitud']].min()[0]
        LatitudFin, LongitudFin = df.loc[df.index.max() == df.index, ['Latitud']].min()[0], df.loc[df.index.max() == df.index, ['Longitud']].min()[0]
        
    Inicio, Fin = df.index.min(), df.index.max()
    FechaInicio, FechaFin = Inicio.strftime("%d/%m/%Y"), Fin.strftime("%d/%m/%Y")
    HoraInicio, HoraFin = Inicio.strftime("%H:%M:%S"), Fin.strftime("%H:%M:%S")
        
    TiempoTotalSegundos = df['TiempoTotal'].max().total_seconds()
    TiempoActividadSegundos = df['TiempoActividad'].max().total_seconds()
    TiempoPausadoSegundos = TiempoTotalSegundos - TiempoActividadSegundos
    NumeroPausas = int(df['Bloque'].max())
    RatioActivoPausado = TiempoActividadSegundos / TiempoTotalSegundos

    DistanciaActividad = df['DistanciaAcumulada'].max()
    
    DesnivelPositivo = df['DesnivelPositivoAcumulado'].max()
    DesnivelPorKilometro = ((df['DesnivelPositivoAcumulado'].max() + df['DesnivelNegativoAcumulado'].max())/df['DistanciaAcumulada'].max())*1000 #Unidades m/km
  
    VelocidadMedia = df['VelocidadCalculada'].mean()*3.6 #Unidades km/h
    VelocidadMediaAscenso = df[df['Pendiente']>=0]['VelocidadCalculada'].mean()*3.6 #Unidades km/h
    VelocidadMediaDescenso = df[df['Pendiente']<=0]['VelocidadCalculada'].mean()*3.6 #Unidades km/h
    VelocidadPercentil90 =  np.percentile(df['VelocidadCalculada'], 90)*3.6
    RatioVelocidadDesnivel = VelocidadMediaAscenso / VelocidadMediaDescenso
    
    # Identificacion del tipo de actividad
    if VelocidadPercentil90 > 20 and RatioVelocidadDesnivel > 2:
        TipoActividad = 'Ciclismo'
    elif VelocidadPercentil90 > 5:
        if DesnivelPorKilometro < 40:
            TipoActividad = 'Running'
            # Identificacion del subtipo de actividad
            if NumeroPausas > 5 and DistanciaActividad < 5000 and DesnivelPorKilometro < 15 and VelocidadMedia > 14 and VelocidadMedia < 30:
                if NumeroPausas/(DistanciaActividad/1000) > 5:
                    SubTipoActividad = 'SeriesCortas'
                elif NumeroPausas/(DistanciaActividad/1000) > 1:
                    SubTipoActividad = 'SeriesMedias'
                elif NumeroPausas/(DistanciaActividad/1000) > 0.2:
                    SubTipoActividad = 'SeriesLargas'
        else:
            TipoActividad = 'TrailRunning'
    else:
        TipoActividad = 'Senderismo'

    return TipoActividad, SubTipoActividad

        

       
def LecturaBBDDActividades(DirectorioBase, BBDD):
    """
        Funcion que lee el fichero de actividades ubicado en la ruta pasada por parametros
    """
    if os.path.exists(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv')):
            DataFrameBBDDActividades = pd.read_csv(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv'), sep= ';', encoding = 'utf-8')
    else:
            DataFrameBBDDActividades = pd.DataFrame(columns=['NombreFichero', 'NombreActividad', 'TipoActividad', 'Fecha', 'Hora', 'LatitudInicio', 'LongitudInicio', \
                                                            'Distancia', 'TiempoTotal', 'TiempoActividad', 'TramosPausas', \
                                                            'FrecuenciaCardiacaMedia', 'FrecuenciaCardiacaMaxima', 'FrecuenciaCardiacaMinima', \
                                                            'CadenciaMedia', 'CadenciaMaxima', 'CadenciaMinima', \
                                                            'TemperaturaMedia', 'TemperaturaMaxima', 'TemperaturaMinima', \
                                                            'AltitudMaxima', 'AltitudMinima', 'DesnivelPositivo', 'DesnivelNegativo', 'DesnivelPorKilometro', \
                                                            'VelocidadMedia', 'VelocidadMaxima', 'VelocidadPercentil90', 'VelocidadMinima', 'VelocidadPercentil10', 'VelocidadMediaAscenso', 'VelocidadMediaDescenso', 'RatioVelocidadDesnivel', \
                                                            'TipoActividadCalculado'])
    return DataFrameBBDDActividades


def AnalisisActividadActual(NombreFichero, NombreActividad, TipoActividad, df):
    """
        Funcion que recibe el nombre de un fichero y el DataFrame correspondente, extrae los datos resumidos
        de la actividad y crea un DataFrame con el regitro correspondiente a estos datos.
        Falta la parte de asignacion del tipo de actividad
    """
    NombreFichero = NombreFichero
    Fecha = df.index.min().date().strftime('%Y/%m/%d')
    Hora = df.index.min().time().strftime('%H:%M:%S')
    
    LatitudInicio = str(df.loc[df.index.min() == df.index, ['Latitud']].min()[0])
    LongitudInicio = str(df.loc[df.index.min() == df.index, ['Longitud']].min()[0])
    
    if (LatitudInicio != np.nan and LongitudInicio != np.nan):
        Distancia = int(round(df['DistanciaAcumulada'].max()))
    else:
        Distancia = 0
    
    TiempoTotal = FormateoTiempos(df['TiempoTotal'].max(), 'Z')
    TiempoActividad = FormateoTiempos(df['TiempoActividad'].max(), 'Z')
    TramosPausas = int(df['Bloque'].max())
    
    if df['FrecuenciaCardiacaCalculada'].max() != df['FrecuenciaCardiacaCalculada'].min() and df['FrecuenciaCardiacaCalculada'].mean() != 0:
        FrecuenciaCardiacaMedia = int(round(df['FrecuenciaCardiacaCalculada'].mean()))
        FrecuenciaCardiacaMaxima = int(round(df['FrecuenciaCardiacaCalculada'].max()))
        FrecuenciaCardiacaMinima = int(round(df['FrecuenciaCardiacaCalculada'].min()))
    else:
        FrecuenciaCardiacaMedia = 0
        FrecuenciaCardiacaMaxima = 0
        FrecuenciaCardiacaMinima = 0
    
    if df['CadenciaCalculada'].max() != df['CadenciaCalculada'].min() and df['CadenciaCalculada'].mean() != 0:
        CadenciaMedia = int(round(df['CadenciaCalculada'].mean()))
        CadenciaMaxima = int(round(df['CadenciaCalculada'].max()))
        CadenciaMinima = int(round(df['CadenciaCalculada'].min()))
    else:
        CadenciaMedia = 0
        CadenciaMaxima = 0
        CadenciaMinima = 0
        
    if df['TemperaturaAmbiente'].max() != df['TemperaturaAmbiente'].min() and df['TemperaturaAmbiente'].mean() != 0:
        TemperaturaMedia = int(round(df['TemperaturaAmbiente'].mean()))
        TemperaturaMaxima = int(round(df['TemperaturaAmbiente'].max()))
        TemperaturaMinima = int(round(df['TemperaturaAmbiente'].min()))
    else:
        TemperaturaMedia = 0
        TemperaturaMaxima = 0
        TemperaturaMinima = 0
    
    if df['AltitudCalculada'].max() != df['AltitudCalculada'].min() and df['AltitudCalculada'].mean() != 0:
        AltitudMaxima = int(round(df['AltitudCalculada'].max()))
        AltitudMinima = int(round(df['AltitudCalculada'].min()))
        DesnivelPositivo = int(round(df['DesnivelPositivoAcumulado'].max()))
        DesnivelNegativo = int(round(df['DesnivelNegativoAcumulado'].max()))
        DesnivelPorKilometro = int(round(((df['DesnivelPositivoAcumulado'].max() + df['DesnivelNegativoAcumulado'].max())/df['DistanciaAcumulada'].max())*1000)) #Unidades m/km
    else:
        AltitudMaxima = 0
        AltitudMinima = 0
        DesnivelPositivo = 0
        DesnivelNegativo = 0
        DesnivelPorKilometro = 0
    
    if df['VelocidadCalculada'].max() != df['VelocidadCalculada'].min() and df['VelocidadCalculada'].mean() != 0:
        VelocidadMedia = round(df['VelocidadCalculada'].mean()*3.6, 1) #Unidades km/h
        VelocidadMaxima = round(df['VelocidadCalculada'].max()*3.6, 1) #Unidades km/h
        VelocidadPercentil90 =  round(np.percentile(df['VelocidadCalculada'], 90)*3.6, 1) #Eliminacion de outliers
        VelocidadMinima = round(df['VelocidadCalculada'].min()*3.6, 1) #Unidades km/h
        VelocidadPercentil10 =  round(np.percentile(df['VelocidadCalculada'], 10)*3.6, 1) #Eliminacion de outliers
        VelocidadMediaAscenso = round(df[df['Pendiente']>0]['VelocidadCalculada'].mean()*3.6, 1) #Unidades km/h
        VelocidadMediaDescenso = round(df[df['Pendiente']<0]['VelocidadCalculada'].mean()*3.6, 1) #Unidades km/h
        RatioVelocidadDesnivel = round(VelocidadMediaAscenso/VelocidadMediaDescenso, 1)
    else:
        VelocidadMedia = 0
        VelocidadMaxima = 0
        VelocidadPercentil90 = 0
        VelocidadMinima = 0
        VelocidadPercentil10 =  0
        VelocidadMediaAscenso = 0
        VelocidadMediaDescenso = 0
        RatioVelocidadDesnivel = 0

    # Creacion del registro correspondiente a la actividad actual
    DataFrameActividadActual = pd.DataFrame({    
        'NombreFichero':NombreFichero,
        'NombreActividad':NombreActividad, 
        'TipoActividad':TipoActividad,
        'Fecha':Fecha,
        'Hora':Hora,
        'LatitudInicio':LatitudInicio,
        'LongitudInicio':LongitudInicio,
        'Distancia':Distancia,
        'TiempoTotal':TiempoTotal,
        'TiempoActividad':TiempoActividad,
        'TramosPausas':TramosPausas,
        'FrecuenciaCardiacaMedia':FrecuenciaCardiacaMedia,
        'FrecuenciaCardiacaMaxima':FrecuenciaCardiacaMaxima,
        'FrecuenciaCardiacaMinima':FrecuenciaCardiacaMinima,
        'CadenciaMedia':CadenciaMedia,
        'CadenciaMaxima':CadenciaMaxima,
        'CadenciaMinima':CadenciaMinima,
        'TemperaturaMedia':TemperaturaMedia,
        'TemperaturaMaxima':TemperaturaMaxima,
        'TemperaturaMinima':TemperaturaMinima,
        'AltitudMaxima':AltitudMaxima,
        'AltitudMinima':AltitudMinima,
        'DesnivelPositivo':DesnivelPositivo,
        'DesnivelNegativo':DesnivelNegativo,
        'DesnivelPorKilometro':DesnivelPorKilometro,
        'VelocidadMedia':VelocidadMedia,
        'VelocidadMaxima':VelocidadMaxima,
        'VelocidadPercentil90':VelocidadPercentil90,
        'VelocidadMinima':VelocidadMinima,
        'VelocidadPercentil10':VelocidadPercentil10,
        'VelocidadMediaAscenso':VelocidadMediaAscenso,
        'VelocidadMediaDescenso':VelocidadMediaDescenso,
        'RatioVelocidadDesnivel':RatioVelocidadDesnivel,
        'TipoActividadCalculado':np.nan}, index= [0])   
    return DataFrameActividadActual
    
    
def EscrituraBBDDActividades(DirectorioBase, BBDD, DataFrameActividadActual, DataFrameBBDDActividades):
    """
        Funcion que recibe un directorio y 2 DataFrames, los concatena/actualiza y los graba en el directorio
    """
    # Insercion o borrado/insercion
    if DataFrameActividadActual['NombreFichero'][0]+'|'+DataFrameActividadActual['Fecha'][0]+'|'+DataFrameActividadActual['Hora'][0] not in list(DataFrameBBDDActividades['NombreFichero']+'|'+DataFrameBBDDActividades['Fecha']+'|'+DataFrameBBDDActividades['Hora']):
        DataFrameBBDDActividades =  pd.concat([DataFrameBBDDActividades, DataFrameActividadActual], sort=False)
    else:
        DataFrameBBDDActividades = DataFrameBBDDActividades[(DataFrameBBDDActividades['NombreFichero']!=DataFrameActividadActual['NombreFichero'][0]) | (DataFrameBBDDActividades['Fecha']!=DataFrameActividadActual['Fecha'][0]) | (DataFrameBBDDActividades['Hora']!=DataFrameActividadActual['Hora'][0])]
        DataFrameBBDDActividades =  pd.concat([DataFrameBBDDActividades, DataFrameActividadActual], sort=False)
    
    # Sobreescritura del fichero
    DataFrameBBDDActividades.to_csv(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv'), sep= ';', index= False, header= True, encoding='utf-8')
    
    

def DeteccionVariables(df, variable):
    """
        Funcion que recibe el DataFrame correspondiente a una actividad y una variable y devuelve los valores 1 o 0
        dependiendo de si esa variable contiene valores para mostrar.
        Valores de variable validos:
            - Coordenadas
            - FrecuenciaCardiaca
            - Velocidad
            - Altitud
            - Cadencia
            - Temperatura
            - DesnivelPositivoAcumulado
            - DesnivelNegativoAcumulado
            - Pendiente
            - LongitudZancada
    """
    
    # Coordenadas geograficas
    if variable == 'Coordenadas':
        if (df['Latitud'].max() != df['Latitud'].min() or df['Latitud'].mean() != 0) and (df['Longitud'].max() != df['Longitud'].min() or df['Longitud'].mean() != 0):
            ExisteVariable = 1
        else:
            ExisteVariable = 0

    # Frecuencia cardiaca
    if variable == 'FrecuenciaCardiaca':
        if df['FrecuenciaCardiacaCalculada'].max() != df['FrecuenciaCardiacaCalculada'].min() or df['FrecuenciaCardiacaCalculada'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0

    # Velocidad
    if variable == 'Velocidad':
        if df['VelocidadCalculada'].max() != df['VelocidadCalculada'].min() or df['VelocidadCalculada'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0
            
    # Altitud
    if variable == 'Altitud':
        if df['AltitudCalculada'].max() != df['AltitudCalculada'].min() or df['AltitudCalculada'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0
            
    # Cadencia
    if variable == 'Cadencia':
        if df['CadenciaCalculada'].max() != df['CadenciaCalculada'].min() or df['CadenciaCalculada'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0

    # Temperatura
    if variable == 'Temperatura':
        if df['TemperaturaAmbiente'].max() != df['TemperaturaAmbiente'].min() or df['TemperaturaAmbiente'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0 

    # DesnivelPositivoAcumulado
    if variable == 'DesnivelPositivoAcumulado':
        if df['DesnivelPositivoAcumulado'].max() != df['DesnivelPositivoAcumulado'].min() and df['DesnivelPositivoAcumulado'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0         

    # DesnivelNegativoAcumulado
    if variable == 'DesnivelNegativoAcumulado':
        if df['DesnivelNegativoAcumulado'].max() != df['DesnivelNegativoAcumulado'].min() and df['DesnivelNegativoAcumulado'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0 

    # Pendiente
    if variable == 'Pendiente':
        if df['Pendiente'].max() != df['Pendiente'].min() or df['Pendiente'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0
            
    # Longitud de zancada
    if variable == 'LongitudZancada':
        if df['LongitudZancada'].max() != df['LongitudZancada'].min() or df['LongitudZancada'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0

    return ExisteVariable
    
    
def GeneracionCodigoJS(dfAnalisisVariables, VariablePrincipal, LineasAuxiliares):
    """
        Esta funcion recibe por parametro un DataFrame, la variable principal a visualizar y un diccionario con las lineas auxiliares disponibles  y devuelve 
        el listado de botones disponibles, la relacion entre botones y nombres de las graficas a superponer y el codigo JavaScript para realizar las interacciones.
        
        El codigo detecta dinamicamente la existencia de valores representativos para las variables a visualizar. Si la variable no ha sido registrada,
        este campo tendra todos sus registros con valor 0 por defecto, por lo que no se incluirá en el listado de variables a visualizar.
        
        Valores validos de la variable VariablePrincipal: 'FrecuenciaCardiaca', 'Velocidad', 'Altitud', 'Cadencia', 'Temperatura', 'Pendiente', 'DesnivelPositivoAcumulado' y 'LongitudZancada'
        Valores validos de la variable TipoActividad: 'Running', 'TrailRunning', 'MTB', 'Indoor' 
    """

    # Seleccion de las variables relevantes a mostrar
    ListadoVariables = {}

    if DeteccionVariables(dfAnalisisVariables, 'FrecuenciaCardiaca'):
        ListadoVariables.update({'FrecuenciaCardiaca':'FRECUENCIA CARDIACA'})
    if DeteccionVariables(dfAnalisisVariables, 'Velocidad'):
        ListadoVariables.update({'Velocidad':'RITMO'})
    if DeteccionVariables(dfAnalisisVariables, 'Altitud'):
        ListadoVariables.update({'Altitud':'ALTITUD'})
    if DeteccionVariables(dfAnalisisVariables, 'Cadencia'):
        ListadoVariables.update({'Cadencia':'CADENCIA'})
    if DeteccionVariables(dfAnalisisVariables, 'Temperatura'):
        ListadoVariables.update({'Temperatura':'TEMPERATURA'})
    if DeteccionVariables(dfAnalisisVariables, 'Pendiente'):
        ListadoVariables.update({'Pendiente':'PENDIENTE'})
    if DeteccionVariables(dfAnalisisVariables, 'DesnivelPositivoAcumulado'):
        ListadoVariables.update({'DesnivelPositivoAcumulado':'DESNIVEL POSITIVO'})
    if DeteccionVariables(dfAnalisisVariables, 'LongitudZancada'):
        ListadoVariables.update({'LongitudZancada':'LONGITUD ZANCADA'})
        
    
    # Eliminacion del boton principal
    if VariablePrincipal == 'FrecuenciaCardiaca':
        del ListadoVariables['FrecuenciaCardiaca']
    elif VariablePrincipal == 'Velocidad':
        del ListadoVariables['Velocidad']
    elif VariablePrincipal == 'Altitud':
        del ListadoVariables['Altitud']
    elif VariablePrincipal == 'Cadencia':
        del ListadoVariables['Cadencia']
    elif VariablePrincipal == 'Temperatura':
        del ListadoVariables['Temperatura']
    elif VariablePrincipal == 'Pendiente':
        del ListadoVariables['Pendiente']
    elif VariablePrincipal == 'DesnivelPositivoAcumulado':
        del ListadoVariables['DesnivelPositivoAcumulado']
    elif VariablePrincipal == 'LongitudZancada':
        del ListadoVariables['LongitudZancada']
    else:
        print("*** Variable principal no identificada. ***")

    n = 0
    # Creacion de variables de lineas en el orden de los botones detectados
    for i, BotonLista in ListadoVariables.items():
        for j, Plot in LineasAuxiliares.items():
            if i == j:
                if n == 0:
                    linea0 = Plot
                    n = n+1
                elif n == 1:
                    linea1 = Plot
                    n = n+1
                elif n == 2:
                    linea2 = Plot
                    n = n+1
                elif n == 3:
                    linea3 = Plot
                    n = n+1
                elif n == 4:
                    linea4 = Plot
                    n = n+1
                elif n == 5:
                    linea5 = Plot
                    n = n+1
                elif n == 6:
                    linea6 = Plot
                    n = n+1
                elif n == 7:
                    linea7 = Plot
                    n = n+1
                elif n == 8:
                    linea8 = Plot
                    n = n+1
                else:
                    linea9 = Plot
                    n = n+1
    
    
    # Asignacion del codigo JavaScript y la relacion entre lineas y graficas
    ElementosBotones = len(ListadoVariables)
    RelacionLineas = {}
    
    if ElementosBotones <= 0:
        CodigoJS = """ """
        
        RelacionLineas = dict()
        
    elif ElementosBotones == 1:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        """
        
        RelacionLineas = dict(l0=linea0)
        
    elif ElementosBotones == 2:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        """
        RelacionLineas = dict(l0=linea0, l1=linea1)
        
    elif ElementosBotones == 3:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        l2.visible = indexOf.call(checkbox.active,2)>=0;
        """
        
        RelacionLineas = dict(l0=linea0, l1=linea1, l2=linea2)
        
    elif ElementosBotones == 4:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        l2.visible = indexOf.call(checkbox.active,2)>=0;
        l3.visible = indexOf.call(checkbox.active,3)>=0;
        """
        
        RelacionLineas = dict(l0=linea0, l1=linea1, l2=linea2, l3=linea3)
        
    elif ElementosBotones == 5:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        l2.visible = indexOf.call(checkbox.active,2)>=0;
        l3.visible = indexOf.call(checkbox.active,3)>=0;
        l4.visible = indexOf.call(checkbox.active,4)>=0;
        """
        
        RelacionLineas = dict(l0=linea0, l1=linea1, l2=linea2, l3=linea3, l4=linea4)
        
    elif ElementosBotones == 6:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        l2.visible = indexOf.call(checkbox.active,2)>=0;
        l3.visible = indexOf.call(checkbox.active,3)>=0;
        l4.visible = indexOf.call(checkbox.active,4)>=0;
        l5.visible = indexOf.call(checkbox.active,5)>=0;
        """
        
        RelacionLineas = dict(l0=linea0, l1=linea1, l2=linea2, l3=linea3, l4=linea4, l5=linea5)
        
    elif ElementosBotones == 7:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        l2.visible = indexOf.call(checkbox.active,2)>=0;
        l3.visible = indexOf.call(checkbox.active,3)>=0;
        l4.visible = indexOf.call(checkbox.active,4)>=0;
        l5.visible = indexOf.call(checkbox.active,5)>=0;
        l6.visible = indexOf.call(checkbox.active,6)>=0;
        """
        
        RelacionLineas = dict(l0=linea0, l1=linea1, l2=linea2, l3=linea3, l4=linea4, l5=linea5, l6=linea6)
        
    elif ElementosBotones == 8:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        l2.visible = indexOf.call(checkbox.active,2)>=0;
        l3.visible = indexOf.call(checkbox.active,3)>=0;
        l4.visible = indexOf.call(checkbox.active,4)>=0;
        l5.visible = indexOf.call(checkbox.active,5)>=0;
        l6.visible = indexOf.call(checkbox.active,6)>=0;
        l7.visible = indexOf.call(checkbox.active,7)>=0;
        """
        
        RelacionLineas = dict(l0=linea0, l1=linea1, l2=linea2, l3=linea3, l4=linea4, l5=linea5, l6=linea6, l7=linea7)
        
    elif ElementosBotones == 9:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        l2.visible = indexOf.call(checkbox.active,2)>=0;
        l3.visible = indexOf.call(checkbox.active,3)>=0;
        l4.visible = indexOf.call(checkbox.active,4)>=0;
        l5.visible = indexOf.call(checkbox.active,5)>=0;
        l6.visible = indexOf.call(checkbox.active,6)>=0;
        l7.visible = indexOf.call(checkbox.active,7)>=0;
        l8.visible = indexOf.call(checkbox.active,8)>=0;
        """
        
        RelacionLineas = dict(l0=linea0, l1=linea1, l2=linea2, l3=linea3, l4=linea4, l5=linea5, l6=linea6, l7=linea7, l8=linea8)
        
    elif ElementosBotones == 10:
        CodigoJS = """
        var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
        l0.visible = indexOf.call(checkbox.active,0)>=0;
        l1.visible = indexOf.call(checkbox.active,1)>=0;
        l2.visible = indexOf.call(checkbox.active,2)>=0;
        l3.visible = indexOf.call(checkbox.active,3)>=0;
        l4.visible = indexOf.call(checkbox.active,4)>=0;
        l5.visible = indexOf.call(checkbox.active,5)>=0;
        l6.visible = indexOf.call(checkbox.active,6)>=0;
        l7.visible = indexOf.call(checkbox.active,7)>=0;
        l8.visible = indexOf.call(checkbox.active,8)>=0;
        l9.visible = indexOf.call(checkbox.active,9)>=0;
        """
        
        RelacionLineas = dict(l0=linea0, l1=linea1, l2=linea2, l3=linea3, l4=linea4, l5=linea5, l6=linea6, l7=linea7, l8=linea8, l9=linea9)
        
    else:
        print("*** Demasiados elementos a visualizar. Esto va a fallar. ***")

    ListadoBotones = [B for B in ListadoVariables.values()]

    return ListadoBotones, RelacionLineas, CodigoJS



def CreacionDirectoriosProyecto(Root):
    """
        Funcion que recibe el directorio raiz del proyecto y crea la estructura de carpetas 
        necesaria para funcionar si no existiera.
    """
    os.makedirs(os.path.join(Root, 'input'), exist_ok=True)
    os.makedirs(os.path.join(Root, 'input\processed'), exist_ok=True)
    os.makedirs(os.path.join(Root, 'library'), exist_ok=True)
    os.makedirs(os.path.join(Root, 'output'), exist_ok=True)


def CalculoOffsetAltitud(DataFrame):
    """
        Funcion que recibe un dataframe con la informacion de altitud y desniveles
        calculada y devuelve los offset optimos superior e inferior para representar
        la altidud de una manera mas acorde a la realidad.
    """
    # Calculo de desniveles finales
    DesnivelPositivo = DataFrame['DesnivelPositivoAcumulado'].max()
    DesnivelNegativo = DataFrame['DesnivelNegativoAcumulado'].max()
    DesnivelAcumulado = DesnivelPositivo + DesnivelNegativo
    DesnivelPorKilometro = (DesnivelAcumulado/DataFrame['DistanciaAcumulada'].max())*1000
        
    # Factor de achatamiento de la altitud
    if DesnivelPorKilometro > 40:
        OffsetSuperiorAltitud = 0.1
        OffsetInferiorAltitud = 0.03
    else:
        OffsetSuperiorAltitud = 2.5
        OffsetInferiorAltitud = 0.5
        
    return OffsetSuperiorAltitud, OffsetInferiorAltitud


def LimiteEjeY(DataFrame, Metrica, TipoLimite):
    """
        Funcion que recibe como parametros un DataFrame la metrica a visualizar y el
        tipo de limite deseado y devuelve el valor adecuado del eje Y para su visualizacion.
        Valores de Metrica validos:
            - FrecuenciaCardiaca
            - Velocidad
            - Altitud
            - Cadencia
            - Temperatura
            - DesnivelPositivoAcumulado
            - DesnivelNegativoAcumulado
            - Pendiente
            - LongitudZancada
        Valores de TipoLimite validos:
            - Inferior
            - Superior
            
        Esta funcion permite realizar cambios en la distancia entre los limites de los graficos
        de Bokeh y los datos a visualizar modificando unicamente 
    """

    # Frecuencia cardiaca
    if Metrica == 'FrecuenciaCardiaca' and 'FrecuenciaCardiacaCalculada' in DataFrame.columns:
        if TipoLimite == 'Inferior':
            LimiteEjeY = min(DataFrame['FrecuenciaCardiacaCalculada'].min(), 85)
        elif TipoLimite == 'Superior':
            LimiteEjeY = max(DataFrame['FrecuenciaCardiacaCalculada'].max(), 180)
        else:
            LimiteEjeY = np.nan
    
    # Ritmo
    if Metrica == 'Velocidad' and 'VelocidadCalculada' in DataFrame.columns:
        if TipoLimite == 'Inferior':
            LimiteEjeY = DataFrame['VelocidadCalculada'].min()-DataFrame['VelocidadCalculada'].min()*0.1
        elif TipoLimite == 'Superior':
            LimiteEjeY = DataFrame['VelocidadCalculada'].max()+DataFrame['VelocidadCalculada'].max()*0.2
        else:
            LimiteEjeY = np.nan
    
    # Altitud
    if Metrica == 'Altitud' and 'AltitudCalculada' in DataFrame.columns:
        OffsetSuperiorAltitud, OffsetInferiorAltitud = CalculoOffsetAltitud(DataFrame)
        if TipoLimite == 'Inferior':
            LimiteEjeY = DataFrame['AltitudCalculada'].min()-(DataFrame['AltitudCalculada'].max()-DataFrame['AltitudCalculada'].min())*OffsetInferiorAltitud
        elif TipoLimite == 'Superior':
            LimiteEjeY = DataFrame['AltitudCalculada'].max()+(DataFrame['AltitudCalculada'].max()-DataFrame['AltitudCalculada'].min())*OffsetSuperiorAltitud
        else:
            LimiteEjeY = np.nan
    
    # Cadencia
    if Metrica == 'Cadencia' and 'CadenciaCalculada' in DataFrame.columns:
        if TipoLimite == 'Inferior':
            LimiteEjeY = DataFrame['CadenciaCalculada'].min()-(DataFrame['CadenciaCalculada'].max()-DataFrame['CadenciaCalculada'].min())*0.03
        elif TipoLimite == 'Superior':
            LimiteEjeY = DataFrame['CadenciaCalculada'].max()+(DataFrame['CadenciaCalculada'].max()-DataFrame['CadenciaCalculada'].min())*0.1
        else:
            LimiteEjeY = np.nan
    
    # Temperatura
    if Metrica == 'Temperatura' and 'TemperaturaAmbiente' in DataFrame.columns:
        # Calculo de un margen sin datos por tramos
        Rango = DataFrame['TemperaturaAmbiente'].max()-DataFrame['TemperaturaAmbiente'].min()
        if Rango < 1:
            Margen = 2
        elif Rango >= 1 and Rango < 10:
            Margen = (1/Rango)*2
        else:
            Margen = 0.2
        
        if TipoLimite == 'Inferior':
            if DataFrame['TemperaturaAmbiente'].min() > 25:
                LimiteEjeY = DataFrame['TemperaturaAmbiente'].min()-Margen*2
            else:
                LimiteEjeY = min(DataFrame['TemperaturaAmbiente'].min()-Margen, 0)
        elif TipoLimite == 'Superior':
            LimiteEjeY = max(DataFrame['TemperaturaAmbiente'].max()+Margen, 0)
        else:
            LimiteEjeY = np.nan
            
    # Desnivel positivo
    if Metrica == 'DesnivelPositivoAcumulado' and 'DesnivelPositivoAcumulado' in DataFrame.columns:
        if TipoLimite == 'Inferior':
            LimiteEjeY = 0
        elif TipoLimite == 'Superior':
            LimiteEjeY = DataFrame['DesnivelPositivoAcumulado'].max()+DataFrame['DesnivelPositivoAcumulado'].max()*0.05
        else:
            LimiteEjeY = np.nan
    
    # Desnivel negativo | Habilitar cuando se incluya esta grafica en las visualizaciones de Bokeh
    #if Metrica == 'DesnivelNegativoAcumulado' and 'DesnivelNegativoAcumulado' in DataFrame.columns:
    #    if TipoLimite == 'Inferior':
    #        LimiteEjeY = 0
    #    elif TipoLimite == 'Superior':
    #        LimiteEjeY = DataFrame['DesnivelNegativoAcumulado'].max()+DataFrame['DesnivelNegativoAcumulado'].max()*0.05
    #    else:
    #        LimiteEjeY = np.nan
    
    # Pendiente
    if Metrica == 'Pendiente' and 'Pendiente' in DataFrame.columns:
        if TipoLimite == 'Inferior':
            LimiteEjeY = DataFrame['Pendiente'].min()-(DataFrame['Pendiente'].max()-DataFrame['Pendiente'].min())*0.05
        elif TipoLimite == 'Superior':
            LimiteEjeY = DataFrame['Pendiente'].max()+(DataFrame['Pendiente'].max()-DataFrame['Pendiente'].min())*0.05
        else:
            LimiteEjeY = np.nan
    
    # Longitud de zancada
    if Metrica == 'LongitudZancada' and 'LongitudZancada' in DataFrame.columns:
        if TipoLimite == 'Inferior':
            LimiteEjeY = DataFrame['LongitudZancada'].min()-(DataFrame['LongitudZancada'].max()-DataFrame['LongitudZancada'].min())*0.03
        elif TipoLimite == 'Superior':
            LimiteEjeY = DataFrame['LongitudZancada'].max()+(DataFrame['LongitudZancada'].max()-DataFrame['LongitudZancada'].min())*0.1
        else:
            LimiteEjeY = np.nan
        
    return LimiteEjeY