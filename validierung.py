#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Martha Kogler und Vanessa Seitner
Validierung der Analog Methode mit Spartacus.
"""

##### PAKETE IMPORTIEREN #####
import xarray as xa
import pandas as pd
import numpy as np
import cloudpickle
import datetime
import matplotlib.pyplot as plt

##### PFADE DEFINIEREN ######
#path = 'Output/Normierte_Anomalien/'
path = 'Klimamodellierung-master/Klimamodellierung-master/'
path_save = 'Output'

##### EINLESEN #####
analoga = cloudpickle.load( open( path + "Analoga_neu_1961.p", "rb") )

sparta = xa.open_mfdataset('sparta/Tx/*.nc')
#sparta = sparta.sel(time=~((sparta.time.dt.month == 2) & (sparta.time.dt.day == 29)))

dates = pd.date_range('1961-01-01', '2017-12-31', freq='D')


##### RMSE BERECHNEN #####

RMSE=[]
CORR=[]

for k, j in enumerate(analoga):
    true_day = sparta.Tx_area_mean.sel(time = dates[k])
    print(true_day)
    for i in j:
        days = sparta.Tx_area_mean.sel(time = i)
        print(days)
        if days.values != np.nan and true_day != np.nan:
            rmse = np.sqrt((days.values - true_day.values)**2).mean()
            RMSE.append(rmse)
            print(rmse)
            corr = np.corrcoef(days.values, true_day.values)
            CORR.append(corr)
        else:
            rmse = np.nan
            RMSE.append(rmse)
            

####Plotten######

one_year = pd.date_range('1961-01-01', '1961-12-31', freq='D')


fig = plt.figure(figsize=(15,10))

sub1 = fig.add_subplot(411)
sub1.set_title('RMSE Analogon 1')
sub1.plot(one_year, RMSE[1:365*5:5])
sub1.set_xticks(())
sub1.set_ylim((0,25))

sub2 = fig.add_subplot(412)
sub2.set_title('RMSE Analogon 2')
sub2.plot(one_year, RMSE[2:365*5:5])
sub2.set_xticks(())
sub2.set_ylim((0,25))

sub3 = fig.add_subplot(413)
sub3.set_title('RMSE Analogon 3')
sub3.plot(one_year, RMSE[3:365*5:5])
sub3.set_xticks(())
sub3.set_ylim((0,25))

sub4 = fig.add_subplot(414)
sub4.set_title('RMSE Analogon 4')
sub4.plot(one_year, RMSE[4:365*5:5])
sub4.set_ylim((0,25))


plt.savefig('rmse_one_year.png')

##### SPEICHERN #####
save = 1

if save == 1:
    cloudpickle.dump( rmse, open( path_save + "rmse.p", "wb" ) )