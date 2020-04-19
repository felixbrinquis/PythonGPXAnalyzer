# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 12:22:01 2020

@author: Felix
"""
import pandas as pd
import numpy as np
from math import ceil, floor, radians, pi, log, tan
import datetime
import os


def FormateoEjes(VariableCDS, PrecisionTick=10, ReduccionEscala=1, MargenInferior=0.5, MargenSuperior=0.5):
    """
        Funcion que recibe los valores de una variable de un ColumnDataDource en formato array y devuelve un dicionario de valores y su correspondiente 
        en formato texto entre el minimo y el maximo valor con margenes inferior y superior, con una dstancia entre valores y reduccion de escala si fuera necesario
    """
    return {i: str(int(i/ReduccionEscala)) for i in range(int(floor(np.nanmin(VariableCDS)*(1-MargenInferior) / PrecisionTick)) * PrecisionTick , int(ceil(np.nanmax(VariableCDS)*(1+MargenSuperior) / PrecisionTick)) * PrecisionTick + PrecisionTick, PrecisionTick)}


def CalculoOffsetAltitud(ColumnDataSource):
    """
        Funcion que recibe un ColumnDataSource de Bokeh con la informacion de altitud y
        desniveles calculada y devuelve los offset optimos superior e inferior para 
        representar la altidud de una manera mas acorde a la realidad.
    """
    # Calculo de desniveles finales
    DesnivelPositivo = ColumnDataSource.data['DesnivelPositivo[m]'].max()
    DesnivelNegativo = ColumnDataSource.data['DesnivelNegativo[m]'].max()
    DesnivelAcumulado = DesnivelPositivo + DesnivelNegativo
    DesnivelPorKilometro = (DesnivelAcumulado/ColumnDataSource.data['Distancia[m]'].max())*1000
    
    # Factor de achatamiento de la altitud
    if DesnivelPorKilometro > 40:
        OffsetSuperiorAltitud = 0.1
        OffsetInferiorAltitud = 0.03
    else:
        OffsetSuperiorAltitud = 2.5
        OffsetInferiorAltitud = 0.5
        
    return OffsetSuperiorAltitud, OffsetInferiorAltitud


def LimiteEjeY(ColumnDataSource, Metrica, TipoLimite):
    """
        Funcion que recibe como parametros un ColumnDataSource de Bokeh, la metrica a visualizar
        y el tipo de limite deseado y devuelve el valor adecuado del eje Y para su visualizacion.
        Valores de Metrica validos:
            - FRECUENCIA CARDIACA
            - RITMO
            - ALTITUD
            - CADENCIA
            - TEMPERATURA
            - PENDIENTE
            - DESNIVEL POSITIVO
            - DESNIVEL NEGATIVO
            - LONGITUD ZANCADA
        Valores de TipoLimite validos:
            - Inferior
            - Superior
            
        Esta funcion permite realizar cambios en la distancia entre los limites de los graficos
        de Bokeh y los datos a visualizar modificando unicamente 
    """
    Limite = np.nan
    
    # Frecuencia cardiaca
    if Metrica == 'FRECUENCIA CARDIACA' and 'FrecuenciaCardiaca[ppm]' in ColumnDataSource.column_names:
        if TipoLimite == 'Inferior':
            Limite = floor(min(np.nanmin(ColumnDataSource.data['FrecuenciaCardiaca[ppm]']), 85))
        elif TipoLimite == 'Superior':
            Limite = ceil(max(np.nanmax(ColumnDataSource.data['FrecuenciaCardiaca[ppm]']), 180))
        else:
            Limite = np.nan
        
    # Ritmo
    if Metrica == 'RITMO' and 'Velocidad[m/s]' in ColumnDataSource.column_names:
        if TipoLimite == 'Inferior':
            Limite = floor(np.nanmin(ColumnDataSource.data['Velocidad[m/s]'])-np.nanmin(ColumnDataSource.data['Velocidad[m/s]'])*0.1)
        elif TipoLimite == 'Superior':
            Limite = ceil(np.nanmax(ColumnDataSource.data['Velocidad[m/s]'])+np.nanmax(ColumnDataSource.data['Velocidad[m/s]'])*0.2)
        else:
            Limite = np.nan
        
    # Altitud
    if Metrica == 'ALTITUD' and 'Altitud[m]' in ColumnDataSource.column_names:
        OffsetSuperiorAltitud, OffsetInferiorAltitud = CalculoOffsetAltitud(ColumnDataSource)
        if TipoLimite == 'Inferior':
            Limite = floor(np.nanmin(ColumnDataSource.data['Altitud[m]'])-((np.nanmax(ColumnDataSource.data['Altitud[m]'])-np.nanmin(ColumnDataSource.data['Altitud[m]']))*OffsetInferiorAltitud))
        elif TipoLimite == 'Superior':
            Limite = ceil(np.nanmax(ColumnDataSource.data['Altitud[m]'])+((np.nanmax(ColumnDataSource.data['Altitud[m]'])-np.nanmin(ColumnDataSource.data['Altitud[m]']))*OffsetSuperiorAltitud))
        else:
            Limite = np.nan
    
    # Cadencia
    if Metrica == 'CADENCIA' and 'Cadencia[ppm]' in ColumnDataSource.column_names:
        if TipoLimite == 'Inferior':
            Limite = floor(np.nanmin(ColumnDataSource.data['Cadencia[ppm]'])-(np.nanmax(ColumnDataSource.data['Cadencia[ppm]'])-np.nanmin(ColumnDataSource.data['Cadencia[ppm]']))*0.03)
        elif TipoLimite == 'Superior':
            Limite = ceil(np.nanmax(ColumnDataSource.data['Cadencia[ppm]'])+(np.nanmax(ColumnDataSource.data['Cadencia[ppm]'])-np.nanmin(ColumnDataSource.data['Cadencia[ppm]']))*0.1)
        else:
            Limite = np.nan
    
    # Temperatura
    if Metrica == 'TEMPERATURA' and 'Temperatura[ºC]' in ColumnDataSource.column_names:
        # Calculo de un margen sin datos por tramos
        Rango = np.nanmax(ColumnDataSource.data['Temperatura[ºC]'])-np.nanmin(ColumnDataSource.data['Temperatura[ºC]'])
        if Rango < 1:
            Margen = 2
        elif Rango >= 1 and Rango < 10:
            Margen = (1/Rango)*2
        else:
            Margen = 0.2
        
        if TipoLimite == 'Inferior':
            if np.nanmin(ColumnDataSource.data['Temperatura[ºC]']) > 25:
                Limite = floor(np.nanmin(ColumnDataSource.data['Temperatura[ºC]'])-Margen*2)
            else:
                Limite = floor(min(np.nanmin(ColumnDataSource.data['Temperatura[ºC]'])-Margen, 0))
        elif TipoLimite == 'Superior':
            Limite = ceil(max(np.nanmax(ColumnDataSource.data['Temperatura[ºC]'])+Margen, 0))
        else:
            Limite = np.nan
    
    # Pendiente
    if Metrica == 'PENDIENTE' and 'Pendiente[%]' in ColumnDataSource.column_names:
        if TipoLimite == 'Inferior':
            Limite = floor(np.nanmin(ColumnDataSource.data['Pendiente[%]'])-(np.nanmax(ColumnDataSource.data['Pendiente[%]'])-np.nanmin(ColumnDataSource.data['Pendiente[%]']))*0.05)
        elif TipoLimite == 'Superior':
            Limite = ceil(np.nanmax(ColumnDataSource.data['Pendiente[%]'])+(np.nanmax(ColumnDataSource.data['Pendiente[%]'])-np.nanmin(ColumnDataSource.data['Pendiente[%]']))*0.05)
        else:
            Limite = np.nan
            
    # Desnivel positivo
    if Metrica == 'DESNIVEL POSITIVO' and 'DesnivelPositivo[m]' in ColumnDataSource.column_names:
        if TipoLimite == 'Inferior':
            Limite = floor(0)
        elif TipoLimite == 'Superior':
            Limite = ceil(np.nanmax(ColumnDataSource.data['DesnivelPositivo[m]'])+np.nanmax(ColumnDataSource.data['DesnivelPositivo[m]'])*0.05)
        else:
            Limite = np.nan
    
    # Desnivel negativo
    if Metrica == 'DESNIVEL NEGATIVO' and 'DesnivelNegativo[m]' in ColumnDataSource.column_names:
        if TipoLimite == 'Inferior':
            Limite = floor(0)
        elif TipoLimite == 'Superior':
            Limite = ceil(np.nanmax(ColumnDataSource.data['DesnivelNegativo[m]'])+np.nanmax(ColumnDataSource.data['DesnivelNegativo[m]'])*0.05)
        else:
            Limite = np.nan
    
    # Longitud de zancada
    if Metrica == 'LONGITUD ZANCADA' and 'LongitudZancada[m]' in ColumnDataSource.column_names:
        if TipoLimite == 'Inferior':
            Limite = floor(np.nanmin(ColumnDataSource.data['LongitudZancada[m]'])-(np.nanmax(ColumnDataSource.data['LongitudZancada[m]'])-np.nanmin(ColumnDataSource.data['LongitudZancada[m]']))*0.03)
        elif TipoLimite == 'Superior':
            Limite = ceil(np.nanmax(ColumnDataSource.data['LongitudZancada[m]'])+(np.nanmax(ColumnDataSource.data['LongitudZancada[m]'])-np.nanmin(ColumnDataSource.data['LongitudZancada[m]']))*0.1)
        else:
            Limite = np.nan
        
    return Limite
    
def ParametrosVariables(ColumnDataSource):
    """
    Funcion que genera un diccionario cuyos valores clave son las diferentes variables necesarias para la creacion y representacion
    de las graficas principales y auxiliares.
    """
    from bokeh.models import LinearColorMapper
    from bokeh.transform import transform
    from source.common.PaletasColores import Grapefruit, Bittersweet, Sunflower, Grass, Mint, Aqua, BlueJeans, Lavender, PinkRose, SkinTone, LightGray, DarkGray, PaletaGrises

    # Creacion de un diccionario de metricas auxiliares
    DiccionarioVariables = {
            'FRECUENCIA CARDIACA':{'Activo':1, 'Variable':'FrecuenciaCardiaca[ppm]', 'CDS':ColumnDataSource, 'Sufijo':'_FRC', 'Tipo':'line', 'Color':Grapefruit[2], 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'FRECUENCIA CARDIACA', 'Inferior')+5, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'FRECUENCIA CARDIACA', 'Superior')-5, 'Propiedades':dict(line_width= 2, line_alpha=0.9, line_cap= 'round', visible= False)},
            'RITMO':{'Activo':1, 'Variable':'Velocidad[m/s]', 'CDS':ColumnDataSource, 'Sufijo':'_VEL', 'Tipo':'line', 'Color':BlueJeans[2], 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'RITMO', 'Inferior')*1.05, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'RITMO', 'Superior')*0.95, 'Propiedades':dict(line_width= 2, line_alpha=0.9, line_cap= 'round', visible= False)},
            'ALTITUD':{'Activo':1, 'Variable':'Altitud[m]', 'CDS':ColumnDataSource, 'Sufijo':'_ALT', 'Tipo':'line', 'Color':Mint[2], 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'ALTITUD', 'Inferior')*1.01, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'ALTITUD', 'Superior')*0.99, 'Propiedades':dict(line_width= 2, line_alpha=0.9, line_cap= 'round', visible= False)},
            'CADENCIA':{'Activo':1, 'Variable':'Cadencia[ppm]', 'CDS':ColumnDataSource, 'Sufijo':'_CAD', 'Tipo':'circle', 'Color':transform('Cadencia[ppm]', LinearColorMapper(palette=PaletaGrises, low= 110, high= 190)), 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'CADENCIA', 'Inferior')*1.05, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'CADENCIA', 'Superior')*0.95, 'Propiedades':dict(fill_alpha= 0.9, visible= False)},
            'TEMPERATURA':{'Activo':1, 'Variable':'Temperatura[ºC]', 'CDS':ColumnDataSource, 'Sufijo':'_TMP', 'Tipo':'step', 'Color':Sunflower[2], 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'TEMPERATURA', 'Inferior')*1.01, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'TEMPERATURA', 'Superior')*0.99, 'Propiedades':dict(line_width= 2, line_alpha=0.9, line_cap= 'round', visible= False)},
            'PENDIENTE':{'Activo':1, 'Variable':'Pendiente[%]', 'CDS':ColumnDataSource, 'Sufijo':'_PEN', 'Tipo':'line', 'Color':PinkRose[2], 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'PENDIENTE', 'Inferior')*1.1, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'PENDIENTE', 'Superior')*0.95, 'Propiedades':dict(line_width= 2, line_alpha=0.9, line_cap= 'round', visible= False)},
            'DESNIVEL POSITIVO':{'Activo':1, 'Variable':'DesnivelPositivo[m]', 'CDS':ColumnDataSource, 'Sufijo':'_DPA', 'Tipo':'line', 'Color':Lavender[2], 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'DESNIVEL POSITIVO', 'Inferior')+1, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'DESNIVEL POSITIVO', 'Superior')-1, 'Propiedades':dict(line_width= 2, line_alpha=0.9, line_cap= 'round', visible= False)},
            'DESNIVEL NEGATIVO':{'Activo':0, 'Variable':'DesnivelNegativo[m]', 'CDS':ColumnDataSource, 'Sufijo':'_DNA', 'Tipo':'line', 'Color':Lavender[2], 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'DESNIVEL NEGATIVO', 'Inferior')+1, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'DESNIVEL NEGATIVO', 'Superior')-1, 'Propiedades':dict(line_width= 2, line_alpha=0.9, line_cap= 'round', visible= False)},
            'LONGITUD ZANCADA':{'Activo':1, 'Variable':'LongitudZancada[m]', 'CDS':ColumnDataSource, 'Sufijo':'_LZN', 'Tipo':'circle', 'Color':transform('LongitudZancada[m]', LinearColorMapper(palette=PaletaGrises, low= 0.8, high= 2)), 'LimiteInferiorY':LimiteEjeY(ColumnDataSource, 'LONGITUD ZANCADA', 'Inferior')*1.05, 'LimiteSuperiorY':LimiteEjeY(ColumnDataSource, 'LONGITUD ZANCADA', 'Superior')*0.95, 'Propiedades':dict(fill_alpha= 0.9, visible= False)}}
    return DiccionarioVariables


def FunctionSizeCircle(ColumnDataSource):
    """
    El tamaño del punto en las graficas por puntos es importante para evitar un solapamiento excesivo de los datos.
    A mayor volumen de informacion a mostrar, menor tamaño de punto.
    Con una frecuencia de muestreo de 1 segundo se eligen como tramos:
        - 60: menos de un minuto
        - 300: menos de cinco minutos
        - 3600: menos de uns hora
        - >3600: actividades de larga duracion
    """
    if ColumnDataSource.data[ColumnDataSource.column_names[0]].shape[0] < 60:
        SizeCircle = 10
    elif ColumnDataSource.data[ColumnDataSource.column_names[0]].shape[0] < 300:
        SizeCircle = 8
    elif ColumnDataSource.data[ColumnDataSource.column_names[0]].shape[0] < 3600:
        SizeCircle = 5
    else:
        SizeCircle = 3
    return SizeCircle