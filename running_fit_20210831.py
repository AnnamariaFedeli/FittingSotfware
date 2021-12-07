import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as pltt
#from sunpy.coordinates import get_horizons_coord
from make_fit_implementations_20210819 import  MAKE_THE_FIT
from make_fit_implementations_20210819 import closest_values
from make_fit_implementations_20210819 import find_c1
from combining_files_average_window import combine_data, low_sigma_threshold, delete_low_sigma, first_het_chan
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

# <--------------------------------------------------------------- ALL NECESSARY INPUTS HERE ----------------------------------------------------------------->

# INITIAL INPUTS TO LOAD FILES
# The path to the folder where the data is storaged
# this path is also used to create new files for all and contaminated data.
#                C:\Users\Omistaja\Desktop\SRL\2021SRL\epd_plot-main\solo_loader-main-shift\csv\18-Nov-20 1420-two-slopes

path_to_file = r'C:/Users/Omistaja/Desktop/SRL/2021SRL/epd_plot-main/solo_loader-main-shift/csv/18-Nov-20-1420-10min-slope/'
path_to_savefig =  r'C:/Users/Omistaja/Desktop/SRL/2021SRL/epd_plot-main/solo_loader-main-shift/fits/18-Nov-20-1420-10min-slope/'# if savefig is true


date_string = '2020-11-18'
averaging = '5min'


step_file_name = 'electron_data-'+date_string+'-step-l2-'+averaging+'_averaging.csv'
ept_file_name = 'electron_data-'+date_string+'-ept-l2-'+averaging+'_averaging-ion_corr.csv'
het_file_name = 'electron_data-'+date_string+'-het-l2-'+averaging+'_averaging.csv'


# You can choose the sigma threshold value below which the data points will not be included in the fit
# You can also choose to leave the first HET channel out from the fit by setting  leave_out_1st_het_chan to True
# You can choose to shift step data by a certain factor (I have used 0.8)

sigma = 3
leave_out_1st_het_chan = True
shift_step_data = False
shift_factor = 0.8


# !!! INPUTS FOR THE FIT !!!

fit_type = 'ept' # fit_type options: step, ept, het, step_ept, step_ept_het  
fit_to = 'peak'   # 'peak' or 'average'for window peak or average
window_type = '10min slope D = 1.3 AU'
slope = 'slope_13'

#window_type = 'two slopes D = 1.1 AU & 1.6 AU'
#slope = 'two_slopes_11_16'
# which_fit options: 
# 'single' will force a single pl fit to the data
# 'broken' will force a broken pl fit to the data but ONLY if the break point is within the energy range otherwise a sigle pl fit will be produced instead
# 'best' will choose automatically the best fit type by comparing the redchis of the fits
# 'cut' will produce a broken pl fit with an exponential cutoff point. If the cutoff point is outside of the energy range a broken or single pl will be fit instead

which_fit = 'broken' 

#!!! e_min, e_max, break_guess and cut_guess SHOULD BE IN MeV !!!
# step energy range: 0.004323343613-0.07803193193
# ept energy range: 0.03295087252-0.452730295
# het energy range: 0.6859485403-10.62300287
# second het channel: 1.590048112
# e_min and e_max can also be None. In this case the MAKE_THE_FIT function will automaically choose the values

e_min =  0.004323343613# in MeV
e_max =	1.590048112 # in MeV
g1_guess = -1.9
g2_guess = -2.5
c1_guess = 1e3
alpha_guess = 7.16
break_guess = 0.1#in MeV
cut_guess = 0.12#in MeV

# if use_random = False the fit will only be made once with the guess values
# if use_random = True 
# the fitting function will first create a list of reasonable values for each of the fitting parameters 
# then randomly select values from the lists and compare the redchis of each fit to find the best one
use_random = True 
iterations = 15


savefig = True # save the fit
save_pickle = False # save a pickle file of the odr run

# <-------------------------------------------------------------- END OF NECESSARY INPUTS ---------------------------------------------------------------->


make_fit = True
peak_spec = True
backsub = True

direction = 'sun'
intensity_label = 'Flux\n/(s cm² sr MeV)'
energy_label = 'primary energy (MeV)'
peak_info = fit_to+' spec'+'\n'+window_type
legend_title = 'Electrons'  # 'mag' or 'foil' or 'Electrons' if there is more than just ept data
data_product = 'l2'

date_str = date_string[8:]+'-'+date_string[5:7]+'-'+date_string[0:4] #DO NOT CHANGE. This is used later for the plot title etc.
#pos = get_horizons_coord('Solar Orbiter', startdate, 'id')
#dist = np.round(pos.radius.value, 2)
dist = ''

# <---------------------------------------------------------------LOADING AND SAVING FILES------------------------------------------------------------------->

#print(path_to_file+step_file_name)
step_data = pd.read_csv(path_to_file+step_file_name)
ept_data = pd.read_csv(path_to_file+ept_file_name)
het_data = pd.read_csv(path_to_file+het_file_name)
#print(step_data)
if shift_step_data:
	step_data['Bg_subtracted_'+fit_to] = shift_factor*step_data['Bg_subtracted_'+fit_to]

data = combine_data([step_data, ept_data, het_data], path_to_file+date_string+'-all-l2-'+averaging+'.csv', sigma = sigma, leave_out_1st_het_chan = leave_out_1st_het_chan)
data = pd.read_csv(path_to_file+date_string+'-all-l2-'+averaging+'.csv')

step_ept_data = combine_data([step_data, ept_data], path_to_file+date_string+'-step_ept-l2-'+averaging+'.csv', sigma = sigma, leave_out_1st_het_chan = leave_out_1st_het_chan)
step_ept_data = pd.read_csv(path_to_file+date_string+'-step_ept-l2-'+averaging+'.csv')


# saving the contaminated data so it can be plotted separately
# then deleting it from the data so it doesn't overlap
contaminated_data = low_sigma_threshold([step_data, ept_data, het_data], sigma = sigma, leave_out_1st_het_chan = leave_out_1st_het_chan)
#print(contaminated_data, 'contaminated_data')
#deleting low sigma data so it doesn't overplot 
first_het_data = first_het_chan(het_data)
step_data = delete_low_sigma(step_data, sigma = sigma)
ept_data = delete_low_sigma(ept_data, sigma = sigma)
het_data = delete_low_sigma(het_data, sigma = sigma, leave_out_1st_het_chan = leave_out_1st_het_chan)

#print(step_data, 'STEPPPP')
#print(ept_data, 'EPTTTTTT')
#print(het_data, 'HETTTTT')
#print(first_het_data, 'first')
#print(data)

#-------------------------------------------------------------------------------------------------------------------------------------------------
color = {'sun':'crimson','asun':'orange', 'north':'darkslateblue', 'south':'c'}
prim_e = data['Primary_energy']


pickle_path = None
if save_pickle:
	pickle_path = path_to_file+date_string+'-pickle_'+fit_type+'-l2-'+averaging+'.p'

# <---------------------------------------------------------------------DATA--------------------------------------------------------------------->

# all data
spec_energy = data['Primary_energy']
energy_err_low  = data['Energy_error_low']
energy_err_high = data['Energy_error_high']
spec_flux   = data['Bg_subtracted_'+fit_to]
flux_err    = data['Backsub_peak_uncertainty']

energy_err = [energy_err_low, energy_err_high]

# step ept
spec_energy_step_ept = step_ept_data['Primary_energy']
energy_err_low_step_ept  = step_ept_data['Energy_error_low']
energy_err_high_step_ept = step_ept_data['Energy_error_high']
spec_flux_step_ept   = step_ept_data['Bg_subtracted_'+fit_to]
flux_err_step_ept    = step_ept_data['Backsub_peak_uncertainty']

energy_err_step_ept = [energy_err_low_step_ept, energy_err_high_step_ept]


# step data
spec_energy_step = step_data['Primary_energy']
energy_err_low_step  = step_data['Energy_error_low']
energy_err_high_step = step_data['Energy_error_high']
spec_flux_step   = step_data['Bg_subtracted_'+fit_to]
flux_err_step    = step_data['Backsub_peak_uncertainty']

energy_err_step = [energy_err_low_step, energy_err_high_step]

# ept data
spec_energy_ept = ept_data ['Primary_energy']
energy_err_low_ept   = ept_data ['Energy_error_low']
energy_err_high_ept  = ept_data ['Energy_error_high']
spec_flux_ept    = ept_data ['Bg_subtracted_'+fit_to]
flux_err_ept     = ept_data ['Backsub_peak_uncertainty']

energy_err_ept  = [energy_err_low_ept, energy_err_high_ept]

# het data
spec_energy_het = het_data['Primary_energy']
energy_err_low_het  = het_data['Energy_error_low']
energy_err_high_het = het_data['Energy_error_high']
spec_flux_het  = het_data['Bg_subtracted_'+fit_to]
flux_err_het    = het_data['Backsub_peak_uncertainty']

energy_err_het = [energy_err_low_het, energy_err_high_het]

# contaminated data
spec_energy_c = contaminated_data['Primary_energy']
energy_err_low_c  = contaminated_data['Energy_error_low']
energy_err_high_c = contaminated_data['Energy_error_high']
spec_flux_c  = contaminated_data['Bg_subtracted_'+fit_to]
flux_err_c   = contaminated_data['Backsub_peak_uncertainty']

energy_err_c = [energy_err_low_c, energy_err_high_c]
#print(spec_energy_step)
if leave_out_1st_het_chan:
	# first het
	spec_energy_first_het = first_het_data['Primary_energy']
	energy_err_low_first_het  = first_het_data['Energy_error_low']
	energy_err_high_first_het = first_het_data['Energy_error_high']
	spec_flux_first_het  = first_het_data['Bg_subtracted_'+fit_to]
	flux_err_first_het   = first_het_data['Backsub_peak_uncertainty']

	energy_err_first_het = [energy_err_low_first_het, energy_err_high_first_het]




# <----------------------------------------------------------------------FIT AND PLOT------------------------------------------------------------------->

f, ax = plt.subplots(1, figsize=(6, 4), dpi = 200)

distance = f'Solar Orbiter (R={dist} au)'

if make_fit:
	if fit_type == 'step':
		plot_title = 'SolO '+ distance+' STEP'
		fit_result = MAKE_THE_FIT(spec_energy_step, spec_flux_step, energy_err_step[1], flux_err_step, ax, direction=direction, e_min = e_min, e_max = e_max, which_fit=which_fit, g1_guess=g1_guess, g2_guess=g2_guess, alpha_guess=alpha_guess, break_guess=break_guess, cut_guess = cut_guess, c1_guess=c1_guess,use_random = use_random, iterations = iterations, path = pickle_path)
	if fit_type == 'ept':
		plot_title = 'SolO '+ distance+' EPT'
		fit_result = MAKE_THE_FIT(spec_energy_ept, spec_flux_ept, energy_err_ept[1], flux_err_ept, ax, direction=direction, e_min = e_min, e_max = e_max, which_fit=which_fit, g1_guess=g1_guess, g2_guess=g2_guess, alpha_guess=alpha_guess, break_guess=break_guess, cut_guess = cut_guess, c1_guess=c1_guess,use_random = use_random, iterations = iterations, path = pickle_path)
	if fit_type == 'het':
		plot_title = 'SolO '+ distance+' HET'
		fit_result = MAKE_THE_FIT(spec_energy_het, spec_flux_het, energy_err_het[1], flux_err_ept, ax, direction=direction, e_min = e_min, e_max = e_max, which_fit='single', g1_guess=g1_guess, g2_guess=g2_guess, alpha_guess=alpha_guess, break_guess=break_guess, cut_guess = cut_guess,  c1_guess=c1_guess,use_random = use_random, iterations = iterations, path = pickle_path)
	if fit_type == 'step_ept':
		plot_title = 'SolO '+ distance+' STEP and EPT'
		fit_result = MAKE_THE_FIT(spec_energy_step_ept, spec_flux_step_ept, energy_err_step_ept[1], flux_err_step_ept, ax, direction=direction, e_min = e_min, e_max = e_max, which_fit=which_fit, g1_guess=g1_guess, g2_guess=g2_guess, alpha_guess=alpha_guess, break_guess=break_guess, cut_guess = cut_guess, c1_guess=c1_guess,use_random = use_random, iterations = iterations, path = pickle_path)
	if fit_type == 'step_ept_het':
		plot_title = 'SolO '+ distance+' STEP, EPT and HET'
		fit_result = MAKE_THE_FIT(spec_energy, spec_flux, energy_err[1], flux_err, ax, direction=direction, e_min = e_min, e_max = e_max, which_fit=which_fit, g1_guess=g1_guess, g2_guess=g2_guess, alpha_guess=alpha_guess, break_guess=break_guess, cut_guess = cut_guess, c1_guess=c1_guess,use_random = use_random, iterations = iterations, path = pickle_path)
	


ax.errorbar(spec_energy_step, spec_flux_step, yerr=flux_err_step, xerr = energy_err_step, marker='o', markersize= 3 , linestyle='', color='darkorange', label='STEP', zorder = -1)
ax.errorbar(spec_energy_ept, spec_flux_ept, yerr=flux_err_ept, xerr = energy_err_ept, marker='o', linestyle='', markersize= 3, color=color[direction], label='EPT '+direction, zorder = -1)
ax.errorbar(spec_energy_het, spec_flux_het, yerr=flux_err_het, xerr = energy_err_het, marker='o', linestyle='', markersize= 3, color='maroon', label='HET '+direction, zorder = -1)
ax.errorbar(spec_energy_c, spec_flux_c, yerr=flux_err_c, xerr = energy_err_c, marker='o', linestyle='', markersize= 3, color='gray', label='Sigma below '+str(sigma), zorder = -1)
if leave_out_1st_het_chan:
	ax.errorbar(spec_energy_first_het, spec_flux_first_het, yerr=flux_err_first_het, xerr = energy_err_first_het, marker='o', linestyle='', markersize= 3, color='black', label='Not included in the fit', zorder = -1)

if backsub:
	ax.errorbar(spec_energy_step, step_data['Background_flux'], yerr=step_data['Bg_electron_uncertainty'], xerr = energy_err_step, marker='o', markersize= 3, linestyle='', color='darkorange', alpha=0.3)
	ax.errorbar(spec_energy_ept, ept_data['Background_flux'], yerr=ept_data['Bg_electron_uncertainty'], xerr = energy_err_ept, marker='o', markersize= 3, linestyle='', color=color[direction], alpha=0.3)
	ax.errorbar(spec_energy_het, het_data['Background_flux'], yerr=het_data['Bg_electron_uncertainty'], xerr = energy_err_het, marker='o', markersize= 3, linestyle='', color='maroon', alpha=0.3)
	ax.errorbar(spec_energy_c, contaminated_data['Background_flux'], yerr=contaminated_data['Bg_electron_uncertainty'], xerr = energy_err_c, marker='o', markersize= 3, linestyle='', color='gray', alpha=0.3)
	if leave_out_1st_het_chan:
		ax.errorbar(spec_energy_first_het, first_het_data['Background_flux'], yerr=first_het_data['Bg_electron_uncertainty'], xerr = energy_err_first_het, marker='o', markersize= 3, linestyle='', color='black', alpha=0.3)
	
	

ax.set_xscale('log')
ax.set_yscale('log')
locmin = pltt.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=12)
ax.yaxis.set_minor_locator(locmin)
ax.yaxis.set_minor_formatter(pltt.NullFormatter())


if legend_title == 'Electrons':
	ax.set_xlim(2e-3, 20)
if legend_title == 'foil':
	ax.set_xlim(2e-3, 20)
if legend_title == 'mag':
    ax.set_xlim(4e1, 7.4e3)


plt.legend(title='"'+legend_title+'"',  prop={'size': 7})
plt.ylabel(intensity_label)
plt.xlabel(energy_label)
plt.title(plot_title+'  '+peak_info+'\n'+date_str+'  '+averaging+'  averaging')

if savefig:
	plt.savefig(path_to_savefig+date_string+'-'+averaging+'-'+fit_type+'-'+slope, dpi=300)

plt.show()
