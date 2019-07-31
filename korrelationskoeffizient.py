
import xarray as xa
import numpy as np
import cloudpickle
import pandas as pd

analoga_load = cloudpickle.load( open( "Output/Analoga_neu_1961.p", "rb") )
sparta = xa.open_mfdataset('Tx/*.nc')

nr = 4    # Anzahl der Analoga
year = '1961' # zu betrachtendens Jahr
one_year = pd.date_range('1961-01-01', '1961-12-31')

corr = []
string = ["Data"]
for n in range(1,nr+1):
    string.append("Analoga"+str(n))

df = pd.DataFrame(analoga_load,columns=string)
df.index = df["Data"]
df = df.loc[one_year]

analoga = df.to_numpy()

for i, analog_list in enumerate(analoga):
    true_day = sparta.sel(time=analog_list[0]) # tatsächliche Beobachtung
    true_day_values = true_day.Tx.values[~np.isnan(true_day.Tx.values)]

    correlation = []

    for n in range(1,nr+1):
        try:
            days = sparta.sel(time=analog_list[n])
            days_values = days.Tx.values[~np.isnan(days.Tx.values)]

            korrkoef = np.corrcoef(days_values,true_day_values)[0][1]
            correlation.append(korrkoef)
        except KeyError:
            correlation.append(np.nan)

    corr.append(correlation)

cloudpickle.dump(corr, open("Output/correlation_1961.p", "wb" ) )
