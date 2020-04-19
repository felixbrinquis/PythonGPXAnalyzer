# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 13:19:43 2020

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

def Resumen(NombreFichero, df):
    """
        RESUMEN DE LA ACTIVIDAD
    """
    # Seleccion del formato a mostrar
    DesnivelPositivo = df['DesnivelPositivoAcumulado'].max()
    DesnivelNegativo = df['DesnivelNegativoAcumulado'].max()
    DesnivelAcumulado = DesnivelPositivo + DesnivelNegativo
    DesnivelPorKilometro = (DesnivelAcumulado/df['Distancia'].max())*1000
    
    # Calculo de los valores agregados
    AVG_Altitud, MAX_Altitud, MIN_Altitud, \
    AVG_Velocidad, MAX_Velocidad, MIN_Velocidad, \
    AVG_Ritmo, MAX_Ritmo, MIN_Ritmo, \
    AVG_FrecuenciaCardiaca, MAX_FrecuenciaCardiaca, MIN_FrecuenciaCardiaca, \
    AVG_Cadencia, MAX_Cadencia, MIN_Cadencia, \
    AVG_Temperatura, MAX_Temperatura, MIN_Temperatura, \
    AVG_LongitudZancada, MAX_LongitudZancada, MIN_LongitudZancada, \
    AVG_Pendiente, MAX_Pendiente , MIN_Pendiente = CalculosVectoresAgregados(df)
    
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
    Resumen_Distancia.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= str(round(df['Distancia'].max()/1000, 2))+'km', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
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
    Resumen_Ritmo.add_layout(Label(x= AnchuraCelda/2, y= AlturaCelda/2, text= FormateoTiempos(timedelta(seconds=1000/np.divide(df['Distancia'].max(), df['TiempoActividad'].max().total_seconds())), 'R')+'/km', x_offset= 0, y_offset= 0, x_units= 'screen', y_units= 'screen', render_mode= 'canvas', level= 'annotation', text_color= 'black', text_align= 'center', text_baseline= 'top', text_alpha= 1, text_font_size= '15pt', text_font_style= 'bold', border_line_color= None, border_line_alpha= 0, background_fill_color= None, background_fill_alpha= 0))
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
        
    if DesnivelPorKilometro > 40: #Trail
        AlturaResumen = 195
        PLT_Resumen_Datos = layout(
                [[Resumen_Titulo],
                 [Resumen_Fecha],
                 [Resumen_Distancia, Resumen_Duracion, Resumen_TiempoTranscurrido],
                 [Resumen_DesnivelAcumulado, Resumen_FC, Resumen_Ritmo],
                 [Resumen_AltitudMax, Resumen_DesnivelPositivo, Resumen_PendienteMax],
                 [Resumen_AltitudMin, Resumen_DesnivelNegativo, Resumen_PendienteMin]],
                 sizing_mode='stretch_height', width=360, height=AlturaResumen)
    else: #Asfalto
        AlturaResumen = 130
        PLT_Resumen_Datos = layout(
                [[Resumen_Titulo],
                 [Resumen_Fecha],
                 [Resumen_Distancia, Resumen_Duracion, Resumen_Ritmo],
                 [Resumen_FC, Resumen_DesnivelPositivo, Resumen_Zancada]],
                 sizing_mode='stretch_height', width=360, height=AlturaResumen)
    
    GridResumen = layout([Column(PLT_Resumen_Datos, width=360, height=AlturaResumen)], sizing_mode='stretch_width', width=360, height=AlturaResumen)


    return GridResumen