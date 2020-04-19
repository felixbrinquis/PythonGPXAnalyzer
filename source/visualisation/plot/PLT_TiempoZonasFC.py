# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 16:01:37 2020

@author: Felix
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


def TiempoZonasFC(df, FCMax, FCRep):

    dfTiempoZonasFC = TablaZonasCardiacas(FCMax, FCRep, df)
    dfTiempoZonasFC['TiempoTotal'] = dfTiempoZonasFC.DeltaTiempo.apply(lambda x: FormateoTiempos(x, 'T'))
    OrigenZonasCardiacas = ColumnDataSource(dfTiempoZonasFC[dfTiempoZonasFC['ZonaFC'].isin(['Z5', 'Z4', 'Z3', 'Z2', 'Z1'])].sort_values('ZonaFC', ascending=False))

    """
        ZONAS CARDIACAS
    """
    MapaColorZonaCardiaca = CategoricalColorMapper(factors= ['Z5', 'Z4', 'Z3', 'Z2', 'Z1'], palette= [Grapefruit[2], Bittersweet[2], Grass[2], BlueJeans[2], LightGray[2]])
    PLT_ZonasCardiacas = figure(plot_width= 400, plot_height= 350, x_range= (0, dfTiempoZonasFC['PorcentajeTiempo'].max()+dfTiempoZonasFC['PorcentajeTiempo'].max()*0.1), y_range= ['Z1', 'Z2', 'Z3', 'Z4', 'Z5'], tools= '', toolbar_location= None)
    PLT_ZonasCardiacas.hbar(y= 'ZonaFC', right= 'PorcentajeTiempo', height= 0.9, source= OrigenZonasCardiacas, line_color= 'black', fill_color= {'field':'ZonaFC', 'transform':MapaColorZonaCardiaca})
    
    PLT_ZonasCardiacas.text(x= 5, y= 'ZonaFC', text= 'TiempoTotal', source= OrigenZonasCardiacas)
    
    PLT_ZonasCardiacas.title.text = 'ZONAS CARDIACAS'
    PLT_ZonasCardiacas.sizing_mode = 'fixed'
    PLT_ZonasCardiacas.grid.visible = False
    PLT_ZonasCardiacas.xaxis.formatter = NumeralTickFormatter(format= '0%')
    
    return PLT_ZonasCardiacas