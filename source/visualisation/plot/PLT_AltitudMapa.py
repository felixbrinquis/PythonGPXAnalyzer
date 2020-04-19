# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 01:33:18 2020

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
from numpy import hstack
from datetime import timedelta
from math import ceil, floor, radians, pi, log, tan

from source.common.PaletasColores import paleta_rojo, paleta_verde, Spectral, Grapefruit, Mint

from source.common.Funciones_Generales import ConversorCoordenadasMercator, FormateoTiempos, FormulaKarvonen, Reescalado, LecturaBBDDActividades, EscrituraBBDDActividades, GeneracionCodigoJS, CreacionDirectoriosProyecto
from source.common.Funciones_DataFrame import CalculosVectoresAgregados, HitosKilometricos, HitosPausas, TablaParcialesKilometricos, TablaParcialesPausas, TablaZonasCardiacas, IdentificacionTipoActividad, LecturaBBDDActividades, AnalisisActividadActual, DeteccionVariables
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables

def AltitudMapa(DatosBokeh):
    """
        ALTITUD SEGUIMIENTO MAPA
    """
    
    # Factor de achatamiento de la altitud
    OffsetSuperiorAltitud, OffsetInferiorAltitud = CalculoOffsetAltitud(DatosBokeh)
    
    # Creacion de un grafica
    PLT_AltitudMapa = figure(width=900, height=110, x_range= (DatosBokeh.data['Distancia[m]'].min(), DatosBokeh.data['Distancia[m]'].max()), y_range= (LimiteEjeY(DatosBokeh, 'ALTITUD', 'Inferior'), LimiteEjeY(DatosBokeh, 'ALTITUD', 'Superior')), tools= '', toolbar_location= None)
    
    # Creacion del area bajo la linea de la metrica a partir del CDS
    Area = DatosBokeh.to_df().copy().reset_index()[['Distancia[m]', 'Altitud[m]']].set_index('Distancia[m]')
    Area.rename(columns= {'Altitud[m]': 'Area'}, inplace=True)
    AreaBottom = Area[::-1]
    AreaBottom['Area'] = 0
    PLT_AltitudMapa.patch(x= hstack((AreaBottom.index, Area.index)), y= hstack((AreaBottom['Area'], Area['Area'])), color= Mint[1], alpha=1, line_color=None)
    
    PLT_AltitudMapa.line('Distancia[m]', 'Altitud[m]', source= DatosBokeh, color= Mint[2], line_width= 2, line_cap= 'round')
       
    PLT_AltitudMapa.add_tools(HoverTool(tooltips=[('', '@{Distancia[m]}{0.0} m')], mode= 'vline'))
       
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
    
    return PLT_AltitudMapa