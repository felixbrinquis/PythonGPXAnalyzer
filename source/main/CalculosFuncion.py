# -*- coding: utf-8 -*-
"""
Created on Mar 9 2019

@author: Felix Brinquis

Description: este programa recibe como parametro un dataframe inicial en bruto leido en formato GPX y realiza 
todos los calculos necesarios para obtener informacion comprensible y representable.
"""


"""
    DEFINICION DEL ENTORNO
"""
# Importacion de librerias
import pandas as pd
import numpy as np
import geopy.distance
import datetime
from math import ceil
import os
from scipy.signal import savgol_filter


def CalculosDataframe(df):

    # Si la actividad no tuviera alguno de estos campos lo completamos con 0 
    df['TemperaturaAmbiente'] = df['TemperaturaAmbiente'].fillna(0)
    df['FrecuenciaCardiaca'] = df['FrecuenciaCardiaca'].fillna(0)
    df['CadenciaBraceo'] = df['CadenciaBraceo'].fillna(0)
    
    # Creacion de campos auxiliares
    df['LatitudAnterior'] = df['Latitud'].shift().fillna(df['Latitud'])
    df['LongitudAnterior'] = df['Longitud'].shift().fillna(df['Longitud'])
    df['HoraMuestra'] = df.index
    df['DeltaTiempo'] = (df['HoraMuestra']-df['HoraMuestra'].shift()).fillna(0)
    
    # Seleccion de la frecuencia de muestreo de los datos GPS
    FrecuenciaMuestreo = df['DeltaTiempo'].value_counts().idxmax().total_seconds()
    
    
    """
        CALCULOS INICIALES
        En este bloque se realiazan los calculos iniciales a partir de los datos brutos.
        Estos datos son susceptibles de sufrir variaciones importantes ya que la frecuencia de muestreo de los datos puede ser muy elevada 
        para poder registrar valores instantaneos de coordenadas o altitud con precision.
        Para poder afinar estos datos a valores mas cercanos a la realidad sera necesario un paso posterior en el que se calculen las diferencias
        de distancia o altitud con una frecuencia de muestreo mas baja.
    """
    HoraInicioActiviad = df.index.min()
    HoraFinActiviad = df.index.max()
    df['TiempoTotal'] = df['HoraMuestra'] - HoraInicioActiviad
    DistanciaAcumulada = 0
    DistanciaBloque = 0
    Bloque = 1
    NumeroMuestrasPorBloque = 1
    Velocidad_i = np.nan
    TiempoActividad = datetime.timedelta(seconds=0)
    
    AltitudInicio, AltitudFin = df.loc[df.index.min() == df.index, ['Altitud']].min()[0], df.loc[df.index.max() == df.index, ['Altitud']].min()[0]
    AltitudAnterior = AltitudInicio
    
    for index, row in df.iterrows():
        # Calculo de la diferencia de distancia entre 2 coordenadas
        if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
            dDistancia = geopy.distance.distance((row.Latitud, row.Longitud), (row.LatitudAnterior, row.LongitudAnterior)).m
            Velocidad_i = np.divide(dDistancia, row['DeltaTiempo'].total_seconds())
            TiempoActividad = TiempoActividad + row['DeltaTiempo']
        else:
            dDistancia = 0
        
        # Calculo de la cadencia
        Cadencia = row['CadenciaBraceo']*2 # El dato de cadencia registrado es solo de 1 braceo
    
        # Calculo de distancia acumulada
        DistanciaAcumulada = DistanciaAcumulada + dDistancia
        
        # Identificacion de pausas en el muestreo de datos
        if row['DeltaTiempo'].total_seconds() > FrecuenciaMuestreo:
            Bloque+=1
            NumeroMuestrasPorBloque = 1
            DistanciaBloque = 0
        else:
             NumeroMuestrasPorBloque+=1
             DistanciaBloque = DistanciaBloque + dDistancia
             
        # Asignacion de los valores calculados en el DataFrame
        df.at[index,'TiempoActividad'] = TiempoActividad
        df.at[index,'dDistancia'] = dDistancia
        df.at[index,'Velocidad_i'] = Velocidad_i
        df.at[index,'Cadencia'] = Cadencia
        df.at[index,'DistanciaAcumulada'] = DistanciaAcumulada
        df.at[index,'Bloque'] = Bloque
        df.at[index,'NumeroMuestrasPorBloque'] = NumeroMuestrasPorBloque
        df.at[index,'DistanciaBloque'] = DistanciaBloque 
    df = df.drop('LatitudAnterior', 1)
    df = df.drop('LongitudAnterior', 1)
    df = df.drop('CadenciaBraceo', 1)
    df = df.drop('HoraMuestra', 1)
    df['Velocidad_i'] = df['Velocidad_i'].fillna(method='bfill')
    
    # Calculo de valores totales
    DistanciaTotal = df['DistanciaAcumulada'].max()
    TiempoActividad = df['TiempoActividad'].max()
    TiempoTranscurrido =  df['TiempoTotal'].max()
    
    
            
    """
        SUAVIZADO DE DATOS
        El suavizado de los datos a analizar lo realizaremos en primera instancia agrupado por bloques continuos debido a las discontinuidades
        que generan las pausas temporales. Si el tamaño del bloque no es superior al numero de muestras minimo del metodo Savitzky-Golay
        se tomara el valor calculado sobre el total de los datos para ese bloque. Si la actividad no tuviera un tamaño minimo, no se
        aplicaria este metodo.
        Tambien se realizan distintos suavizados por medias moviles con ventanas temporales dependientes de la frecuencia de muestreo que
        van desde los 5 segundos a los 30.
        Finalmente seleccionamos un unico valor calculado que será el que mejor se adapte a cada proposito. 
    """
    # Identificacion del numero de Bloques temporales
    MIN_Bloque = int(df['Bloque'].min())
    MAX_Bloque = int(df['Bloque'].max())
    
    # Calculo de ventanas de medias moviles(VMM_n) dependientes de la frecuencia de muestreo de los datos
    VMM_5 = ceil(5/FrecuenciaMuestreo)
    VMM_10 = ceil(10/FrecuenciaMuestreo)
    VMM_15 = ceil(15/FrecuenciaMuestreo)
    VMM_20 = ceil(20/FrecuenciaMuestreo)
    VMM_30 = ceil(30/FrecuenciaMuestreo)
    
    # Suavizado de los datos por el metodo Savitzky-Golay
    MuestrasAlt = 21
    MuestrasVel = 31
    MuestrasFC = 9
    MuestrasCad = 5
    
    # El metodo Savitzky-Golay solo se aplicara si la actividad tiene una duracion minima
    df['Altitud_SAVGOL'] = np.nan
    df['Velocidad_SAVGOL'] = np.nan
    df['FrecuenciaCardiaca_SAVGOL'] = np.nan
    df['Cadencia_SAVGOL'] = np.nan
    if df.shape[0] >= max(MuestrasAlt, MuestrasVel, MuestrasFC, MuestrasCad):
    
        # Seleccion de bloques con numero de muestras superior al necesario por dato
        VectorMuestrasMinimas = df.groupby('Bloque')['Bloque'].count()
        BloquesMuestreablesAlt = []
        BloquesMuestreablesVel = []
        BloquesMuestreablesFC = []
        BloquesMuestreablesCad = []
        for i, muestras in enumerate(VectorMuestrasMinimas):
            Bloque = i+1
            if muestras >= MuestrasAlt:
                BloquesMuestreablesAlt.append(Bloque)
            if muestras >= MuestrasVel:
                BloquesMuestreablesVel.append(Bloque)
            if muestras >= MuestrasFC:
                BloquesMuestreablesFC.append(Bloque)
            if muestras >= MuestrasCad:
                BloquesMuestreablesCad.append(Bloque)    
    
        # Altitud SAVGOL
        df['Altitud_SAVGOL_Bloque'] = np.nan
        df['Altitud_SAVGOL_Bloque'] = np.nan
        df['Altitud_SAVGOL_Total'] = df.loc[df['Bloque'].isin(BloquesMuestreablesAlt)][['Bloque', 'Altitud']].groupby('Bloque').transform(lambda x: savgol_filter(tuple(x), MuestrasAlt, 3))
        df['Altitud_SAVGOL_Total'] = df['Altitud'].transform(lambda x: savgol_filter(tuple(x), MuestrasAlt, 3))
        df['Altitud_SAVGOL'] = df.Altitud_SAVGOL_Bloque.combine_first(df.Altitud_SAVGOL_Total)
        df = df.drop('Altitud_SAVGOL_Bloque', 1)
        df = df.drop('Altitud_SAVGOL_Total', 1)
        
        # Velocidad SAVGOL
        df['Velocidad_SAVGOL_Bloque'] = np.nan
        df['Velocidad_SAVGOL_Bloque'] = np.nan
        df['Velocidad_SAVGOL_Total'] = df.loc[df['Bloque'].isin(BloquesMuestreablesVel)][['Bloque', 'Velocidad_i']].groupby('Bloque').transform(lambda x: savgol_filter(tuple(x), MuestrasVel, 3))
        df['Velocidad_SAVGOL_Total'] = df['Velocidad_i'].transform(lambda x: savgol_filter(tuple(x), MuestrasVel, 3))
        df['Velocidad_SAVGOL'] = df.Velocidad_SAVGOL_Bloque.combine_first(df.Velocidad_SAVGOL_Total)
        df = df.drop('Velocidad_SAVGOL_Bloque', 1)
        df = df.drop('Velocidad_SAVGOL_Total', 1)
        
        # Frecuencia cardiaca SAVGOL
        df['FrecuenciaCardiaca_SAVGOL_Bloque'] = np.nan
        df['FrecuenciaCardiaca_SAVGOL_Bloque'] = np.nan
        df['FrecuenciaCardiaca_SAVGOL_Total'] = df.loc[df['Bloque'].isin(BloquesMuestreablesFC)][['Bloque','FrecuenciaCardiaca']].groupby('Bloque').transform(lambda x: savgol_filter(tuple(x), MuestrasFC, 3))
        df['FrecuenciaCardiaca_SAVGOL_Total'] = df['FrecuenciaCardiaca'].transform(lambda x: savgol_filter(tuple(x), MuestrasFC, 3))
        df['FrecuenciaCardiaca_SAVGOL'] = df.FrecuenciaCardiaca_SAVGOL_Bloque.combine_first(df.FrecuenciaCardiaca_SAVGOL_Total)
        df = df.drop('FrecuenciaCardiaca_SAVGOL_Bloque', 1)
        df = df.drop('FrecuenciaCardiaca_SAVGOL_Total', 1)
        
        # Cadencia SAVGOL
        df['Cadencia_SAVGOL_Bloque'] = np.nan
        df['Cadencia_SAVGOL_Bloque'] = np.nan
        df['Cadencia_SAVGOL_Total'] = df.loc[df['Bloque'].isin(BloquesMuestreablesCad)][['Bloque', 'Cadencia']].groupby('Bloque').transform(lambda x: savgol_filter(tuple(x), MuestrasCad, 3))
        df['Cadencia_SAVGOL_Total'] = df['Cadencia'].transform(lambda x: savgol_filter(tuple(x), MuestrasCad, 3))
        df['Cadencia_SAVGOL'] = df.Cadencia_SAVGOL_Bloque.combine_first(df.Cadencia_SAVGOL_Total)
        df = df.drop('Cadencia_SAVGOL_Bloque', 1)
        df = df.drop('Cadencia_SAVGOL_Total', 1)
    
    
    # Calculo de medias moviles dependientes de la frecuencia de muestreo por bloque
    df['dDistancia_5'] = df.groupby('Bloque')['dDistancia'].transform(lambda x: x.rolling(VMM_5, VMM_5).mean().bfill())
    df['dDistancia_10'] = df.groupby('Bloque')['dDistancia'].transform(lambda x: x.rolling(VMM_10, VMM_10).mean().bfill())
    df['dDistancia_15'] = df.groupby('Bloque')['dDistancia'].transform(lambda x: x.rolling(VMM_15, VMM_15).mean().bfill())
    df['dDistancia_20'] = df.groupby('Bloque')['dDistancia'].transform(lambda x: x.rolling(VMM_20, VMM_20).mean().bfill())
    
    df['Altitud_20'] = df.groupby('Bloque')['Altitud'].transform(lambda x: x.rolling(VMM_20, VMM_20).median().bfill())
    
    df['Velocidad_5'] = df.groupby('Bloque')['Velocidad_i'].transform(lambda x: x.rolling(VMM_5, VMM_5).mean().bfill())
    df['Velocidad_10'] = df.groupby('Bloque')['Velocidad_i'].transform(lambda x: x.rolling(VMM_10, VMM_10).mean().bfill())
    df['Velocidad_15'] = df.groupby('Bloque')['Velocidad_i'].transform(lambda x: x.rolling(VMM_15, VMM_15).mean().bfill())
    df['Velocidad_20'] = df.groupby('Bloque')['Velocidad_i'].transform(lambda x: x.rolling(VMM_20, VMM_20).mean().bfill())
    
    df['FrecuenciaCardiaca_5'] = df.groupby('Bloque')['FrecuenciaCardiaca'].transform(lambda x: x.rolling(VMM_5, VMM_5).mean().bfill())
    df['FrecuenciaCardiaca_10'] = df.groupby('Bloque')['FrecuenciaCardiaca'].transform(lambda x: x.rolling(VMM_10, VMM_10).mean().bfill())
    df['FrecuenciaCardiaca_15'] = df.groupby('Bloque')['FrecuenciaCardiaca'].transform(lambda x: x.rolling(VMM_15, VMM_15).mean().bfill())
    df['FrecuenciaCardiaca_20'] = df.groupby('Bloque')['FrecuenciaCardiaca'].transform(lambda x: x.rolling(VMM_20, VMM_20).mean().bfill())
    
    df['Cadencia_5'] = df.groupby('Bloque')['Cadencia'].transform(lambda x: x.rolling(VMM_5, VMM_5).mean().bfill())
    df['Cadencia_10'] = df.groupby('Bloque')['Cadencia'].transform(lambda x: x.rolling(VMM_10, VMM_10).mean().bfill())
    df['Cadencia_15'] = df.groupby('Bloque')['Cadencia'].transform(lambda x: x.rolling(VMM_15, VMM_15).mean().bfill())
    df['Cadencia_20'] = df.groupby('Bloque')['Cadencia'].transform(lambda x: x.rolling(VMM_20, VMM_20).mean().bfill())
    
    
    # Seleccion de un valor calculado
    df['AltitudCalculada'] = round(df.Altitud_SAVGOL.combine_first(df.Altitud_20), 1)
    df['VelocidadCalculada'] = round(df.Velocidad_SAVGOL.combine_first(df.Velocidad_5), 2)
    df['FrecuenciaCardiacaCalculada'] = round(df.FrecuenciaCardiaca_SAVGOL.combine_first(df.FrecuenciaCardiaca_10))
    df['CadenciaCalculada'] = round(df.Cadencia_SAVGOL.combine_first(df.Cadencia_10))
    
    # Correccion de valores atipicos
    for index, row in df.iterrows():
        if row.CadenciaCalculada <= 0:
            CadenciaCorregida = np.nan
        else:
            CadenciaCorregida = row.CadenciaCalculada        
        if row.VelocidadCalculada <= 0:
            VelocidadCorregida = np.nan
        else:
            VelocidadCorregida = row.VelocidadCalculada
        if row.FrecuenciaCardiacaCalculada <= 0:
            FrecuenciaCardiacaCorregida = np.nan        
        else:
            FrecuenciaCardiacaCorregida = row.FrecuenciaCardiacaCalculada
        df.at[index,'CadenciaCalculada'] = CadenciaCorregida         
        df.at[index,'VelocidadCalculada'] = VelocidadCorregida    
        df.at[index,'FrecuenciaCardiacaCalculada'] = FrecuenciaCardiacaCorregida    
    df['CadenciaCalculada'] = df['CadenciaCalculada'].fillna(method='ffill').fillna(0).astype(int)
    df['VelocidadCalculada'] = df['VelocidadCalculada'].fillna(method='ffill').fillna(0)
    df['FrecuenciaCardiacaCalculada'] = df['FrecuenciaCardiacaCalculada'].fillna(method='ffill').fillna(0).astype(int)
    
    
    # Eliminacion de datos auxiliares
    df = df.drop('dDistancia_5', 1)
    df = df.drop('dDistancia_10', 1)
    df = df.drop('dDistancia_15', 1)
    df = df.drop('dDistancia_20', 1)
    
    df = df.drop('Altitud_SAVGOL', 1)
    df = df.drop('Altitud_20', 1)
    
    df = df.drop('Velocidad_SAVGOL', 1)
    df = df.drop('Velocidad_5', 1)
    df = df.drop('Velocidad_10', 1)
    df = df.drop('Velocidad_15', 1)
    df = df.drop('Velocidad_20', 1)
    
    df = df.drop('FrecuenciaCardiaca_SAVGOL', 1)
    df = df.drop('FrecuenciaCardiaca_5', 1)
    df = df.drop('FrecuenciaCardiaca_10', 1)
    df = df.drop('FrecuenciaCardiaca_15', 1)
    df = df.drop('FrecuenciaCardiaca_20', 1)
    
    df = df.drop('Cadencia_SAVGOL', 1)
    df = df.drop('Cadencia_5', 1)
    df = df.drop('Cadencia_10', 1)
    df = df.drop('Cadencia_15', 1)
    df = df.drop('Cadencia_20', 1)
    
    
    
    """
        RITMO [MIN/KM]
        Calculo del ritmo en min/km
    """
    for index, row in df.iterrows():
        # Calculo del ritmo equivalente    
        if row['VelocidadCalculada'] >= 0.5:
            Ritmo = datetime.timedelta(seconds=1000/row['VelocidadCalculada'])
        else:
            Ritmo = np.nan
    
        # Asignacion de los valores calculados en el DataFrame
        df.at[index,'Ritmo'] = Ritmo
    df['Ritmo'] = df['Ritmo'].fillna(method='bfill')    
    
    
    
    """
        CALCULOS SUAVIZADOS    
        Para minimizar los errores generados por la precision de los sensores realizamos una reduccion de la frecuencia de calculo.
        El valor de altitud que mejores resultados de desnivel acumulado ha arrojado es la media movil agrupada por bloques sin pausas
        con una ventana movil de 20 observaciones, reiniciando la posicion inicial de altitud a la medida real en cada pausa.
    """
    ContadorDesnivel = 0
    Pendiente = 0
    DesnivelPositivoAcumulado = 0
    DesnivelNegativoAcumulado = 0
    MuestrasCadencia = 0
    SumaCadencia = 0
    DistanciaAnteriorCadencia = 0
    LongitudZancada = float('NaN')
    df['Altitud_20'] = df.groupby('Bloque')['Altitud'].transform(lambda x: x.rolling(VMM_20, VMM_20).median().bfill())
    CadenciaAnterior = df[df.index.min()==df.index]['Cadencia'].min()
    
    for index, row in df.iterrows(): 
        # Calculo del desnivel acumulado
        if row['DeltaTiempo'].total_seconds() == 0:
            # Inicializacion en la primera lectura
            AltitudAnterior = row['Altitud']
            AltitudPendiente = row['Altitud']
            DistanciaAnterior = row ['DistanciaAcumulada']
            Pendiente = 0
            DesnivelPositivoAcumulado = 0
            DesnivelNegativoAcumulado = 0
        else:
            # Se mide solo el desnivel en funcionamiento
            if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
                # Diferencia de altitud instantanea
                DeltaAltitud = row['Altitud_20'] - AltitudAnterior
                DeltaDistancia = row['DistanciaAcumulada'] - DistanciaAnterior
                # El conteo del desnivel cada segundo da un error del 25%. Hay que reducir la frecencia de captura del dato
                if ContadorDesnivel < 10/FrecuenciaMuestreo:
                    # Si el desnivel es superior a 2 metros se contabiliza, sino se añade un retraso
                    if DeltaAltitud >= 2:
                        if DeltaDistancia > 0:
                            DesnivelPositivoAcumulado = DesnivelPositivoAcumulado + DeltaAltitud
                            AltitudAnterior = row['Altitud_20']
                            if row['NumeroMuestrasPorBloque'] > 10:
                                Pendiente = (row['Altitud_20'] - AltitudPendiente)/DeltaDistancia*100
                                AltitudPendiente = row['Altitud_20']
                            DistanciaAnterior = row ['DistanciaAcumulada']
                            ContadorDesnivel = 0
                    elif DeltaAltitud <= -2: 
                        if DeltaDistancia > 0:
                            DesnivelNegativoAcumulado = DesnivelNegativoAcumulado + abs(DeltaAltitud)
                            AltitudAnterior = row['Altitud_20']
                            if row['NumeroMuestrasPorBloque'] > 10:
                                Pendiente = (row['Altitud_20'] - AltitudPendiente)/DeltaDistancia*100
                                AltitudPendiente = row['Altitud_20']
                            DistanciaAnterior = row ['DistanciaAcumulada']
                            ContadorDesnivel = 0
                    else:
                        ContadorDesnivel+=1
                else:
                    # Si transcurren 10 segundos sin contabilizar una diferenca, se añade
                    if DeltaAltitud > 0:
                        if DeltaDistancia > 0:
                            DesnivelPositivoAcumulado = DesnivelPositivoAcumulado + DeltaAltitud
                            AltitudAnterior = row['Altitud_20']
                            if row['NumeroMuestrasPorBloque'] > 10:
                                Pendiente = (row['Altitud_20'] - AltitudPendiente)/DeltaDistancia*100
                                AltitudPendiente = row['Altitud_20']
                            DistanciaAnterior = row ['DistanciaAcumulada']
                            ContadorDesnivel = 0
                    elif DeltaAltitud < 0:
                        if DeltaDistancia > 0:
                            DesnivelNegativoAcumulado = DesnivelNegativoAcumulado + abs(DeltaAltitud)
                            AltitudAnterior = row['Altitud_20']
                            if row['NumeroMuestrasPorBloque'] > 10:
                                Pendiente = (row['Altitud_20'] - AltitudPendiente)/DeltaDistancia*100
                                AltitudPendiente = row['Altitud_20']
                            DistanciaAnterior = row ['DistanciaAcumulada']
                            ContadorDesnivel = 0
                    else:
                        ContadorDesnivel = 0
            else:
                # Correccion de valores en las pausas
                AltitudAnterior = row['Altitud']
                AltitudPendiente = row['Altitud']
                DistanciaAnterior = row ['DistanciaAcumulada']
        
        # Calculo de la longitud de zancada
        if row.CadenciaCalculada > 0:
            if row['DeltaTiempo'].total_seconds() == 0:
                LongitudZancada = float('NaN')
                DistanciaAnteriorCadencia = row['DistanciaAcumulada']
                MuestrasCadencia = 1
                SumaCadencia = row['Cadencia']
                CadenciaAnterior = row['Cadencia']
            else:
                if row['DeltaTiempo'].total_seconds() == FrecuenciaMuestreo:
                    MuestrasCadencia+=1
                    SumaCadencia = SumaCadencia + row['Cadencia'] 
                    # Si se aprecia una variacion sustancial en la cadencia se registra
                    if MuestrasCadencia < 5/FrecuenciaMuestreo:
                        if row['Cadencia'] < 0.8*CadenciaAnterior or row['Cadencia'] > 1.2*CadenciaAnterior:
                            try:
                                LongitudZancada = (row['DistanciaAcumulada']-DistanciaAnteriorCadencia)/((SumaCadencia)/60)
                            except:
                                LongitudZancada = 0
                            DistanciaAnteriorCadencia = row['DistanciaAcumulada']
                            MuestrasCadencia = 0
                            SumaCadencia = 0
                    else:
                        try:
                            LongitudZancada = (row['DistanciaAcumulada']-DistanciaAnteriorCadencia)/((SumaCadencia)/60)
                        except:
                            LongitudZancada = 0
                        DistanciaAnteriorCadencia = row['DistanciaAcumulada']
                        MuestrasCadencia = 0
                        SumaCadencia = 0
                    CadenciaAnterior = row['Cadencia'] 
                else:
                    LongitudZancada = float('NaN')
                    DistanciaAnteriorCadencia = row['DistanciaAcumulada']
                    MuestrasCadencia = 1
                    SumaCadencia = row['Cadencia']
                    CadenciaAnterior = row['Cadencia']
        else:
            LongitudZancada = 0
    
            # Asignacion de los valores calculados en el DataFrame
        df.at[index,'LongitudZancada'] = LongitudZancada
        df.at[index,'PendienteCalculada'] = Pendiente
        df.at[index,'DesnivelPositivoAcumulado'] = DesnivelPositivoAcumulado
        df.at[index,'DesnivelNegativoAcumulado'] = DesnivelNegativoAcumulado
    df['Pendiente'] = df['PendienteCalculada'].transform(lambda x: x.rolling(VMM_20, VMM_20).mean().bfill())
    df['LongitudZancada'] = df['LongitudZancada'].fillna(method='bfill')
    df = df.drop('PendienteCalculada', 1)

    # Calculo de desniveles finales
    DesnivelPositivo = df['DesnivelPositivoAcumulado'].max()
    DesnivelNegativo = df['DesnivelNegativoAcumulado'].max()
    DesnivelAcumulado = DesnivelPositivo + DesnivelNegativo
    DesnivelPorKilometro = (DesnivelAcumulado/DistanciaTotal)*1000

    return df