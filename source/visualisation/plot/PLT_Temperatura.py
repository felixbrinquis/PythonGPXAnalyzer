# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 12:41:45 2020

@author: Felix
"""

"""
    IMPORTACION DE LIBRERIAS
"""
# Importacion de librerias externas
from numpy import hstack
from bokeh.layouts import gridplot, layout, Spacer
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter, DatetimeTickFormatter, CustomJS, Column
from bokeh.models.widgets import CheckboxGroup
from bokeh.models.tickers import SingleIntervalTicker, DatetimeTicker
from bokeh.plotting import figure

# Importacion de librerias propias
from source.common.Funciones_Generales import ConversorCoordenadasMercator, FormateoTiempos, FormulaKarvonen, Reescalado, LecturaBBDDActividades, EscrituraBBDDActividades, GeneracionCodigoJS, CreacionDirectoriosProyecto
from source.common.Funciones_DataFrame import CalculosVectoresAgregados, HitosKilometricos, HitosPausas, TablaParcialesKilometricos, TablaParcialesPausas, TablaZonasCardiacas, IdentificacionTipoActividad, LecturaBBDDActividades, AnalisisActividadActual, DeteccionVariables
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables, FunctionSizeCircle

from source.common.PaletasColores import Sunflower

def Temperatura(DatosBokeh, EjeX, MetricasAuxiliares):
    """
        GRAFICO AREA | TEMPERATURA AMBIENTE
    """
    
    # Creacion del diccionario de metricas auxiliares
    DiccionarioVariables = ParametrosVariables(DatosBokeh)

    # Generacion del codigo JavaScript que habilita la visualizacion de metricas auxiliares
    CodigoJS = GeneracionCodigoJS(MetricasAuxiliares)
  
    # Asignacion de tamaño del punto en graficas discretas
    SizeCircle = FunctionSizeCircle(DatosBokeh)
    
    # Creacion de un grafica
    PLT = figure(width=1000, height=400, x_range=(DatosBokeh.data[EjeX].min(), DatosBokeh.data[EjeX].max()), y_range=(LimiteEjeY(DatosBokeh, 'TEMPERATURA', 'Inferior'), LimiteEjeY(DatosBokeh, 'TEMPERATURA', 'Superior')), tools='', toolbar_location=None)
    
	# Creacion del area bajo la linea de la metrica a partir del CDS
    Area = DatosBokeh.to_df().copy().reset_index()[[EjeX, 'Temperatura[ºC]']].set_index(EjeX)
    Area.rename(columns= {'Temperatura[ºC]': 'Area'}, inplace=True)
    AreaBottom = Area[::-1]
    AreaBottom['Area'] = 0
    PLT.patch(x= hstack((AreaBottom.index, Area.index)), y= hstack((AreaBottom['Area'], Area['Area'])), color= Sunflower[0], alpha=1, line_color=None)
	
    # Inclusion de datos
    PLT.line(EjeX, 'Temperatura[ºC]', source=DatosBokeh, color=Sunflower[1], line_width=2, line_cap='round')
    PLT_Linea = PLT.line(EjeX, 'Temperatura[ºC]', source=DatosBokeh, color='white', line_width=0, line_alpha=0)
    PLT.add_tools(HoverTool(tooltips=[('', '@{Temperatura[ºC]}{int} ºC')], renderers= [PLT_Linea], mode= 'vline'))

    # Inclusion de lineas auxiliares
    ListadoMetricasAuxiliares = {}
    for Metrica in MetricasAuxiliares:
        if DiccionarioVariables[Metrica]['Tipo'] == 'circle':
            ListadoMetricasAuxiliares['l' + str(MetricasAuxiliares.index(Metrica))] = PLT.circle(EjeX, DiccionarioVariables[Metrica]['Variable'].split('[',1)[0] + DiccionarioVariables['TEMPERATURA']['Sufijo'], source=DiccionarioVariables[Metrica]['CDS'], size=SizeCircle, line_color=DiccionarioVariables[Metrica]['Color'], color=DiccionarioVariables[Metrica]['Color'], **DiccionarioVariables[Metrica]['Propiedades'])
        elif DiccionarioVariables[Metrica]['Tipo'] == 'step':
            ListadoMetricasAuxiliares['l' + str(MetricasAuxiliares.index(Metrica))] = PLT.step(EjeX, DiccionarioVariables[Metrica]['Variable'].split('[',1)[0] + DiccionarioVariables['TEMPERATURA']['Sufijo'], source=DiccionarioVariables[Metrica]['CDS'], color=DiccionarioVariables[Metrica]['Color'], **DiccionarioVariables[Metrica]['Propiedades'])
        else:
            ListadoMetricasAuxiliares['l' + str(MetricasAuxiliares.index(Metrica))] = PLT.line(EjeX, DiccionarioVariables[Metrica]['Variable'].split('[',1)[0] + DiccionarioVariables['TEMPERATURA']['Sufijo'], source=DiccionarioVariables[Metrica]['CDS'], color=DiccionarioVariables[Metrica]['Color'], **DiccionarioVariables[Metrica]['Propiedades'])
     
    # Atributos
    PLT.title.text = 'TEMPERATURA AMBIENTE'
    PLT.sizing_mode = 'fixed'
    PLT.yaxis.axis_label = 'Temperatura [ºC]'
    PLT.yaxis.formatter = NumeralTickFormatter(format= '0,0')
    PLT.grid.visible = False
    PLT.yaxis.minor_tick_line_color = None
    PLT.yaxis.major_label_overrides = FormateoEjes(DatosBokeh.data['Temperatura[ºC]'], 5, 1)

    # Asignacion de opciones de visualizacion del eje X
    if EjeX == 'Distancia[m]':
        PLT.xaxis.axis_label = 'Distancia'
        PLT.xaxis.formatter = NumeralTickFormatter(format='0')
        if DatosBokeh.data['Distancia[m]'].max() >= 4000:
            PLT.xaxis.ticker = SingleIntervalTicker(interval=1000)
            PLT.xaxis.major_label_overrides = FormateoEjes(DatosBokeh.data['Distancia[m]'], 1000, 1000, 0, 0)
    elif EjeX == 'TiempoActividad':
        PLT.xaxis.axis_label = 'Tiempo actividad'
        PLT.xaxis.formatter = DatetimeTickFormatter(hourmin='%H:%M:%S', minutes='%M:%S', seconds='%Ss' )
        PLT.xaxis.ticker = DatetimeTicker()
    elif EjeX == 'TiempoTotal':
        PLT.xaxis.axis_label = 'Tiempo total'
        PLT.xaxis.formatter = DatetimeTickFormatter(hourmin='%H:%M:%S', minutes='%M:%S', seconds='%Ss' )
        PLT.xaxis.ticker = DatetimeTicker()
		
    #Botones
    Botones = CheckboxGroup(labels=MetricasAuxiliares, active=[], width=100, height=380)
    ListadoMetricasAuxiliares['checkbox'] = Botones
    CodigoJSFrecuenciaCardiaca = CustomJS(code=CodigoJS, args=ListadoMetricasAuxiliares)
    Botones.js_on_click(CodigoJSFrecuenciaCardiaca)
    
    #Layout
    GridBotones = layout([Spacer(width=100, height=25), Column(Botones, width=100, height=375)], sizing_mode='fixed', width=100, height=400)
    GridGrafica = gridplot([PLT, GridBotones], ncols= 2, sizing_mode='stretch_width', toolbar_location=None, plot_width=1100, plot_height=400)

    return GridGrafica