# -*- coding: utf-8 -*-

"""
von Martha Kogler und Vanessa Seitner
Berechnung der normierten Anomalien.
"""

##### BENÖIGTE PAKETE IMPORTIEREN #####
import xarray as xa

##### PFADE DEFINIEREN ######
path = 'JRA-55/*/*.nc'           # Pfad zu den Daten
path_save = 'Output/Normierte_Anomalien/' # Pfad zum Speichern der normiertern Anomalien

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

##### BERECHNETE NORMIERTE ANOMALIEN SPEICHERN #####
save = 1 # zur Auswahl ob die normierten Anomalien gespeichert werden sollen
data = read_data(path)
ano_nom = daily_mean_anomalies(data, 21)

if save == 1:
    if path == 'JRA-55_subsets/*/*.nc':
        ano_nom.to_netcdf(path_save + 'normierte_anomalien_subset.nc')
    else:
        ano_nom.to_netcdf(path_save + 'normierte_anomalien_allyears.nc')
