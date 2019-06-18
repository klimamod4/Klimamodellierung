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
def xa_to_iris(xarray_DataArray):
    cube_mslp = xarray_DataArray['mslp'].to_iris()
    cube_rh = xarray_DataArray['rh'].to_iris()
    cube_sh = xarray_DataArray['sh'].to_iris()
    cube_list = iris.cube.CubeList([cube_mslp, cube_rh, cube_sh])
    cube = cube_list.concatenate()#[0]
    return cube


##### EOF BERECHNUNG ####
# Eof Analyse eines xarray DataArray
def eof_analyse(xarray_DataArray,neofs):
    solver = Eof(xarray_DataArray.dropna('time'))
    eofs = solver.eofs(neofs)
    return eofs

# Eof Analyse eines Iris Cube
def eof_multivar(iris_cube):
    solver = MultivariateEof(iris_cube)

    # Schleife die Eofs berechnet bis bestimmte Varianz erreicht wird:
    j=1
    while (j<=10):
        if np.sum(solver.varianceFraction(neigs=j).data)<=0.90:
            j=j+1
        else:
            break
    eof_list = solver.eofs(neofs=j)
    pc_list = solver.pcs(npcs=j)
    return eof_list, pc_list




##### ANWENDUNG DER FUNCTIONS #####
#mslp_data = read_data(path)
#ano_nom = daily_mean_anomalies(mslp_data, 21)
#print(ano_nom)
#ano_nom_roll = ano_nom.rolling(time=21, center=True).construct('window_dim')
#print (ano_nom_roll)

#data = read_data(path)
#ano_nom = daily_mean_anomalies(data,21)


ano_nom = xa.open_dataset('normierte_anomalien_subset.nc', decode_cf=True)
iris_cube = xa_to_iris(ano_nom)
eof,pc = eof_multivar(iris_cube)

print(eof[0][10,:,:])


###### PLOTTEN 1.EOF ######
qplt.contourf(eof[0][0])
plt.savefig('EOF.png')


"""
##### PLOTTEN DER ANOMALIEN #####
plt.plot(ano_nom.mslp.isel(lat=15, lon=20))
plt.title('Normierte Anomalien \n lat=15 lon=20')
plt.savefig('Ano_nom.png')
"""