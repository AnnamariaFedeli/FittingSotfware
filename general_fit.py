import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as pltt
from sunpy.coordinates import get_horizons_coord
from make_fit_implementations_20210819 import  MAKE_THE_FIT
from make_fit_implementations_20210819 import closest_values
from make_fit_implementations_20210819 import find_c1
from combining_files import *
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
# Import mymodule
import importlib.machinery
import importlib.util
#loader = importlib.machinery.SourceFileLoader( 'savecsv', r'C:\Users\Omistaja\Documents\GitHub\SavingCsv\savecsv.py' )
#spec = importlib.util.spec_from_loader( 'savecsv', loader )
#mymodule = importlib.util.module_from_spec( spec )
#loader.exec_module( mymodule )

# <--------------------------------------------------------------- ALL NECESSARY INPUTS HERE ----------------------------------------------------------------->

# INITIAL INPUTS TO LOAD FILES
# The path to the folder where the data is storaged
# this path is also used to create new files for all and contaminated data.
#                C:\Users\Omistaja\Desktop\SRL\2021SRL\epd_plot-main\solo_loader-main-shift\csv\18-Nov-20 1420-two-slopes

path_to_file = r'C:/Users/Omistaja/Desktop/SRL/2021SRL/messenger/event1.txt'
path_to_savefig =  r'C:/Users/Omistaja/Desktop/SRL/2021SRL/messenger/' # if savefig is true

date_string = ''
event = 'event1'
averaging = ''

file_name = ''
plot_title = 'MESSENGER event 1'

# You can choose the sigma threshold value below which the data points will not be included in the fit
# You can also choose to leave the first HET channel out from the fit by setting  leave_out_1st_het_chan to True
# You can choose to shift step data by a certain factor (I have used 0.8)

sigma = 3
rel_err = 0.5
frac_nan_threshold = 0.9
leave_out_1st_het_chan = False
shift_step_data = False
shift_factor = None #0.8

# !!! INPUTS FOR THE FIT !!!

# which_fit options: 
# 'single' will force a single pl fit to the data
# 'broken' will force a broken pl fit to the data but ONLY if the break point is within the energy range otherwise a sigle pl fit will be produced instead
# 'best_sb' will choose automatically the best fit type between single and broken by comparing the redchis of the fits
# 'best' will choose automatically the best fit type by comparing the redchis of the fits
# 'cut' will produce a broken pl fit with an exponential cutoff point. If the cutoff point is outside of the energy range a broken or single pl will be fit instead


which_fit = 'best' 

#!!! e_min, e_max, break_guess and cut_guess SHOULD BE IN MeV !!!

# e_min and e_max can also be None. In this case the MAKE_THE_FIT function will automaically choose the values

e_min =  None# in MeV
e_max =	0.089# in MeV
g1_guess = -1.9
g2_guess = -2.5
c1_guess = 1e2
alpha_guess = 7.16
break_guess = 0.1#in MeV
cut_guess = 0.12#in MeV

# if use_random = False the fit will only be made once with the guess values
# if use_random = True 
# the fitting function will first create a list of reasonable values for each of the fitting parameters 
# then randomly select values from the lists and compare the redchis of each fit to find the best one
use_random = True 
iterations = 20


savefig = False # save the fit
save_pickle = False # save a pickle file of the odr run
save_fit_variables = False # save the variables from the fit
save_fitrun = False # save all variables used for the fit



# <-------------------------------------------------------------- END OF NECESSARY INPUTS ---------------------------------------------------------------->


make_fit = True


#direction = 'sun'
intensity_label = 'Flux\n/(s cm² sr MeV)'
energy_label = 'primary energy (MeV)'
#peak_info = fit_to+' spec'+'\n'+window_type
legend_title = 'Electrons'  # 'mag' or 'foil' or 'Electrons' if there is more than just ept data
#data_product = 'l2'

#date_str = date_string[8:]+'-'+date_string[5:7]+'-'+date_string[0:4] #DO NOT CHANGE. This is used later for the plot title etc.
#pos = get_horizons_coord('Messenger', date_string, 'id')
#dist = np.round(pos.radius.value, 2)
#distance = f' (R={dist} au)'
#print(distance)
#dist = ''

# <---------------------------------------------------------------LOADING AND SAVING FILES------------------------------------------------------------------->

#print(path_to_file+step_file_name)
data = pd.read_csv(path_to_file, skiprows = 0, sep = ';')
print(data)
data.columns = ['energy', 'energy error', 'intensity', 'intensity error']



#-------------------------------------------------------------------------------------------------------------------------------------------------
color = {'sun':'crimson','asun':'orange', 'north':'darkslateblue', 'south':'c'}
#prim_e = data['Primary_energy']


pickle_path = None
if save_pickle:
	pickle_path = path_to_file+event+'-pickle_'+'-'+which_fit+'.p'

fit_var_path = None
if save_fit_variables:
	fit_var_path = path_to_file+event+'-fit-result-variables_'+which_fit+'.csv'



# <---------------------------------------------------------------------DATA--------------------------------------------------------------------->

# all data
spec_energy = data['energy']
energy_err_low  = data['energy error']
energy_err_high = data['energy error']
spec_flux   = data['intensity']
flux_err    = data['intensity error']


# <----------------------------------------------------------------------FIT AND PLOT------------------------------------------------------------------->

f, ax = plt.subplots(1, figsize=(6, 5), dpi = 200)


if make_fit:
    fit_result = MAKE_THE_FIT(spec_energy, spec_flux, energy_err_low, flux_err, ax, direction='sun', e_min = e_min, e_max = e_max, which_fit=which_fit, g1_guess=g1_guess, g2_guess=g2_guess, alpha_guess=alpha_guess, break_guess=break_guess, cut_guess = cut_guess, c1_guess=c1_guess,use_random = use_random, iterations = iterations, path = pickle_path)
	
ax.errorbar(spec_energy, spec_flux, yerr=flux_err, xerr = energy_err_low, marker='o', markersize= 3 , linestyle='', color='darkorange', alpha = 0.5, label='Data', zorder = -1)
		

energy_range = [0.040,1]

e_range_min = energy_range[0]
e_range_max = energy_range[1]

ax.set_xscale('log')
ax.set_yscale('log')
#locmin = pltt.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=12)
ax.set_xlim(e_range_min-(e_range_min/2), e_range_max+(e_range_max/2))
ax.set_ylim(1e5, 1.1e8)
#ax.yaxis.set_minor_locator(locmin)
#ax.yaxis.set_minor_formatter(pltt.NullFormatter())


plt.legend(title='"'+legend_title+'"',  prop={'size': 7})
plt.ylabel(intensity_label)
plt.xlabel(energy_label)
plt.title(plot_title)
#+'  '+peak_info+'\n'+date_str+'  '+averaging+'  averaging')

if savefig:
	plt.savefig(path_to_savefig+event, dpi=300)

plt.show()
