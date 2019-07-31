import cloudpickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# Korrelationskoeffizient laden
corr = np.array(cloudpickle.load(open("Output/correlation_1961.p", "rb" )))

year = '1961' # zu betrachtendes Jahr auswählen
nr = 4        # Anzahl der berechneten Analoga
one_year = pd.date_range('1961-01-01', '1961-12-31', freq='D')


fig = plt.figure(figsize=(15,10))

sub1 = fig.add_subplot(411)
sub1.set_title('Korrelationskoeffizient Analogon 1')
sub1.plot(one_year, corr[:,0])
sub1.axhline(0,color="k",ls='--',linewidth=0.5)
sub1.axhline(1,color="k",ls='--',linewidth=0.5)
sub1.set_xticks(())
sub1.set_ylim((-0.7,1.2))

sub2 = fig.add_subplot(412)
sub2.set_title('Korrelationskoeffizient Analogon 2')
sub2.plot(one_year, corr[:,1])
sub2.axhline(0,color="k",ls='--',linewidth=0.5)
sub2.axhline(1,color="k",ls='--',linewidth=0.5)
sub2.set_xticks(())
sub2.set_ylim((-0.7,1.2))

sub3 = fig.add_subplot(413)
sub3.set_title('Korrelationskoeffizient Analogon 3')
sub3.plot(one_year, corr[:,2])
sub3.axhline(0,color="k",ls='--',linewidth=0.5)
sub3.axhline(1,color="k",ls='--',linewidth=0.5)
sub3.set_xticks(())
sub3.set_ylim((-0.7,1.2))

sub4 = fig.add_subplot(414)
sub4.set_title('Korrelationskoeffizient Analogon 4')
sub4.plot(one_year, corr[:,3])
sub4.axhline(0,color="k",ls='--',linewidth=0.5)
sub4.axhline(1,color="k",ls='--',linewidth=0.5)
sub4.set_ylim((-0.7,1.2))

plt.tight_layout()
plt.savefig('correlation_one_year.png')
plt.show()
