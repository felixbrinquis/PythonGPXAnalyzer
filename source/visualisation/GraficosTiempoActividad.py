# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este modulo contiene la funcion TabGraficosTiempoActividad la cual crea un tablon donde se visualizan
distintas metricas usando como eje horizontal el tiempo durante el cual se ha recogido informacion de manera activa.
"""

"""
    IMPORTACION DE LIBRERIAS
"""
# Importacion de las funciones necesarias
from bokeh.layouts import gridplot, layout, widgetbox, Spacer
from bokeh.models import ColumnDataSource, Span, HoverTool, LinearColorMapper, NumeralTickFormatter, DatetimeTickFormatter, CustomJS
from bokeh.models.widgets import CheckboxGroup
from bokeh.models.tickers import SingleIntervalTicker
from bokeh.plotting import figure
from bokeh.transform import transform

import numpy as np
import pandas as pd

from source.common.funciones import ConversorCoordenadasMercator, Reescalado, CalculosVectoresAgregados, FormateoEjes, DeteccionVariables
from source.common.PaletasColores import paleta_rojo, paleta_verde, paleta_azul, paleta_negro, paleta_cadencia, paleta_zancada




def TabGraficosTiempoActividad(df):
    """
        PREPARACION DE DATOS
    """
    # Calculo de los valores agregados
    AVG_Altitud, MAX_Altitud, MIN_Altitud, \
        AVG_Velocidad, MAX_Velocidad, MIN_Velocidad, \
        AVG_Ritmo, MAX_Ritmo, MIN_Ritmo, \
        AVG_FrecuenciaCardiaca, MAX_FrecuenciaCardiaca, MIN_FrecuenciaCardiaca, \
        AVG_Cadencia, MAX_Cadencia, MIN_Cadencia, \
        AVG_Temperatura, MAX_Temperatura, MIN_Temperatura, \
        AVG_LongitudZancada, MAX_LongitudZancada, MIN_LongitudZancada, \
        AVG_Pendiente, MAX_Pendiente , MIN_Pendiente = CalculosVectoresAgregados(df)
        
        # Calculo de desniveles finales
    DesnivelPositivo = df['DesnivelPositivoAcumulado'].max()
    DesnivelNegativo = df['DesnivelNegativoAcumulado'].max()
    DesnivelAcumulado = DesnivelPositivo + DesnivelNegativo
    DesnivelPorKilometro = (DesnivelAcumulado/df['DistanciaAcumulada'].max())*1000
        
    # Factor de achatamiento de la altitud
    if DesnivelPorKilometro > 40:
        OffsetSuperiorAltitud = 0.1
        OffsetInferiorAltitud = 0.03
    else:
        OffsetSuperiorAltitud = 2.5
        OffsetInferiorAltitud = 0.5
    
    # Seleccion de un subconjunto de datos para visualizar
    dfBokeh = df[['TiempoTotal', 'TiempoActividad', 'DistanciaAcumulada', 'Bloque', 'Latitud', 'Longitud', 'Altitud', 'AltitudCalculada', 'Velocidad_i', 'VelocidadCalculada', 'Ritmo', 'FrecuenciaCardiaca', 'FrecuenciaCardiacaCalculada', 'Cadencia', 'CadenciaCalculada', 'TemperaturaAmbiente', 'LongitudZancada', 'DesnivelPositivoAcumulado', 'Pendiente']].copy()
    # Inclusion del ritmo instantaneo en formato texto
    dfBokeh['Ritmo_STR'] = dfBokeh.Ritmo.dt.round('1s').dt.components['minutes'].astype(str).apply(lambda x: x.zfill(2))+':'+dfBokeh.Ritmo.dt.round('1s').dt.components['seconds'].astype(str).apply(lambda x: x.zfill(2))
        
    #  Reducion de la frecuencia de muestreo
    dfBokehAgregables = dfBokeh.groupby('Bloque').resample('10S').agg({'TiempoTotal': np.max, 'TiempoActividad': np.max, 'DistanciaAcumulada': np.max, 'AltitudCalculada': np.max, 'VelocidadCalculada': np.mean, 'FrecuenciaCardiacaCalculada': np.mean, 'CadenciaCalculada': np.mean, 'TemperaturaAmbiente': np.mean, 'LongitudZancada': np.mean, 'DesnivelPositivoAcumulado': np.max, 'Pendiente': np.mean})
    dfBokehAgregables['CadenciaCalculada'] = dfBokehAgregables['CadenciaCalculada'].round()
        
    dfRitmo = dfBokeh[['Bloque', 'Ritmo']].copy()
    dfRitmo['Ritmo_S'] = dfBokeh['Ritmo']/ np.timedelta64(1, 's')
    dfRitmoAGG = dfRitmo.groupby('Bloque').resample('10S').mean()
    dfRitmoAGG['Ritmo'] = pd.to_timedelta(dfRitmoAGG['Ritmo_S'], unit='s')
    dfRitmoAGG = dfRitmoAGG.drop('Ritmo_S', 1)
    dfBokehAGG = pd.merge(dfBokehAgregables, dfRitmoAGG[['Ritmo']], left_index=True, right_index=True)
    dfBokehAGG['Ritmo_STR'] = dfBokehAGG.Ritmo.dt.round('1s').dt.components['minutes'].astype(str).apply(lambda x: x.zfill(2))+':'+dfBokehAGG.Ritmo.dt.round('1s').dt.components['seconds'].astype(str).apply(lambda x: x.zfill(2))
        
    #Creacion de variables reescaladas por variable principal
    dfBokeh['VelocidadEscalada_FC'] = Reescalado(dfBokeh['VelocidadCalculada'], [MIN_Velocidad[0], MAX_Velocidad[0]], [min(MIN_FrecuenciaCardiaca[0]+5, 90), max(MAX_FrecuenciaCardiaca[0]-5, 175)])
    dfBokeh['AltitudEscalada_FC'] = Reescalado(dfBokeh['AltitudCalculada'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)], [min(MIN_FrecuenciaCardiaca[0]+5, 90), max(MAX_FrecuenciaCardiaca[0]-5, 175)])
    dfBokehAGG['CadenciaEscalada_FC'] = Reescalado(dfBokehAGG['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]], [min(MIN_FrecuenciaCardiaca[0]+5, 90), max(MAX_FrecuenciaCardiaca[0]-5, 175)])
    dfBokeh['TemperaturaEscalada_FC'] = Reescalado(dfBokeh['TemperaturaAmbiente'], [MIN_Temperatura[0], MAX_Temperatura[0]], [min(MIN_FrecuenciaCardiaca[0]+5, 90), max(MAX_FrecuenciaCardiaca[0]-5, 175)])
    dfBokeh['PendienteEscalada_FC'] = Reescalado(dfBokeh['Pendiente'], [MIN_Pendiente[0], MAX_Pendiente[0]], [min(MIN_FrecuenciaCardiaca[0]+5, 90), max(MAX_FrecuenciaCardiaca[0]-5, 175)])
    dfBokeh['DesnivelPositivoEscalado_FC'] = Reescalado(dfBokeh['DesnivelPositivoAcumulado'], [0, dfBokeh['DesnivelPositivoAcumulado'].max()], [min(MIN_FrecuenciaCardiaca[0]+5, 90), max(MAX_FrecuenciaCardiaca[0]-5, 175)])
    dfBokehAGG['ZancadaEscalada_FC'] = Reescalado(dfBokehAGG['LongitudZancada'], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]], [min(MIN_FrecuenciaCardiaca[0]+5, 90), max(MAX_FrecuenciaCardiaca[0]-5, 175)])
    
    dfBokeh['FrecuenciaCardiacaEscalada_Vel'] = Reescalado(dfBokeh['FrecuenciaCardiacaCalculada'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [MIN_Velocidad[0], MAX_Velocidad[0]])
    dfBokeh['AltitudEscalada_Vel'] = Reescalado(dfBokeh['AltitudCalculada'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)], [MIN_Velocidad[0], MAX_Velocidad[0]])
    dfBokehAGG['CadenciaEscalada_Vel'] = Reescalado(dfBokehAGG['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]], [MIN_Velocidad[0], MAX_Velocidad[0]])
    dfBokeh['TemperaturaEscalada_Vel'] = Reescalado(dfBokeh['TemperaturaAmbiente'], [MIN_Temperatura[0], MAX_Temperatura[0]], [MIN_Velocidad[0], MAX_Velocidad[0]])
    dfBokeh['PendienteEscalada_Vel'] = Reescalado(dfBokeh['Pendiente'], [MIN_Pendiente[0], MAX_Pendiente[0]], [MIN_Velocidad[0], MAX_Velocidad[0]])
    dfBokeh['DesnivelPositivoEscalado_Vel'] = Reescalado(dfBokeh['DesnivelPositivoAcumulado'], [0, dfBokeh['DesnivelPositivoAcumulado'].max()], [MIN_Velocidad[0], MAX_Velocidad[0]])
    dfBokehAGG['ZancadaEscalada_Vel'] = Reescalado(dfBokehAGG['LongitudZancada'], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]], [MIN_Velocidad[0], MAX_Velocidad[0]])
        
    dfBokeh['FrecuenciaCardiacaEscalada_Alt'] = Reescalado(dfBokeh['FrecuenciaCardiacaCalculada'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)])
    dfBokeh['VelocidadEscalada_Alt'] = Reescalado(dfBokeh['VelocidadCalculada'], [MIN_Velocidad[0], MAX_Velocidad[0]],[MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)])
    dfBokehAGG['CadenciaEscalada_Alt'] = Reescalado(dfBokehAGG['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]],[MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)])
    dfBokeh['TemperaturaEscalada_Alt'] = Reescalado(dfBokeh['TemperaturaAmbiente'], [MIN_Temperatura[0], MAX_Temperatura[0]], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)])
    dfBokeh['PendienteEscalada_Alt'] = Reescalado(dfBokeh['Pendiente'], [MIN_Pendiente[0], MAX_Pendiente[0]], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)])
    dfBokeh['DesnivelPositivoEscalado_Alt'] = Reescalado(dfBokeh['DesnivelPositivoAcumulado'], [0, dfBokeh['DesnivelPositivoAcumulado'].max()], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)])
    dfBokehAGG['ZancadaEscalada_Alt'] = Reescalado(dfBokehAGG['LongitudZancada'], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)])
    
    dfBokeh['FrecuenciaCardiacaEscalada_Cad'] = Reescalado(dfBokeh['FrecuenciaCardiacaCalculada'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [MIN_Cadencia[0], MAX_Cadencia[0]])
    dfBokeh['VelocidadEscalada_Cad'] = Reescalado(dfBokeh['VelocidadCalculada'], [MIN_Velocidad[0], MAX_Velocidad[0]], [MIN_Cadencia[0], MAX_Cadencia[0]])
    dfBokeh['AltitudEscalada_Cad'] = Reescalado(dfBokeh['AltitudCalculada'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)], [MIN_Cadencia[0], MAX_Cadencia[0]])
    dfBokeh['TemperaturaEscalada_Cad'] = Reescalado(dfBokeh['TemperaturaAmbiente'], [MIN_Temperatura[0], MAX_Temperatura[0]], [MIN_Cadencia[0], MAX_Cadencia[0]])
    dfBokeh['PendienteEscalada_Cad'] = Reescalado(dfBokeh['Pendiente'], [MIN_Pendiente[0], MAX_Pendiente[0]], [MIN_Cadencia[0], MAX_Cadencia[0]])
    dfBokeh['DesnivelPositivoEscalado_Cad'] = Reescalado(dfBokeh['DesnivelPositivoAcumulado'], [0, dfBokeh['DesnivelPositivoAcumulado'].max()], [MIN_Cadencia[0], MAX_Cadencia[0]])
    dfBokehAGG['ZancadaEscalada_Cad'] = Reescalado(dfBokehAGG['LongitudZancada'], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]], [MIN_Cadencia[0], MAX_Cadencia[0]])
     
    dfBokeh['FrecuenciaCardiacaEscalada_Tem'] = Reescalado(dfBokeh['FrecuenciaCardiacaCalculada'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [MIN_Temperatura[0], MAX_Temperatura[0]])
    dfBokeh['VelocidadEscalada_Tem'] = Reescalado(dfBokeh['VelocidadCalculada'], [MIN_Velocidad[0], MAX_Velocidad[0]], [MIN_Temperatura[0], MAX_Temperatura[0]])
    dfBokeh['AltitudEscalada_Tem'] = Reescalado(dfBokeh['AltitudCalculada'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)], [MIN_Temperatura[0], MAX_Temperatura[0]])
    dfBokehAGG['CadenciaEscalada_Tem'] = Reescalado(dfBokehAGG['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]], [MIN_Temperatura[0], MAX_Temperatura[0]])
    dfBokeh['PendienteEscalada_Tem'] = Reescalado(dfBokeh['Pendiente'], [MIN_Pendiente[0], MAX_Pendiente[0]], [MIN_Temperatura[0], MAX_Temperatura[0]])
    dfBokeh['DesnivelPositivoEscalado_Tem'] = Reescalado(dfBokeh['DesnivelPositivoAcumulado'], [0, dfBokeh['DesnivelPositivoAcumulado'].max()], [MIN_Temperatura[0], MAX_Temperatura[0]])
    dfBokehAGG['ZancadaEscalada_Tem'] = Reescalado(dfBokehAGG['LongitudZancada'], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]], [MIN_Temperatura[0], MAX_Temperatura[0]])
        
    dfBokeh['FrecuenciaCardiacaEscalada_Pen'] = Reescalado(dfBokeh['FrecuenciaCardiacaCalculada'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [MIN_Pendiente[0], MAX_Pendiente[0]])
    dfBokeh['VelocidadEscalada_Pen'] = Reescalado(dfBokeh['VelocidadCalculada'], [MIN_Velocidad[0], MAX_Velocidad[0]], [MIN_Pendiente[0], MAX_Pendiente[0]])
    dfBokeh['AltitudEscalada_Pen'] = Reescalado(dfBokeh['AltitudCalculada'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)], [MIN_Pendiente[0], MAX_Pendiente[0]])
    dfBokehAGG['CadenciaEscalada_Pen'] = Reescalado(dfBokehAGG['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]], [MIN_Pendiente[0], MAX_Pendiente[0]])
    dfBokeh['TemperaturaEscalada_Pen'] = Reescalado(dfBokeh['TemperaturaAmbiente'], [MIN_Temperatura[0], MAX_Temperatura[0]], [MIN_Pendiente[0], MAX_Pendiente[0]])
    dfBokeh['DesnivelPositivoEscalado_Pen'] = Reescalado(dfBokeh['DesnivelPositivoAcumulado'], [0, dfBokeh['DesnivelPositivoAcumulado'].max()], [MIN_Pendiente[0], MAX_Pendiente[0]])
    dfBokehAGG['ZancadaEscalada_Pen'] = Reescalado(dfBokehAGG['LongitudZancada'], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]], [MIN_Pendiente[0], MAX_Pendiente[0]])
        
    dfBokeh['FrecuenciaCardiacaEscalada_Des'] = Reescalado(dfBokeh['FrecuenciaCardiacaCalculada'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [10, 0.95*DesnivelPositivo])
    dfBokeh['VelocidadEscalada_Des'] = Reescalado(dfBokeh['VelocidadCalculada'], [MIN_Velocidad[0], MAX_Velocidad[0]], [10, 0.95*DesnivelPositivo])
    dfBokeh['AltitudEscalada_Des'] = Reescalado(dfBokeh['AltitudCalculada'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)], [10, 0.95*DesnivelPositivo])
    dfBokehAGG['CadenciaEscalada_Des'] = Reescalado(dfBokehAGG['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]], [10, 0.95*DesnivelPositivo])
    dfBokeh['TemperaturaEscalada_Des'] = Reescalado(dfBokeh['TemperaturaAmbiente'], [MIN_Temperatura[0], MAX_Temperatura[0]], [10, 0.95*DesnivelPositivo])
    dfBokeh['PendienteEscalada_Des'] = Reescalado(dfBokeh['Pendiente'], [MIN_Pendiente[0], MAX_Pendiente[0]], [10, 0.95*DesnivelPositivo])
    dfBokehAGG['ZancadaEscalada_Des'] = Reescalado(dfBokehAGG['LongitudZancada'], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]], [10, 0.95*DesnivelPositivo])    
        
    dfBokeh['FrecuenciaCardiacaEscalada_Zan'] = Reescalado(dfBokeh['FrecuenciaCardiacaCalculada'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]])
    dfBokeh['VelocidadEscalada_Zan'] = Reescalado(dfBokeh['VelocidadCalculada'], [MIN_Velocidad[0], MAX_Velocidad[0]], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]])
    dfBokeh['AltitudEscalada_Zan'] = Reescalado(dfBokeh['AltitudCalculada'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetInferiorAltitud), MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*(0.5*OffsetSuperiorAltitud)], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]])
    dfBokehAGG['CadenciaEscalada_Zan'] = Reescalado(dfBokehAGG['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]])
    dfBokeh['TemperaturaEscalada_Zan'] = Reescalado(dfBokeh['TemperaturaAmbiente'], [MIN_Temperatura[0], MAX_Temperatura[0]], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]])
    dfBokeh['PendienteEscalada_Zan'] = Reescalado(dfBokeh['Pendiente'], [MIN_Pendiente[0], MAX_Pendiente[0]], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]])
    dfBokeh['DesnivelPositivoEscalado_Zan'] = Reescalado(dfBokeh['DesnivelPositivoAcumulado'], [0, dfBokeh['DesnivelPositivoAcumulado'].max()], [MIN_LongitudZancada[0], MAX_LongitudZancada[0]])
     
        
    # Creacion de coordenadas Mercator en el DataFrame
    for index, row in dfBokeh.iterrows():
        LongitudMercator, LatitudMercator = ConversorCoordenadasMercator(row.Longitud, row.Latitud)
        dfBokeh.at[index,'LongitudMercator'] = LongitudMercator
        dfBokeh.at[index,'LatitudMercator'] = LatitudMercator
        
        
    # Asignacion de tamaño segun el total de puntos
    if df['DistanciaAcumulada'].max() < 5:
        SizeCircle = 10
    elif df['DistanciaAcumulada'].max() <10:
        SizeCircle = 8
    else:
        SizeCircle = 5
            
    # Definicion de la paleta de colores por cadencia
    MapaColorCadencia = LinearColorMapper(palette= paleta_cadencia, low= 110, high= 190)
    MapaColorZancada = LinearColorMapper(palette= paleta_zancada, low= 0.8, high= 2)

    # Creacion de los ColumnDataSource de origen de Bokeh
    DatosBokeh = ColumnDataSource(dfBokeh) 
    DatosBokehAGG = ColumnDataSource(dfBokehAGG)
    
    
    """
        FRECUENCIA CARDIACA | TIEMPO ACTIVIDAD
    """
    # Creacion de un grafica
    PLT_FrecuenciaCardiaca_TMA = figure(width= 1000, height= 400, x_range= (0, dfBokeh['TiempoActividad'].max()), y_range= (min(MIN_FrecuenciaCardiaca[0], 85), max(MAX_FrecuenciaCardiaca[0], 180)), x_axis_type= 'datetime', tools= '', toolbar_location= None)
    
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['TiempoActividad', 'FrecuenciaCardiacaCalculada']].set_index('TiempoActividad')
    dfBokehArea.rename(columns= {'FrecuenciaCardiacaCalculada': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_FrecuenciaCardiaca_TMA.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_rojo[5], alpha= 1, line_color= None)
        
    PLT_FC_Linea_TMA = PLT_FrecuenciaCardiaca_TMA.line('TiempoActividad', 'FrecuenciaCardiacaCalculada', source= DatosBokeh, color= paleta_rojo[6], line_width= 2, line_cap= 'round')
    PLT_FrecuenciaCardiaca_TMA.add_tools(HoverTool(tooltips=[('', '@FrecuenciaCardiaca{int} ppm')], renderers= [PLT_FC_Linea_TMA], mode= 'vline'))
    PLT_FC_Maxima_TMA = PLT_FrecuenciaCardiaca_TMA.inverted_triangle(dfBokeh[dfBokeh['FrecuenciaCardiacaCalculada']==MAX_FrecuenciaCardiaca[0]]['TiempoActividad'].min(), MAX_FrecuenciaCardiaca[0], size= 10, line_color= paleta_negro[7], line_width= 2, fill_color= paleta_negro[5])
    PLT_FrecuenciaCardiaca_TMA.add_tools(HoverTool(tooltips=[('Maximo', str(MAX_FrecuenciaCardiaca[0])+' ppm')], renderers= [PLT_FC_Maxima_TMA], mode= 'mouse'))
    PLT_FrecuenciaCardiaca_TMA.add_layout(Span(location= AVG_FrecuenciaCardiaca[0], dimension= 'width', line_color= paleta_rojo[7], line_dash= 'dashed', line_width= 1, line_alpha= 1))
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_FC_Ritmo_TMA = PLT_FrecuenciaCardiaca_TMA.line('TiempoActividad', 'VelocidadEscalada_FC', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_FC_Altitud_TMA = PLT_FrecuenciaCardiaca_TMA.line('TiempoActividad', 'AltitudEscalada_FC', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_FC_Cadencia_TMA = PLT_FrecuenciaCardiaca_TMA.circle('TiempoActividad', 'CadenciaEscalada_FC', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_FC_Temperatura_TMA = PLT_FrecuenciaCardiaca_TMA.step('TiempoActividad', 'TemperaturaEscalada_FC', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_FC_Pendiente_TMA = PLT_FrecuenciaCardiaca_TMA.line('TiempoActividad', 'PendienteEscalada_FC', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_FC_Desnivel_TMA = PLT_FrecuenciaCardiaca_TMA.line('TiempoActividad', 'DesnivelPositivoEscalado_FC', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_FC_Zancada_TMA = PLT_FrecuenciaCardiaca_TMA.circle('TiempoActividad', 'ZancadaEscalada_FC', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)
        
    # Atributos
    PLT_FrecuenciaCardiaca_TMA.title.text = 'FRECUENCIA CARDIACA'
    PLT_FrecuenciaCardiaca_TMA.sizing_mode = 'fixed'
    PLT_FrecuenciaCardiaca_TMA.xaxis.axis_label = 'Tiempo actividad'
    PLT_FrecuenciaCardiaca_TMA.xaxis.formatter = DatetimeTickFormatter(minutes = [':%M', '%Mm'])
    PLT_FrecuenciaCardiaca_TMA.yaxis.axis_label = 'Frecuencia cardiaca [ppm]'
    PLT_FrecuenciaCardiaca_TMA.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_FrecuenciaCardiaca_TMA.grid.visible = False
    PLT_FrecuenciaCardiaca_TMA.yaxis.minor_tick_line_color = None
    PLT_FrecuenciaCardiaca_TMA.yaxis.major_label_overrides = FormateoEjes(dfBokeh.FrecuenciaCardiacaCalculada, 10, 1)
   
    
    #Botones
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
    
    CodigoJSFrecuenciaCardiaca = CustomJS(code=CodigoJS, args={})
    
    BotonesGraficaFC = CheckboxGroup(labels=['RITMO', 'ALTITUD', 'CADENCIA', 'TEMPERATURA', 'PENDIENTE', 'DESNIVEL POSITIVO', 'LONGITUD ZANCADA'], active=[], callback=CodigoJSFrecuenciaCardiaca, width= 100)
    
    CodigoJSFrecuenciaCardiaca.args = dict(l0=PLT_FC_Ritmo_TMA, l1=PLT_FC_Altitud_TMA, l2=PLT_FC_Cadencia_TMA, l3=PLT_FC_Temperatura_TMA, l4=PLT_FC_Pendiente_TMA, l5=PLT_FC_Desnivel_TMA, l6=PLT_FC_Zancada_TMA, checkbox=BotonesGraficaFC)
    
    
    
    """
        VELOCIDAD | TIEMPO ACTIVIDAD
    """
    # Creacion de un grafica
    PLT_VelocidadCalculada_TMA = figure(width= 1000, height= 400, x_range= (0, dfBokeh['TiempoActividad'].max()), y_range= (MIN_Velocidad[0]-MIN_Velocidad[0]*0.1, MAX_Velocidad[0]+MAX_Velocidad[0]*0.2), x_axis_type= 'datetime', tools= '', toolbar_location= None)
    
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['TiempoActividad', 'VelocidadCalculada']].set_index('TiempoActividad')
    dfBokehArea.rename(columns= {'VelocidadCalculada': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_VelocidadCalculada_TMA.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_azul[5], alpha= 1, line_color= None)
    
    PLT_V_Linea_TMA = PLT_VelocidadCalculada_TMA.line('TiempoActividad', 'VelocidadCalculada', source= DatosBokeh, line_width= 2, color= paleta_azul[6], line_cap= 'round')
    PLT_VelocidadCalculada_TMA.add_layout(Span(location= AVG_Velocidad[0], dimension= 'width', line_color= paleta_azul[7], line_dash= 'dashed', line_width= 1, line_alpha= 1))
    PLT_VelocidadCalculada_TMA.add_tools(HoverTool(tooltips=[('Ritmo', '@Ritmo_STR')], renderers= [PLT_V_Linea_TMA], mode= 'vline'))
    
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_V_FrecuenciaCardiaca_TMA = PLT_VelocidadCalculada_TMA.line('TiempoActividad', 'FrecuenciaCardiacaEscalada_Vel', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_V_Altitud_TMA = PLT_VelocidadCalculada_TMA.line('TiempoActividad', 'AltitudEscalada_Vel', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_V_Cadencia_TMA = PLT_VelocidadCalculada_TMA.circle('TiempoActividad', 'CadenciaEscalada_Vel', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_V_Temperatura_TMA = PLT_VelocidadCalculada_TMA.step('TiempoActividad', 'TemperaturaEscalada_Vel', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_V_Pendiente_TMA = PLT_VelocidadCalculada_TMA.line('TiempoActividad', 'PendienteEscalada_Vel', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_V_Desnivel_TMA = PLT_VelocidadCalculada_TMA.line('TiempoActividad', 'DesnivelPositivoEscalado_Vel', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_V_Zancada_TMA = PLT_VelocidadCalculada_TMA.circle('TiempoActividad', 'ZancadaEscalada_Vel', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)
    	
    # Atributos
    PLT_VelocidadCalculada_TMA.title.text = 'RITMO INSTANTANEO'
    PLT_VelocidadCalculada_TMA.sizing_mode = 'fixed'
    PLT_VelocidadCalculada_TMA.xaxis.axis_label = 'Tiempo actividad'
    PLT_VelocidadCalculada_TMA.xaxis.formatter = DatetimeTickFormatter(minutes = [':%M', '%Mm'])
    PLT_VelocidadCalculada_TMA.yaxis.axis_label = 'Ritmo [min/km]'
    PLT_VelocidadCalculada_TMA.yaxis.formatter = NumeralTickFormatter(format= '0.0')
    PLT_VelocidadCalculada_TMA.grid.visible = False
    PLT_VelocidadCalculada_TMA.yaxis.minor_tick_line_color = None
    PLT_VelocidadCalculada_TMA.yaxis.major_label_overrides = {1: '16:40', 1.5: '16:06', 2: '8:20', 2.5: '6:40', 3: '5:33', 3.5: '4:45', 4: '4:10', 4.5: '3:42', 5: '3:20', 5.5: '3:01', 6: '2:46', 6.5: '2:34', 7: '2:22'}


    #Botones
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
    
    CodigoJSVelocidad = CustomJS(code=CodigoJS, args={})
    
    BotonesGraficaVelocidad = CheckboxGroup(labels=['FRECUENCIA CARDIACA', 'ALTITUD', 'CADENCIA', 'TEMPERATURA', 'PENDIENTE', 'DESNIVEL POSITIVO', 'LONGITUD ZANCADA'], active=[], callback=CodigoJSVelocidad, width= 100)
    
    CodigoJSVelocidad.args = dict(l0=PLT_V_FrecuenciaCardiaca_TMA, l1=PLT_V_Altitud_TMA, l2=PLT_V_Cadencia_TMA, l3=PLT_V_Temperatura_TMA, l4=PLT_V_Pendiente_TMA, l5=PLT_V_Desnivel_TMA, l6=PLT_V_Zancada_TMA, checkbox=BotonesGraficaVelocidad)
 

    
    """
    	ALTITUD | TIEMPO ACTIVIDAD
    """
    # Creacion de un grafica
    PLT_Altitud_TMA = figure(width= 1000, height= 400, x_range= (0, dfBokeh['TiempoActividad'].max()), y_range= (MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*OffsetInferiorAltitud, MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*OffsetSuperiorAltitud), x_axis_type= 'datetime', tools= '', toolbar_location= None)
    
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['TiempoActividad', 'AltitudCalculada']].set_index('TiempoActividad')
    dfBokehArea.rename(columns= {'AltitudCalculada': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_Altitud_TMA.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_verde[5], alpha= 1, line_color= None)
    
    PLT_ALT_Altitud_TMA = PLT_Altitud_TMA.line('TiempoActividad', 'AltitudCalculada', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
    
    # Efectos visuales
    if DesnivelPorKilometro > 40:
        PLT_Altitud_TMA.add_tools(HoverTool(tooltips=[('Distancia', '@TiempoActividad{0.0} km'),('Altitud', '@AltitudCalculada{int} m'),('Desnivel positivo', '@DesnivelPositivoAcumulado{int} m'),('Pendiente', '@Pendiente{0.00}%')], renderers= [PLT_ALT_Altitud_TMA], mode= 'vline'))
    else:
        PLT_Altitud_TMA.add_tools(HoverTool(tooltips=[('Distancia', '@TiempoActividad{0.0} km'),('Altitud', '@AltitudCalculada{int} m')], renderers= [PLT_ALT_Altitud_TMA], mode= 'vline'))
    
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_ALT_FC_TMA = PLT_Altitud_TMA.line('TiempoActividad', 'FrecuenciaCardiacaEscalada_Alt', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_ALT_Ritmo_TMA = PLT_Altitud_TMA.line('TiempoActividad', 'VelocidadEscalada_Alt', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_ALT_Cadencia_TMA = PLT_Altitud_TMA.circle('TiempoActividad', 'CadenciaEscalada_Alt', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_ALT_Temperatura_TMA = PLT_Altitud_TMA.step('TiempoActividad', 'TemperaturaEscalada_Alt', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_ALT_Pendiente_TMA = PLT_Altitud_TMA.line('TiempoActividad', 'PendienteEscalada_Alt', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_ALT_Desnivel_TMA = PLT_Altitud_TMA.line('TiempoActividad', 'DesnivelPositivoEscalado_Alt', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_ALT_Zancada_TMA = PLT_Altitud_TMA.circle('TiempoActividad', 'ZancadaEscalada_Alt', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)
    
    
    # Atributos
    PLT_Altitud_TMA.title.text = 'ALTITUD'
    PLT_Altitud_TMA.sizing_mode = 'fixed'
    PLT_Altitud_TMA.xaxis.axis_label = 'Tiempo actividad'
    PLT_Altitud_TMA.xaxis.formatter = DatetimeTickFormatter(minutes = [':%M', '%Mm'])
    PLT_Altitud_TMA.yaxis.axis_label = 'Altitud [m]'
    PLT_Altitud_TMA.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Altitud_TMA.grid.visible = False
    PLT_Altitud_TMA.yaxis.minor_tick_line_color = None
    PLT_Altitud_TMA.yaxis.major_label_overrides = FormateoEjes(dfBokeh.AltitudCalculada, 100, 1)

   
    #Botones
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
    
    CodigoJSAltitud = CustomJS(code=CodigoJS, args={})
    
    BotonesGraficaALT = CheckboxGroup(labels=['FRECUENCIA CARDIACA', 'RITMO', 'CADENCIA', 'TEMPERATURA', 'PENDIENTE', 'DESNIVEL POSITIVO', 'LONGITUD ZANCADA'], active=[], callback=CodigoJSAltitud, width= 100)
    
    CodigoJSAltitud.args = dict(l0=PLT_ALT_FC_TMA, l1=PLT_ALT_Ritmo_TMA, l2=PLT_ALT_Cadencia_TMA, l3=PLT_ALT_Temperatura_TMA, l4=PLT_ALT_Pendiente_TMA, l5=PLT_ALT_Desnivel_TMA, l6=PLT_ALT_Zancada_TMA, checkbox=BotonesGraficaALT)
     
 
    
    """
    	CADENCIA | TIEMPO ACTIVIDAD
    """
    # Creacion de un grafica
    PLT_Cadencia_TMA = figure(width= 1000, height= 400, x_range= (0, dfBokeh['TiempoActividad'].max()), y_range= (MIN_Cadencia[0]-(MAX_Cadencia[0]-MIN_Cadencia[0])*0.03, MAX_Cadencia[0]+(MAX_Cadencia[0]-MIN_Cadencia[0])*0.1), x_axis_type= 'datetime', tools= '', toolbar_location= None)
        
    # Inclusion de datos
    PLT_Cadencia_TMA.circle('TiempoActividad', 'CadenciaCalculada', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 1)
    PLT_C_Linea_TMA = PLT_Cadencia_TMA.line('TiempoActividad', 'CadenciaCalculada', source= DatosBokehAGG, color= 'white', line_width= 0, line_alpha= 0)
    PLT_Cadencia_TMA.add_tools(HoverTool(tooltips=[('', '@CadenciaCalculada')], renderers= [PLT_C_Linea_TMA], mode= 'vline'))
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_C_FC_TMA = PLT_Cadencia_TMA.line('TiempoActividad', 'FrecuenciaCardiacaEscalada_Cad', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_C_Ritmo_TMA = PLT_Cadencia_TMA.line('TiempoActividad', 'VelocidadEscalada_Cad', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_C_Altitud_TMA = PLT_Cadencia_TMA.line('TiempoActividad', 'AltitudEscalada_Cad', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_C_Temperatura_TMA = PLT_Cadencia_TMA.step('TiempoActividad', 'TemperaturaEscalada_Cad', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_C_Pendiente_TMA = PLT_Cadencia_TMA.line('TiempoActividad', 'PendienteEscalada_Cad', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_C_Desnivel_TMA = PLT_Cadencia_TMA.line('TiempoActividad', 'DesnivelPositivoEscalado_Cad', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_C_Zancada_TMA = PLT_Cadencia_TMA.circle('TiempoActividad', 'ZancadaEscalada_Cad', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)
       
     
    # Atributos
    PLT_Cadencia_TMA.title.text = 'CADENCIA'
    PLT_Cadencia_TMA.sizing_mode = 'fixed'
    PLT_Cadencia_TMA.xaxis.axis_label = 'Tiempo actividad'
    PLT_Cadencia_TMA.xaxis.formatter = DatetimeTickFormatter(minutes = [':%M', '%Mm'])
    PLT_Cadencia_TMA.yaxis.axis_label = 'Cadencia [Pasos por minuto]'
    PLT_Cadencia_TMA.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Cadencia_TMA.grid.visible = False
    PLT_Cadencia_TMA.yaxis.minor_tick_line_color = None
    PLT_Cadencia_TMA.yaxis.major_label_overrides = FormateoEjes(dfBokeh.CadenciaCalculada, 10, 1)
    
    #Botones
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
    
    CodigoJSCadencia = CustomJS(code=CodigoJS, args={})
    
    BotonesGraficaCadencia = CheckboxGroup(labels=['FRECUENCIA CARDIACA', 'RITMO', 'ALTITUD', 'TEMPERATURA', 'PENDIENTE', 'DESNIVEL POSITIVO', 'LONGITUD ZANCADA'], active=[], callback=CodigoJSCadencia, width= 100)
    
    CodigoJSCadencia.args = dict(l0=PLT_C_FC_TMA, l1=PLT_C_Ritmo_TMA, l2=PLT_C_Altitud_TMA, l3=PLT_C_Temperatura_TMA, l4=PLT_C_Pendiente_TMA, l5=PLT_C_Desnivel_TMA, l6=PLT_C_Zancada_TMA, checkbox=BotonesGraficaCadencia)
 
 

    
    """
        TEMPERATURA AMBIENTE | TIEMPO ACTIVIDAD
    """
    # Creacion de un grafica
    PLT_Temperatura_TMA = figure(width= 1000, height= 400, x_range= (0, dfBokeh['TiempoActividad'].max()), y_range= (min(MIN_Temperatura[0], 0), MAX_Temperatura[0]+(MAX_Temperatura[0]-MIN_Temperatura[0])*0.1), x_axis_type= 'datetime', tools= '', toolbar_location= None)
        
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['TiempoActividad', 'TemperaturaAmbiente']].set_index('TiempoActividad')
    dfBokehArea.rename(columns= {'TemperaturaAmbiente': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_Temperatura_TMA.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_azul[3], alpha= 1, line_color= None)
        
    PLT_Temperatura_TMA.step('TiempoActividad', 'TemperaturaAmbiente', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_TMP_FC_TMA = PLT_Temperatura_TMA.line('TiempoTotal', 'FrecuenciaCardiacaEscalada_Tem', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_TMP_Ritmo_TMA = PLT_Temperatura_TMA.line('TiempoTotal', 'VelocidadEscalada_Tem', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_TMP_Altitud_TMA = PLT_Temperatura_TMA.line('TiempoTotal', 'AltitudEscalada_Tem', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas) 
    PLT_TMP_Cadencia_TMA = PLT_Temperatura_TMA.circle('TiempoTotal', 'CadenciaEscalada_Tem', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_TMP_Pendiente_TMA = PLT_Temperatura_TMA.line('TiempoTotal', 'PendienteEscalada_Tem', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_TMP_Desnivel_TMA = PLT_Temperatura_TMA.line('TiempoTotal', 'DesnivelPositivoEscalado_Tem', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_TMP_Zancada_TMA = PLT_Temperatura_TMA.circle('TiempoTotal', 'ZancadaEscalada_Tem', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)   
    
    # Atributos
    PLT_Temperatura_TMA.title.text = 'TEMPERATURA AMBIENTE'
    PLT_Temperatura_TMA.sizing_mode = 'fixed'
    PLT_Temperatura_TMA.xaxis.axis_label = 'Tiempo actividad'
    PLT_Temperatura_TMA.xaxis.formatter = DatetimeTickFormatter(minutes = [':%M', '%Mm'])
    PLT_Temperatura_TMA.yaxis.axis_label = 'Temperatura [ºC]'
    PLT_Temperatura_TMA.yaxis.formatter = NumeralTickFormatter(format= '0,0')
    PLT_Temperatura_TMA.grid.visible = False
    PLT_Temperatura_TMA.yaxis.minor_tick_line_color = None
    PLT_Temperatura_TMA.yaxis.major_label_overrides = FormateoEjes(dfBokeh.TemperaturaAmbiente, 5, 1)

    #Botones
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
    
    CodigoJSTemperatura= CustomJS(code=CodigoJS, args={})
    
    BotonesGraficaTMP = CheckboxGroup(labels=['FRECUENCIA CARDIACA', 'RITMO',  'ALTITUD', 'CADENCIA', 'PENDIENTE', 'DESNIVEL POSITIVO', 'LONGITUD ZANCADA'], active=[], callback=CodigoJSTemperatura, width= 100)
    
    CodigoJSTemperatura.args = dict(l0=PLT_TMP_FC_TMA, l1=PLT_TMP_Ritmo_TMA, l2=PLT_TMP_Altitud_TMA, l3=PLT_TMP_Cadencia_TMA, l4=PLT_TMP_Pendiente_TMA, l5=PLT_TMP_Desnivel_TMA, l6=PLT_TMP_Zancada_TMA, checkbox=BotonesGraficaTMP)

  
    
    """
    	PENDIENTE | TIEMPO ACTIVIDAD
    """
    # Creacion de un grafica
    PLT_Pendiente_TMA = figure(width= 1000, height= 400, x_range= (0, dfBokeh['TiempoActividad'].max()), y_range= (MIN_Pendiente[0]-(MAX_Pendiente[0]-MIN_Pendiente[0])*0.05, MAX_Pendiente[0]+(MAX_Pendiente[0]-MIN_Pendiente[0])*0.05), x_axis_type= 'datetime', tools= '', toolbar_location= None)
        
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['TiempoActividad', 'Pendiente']].set_index('TiempoActividad')
    dfBokehArea.rename(columns= {'Pendiente': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_Pendiente_TMA.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_verde[5], alpha= 1, line_color= None)
        
    PLT_Pendiente_TMA.line('TiempoActividad', 'Pendiente', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_PEN_FC_TMA = PLT_Pendiente_TMA.line('TiempoActividad', 'FrecuenciaCardiacaEscalada_Pen', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_PEN_Ritmo_TMA = PLT_Pendiente_TMA.line('TiempoActividad', 'VelocidadEscalada_Pen', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_PEN_Altitud_TMA = PLT_Pendiente_TMA.line('TiempoActividad', 'AltitudEscalada_Pen', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_PEN_Cadencia_TMA = PLT_Pendiente_TMA.circle('TiempoActividad', 'CadenciaEscalada_Pen', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_PEN_Temperatura_TMA = PLT_Pendiente_TMA.step('TiempoActividad', 'TemperaturaEscalada_Pen', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_PEN_Desnivel_TMA = PLT_Pendiente_TMA.line('TiempoActividad', 'DesnivelPositivoEscalado_Pen', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_PEN_Zancada_TMA = PLT_Pendiente_TMA.circle('TiempoActividad', 'ZancadaEscalada_Pen', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)   
     
    # Atributos
    PLT_Pendiente_TMA.title.text = 'PENDIENTE'
    PLT_Pendiente_TMA.sizing_mode = 'fixed'
    PLT_Pendiente_TMA.xaxis.axis_label = 'Tiempo actividad'
    PLT_Pendiente_TMA.xaxis.formatter = DatetimeTickFormatter(minutes = [':%M', '%Mm'])
    PLT_Pendiente_TMA.yaxis.axis_label = 'Pendiente [%]'
    PLT_Pendiente_TMA.yaxis.formatter = NumeralTickFormatter(format= '0,0')
    PLT_Pendiente_TMA.grid.visible = False
    PLT_Pendiente_TMA.yaxis.minor_tick_line_color = None
    PLT_Pendiente_TMA.yaxis.major_label_overrides = FormateoEjes(dfBokeh.Pendiente, 1, 1)

    
    #Botones
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
    
    CodigoJSPendiente = CustomJS(code=CodigoJS, args={})
    
    BotonesGraficaPEN = CheckboxGroup(labels=['FRECUENCIA CARDIACA', 'RITMO', 'ALTITUD', 'CADENCIA', 'TEMPERATURA', 'DESNIVEL POSITIVO', 'LONGITUD ZANCADA'], active=[], callback=CodigoJSPendiente, width= 100)
    
    CodigoJSPendiente.args = dict(l0=PLT_PEN_FC_TMA, l1=PLT_PEN_Ritmo_TMA, l2=PLT_PEN_Altitud_TMA, l3=PLT_PEN_Cadencia_TMA, l4=PLT_PEN_Temperatura_TMA, l5=PLT_PEN_Desnivel_TMA, l6=PLT_PEN_Zancada_TMA, checkbox=BotonesGraficaPEN)


    
    """
        DESNIVEL POSITIVO ACUMULADO | TIEMPO ACTIVIDAD
    """
    # Creacion de un grafica
    PLT_DesnivelPositivo_TMA = figure(width= 1000, height= 400, x_range= (0, dfBokeh['TiempoActividad'].max()), y_range= (0, DesnivelPositivo+DesnivelPositivo*0.05), x_axis_type= 'datetime', tools= '', toolbar_location= None)
        
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['TiempoActividad', 'DesnivelPositivoAcumulado']].set_index('TiempoActividad')
    dfBokehArea.rename(columns= {'DesnivelPositivoAcumulado': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_DesnivelPositivo_TMA.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_verde[5], alpha= 1, line_color= None)
        
    PLT_DesnivelPositivo_TMA.line('TiempoActividad', 'DesnivelPositivoAcumulado', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
    
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_DPA_FC_TMA = PLT_DesnivelPositivo_TMA.line('TiempoActividad', 'FrecuenciaCardiacaEscalada_Des', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas) 
    PLT_DPA_Ritmo_TMA = PLT_DesnivelPositivo_TMA.line('TiempoActividad', 'VelocidadEscalada_Des', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_DPA_Altitud_TMA = PLT_DesnivelPositivo_TMA.line('TiempoActividad', 'AltitudEscalada_Des', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_DPA_Cadencia_TMA = PLT_DesnivelPositivo_TMA.circle('TiempoActividad', 'CadenciaEscalada_Des', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_DPA_Temperatura_TMA = PLT_DesnivelPositivo_TMA.step('TiempoActividad', 'TemperaturaEscalada_Des', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_DPA_Pendiente_TMA = PLT_DesnivelPositivo_TMA.line('TiempoActividad', 'PendienteEscalada_Des', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_DPA_Zancada_TMA = PLT_DesnivelPositivo_TMA.circle('TiempoActividad', 'ZancadaEscalada_Des', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)   
       
    # Atributos
    PLT_DesnivelPositivo_TMA.title.text = 'DESNIVEL POSITIVO ACUMULADO'
    PLT_DesnivelPositivo_TMA.sizing_mode = 'fixed'
    PLT_DesnivelPositivo_TMA.xaxis.axis_label = 'Tiempo actividad'
    PLT_DesnivelPositivo_TMA.xaxis.formatter = DatetimeTickFormatter(minutes = [':%M', '%Mm'])
    PLT_DesnivelPositivo_TMA.yaxis.axis_label = 'Desnivel positivo acumulado [m]'
    PLT_DesnivelPositivo_TMA.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_DesnivelPositivo_TMA.grid.visible = False
    PLT_DesnivelPositivo_TMA.yaxis.minor_tick_line_color = None
    PLT_DesnivelPositivo_TMA.yaxis.major_label_overrides = FormateoEjes(dfBokeh.DesnivelPositivoAcumulado, 100, 1)

    
    #Botones
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
    
    CodigoJSDesnivelPositivo = CustomJS(code=CodigoJS, args={})
    
    BotonesGraficaDPA = CheckboxGroup(labels=['FRECUENCIA CARDIACA', 'RITMO', 'ALTITUD', 'CADENCIA', 'TEMPERATURA', 'PENDIENTE', 'LONGITUD ZANCADA'], active=[], callback=CodigoJSDesnivelPositivo, width= 100)
    
    CodigoJSDesnivelPositivo.args = dict(l0=PLT_DPA_FC_TMA, l1=PLT_DPA_Ritmo_TMA, l2=PLT_DPA_Altitud_TMA, l3=PLT_DPA_Cadencia_TMA, l4=PLT_DPA_Temperatura_TMA, l5=PLT_DPA_Pendiente_TMA, l6=PLT_DPA_Zancada_TMA, checkbox=BotonesGraficaDPA)
       

    
    """
    	LONGITUD DE ZANCADA | TIEMPO ACTIVIDAD
    """
    # Creacion de un grafica
    PLT_Zancada_TMA = figure(width= 1000, height= 400, x_range= (0, dfBokeh['TiempoActividad'].max()), y_range= (MIN_LongitudZancada[0]-(MAX_LongitudZancada[0]-MIN_LongitudZancada[0])*0.03, MAX_LongitudZancada[0]+(MAX_LongitudZancada[0]-MIN_LongitudZancada[0])*0.1), x_axis_type= 'datetime', tools= '', toolbar_location= None)
    
    # Inclusion de datos
    PLT_Zancada_TMA.circle('TiempoActividad', 'LongitudZancada', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 1)
    PLT_Z_Linea_TMA = PLT_Zancada_TMA.line('TiempoActividad', 'LongitudZancada', source= DatosBokehAGG, color= 'white', line_width= 0, line_alpha= 0)
    PLT_Zancada_TMA.add_tools(HoverTool(tooltips=[('', '@LongitudZancada')], renderers= [PLT_Z_Linea_TMA], mode= 'vline'))
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_Z_FC_TMA = PLT_Zancada_TMA.line('TiempoActividad', 'FrecuenciaCardiacaEscalada_Zan', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_Z_Ritmo_TMA = PLT_Zancada_TMA.line('TiempoActividad', 'VelocidadEscalada_Zan', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_Z_Altitud_TMA = PLT_Zancada_TMA.line('TiempoActividad', 'AltitudEscalada_Zan', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_Z_Cadencia_TMA = PLT_Zancada_TMA.circle('TiempoActividad', 'CadenciaEscalada_Zan', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_Z_Temperatura_TMA = PLT_Zancada_TMA.step('TiempoActividad', 'TemperaturaEscalada_Zan', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_Z_Pendiente_TMA = PLT_Zancada_TMA.line('TiempoActividad', 'PendienteEscalada_Zan', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_Z_Desnivel_TMA = PLT_Zancada_TMA.line('TiempoActividad', 'DesnivelPositivoEscalado_Zan', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
        
    # Atributos
    PLT_Zancada_TMA.title.text = 'LONGITUD DE ZANCADA'
    PLT_Zancada_TMA.sizing_mode = 'fixed'
    PLT_Zancada_TMA.xaxis.axis_label = 'Tiempo actividad'
    PLT_Zancada_TMA.xaxis.formatter = DatetimeTickFormatter(minutes = [':%M', '%Mm'])
    PLT_Zancada_TMA.yaxis.axis_label = 'Longitud de zancada [m]'
    PLT_Zancada_TMA.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Zancada_TMA.grid.visible = False
    PLT_Zancada_TMA.yaxis.minor_tick_line_color = None

  
    #Botones
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
    
    CodigoJSZancada = CustomJS(code=CodigoJS, args={})
    
    BotonesGraficaZAN = CheckboxGroup(labels=['FRECUENCIA CARDIACA', 'RITMO', 'ALTITUD', 'CADENCIA', 'TEMPERATURA', 'PENDIENTE', 'DESNIVEL POSITIVO'], active=[], callback=CodigoJSZancada, width= 100)
    
    CodigoJSZancada.args = dict(l0=PLT_Z_FC_TMA, l1=PLT_Z_Ritmo_TMA, l2=PLT_Z_Altitud_TMA, l3=PLT_Z_Cadencia_TMA, l4=PLT_Z_Temperatura_TMA, l5=PLT_Z_Pendiente_TMA, l6=PLT_Z_Desnivel_TMA, checkbox=BotonesGraficaZAN)
 

    
       
    """
        LAYOUT
    """
    
    GridBotonesFC = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaFC, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaFC = gridplot(
            [PLT_FrecuenciaCardiaca_TMA, GridBotonesFC],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
 
    GridBotonesVEL = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaVelocidad, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaVEL = gridplot(
            [PLT_VelocidadCalculada_TMA, GridBotonesVEL],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 
    
    GridBotonesALT = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaALT, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaALT = gridplot(
            [PLT_Altitud_TMA, GridBotonesALT],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    
    GridBotonesCAD = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaCadencia, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaCAD = gridplot(
            [PLT_Cadencia_TMA, GridBotonesCAD],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 
 
    GridBotonesTMP = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaTMP, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaTMP = gridplot(
            [PLT_Temperatura_TMA, GridBotonesTMP],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 

    GridBotonesPEN = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaPEN, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaPEN = gridplot(
            [PLT_Pendiente_TMA, GridBotonesPEN],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 

    GridBotonesDPA = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaDPA, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaDPA = gridplot(
            [PLT_DesnivelPositivo_TMA, GridBotonesDPA],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    
    GridBotonesZAN = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaZAN, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaZAN = gridplot(
            [PLT_Zancada_TMA, GridBotonesZAN],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 
    
    
    # Seleccion de las graficas relevantes a mostrar
    ListadoGraficas = []
    
    if DeteccionVariables(df, 'FrecuenciaCardiaca'):
        ListadoGraficas.append(GridGraficaFC)
    if DeteccionVariables(df, 'Velocidad'):
        ListadoGraficas.append(GridGraficaVEL)
    if DeteccionVariables(df, 'Altitud'):
        ListadoGraficas.append(GridGraficaALT)
    if DeteccionVariables(df, 'Cadencia'):
        ListadoGraficas.append(GridGraficaCAD)
    if DeteccionVariables(df, 'Temperatura'):
        ListadoGraficas.append(GridGraficaTMP)
    if DeteccionVariables(df, 'Pendiente'):
        ListadoGraficas.append(GridGraficaPEN)
    if DeteccionVariables(df, 'DesnivelPositivoAcumulado'):
        ListadoGraficas.append(GridGraficaDPA)
    if DeteccionVariables(df, 'LongitudZancada'):
        ListadoGraficas.append(GridGraficaZAN)
        
    GraficasTiempoActividad = layout(
            ListadoGraficas,
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))

    return GraficasTiempoActividad