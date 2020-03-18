# -*- coding: utf-8 -*-
"""
Created on Mar 9 2019

@author: Felix Brinquis

Description: este programa recibe como parametro un fichero en formato GPX Garmin, lee el contenido
del mismo y lo convierte en un dataframe.
"""

# Importacion de librerias
from lxml import etree
import dateutil.parser
import timezonefinder, pytz
import pandas as pd

def LecturaGPX(ficheroGPX):
    gpx = etree.parse(ficheroGPX)
    
    Name = gpx.xpath("//gpx:name", namespaces = {'gpx': "http://www.topografix.com/GPX/1/1"})[0].text
    Type = gpx.xpath("//gpx:type", namespaces = {'gpx': "http://www.topografix.com/GPX/1/1"})[0].text
    
    # Definicion de listas
    Latitud = []
    Longitud = []
    Altitud = []
    HoraISO = []
    TemperaturaAmbiente = []
    FrecuenciaCardiaca = []
    CadenciaBraceo = []
    
    # Extraccion de valores en forma de listas
    for point in gpx.xpath("//gpx:trkpt", namespaces = {'gpx': "http://www.topografix.com/GPX/1/1"}):
        Latitud.append(float(point.attrib['lat']))
        Longitud.append(float(point.attrib['lon']))
    
    for alt in gpx.xpath("//gpx:ele", namespaces = {'gpx': "http://www.topografix.com/GPX/1/1"}):
        Altitud.append(float(alt.text))
    
    for time in gpx.xpath("//gpx:time", namespaces = {'gpx': "http://www.topografix.com/GPX/1/1"}):
        HoraISO.append(dateutil.parser.parse(time.text).replace(tzinfo=None))
    
    for extensions in gpx.xpath("//gpx:extensions", namespaces = {'gpx': "http://www.topografix.com/GPX/1/1"}):
        for tpe in extensions:
            if tpe.tag == '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension':
                for tpx in tpe:
                    if tpx.tag == '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}atemp':
                        TemperaturaAmbiente.append(float(tpx.text))
                    if tpx.tag == '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr':
                        FrecuenciaCardiaca.append(float(tpx.text))
                    if tpx.tag == '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}cad':
                        CadenciaBraceo.append(float(tpx.text))
                        
    # Generacion de la hora local
    OffsetHorario = pytz.timezone(timezonefinder.TimezoneFinder().certain_timezone_at(lat= Latitud[0], lng= Longitud[0])).utcoffset(HoraISO[0])
    Hora = []
    for index, time in enumerate(HoraISO):
        if index > 0:
            Hora.append((time+OffsetHorario))
    
    # Creacion de vectores vacios si tuvieran distinta longitud que la referencia temporal
    if len(Latitud) != len(Hora) or len(Longitud) != len(Hora):
        Latitud = []
        Longitud = []
        for i in range(len(Hora)):
            Latitud.append(0)
            Longitud.append(0)
            
    if len(Altitud) != len(Hora):
        Altitud = []
        for i in range(len(Hora)):
            Altitud.append(0)
    
    if len(TemperaturaAmbiente) != len(Hora):
        TemperaturaAmbiente = []
        for i in range(len(Hora)):
            TemperaturaAmbiente.append(0)
    
    if len(FrecuenciaCardiaca) != len(Hora):
        FrecuenciaCardiaca = []
        for i in range(len(Hora)):
            FrecuenciaCardiaca.append(0)
    
    if len(CadenciaBraceo) != len(Hora):
        CadenciaBraceo = []
        for i in range(len(Hora)):
            CadenciaBraceo.append(0)
            
    # Creacion del DataFrame con la hora como indice ordenado     
    DataFrame = pd.DataFrame({'Hora':Hora,
        'Latitud':Latitud,
        'Longitud':Longitud,
        'Altitud':Altitud,
        'TemperaturaAmbiente':TemperaturaAmbiente,
        'FrecuenciaCardiaca':FrecuenciaCardiaca,
        'CadenciaBraceo':CadenciaBraceo}).set_index('Hora').sort_index()
    
    return Name, Type, DataFrame