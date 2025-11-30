#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 RFHS.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

CODE = {
    'A': '1,0,1,1,1,0',
    'B': '1,1,1,0,1,0,1,0,1,0',
    'C': '1,1,1,0,1,0,1,1,1,0,1,0',
    'D': '1,1,1,0,1,0,1,0',
    'E': '1,0',
    'F': '1,0,1,0,1,1,1,0,1,0',
    'G': '1,1,1,0,1,1,1,0,1,0',
    'H': '1,0,1,0,1,0,1,0',
    'I': '1,0,1,0',
    'J': '1,0,1,1,1,0,1,1,1,0,1,1,1,0',
    'K': '1,1,1,0,1,0,1,1,1,0',
    'L': '1,0,1,1,1,0,1,0,1,0',
    'M': '1,1,1,0,1,1,1,0',
    'N': '1,1,1,0,1,0',
    'O': '1,1,1,0,1,1,1,0,1,1,1,0',
    'P': '1,0,1,1,1,0,1,1,1,0,1,0',
    'Q': '1,1,1,0,1,1,1,0,1,0,1,1,1,0',
    'R': '1,0,1,1,1,0,1,0',
    'S': '1,0,1,0,1,0',
    'T': '1,1,1,0',
    'U': '1,0,1,0,1,1,1,0',
    'V': '1,0,1,0,1,0,1,1,1,0',
    'W': '1,0,1,1,1,0,1,1,1,0',
    'X': '1,1,1,0,1,0,1,0,1,1,1,0',
    'Y': '1,1,1,0,1,0,1,1,1,0,1,1,1,0',
    'Z': '1,1,1,0,1,1,1,0,1,0,1,0',
    '0': '1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0',
    '1': '1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0',
    '2': '1,0,1,0,1,1,1,0,1,1,1,0,1,1,1,0',
    '3': '1,0,1,0,1,0,1,1,1,0,1,1,1,0',
    '4': '1,0,1,0,1,0,1,0,1,1,1,0',
    '5': '1,0,1,0,1,0,1,0,1,0',
    '6': '1,1,1,0,1,0,1,0,1,0,1,0',
    '7': '1,1,1,0,1,1,1,0,1,0,1,0,1,0',
    '8': '1,1,1,0,1,1,1,0,1,1,1,0,1,0,1,0',
    '9': '1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,0',
    '.': '1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0',
    ',': '1,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,1,1,0',
    '?': '1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,0',
    '!': '1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0',
    ' ': '0,0,0',
    '-': '1,1,1,0,1,0,1,0,1,0,1,0,1,1,1,0',
    ':': '1,1,1,0,1,1,1,0,1,1,1,0,1,0,1,0,1,0',
    '_': '1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0'
}


class cw_source(gr.sync_block):
    """
    docstring for block cw_source
    """
    def __init__(self, text="RFHS", wpm=35, samp_rate=48000):
        gr.sync_block.__init__(self,
            name="Morse Code Source",
            in_sig=None,
            out_sig=[np.float32])
        
        self.wpm = wpm
        self.text = text
        self.samp_rate = samp_rate
        self.output_data = np.array(main(self.text, self.samp_rate, self.wpm), dtype=np.float32)

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


def calculate_dit_sample_repetitions(sample_rate_sps: float, desired_wpm: float) -> int:
    """
    Calculates the integer number of times a single sample must be repeated
    to represent the duration of one 'dit' (the shortest element) at a
    target Morse code speed (WPM), given a constant sample rate (SPS).

    The calculation uses the standard "Paris" formula, where 1 WPM is equivalent
    to a dit duration of 1.2 / WPM seconds.

    Args:
        sample_rate_sps (float): The system's sample rate in Samples Per Second (SPS).
        desired_wpm (float): The target speed in Words Per Minute (WPM).

    Returns:
        int: The repetition factor (number of samples) required for one dit.
    
    Raises:
        ValueError: If sample_rate_sps or desired_wpm is not positive.
    """
    if sample_rate_sps <= 0 or desired_wpm <= 0:
        raise ValueError("Sample rate (SPS) and desired speed (WPM) must be positive.")

    # 1. Calculate Dit Duration in Seconds (t_dit)
    # The standard formula (Paris Standard) defines 1 WPM as 50 unit elements
    # per minute, corresponding to a dit duration of 1.2 seconds per WPM.
    # t_dit = 60 seconds / (50 units/word * WPM) = 1.2 / WPM
    
    T_DIT_SECONDS = 1.2 / desired_wpm

    # 2. Calculate Samples per Dit (Repetition Factor)
    # The number of samples required is the duration multiplied by the rate.
    # Repetitions = T_DIT_SECONDS * Sample Rate (SPS)
    
    repetitions_float = T_DIT_SECONDS * sample_rate_sps

    # 3. Return as an integer (rounded for best accuracy)
    # The result must be an integer number of samples. Rounding ensures the
    # generated duration is as close as possible to the target WPM speed.
    return int(round(repetitions_float))


def main(mesg, samp_rate, wpm):
    morse_code = '0,'
    for char in mesg:
        morse_code = morse_code + CODE[char.upper()] + ',0,'

    morse_code = morse_code + '0,0,0,0,0,0,0,0,0,0,0'

    repeat = calculate_dit_sample_repetitions(samp_rate, wpm)

    # print(repeat)

    m_split = morse_code.split(',')
    m_split = [item for character in m_split
                 for item in [character] * repeat]
    #morse=np.asarray(map(int,m_split))
    morse = list(map(int, m_split))
    return morse