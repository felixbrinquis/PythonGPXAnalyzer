# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 13:44:52 2020

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
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables

from source.common.PaletasColores import paleta_rojo, paleta_verde, Spectral, Grapefruit, Mint


def TablaKmResumen(df):
    """
        DATOS EN FORMA DE TABLA POR PARCIALES KILOMETRICOS
    """
    dfTramosKm = TablaParcialesKilometricos(df)
    dfTramosKm['Ritmo_STR'] = dfTramosKm.Ritmo.apply(lambda x: FormateoTiempos(x, 'R'))
    OrigenTramosKm = ColumnDataSource(dfTramosKm)
    TablaKmResumen = [
            TableColumn(field= 'TramoKm', title= 'Km', width= 40, default_sort= 'ascending', sortable= False, formatter= StringFormatter(font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'Ritmo_STR', title= 'Ritmo[min/Km]', width= 80, default_sort= 'ascending', sortable= False, formatter= StringFormatter(font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'FrecuenciaCardiaca', title= 'FC[ppm]', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'Cadencia', title= 'Cadencia[ppm]', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'DesnivelAcumulado', title= 'Desnivel', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black'))
        ]
    PLT_TablaKmResumen = DataTable(source= OrigenTramosKm, columns= TablaKmResumen, width=360, height=550, fit_columns= False, sortable= False, reorderable= False, selectable= True, editable= False, index_position= None, header_row= True, row_height= 25)

    return PLT_TablaKmResumen