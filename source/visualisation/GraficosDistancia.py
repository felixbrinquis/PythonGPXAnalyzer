# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este modulo contiene la funcion TabGraficosDistancia la cual crea un tablon donde se visualizan
distintas metricas usando como eje horizontal la distancia recorrida.
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

from source.common.funciones import ConversorCoordenadasMercator, Reescalado, CalculosVectoresAgregados, FormateoEjes, DeteccionVariables, GeneracionCodigoJS
from source.common.PaletasColores import paleta_rojo, paleta_verde, paleta_azul, paleta_negro, paleta_cadencia, paleta_zancada




def TabGraficosDistancia(df):
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
        
    # Reducion de la frecuencia de muestreo
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
        FRECUENCIA CARDIACA | DISTANCIA
    """
    # Creacion de un grafica
    PLT_FrecuenciaCardiaca_DST = figure(width= 1000, height= 400, x_range= (0, dfBokeh['DistanciaAcumulada'].max()), y_range= (min(MIN_FrecuenciaCardiaca[0], 85), max(MAX_FrecuenciaCardiaca[0], 180)), tools= '', toolbar_location= None)
    
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['DistanciaAcumulada', 'FrecuenciaCardiacaCalculada']].set_index('DistanciaAcumulada')
    dfBokehArea.rename(columns= {'FrecuenciaCardiacaCalculada': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_FrecuenciaCardiaca_DST.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_rojo[5], alpha= 1, line_color= None)
        
    PLT_FC_Linea_DST = PLT_FrecuenciaCardiaca_DST.line('DistanciaAcumulada', 'FrecuenciaCardiacaCalculada', source= DatosBokeh, color= paleta_rojo[6], line_width= 2, line_cap= 'round')
    PLT_FrecuenciaCardiaca_DST.add_tools(HoverTool(tooltips=[('', '@FrecuenciaCardiaca{int} ppm')], renderers= [PLT_FC_Linea_DST], mode= 'vline'))
    PLT_FC_Maxima_DST = PLT_FrecuenciaCardiaca_DST.inverted_triangle(dfBokeh[dfBokeh['FrecuenciaCardiacaCalculada']==MAX_FrecuenciaCardiaca[0]]['DistanciaAcumulada'].min(), MAX_FrecuenciaCardiaca[0], size= 10, line_color= paleta_negro[7], line_width= 2, fill_color= paleta_negro[5])
    PLT_FrecuenciaCardiaca_DST.add_tools(HoverTool(tooltips=[('Maximo', str(MAX_FrecuenciaCardiaca[0])+' ppm')], renderers= [PLT_FC_Maxima_DST], mode= 'mouse'))
    PLT_FrecuenciaCardiaca_DST.add_layout(Span(location= AVG_FrecuenciaCardiaca[0], dimension= 'width', line_color= paleta_rojo[7], line_dash= 'dashed', line_width= 1, line_alpha= 1))
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_FC_Ritmo_DST = PLT_FrecuenciaCardiaca_DST.line('DistanciaAcumulada', 'VelocidadEscalada_FC', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_FC_Altitud_DST = PLT_FrecuenciaCardiaca_DST.line('DistanciaAcumulada', 'AltitudEscalada_FC', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_FC_Cadencia_DST = PLT_FrecuenciaCardiaca_DST.circle('DistanciaAcumulada', 'CadenciaEscalada_FC', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_FC_Temperatura_DST = PLT_FrecuenciaCardiaca_DST.step('DistanciaAcumulada', 'TemperaturaEscalada_FC', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_FC_Pendiente_DST = PLT_FrecuenciaCardiaca_DST.line('DistanciaAcumulada', 'PendienteEscalada_FC', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_FC_Desnivel_DST = PLT_FrecuenciaCardiaca_DST.line('DistanciaAcumulada', 'DesnivelPositivoEscalado_FC', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_FC_Zancada_DST = PLT_FrecuenciaCardiaca_DST.circle('DistanciaAcumulada', 'ZancadaEscalada_FC', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)
    
    DiccionarioLineasAuxiliares = {'FrecuenciaCardiaca':'XXX', 'Velocidad':PLT_FC_Ritmo_DST, 'Altitud':PLT_FC_Altitud_DST, 'Cadencia':PLT_FC_Cadencia_DST, \
            'Temperatura':PLT_FC_Temperatura_DST, 'Pendiente':PLT_FC_Pendiente_DST, 'DesnivelPositivoAcumulado':PLT_FC_Desnivel_DST, 'LongitudZancada':PLT_FC_Zancada_DST}

    # Atributos
    PLT_FrecuenciaCardiaca_DST.title.text = 'FRECUENCIA CARDIACA'
    PLT_FrecuenciaCardiaca_DST.sizing_mode = 'fixed'
    PLT_FrecuenciaCardiaca_DST.xaxis.axis_label = 'Distancia'
    PLT_FrecuenciaCardiaca_DST.xaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_FrecuenciaCardiaca_DST.yaxis.axis_label = 'Frecuencia cardiaca [ppm]'
    PLT_FrecuenciaCardiaca_DST.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_FrecuenciaCardiaca_DST.grid.visible = False
    PLT_FrecuenciaCardiaca_DST.yaxis.minor_tick_line_color = None
    PLT_FrecuenciaCardiaca_DST.yaxis.major_label_overrides = FormateoEjes(dfBokeh.FrecuenciaCardiacaCalculada, 10, 1)
    PLT_FrecuenciaCardiaca_DST.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_FrecuenciaCardiaca_DST.xaxis.major_label_overrides = FormateoEjes(dfBokeh.DistanciaAcumulada, 1000, 1000, 0, 0)


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
    
    CodigoJSFrecuenciaCardiaca.args = dict(l0=PLT_FC_Ritmo_DST, l1=PLT_FC_Altitud_DST, l2=PLT_FC_Cadencia_DST, l3=PLT_FC_Temperatura_DST, l4=PLT_FC_Pendiente_DST, l5=PLT_FC_Desnivel_DST, l6=PLT_FC_Zancada_DST, checkbox=BotonesGraficaFC)
 
   
    """
        VELOCIDAD | DISTANCIA
    """
    # Creacion de un grafica
    PLT_VelocidadCalculada_DST = figure(width= 1000, height= 400, x_range= (0, dfBokeh['DistanciaAcumulada'].max()), y_range= (MIN_Velocidad[0]-MIN_Velocidad[0]*0.1, MAX_Velocidad[0]+MAX_Velocidad[0]*0.2), tools= '', toolbar_location= None)
    
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['DistanciaAcumulada', 'VelocidadCalculada']].set_index('DistanciaAcumulada')
    dfBokehArea.rename(columns= {'VelocidadCalculada': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_VelocidadCalculada_DST.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_azul[5], alpha= 1, line_color= None)
    
    PLT_V_Linea_DST = PLT_VelocidadCalculada_DST.line('DistanciaAcumulada', 'VelocidadCalculada', source= DatosBokeh, line_width= 2, color= paleta_azul[6], line_cap= 'round')
    PLT_VelocidadCalculada_DST.add_layout(Span(location= AVG_Velocidad[0], dimension= 'width', line_color= paleta_azul[7], line_dash= 'dashed', line_width= 1, line_alpha= 1))
    PLT_VelocidadCalculada_DST.add_tools(HoverTool(tooltips=[('Ritmo', '@Ritmo_STR')], renderers= [PLT_V_Linea_DST], mode= 'vline'))
    
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_V_FrecuenciaCardiaca_DST = PLT_VelocidadCalculada_DST.line('DistanciaAcumulada', 'FrecuenciaCardiacaEscalada_Vel', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_V_Altitud_DST = PLT_VelocidadCalculada_DST.line('DistanciaAcumulada', 'AltitudEscalada_Vel', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_V_Cadencia_DST = PLT_VelocidadCalculada_DST.circle('DistanciaAcumulada', 'CadenciaEscalada_Vel', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_V_Temperatura_DST = PLT_VelocidadCalculada_DST.step('DistanciaAcumulada', 'TemperaturaEscalada_Vel', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_V_Pendiente_DST = PLT_VelocidadCalculada_DST.line('DistanciaAcumulada', 'PendienteEscalada_Vel', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_V_Desnivel_DST = PLT_VelocidadCalculada_DST.line('DistanciaAcumulada', 'DesnivelPositivoEscalado_Vel', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_V_Zancada_DST = PLT_VelocidadCalculada_DST.circle('DistanciaAcumulada', 'ZancadaEscalada_Vel', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)
    	
    # Atributos
    PLT_VelocidadCalculada_DST.title.text = 'RITMO INSTANTANEO'
    PLT_VelocidadCalculada_DST.sizing_mode = 'fixed'
    PLT_VelocidadCalculada_DST.xaxis.axis_label = 'Distancia'
    PLT_VelocidadCalculada_DST.xaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_VelocidadCalculada_DST.yaxis.axis_label = 'Ritmo [min/km]'
    PLT_VelocidadCalculada_DST.yaxis.formatter = NumeralTickFormatter(format= '0.0')
    PLT_VelocidadCalculada_DST.grid.visible = False
    PLT_VelocidadCalculada_DST.yaxis.minor_tick_line_color = None
    PLT_VelocidadCalculada_DST.yaxis.major_label_overrides = {1: '16:40', 1.5: '16:06', 2: '8:20', 2.5: '6:40', 3: '5:33', 3.5: '4:45', 4: '4:10', 4.5: '3:42', 5: '3:20', 5.5: '3:01', 6: '2:46', 6.5: '2:34', 7: '2:22'}
    PLT_VelocidadCalculada_DST.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_VelocidadCalculada_DST.xaxis.major_label_overrides = FormateoEjes(dfBokeh.DistanciaAcumulada, 1000, 1000, 0, 0)
    
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
    
    CodigoJSVelocidad.args = dict(l0=PLT_V_FrecuenciaCardiaca_DST, l1=PLT_V_Altitud_DST, l2=PLT_V_Cadencia_DST, l3=PLT_V_Temperatura_DST, l4=PLT_V_Pendiente_DST, l5=PLT_V_Desnivel_DST, l6=PLT_V_Zancada_DST, checkbox=BotonesGraficaVelocidad)


    """
    	ALTITUD | DISTANCIA
    """
    # Creacion de un grafica
    PLT_Altitud_DST = figure(width= 1000, height= 400, x_range= (0, dfBokeh['DistanciaAcumulada'].max()), y_range= (MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*OffsetInferiorAltitud, MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*OffsetSuperiorAltitud), tools= '', toolbar_location= None)
    
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['DistanciaAcumulada', 'AltitudCalculada']].set_index('DistanciaAcumulada')
    dfBokehArea.rename(columns= {'AltitudCalculada': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_Altitud_DST.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_verde[5], alpha= 1, line_color= None)
    
    PLT_ALT_Altitud_DST = PLT_Altitud_DST.line('DistanciaAcumulada', 'AltitudCalculada', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
    
    # Efectos visuales
    if DesnivelPorKilometro > 40:
        PLT_Altitud_DST.add_tools(HoverTool(tooltips=[('Distancia', '@DistanciaAcumulada{0.0} km'),('Altitud', '@AltitudCalculada{int} m'),('Desnivel positivo', '@DesnivelPositivoAcumulado{int} m'),('Pendiente', '@Pendiente{0.00}%')], renderers= [PLT_ALT_Altitud_DST], mode= 'vline'))
    else:
        PLT_Altitud_DST.add_tools(HoverTool(tooltips=[('Distancia', '@DistanciaAcumulada{0.0} km'),('Altitud', '@AltitudCalculada{int} m')], renderers= [PLT_ALT_Altitud_DST], mode= 'vline'))
    
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_ALT_FC_DST = PLT_Altitud_DST.line('DistanciaAcumulada', 'FrecuenciaCardiacaEscalada_Alt', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_ALT_Ritmo_DST = PLT_Altitud_DST.line('DistanciaAcumulada', 'VelocidadEscalada_Alt', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_ALT_Cadencia_DST = PLT_Altitud_DST.circle('DistanciaAcumulada', 'CadenciaEscalada_Alt', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_ALT_Temperatura_DST = PLT_Altitud_DST.step('DistanciaAcumulada', 'TemperaturaEscalada_Alt', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_ALT_Pendiente_DST = PLT_Altitud_DST.line('DistanciaAcumulada', 'PendienteEscalada_Alt', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_ALT_Desnivel_DST = PLT_Altitud_DST.line('DistanciaAcumulada', 'DesnivelPositivoEscalado_Alt', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_ALT_Zancada_DST = PLT_Altitud_DST.circle('DistanciaAcumulada', 'ZancadaEscalada_Alt', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)
    
    
    # Atributos
    PLT_Altitud_DST.title.text = 'ALTITUD'
    PLT_Altitud_DST.sizing_mode = 'fixed'
    PLT_Altitud_DST.xaxis.axis_label = 'Distancia'
    PLT_Altitud_DST.xaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Altitud_DST.yaxis.axis_label = 'Altitud [m]'
    PLT_Altitud_DST.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Altitud_DST.grid.visible = False
    PLT_Altitud_DST.yaxis.minor_tick_line_color = None
    PLT_Altitud_DST.yaxis.major_label_overrides = FormateoEjes(dfBokeh.AltitudCalculada, 100, 1)
    PLT_Altitud_DST.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_Altitud_DST.xaxis.major_label_overrides = FormateoEjes(dfBokeh.DistanciaAcumulada, 1000, 1000, 0, 0)
       
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
    
    CodigoJSAltitud.args = dict(l0=PLT_ALT_FC_DST, l1=PLT_ALT_Ritmo_DST, l2=PLT_ALT_Cadencia_DST, l3=PLT_ALT_Temperatura_DST, l4=PLT_ALT_Pendiente_DST, l5=PLT_ALT_Desnivel_DST, l6=PLT_ALT_Zancada_DST, checkbox=BotonesGraficaALT)
    

    """
    	CADENCIA | DISTANCIA
    """
    # Creacion de un grafica
    PLT_Cadencia_DST = figure(width= 1000, height= 400, x_range= (0, dfBokeh['DistanciaAcumulada'].max()), y_range= (MIN_Cadencia[0]-(MAX_Cadencia[0]-MIN_Cadencia[0])*0.03, MAX_Cadencia[0]+(MAX_Cadencia[0]-MIN_Cadencia[0])*0.1), tools= '', toolbar_location= None)
        
    # Inclusion de datos
    PLT_Cadencia_DST.circle('DistanciaAcumulada', 'CadenciaCalculada', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 1)
    PLT_C_Linea_DST = PLT_Cadencia_DST.line('DistanciaAcumulada', 'CadenciaCalculada', source= DatosBokehAGG, color= 'white', line_width= 0, line_alpha= 0)
    PLT_Cadencia_DST.add_tools(HoverTool(tooltips=[('', '@CadenciaCalculada')], renderers= [PLT_C_Linea_DST], mode= 'vline'))
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_C_FC_DST = PLT_Cadencia_DST.line('DistanciaAcumulada', 'FrecuenciaCardiacaEscalada_Cad', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_C_Ritmo_DST = PLT_Cadencia_DST.line('DistanciaAcumulada', 'VelocidadEscalada_Cad', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_C_Altitud_DST = PLT_Cadencia_DST.line('DistanciaAcumulada', 'AltitudEscalada_Cad', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_C_Temperatura_DST = PLT_Cadencia_DST.step('DistanciaAcumulada', 'TemperaturaEscalada_Cad', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_C_Pendiente_DST = PLT_Cadencia_DST.line('DistanciaAcumulada', 'PendienteEscalada_Cad', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_C_Desnivel_DST = PLT_Cadencia_DST.line('DistanciaAcumulada', 'DesnivelPositivoEscalado_Cad', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_C_Zancada_DST = PLT_Cadencia_DST.circle('DistanciaAcumulada', 'ZancadaEscalada_Cad', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)
       
     
    # Atributos
    PLT_Cadencia_DST.title.text = 'CADENCIA'
    PLT_Cadencia_DST.sizing_mode = 'fixed'
    PLT_Cadencia_DST.xaxis.axis_label = 'Distancia'
    PLT_Cadencia_DST.xaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Cadencia_DST.yaxis.axis_label = 'Cadencia [Pasos por minuto]'
    PLT_Cadencia_DST.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Cadencia_DST.grid.visible = False
    PLT_Cadencia_DST.yaxis.minor_tick_line_color = None
    PLT_Cadencia_DST.yaxis.major_label_overrides = FormateoEjes(dfBokeh.CadenciaCalculada, 10, 1)
    PLT_Cadencia_DST.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_Cadencia_DST.xaxis.major_label_overrides = FormateoEjes(dfBokeh.DistanciaAcumulada, 1000, 1000, 0, 0)
 
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
    
    CodigoJSCadencia.args = dict(l0=PLT_C_FC_DST, l1=PLT_C_Ritmo_DST, l2=PLT_C_Altitud_DST, l3=PLT_C_Temperatura_DST, l4=PLT_C_Pendiente_DST, l5=PLT_C_Desnivel_DST, l6=PLT_C_Zancada_DST, checkbox=BotonesGraficaCadencia)
 
 

    """
        TEMPERATURA AMBIENTE | DISTANCIA
    """
    # Creacion de un grafica
    PLT_Temperatura_DST = figure(width= 1000, height= 400, x_range= (0, dfBokeh['DistanciaAcumulada'].max()), y_range= (min(MIN_Temperatura[0], 0), MAX_Temperatura[0]+(MAX_Temperatura[0]-MIN_Temperatura[0])*0.1), tools= '', toolbar_location= None)
        
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['DistanciaAcumulada', 'TemperaturaAmbiente']].set_index('DistanciaAcumulada')
    dfBokehArea.rename(columns= {'TemperaturaAmbiente': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_Temperatura_DST.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_azul[3], alpha= 1, line_color= None)
        
    PLT_Temperatura_DST.step('DistanciaAcumulada', 'TemperaturaAmbiente', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_TMP_FC_DST = PLT_Temperatura_DST.line('DistanciaAcumulada', 'FrecuenciaCardiacaEscalada_Tem', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_TMP_Ritmo_DST = PLT_Temperatura_DST.line('DistanciaAcumulada', 'VelocidadEscalada_Tem', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_TMP_Altitud_DST = PLT_Temperatura_DST.line('DistanciaAcumulada', 'AltitudEscalada_Tem', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas) 
    PLT_TMP_Cadencia_DST = PLT_Temperatura_DST.circle('DistanciaAcumulada', 'CadenciaEscalada_Tem', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_TMP_Pendiente_DST = PLT_Temperatura_DST.line('DistanciaAcumulada', 'PendienteEscalada_Tem', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_TMP_Desnivel_DST = PLT_Temperatura_DST.line('DistanciaAcumulada', 'DesnivelPositivoEscalado_Tem', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_TMP_Zancada_DST = PLT_Temperatura_DST.circle('DistanciaAcumulada', 'ZancadaEscalada_Tem', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)   
    
    # Atributos
    PLT_Temperatura_DST.title.text = 'TEMPERATURA AMBIENTE'
    PLT_Temperatura_DST.sizing_mode = 'fixed'
    PLT_Temperatura_DST.xaxis.axis_label = 'Distancia'
    PLT_Temperatura_DST.xaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Temperatura_DST.yaxis.axis_label = 'Temperatura [ºC]'
    PLT_Temperatura_DST.yaxis.formatter = NumeralTickFormatter(format= '0,0')
    PLT_Temperatura_DST.grid.visible = False
    PLT_Temperatura_DST.yaxis.minor_tick_line_color = None
    PLT_Temperatura_DST.yaxis.major_label_overrides = FormateoEjes(dfBokeh.TemperaturaAmbiente, 5, 1)
    PLT_Temperatura_DST.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_Temperatura_DST.xaxis.major_label_overrides = FormateoEjes(dfBokeh.DistanciaAcumulada, 1000, 1000, 0, 0)
    
    
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
    
    CodigoJSTemperatura.args = dict(l0=PLT_TMP_FC_DST, l1=PLT_TMP_Ritmo_DST, l2=PLT_TMP_Altitud_DST, l3=PLT_TMP_Cadencia_DST, l4=PLT_TMP_Pendiente_DST, l5=PLT_TMP_Desnivel_DST, l6=PLT_TMP_Zancada_DST, checkbox=BotonesGraficaTMP)


    
    """
    	PENDIENTE | DISTANCIA
    """
    # Creacion de un grafica
    PLT_Pendiente_DST = figure(width= 1000, height= 400, x_range= (0, dfBokeh['DistanciaAcumulada'].max()), y_range= (MIN_Pendiente[0]-(MAX_Pendiente[0]-MIN_Pendiente[0])*0.05, MAX_Pendiente[0]+(MAX_Pendiente[0]-MIN_Pendiente[0])*0.05), tools= '', toolbar_location= None)
        
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['DistanciaAcumulada', 'Pendiente']].set_index('DistanciaAcumulada')
    dfBokehArea.rename(columns= {'Pendiente': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_Pendiente_DST.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_verde[5], alpha= 1, line_color= None)
        
    PLT_Pendiente_DST.line('DistanciaAcumulada', 'Pendiente', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_PEN_FC_DST = PLT_Pendiente_DST.line('DistanciaAcumulada', 'FrecuenciaCardiacaEscalada_Pen', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_PEN_Ritmo_DST = PLT_Pendiente_DST.line('DistanciaAcumulada', 'VelocidadEscalada_Pen', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_PEN_Altitud_DST = PLT_Pendiente_DST.line('DistanciaAcumulada', 'AltitudEscalada_Pen', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_PEN_Cadencia_DST = PLT_Pendiente_DST.circle('DistanciaAcumulada', 'CadenciaEscalada_Pen', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_PEN_Temperatura_DST = PLT_Pendiente_DST.step('DistanciaAcumulada', 'TemperaturaEscalada_Pen', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_PEN_Desnivel_DST = PLT_Pendiente_DST.line('DistanciaAcumulada', 'DesnivelPositivoEscalado_Pen', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_PEN_Zancada_DST = PLT_Pendiente_DST.circle('DistanciaAcumulada', 'ZancadaEscalada_Pen', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)   
     
    # Atributos
    PLT_Pendiente_DST.title.text = 'PENDIENTE'
    PLT_Pendiente_DST.sizing_mode = 'fixed'
    PLT_Pendiente_DST.xaxis.axis_label = 'Distancia'
    PLT_Pendiente_DST.xaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Pendiente_DST.yaxis.axis_label = 'Pendiente [%]'
    PLT_Pendiente_DST.yaxis.formatter = NumeralTickFormatter(format= '0,0')
    PLT_Pendiente_DST.grid.visible = False
    PLT_Pendiente_DST.yaxis.minor_tick_line_color = None
    PLT_Pendiente_DST.yaxis.major_label_overrides = FormateoEjes(dfBokeh.Pendiente, 1, 1)
    PLT_Pendiente_DST.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_Pendiente_DST.xaxis.major_label_overrides = FormateoEjes(dfBokeh.DistanciaAcumulada, 1000, 1000, 0, 0)
            
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
    
    CodigoJSPendiente.args = dict(l0=PLT_PEN_FC_DST, l1=PLT_PEN_Ritmo_DST, l2=PLT_PEN_Altitud_DST, l3=PLT_PEN_Cadencia_DST, l4=PLT_PEN_Temperatura_DST, l5=PLT_PEN_Desnivel_DST, l6=PLT_PEN_Zancada_DST, checkbox=BotonesGraficaPEN)

 

    """
        DESNIVEL POSITIVO ACUMULADO | DISTANCIA
    """
    # Creacion de un grafica
    PLT_DesnivelPositivo_DST = figure(width= 1000, height= 400, x_range= (0, dfBokeh['DistanciaAcumulada'].max()), y_range= (0, DesnivelPositivo+DesnivelPositivo*0.05), tools= '', toolbar_location= None)
        
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['DistanciaAcumulada', 'DesnivelPositivoAcumulado']].set_index('DistanciaAcumulada')
    dfBokehArea.rename(columns= {'DesnivelPositivoAcumulado': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_DesnivelPositivo_DST.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_verde[5], alpha= 1, line_color= None)
        
    PLT_DesnivelPositivo_DST.line('DistanciaAcumulada', 'DesnivelPositivoAcumulado', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
    
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_DPA_FC_DST = PLT_DesnivelPositivo_DST.line('DistanciaAcumulada', 'FrecuenciaCardiacaEscalada_Des', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas) 
    PLT_DPA_Ritmo_DST = PLT_DesnivelPositivo_DST.line('DistanciaAcumulada', 'VelocidadEscalada_Des', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_DPA_Altitud_DST = PLT_DesnivelPositivo_DST.line('DistanciaAcumulada', 'AltitudEscalada_Des', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_DPA_Cadencia_DST = PLT_DesnivelPositivo_DST.circle('DistanciaAcumulada', 'CadenciaEscalada_Des', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_DPA_Temperatura_DST = PLT_DesnivelPositivo_DST.step('DistanciaAcumulada', 'TemperaturaEscalada_Des', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_DPA_Pendiente_DST = PLT_DesnivelPositivo_DST.line('DistanciaAcumulada', 'PendienteEscalada_Des', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_DPA_Zancada_DST = PLT_DesnivelPositivo_DST.circle('DistanciaAcumulada', 'ZancadaEscalada_Des', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 0.7, visible= False)   
       
    # Atributos
    PLT_DesnivelPositivo_DST.title.text = 'DESNIVEL POSITIVO ACUMULADO'
    PLT_DesnivelPositivo_DST.sizing_mode = 'fixed'
    PLT_DesnivelPositivo_DST.xaxis.axis_label = 'Distancia'
    PLT_DesnivelPositivo_DST.xaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_DesnivelPositivo_DST.yaxis.axis_label = 'Desnivel positivo acumulado [m]'
    PLT_DesnivelPositivo_DST.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_DesnivelPositivo_DST.grid.visible = False
    PLT_DesnivelPositivo_DST.yaxis.minor_tick_line_color = None
    PLT_DesnivelPositivo_DST.yaxis.major_label_overrides = FormateoEjes(dfBokeh.DesnivelPositivoAcumulado, 100, 1)
    PLT_DesnivelPositivo_DST.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_DesnivelPositivo_DST.xaxis.major_label_overrides = FormateoEjes(dfBokeh.DistanciaAcumulada, 1000, 1000, 0, 0)
    
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
    
    CodigoJSDesnivelPositivo.args = dict(l0=PLT_DPA_FC_DST, l1=PLT_DPA_Ritmo_DST, l2=PLT_DPA_Altitud_DST, l3=PLT_DPA_Cadencia_DST, l4=PLT_DPA_Temperatura_DST, l5=PLT_DPA_Pendiente_DST, l6=PLT_DPA_Zancada_DST, checkbox=BotonesGraficaDPA)
        


    """
    	LONGITUD DE ZANCADA | DISTANCIA
    """
    # Creacion de un grafica
    PLT_Zancada_DST = figure(width= 1000, height= 400, x_range= (0, dfBokeh['DistanciaAcumulada'].max()), y_range= (MIN_LongitudZancada[0]-(MAX_LongitudZancada[0]-MIN_LongitudZancada[0])*0.03, MAX_LongitudZancada[0]+(MAX_LongitudZancada[0]-MIN_LongitudZancada[0])*0.1), tools= '', toolbar_location= None)
    
    # Inclusion de datos
    PLT_Zancada_DST.circle('DistanciaAcumulada', 'LongitudZancada', source= DatosBokehAGG, size= SizeCircle, line_color= transform('LongitudZancada', MapaColorZancada), color= transform('LongitudZancada', MapaColorZancada), fill_alpha= 1)
    PLT_Z_Linea_DST = PLT_Zancada_DST.line('DistanciaAcumulada', 'LongitudZancada', source= DatosBokehAGG, color= 'white', line_width= 0, line_alpha= 0)
    PLT_Zancada_DST.add_tools(HoverTool(tooltips=[('', '@LongitudZancada')], renderers= [PLT_Z_Linea_DST], mode= 'vline'))
        
    # Inclusion de lineas auxiliares
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_Z_FC_DST = PLT_Zancada_DST.line('DistanciaAcumulada', 'FrecuenciaCardiacaEscalada_Zan', source= DatosBokeh, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_Z_Ritmo_DST = PLT_Zancada_DST.line('DistanciaAcumulada', 'VelocidadEscalada_Zan', source= DatosBokeh, color= paleta_azul[6], **PropiedadesLineas)
    PLT_Z_Altitud_DST = PLT_Zancada_DST.line('DistanciaAcumulada', 'AltitudEscalada_Zan', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_Z_Cadencia_DST = PLT_Zancada_DST.circle('DistanciaAcumulada', 'CadenciaEscalada_Zan', source= DatosBokehAGG, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 0.7, visible= False)
    PLT_Z_Temperatura_DST = PLT_Zancada_DST.step('DistanciaAcumulada', 'TemperaturaEscalada_Zan', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_Z_Pendiente_DST = PLT_Zancada_DST.line('DistanciaAcumulada', 'PendienteEscalada_Zan', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
    PLT_Z_Desnivel_DST = PLT_Zancada_DST.line('DistanciaAcumulada', 'DesnivelPositivoEscalado_Zan', source= DatosBokeh, color= paleta_verde[6], **PropiedadesLineas)
        
    # Atributos
    PLT_Zancada_DST.title.text = 'LONGITUD DE ZANCADA'
    PLT_Zancada_DST.sizing_mode = 'fixed'
    PLT_Zancada_DST.xaxis.axis_label = 'Distancia'
    PLT_Zancada_DST.xaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Zancada_DST.yaxis.axis_label = 'Longitud de zancada [m]'
    PLT_Zancada_DST.yaxis.formatter = NumeralTickFormatter(format= '0')
    PLT_Zancada_DST.grid.visible = False
    PLT_Zancada_DST.yaxis.minor_tick_line_color = None
    PLT_Zancada_DST.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_Zancada_DST.xaxis.major_label_overrides = FormateoEjes(dfBokeh.DistanciaAcumulada, 1000, 1000, 0, 0)

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
    
    CodigoJSZancada.args = dict(l0=PLT_Z_FC_DST, l1=PLT_Z_Ritmo_DST, l2=PLT_Z_Altitud_DST, l3=PLT_Z_Cadencia_DST, l4=PLT_Z_Temperatura_DST, l5=PLT_Z_Pendiente_DST, l6=PLT_Z_Desnivel_DST, checkbox=BotonesGraficaZAN)
 

    
       
    """
        LAYOUT
    """
    
    GridBotonesFC = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaFC, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaFC = gridplot(
            [PLT_FrecuenciaCardiaca_DST, GridBotonesFC],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
 
    GridBotonesVEL = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaVelocidad, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaVEL = gridplot(
            [PLT_VelocidadCalculada_DST, GridBotonesVEL],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 
    
    GridBotonesALT = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaALT, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaALT = gridplot(
            [PLT_Altitud_DST, GridBotonesALT],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    
    GridBotonesCAD = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaCadencia, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaCAD = gridplot(
            [PLT_Cadencia_DST, GridBotonesCAD],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 
 
    GridBotonesTMP = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaTMP, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaTMP = gridplot(
            [PLT_Temperatura_DST, GridBotonesTMP],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 

    GridBotonesPEN = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaPEN, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaPEN = gridplot(
            [PLT_Pendiente_DST, GridBotonesPEN],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None)) 

    GridBotonesDPA = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaDPA, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaDPA = gridplot(
            [PLT_DesnivelPositivo_DST, GridBotonesDPA],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    
    GridBotonesZAN = layout(
            [Spacer(height= 20), widgetbox(BotonesGraficaZAN, width= 100)],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    GridGraficaZAN = gridplot(
            [PLT_Zancada_DST, GridBotonesZAN],
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
        
    GraficasDistancia = layout(
            ListadoGraficas,
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))

    return GraficasDistancia