# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este modulo contiene la funcion TabParcialesKilometricos la cual crea un tablon donde se visualiza
mediante un diagrama de barras verticales el ritmo medio por cada bloque de ejercicio delimitado por las pausas
en la actividad. Tambien pueden superponerse otras metricas de manera opcional.
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
from source.common.PaletasColores import paleta_rojo, paleta_verde, paleta_cadencia, BlueJeans

from source.common.Funciones_Generales import ConversorCoordenadasMercator, FormateoTiempos, FormulaKarvonen, Reescalado, LecturaBBDDActividades, EscrituraBBDDActividades, GeneracionCodigoJS, CreacionDirectoriosProyecto
from source.common.Funciones_DataFrame import CalculosVectoresAgregados, HitosKilometricos, HitosPausas, TablaParcialesKilometricos, TablaParcialesPausas, TablaZonasCardiacas, IdentificacionTipoActividad, LecturaBBDDActividades, AnalisisActividadActual, DeteccionVariables
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables



def TabParcialesPausas(df):
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
    DesnivelPorKilometro = (DesnivelAcumulado/df['Distancia'].max())*1000
    
    # Factor de achatamiento de la altitud
    if DesnivelPorKilometro > 40:
        OffsetSuperiorAltitud = 0.1
        OffsetInferiorAltitud = 0.03
    else:
        OffsetSuperiorAltitud = 2.5
        OffsetInferiorAltitud = 0.5
        
    dfTramosPausas = TablaParcialesPausas(df)
    dfTramosPausas['Ritmo_STR'] = dfTramosPausas.Ritmo.apply(lambda x: FormateoTiempos(x, 'R'))

    # Seleccion de un subconjunto de datos para visualizar
    dfBokehParcialesPausas = df[['Bloque', 'Distancia', 'Altitud', 'FrecuenciaCardiaca', 'Cadencia']].copy()
    dfBokehParcialesPausas['AltitudEscalada'] = Reescalado(dfBokehParcialesPausas['Altitud'], [MIN_Altitud[0]-(MAX_Altitud[0]-MIN_Altitud[0])*OffsetInferiorAltitud, MAX_Altitud[0]+(MAX_Altitud[0]-MIN_Altitud[0])*OffsetSuperiorAltitud], [0, dfTramosPausas.Velocidad.max()])
    dfBokehParcialesPausas['FrecuenciaCardiacaEscalada'] = Reescalado(dfBokehParcialesPausas['FrecuenciaCardiaca'], [MIN_FrecuenciaCardiaca[0], MAX_FrecuenciaCardiaca[0]], [0, dfTramosPausas.Velocidad.max()])
    dfBokehParcialesPausas['CadenciaEscalada'] = Reescalado(dfBokehParcialesPausas['Cadencia'], [MIN_Cadencia[0], MAX_Cadencia[0]], [0, dfTramosPausas.Velocidad.max()])
    OrigenTramosPausa = ColumnDataSource(dfBokehParcialesPausas)
    
    #  Reducion de la frecuencia de muestreo
    dfBokehParcialesPausas_Agg = dfBokehParcialesPausas.groupby('Bloque').resample('10S').agg({'Distancia': np.max, 'Cadencia': np.mean})
    dfBokehParcialesPausas_Agg['Cadencia'] = dfBokehParcialesPausas_Agg['Cadencia'].round()
    dfBokehParcialesPausas_Agg['CadenciaEscalada'] = Reescalado(dfBokehParcialesPausas_Agg['Cadencia'], [MIN_Cadencia[0], MAX_Cadencia[0]], [0, dfTramosPausas.Velocidad.max()])
    
    # Creacion de los ColumnDataSource de origen de Bokeh
    OrigenParcialesPausa = ColumnDataSource(dfBokehParcialesPausas) 
    OrigenParcialesPausa_Agg = ColumnDataSource(dfBokehParcialesPausas_Agg)
    OrigenTramosPausa = ColumnDataSource(dfTramosPausas)
    
    # Asignacion de tamaño segun el total de puntos
    if df['Distancia'].max() < 5:
        SizeCircle = 10
    elif df['Distancia'].max() <10:
        SizeCircle = 8
    else:
        SizeCircle = 5
    
    # Definicion de la paleta de colores por cadencia
    MapaColorCadencia = LinearColorMapper(palette= paleta_cadencia, low= 110, high= 190)   
    
    
    """
        TRAMOS POR PAUSAS
    """
    
    PLT_TramosPausas = figure(plot_width= 900, plot_height= 500, x_range= (0, df['Distancia'].max()), y_range= (0, dfTramosPausas.Velocidad.max()+dfTramosPausas.Velocidad.max()*0.1), tools= '', toolbar_location= None)
    PLT_TramosPausas.add_layout(Span(location= AVG_Velocidad[0], dimension= 'width', line_color= BlueJeans[2], line_dash= 'dashed', line_width= 1, line_alpha= 0.7))
    PLT_TramosPausas.rect(x= 'x', y= 'y', width= 'Distancia', height= 'Velocidad', source= OrigenTramosPausa, line_width= 1, line_color= BlueJeans[2], fill_color= BlueJeans[1])
    PLT_TramosPausas.add_tools(HoverTool(tooltips=[('', '@Ritmo_STR')], mode= 'mouse'))
    
    PropiedadesLineas = dict(line_width= 2, line_alpha=0.7, line_cap= 'round', visible= False)
    PLT_TramosPausas_Altitud = PLT_TramosPausas.line('Distancia', 'AltitudEscalada', source= OrigenParcialesPausa, color= paleta_verde[6], **PropiedadesLineas)
    PLT_TramosPausas_FC = PLT_TramosPausas.line('Distancia', 'FrecuenciaCardiacaEscalada', source= OrigenParcialesPausa, color= paleta_rojo[6], **PropiedadesLineas)
    PLT_TramosPausas_Cadencia = PLT_TramosPausas.circle('Distancia', 'CadenciaEscalada', source= OrigenParcialesPausa_Agg, size= SizeCircle, line_color= transform('Cadencia', MapaColorCadencia), color= transform('Cadencia', MapaColorCadencia), fill_alpha= 1, visible= False)

    # Atributos
    PLT_TramosPausas.title.text = 'RITMO MEDIO POR BLOQUES'
    PLT_TramosPausas.xaxis.axis_label = 'Distancia'
    PLT_TramosPausas.xaxis.formatter = NumeralTickFormatter(format= '0 a')
    PLT_TramosPausas.yaxis.axis_label = 'Ritmo [min/km]'
    PLT_TramosPausas.grid.visible = False
    PLT_TramosPausas.yaxis.major_label_overrides = {1: '16:40', 1.5: '16:06', 2: '8:20', 2.5: '6:40', 3: '5:33', 3.5: '4:45', 4: '4:10', 4.5: '3:42', 5: '3:20', 5.5: '3:01', 6: '2:46', 6.5: '2:34', 7: '2:22'}
    PLT_TramosPausas.xaxis.ticker = SingleIntervalTicker(interval= 1000)
    PLT_TramosPausas.xaxis.major_label_overrides = FormateoEjes(OrigenParcialesPausa.data['Distancia'], 1000, 1000, 0, 0)

    """
        DATOS EN FORMA DE TABLA POR PAUSAS
    """
    TablaPausas = [
            TableColumn(field= 'TramoKm', title= 'Km', width= 40, default_sort= 'ascending', sortable= False, formatter= StringFormatter(font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'Ritmo_STR', title= 'Ritmo[min/Km]', width= 80, default_sort= 'ascending', sortable= False, formatter= StringFormatter(font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'FrecuenciaCardiaca', title= 'FC[ppm]', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'Cadencia', title= 'Cadencia[ppm]', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black')),
            TableColumn(field= 'DesnivelAcumulado', title= 'Desnivel', width= 80, default_sort= 'ascending', sortable= False, formatter= NumberFormatter(format= '0,0', language= 'es', rounding= 'round', font_style= 'normal', text_align= 'center', text_color= 'black'))
        ]
    PLT_TablaPausas = DataTable(source= OrigenTramosPausa, columns= TablaPausas, width= 360, height= 550, fit_columns= False, sortable= False, reorderable= False, selectable= True, editable= False, index_position= None, header_row= True, row_height= 25)

    """
        BOTONES
    """
    
    CodigoJS = """
    var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };
    
    l0.visible = indexOf.call(checkbox.active,0)>=0;
    l1.visible = indexOf.call(checkbox.active,1)>=0;
    l2.visible = indexOf.call(checkbox.active,2)>=0;
    """
    
    BotonesTramosPausas = CheckboxButtonGroup(labels=["Altitud", "Frecuencia Cardiaca", "Cadencia"], active=[], width=300, height=30)
    CodigoJSTramosPausas = CustomJS(code=CodigoJS, args=dict(l0=PLT_TramosPausas_Altitud, l1=PLT_TramosPausas_FC, l2=PLT_TramosPausas_Cadencia, checkbox=BotonesTramosPausas))
    BotonesTramosPausas.js_on_click(CodigoJSTramosPausas)
 

    """
        LAYOUT
    """
    GridGraficaTramosPausas = layout([Column(PLT_TramosPausas, width=900, height=500), [Spacer(width=300, height=30), Column(BotonesTramosPausas, width=300, height=30), Spacer(width=300, height=30)]], sizing_mode='stretch_width', width=900, height=570)
    GridTablaTramosPausas = layout([Spacer(width=360, height= 25), Column(PLT_TablaPausas, width=360, height=550)], sizing_mode='stretch_width', width=360, height=570)   
    GridAnalisisPausas = gridplot([GridGraficaTramosPausas, GridTablaTramosPausas], ncols= 2, sizing_mode='stretch_width', toolbar_location=None, plot_width=1000, plot_height=570)

    return GridAnalisisPausas