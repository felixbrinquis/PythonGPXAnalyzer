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
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables

from source.common.PaletasColores import paleta_rojo, paleta_verde, Spectral, Grapefruit, Mint



def TabInicio(NombreFichero, df, DatosBokeh):
    
    from source.visualisation.plot.PLT_Mapa import Mapa
    GridMapa = Mapa(df, DatosBokeh)

    from source.visualisation.plot.PLT_AltitudMapa import AltitudMapa
    PLT_AltitudMapa = AltitudMapa(DatosBokeh)
    
    from source.visualisation.plot.PLT_Resumen import Resumen
    GridResumen = Resumen(NombreFichero, df)

    from source.visualisation.plot.PLT_TablaKmResumen import TablaKmResumen
    PLT_TablaKmResumen = TablaKmResumen(df)

    """
        LAYOUT
    """
    
    
    GridResumenInicio = layout([GridResumen, Column(PLT_TablaKmResumen, width=360, height=550)], sizing_mode='stretch_width', width=360, height=700)
    GridMapaAltitud= layout([GridMapa, PLT_AltitudMapa], sizing_mode='stretch_width', width=900, height=800)
    
    TabMapa = gridplot([GridMapaAltitud, GridResumenInicio], ncols= 2, sizing_mode='stretch_width', plot_width=1000, plot_height=800, toolbar_location='left')

    return TabMapa