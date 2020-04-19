# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 01:10:23 2020

@author: Felix
"""

"""
    IMPORTACION DE LIBRERIAS
"""
# Importacion de las funciones necesarias
from bokeh.io import output_file, show, curdoc
from bokeh.layouts import gridplot, layout, widgetbox, Spacer
from bokeh.models import ColumnDataSource, Span, HoverTool, CategoricalColorMapper, Rect, LinearColorMapper, NumeralTickFormatter, BoxAnnotation, LabelSet, Label, NumberFormatter, StringFormatter, CheckboxButtonGroup, CustomJS, Column, Row
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Panel, Tabs, PreText, RadioButtonGroup
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors
from bokeh.transform import linear_cmap, transform
from bokeh.palettes import Spectral6
import numpy as np
from datetime import timedelta
from math import ceil, floor, radians, pi, log, tan

from source.common.Funciones_Generales import ConversorCoordenadasMercator, FormateoTiempos, FormulaKarvonen, Reescalado, LecturaBBDDActividades, EscrituraBBDDActividades, GeneracionCodigoJS, CreacionDirectoriosProyecto
from source.common.Funciones_DataFrame import CalculosVectoresAgregados, HitosKilometricos, HitosPausas, TablaParcialesKilometricos, TablaParcialesPausas, TablaZonasCardiacas, IdentificacionTipoActividad, LecturaBBDDActividades, AnalisisActividadActual, DeteccionVariables
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables, FunctionSizeCircle

from source.common.PaletasColores import paleta_rojo, paleta_verde, Spectral, Grapefruit, Mint


def Mapa(dfBokeh, DatosBokeh):
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
    AVG_Pendiente, MAX_Pendiente , MIN_Pendiente = CalculosVectoresAgregados(dfBokeh)

    AltitudInicio, AltitudFin = dfBokeh.loc[dfBokeh.index.min() == dfBokeh.index, ['Altitud']].min()[0], dfBokeh.loc[dfBokeh.index.max() == dfBokeh.index, ['Altitud']].min()[0]
    # Calculo de desniveles finales
    DesnivelPositivo = dfBokeh['DesnivelPositivoAcumulado'].max()
    DesnivelNegativo = dfBokeh['DesnivelNegativoAcumulado'].max()
    DesnivelAcumulado = DesnivelPositivo + DesnivelNegativo
    DesnivelPorKilometro = (DesnivelAcumulado/dfBokeh['Distancia'].max())*1000
    
    """
        MAPA
        
        CARTODBPOSITRON
        CARTODBPOSITRON_RETINA
        STAMEN_TERRAIN
        STAMEN_TERRAIN_RETINA
        STAMEN_TONER
        STAMEN_TONER_BACKGROUND
        STAMEN_TONER_LABELS
    """
    # Creacion de un grafica
    PLT_Mapa = figure(width=900, height=430, x_range=(DatosBokeh.data['LongitudMercator'].min()-100, DatosBokeh.data['LongitudMercator'].max()+100), y_range=(DatosBokeh.data['LatitudMercator'].min()-100, DatosBokeh.data['LatitudMercator'].max()+100), x_axis_type= 'mercator', y_axis_type= 'mercator', tools= 'wheel_zoom, reset, hover')
    PLT_Mapa.add_tile(get_provider('STAMEN_TERRAIN'))
    
    # Inclusion de datos
    PLT_MP_Linea = PLT_Mapa.line(x= 'LongitudMercator', y= 'LatitudMercator', source= DatosBokeh, line_color= Grapefruit[2], line_width= 3, line_cap= 'round')
    """
    #PLT_Mapa.circle(x= 'LongitudMercator', y= 'LatitudMercator', source= DatosBokeh, size= 5, line_color= None, fill_color= None, fill_alpha= 0, hover_fill_color= 'yellow', hover_line_color = 'black', hover_alpha= 1)
    #PLT_Mapa.add_tools(HoverTool(tooltips=None, mode='mouse'))
    """
    
    CoordenadasHitosKm, TiempoTotalKm, TiempoActividadKm, MinDistanciaKm = HitosKilometricos(dfBokeh)
    CoordenadasPausas, TiempoTotalPausas, TiempoActividadPausas, DistanciasPausas = HitosPausas(dfBokeh)
    
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
    for index, row in dfBokeh.iterrows():
        LongitudMercator, LatitudMercator = ConversorCoordenadasMercator(row.Longitud, row.Latitud)
        dfBokeh.at[index,'LongitudMercator'] = LongitudMercator
        dfBokeh.at[index,'LatitudMercator'] = LatitudMercator
        
    if (DesnivelPorKilometro > 40) and (MAX_Altitud[0] >= (AltitudInicio + 50) and MAX_Altitud[0] >= (AltitudFin + 50)):
        PLT_Mapa_Cima = PLT_Mapa.triangle(dfBokeh[dfBokeh['Altitud']==MAX_Altitud[0]]['LongitudMercator'].min(), dfBokeh[dfBokeh['Altitud']==MAX_Altitud[0]]['LatitudMercator'].min(), size= 10, line_color= 'black', line_width= 2, fill_color= Spectral[4], visible= False)
        PLT_Mapa_Cima_TXT = Label(x= dfBokeh[dfBokeh['Altitud']==MAX_Altitud[0]]['LongitudMercator'].min(), y= dfBokeh[dfBokeh['Altitud']==MAX_Altitud[0]]['LatitudMercator'].min(), text= str(round(MAX_Altitud[0])), x_offset= 5, y_offset= 0, text_font_size= '10pt', text_color= 'black', text_align= 'left', text_baseline= 'middle', text_font_style= 'bold', visible= False)
        PLT_Mapa.add_layout(PLT_Mapa_Cima_TXT)
    else:
        PLT_Mapa_Cima = PLT_Mapa.triangle(0, 0, size= 0, line_alpha= 0, visible= False)
        PLT_Mapa_Cima_TXT = Label(x= 0, y= 0, text= '', text_font_size= '0pt', text_alpha= 0, visible= False)
        
    if (DesnivelPorKilometro > 40) and (MIN_Altitud[0] <= (AltitudInicio - 50) and MIN_Altitud[0] <= (AltitudFin - 50)):    
        PLT_Mapa_Valle = PLT_Mapa.inverted_triangle(dfBokeh[dfBokeh['Altitud']==MIN_Altitud[0]]['LongitudMercator'].min(), dfBokeh[dfBokeh['Altitud']==MIN_Altitud[0]]['LatitudMercator'].min(), size= 10, line_color= 'black', line_width= 2, fill_color= Spectral[0], visible= False)
        PLT_Mapa_Valle_TXT = Label(x= dfBokeh[dfBokeh['Altitud']==MIN_Altitud[0]]['LongitudMercator'].min(), y= dfBokeh[dfBokeh['Altitud']==MIN_Altitud[0]]['LatitudMercator'].min(), text= str(round(MIN_Altitud[0])), x_offset= 5, y_offset= 0, text_font_size= '10pt', text_color= 'black', text_align= 'left', text_baseline= 'middle', text_font_style= 'bold', visible= False)
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
    
    BotonesMapa = CheckboxButtonGroup(labels=["INICIO/FIN", "PUNTOS KILOMETRICOS", "CIMA/VALLE", 'PAUSAS'], active=[0, 1], width=300, height=30)
    CodigoJSMapa = CustomJS(code=CodigoJS, args=dict(l0=PLT_Mapa_Inicio, l1=PLT_Mapa_Fin, l2=PLT_Mapa_PuntoKm, l3= PLT_Mapa_PuntoKm_TXT, l4=PLT_Mapa_Cima, l5=PLT_Mapa_Cima_TXT, l6=PLT_Mapa_Valle, l7=PLT_Mapa_Valle_TXT, l8=PLT_Mapa_Pausas, checkbox= BotonesMapa))
    BotonesMapa.js_on_click(CodigoJSMapa)
    
    GridMapa = layout([PLT_Mapa, Column(BotonesMapa, width=300, height=35)], sizing_mode='stretch_width', width=900, height=470)

        
    return GridMapa