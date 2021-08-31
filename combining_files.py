import os
import glob
import pandas as pd


def combine_data(data_name_list, path, sigma = 3, leave_out_1st_het_chan = False):
	#print(data_name_list)
	if leave_out_1st_het_chan and len(data_name_list)>2:
		het = data_name_list[2]
		first_het = het.index[data_name_list[2]['Primary_energy']< 0.7].tolist()
		het = het.drop(first_het, axis = 0)
		het.reset_index(drop=True, inplace=True)
		data_name_list[2] = het 
	
	combined_csv = pd.concat(data_name_list)
	combined_csv.reset_index(drop=True, inplace=True)
	combined_csv = combined_csv.drop(columns = 'Energy_channel')
	
	rows_to_delete = combined_csv.index[combined_csv['Peak_significance'] <sigma].tolist()
	combined_csv = combined_csv.drop(rows_to_delete, axis = 0)
	combined_csv.reset_index(drop=True, inplace=True)
	
	combined_csv.to_csv(path)
	
	return(combined_csv)

def low_sigma_threshold(data_name_list, sigma = 3, leave_out_1st_het_chan = False):
	combined_csv = pd.concat(data_name_list)
	combined_csv.reset_index(drop=True, inplace=True)
	combined_csv = combined_csv.drop(columns = 'Energy_channel')
	
	if leave_out_1st_het_chan:
		het = data_name_list[2]
		first_het = het.index[data_name_list[2]['Primary_energy']< 0.7].tolist()
		het = het.drop(first_het, axis = 0)
		het.reset_index(drop=True, inplace=True)
		data_name_list[2] = het 
	

	rows_to_delete = combined_csv.index[combined_csv['Peak_significance'] >sigma].tolist()
	combined_csv = combined_csv.drop(rows_to_delete, axis = 0)
	combined_csv.reset_index(drop=True, inplace=True)
	
	return(combined_csv)
	
	
def delete_low_sigma(data, sigma = 3, leave_out_1st_het_chan = False):
	data = data.drop(columns = 'Energy_channel')
	rows_to_delete = data.index[data['Peak_significance'] <sigma].tolist()
	data = data.drop(rows_to_delete, axis = 0)
	data.reset_index(drop=True, inplace=True)
	
	if leave_out_1st_het_chan:
		first_het = data.index[data['Primary_energy']< 0.7].tolist()
		data = data.drop(first_het, axis = 0)
		data.reset_index(drop=True, inplace=True)

	return(data)
	

def first_het_chan(data):
	
	first_het = data.index[data['Primary_energy']> 0.7].tolist()
	data = data.drop(first_het, axis = 0)
	data.reset_index(drop=True, inplace=True)
	
	return(data)
	
