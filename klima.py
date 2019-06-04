# -*- coding: utf-8 -*-

"""
Martha Kogeler und Vanessa Seitner
"""


##### PAKETE IMPORTIEREN #####
import iris
import xarray as xa
from eofs.xarray import Eof

##### PFADE DEFINIEREN ######
# Pfade zu den Daten, in den jeweiligen Ordnern der Parameter sind mehrere *.nc Datein
mslp_path = 'JRA-55_subsets/mslp/*.nc'
rh_path = 'JRA-55_subsets/rh/*.nc'
sh_path = 'JRA-55_subsets/sh/*.nc'

##### EINLESEN #####
# Daten als DataArray einlesen, Umbennung der Variablen aus Übersichtsgründen
def read_data(path):
    data = xa.open_mfdataset(path)     # Daten werden als xarray Dataset eingelesen
    data = data.rename({'initial_time0_hours': 'time', 'g0_lat_1': 'lat', 'g0_lon_2': 'lon'}).drop('initial_time0_encoded')
    if path == mslp_path:
        data = data.rename({'PRMSL_GDS0_MSL': 'mslp'})
    elif path == rh_path:
        data = data.rename({'RH_GDS0_ISBL':'rh'})
    else:
        data = data.rename({'SPFH_GDS0_ISBL':'sh'})
    return data

##### NORMIERTE ANOMALIEN #####
# Tägliche Mittelwerte mittels rollendem Fenster bilden, auch Anomalien und normierte Anomalien berechnen
def daily_mean_anomalies(data):
    # Daily Mean
    mean = data.resample(time='1D').mean()
    mean = mean.chunk(21)
    daily_roll = mean.rolling(time=21,center=1).mean() # Rollendes Fenster, 1 in Mitte, 10 Tage davor, 10 Tage danach
    daily_mean = daily_roll.groupby('time.dayofyear').mean('time')
    # Anomalies
    ano = daily_roll.groupby('time.dayofyear') - daily_mean
    # Standard Deviation
    std = daily_mean.groupby('dayofyear').std()
    # Normalize
    ano_nom = ano.groupby('time.dayofyear')/std
    return daily_mean, ano_nom

##### XARRAY DATASET IN XARRAY DATAARRAY #####
# für Eof Berechnung mit xarray, muss dem EOF Solver ein DataArray übergeben werden
def xaDataSet_to_xaDataArray(xarrayDataSet, parameter):
    if parameter == 'mslp':
        data = xarrayDataSet['mslp']
    elif parameter == 'rh':
        data = xarrayDataSet['rh']
    else:
        data = xarrayDataSet['sh']
    return data

##### EOF BERECHNUNG ####
# Eof Analyse eines xarray DataArray
def eof_analyse(xarray_DataArray,neofs):
    solver = Eof(xarray_DataArray)
    eofs = solver.eofs(neofs)
    return eofs
    # Hier liegt noch ein Fehler, eventuell falsche Reihenfolge der Parameter...?


##### ANWENDUNG DER FUNCTIONS #####
mslp_data = read_data(mslp_path)
mslp_mean, mslp_ano = daily_mean_anomalies(mslp_data)
mslp = xaDataSet_to_xaDataArray(mslp_ano,'mslp') # Dataarray der normierten Anomalien
eof_mslp = eof_analyse(mslp,2)

##### ÜBERPRÜFEN #####
print (mslp_ano)
print (mslp)
print (eof_mslp)
