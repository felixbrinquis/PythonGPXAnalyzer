# -*- coding: utf-8 -*-
"""
Created on Apr 13 2019

@author: Felix Brinquis

Description: conjunto de funciones que podrian usarse recursivamente en varios programas.
"""


import pandas as pd
import numpy as np
from math import ceil, floor, radians, pi, log, tan
import datetime
import os



"""
    DEFINICION DE FUNCIONES
"""


# Generacion de coordenadas mercator
def ConversorCoordenadasMercator(lon, lat):
    """
    Funcion que convierte las coordenadas en radianes a mercator de modo que se pueda visualizar en el mapa
    """
    r_major = 6378137.000
    x = r_major * radians(lon)
    scale = x/lon
    y = 180.0/pi * log(tan(pi/4.0 + lat * (pi/180.0)/2.0)) * scale
    return (x, y)



# Formateo de tiempos como texto
def FormateoTiempos(Tiempo_TD, Formato= 'T'):
    """
      Funcion que recibe como parametros una variable en formato timedelta y la forma de mostrar los datos 
      y devuelve texto formateado.
      
      Z: 00:00:05 - 01:08:25
      T: 00:05 - 1:08:25
      R: 0:05 - 1:08:25
      MM: 00 - 68
      HMM: 0:00 - 1:08
          
    """
    DD, SS = Tiempo_TD.days, Tiempo_TD.seconds
    HH = DD * 24 + SS // 3600
    MM = (SS % 3600) // 60
    SS = SS % 60
    
    if Formato.upper() == 'T':
        if HH > 0:
            TiempoFormateado = str(HH)+':'+str(MM).zfill(2)+':'+str(SS).zfill(2)
        else:
            TiempoFormateado = str(MM).zfill(2)+':'+str(SS).zfill(2)
    elif Formato.upper() == 'R':
        if HH > 0:
            TiempoFormateado = str(HH)+':'+str(MM).zfill(2)+':'+str(SS).zfill(2)
        else:
            TiempoFormateado = str(MM)+':'+str(SS).zfill(2) 
    elif Formato.upper() == 'MM':
        TiempoFormateado = str(HH*60+MM).zfill(2)
    elif Formato.upper() == 'HMM':
        TiempoFormateado = str(HH)+':'+str(MM).zfill(2)
    else: # Por defecto format Z
        TiempoFormateado = str(HH).zfill(2)+':'+str(MM).zfill(2)+':'+str(SS).zfill(2) 
        
    return TiempoFormateado



def FormulaKarvonen(FCM, FCR, I):
    """
    Formula que devuelve unas pulsaciones en funcion de las pulsaciones maximas, minimas y el % de intensidad objetivo
    """
    FCO = ((FCM - FCR) * I) + FCR
    return FCO


# Reescalado de un valor para mostrar sobre otra medida
def Reescalado(Valor, RangoOrginal, RangoEscalado):
    Delta1 = RangoOrginal[1] - RangoOrginal[0]
    Delta2 = RangoEscalado[1] - RangoEscalado[0]
    return (Delta2 * (Valor - RangoOrginal[0]) / Delta1) + RangoEscalado[0]
        

       
def LecturaBBDDActividades(DirectorioBase, BBDD):
    """
        Funcion que lee el fichero de actividades ubicado en la ruta pasada por parametros
    """
    if os.path.exists(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv')):
            DataFrameBBDDActividades = pd.read_csv(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv'), sep= ';', encoding = 'utf-8')
    else:
            DataFrameBBDDActividades = pd.DataFrame(columns=['NombreFichero', 'NombreActividad', 'TipoActividad', 'Fecha', 'Hora', 'LatitudInicio', 'LongitudInicio', \
                                                            'Distancia', 'TiempoTotal', 'TiempoActividad', 'TramosPausas', \
                                                            'FrecuenciaCardiacaMedia', 'FrecuenciaCardiacaMaxima', 'FrecuenciaCardiacaMinima', \
                                                            'CadenciaMedia', 'CadenciaMaxima', 'CadenciaMinima', \
                                                            'TemperaturaMedia', 'TemperaturaMaxima', 'TemperaturaMinima', \
                                                            'AltitudMaxima', 'AltitudMinima', 'DesnivelPositivo', 'DesnivelNegativo', 'DesnivelPorKilometro', \
                                                            'VelocidadMedia', 'VelocidadMaxima', 'VelocidadPercentil90', 'VelocidadMinima', 'VelocidadPercentil10', 'VelocidadMediaAscenso', 'VelocidadMediaDescenso', 'RatioVelocidadDesnivel', \
                                                            'TipoActividadCalculado'])
    return DataFrameBBDDActividades

    
    
def EscrituraBBDDActividades(DirectorioBase, BBDD, DataFrameActividadActual, DataFrameBBDDActividades):
    """
        Funcion que recibe un directorio y 2 DataFrames, los concatena/actualiza y los graba en el directorio
    """
    # Insercion o borrado/insercion
    if DataFrameActividadActual['NombreFichero'][0]+'|'+DataFrameActividadActual['Fecha'][0]+'|'+DataFrameActividadActual['Hora'][0] not in list(DataFrameBBDDActividades['NombreFichero']+'|'+DataFrameBBDDActividades['Fecha']+'|'+DataFrameBBDDActividades['Hora']):
        DataFrameBBDDActividades =  pd.concat([DataFrameBBDDActividades, DataFrameActividadActual], sort=False)
    else:
        DataFrameBBDDActividades = DataFrameBBDDActividades[(DataFrameBBDDActividades['NombreFichero']!=DataFrameActividadActual['NombreFichero'][0]) | (DataFrameBBDDActividades['Fecha']!=DataFrameActividadActual['Fecha'][0]) | (DataFrameBBDDActividades['Hora']!=DataFrameActividadActual['Hora'][0])]
        DataFrameBBDDActividades =  pd.concat([DataFrameBBDDActividades, DataFrameActividadActual], sort=False)
    
    # Sobreescritura del fichero
    DataFrameBBDDActividades.to_csv(os.path.join(DirectorioBase, BBDD, 'BBDD_Actividades.csv'), sep= ';', index= False, header= True, encoding='utf-8')
    
    
def GeneracionCodigoJS(MetricasAuxiliares):
    """
        Esta funcion recibe por parametro el listado de n metricas auxiliares a visualizar y devuelve el
        codigo JavaScript necesario para interactuar con las n.
    """
    if len(MetricasAuxiliares) > 0:
        CodigoJS = 'var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };'
        for Metrica in MetricasAuxiliares:
            CodigoJS = CodigoJS + 'l' + str(MetricasAuxiliares.index(Metrica)) + '.visible = indexOf.call(checkbox.active,' + str(MetricasAuxiliares.index(Metrica)) + ')>=0;'
    else:
        CodigoJS = """ """

    return CodigoJS



def CreacionDirectoriosProyecto(Root):
    """
        Funcion que recibe el directorio raiz del proyecto y crea la estructura de carpetas 
        necesaria para funcionar si no existiera.
    """
    os.makedirs(os.path.join(Root, 'input'), exist_ok=True)
    os.makedirs(os.path.join(Root, 'input\processed'), exist_ok=True)
    os.makedirs(os.path.join(Root, 'library'), exist_ok=True)
    os.makedirs(os.path.join(Root, 'output'), exist_ok=True)
