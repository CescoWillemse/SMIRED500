# SMIRED500
Python tools for the eye-tracker SMI RED 500


## smi2csv.py - Exporting eye-tracking data in CSV
This Python script extracts a SMI RED 500 text file in a CSV

python smi2csv.py <smi_input> <smi_output>

Example of usage:
python smi2csv.py input.txt output.csv

## SMI_dwelltimes.py - Calculating AOI dwell times per trial
This python script reads SMI csv file (the smi2csv.py output), labels relevant AOIs, calculates dwell time on each AOI per trial (from 'Video_onset' until 'Distraction_start') and saves the variables.

python SMI_dwelltimes <input filename> <output filename>

Example of use: 
python SMI_dwelltimes.py input.csv output.csv
