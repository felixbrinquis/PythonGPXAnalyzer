# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este modulo contiene la funcion TabZonasCardiacas la cual crea un tablon donde se visualiza
el porcentaje de tiempo sobre el total en cada una de las 5 zonas cardiacas según la FCMax y FCRep del usuario.
"""

"""
    IMPORTACION DE LIBRERIAS
"""
from bokeh.layouts import layout
from bokeh.models import CategoricalColorMapper, ColumnDataSource, NumeralTickFormatter
from bokeh.plotting import figure

from source.common.Funciones_Generales import ConversorCoordenadasMercator, FormateoTiempos, FormulaKarvonen, Reescalado, LecturaBBDDActividades, EscrituraBBDDActividades, GeneracionCodigoJS, CreacionDirectoriosProyecto
from source.common.Funciones_DataFrame import CalculosVectoresAgregados, HitosKilometricos, HitosPausas, TablaParcialesKilometricos, TablaParcialesPausas, TablaZonasCardiacas, IdentificacionTipoActividad, LecturaBBDDActividades, AnalisisActividadActual, DeteccionVariables
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables

from source.common.PaletasColores import Grapefruit, Bittersweet, Sunflower, Grass, Mint, Aqua, BlueJeans, Lavender, PinkRose, SkinTone, LightGray, DarkGray 

def TabZonasCardiacas(df, FCMax, FCRep):
    
    from source.visualisation.plot.PLT_TiempoZonasFC import TiempoZonasFC
    PLT_ZonasCardiacas = TiempoZonasFC(df, FCMax, FCRep)
    
    """
        LAYOUT
    """
    GridZonasCardiacas = layout([PLT_ZonasCardiacas], sizing_mode='stretch_width')
    
    return GridZonasCardiacas