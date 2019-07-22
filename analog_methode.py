# -*- coding: utf-8 -*-

"""
Martha Kogler und Vanessa Seitner
"""

##### PAKETE IMPORTIEREN #####
import iris
import xarray as xa
from eofs.xarray import Eof
from eofs.multivariate.iris import MultivariateEof
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import iris.quickplot as qplt
import datetime

##### PFADE DEFINIEREN ######
path = 'JRA-55_subsets/*/*.nc'

##### EINLESEN #####
# Daten als DataArray einlesen, Umbennung der Variablen aus Übersichtsgründen
#latlon voher noch einheitlich einrechnen
def read_data(path):
    data = xa.open_mfdataset(path, decode_cf=True) # Daten werden als xarray Dataset eingelesen
    data = data.rename({'initial_time0_hours': 'time', 'g0_lat_1': 'lat', 'g0_lon_2': 'lon',
                        'PRMSL_GDS0_MSL': 'mslp','RH_GDS0_ISBL':'rh','SPFH_GDS0_ISBL':'sh'}).drop(['initial_time0_encoded','initial_time0'])
    data.coords['lon'].data = (data.coords['lon'] + 180) % 360 - 180
    data = data.sortby(data.lon)
    return data

##### NORMIERTE ANOMALIEN #####
# Tägliche Mittelwerte mittels rollendem Fenster bilden, auch Anomalien und normierte Anomalien berechnen
def daily_mean_anomalies(data, window_size):
    # Daily Mean
    mean = data.resample(time='1D').mean()
    mean = mean.chunk({'time':-1})# mean.chunk(21) #{time}
    daily_roll = mean.rolling(time=window_size,center=True).construct('window_dim') # Rollendes Fenster, 1 in Mitte, 10 Tage davor, 10 Tage danach
    daily_mean = daily_roll.groupby('time.dayofyear').mean(dim=['window_dim', 'time'])
    # Anomalies statt daily_roll normaler mean
    ano = mean.groupby('time.dayofyear') - daily_mean
    # Standard Deviation
    std = daily_roll.groupby('time.dayofyear').std(dim=xa.ALL_DIMS)
    # Normalize
    ano_nom = ano.groupby('time.dayofyear')/std
    ano_nom = ano_nom.chunk({'time': -1})
    return ano_nom

##### XARRAY IN IRIS #####
#def xa_to_iris(xarray_DataArray):
#    cube_mslp = xarray_DataArray['mslp'].to_iris()
#    cube_rh = xarray_DataArray['rh'].to_iris()
#    cube_sh = xarray_DataArray['sh'].to_iris()
#    cube_list = iris.cube.CubeList([cube_mslp, cube_rh, cube_sh])
#    cube = cube_list.concatenate()#[0]
#    return cube


##### EOF BERECHNUNG ####
def eof_multivar(iris_cube):
    solver = MultivariateEof(iris_cube)

    # Schleife die Eofs berechnet bis bestimmte Varianz erreicht wird:
    j=1
    while (j<=100):
        if np.sum(solver.varianceFraction(neigs=j).data)<=0.90:
            j=j+1
        else:
            break
    eof_list = solver.eofs(neofs=j)
    pc_list = solver.pcs(npcs=j)
    return solver, j, eof_list, pc_list

##### berechnete normierte Anomalien laden #####
ano_nom = xa.open_dataset('normierte_anomalien_subset.nc', decode_cf=True)
ano_nom.coords['time'].attrs['axis'] = 'T' # time attributes = 'T' setzen

##### Einstellungen für Analog Methode #####
sel_year = '1960'  # Jahr für welches Analog erstellt werden soll
year = pd.date_range(sel_year+'-01-01', sel_year+'-12-31')
n = 5 # Anzahl der zu suchenden Analoga
len_year = len(ano_nom.groupby('time.year')) # Länge der Zeitreihe

##### Array zum Speichern des Ergebnisses vorbereiten #####
out_pc = []
out_rh = []
out_sh = []
out_mslp = []
# für gefundene Analoga:
output = np.zeros((len(ano_nom.time), n+1), dtype='datetime64[s]')
output[:,0] = ano_nom.time # ersten Spalte sollen Tage sein (Zeitelement)

##### Anwenden der Analog Methode #####

for i, day in enumerate(year):
    # Iteration erfolgt über alle doy_window

    # Zeitfenster erstellen
    start = day - datetime.timedelta(days = 10)
    end = day + datetime.timedelta(days = 10)
    win_dow = pd.date_range(start, end, freq='D')
    window = win_dow.dayofyear

    # Daten die sich im definierten Fenster befinden ausschneiden
    data = ano_nom.sel(time = ano_nom.time.dt.dayofyear.isin(window))
    #data.coords['time'].attrs['axis'] = 'T' # time attributes = 'T' setzen
    #print(data)
    # in Iris Cube:s
    iris_cube = iris.cube.CubeList([data.mslp.to_iris(), data.rh.to_iris(), data.sh.to_iris()]).merge()

    # Daten des aktuellen Tages ausschneiden (benötigt für Pseudo PC Berechnung)
    data_curr = ano_nom.sel(time = ano_nom.time.dt.dayofyear.isin(day.dayofyear))

    # EOF anwenden
    solver, j, eof_list, pc_list = eof_multivar(iris_cube)

    # in Iris Cube:
    current_iris_cube = iris.cube.CubeList([data_curr.rh.to_iris(), data_curr.sh.to_iris(), data_curr.mslp.to_iris()]).merge()

    # Pseudo- PCS berechnen
    pseudo_pc = solver.projectField(current_iris_cube, neofs=j)

    # PC und Pseudo- PCS als xarray DataArray
    xa_pc = xa.DataArray.from_iris(pc_list).rename('pc')
    xa_pseudo_pc = xa.DataArray.from_iris(pseudo_pc).rename('ppc')

    # in output Array speichern
    #out_pc.append(xa_pc)
    #out_mslp.append(xa.DataArray.from_iris(eof_list[0]).rename('EOF_mslp'))
    #out_rh.append(xa.DataArray.from_iris(eof_list[1]).rename('EOF_rh'))
    #out_sh.append(xa.DataArray.from_iris(eof_list[2]).rename('EOF_sh'))

    # über alle jahre iterieren
    for k in range(0,len_year):
        # Norm berechnen:
        norm = ((xa_pc - xa_pseudo_pc[k])**2).sum(dim='pc')

        # aktuelles Jahr aus allen Jahren entfernen:
        norm = norm.sel(time = ~norm.time.dt.year.isin(xa_pseudo_pc.time.to_series()[k].year))
        kday = xa_pseudo_pc.time.to_series().dt.strftime('%Y-%m-%d')[k]

        # Reihe im Ausgabe Array festlegen
        row = np.where(output[:,0] == datetime.datetime.strptime(kday, '%Y-%m-%d'))[0][0]

        # Analog für den aktuellen Tag (Anzahl duch n festgelegt)
        for a in range(1,n+1):
            # Norm minimieren (kleinste Norm = beste Übereinstimmung)
            norm_min = np.argmin(norm).values

            # kte Jahr auslblenden und Analogon bestimmen
            analog = data.sel(time = ~data.time.dt.year.isin(xa_pseudo_pc.time.to_series()[k].year)).time.to_series()[norm_min]

            # Analogon im Array ablegen
            output[row][a] = analog

            # bereits gefunden Minimum herausnehmen, um weitere zu finden
            norm = norm.where(norm.values != norm[norm_min].values)
