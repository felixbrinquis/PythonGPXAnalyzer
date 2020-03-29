# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este modulo contiene la funcion TabParcialesKilometricos la cual crea un tablon donde se visualiza
mediante un diagrama de barras verticales el ritmo medio por cada kilometro. Tambien pueden superponerse otras
metricas de manera opcional.
"""

"""
    IMPORTACION DE LIBRERIAS
"""
# Importacion de las funciones necesarias
from bokeh.layouts import gridplot, layout, widgetbox, Spacer
from bokeh.models import ColumnDataSource, Span, HoverTool, LinearColorMapper, NumberFormatter, StringFormatter, CheckboxButtonGroup, NumeralTickFormatter, CustomJS, Column
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models.tickers import SingleIntervalTicker
from bokeh.plotting import figure
from bokeh.transform import transform

import numpy as np
from source.common.funciones import FormateoTiempos, Reescalado, CalculosVectoresAgregados, TablaParcialesKilometricos, FormateoEjes
from source.common.PaletasColores import paleta_rojo, paleta_verde, paleta_cadencia


def TabParcialesKilometricos(df):
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
        
    dfTramosKm = TablaParcialesKilometricos(df)
    dfTramosKm['Ritmo_STR'] = dfTramosKm.Ritmo.apply(lambda x: FormateoTiempos(x, 'R'))
    
    # Seleccion de un subconjunto de datos para visualizar
    dfBokehParcialesKM = df[['Bloque', 'DistanciaAcumulada', 'AltitudCalculada', 'FrecuenciaCardiacaCalculada', 'CadenciaCalculada']].copy()
    dfBokehParcialesKM['AltitudEscalada'] = Reescalado(dfBokehParcialesKM['AltitudCalculada'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*OffsetInferiorAltitud, MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*OffsetSuperiorAltitud], [0, dfTramosKm.Velocidad.max()])
    dfBokehParcialesKM['FrecuenciaCardiacaEscalada'] = Reescalado(dfBokehParcialesKM['FrecuenciaCardiacaCalculada'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [0, dfTramosKm.Velocidad.max()])
    dfBokehParcialesKM['CadenciaEscalada'] = Reescalado(dfBokehParcialesKM['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]], [0, dfTramosKm.Velocidad.max()])

    #  Reducion de la frecuencia de muestreo
    dfBokehParcialesKM_Agg = dfBokehParcialesKM.groupby('Bloque').resample('10S').agg({'DistanciaAcumulada': np.max, 'CadenciaCalculada': np.mean})
    dfBokehParcialesKM_Agg['CadenciaCalculada'] = dfBokehParcialesKM_Agg['CadenciaCalculada'].round()
    dfBokehParcialesKM_Agg['CadenciaEscalada'] = Reescalado(dfBokehParcialesKM_Agg['CadenciaCalculada'], [MIN_Cadencia[0], MAX_Cadencia[0]], [0, dfTramosKm.Velocidad.max()])
    
    # Creacion de los ColumnDataSource de origen de Bokeh
    OrigenParcialesKM = ColumnDataSource(dfBokehParcialesKM) 
    OrigenParcialesKM_Agg = ColumnDataSource(dfBokehParcialesKM_Agg)
    OrigenTramosKm = ColumnDataSource(dfTramosKm)
    
 
    # Asignacion de tamaño segun el total de puntos
    if df['DistanciaAcumulada'].max() < 5:
        SizeCircle = 10
    elif df['DistanciaAcumulada'].max() <10:
        SizeCircle = 8
    else:
        SizeCircle = 5
    
    # Definicion de la paleta de colores por cadencia
    MapaColorCadencia = LinearColorMapper(palette= paleta_cadencia, low= 110, high= 190)    
        
    """
        TRAMOS KILOMETRICOS | STRAVA
    """
    PLT_TramosKm = figure(plot_width= 900, plot_height= 500, x_range= (0, df['DistanciaAcumulada'].max()), y_range= (0, dfTramosKm.Velocidad.max()*1.1), tools= '', toolbar_location= None)
    PLT_TramosKm.add_layout(Span(location= AVG_Velocidad[0], dimension= 'width', line_color= 'deepskyblue', line_dash= 'dashed', line_width= 0.1, line_alpha= 0.3))
    PLT_BarrasKM = PLT_TramosKm.rect(x= 'x', y= 'y', width= 'Distancia', height= 'Velocidad', source= OrigenTramosKm, line_width= 1, line_color= 'skyblue', fill_color= 'dodgerblue')
    PLT_TramosKm.add_tools(HoverTool(tooltips=[('', '@Ritmo_STR')], renderers= [PLT_BarrasKM], mode= 'mouse'))
    
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_TramosKM_Altitud = PLT_TramosKm.line('DistanciaAcumulada', 'AltitudEscalada', source= OrigenParcialesKM, color= paleta_verde[6], **PropiedadesLineas)
    PLT_TramosKM_FC = PLT_TramosKm.line('DistanciaAcumulada', 'FrecuenciaCardiacaEscalada', source= OrigenParcialesKM, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_TramosKM_Cadencia = PLT_TramosKm.circle('DistanciaAcumulada', 'CadenciaEscalada', source= OrigenParcialesKM_Agg, size= SizeCircle, line_color= transform('CadenciaCalculada', MapaColorCadencia), color= transform('CadenciaCalculada', MapaColorCadencia), fill_alpha= 1, visible= False)
    
    # Atributos
    PLT_TramosKm.title.text = 'RITMO MEDIO KILOMETRICO'
    PLT_TramosKm.sizing_mode = 'fixed'
    PLT_TramosKm.xaxis.axis_label = 'Distancia'
    PLT_TramosKm.xaxis.formatter = NumeralTickFormatter(format= '0 a')
    PLT_TramosKm.yaxis.axis_label = 'Ritmo [min/km]'
    PLT_TramosKm.grid.visible = False
    PLT_TramosKm.yaxis.major_label_overrides = {1: '16:40', 1.5: '16:06', 2: '8:20', 2.5: '6:40', 3: '5:33', 3.5: '4:45', 4: '4:10', 4.5: '3:42', 5: '3:20', 5.5: '3:01', 6: '2:46', 6.5: '2:34', 7: '2:22'}
    PLT_TramosKm.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_TramosKm.xaxis.major_label_overrides = FormateoEjes(df.DistanciaAcumulada, 1000, 1000, 0, 0)

     
    """
        DATOS EN FORMA DE TABLA POR PARCIALES KILOMETRICOS
    """
    TablaKm = [
            TableColumn(field= 'TramoKm', title= 'Km', width= 40, default_sort= 'ascending', sortable= False, formatter= StringFormatter(font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'Ritmo_STR', title= 'Ritmo[min/Km]', width= 80, default_sort= 'ascending', sortable= False, formatter= StringFormatter(font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'FrecuenciaCardiaca', title= 'FC[ppm]', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'Cadencia', title= 'Cadencia[ppm]', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'DesnivelAcumulado', title= 'Desnivel', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black'))
        ]
    PLT_TablaKm = DataTable(source= OrigenTramosKm, columns= TablaKm, width= 360, height= 550, fit_columns= False, sortable= False, reorderable= False, selectable= True, editable= False, index_position= None, header_row= True, row_height= 25)
    

    """
        BOTONES
    """
    
    CodigoJS = """
    var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
    
    l0.visible = indexOf.call(checkbox.active,0)>=0;
    l1.visible = indexOf.call(checkbox.active,1)>=0;
    l2.visible = indexOf.call(checkbox.active,2)>=0;
    """
    BotonesTramosKm = CheckboxButtonGroup(labels=["Altitud", "Frecuencia Cardiaca", "Cadencia"], active=[], width=300, height=30)
    CodigoJSTramosKm = CustomJS(code=CodigoJS, args=dict(l0=PLT_TramosKM_Altitud, l1=PLT_TramosKM_FC, l2=PLT_TramosKM_Cadencia, checkbox=BotonesTramosKm))
    BotonesTramosKm.js_on_click(CodigoJSTramosKm)
    
    
    """
        LAYOUT
    """
    GridGraficaTramosKm = layout([Column(PLT_TramosKm, width=900, height=500), [Spacer(width=300, height=30), Column(BotonesTramosKm, width=300, height=30), Spacer(width=300, height=30)]], sizing_mode='stretch_width', width=900, height=570)
    GridTablaTramosKm = layout([Spacer(width=360, height= 25), Column(PLT_TablaKm, width=360, height=550)], sizing_mode='stretch_width', width=360, height=570)   
    GridAnalisisKm = gridplot([GridGraficaTramosKm, GridTablaTramosKm], ncols= 2, sizing_mode='stretch_width', toolbar_location=None, plot_width=1000, plot_height=570)
    
    return GridAnalisisKm