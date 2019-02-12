#   Copyright (C) 2019  Davide De Tommaso
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

import sys
import argparse
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser()
parser.add_argument('smifile_input', metavar='smifile_input', type=str, nargs='+',
                    help='The SMI text file containing name and path,')
parser.add_argument('smifile_output', metavar='smifile_output', type=str, nargs='+',
                    help='The SMI CSV file containing name and path,')
args = parser.parse_args()
logging.info('Loading SMI file from %s' % args.smifile_input[0])

data = {}
with open(args.smifile_input[0], 'r') as f:
    headers = f.readline().rstrip().split(',')
    headers.append('Event')
    logging.info('Parsing data headers ...')
    for item in headers:
        logging.info(item)
        data[item] = []
    logging.info('Parsing data rows ...')
    for row in f:
        fields = row.rstrip().split(',')
        for i in range(0, len(headers) - 1):
            if len(fields) == len(headers) - 1:
                data[headers[i]].append(fields[i])
            else:
                data[headers[i]].append(None)
            i+=1
        if fields[1] == 'MSG':
            data['Time'].pop()
            data['Time'].append(fields[0])
            data['Type'].pop()
            data['Type'].append(fields[1])
            data['Trial'].pop()
            data['Trial'].append(fields[2])
            data['Event'].append(fields[3][11:])
        else:
            data['Event'].append(None)

logging.info('Exporting data in CSV file %s', args.smifile_output[0])
df = pd.DataFrame.from_dict(data)
df.to_csv(args.smifile_output[0])
