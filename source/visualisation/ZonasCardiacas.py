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

from source.common.funciones import TablaZonasCardiacas, FormateoTiempos



def TabZonasCardiacas(df):
    
    FCMax = 185 #Frecuencia cardiaca maxima
    FCRep = 37 #Frecuencia cardiaca en reposo
    
    dfTiempoZonasFC = TablaZonasCardiacas(FCMax, FCRep, df)
    dfTiempoZonasFC['TiempoTotal'] = dfTiempoZonasFC.DeltaTiempo.apply(lambda x: FormateoTiempos(x, 'T'))
    OrigenZonasCardiacas = ColumnDataSource(dfTiempoZonasFC[dfTiempoZonasFC['ZonaFC'].isin(['Z5', 'Z4', 'Z3', 'Z2', 'Z1'])].sort_values('ZonaFC', ascending=False))

    """
        ZONAS CARDIACAS
    """
    MapaColorZonaCardiaca = CategoricalColorMapper(factors= ['Z5', 'Z4', 'Z3', 'Z2', 'Z1'], palette= ['tomato', 'darkorange', 'limegreen', 'dodgerblue', 'grey'])
    PLT_ZonasCardiacas = figure(plot_width= 400, plot_height= 350, x_range= (0, dfTiempoZonasFC['PorcentajeTiempo'].max()+dfTiempoZonasFC['PorcentajeTiempo'].max()*0.1), y_range= ['Z1', 'Z2', 'Z3', 'Z4', 'Z5'], tools= '', toolbar_location= None)
    PLT_ZonasCardiacas.hbar(y= 'ZonaFC', right= 'PorcentajeTiempo', height= 0.9, source= OrigenZonasCardiacas, line_color= 'black', fill_color= {'field':'ZonaFC', 'transform':MapaColorZonaCardiaca})
    
    PLT_ZonasCardiacas.text(x= 5, y= 'ZonaFC', text= 'TiempoTotal', source= OrigenZonasCardiacas)
    
    PLT_ZonasCardiacas.title.text = 'ZONAS CARDIACAS'
    PLT_ZonasCardiacas.sizing_mode = 'fixed'
    PLT_ZonasCardiacas.grid.visible = False
    PLT_ZonasCardiacas.xaxis.formatter = NumeralTickFormatter(format= '0%')
    
    """
        LAYOUT
    """
    GridZonasCardiacas = layout(
            [PLT_ZonasCardiacas],
            ncols= 1, merge_tools= True, sizing_mode='fixed', toolbar_options=dict(logo=None))
    
    return GridZonasCardiacas