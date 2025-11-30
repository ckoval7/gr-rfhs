#!/usr/bin/python3

"""
Written by: Tony Tiger 6/2019
RFHS Updates: Dan
Incorporated into GRC by Corey Koval 11/2025

This program generates manchester encoded data packets for LRS pagers and GNU Radio.

Watch the YouTube video for more information: https://www.youtube.com/watch?v=ycLLb4eVZpI

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import re
# import struct
import argparse
import random

# GR Block Stuff
import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self, systemid=1, pagerid=1, function=1, printkey=False, random=False, verbose=False):
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='LRS Pager Source',   # will show up in GRC
            in_sig=None,
            out_sig=[np.float32]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.systemid = systemid
        self.pagerid = pagerid
        self.function = function
        self.printkey = printkey
        self.random = random
        self.verbose = verbose
        self.pager_data = np.array(main(systemid= self.systemid,
                               pagerid= self.pagerid,
                               function= self.function,
                               printkey= self.printkey
                               ), dtype=np.float32)

        # Initialize an index to track position
        self.idx = 0

    def work(self, input_items, output_items):
        out = output_items[0]
        n_output_items = len(out) # The space available (e.g., 8192)
        if self.idx >= len(self.pager_data):
            return -1
        
        # Calculate how much data we have left to send in this cycle
        data_len = len(self.pager_data)
        num_to_send = min(n_output_items, data_len - self.idx)
        
        # Write the chunk to the output buffer
        out[:num_to_send] = self.pager_data[self.idx : self.idx + num_to_send]
        
        # Update the index
        self.idx += num_to_send
        # output_items[0][:len(self.pager_data)] = self.pager_data
        return num_to_send


def encode_manchester( bin_list, verbose ):

      pre = []  # create extra preambles to wake up the pager
      for x in range(0,50): 
            pre.append('1')
            pre.append('0')

      l = re.findall('.', "".join( pre + bin_list  ) )  # join the preamble and the rest of the packet

      m = []
      if(verbose):
          print('\n')
          print("".join(str(x) for x in l))  # convert list to string

      for x in l:   # convert to manchaster coding
           if( x == '0'):
               m.append(1)
               m.append(0)

           if( x == '1'):
               m.append(0)
               m.append(1)
      return m


# calculate the crc
def calculate_crc( pre, sink_word, rest_id, station_id, pager_n, alert_type, printkey, verbose ):

    l = re.findall('..', pre + sink_word + rest_id + station_id +  pager_n + '0000000000' + alert_type  )

    bin_array = []
    for c in l:
         bin_array.append ( (format( int(c, 16) , '08b')))

    sum=0
    for b in bin_array:
         sum +=  int(b , 2)

    if(verbose):
        print('Full Packet: {0} {1} {2} {3} {4} {5} {6} {7}'.format( pre, sink_word, rest_id, station_id, pager_n, '0000000000', alert_type, format( ( sum % 255), '02x' )))

    if(verbose or printkey):
        rfctfkey = '{0}{1}{2}{3}{4}{5}{6}'.format( sink_word, rest_id, station_id, pager_n, '0000000000', alert_type, format( ( sum % 255), '02x' ))
        print('')
        print('RFCTF Key: {0}'.format(rfctfkey))
        print('')
        print('Keystore line:')
        rfctfpoints = 75
        print('LRS_PAGER,{0},{1},stat,LRS Pager RX'.format(rfctfkey, rfctfpoints))

    bin_array.append( format( ( sum % 255), '08b') )
    return bin_array

#     #1 Flash 30 Seconds, 2 Flash 5 Minutes
#     #3 Flash/Beep 5X5
#     #4 Beep 3 Times
#     #5 Beep 5 Minutes
#     #6 Glow 5 Minutes
#     #7 Glow/Vib 15 Times
#     #10 Flash/Vib 1 Second
#     #68 beep 3 times


def main(systemid=1, pagerid=1, function=1, printkey=True, random=False, verbose=False):
    ##########################################
    # main program start                     #
    ##########################################
    
    if(verbose):
        print("System ID: 0x{:02x}".format(systemid))
        print("Pager ID: 0x{:02x}".format(pagerid))
        print("Page Function: 0x{:02x}".format(function))
        # print("Output file: {}".format(outputfile))

    randomkey = random

    if(randomkey):
        rest_id = random.randint(0,255)
    else:
        rest_id = systemid

    if(randomkey):
        pagers = str(random.randint(0,1023))
    else:
        pagers = str(pagerid)

    pager_list = []
    pager_list = list(map( int, re.split(r'\s+',pagers)))

    if(randomkey):
        alert_type = random.choice([1, 10, 4])
    else:
        alert_type = function

    # outputfile = outputfile
    if(random):
        printkey = True
    else:
        printkey = printkey
    verbose = verbose

    if(printkey):
        print('SDR Simple Challenge Runner line:')
        print('16,LRS_PAGER,-s {0} -p {1} -pf {2},lrs,,0'.format(rest_id, pagers, alert_type))

    # Build list of floats in memory instead of writing to disk
    all_floats = []

    data = []
    for pager_n in pager_list:
        crc_out = ( calculate_crc( format(11184810, '06x') , format( 64557,'04x'), format(rest_id, '02x'), '0', format( pager_n  ,'03x' ), format(alert_type, '02x'), printkey, verbose ) )

        data = encode_manchester( crc_out, verbose )
        [ data.append(0) for x in range(0,100) ]

        if(verbose):
            print('\n')
            print("".join(str(x) for x in data))
            print('\n')

        # Convert binary data to floats in memory
        for d in data:
            if d == 0:
                all_floats.append(0.0001)
            elif d == 1:
                all_floats.append(1.0)
            else:
                print("Error detected in data")
                sys.exit()

    return all_floats