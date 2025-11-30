#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 RFHS.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr


class ask_source(gr.sync_block):
    """
    docstring for block cw_source
    """
    def __init__(self, text="RFHS", samp_rate=48000, baud_rate=3300, repeat=10):
        gr.sync_block.__init__(self,
            name="ASK Source",
            in_sig=None,
            out_sig=[np.float32])
        
        self.text = text
        self.samp_rate = samp_rate
        self.baud_rate = baud_rate
        self.repeat = repeat
        self.output_data = np.array(main(self.text, self.samp_rate, self.baud_rate, self.repeat), dtype=np.float32)

        # Initialize an index to track position
        self.idx = 0



    def work(self, input_items, output_items):
        out = output_items[0]
        n_output_items = len(out) # The space available (e.g., 8192)
        if self.idx >= len(self.output_data):
            return -1
        
        # Calculate how much data we have left to send in this cycle
        data_len = len(self.output_data)
        num_to_send = min(n_output_items, data_len - self.idx)
        
        # Write the chunk to the output buffer
        out[:num_to_send] = self.output_data[self.idx : self.idx + num_to_send]
        
        # Update the index
        self.idx += num_to_send
        # output_items[0][:len(self.pager_data)] = self.pager_data
        return num_to_send


def main(msg, samp_rate, baud_rate, repeat):
    ask_code = '0,'*100
    msg = msg.encode("utf-8").hex()
    scale = 16
    num_of_bits = 8
    str1 = bin(int(msg, scale))[2:].zfill(num_of_bits)
    tmp = ','.join(list(str1))
    ask_code = ask_code + tmp + ',0'*25
    bit_duration = int(samp_rate / baud_rate)
    ask_split = ask_code.split(',')
    ask_split = [item for character in ask_split
                 for item in [character] * bit_duration]

    ask = list(map(int, ask_split)) * repeat

    return ask