# -*- coding: utf-8 -*-

"""
Martha Kogler und Vanessa Seitner
Durchführung der Analog Methode.
"""

##### PAKETE IMPORTIEREN #####
import iris
import xarray as xa
from eofs.multivariate.iris import MultivariateEof
import pandas as pd
import numpy as np
import cloudpickle
import datetime

##### PFADE DEFINIEREN ######
path = 'Output/Normierte_Anomalien/'
path_save = 'Output'

##### BERECHNETE NORMIERTE ANOMALIEN LADEN #####
ano_nom = xa.open_dataset(path + 'normierte_anomalien_allyears.nc', decode_cf=True)
ano_nom.coords['time'].attrs['axis'] = 'T' # time attributes = 'T' setzen

##### EINSTELLUNGEN FÜR ANALOG METHODE #####
sel_year = '1961'  # Jahr für welches Analog erstellt werden soll
year = pd.date_range(sel_year+'-01-01', sel_year+'-12-31')
n = 5 # Anzahl der zu suchenden Analoga
len_year = len(ano_nom.groupby('time.year')) # Länge der Zeitreihe

##### ZUM SPEICHERN VORBEREITEN #####
out_pc = []
out_rh = []
out_sh = []
out_mslp = []
# für gefundene Analoga:
output = np.zeros((len(ano_nom.time), n+1), dtype='datetime64[s]')
output[:,0] = ano_nom.time # ersten Spalte sollen Tage sein (Zeitelement)

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

##### ANWENDEN DER ANALOG METHODE #####
for i, day in enumerate(year):
    # Iteration erfolgt über alle doy_window

    # Zeitfenster erstellen
    start = day - datetime.timedelta(days = 10)
    end = day + datetime.timedelta(days = 10)
    win_dow = pd.date_range(start, end, freq='D')
    window = win_dow.dayofyear

    # Daten die sich im definierten Fenster befinden ausschneiden
    data = ano_nom.sel(time = ano_nom.time.dt.dayofyear.isin(window))
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
    out_pc.append(xa_pc)
    out_mslp.append(xa.DataArray.from_iris(eof_list[0]).rename('EOF_mslp'))
    out_rh.append(xa.DataArray.from_iris(eof_list[1]).rename('EOF_rh'))
    out_sh.append(xa.DataArray.from_iris(eof_list[2]).rename('EOF_sh'))

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

            # bereits gefundenes Minimum herausnehmen, um weitere zu finden
            norm = norm.where(norm.values != norm[norm_min].values)

##### SPEICHERN #####
save = 1

if save == 1:
    cloudpickle.dump( out_rh, open( path_save + "/EOFrh_" + sel_year + ".p", "wb" ) )
    cloudpickle.dump( out_sh, open(path_save + "/EOFsh_" + sel_year + ".p", "wb" ) )
    cloudpickle.dump( out_mslp, open(path_save + "/EOFmslp_" + sel_year + ".p", "wb" ) )
    cloudpickle.dump( output, open( path_save +"/Analoga_" + sel_year + ".p", "wb" ) )
    cloudpickle.dump( out_pc, open(path_save + "/PC_" + sel_year + ".p", "wb" ) )
