# -*- coding: utf-8 -*-
"""
Created on Apr 11 2020

@author: Felix Brinquis

Description: este programa recibe como parametro un fichero en formato TCX Garmin, lee el contenido
del mismo y lo convierte en un dataframe.
"""

# Importacion de librerias
from lxml.etree import parse as lxml_parse
from dateutil.parser import parse as dateutil_parse
import pandas as pd
import numpy as np

def LecturaTCX(ficheroTCX):
    tcx = lxml_parse(ficheroTCX)

    Name = ficheroTCX.split('\\')[-1].split('.')[0]
    for Activity in tcx.xpath("//TrainingCenterDatabase:Activity", namespaces = {'TrainingCenterDatabase': "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}):
        Type = Activity.attrib['Sport']
        
    # Definicion de listas
    HoraISO = []
    Distancia = []
    FrecuenciaCardiaca = []
    Velocidad = []
    CadenciaBraceo = []

    # Extraccion de valores en forma de listas   
    for Trackpoint in tcx.xpath("//TrainingCenterDatabase:Trackpoint", namespaces = {'TrainingCenterDatabase': "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}):
        if Trackpoint.tag == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint':
            for tpt in Trackpoint:
                if tpt.tag == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time':
                    HoraISO.append(dateutil_parse(tpt.text).replace(tzinfo=None))
                if tpt.tag == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters':
                    Distancia.append(float(tpt.text))
                if tpt.tag == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm':
                    for HeartRateBpm in tpt:
                        if HeartRateBpm.tag == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value':
                            FrecuenciaCardiaca.append(float(HeartRateBpm.text))
                if tpt.tag == '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Extensions':
                    for Extensions in tpt:
                        if Extensions.tag == '{http://www.garmin.com/xmlschemas/ActivityExtension/v2}TPX':
                            for ns3 in Extensions:
                                if ns3.tag == '{http://www.garmin.com/xmlschemas/ActivityExtension/v2}Speed':
                                    Velocidad.append(float(ns3.text))
                                if ns3.tag == '{http://www.garmin.com/xmlschemas/ActivityExtension/v2}RunCadence':
                                    CadenciaBraceo.append(float(ns3.text))

            # Control de fallos en el sensor
            for Variable in (Distancia, FrecuenciaCardiaca, Velocidad, CadenciaBraceo):
                if len(HoraISO) > len(Variable):
                    Variable.append(np.nan)
  
    # No tenemos una referencia que permita corregir el indice temporal a la hora local
    
    # Creacion de vectores vacios si tuvieran distinta longitud que la referencia temporal
    for Variable in (Distancia, FrecuenciaCardiaca, Velocidad, CadenciaBraceo):
        if len(Variable) != len(HoraISO):
            Variable = []
            for i in range(len(HoraISO)):
                Variable.append(0) 
        
    # Creacion del DataFrame con la hora como indice ordenado     
    DataFrame = pd.DataFrame({
        'Hora':HoraISO,
        'Distancia':Distancia,
        'FrecuenciaCardiaca':FrecuenciaCardiaca,
        'Velocidad':Velocidad,
        'CadenciaBraceo':CadenciaBraceo}).set_index('Hora').sort_index()
    
    # Si algun valor leido no contiene valores se elimina
    for campo in DataFrame.columns:
        if (DataFrame[campo] == 0).all():
            DataFrame = DataFrame.drop([campo], axis=1)
        
    # Se eliminan duplicados en el indice
    DataFrame = DataFrame[~DataFrame.index.duplicated()]
    
    return Name, Type, DataFrame