# -*- coding: utf-8 -*-

"""
von Martha Kogler und Vanessa Seitner
Berechnung der normierten Anomalien.
"""

##### BENÖIGTE PAKETE IMPORTIEREN #####
import xarray as xa
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

##### PFADE DEFINIEREN ######
path = 'JRA-55/*/*.nc'           # Pfad zu den Daten

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

data = read_data(path)


msl = data.mslp.isel(time = 500)

xa.plot.contourf(msl)
plt.show()

ax = plt.axes(projection=ccrs.Orthographic(0, 35))
msl.plot.contourf(ax=ax, transform=ccrs.PlateCarree());
ax.set_global(); ax.coastlines();
plt.show()
plt.savefig('koordinaten')
