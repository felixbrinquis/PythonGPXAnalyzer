# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este modulo contiene la funcion TabGraficosTiempoActividad la cual crea un tablon donde se visualizan
distintas metricas usando como eje horizontal el tiempo durante el cual se ha recogido informacion de manera activa.
"""

"""
    IMPORTACION DE LIBRERIAS
"""
# Importacion de las funciones necesarias
from bokeh.layouts import gridplot, layout, widgetbox, Spacer
from bokeh.models import ColumnDataSource, Span, HoverTool, LinearColorMapper, NumeralTickFormatter, DatetimeTickFormatter, CustomJS, Column
from bokeh.models.widgets import CheckboxGroup
from bokeh.models.tickers import SingleIntervalTicker
from bokeh.plotting import figure
from bokeh.transform import transform

import numpy as np
import pandas as pd

from source.common.PaletasColores import paleta_rojo, paleta_verde, paleta_azul, paleta_negro, paleta_cadencia, paleta_zancada

from source.common.Funciones_Generales import ConversorCoordenadasMercator, FormateoTiempos, FormulaKarvonen, Reescalado, LecturaBBDDActividades, EscrituraBBDDActividades, GeneracionCodigoJS, CreacionDirectoriosProyecto
from source.common.Funciones_DataFrame import CalculosVectoresAgregados, HitosKilometricos, HitosPausas, TablaParcialesKilometricos, TablaParcialesPausas, TablaZonasCardiacas, IdentificacionTipoActividad, LecturaBBDDActividades, AnalisisActividadActual, DeteccionVariables
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables



def TabGraficosTiempoActividad(DatosBokeh):

    """
        LAYOUT
    """
    from source.visualisation.plot.PLT_Altitud import Altitud
    from source.visualisation.plot.PLT_Cadencia import Cadencia
    from source.visualisation.plot.PLT_DesnivelPositivoAcumulado import DesnivelPositivoAcumulado
    from source.visualisation.plot.PLT_FrecuenciaCardiaca import FrecuenciaCardiaca
    from source.visualisation.plot.PLT_Pendiente import Pendiente
    from source.visualisation.plot.PLT_Ritmo import Ritmo
    from source.visualisation.plot.PLT_Temperatura import Temperatura
    from source.visualisation.plot.PLT_Zancada import Zancada

    MetricasAuxiliares = ['FRECUENCIA CARDIACA', 'RITMO', 'ALTITUD', 'CADENCIA', 'TEMPERATURA', 'PENDIENTE', 'DESNIVEL POSITIVO', 'LONGITUD ZANCADA']
    
    dict_MetricasAuxiliares = {
            'FRECUENCIA CARDIACA':'FrecuenciaCardiaca[ppm]',
            'RITMO':'Velocidad[m/s]',
            'ALTITUD':'Altitud[m]',
            'CADENCIA':'Cadencia[ppm]',
            'TEMPERATURA':'Temperatura[ºC]',
            'LONGITUD ZANCADA':'LongitudZancada[m]',
            'PENDIENTE':'Pendiente[%]',
            'DESNIVEL POSITIVO':'DesnivelPositivo[m]'}

    MetricasDisponibles = []
    for Metrica in MetricasAuxiliares:
        for key in dict_MetricasAuxiliares:
            if Metrica == key and dict_MetricasAuxiliares[key] in DatosBokeh.column_names:
                MetricasDisponibles.append(key)        
    
    ListadoGraficas = []
    
    MetricaPrincipal = 'FRECUENCIA CARDIACA'
    if dict_MetricasAuxiliares[MetricaPrincipal] in DatosBokeh.column_names:
        GridGraficaFC = FrecuenciaCardiaca(DatosBokeh, 'TiempoActividad', [Metricas for Metricas in MetricasDisponibles if Metricas != MetricaPrincipal])
        ListadoGraficas.append(GridGraficaFC)
        
    MetricaPrincipal = 'RITMO'
    if dict_MetricasAuxiliares[MetricaPrincipal] in DatosBokeh.column_names:
        GridGraficaVEL = Ritmo(DatosBokeh, 'TiempoActividad', [Metricas for Metricas in MetricasDisponibles if Metricas != MetricaPrincipal])
        ListadoGraficas.append(GridGraficaVEL)
        
    MetricaPrincipal = 'ALTITUD'
    if dict_MetricasAuxiliares[MetricaPrincipal] in DatosBokeh.column_names:
        GridGraficaALT = Altitud(DatosBokeh, 'TiempoActividad', [Metricas for Metricas in MetricasDisponibles if Metricas != MetricaPrincipal])
        ListadoGraficas.append(GridGraficaALT)
        
    MetricaPrincipal = 'CADENCIA'
    if dict_MetricasAuxiliares[MetricaPrincipal] in DatosBokeh.column_names:
        GridGraficaCAD = Cadencia(DatosBokeh, 'TiempoActividad', [Metricas for Metricas in MetricasDisponibles if Metricas != MetricaPrincipal])
        ListadoGraficas.append(GridGraficaCAD)
        
    MetricaPrincipal = 'TEMPERATURA'
    if dict_MetricasAuxiliares[MetricaPrincipal] in DatosBokeh.column_names:
        GridGraficaTMP = Temperatura(DatosBokeh, 'TiempoActividad', [Metricas for Metricas in MetricasDisponibles if Metricas != MetricaPrincipal])
        ListadoGraficas.append(GridGraficaTMP)
        
    MetricaPrincipal = 'PENDIENTE'
    if dict_MetricasAuxiliares[MetricaPrincipal] in DatosBokeh.column_names:
        GridGraficaPEN = Pendiente(DatosBokeh, 'TiempoActividad', [Metricas for Metricas in MetricasDisponibles if Metricas != MetricaPrincipal])
        ListadoGraficas.append(GridGraficaPEN)
        
    MetricaPrincipal = 'DESNIVEL POSITIVO'
    if dict_MetricasAuxiliares[MetricaPrincipal] in DatosBokeh.column_names:
        GridGraficaDPA = DesnivelPositivoAcumulado(DatosBokeh, 'TiempoActividad', [Metricas for Metricas in MetricasDisponibles if Metricas != MetricaPrincipal])
        ListadoGraficas.append(GridGraficaDPA)
        
    MetricaPrincipal = 'LONGITUD ZANCADA'
    if dict_MetricasAuxiliares[MetricaPrincipal] in DatosBokeh.column_names:
        GridGraficaZAN = Zancada(DatosBokeh, 'TiempoActividad', [Metricas for Metricas in MetricasDisponibles if Metricas != MetricaPrincipal])
        ListadoGraficas.append(GridGraficaZAN)

    GraficasTiempoActividad = layout(ListadoGraficas, sizing_mode='stretch_both')

    return GraficasTiempoActividad