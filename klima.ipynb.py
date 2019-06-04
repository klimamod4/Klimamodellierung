# -*- coding: utf-8 -*-

"""

"""

import iris
import xarray as xa
from eofs.xarray import Eof

# Pfade zu den Daten, in den jeweiligen Ordnern der Parameter sind mehrere *.nc Datein
mslp_path = 'JRA-55_subsets/mslp/*.nc'
rh_path = 'JRA-55_subsets/rh/*.nc'
sh_path = 'JRA-55_subsets/sh/*.nc'

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

mslp_data = read_data(mslp_path)
mslp_mean, mslp_ano = daily_mean_anomalies(mslp_data)
print (mslp_data)

def xarray_to_iris(xarrayDataSet):
    #data_iris = xarrayDataSet[variable].to_iris()
    #iris.cube.Cubelist
    #cube_list.merge
    data = xa.Dataset.to_array(xarrayDataSet)#, coords=['time', 'lat', 'lon']) # xarray DataSet müssen in xarray Dataarrays umgewandelt werden
    # Zeit muss erste Dimension sein:
    data = data.transpose('time','lat','lon','variable')
    # xarray in Iris Cube umwandeln:
    #data_iris = data.to_iris()
    return data, data_iris

mslp, mslp_iris = xarray_to_iris(mslp_ano)
print (mslp)
print ('xxxxxx')
print (mslp_iris)
"""
def eof_analyse(xarray_DataArray,neofs=None):
    solver = Eof(xarray_DataArray)
    eofs = solver.eofs(neofs=neofs)
    return eofs

test = eof_analyse(mslp, 2)
print (test)
"""