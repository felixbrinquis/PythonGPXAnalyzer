# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este modulo contiene la funcion TabResumenMapa la cual crea un tablon donde se visualiza
la informacion en forma de mapa junto con otros valores medios o agregados totales de la actividad.
"""

"""
    IMPORTACION DE LIBRERIAS
"""
# Importacion de las funciones necesarias
from bokeh.io import output_file, show, curdoc
from bokeh.layouts import gridplot, layout, widgetbox, Spacer
from bokeh.models import ColumnDataSource, Span, HoverTool, CategoricalColorMapper, Rect, LinearColorMapper, NumeralTickFormatter, BoxAnnotation, LabelSet, Label, NumberFormatter, StringFormatter, CheckboxButtonGroup, CustomJS
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Panel, Tabs, PreText, RadioButtonGroup
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON
from bokeh.transform import linear_cmap, transform
from bokeh.palettes import Spectral6
import numpy as np
from datetime import timedelta
from math import ceil, floor, radians, pi, log, tan

from source.common.funciones import ConversorCoordenadasMercator, FormateoTiempos, CalculosVectoresAgregados, TablaParcialesKilometricos, HitosKilometricos, HitosPausas
from source.common.PaletasColores import paleta_rojo, paleta_verde, Spectral



def TabResumenMapa(NombreFichero, df):
    
    
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

    CoordenadasHitosKm, TiempoTotalKm, TiempoActividadKm, MinDistanciaKm = HitosKilometricos(df)
    CoordenadasPausas, TiempoTotalPausas, TiempoActividadPausas, DistanciasPausas = HitosPausas(df)

    AltitudInicio, AltitudFin = df.loc[df.index.min() == df.index, ['Altitud']].min()[0], df.loc[df.index.max() == df.index, ['Altitud']].min()[0]
 
    # Calculo de desniveles finales
    DesnivelPositivo = df['DesnivelPositivoAcumulado'].max()
    DesnivelNegativo = df['DesnivelNegativoAcumulado'].max()
    DesnivelAcumulado = DesnivelPositivo + DesnivelNegativo
    DesnivelPorKilometro = (DesnivelAcumulado/df['DistanciaAcumulada'].max())*1000

    # Seleccion de un subconjunto de datos para visualizar
    dfBokeh = df[['Bloque', 'Latitud', 'Longitud', 'DistanciaAcumulada', 'AltitudCalculada', 'VelocidadCalculada', 'Ritmo', 'FrecuenciaCardiaca', 'FrecuenciaCardiacaCalculada', 'CadenciaCalculada', 'LongitudZancada', 'DesnivelPositivoAcumulado', 'Pendiente']].copy()
    dfBokeh['Ritmo_STR'] = dfBokeh.Ritmo.dt.round('1s').dt.components['minutes'].astype(str).apply(lambda x: x.zfill(2))+':'+dfBokeh.Ritmo.dt.round('1s').dt.components['seconds'].astype(str).apply(lambda x: x.zfill(2))
    
    # Creacion de coordenadas Mercator en el DataFrame
    for index, row in dfBokeh.iterrows():
        LongitudMercator, LatitudMercator = ConversorCoordenadasMercator(row.Longitud, row.Latitud)
        dfBokeh.at[index,'LongitudMercator'] = LongitudMercator
        dfBokeh.at[index,'LatitudMercator'] = LatitudMercator

    dfTramosKm = TablaParcialesKilometricos(df)
    dfTramosKm['Ritmo_STR'] = dfTramosKm.Ritmo.apply(lambda x: FormateoTiempos(x, 'R'))

    # Creacion de los ColumnDataSource de origen de Bokeh
    DatosBokeh = ColumnDataSource(dfBokeh) 
    OrigenTramosKm = ColumnDataSource(dfTramosKm)



    """
        MAPA
    """
    # Creacion de un grafica
    PLT_Mapa = figure(width= 800, height= 450, x_range=(dfBokeh.LongitudMercator.min()-100, dfBokeh.LongitudMercator.max()+100), y_range=(dfBokeh.LatitudMercator.min()-100, dfBokeh.LatitudMercator.max()+100), x_axis_type= 'mercator', y_axis_type= 'mercator', tools= 'wheel_zoom, reset, hover')
    PLT_Mapa.add_tile(CARTODBPOSITRON)
    
    # Inclusion de datos
    PLT_MP_Linea = PLT_Mapa.line(x= 'LongitudMercator', y= 'LatitudMercator', source= DatosBokeh, line_color= paleta_rojo[7], line_width= 3, line_cap= 'round')
    #PLT_Mapa.circle(x= 'LongitudMercator', y= 'LatitudMercator', source= DatosBokeh, size= 5, line_color= None, fill_color= None, fill_alpha= 0, hover_fill_color= 'yellow', hover_line_color = 'black', hover_alpha= 1)
    #PLT_Mapa.add_tools(HoverTool(tooltips=None, mode='mouse'))
    
    # Ubicacion de puntos de inicio, fin y kilometros
    LongitudKm =[]
    LatitudKm =[]
    PuntoKilometrico = []
    for i, Km in enumerate(CoordenadasHitosKm):
        if i == 0:
            PLT_Mapa_Inicio = PLT_Mapa.circle(ConversorCoordenadasMercator(Km[1], Km[0])[0], ConversorCoordenadasMercator(Km[1], Km[0])[1], size= 8, line_color= 'black', fill_color= Spectral[2], visible= True)
        elif i == len(CoordenadasHitosKm)-1:
            PLT_Mapa_Fin = PLT_Mapa.circle(ConversorCoordenadasMercator(Km[1], Km[0])[0], ConversorCoordenadasMercator(Km[1], Km[0])[1], size= 8, line_color= 'black', fill_color= Spectral[7], visible= True)
        else:
            LongitudKm.append(ConversorCoordenadasMercator(Km[1], Km[0])[0])
            LatitudKm.append(ConversorCoordenadasMercator(Km[1], Km[0])[1])
            PuntoKilometrico.append(str(i))
    CDS_PuntosKm = ColumnDataSource(data= dict(Longitud= LongitudKm, Latitud= LatitudKm, PuntoKilometrico= PuntoKilometrico))
    PLT_Mapa_PuntoKm = PLT_Mapa.circle(x= 'Longitud', y= 'Latitud', source= CDS_PuntosKm, color= 'white', size= 8, line_color= 'black', fill_color= 'white', visible= True)
    PLT_Mapa_PuntoKm_TXT = LabelSet(x= 'Longitud', y= 'Latitud', text='PuntoKilometrico', level='glyph', x_offset= 5, y_offset= 0, source= CDS_PuntosKm, render_mode='canvas', text_font_size= '10pt', text_color= 'black', text_align= 'left', text_baseline= 'middle', text_font_style= 'bold', visible= True)
    PLT_Mapa.add_layout(PLT_Mapa_PuntoKm_TXT)
        
    # Ubicacion de pausas
    LongitudPausa =[]
    LatitudPausa =[]
    for i, Km in enumerate(CoordenadasPausas):
        LongitudPausa.append(ConversorCoordenadasMercator(Km[1], Km[0])[0])
        LatitudPausa.append(ConversorCoordenadasMercator(Km[1], Km[0])[1])
    PLT_Mapa_Pausas = PLT_Mapa.x(LongitudPausa, LatitudPausa, line_color= 'black', line_width= 2, fill_color= None, visible= False)
    
    
    # Identificacion de pico y valle en trails    
    if (DesnivelPorKilometro > 40) and (MAX_Altitud[0] >= (AltitudInicio + 50) and MAX_Altitud[0] >= (AltitudFin + 50)):
        PLT_Mapa_Cima = PLT_Mapa.triangle(dfBokeh[dfBokeh['AltitudCalculada']==MAX_Altitud[0]]['LongitudMercator'].min(), dfBokeh[dfBokeh['AltitudCalculada']==MAX_Altitud[0]]['LatitudMercator'].min(), size= 10, line_color= 'black', line_width= 2, fill_color= Spectral[4], visible= False)
        PLT_Mapa_Cima_TXT = Label(x= dfBokeh[dfBokeh['AltitudCalculada']==MAX_Altitud[0]]['LongitudMercator'].min(), y= dfBokeh[dfBokeh['AltitudCalculada']==MAX_Altitud[0]]['LatitudMercator'].min(), text= str(round(MAX_Altitud[0])), x_offset= 5, y_offset= 0, text_font_size= '10pt', text_color= 'black', text_align= 'left', text_baseline= 'middle', text_font_style= 'bold', visible= False)
        PLT_Mapa.add_layout(PLT_Mapa_Cima_TXT)
    else:
        PLT_Mapa_Cima = PLT_Mapa.triangle(0, 0, size= 0, line_alpha= 0, visible= False)
        PLT_Mapa_Cima_TXT = Label(x= 0, y= 0, text= '', text_font_size= '0pt', text_alpha= 0, visible= False)
        
    if (DesnivelPorKilometro > 40) and (MIN_Altitud[0] <= (AltitudInicio - 50) and MIN_Altitud[0] <= (AltitudFin - 50)):    
        PLT_Mapa_Valle = PLT_Mapa.inverted_triangle(dfBokeh[dfBokeh['AltitudCalculada']==MIN_Altitud[0]]['LongitudMercator'].min(), dfBokeh[dfBokeh['AltitudCalculada']==MIN_Altitud[0]]['LatitudMercator'].min(), size= 10, line_color= 'black', line_width= 2, fill_color= Spectral[0], visible= False)
        PLT_Mapa_Valle_TXT = Label(x= dfBokeh[dfBokeh['AltitudCalculada']==MIN_Altitud[0]]['LongitudMercator'].min(), y= dfBokeh[dfBokeh['AltitudCalculada']==MIN_Altitud[0]]['LatitudMercator'].min(), text= str(round(MIN_Altitud[0])), x_offset= 5, y_offset= 0, text_font_size= '10pt', text_color= 'black', text_align= 'left', text_baseline= 'middle', text_font_style= 'bold', visible= False)
        PLT_Mapa.add_layout(PLT_Mapa_Valle_TXT)
    else:
        PLT_Mapa_Valle = PLT_Mapa.inverted_triangle(0, 0, size= 0, line_alpha= 0, visible= False)
        PLT_Mapa_Valle_TXT = Label(x= 0, y= 0, text= '', text_font_size= '0pt', text_alpha= 0, visible= False)
    
    # Atributos
    PLT_Mapa.sizing_mode = 'fixed'
    PLT_Mapa.xaxis.major_tick_line_color = None
    PLT_Mapa.xaxis.minor_tick_line_color = None
    PLT_Mapa.yaxis.major_tick_line_color = None
    PLT_Mapa.yaxis.minor_tick_line_color = None
    PLT_Mapa.xaxis.major_label_text_font_size = '0pt'
    PLT_Mapa.yaxis.major_label_text_font_size = '0pt'
    PLT_Mapa.grid.visible = False
    PLT_Mapa.toolbar.autohide = True
    # Sin bordes
    PLT_Mapa.min_border_left = 0
    PLT_Mapa.min_border_right = 0
    PLT_Mapa.min_border_top = 0
    PLT_Mapa.min_border_bottom = 0
    # Linea exterior
    PLT_Mapa.outline_line_width = 3
    PLT_Mapa.outline_line_alpha = 0.3
    PLT_Mapa.outline_line_color = 'black'


    """
        DATOS EN FORMA DE TABLA POR PARCIALES KILOMETRICOS
    """
    TablaKmResumen = [
            TableColumn(field= 'TramoKm', title= 'Km', width= 40, default_sort= 'ascending', sortable= False, formatter= StringFormatter(font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'Ritmo_STR', title= 'Ritmo[min/Km]', width= 80, default_sort= 'ascending', sortable= False, formatter= StringFormatter(font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'FrecuenciaCardiaca', title= 'FC[ppm]', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'Cadencia', title= 'Cadencia[ppm]', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'DesnivelAcumulado', title= 'Desnivel', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black'))
        ]
    PLT_TablaKmResumen = DataTable(source= OrigenTramosKm, columns= TablaKmResumen, width= 360, height= 550, fit_columns= False, sortable= False, reorderable= False, selectable= True, editable= False, index_position= None, header_row= True, row_height= 25)


    """
        ALTITUD SEGUIMIENTO MAPA
    """
    # Factor de achatamiento de la altitud
    if DesnivelPorKilometro > 40:
        OffsetSuperior = 0.1
        OffsetInferior = 0.03
    else:
        OffsetSuperior = 2.5
        OffsetInferior = 0.5
    
    # Creacion de un grafica
    PLT_AltitudMapa = figure(width= 800, height= 150, x_range= (0, df['DistanciaAcumulada'].max()), y_range= (MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*OffsetInferior, MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*OffsetSuperior), tools= '', toolbar_location= None)
    
    # Inclusion de datos
    dfBokehArea = dfBokeh.copy().reset_index()[['DistanciaAcumulada', 'AltitudCalculada']].set_index('DistanciaAcumulada')
    dfBokehArea.rename(columns= {'AltitudCalculada': 'Area'}, inplace=True)
    dfBokehAreaBottom = dfBokehArea[::-1]
    dfBokehAreaBottom['Area'] = 0
    PLT_AltitudMapa.patch(x= np.hstack((dfBokehAreaBottom.index, dfBokehArea.index)), y= np.hstack((dfBokehAreaBottom['Area'], dfBokehArea['Area'])), color= paleta_verde[5], alpha= 1, line_color= None)
    
    PLT_AltitudMapa.line('DistanciaAcumulada', 'AltitudCalculada', source= DatosBokeh, color= paleta_verde[6], line_width= 2, line_cap= 'round')
       
    PLT_AltitudMapa.add_tools(HoverTool(tooltips=[('', '@DistanciaAcumulada{0.0} km')], mode= 'vline'))
       
    # Atributos
    PLT_AltitudMapa.title.text = None
    PLT_AltitudMapa.sizing_mode = 'fixed'
    PLT_AltitudMapa.xaxis.axis_label = None
    PLT_AltitudMapa.yaxis.axis_label = None
    PLT_AltitudMapa.grid.visible = False
    PLT_AltitudMapa.xaxis.major_tick_line_color = None
    PLT_AltitudMapa.xaxis.minor_tick_line_color = None
    PLT_AltitudMapa.yaxis.major_tick_line_color = None
    PLT_AltitudMapa.yaxis.minor_tick_line_color = None
    PLT_AltitudMapa.xaxis.major_label_text_font_size = '0pt'
    PLT_AltitudMapa.yaxis.major_label_text_font_size = '0pt'
       
    
    """
        RESUMEN DE LA ACTIVIDAD
    """
    AnchuraCelda = 120
    AlturaCelda = 40
    
    # TITULO
    Resumen_Titulo = figure(width= AnchuraCelda*3, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_Titulo.add_layout(Label(x= 5, y= AlturaCelda/2, text= NombreFichero, x_offset= 2, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'left', text_baseline= 'top', text_alpha= 1, text_font_size= '14pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_Titulo.outline_line_color = None
    Resumen_Titulo.min_border_left = 0
    Resumen_Titulo.min_border_right = 0
    Resumen_Titulo.min_border_top = 0
    Resumen_Titulo.min_border_bottom = 0
    
    #FECHA Y HORA DE INICIO
    Resumen_Fecha = figure(width= AnchuraCelda*3, height= round(AlturaCelda/1.8), tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_Fecha.add_layout(Label(x= 5, y= AlturaCelda/2, text= df.index.min().strftime("%d/%m/%Y, %H:%M:%S"), x_offset= 2, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'left', text_baseline= 'top', text_alpha= 1, text_font_size= '10pt', text_font_style= 'italic', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_Fecha.outline_line_color = None
    Resumen_Fecha.min_border_left = 0
    Resumen_Fecha.min_border_right = 0
    Resumen_Fecha.min_border_top = 0
    Resumen_Fecha.min_border_bottom = 0
    
    
    Resumen_Distancia = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_Distancia.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(round(df['DistanciaAcumulada'].max()/1000, 2))+'km', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_Distancia.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Distancia', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_Distancia.outline_line_color = None
    Resumen_Distancia.min_border_left = 0
    Resumen_Distancia.min_border_right = 0
    Resumen_Distancia.min_border_top = 0
    Resumen_Distancia.min_border_bottom = 0
    
    
    Resumen_Duracion = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_Duracion.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= FormateoTiempos(df['TiempoActividad'].max(), 'T'), x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_Duracion.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Duracion', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_Duracion.outline_line_color = None
    Resumen_Duracion.min_border_left = 0
    Resumen_Duracion.min_border_right = 0
    Resumen_Duracion.min_border_top = 0
    Resumen_Duracion.min_border_bottom = 0
    
    Resumen_TiempoTranscurrido = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_TiempoTranscurrido.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= FormateoTiempos(df['TiempoTotal'].max(), 'T'), x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_TiempoTranscurrido.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Tiempo transcurrido', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_TiempoTranscurrido.outline_line_color = None
    Resumen_TiempoTranscurrido.min_border_left = 0
    Resumen_TiempoTranscurrido.min_border_right = 0
    Resumen_TiempoTranscurrido.min_border_top = 0
    Resumen_TiempoTranscurrido.min_border_bottom = 0
    
    
    Resumen_Ritmo = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_Ritmo.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= FormateoTiempos(timedelta(seconds=1000/np.divide(df['DistanciaAcumulada'].max(), df['TiempoActividad'].max().total_seconds())), 'R')+'/km', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_Ritmo.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Ritmo medio', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_Ritmo.outline_line_color = None
    Resumen_Ritmo.min_border_left = 0
    Resumen_Ritmo.min_border_right = 0
    Resumen_Ritmo.min_border_top = 0
    Resumen_Ritmo.min_border_bottom = 0
    
    
    Resumen_FC = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_FC.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(round(AVG_FrecuenciaCardiaca[0]))+'ppm', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_FC.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'FC media', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_FC.outline_line_color = None
    Resumen_FC.min_border_left = 0
    Resumen_FC.min_border_right = 0
    Resumen_FC.min_border_top = 0
    Resumen_FC.min_border_bottom = 0
    
    
    Resumen_DesnivelPositivo = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_DesnivelPositivo.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(int(round(DesnivelPositivo)))+'m', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_DesnivelPositivo.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Desnivel positivo', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_DesnivelPositivo.outline_line_color = None
    Resumen_DesnivelPositivo.min_border_left = 0
    Resumen_DesnivelPositivo.min_border_right = 0
    Resumen_DesnivelPositivo.min_border_top = 0
    Resumen_DesnivelPositivo.min_border_bottom = 0
    
    Resumen_DesnivelNegativo = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_DesnivelNegativo.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(int(round(DesnivelNegativo)))+'m', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_DesnivelNegativo.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Desnivel negativo', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_DesnivelNegativo.outline_line_color = None
    Resumen_DesnivelNegativo.min_border_left = 0
    Resumen_DesnivelNegativo.min_border_right = 0
    Resumen_DesnivelNegativo.min_border_top = 0
    Resumen_DesnivelNegativo.min_border_bottom = 0
    
    Resumen_DesnivelAcumulado = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_DesnivelAcumulado.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(int(round(DesnivelAcumulado)))+'m', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_DesnivelAcumulado.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Desnivel aumulado', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_DesnivelAcumulado.outline_line_color = None
    Resumen_DesnivelAcumulado.min_border_left = 0
    Resumen_DesnivelAcumulado.min_border_right = 0
    Resumen_DesnivelAcumulado.min_border_top = 0
    Resumen_DesnivelAcumulado.min_border_bottom = 0
    
    Resumen_Zancada = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_Zancada.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(round(AVG_LongitudZancada[0], 2))+'m', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_Zancada.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Zancada media', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_Zancada.outline_line_color = None
    Resumen_Zancada.min_border_left = 0
    Resumen_Zancada.min_border_right = 0
    Resumen_Zancada.min_border_top = 0
    Resumen_Zancada.min_border_bottom = 0
    
    Resumen_PendienteMax = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_PendienteMax.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(round(MAX_Pendiente[0], 2))+'%', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_PendienteMax.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Pendiente máxima', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_PendienteMax.outline_line_color = None
    Resumen_PendienteMax.min_border_left = 0
    Resumen_PendienteMax.min_border_right = 0
    Resumen_PendienteMax.min_border_top = 0
    Resumen_PendienteMax.min_border_bottom = 0
    
    Resumen_PendienteMin = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_PendienteMin.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(round(MIN_Pendiente[0], 2))+'%', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_PendienteMin.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Pendiente mínima', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_PendienteMin.outline_line_color = None
    Resumen_PendienteMin.min_border_left = 0
    Resumen_PendienteMin.min_border_right = 0
    Resumen_PendienteMin.min_border_top = 0
    Resumen_PendienteMin.min_border_bottom = 0
    
    
    Resumen_AltitudMax = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_AltitudMax.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(int(round(MAX_Altitud[0])))+'m', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_AltitudMax.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Altitud máxima', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_AltitudMax.outline_line_color = None
    Resumen_AltitudMax.min_border_left = 0
    Resumen_AltitudMax.min_border_right = 0
    Resumen_AltitudMax.min_border_top = 0
    Resumen_AltitudMax.min_border_bottom = 0
    
    
    Resumen_AltitudMin = figure(width= AnchuraCelda, height= AlturaCelda, tools= '', toolbar_location= None, x_axis_location= None, y_axis_location= None)
    Resumen_AltitudMin.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(int(round(MIN_Altitud[0])))+'m', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
    Resumen_AltitudMin.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= 'Altitud mínima', x_offset= 0, y_offset= 12, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'steelblue', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '8pt', text_font_style= 'normal', border_line_color= None, border_line_alpha= 0,background_fill_color= None, background_fill_alpha= 0))
    Resumen_AltitudMin.outline_line_color = None
    Resumen_AltitudMin.min_border_left = 0
    Resumen_AltitudMin.min_border_right = 0
    Resumen_AltitudMin.min_border_top = 0
    Resumen_AltitudMin.min_border_bottom = 0
    
    
    # Seleccion del formato a mostrar
    if DesnivelPorKilometro > 40: #Trail
        PLT_Resumen_Datos = layout(
                [[Resumen_Titulo],
                 [Resumen_Fecha],
                 [Resumen_Distancia, Resumen_Duracion, Resumen_TiempoTranscurrido],
                 [Resumen_DesnivelAcumulado, Resumen_FC, Resumen_Ritmo],
                 [Resumen_AltitudMax, Resumen_DesnivelPositivo, Resumen_PendienteMax],
                 [Resumen_AltitudMin, Resumen_DesnivelNegativo, Resumen_PendienteMin]],
                 merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    else: #Asfalto
        PLT_Resumen_Datos = layout(
                [[Resumen_Titulo],
                 [Resumen_Fecha],
                 [Resumen_Distancia, Resumen_Duracion, Resumen_Ritmo],
                 [Resumen_FC, Resumen_DesnivelPositivo, Resumen_Zancada]],
                 merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))


    """
        BOTONES
    """
    
    CodigoJS = """
    var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
    
    l0.visible = indexOf.call(checkbox.active,0)>=0;
    l1.visible = indexOf.call(checkbox.active,0)>=0;
    
    l2.visible = indexOf.call(checkbox.active,1)>=0;
    l3.visible = indexOf.call(checkbox.active,1)>=0;
    
    l4.visible = indexOf.call(checkbox.active,2)>=0;
    l5.visible = indexOf.call(checkbox.active,2)>=0;
    
    l6.visible = indexOf.call(checkbox.active,2)>=0;
    l7.visible = indexOf.call(checkbox.active,2)>=0;
    
    l8.visible = indexOf.call(checkbox.active,3)>=0;
    """
    
    CodigoJSMapa = CustomJS(code=CodigoJS, args={})
    
    BotonesMapa = CheckboxButtonGroup(labels=["INICIO/FIN", "PUNTOS KILOMETRICOS", "CIMA/VALLE", 'PAUSAS'], active=[0, 1], callback=CodigoJSMapa, width= 500)
    
    CodigoJSMapa.args = dict(l0=PLT_Mapa_Inicio, l1=PLT_Mapa_Fin, l2=PLT_Mapa_PuntoKm, l3= PLT_Mapa_PuntoKm_TXT, l4=PLT_Mapa_Cima, l5=PLT_Mapa_Cima_TXT, l6=PLT_Mapa_Valle, l7=PLT_Mapa_Valle_TXT, l8=PLT_Mapa_Pausas, checkbox= BotonesMapa)


    """
        LAYOUT
    """
    GridResumenInicio = layout(
            [PLT_Resumen_Datos, PLT_TablaKmResumen],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    
    GridMapaAltitud= layout(
            [PLT_Mapa, widgetbox(BotonesMapa, width= 500), PLT_AltitudMapa],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    
    TabMapa = gridplot(
            [GridMapaAltitud, GridResumenInicio],
            ncols= 2, merge_tools= True, sizing_mode='fixed', toolbar_location='left', toolbar_options=dict(logo=None))
    
    return TabMapa