# -*- coding: utf-8 -*-
"""
Created on Apr 11 2019

@author: Felix Brinquis

Description: este programa contiene la funcion CreacionHTML, la cual crea un informe en HTML con las pestañas seleccionadas.
La funcion recibe por parametros el directorio base, la carpeta en la que se crean los informes y el nombre del fchero.
La creacion de cada una de estas pestañas se realziza mediante funciones importadas al inicio del programa.
"""

import os
from bokeh.io import output_file, save
from bokeh.models.widgets import Panel, Tabs

from source.visualisation.Resumen import TabResumenMapa
from source.visualisation.ParcialesKilometricos import TabParcialesKilometricos
from source.visualisation.GraficosDistancia import TabGraficosDistancia
from source.visualisation.GraficosTiempoActividad import TabGraficosTiempoActividad
from source.visualisation.GraficosTiempoTotal import TabGraficosTiempoTotal
from source.visualisation.ParcialesPausas import TabParcialesPausas
from source.visualisation.ZonasCardiacas import TabZonasCardiacas


def CreacionHTML(DirectorioBase, Informes, NombreFichero, df):

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
    DiccionarioTabs['tab1'] = Panel(child = TabResumenMapa(NombreFichero, df), title = 'RESUMEN')
    DiccionarioTabs['tab2'] = Panel(child = TabGraficosDistancia(df), title = 'GRAFICAS DISTANCIA')
    DiccionarioTabs['tab3'] = Panel(child = TabGraficosTiempoActividad(df), title = 'GRAFICAS TIEMPO ACTIVIDAD')
    DiccionarioTabs['tab4'] = Panel(child = TabGraficosTiempoTotal(df), title = 'GRAFICAS TIEMPO TOTAL')
    DiccionarioTabs['tab5'] = Panel(child = TabParcialesKilometricos(df), title = 'PARCIALES KILOMETRCOS')
    DiccionarioTabs['tab6'] = Panel(child = TabParcialesPausas(df), title = 'ANALISIS POR PAUSAS')
    DiccionarioTabs['tab7'] = Panel(child = TabZonasCardiacas(df), title = 'ZONAS CARDIACAS')
     
    DiccionarioTabs['HTML'] = Tabs(tabs = [DiccionarioTabs['tab1'], DiccionarioTabs['tab2'], DiccionarioTabs['tab3'], DiccionarioTabs['tab4'], DiccionarioTabs['tab5'], DiccionarioTabs['tab6'], DiccionarioTabs['tab7']])     
    save(DiccionarioTabs['HTML'])