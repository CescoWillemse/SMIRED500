#!/usr/bin/env python
# coding: utf-8

#   2019 Cesco Willemse - cesco.willemse@iit.it
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

# SMI processing for dwell times
# Reads SMI csv file, labels relevant AOIs, calculates dwell time on each AOI per trial (until Distraction_start)and saves the variables.

# To use: in shell / terminal type: python SMI_dwelltimes <input filename> <output filename>
# Example: python SMI_dwelltimes.py smipp6.csv pp6dwelltimes.csv

import pandas as pd
import numpy as np
import argparse
import logging
from pygaze.plugins import aoi

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser()
parser.add_argument('input_file', metavar='input_file', type=str, nargs='+',
                    help='The SMI CSV file containing name and path,')
parser.add_argument('output_file', metavar='output_file', type=str, nargs='+',
                    help='The file with dwell times per trial')
args = parser.parse_args()

df = pd.read_csv(args.input_file[0])
logging.info('Loading SMI file from %s' % args.input_file[0])

# Not strictly necessary, but calculating binocular-averaged gaze posistion
df['X_pos_Average'] = df[['L POR X [px]', 'R POR X [px]']].mean(axis=1)
df['Y_pos_Average'] = df[['L POR Y [px]', 'R POR Y [px]']].mean(axis=1)

# Use the PyGaze AOI plugin to define the AOIs; than scan each row to see if the gaze was in one of the AOIs or not.
TopAOI = aoi.AOI('ellipse', (564, 159), [244, 225])
MiddleAOI = aoi.AOI('rectangle', (563, 282), [241, 120])
BottomAOI = aoi.AOI('ellipse', (564, 326), [240, 149])
EyesAOI = aoi.AOI('rectangle', (588,312),[193,63])
df['AOI'] = ''

logging.info('Matching gaze samples to AOIs ...')
for row in df.itertuples():
    gazepos = (row.X_pos_Average, row.Y_pos_Average)
    if row.Type == 'SMP':
        if row.X_pos_Average == 0 or row.Y_pos_Average == 0:
            df.set_value(row.Index, 'AOI', 'None')
        elif EyesAOI.contains(gazepos):
            df.set_value(row.Index, 'AOI', 'Eyes')
        elif TopAOI.contains(gazepos) or MiddleAOI.contains(gazepos) or BottomAOI.contains(gazepos):
            df.set_value(row.Index, 'AOI', 'Face')
        else:
            df.set_value(row.Index, 'AOI', 'Outside')
    else:
        df.set_value(row.Index, 'AOI', 'None')

col_names = ['Trial', 'dwell_eyes', 'dwell_face', 'dwell_outside', 'dwell_NaN', 'total_duration']
dwell_times = pd.DataFrame(columns = col_names)

logging.info('Calculating AOI dwell times per trial ...')
for Trial in range (1, 109):
    df_trial = df.loc[df['Trial']==Trial].reset_index()
    start_phase = df_trial.index[df_trial['Event']=='Video_onset']
    #print start_phase
    end_phase = df_trial.index[df_trial['Event']=='Distraction_onset']
    start_phase = start_phase[0]+1 #plus one to ignore the message line itself
    end_phase = end_phase[0]
    df_trial = df_trial.iloc[start_phase : end_phase, : ]
    #df_t1 #Uncomment to check

    dwell_eyes = df_trial.loc[df_trial.AOI == 'Eyes', 'AOI'].count() * 2
    dwell_face = df_trial.loc[df_trial.AOI == 'Face', 'AOI'].count() * 2
    dwell_outside = df_trial.loc[df_trial.AOI == 'Outside', 'AOI'].count() * 2
    dwell_NaN = df_trial.loc[df_trial.AOI == 'None', 'AOI'].count() * 2
    total_duration = dwell_eyes + dwell_face + dwell_outside + dwell_NaN

    vals = ([Trial, dwell_eyes, dwell_face, dwell_outside, dwell_NaN, total_duration])

    # Uncomment to check
    #print df_trial['AOI'].value_counts()*2 #count the samples, times two milliseconds
    #print dwell_eyes
    #print dwell_face
    #print dwell_outside
    #print dwell_NaN

    df_out = pd.DataFrame([vals], columns = col_names)
    dwell_times = dwell_times.append(df_out)

logging.info('Exporting data in CSV file %s', args.output_file[0])
dwell_times.to_csv(args.output_file[0])
