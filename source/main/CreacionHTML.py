# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este programa contiene la funcion CreacionHTML, la cual crea un informe en HTML con las pestañas seleccionadas.
La funcion recibe por parametros el directorio base, la carpeta en la que se crean los informes y el nombre del fchero.
La creacion de cada una de estas pestañas se realziza mediante funciones importadas al inicio del programa.
"""

import os
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.io import output_file, save
from bokeh.models.widgets import Panel, Tabs

from source.visualisation.tab.TAB_Inicio import TabInicio
from source.visualisation.tab.TAB_ParcialesKilometricos import TabParcialesKilometricos
from source.visualisation.tab.TAB_GraficosDistancia import TabGraficosDistancia
from source.visualisation.tab.TAB_GraficosTiempoActividad import TabGraficosTiempoActividad
from source.visualisation.tab.TAB_GraficosTiempoTotal import TabGraficosTiempoTotal
from source.visualisation.tab.TAB_ParcialesPausas import TabParcialesPausas
from source.visualisation.tab.TAB_ZonasCardiacas import TabZonasCardiacas

from source.common.Funciones_Generales import ConversorCoordenadasMercator, FormateoTiempos, FormulaKarvonen, Reescalado, LecturaBBDDActividades, EscrituraBBDDActividades, GeneracionCodigoJS, CreacionDirectoriosProyecto
from source.common.Funciones_DataFrame import CalculosVectoresAgregados, HitosKilometricos, HitosPausas, TablaParcialesKilometricos, TablaParcialesPausas, TablaZonasCardiacas, IdentificacionTipoActividad, LecturaBBDDActividades, AnalisisActividadActual, DeteccionVariables
from source.common.Funciones_CulumnDataSource import FormateoEjes, CalculoOffsetAltitud, LimiteEjeY, ParametrosVariables

def CreacionHTML(DirectorioBase, Informes, NombreFichero, df):

    """
        PREPARACION DE DATOS
    """
    campos_rename = {
            'TiempoTotal':'TiempoTotal',
            'TiempoActividad':'TiempoActividad',
            'Distancia':'Distancia[m]',
            'Bloque':'Bloque', 
            'Latitud':'Latitud',
            'Longitud':'Longitud',
            'FrecuenciaCardiaca':'FrecuenciaCardiaca[ppm]',
            'Velocidad':'Velocidad[m/s]',
            'Ritmo':'Ritmo[m:s]',
            'Altitud':'Altitud[m]',
            'Cadencia':'Cadencia[ppm]',
            'TemperaturaAmbiente':'Temperatura[ºC]',
            'LongitudZancada':'LongitudZancada[m]',
            'Pendiente':'Pendiente[%]',
            'DesnivelPositivoAcumulado':'DesnivelPositivo[m]',
            'DesnivelNegativoAcumulado':'DesnivelNegativo[m]'}
    
    list_keep = []
    dict_rename = {}
    for Column in df.columns:
        for key in campos_rename:
            if Column == key:
                list_keep.append(key)
                dict_rename.update({key : campos_rename[key]})

    # Creacion del DataFrame de origen de Bokeh con renombrado de las columnas
    dfBokeh = df[list_keep].rename(columns=dict_rename).copy()

    # ReIndexado del dataframe para generar datos durante todo el tiempo que dure la actividad
    dfBokeh['Hora'] = df.index
    dfBokeh['DeltaTiempo'] = (dfBokeh['Hora']-dfBokeh['Hora'].shift()).fillna(pd.Timedelta(seconds=0))
    NuevoIndice = pd.date_range(start= dfBokeh.index.min(), end= dfBokeh.index.max(), freq= pd.DateOffset(seconds= dfBokeh['DeltaTiempo'].value_counts().idxmax().total_seconds()))
    dfBokeh = dfBokeh.reindex(NuevoIndice, fill_value= np.NaN) # Recalculo del tiempo total
    dfBokeh = dfBokeh.drop(['Hora', 'DeltaTiempo'], 1)
    dfBokeh['TiempoTotal'] = dfBokeh.index - dfBokeh.index.min()

    # Reasignacion de valores missing
    for Column in dfBokeh.columns:
        if Column in ['TiempoActividad', 'Distancia[m]', 'Bloque', 'Latitud', 'Longitud', 'Altitud[m]', 'Temperatura[ºC]', 'DesnivelPositivo[m]', 'DesnivelNegativo[m]']:
            dfBokeh.update(dfBokeh[Column].fillna(method='ffill')) # Variables que mantienen el ultimo valor registrado
        elif Column in ['Velocidad[m/s]', 'Pendiente[%]']:
                dfBokeh.update(dfBokeh[Column].fillna(0)) # Variables que interesa tenerlas a 0 incluso aunque no se llegue a representar
        elif Column in ['Ritmo[m:s]']:
            dfBokeh.update(dfBokeh[Column].fillna(dfBokeh['Ritmo[m:s]'].max())) # En el caso del ritmo cuanto mejor, peor xD
            # Inclusion del ritmo instantaneo en formato texto
            dfBokeh['Ritmo[STR]'] = dfBokeh['Ritmo[m:s]'].dt.round('1s').dt.components['minutes'].astype(str).apply(lambda x: x.zfill(2))+':'+dfBokeh['Ritmo[m:s]'].dt.round('1s').dt.components['seconds'].astype(str).apply(lambda x: x.zfill(2))
        elif Column in ['FrecuenciaCardiaca[ppm]']:
            dfBokeh.update(dfBokeh[Column].fillna(min(dfBokeh['FrecuenciaCardiaca[ppm]'].min(), 85))) # Como desconocemos el valor instanteneo, le asignamos un minimo por defecto


    # Creacion de coordenadas Mercator en el DataFrame
    if 'Longitud' in dfBokeh.columns and 'Latitud' in dfBokeh.columns:
        for index, row in dfBokeh.iterrows():
            LongitudMercator, LatitudMercator = ConversorCoordenadasMercator(row.Longitud, row.Latitud)
            dfBokeh.at[index,'LongitudMercator'] = LongitudMercator
            dfBokeh.at[index,'LatitudMercator'] = LatitudMercator
    
    """
        Dropeo aqui de las cooredenadas que no sean mercator
    """    
    """
        Incluir aqui una funcion que determine la freecuencia de muestreo adecuada
    """
    campos_resample = {
                # Indice
                'TiempoTotal': np.max,
                # Frecuencia 1
                'TiempoActividad': np.max,
                'Distancia[m]':np.max,
                'LongitudMercator': np.mean,
                'LatitudMercator': np.mean,
                'Altitud[m]': np.max,
                'Velocidad[m/s]': np.mean,
                'FrecuenciaCardiaca[ppm]': np.mean,
                'Temperatura[ºC]': np.min,
                'Pendiente[%]': np.mean,
                'DesnivelPositivo[m]': np.max,
                'DesnivelNegativo[m]': np.max,
                # Frecuencia 2
                'Cadencia[ppm]': np.mean, 
                'LongitudZancada[m]': np.mean}
                
    dict_frec_1 = {}
    dict_frec_2 = {}
    for Column in dfBokeh.columns:
        for key in campos_resample:
            if Column == key:
                if Column in ['TiempoTotal', 'TiempoActividad', 'Distancia[m]', 'LongitudMercator', 'LatitudMercator', 'Altitud[m]', 'Velocidad[m/s]', 'FrecuenciaCardiaca[ppm]', 'Temperatura[ºC]', 'Pendiente[%]', 'DesnivelPositivo[m]', 'DesnivelNegativo[m]']:
                    dict_frec_1.update({key : campos_resample[key]})
                if Column in ['TiempoTotal', 'Cadencia[ppm]', 'LongitudZancada[m]']:
                    dict_frec_2.update({key : campos_resample[key]})
                
    
    # Reduccion de la frecuencia de muestreo para visualiza mejor graficas con muchos datos
    dfBokehResample = dfBokeh.groupby('Bloque').resample('5S').agg(dict_frec_1)

    # Reducion de la frecuencia de muestreo de los datos que se visualizaran de manera discreta
    dfBokehDiscretos = dfBokeh.groupby('Bloque').resample('10S').agg(dict_frec_2)
    if 'Cadencia[ppm]' in dfBokehDiscretos.columns:
        dfBokehDiscretos['Cadencia[ppm]'] = dfBokehDiscretos['Cadencia[ppm]'].round()

    # Se incluyen en el mismo DataFrame variables con diferente frecuencia de muestreo
    DataFrameBokeh = pd.merge(dfBokehResample, dfBokehDiscretos, how='left', on='TiempoTotal')
    if 'Ritmo[STR]' in dfBokeh.columns:
        dfBokehSTR = dfBokeh[['TiempoTotal', 'Ritmo[STR]']]
        DataFrameBokeh = pd.merge(DataFrameBokeh, dfBokehSTR, how='left', on='TiempoTotal')
    
    # Creacion del ColumnDataSource de origen de Bokeh
    DatosBokeh = ColumnDataSource(DataFrameBokeh) 

    from source.common.PaletasColores import Grapefruit, Bittersweet, Sunflower, Grass, Mint, Aqua, BlueJeans, Lavender, PinkRose, SkinTone, LightGray, DarkGray, PaletaGrises
      
    # Creacion de metricas auxiliares reescaladas a la metrica principal
    DiccionarioVariables = ParametrosVariables(DatosBokeh)
     
    """
        Se recorre el diccionario de variables filtrando aquellas que esten activas, estan seran
        las metricas principales.
        Una vez seleccionada una metrica principal se vuelve a iterar sobre el diccionario de variables
        para seleccionar aquellas activas que no coincidan con la principal, estas seran las metricas auxiliares.
        Por cada una de estas combinaciones se crea un campo nuevo sobre el ColumnDataSource de la metrica 
        principal cuyo nombre sera la variable auxiliar sin las unidades y añadiendo el sufijo correspondiente
        a la metrica principal. Los valores de estos campos seran un reescalado de la metrica auxiliar
        para la visualizacion junto con la metrica principal sin importar las unidades de la primeras.
    """           
    for MetricaPrincipal in DiccionarioVariables:
        if DiccionarioVariables[MetricaPrincipal]['Activo'] == 1 and DiccionarioVariables[MetricaPrincipal]['Variable'] in DatosBokeh.column_names:
            for MetricaAuxiliar in DiccionarioVariables:
                if MetricaAuxiliar != MetricaPrincipal and DiccionarioVariables[MetricaAuxiliar]['Activo'] == 1 and DiccionarioVariables[MetricaAuxiliar]['Variable'] in DatosBokeh.column_names:
                    if MetricaAuxiliar == 'ALTITUD':
                        OffsetSuperiorAltitud, OffsetInferiorAltitud = CalculoOffsetAltitud(DiccionarioVariables[MetricaPrincipal]['CDS'])
                        MinVariable = np.nanmin(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']]) - (np.nanmax(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']])-np.nanmin(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']]))*(0.5*OffsetInferiorAltitud)
                        MaxVariable = np.nanmax(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']]) + (np.nanmax(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']])-np.nanmin(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']]))*(0.5*OffsetSuperiorAltitud)
                    else:
                        MinVariable = np.nanmin(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']])
                        MaxVariable = np.nanmax(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']])        
                    DiccionarioVariables[MetricaPrincipal]['CDS'].add(Reescalado(DiccionarioVariables[MetricaPrincipal]['CDS'].data[DiccionarioVariables[MetricaAuxiliar]['Variable']], [MinVariable, MaxVariable], [DiccionarioVariables[MetricaPrincipal]['LimiteInferiorY'],DiccionarioVariables[MetricaPrincipal]['LimiteSuperiorY']]), name=DiccionarioVariables[MetricaAuxiliar]['Variable'].split('[',1)[0] + DiccionarioVariables[MetricaPrincipal]['Sufijo'])

    """
        Datos de usuario
    """
    FCMax = 185 #Frecuencia cardiaca maxima
    FCRep = 37 #Frecuencia cardiaca en reposo

    output_file(os.path.join(DirectorioBase, Informes, NombreFichero+'.html'))

    DiccionarioTabs = {
            'HTML':NombreFichero,
            'tab1':NombreFichero+'_tab1',
            'tab2':NombreFichero+'_tab2',
            'tab3':NombreFichero+'_tab3',
            'tab4':NombreFichero+'_tab4',
            'tab5':NombreFichero+'_tab5',
            'tab6':NombreFichero+'_tab6',
            'tab7':NombreFichero+'_tab7'
            }
    
    # Visualizacion de la actividad
    TabsDisponibles = []
    
    # Coordenadas y altitud
    if 'LatitudMercator' in DatosBokeh.column_names and 'LongitudMercator' in DatosBokeh.column_names:
        DiccionarioTabs['tab1'] = Panel(child = TabInicio(NombreFichero, df, DatosBokeh), title = 'RESUMEN')
        TabsDisponibles.append(DiccionarioTabs['tab1'])
    # Distancia y alguna metrica
    if 'Distancia[m]' in DatosBokeh.column_names:
        DiccionarioTabs['tab2'] = Panel(child = TabGraficosDistancia(DatosBokeh), title = 'GRAFICAS DISTANCIA')
        TabsDisponibles.append(DiccionarioTabs['tab2'])
    # Alguna metrica
    DiccionarioTabs['tab3'] = Panel(child = TabGraficosTiempoActividad(DatosBokeh), title = 'GRAFICAS TIEMPO ACTIVIDAD')
    TabsDisponibles.append(DiccionarioTabs['tab3'])
    DiccionarioTabs['tab4'] = Panel(child = TabGraficosTiempoTotal(DatosBokeh), title = 'GRAFICAS TIEMPO TOTAL')
    TabsDisponibles.append(DiccionarioTabs['tab4'])
    # Distancia, altitud, FC y Cadencia
    if 'Distancia[m]' in DatosBokeh.column_names and 'Altitud[m]' in DatosBokeh.column_names and 'FrecuenciaCardiaca[ppm]' in DatosBokeh.column_names and 'Cadencia[ppm]' in DatosBokeh.column_names:
        DiccionarioTabs['tab5'] = Panel(child = TabParcialesKilometricos(df), title = 'PARCIALES KILOMETRICOS')
        TabsDisponibles.append(DiccionarioTabs['tab5'])
        DiccionarioTabs['tab6'] = Panel(child = TabParcialesPausas(df), title = 'ANALISIS POR PAUSAS')
        TabsDisponibles.append(DiccionarioTabs['tab6'])
    # FC
    if 'FrecuenciaCardiaca[ppm]' in DatosBokeh.column_names:
        DiccionarioTabs['tab7'] = Panel(child = TabZonasCardiacas(df, FCMax, FCRep), title = 'ZONAS CARDIACAS')
        TabsDisponibles.append(DiccionarioTabs['tab7'])
     
    DiccionarioTabs['HTML'] = Tabs(tabs = TabsDisponibles)     
    save(DiccionarioTabs['HTML'])