# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 12:22:28 2020

@author: Felix
"""

import pandas as pd
import numpy as np
from math import ceil, floor, radians, pi, log, tan
import datetime
import os
from reverse_geocoder import search as rg_search

from source.common.Funciones_Generales import FormulaKarvonen, FormateoTiempos


def CalculosVectoresAgregados(df):
    """
        MEDIAS, MAXIMOS Y MINIMOS
        Calculo de medias, maximos y minimos totales[0] y por bloques[i] de los valores calculados
    """
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
    
    
    if 'Altitud' in df.columns:
        AVG_Altitud.append(df['Altitud'].mean())
        MAX_Altitud.append(df['Altitud'].max())
        MIN_Altitud.append(df['Altitud'].min())
    else:
        AVG_Altitud.append(np.nan)
        MAX_Altitud.append(np.nan)
        MIN_Altitud.append(np.nan)
            
    if 'Velocidad' in df.columns:
        AVG_Velocidad.append(df['Velocidad'].mean())
        MAX_Velocidad.append(df['Velocidad'].max())
        MIN_Velocidad.append(df['Velocidad'].min())
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
        
    if 'FrecuenciaCardiaca' in df.columns:
        AVG_FrecuenciaCardiaca.append(df['FrecuenciaCardiaca'].mean())
        MAX_FrecuenciaCardiaca.append(df['FrecuenciaCardiaca'].max())
        MIN_FrecuenciaCardiaca.append(df['FrecuenciaCardiaca'].min())
    else:
        AVG_FrecuenciaCardiaca.append(np.nan)
        MAX_FrecuenciaCardiaca.append(np.nan)
        MIN_FrecuenciaCardiaca.append(np.nan)
            
    if 'Cadencia' in df.columns:
        AVG_Cadencia.append(df['Cadencia'].mean())
        MAX_Cadencia.append(df['Cadencia'].max())
        MIN_Cadencia.append(df['Cadencia'].min())
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
        if 'Altitud' in df.columns:
            AVG_Altitud.append(df[df['Bloque']==i]['Altitud'].mean())
            MAX_Altitud.append(df[df['Bloque']==i]['Altitud'].max())
            MIN_Altitud.append(df[df['Bloque']==i]['Altitud'].min())     
        else:
            AVG_Altitud.append(np.nan)
            MAX_Altitud.append(np.nan)
            MIN_Altitud.append(np.nan)
                
        if 'Velocidad' in df.columns:
            AVG_Velocidad.append(df[df['Bloque']==i]['Velocidad'].mean())
            MAX_Velocidad.append(df[df['Bloque']==i]['Velocidad'].max())
            MIN_Velocidad.append(df[df['Bloque']==i]['Velocidad'].min())
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
            
        if 'FrecuenciaCardiaca' in df.columns:
            AVG_FrecuenciaCardiaca.append(df[df['Bloque']==i]['FrecuenciaCardiaca'].mean())
            MAX_FrecuenciaCardiaca.append(df[df['Bloque']==i]['FrecuenciaCardiaca'].max())
            MIN_FrecuenciaCardiaca.append(df[df['Bloque']==i]['FrecuenciaCardiaca'].min())      
        else:
            AVG_FrecuenciaCardiaca.append(np.nan)
            MAX_FrecuenciaCardiaca.append(np.nan)
            MIN_FrecuenciaCardiaca.append(np.nan)
                
        if 'Cadencia' in df.columns:
            AVG_Cadencia.append(df[df['Bloque']==i]['Cadencia'].mean())
            MAX_Cadencia.append(df[df['Bloque']==i]['Cadencia'].max())
            MIN_Cadencia.append(df[df['Bloque']==i]['Cadencia'].min())
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
    MinDistanciaKm.append(df.loc[df.index.min() == df.index, ['Distancia']].min()[0])
    for km in range(1, floor(df['Distancia'].max()/1000)+1):
        LatitudKm.append(df.loc[df[df['Distancia'] >= km*1000].index.min() == df.index, ['Latitud']].min()[0])
        LongitudKm.append(df.loc[df[df['Distancia'] >= km*1000].index.min() == df.index, ['Longitud']].min()[0])
        TiempoTotalKm.append(df.loc[df[df['Distancia'] >= km*1000].index.min() == df.index, ['TiempoTotal']].min()[0])
        TiempoActividadKm.append(df.loc[df[df['Distancia'] >= km*1000].index.min() == df.index, ['TiempoActividad']].min()[0])
        MinDistanciaKm.append(df.loc[df[df['Distancia'] >= km*1000].index.min() == df.index, ['Distancia']].min()[0])
    LatitudKm.append(df.loc[df.index.max() == df.index, ['Latitud']].min()[0])
    LongitudKm.append(df.loc[df.index.max() == df.index, ['Longitud']].min()[0])
    TiempoTotalKm.append(df.loc[df.index.max() == df.index, ['TiempoTotal']].min()[0])
    TiempoActividadKm.append(df.loc[df.index.max() == df.index, ['TiempoActividad']].min()[0])
    MinDistanciaKm.append(df.loc[df.index.max() == df.index, ['Distancia']].min()[0])
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
    df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))
    
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()
    
    for index, row in df.iterrows():
        if row['DeltaTiempo'].total_seconds() > FrecuenciaMuestreo:
            DistanciasPausas.append(row['Distancia'])
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
        Tramo = ceil(row['Distancia']/TramoDistancia)
        df.at[index,'Tramo'] = Tramo
    
    for i in range(floor(df['Distancia'].max()/(df['Distancia'].max()-1)), ceil(df['Distancia'].max()/TramoDistancia)+1):
        TramoParcial.append(i)
        DistanciaTramo.append(df[df['Tramo']==i]['Distancia'].max()-df[df['Tramo']==i]['Distancia'].min())
        DistanciaTramoMin.append(df[df['Tramo']==i]['Distancia'].min())
        DistanciaTramoMax.append(df[df['Tramo']==i]['Distancia'].max())
        AVG_Velocidad_Tramo.append(round(df[df['Tramo']==i]['Velocidad'].mean(), 1))
        AVG_Ritmo_Tramo.append(df[df['Tramo']==i]['Ritmo'].mean())
        AVG_FrecuenciaCardiaca_Tramo.append(round(df[df['Tramo']==i]['FrecuenciaCardiaca'].mean()))
        if 'Cadencia' in df.columns:
            AVG_Cadencia_Tramo.append(round(df[df['Tramo']==i]['Cadencia'].mean()))
        else:
            AVG_Cadencia_Tramo.append(0)
        SUM_DesnivelAcumulado_Tramo.append(round(df[df[df['Tramo']==i].index.max()==df.index]['Altitud'][0]-df[df[df['Tramo']==i].index.min()==df.index]['Altitud'][0]))
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
        DistanciaPausa.append(df[df['Bloque']==i]['Distancia'].max()-df[df['Bloque']==i]['Distancia'].min())
        DistanciaPausaMin.append(df[df['Bloque']==i]['Distancia'].min())
        DistanciaPausaMax.append(df[df['Bloque']==i]['Distancia'].max())
        AVG_Velocidad_Pausa.append(round(df[df['Bloque']==i]['Velocidad'].mean(), 1))
        AVG_Ritmo_Pausa.append(df[df['Bloque']==i]['Ritmo'].mean())
        AVG_FrecuenciaCardiaca_Pausa.append(round(df[df['Bloque']==i]['FrecuenciaCardiaca'].mean()))
        AVG_Cadencia_Pausa.append(round(df[df['Bloque']==i]['Cadencia'].mean()))
        SUM_DesnivelAcumulado_Pausa.append(round(df[df[df['Bloque']==i].index.max()==df.index]['Altitud'][0]-df[df[df['Bloque']==i].index.min()==df.index]['Altitud'][0]))  
    
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
    # Creacion de campos auxiliares
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))

    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()

    """
        Definicion de 5 zonas cardiacas y calculo de %en cada zona
    """
    ZonasIntensidad = {'Z1':[0.5, 0.6], 'Z2':[0.6, 0.7], 'Z3':[0.7, 0.8], 'Z4':[0.8, 0.9], 'Z5':[0.9, 1]} #Intensidad
    
    # Creacion de un diccionario 
    ZonasCardiacas = {Z:[floor(FormulaKarvonen(FCMax, FCRep, ZonasIntensidad[Z][0])), floor(FormulaKarvonen(FCMax, FCRep, ZonasIntensidad[Z][1]))] for Z in ZonasIntensidad.keys()}
           
    for index, row in df.iterrows():
        for k, v in ZonasCardiacas.items():
            if row['FrecuenciaCardiaca'] >= v[0] and row['FrecuenciaCardiaca'] < v[1]:
                ZonaFC = k        
        if row['FrecuenciaCardiaca'] >= ZonasCardiacas['Z5'][1]:
            ZonaFC = 'Z5'
        if row['FrecuenciaCardiaca'] < ZonasCardiacas['Z1'][0]:
            ZonaFC = '-'    
        df.at[index,'ZonaFC'] = ZonaFC    
        
    dfTiempoZonasFC = df[df['DeltaTiempo'] == datetime.timedelta(seconds= FrecuenciaMuestreo)][['ZonaFC', 'DeltaTiempo']].groupby('ZonaFC').sum().reset_index()
    dfTiempoZonasFC['PorcentajeTiempo'] = (dfTiempoZonasFC['DeltaTiempo']/np.timedelta64(1, 's'))/(dfTiempoZonasFC['DeltaTiempo'].sum()/np.timedelta64(1, 's'))

    df = df.drop(['HoraMuestra', 'DeltaTiempo'], 1)
    
    return dfTiempoZonasFC


def IdentificacionTipoActividad(df, Type='Actividad'):
    """
        Esta funcion recibe por parametros el tipo de actividad leido del fichero de origen GPX y el propio DataFrame.
        Si el tipo de actividad leido no aporta suficiente informacion como para saber a que deporte se corresponden los datos, se procede
        a analizar la informacion contenida en el DataFrame.
    """
    # Valores por defecto
    UbicacionActividad = 'NoIdentificada'
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
    """
    Ciclismo = [x.upper() for x in CiclismoGenerico] + CiclismoStrava.upper() + CiclismoGarmin.upper()
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
    """
    Inicio, Fin = df.index.min(), df.index.max()
    FechaInicio, FechaFin = Inicio.strftime("%d/%m/%Y"), Fin.strftime("%d/%m/%Y")
    HoraInicio, HoraFin = Inicio.strftime("%H:%M:%S"), Fin.strftime("%H:%M:%S")
        
    TiempoTotalSegundos = df['TiempoTotal'].max().total_seconds()
    TiempoActividadSegundos = df['TiempoActividad'].max().total_seconds()
    TiempoPausadoSegundos = TiempoTotalSegundos - TiempoActividadSegundos
    NumeroPausas = int(df['Bloque'].max())
    RatioActivoPausado = TiempoActividadSegundos / TiempoTotalSegundos

    if 'Distancia' in df.columns:
        DistanciaActividad = df['Distancia'].max()
    else:
        DistanciaActividad = df['Distancia'].max()
    
    if 'DesnivelPositivoAcumulado' in df.columns and 'DesnivelNegativoAcumulado' in df.columns:
        DesnivelPositivo = df['DesnivelPositivoAcumulado'].max()
        DesnivelPorKilometro = ((df['DesnivelPositivoAcumulado'].max() + df['DesnivelNegativoAcumulado'].max())/df['Distancia'].max())*1000 #Unidades m/km
    else:
        DesnivelPositivo = 0
        DesnivelPorKilometro = 0
    
    if 'Velocidad' in df.columns and 'Pendiente' in df.columns:
        VelocidadMedia = df['Velocidad'].mean()*3.6 #Unidades km/h
        VelocidadMediaAscenso = df[df['Pendiente']>=0]['Velocidad'].mean()*3.6 #Unidades km/h
        VelocidadMediaDescenso = df[df['Pendiente']<=0]['Velocidad'].mean()*3.6 #Unidades km/h
        VelocidadPercentil90 =  np.percentile(df['Velocidad'], 90)*3.6
        RatioVelocidadDesnivel = VelocidadMediaAscenso / VelocidadMediaDescenso
    else:
        VelocidadMedia = 0
        VelocidadMediaAscenso = 0
        VelocidadMediaDescenso = 0
        VelocidadPercentil90 =  0
        RatioVelocidadDesnivel = 0
    
    # Identificacion del tipo de actividad
    if DeteccionVariables(df, 'Coordenadas'):
        UbicacionActividad = 'Outdoor'
        LatitudInicio, LongitudInicio = df.loc[df.index.min() == df.index, ['Latitud']].min()[0], df.loc[df.index.min() == df.index, ['Longitud']].min()[0]
        LatitudFin, LongitudFin = df.loc[df.index.max() == df.index, ['Latitud']].min()[0], df.loc[df.index.max() == df.index, ['Longitud']].min()[0]
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
    else:
        UbicacionActividad = 'Indoor'
        if DeteccionVariables(df, 'Distancia') and DeteccionVariables(df, 'Velocidad'):
            TipoActividad = 'Treadmill'
            SubTipoActividad = '-'       
        
    # Valores por defecto
    if TipoActividad == 'NoIdentificada':
        TipoActividad = Type
        
    return UbicacionActividad, TipoActividad, SubTipoActividad

        

       
def LecturaBBDDActividades(DirectorioBase, BBDD):
    """
        Funcion que lee el fichero de actividades ubicado en la ruta pasada por parametros
    """
    if os.path.exists(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv')):
            DataFrameBBDDActividades = pd.read_csv(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv'), sep= ';', encoding = 'utf-8')
    else:
            DataFrameBBDDActividades = pd.DataFrame(columns=['NombreFichero', 'NombreActividad', 'Ubicacion', 'TipoActividadOriginal', 'UbicacionActividad', 'TipoActividad', 'SubTipoActividad', \
                                                            'Fecha', 'Hora', 'LatitudInicio', 'LongitudInicio', \
                                                            'Distancia', 'TiempoTotal', 'TiempoActividad', 'TramosPausas', \
                                                            'FrecuenciaCardiacaMedia', 'FrecuenciaCardiacaMaxima', 'FrecuenciaCardiacaMinima', \
                                                            'CadenciaMedia', 'CadenciaMaxima', 'CadenciaMinima', \
                                                            'TemperaturaMedia', 'TemperaturaMaxima', 'TemperaturaMinima', \
                                                            'AltitudMaxima', 'AltitudMinima', 'DesnivelPositivo', 'DesnivelNegativo', 'DesnivelPorKilometro', \
                                                            'VelocidadMedia', 'VelocidadMaxima', 'VelocidadPercentil90', 'VelocidadMinima', 'VelocidadPercentil10', 'VelocidadMediaAscenso', 'VelocidadMediaDescenso', 'RatioVelocidadDesnivel'])
    return DataFrameBBDDActividades


def AnalisisActividadActual(NombreFichero, NombreActividad, TipoActividadOriginal, df):
    """
        Funcion que recibe el nombre de un fichero y el DataFrame correspondente, extrae los datos resumidos
        de la actividad y crea un DataFrame con el regitro correspondiente a estos datos.
        Falta la parte de asignacion del tipo de actividad
    """
    NombreFichero = NombreFichero
    Fecha = df.index.min().date().strftime('%Y/%m/%d')
    Hora = df.index.min().time().strftime('%H:%M:%S')
    
    if 'Latitud' in df.columns and 'Longitud' in df.columns:
        LatitudInicio = str(df.loc[df.index.min() == df.index, ['Latitud']].min()[0])
        LongitudInicio = str(df.loc[df.index.min() == df.index, ['Longitud']].min()[0])
        Distancia = int(round(df['Distancia'].max()))        
    elif 'Distancia' in df.columns:
        Ubicacion = ''
        Distancia = int(round(df['Distancia'].max()))
    else:
        Ubicacion = ''
        Distancia = 0
    
    # Determinaicion de la localizacion
    try:
        Localizaciones = rg_search((LatitudInicio, LongitudInicio)) # Admite multiples coordenadas
        Ubicacion = Localizaciones[0]['name']
    except:
        Ubicacion = ''
    
    TiempoTotal = FormateoTiempos(df['TiempoTotal'].max(), 'Z')
    TiempoActividad = FormateoTiempos(df['TiempoActividad'].max(), 'Z')
    TramosPausas = int(df['Bloque'].max())
    
    if 'FrecuenciaCardiaca' in df.columns:
        FrecuenciaCardiacaMedia = int(round(df['FrecuenciaCardiaca'].mean()))
        FrecuenciaCardiacaMaxima = int(round(df['FrecuenciaCardiaca'].max()))
        FrecuenciaCardiacaMinima = int(round(df['FrecuenciaCardiaca'].min()))
    else:
        FrecuenciaCardiacaMedia = 0
        FrecuenciaCardiacaMaxima = 0
        FrecuenciaCardiacaMinima = 0
    
    if 'Cadencia' in df.columns:
        CadenciaMedia = int(round(df['Cadencia'].mean()))
        CadenciaMaxima = int(round(df['Cadencia'].max()))
        CadenciaMinima = int(round(df['Cadencia'].min()))
    else:
        CadenciaMedia = 0
        CadenciaMaxima = 0
        CadenciaMinima = 0
        
    if 'TemperaturaAmbiente' in df.columns:
        TemperaturaMedia = int(round(df['TemperaturaAmbiente'].mean()))
        TemperaturaMaxima = int(round(df['TemperaturaAmbiente'].max()))
        TemperaturaMinima = int(round(df['TemperaturaAmbiente'].min()))
    else:
        TemperaturaMedia = 0
        TemperaturaMaxima = 0
        TemperaturaMinima = 0
    
    if 'Altitud' in df.columns:
        AltitudMaxima = int(round(df['Altitud'].max()))
        AltitudMinima = int(round(df['Altitud'].min()))
        DesnivelPositivo = int(round(df['DesnivelPositivoAcumulado'].max()))
        DesnivelNegativo = int(round(df['DesnivelNegativoAcumulado'].max()))
        DesnivelPorKilometro = int(round(((df['DesnivelPositivoAcumulado'].max() + df['DesnivelNegativoAcumulado'].max())/df['Distancia'].max())*1000)) #Unidades m/km
    else:
        AltitudMaxima = 0
        AltitudMinima = 0
        DesnivelPositivo = 0
        DesnivelNegativo = 0
        DesnivelPorKilometro = 0
    
    if 'Velocidad' in df.columns:
        VelocidadMedia = round(df['Velocidad'].mean()*3.6, 1) #Unidades km/h
        VelocidadMaxima = round(df['Velocidad'].max()*3.6, 1) #Unidades km/h
        VelocidadPercentil90 =  round(np.percentile(df['Velocidad'], 90)*3.6, 1) #Eliminacion de outliers
        VelocidadMinima = round(df['Velocidad'].min()*3.6, 1) #Unidades km/h
        VelocidadPercentil10 =  round(np.percentile(df['Velocidad'], 10)*3.6, 1) #Eliminacion de outliers
        if 'Pendiente' in df.columns:
            VelocidadMediaAscenso = round(df[df['Pendiente']>0]['Velocidad'].mean()*3.6, 1) #Unidades km/h
            VelocidadMediaDescenso = round(df[df['Pendiente']<0]['Velocidad'].mean()*3.6, 1) #Unidades km/h
            RatioVelocidadDesnivel = round(VelocidadMediaAscenso/VelocidadMediaDescenso, 1)
        else:
            VelocidadMediaAscenso = 0
            VelocidadMediaDescenso = 0
            RatioVelocidadDesnivel = 0
    else:
        VelocidadMedia = 0
        VelocidadMaxima = 0
        VelocidadPercentil90 = 0
        VelocidadMinima = 0
        VelocidadPercentil10 =  0
        VelocidadMediaAscenso = 0
        VelocidadMediaDescenso = 0
        RatioVelocidadDesnivel = 0
        
    # Algoritmo de identificacion de actividades
    UbicacionActividad, TipoActividad, SubTipoActividad = IdentificacionTipoActividad(df, TipoActividadOriginal)
    
    # Creacion del registro correspondiente a la actividad actual
    DataFrameActividadActual = pd.DataFrame({    
        'NombreFichero':NombreFichero,
        'NombreActividad':NombreActividad,
        'Ubicacion':Ubicacion,
        'TipoActividadOriginal':TipoActividadOriginal,
        'UbicacionActividad':UbicacionActividad,        
        'TipoActividad':TipoActividad,
        'SubTipoActividad':SubTipoActividad,
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
        'RatioVelocidadDesnivel':RatioVelocidadDesnivel}, index= [0])   
    return DataFrameActividadActual
    
    
def DeteccionVariables(df, variable):
    """
        Funcion que recibe el DataFrame correspondiente a una actividad y una variable y devuelve los valores 1 o 0
        dependiendo de si esa variable contiene valores para mostrar.
        Valores de variable validos:
            - Coordenadas
            - Distancia
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
    ExisteVariable = 0
    
    # Coordenadas geograficas
    if variable == 'Coordenadas' and 'Latitud' in df.columns and 'Longitud' in df.columns:
        if (df['Latitud'].max() != df['Latitud'].min() or df['Latitud'].mean() != 0) and (df['Longitud'].max() != df['Longitud'].min() or df['Longitud'].mean() != 0):
            ExisteVariable = 1
        else:
            ExisteVariable = 0

    # Frecuencia cardiaca
    if variable == 'FrecuenciaCardiaca' and 'FrecuenciaCardiaca' in df.columns:
        if df['FrecuenciaCardiaca'].max() != df['FrecuenciaCardiaca'].min() or df['FrecuenciaCardiaca'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0

    # Velocidad
    if variable == 'Velocidad' and 'Velocidad' in df.columns:
        if df['Velocidad'].max() != df['Velocidad'].min() or df['Velocidad'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0
            
    # Altitud
    if variable == 'Altitud' and 'Altitud' in df.columns:
        if df['Altitud'].max() != df['Altitud'].min() or df['Altitud'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0
            
    # Cadencia
    if variable == 'Cadencia' and 'Cadencia' in df.columns:
        if df['Cadencia'].max() != df['Cadencia'].min() or df['Cadencia'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0

    # Temperatura
    if variable == 'Temperatura' and 'TemperaturaAmbiente' in df.columns:
        if df['TemperaturaAmbiente'].max() != df['TemperaturaAmbiente'].min() or df['TemperaturaAmbiente'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0 

    # DesnivelPositivoAcumulado
    if variable == 'DesnivelPositivoAcumulado' and 'DesnivelPositivoAcumulado' in df.columns:
        if df['DesnivelPositivoAcumulado'].max() != df['DesnivelPositivoAcumulado'].min() and df['DesnivelPositivoAcumulado'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0         

    # DesnivelNegativoAcumulado
    if variable == 'DesnivelNegativoAcumulado' and 'DesnivelNegativoAcumulado' in df.columns:
        if df['DesnivelNegativoAcumulado'].max() != df['DesnivelNegativoAcumulado'].min() and df['DesnivelNegativoAcumulado'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0 

    # Pendiente
    if variable == 'Pendiente'and 'Pendiente' in df.columns:
        if df['Pendiente'].max() != df['Pendiente'].min() or df['Pendiente'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0
            
    # Longitud de zancada
    if variable == 'LongitudZancada' and 'LongitudZancada' in df.columns:
        if df['LongitudZancada'].max() != df['LongitudZancada'].min() or df['LongitudZancada'].mean() != 0:
            ExisteVariable = 1
        else:
            ExisteVariable = 0

    return ExisteVariable



def IdentificacionPausas(df):
    """
    Funcion que recibe como parametro un DataFrame y devuelve el numero de pausas
    temporales identificados en los datos
    """
    if 'DeltaTiempo' not in df.columns:
        df['HoraMuestra'] = df.index
        df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(pd.Timedelta(seconds=0))
        df = df.drop('HoraMuestra', 1)
        
    NumeroPausas = 0
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()   
    for index, row in df.iterrows():
        if row['DeltaTiempo'].total_seconds() > FrecuenciaMuestreo:
            print(row)
            NumeroPausas += 1
            
    return NumeroPausas